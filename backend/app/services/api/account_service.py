"""
Account Service
アカウント管理用のビジネスロジック層
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ...models.instagram_account import InstagramAccount
from ...repositories.instagram_account_repository import InstagramAccountRepository
from ...schemas.instagram_account_schema import (
    AccountListResponse,
    AccountDetailResponse,
    InstagramAccountWithStats,
    TokenValidationResponse
)

# ログ設定
logger = logging.getLogger(__name__)


class AccountService:
    """アカウント管理サービス"""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = InstagramAccountRepository(db)
    
    async def get_accounts(
        self, 
        active_only: bool = True,
        include_metrics: bool = False
    ) -> AccountListResponse:
        """
        アカウント一覧取得
        
        Args:
            active_only: アクティブアカウントのみ取得
            include_metrics: 統計情報を含む
            
        Returns:
            アカウント一覧レスポンス
        """
        try:
            logger.info(f"Getting accounts: active_only={active_only}, include_metrics={include_metrics}")
            
            if active_only:
                accounts = await self.account_repo.get_active_accounts()
            else:
                accounts = await self.account_repo.get_all()
            
            # アカウントデータを変換
            account_responses = []
            for account in accounts:
                account_data = await self._convert_to_account_response(
                    account, include_metrics
                )
                account_responses.append(account_data)
            
            # サマリー情報計算
            total = len(accounts)
            active_count = sum(1 for acc in accounts if acc.is_active)
            
            result = AccountListResponse(
                accounts=account_responses,
                total=total,
                active_count=active_count
            )
            
            logger.info(f"Successfully retrieved {total} accounts ({active_count} active)")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get accounts: {str(e)}", exc_info=True)
            raise

    async def get_account_details(self, account_id: str) -> Optional[AccountDetailResponse]:
        """
        アカウント詳細取得
        
        Args:
            account_id: アカウントID (UUID または Instagram User ID)
            
        Returns:
            アカウント詳細レスポンス
        """
        try:
            logger.info(f"Getting account details for: {account_id}")
            
            # UUIDまたはInstagram User IDで検索
            account = await self._get_account_by_id_or_instagram_id(account_id)
            
            if not account:
                logger.warning(f"Account not found: {account_id}")
                return None
            
            # 詳細データに変換
            account_data = await self._convert_to_account_response(
                account, include_metrics=True
            )
            
            # 詳細レスポンスに変換
            detail_response = AccountDetailResponse(
                **account_data.dict(),
                facebook_page_id=account.facebook_page_id
            )
            
            logger.info(f"Successfully retrieved account details for: {account.username}")
            return detail_response
            
        except Exception as e:
            logger.error(f"Failed to get account details: {str(e)}", exc_info=True)
            raise

    async def validate_token(self, account_id: str) -> Optional[TokenValidationResponse]:
        """
        トークン有効性確認
        
        Args:
            account_id: アカウントID
            
        Returns:
            トークン検証レスポンス
        """
        try:
            logger.info(f"Validating token for account: {account_id}")
            
            account = await self._get_account_by_id_or_instagram_id(account_id)
            
            if not account:
                logger.warning(f"Account not found for token validation: {account_id}")
                return None
            
            # トークン有効性チェック
            is_valid, days_until_expiry, warning_level = self._check_token_validity(account)
            
            response = TokenValidationResponse(
                account_id=account.id,
                is_valid=is_valid,
                expires_at=account.token_expires_at,
                days_until_expiry=days_until_expiry,
                warning_level=warning_level,
                needs_refresh=warning_level in ['critical', 'expired']
            )
            
            logger.info(f"Token validation result for {account.username}: {warning_level}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to validate token: {str(e)}", exc_info=True)
            raise

    async def get_accounts_needing_refresh(self, days_threshold: int = 7) -> List[InstagramAccount]:
        """
        リフレッシュが必要なアカウント取得
        
        Args:
            days_threshold: 期限切れまでの日数閾値
            
        Returns:
            リフレッシュが必要なアカウントリスト
        """
        try:
            accounts = await self.account_repo.get_token_expiring_soon(days_threshold)
            logger.info(f"Found {len(accounts)} accounts needing token refresh")
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to get accounts needing refresh: {str(e)}", exc_info=True)
            raise

    async def _get_account_by_id_or_instagram_id(self, account_id: str) -> Optional[InstagramAccount]:
        """UUIDまたはInstagram User IDでアカウント取得"""
        try:
            # まずInstagram User IDで検索
            account = await self.account_repo.get_by_instagram_user_id(account_id)
            if account:
                return account
            
            # UUID形式で検索
            try:
                account = await self.account_repo.get_by_id(account_id)
                return account
            except Exception:
                # UUID パースエラーの場合は None を返す
                return None
                
        except Exception as e:
            logger.error(f"Failed to get account by ID: {str(e)}")
            return None

    async def _convert_to_account_response(
        self, 
        account: InstagramAccount, 
        include_metrics: bool = False
    ) -> InstagramAccountWithStats:
        """
        アカウントモデルをレスポンススキーマに変換
        
        Args:
            account: アカウントモデル
            include_metrics: 統計情報を含むか
            
        Returns:
            アカウントレスポンス
        """
        try:
            # トークン有効性チェック
            is_valid, days_until_expiry, _ = self._check_token_validity(account)
            
            # 基本データ
            account_data = {
                "id": account.id,
                "instagram_user_id": account.instagram_user_id,
                "username": account.username,
                "account_name": account.account_name,
                "profile_picture_url": account.profile_picture_url,
                "facebook_page_id": account.facebook_page_id,
                "is_active": account.is_active,
                "token_expires_at": account.token_expires_at,
                "created_at": account.created_at,
                "updated_at": account.updated_at,
                "is_token_valid": is_valid,
                "days_until_expiry": days_until_expiry,
            }
            
            # 統計情報（必要に応じて）
            if include_metrics:
                metrics = await self._calculate_account_metrics(account)
                account_data.update(metrics)
            else:
                # デフォルト値
                account_data.update({
                    "latest_follower_count": None,
                    "latest_following_count": None,
                    "total_posts": None,
                    "data_quality_score": None,
                    "last_synced_at": None,
                })
            
            return InstagramAccountWithStats(**account_data)
            
        except Exception as e:
            logger.error(f"Failed to convert account to response: {str(e)}")
            raise

    def _check_token_validity(self, account: InstagramAccount) -> tuple[bool, Optional[int], str]:
        """
        トークン有効性チェック
        
        Returns:
            (is_valid, days_until_expiry, warning_level)
        """
        if not account.token_expires_at:
            return True, None, "none"  # 期限未設定は有効とみなす
        
        now = datetime.now()
        expires_at = account.token_expires_at.replace(tzinfo=None) if account.token_expires_at.tzinfo else account.token_expires_at
        
        if expires_at <= now:
            return False, 0, "expired"
        
        days_until_expiry = (expires_at - now).days
        
        if days_until_expiry <= 1:
            return True, days_until_expiry, "critical"
        elif days_until_expiry <= 7:
            return True, days_until_expiry, "warning"
        else:
            return True, days_until_expiry, "none"

    async def _calculate_account_metrics(self, account: InstagramAccount) -> Dict[str, Any]:
        """
        アカウント統計情報計算
        
        Args:
            account: アカウントモデル
            
        Returns:
            統計情報辞書
        """
        try:
            # TODO: 実際の統計計算ロジックを実装
            # 現在は仮の実装
            
            # 投稿数を計算（posts テーブルから）
            from ...models.instagram_post import InstagramPost
            total_posts = (
                self.db.query(InstagramPost)
                .filter(InstagramPost.account_id == account.id)
                .count()
            )
            
            # その他の統計は将来的に daily_stats テーブルから取得
            return {
                "latest_follower_count": None,  # TODO: 最新のフォロワー数
                "latest_following_count": None,  # TODO: 最新のフォロー数
                "total_posts": total_posts,
                "data_quality_score": None,  # TODO: データ品質スコア
                "last_synced_at": None,  # TODO: 最終同期時刻
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate account metrics: {str(e)}")
            # エラー時はデフォルト値を返す
            return {
                "latest_follower_count": None,
                "latest_following_count": None,
                "total_posts": 0,
                "data_quality_score": None,
                "last_synced_at": None,
            }


# サービスインスタンス作成関数
def create_account_service(db: Session) -> AccountService:
    """Account Service インスタンス作成"""
    return AccountService(db)