"""
Instagram Account Repository
InstagramAccount モデル専用のデータアクセス層
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from ..models.instagram_account import InstagramAccount


class InstagramAccountRepository:
    """Instagram アカウント専用リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self) -> List[InstagramAccount]:
        """全アカウント取得"""
        return self.db.query(InstagramAccount).all()
    
    async def get_active_accounts(self) -> List[InstagramAccount]:
        """アクティブなアカウント取得"""
        return (
            self.db.query(InstagramAccount)
            .filter(InstagramAccount.is_active == True)
            .all()
        )
    
    async def get_by_id(self, account_id: str) -> Optional[InstagramAccount]:
        """ID によるアカウント取得"""
        return (
            self.db.query(InstagramAccount)
            .filter(InstagramAccount.id == account_id)
            .first()
        )
    
    async def get_by_instagram_user_id(self, instagram_user_id: str) -> Optional[InstagramAccount]:
        """Instagram User ID によるアカウント取得"""
        return (
            self.db.query(InstagramAccount)
            .filter(InstagramAccount.instagram_user_id == instagram_user_id)
            .first()
        )
    
    async def get_by_username(self, username: str) -> Optional[InstagramAccount]:
        """ユーザーネームによるアカウント取得"""
        return (
            self.db.query(InstagramAccount)
            .filter(InstagramAccount.username == username)
            .first()
        )
    
    async def create(self, account_data: dict) -> InstagramAccount:
        """新規アカウント作成"""
        account = InstagramAccount(**account_data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def update(self, account_id: str, account_data: dict) -> Optional[InstagramAccount]:
        """アカウント情報更新"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        # 更新時刻を設定
        account_data['updated_at'] = datetime.now()
        
        for key, value in account_data.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def update_basic_info(
        self, 
        account_id: str, 
        username: str = None,
        account_name: str = None,
        profile_picture_url: str = None
    ) -> Optional[InstagramAccount]:
        """基本情報の更新"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        if username is not None:
            account.username = username
        if account_name is not None:
            account.account_name = account_name
        if profile_picture_url is not None:
            account.profile_picture_url = profile_picture_url
        
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def update_token(
        self, 
        account_id: str, 
        access_token_encrypted: str,
        token_expires_at: datetime = None
    ) -> Optional[InstagramAccount]:
        """アクセストークン更新"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.access_token_encrypted = access_token_encrypted
        if token_expires_at:
            account.token_expires_at = token_expires_at
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def deactivate(self, account_id: str) -> Optional[InstagramAccount]:
        """アカウント非アクティブ化"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.is_active = False
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def activate(self, account_id: str) -> Optional[InstagramAccount]:
        """アカウントアクティブ化"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.is_active = True
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def delete(self, account_id: str) -> bool:
        """アカウント削除"""
        account = await self.get_by_id(account_id)
        if not account:
            return False
        
        self.db.delete(account)
        self.db.commit()
        return True
    
    async def get_token_expiring_soon(self, days_threshold: int = 7) -> List[InstagramAccount]:
        """トークン期限切れが近いアカウント取得"""
        from datetime import timedelta
        threshold_date = datetime.now() + timedelta(days=days_threshold)
        
        return (
            self.db.query(InstagramAccount)
            .filter(
                and_(
                    InstagramAccount.is_active == True,
                    InstagramAccount.token_expires_at <= threshold_date
                )
            )
            .all()
        )
    
    async def update_last_sync(self, account_id: str, sync_time: datetime) -> Optional[InstagramAccount]:
        """最終同期時刻更新"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.last_synced_at = sync_time
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def update_collection_status(
        self, 
        account_id: str, 
        collection_success: bool,
        error_message: str = None
    ) -> Optional[InstagramAccount]:
        """データ収集ステータス更新"""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        # 最終データ収集成功時刻を更新
        if collection_success:
            account.last_synced_at = datetime.now()
        
        # TODO: collection_statusやerror_messageフィールドが追加された場合の処理
        # account.collection_status = 'success' if collection_success else 'failed'
        # account.last_error_message = error_message if not collection_success else None
        
        account.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        return account
    
    async def get_accounts_for_collection(self, account_filter: Optional[List[str]] = None) -> List[InstagramAccount]:
        """データ収集対象アカウント取得"""
        query = (
            self.db.query(InstagramAccount)
            .filter(InstagramAccount.is_active == True)
        )
        
        # フィルタ適用
        if account_filter:
            query = query.filter(InstagramAccount.instagram_user_id.in_(account_filter))
        
        return query.all()
    
    async def bulk_update_sync_status(self, account_ids: List[str], sync_time: datetime) -> int:
        """複数アカウントの同期ステータス一括更新"""
        try:
            updated_count = (
                self.db.query(InstagramAccount)
                .filter(InstagramAccount.id.in_(account_ids))
                .update(
                    {
                        'last_synced_at': sync_time,
                        'updated_at': datetime.now()
                    },
                    synchronize_session=False
                )
            )
            self.db.commit()
            return updated_count
        except Exception as e:
            self.db.rollback()
            raise e