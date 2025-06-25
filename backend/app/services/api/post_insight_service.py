"""
Post Insight Service
投稿インサイトAPIサービス - フロントエンド向けの投稿データと分析を提供
"""
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from ...models.instagram_post import InstagramPost
from ...models.instagram_post_metrics import InstagramPostMetrics
from ...models.instagram_account import InstagramAccount
from ...repositories.instagram_post_repository import InstagramPostRepository
from ...repositories.instagram_post_metrics_repository import InstagramPostMetricsRepository
from ...repositories.instagram_account_repository import InstagramAccountRepository

# ログ設定
logger = logging.getLogger(__name__)

class PostInsightService:
    """投稿インサイトサービス"""
    
    def __init__(self, db: Session):
        self.db = db
        self.post_repo = InstagramPostRepository(db)
        self.metrics_repo = InstagramPostMetricsRepository(db)
        self.account_repo = InstagramAccountRepository(db)
    
    async def get_post_insights(
        self,
        account_id: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        media_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        投稿インサイトデータを取得
        
        Args:
            account_id: アカウントID（UUID文字列またはInstagram User ID）
            from_date: 開始日付
            to_date: 終了日付
            media_type: メディアタイプフィルター（IMAGE, VIDEO, CAROUSEL_ALBUM, STORY）
            limit: 最大取得件数
            
        Returns:
            投稿インサイトデータ
        """
        try:
            logger.info(f"Getting post insights for account: {account_id}")
            
            # アカウント情報取得・検証
            account = await self._get_account(account_id)
            if not account:
                raise ValueError(f"Account not found: {account_id}")
            
            # 投稿データとメトリクスを結合して取得
            posts_with_metrics = await self._get_posts_with_metrics(
                account.id,
                from_date,
                to_date,
                media_type,
                limit
            )
            
            # データ変換
            post_insights = []
            for post, metrics in posts_with_metrics:
                insight_data = self._convert_to_insight_data(post, metrics)
                post_insights.append(insight_data)
            
            # サマリー計算
            summary = self._calculate_summary(post_insights)
            
            result = {
                "posts": post_insights,
                "summary": summary,
                "meta": {
                    "account_id": str(account.id),
                    "instagram_user_id": account.instagram_user_id,
                    "username": account.username,
                    "total_posts": len(post_insights),
                    "date_range": {
                        "from": from_date.isoformat() if from_date else None,
                        "to": to_date.isoformat() if to_date else None
                    },
                    "filters": {
                        "media_type": media_type,
                        "limit": limit
                    }
                }
            }
            
            logger.info(f"Successfully retrieved {len(post_insights)} post insights")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get post insights: {str(e)}", exc_info=True)
            raise
    
    async def _get_account(self, account_id: str) -> Optional[InstagramAccount]:
        """アカウント取得（UUIDまたはInstagram User IDで検索）"""
        try:
            # まずInstagram User IDで検索（よく使われるパターン）
            account = self.db.query(InstagramAccount).filter(
                InstagramAccount.instagram_user_id == account_id
            ).first()
            
            if account:
                return account
            
            # UUID形式で検索
            try:
                account = self.db.query(InstagramAccount).filter(
                    InstagramAccount.id == account_id
                ).first()
                return account
            except Exception:
                # UUID パースエラーの場合は None を返す
                return None
                
        except Exception as e:
            logger.error(f"Failed to get account: {str(e)}")
            return None
    
    async def _get_posts_with_metrics(
        self,
        account_uuid: str,
        from_date: Optional[date],
        to_date: Optional[date],
        media_type: Optional[str],
        limit: Optional[int]
    ) -> List[tuple[InstagramPost, Optional[InstagramPostMetrics]]]:
        """投稿とメトリクスを結合して取得"""
        try:
            from sqlalchemy import func
            
            # ベースクエリ
            query = (
                self.db.query(InstagramPost, InstagramPostMetrics)
                .outerjoin(InstagramPostMetrics, InstagramPost.id == InstagramPostMetrics.post_id)
                .filter(InstagramPost.account_id == account_uuid)
            )
            
            # 日付フィルター
            if from_date:
                query = query.filter(func.date(InstagramPost.posted_at) >= from_date)
            if to_date:
                query = query.filter(func.date(InstagramPost.posted_at) <= to_date)
            
            # メディアタイプフィルター
            if media_type:
                valid_types = ["IMAGE", "VIDEO", "CAROUSEL_ALBUM", "STORY"]
                if media_type.upper() in valid_types:
                    query = query.filter(InstagramPost.media_type == media_type.upper())
            
            # ソートと制限
            query = query.order_by(InstagramPost.posted_at.desc())
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            logger.debug(f"Retrieved {len(results)} posts with metrics")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get posts with metrics: {str(e)}")
            raise
    
    def _convert_to_insight_data(
        self, 
        post: InstagramPost, 
        metrics: Optional[InstagramPostMetrics]
    ) -> Dict[str, Any]:
        """投稿データをインサイト形式に変換"""
        try:
            # 基本データ
            insight_data = {
                "id": post.instagram_post_id,
                "date": post.posted_at.isoformat(),
                "thumbnail": self._get_thumbnail_url(post),
                "type": post.media_type,
                "caption": post.caption or "",
                "media_url": post.media_url or "",
                "permalink": post.permalink or ""
            }
            
            # メトリクスデータ
            if metrics:
                insight_data.update({
                    "reach": metrics.reach or 0,
                    "likes": metrics.likes or 0,
                    "comments": metrics.comments or 0,
                    "shares": metrics.shares or 0,
                    "saves": metrics.saved or 0,
                    "views": metrics.views or 0,
                    "total_interactions": metrics.total_interactions or 0,
                    "engagement_rate": self._calculate_engagement_rate(metrics),
                    "view_rate": self._calculate_view_rate(metrics) if post.media_type == "VIDEO" else None,
                    
                    # 動画専用メトリクス
                    "video_view_total_time": metrics.video_view_total_time if post.media_type == "VIDEO" else None,
                    "avg_watch_time": metrics.avg_watch_time if post.media_type == "VIDEO" else None,
                    
                    # CAROUSEL/STORY専用メトリクス
                    "follows": metrics.follows if post.media_type in ["CAROUSEL_ALBUM", "STORY"] else None,
                    "profile_visits": metrics.profile_visits if post.media_type in ["CAROUSEL_ALBUM", "STORY"] else None,
                    "profile_activity": metrics.profile_activity if post.media_type in ["CAROUSEL_ALBUM", "STORY"] else None,
                    
                    "recorded_at": metrics.recorded_at.isoformat() if metrics.recorded_at else None
                })
            else:
                # メトリクスなしの場合はデフォルト値
                insight_data.update({
                    "reach": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "saves": 0,
                    "views": 0,
                    "total_interactions": 0,
                    "engagement_rate": 0.0,
                    "view_rate": None,
                    "video_view_total_time": None,
                    "avg_watch_time": None,
                    "follows": None,
                    "profile_visits": None,
                    "profile_activity": None,
                    "recorded_at": None
                })
            
            return insight_data
            
        except Exception as e:
            logger.error(f"Failed to convert post data: {str(e)}")
            raise
    
    def _get_thumbnail_url(self, post: InstagramPost) -> str:
        """サムネイルURL取得（フォールバック付き）"""
        return post.thumbnail_url or post.media_url or ""
    
    def _calculate_engagement_rate(self, metrics: InstagramPostMetrics) -> float:
        """エンゲージメント率計算"""
        if not metrics or not metrics.reach or metrics.reach == 0:
            return 0.0
        
        total_engagement = (
            (metrics.likes or 0) + 
            (metrics.comments or 0) + 
            (metrics.shares or 0) + 
            (metrics.saved or 0)
        )
        
        rate = (total_engagement / metrics.reach) * 100
        return round(rate, 2)
    
    def _calculate_view_rate(self, metrics: InstagramPostMetrics) -> Optional[float]:
        """視聴率計算（VIDEO専用）"""
        if not metrics or not metrics.reach or metrics.reach == 0:
            return None
        
        if not metrics.views:
            return None
        
        rate = (metrics.views / metrics.reach) * 100
        return round(rate, 2)
    
    def _calculate_summary(self, post_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """サマリー統計計算"""
        if not post_insights:
            return {
                "total_posts": 0,
                "avg_engagement_rate": 0.0,
                "total_reach": 0,
                "total_engagement": 0,
                "best_performing_post": None,
                "media_type_distribution": {}
            }
        
        total_reach = sum(post.get("reach", 0) for post in post_insights)
        total_engagement = sum(
            post.get("likes", 0) + post.get("comments", 0) + 
            post.get("shares", 0) + post.get("saves", 0) 
            for post in post_insights
        )
        
        # 平均エンゲージメント率
        engagement_rates = [post.get("engagement_rate", 0) for post in post_insights if post.get("engagement_rate") is not None]
        avg_engagement_rate = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
        
        # 最高パフォーマンス投稿
        best_post = None
        if post_insights:
            best_post = max(post_insights, key=lambda x: x.get("engagement_rate", 0))
        
        # メディアタイプ分布
        media_type_distribution = {}
        for post in post_insights:
            media_type = post.get("type", "UNKNOWN")
            media_type_distribution[media_type] = media_type_distribution.get(media_type, 0) + 1
        
        return {
            "total_posts": len(post_insights),
            "avg_engagement_rate": round(avg_engagement_rate, 2),
            "total_reach": total_reach,
            "total_engagement": total_engagement,
            "best_performing_post": {
                "id": best_post.get("id"),
                "engagement_rate": best_post.get("engagement_rate"),
                "type": best_post.get("type")
            } if best_post else None,
            "media_type_distribution": media_type_distribution
        }

# サービスインスタンス作成関数
def create_post_insight_service(db: Session) -> PostInsightService:
    """Post Insight Service インスタンス作成"""
    return PostInsightService(db)