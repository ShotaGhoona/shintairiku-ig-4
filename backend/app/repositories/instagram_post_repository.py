"""
Instagram Post Repository
InstagramPost モデル専用のデータアクセス層
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from ..models.instagram_post import InstagramPost


class InstagramPostRepository:
    """Instagram 投稿専用リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self, account_id: str = None, limit: int = None) -> List[InstagramPost]:
        """投稿一覧取得"""
        query = self.db.query(InstagramPost)
        
        if account_id:
            query = query.filter(InstagramPost.account_id == account_id)
        
        query = query.order_by(desc(InstagramPost.posted_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_id(self, post_id: str) -> Optional[InstagramPost]:
        """ID による投稿取得"""
        return (
            self.db.query(InstagramPost)
            .filter(InstagramPost.id == post_id)
            .first()
        )
    
    async def get_by_instagram_post_id(self, instagram_post_id: str) -> Optional[InstagramPost]:
        """Instagram Post ID による投稿取得"""
        return (
            self.db.query(InstagramPost)
            .filter(InstagramPost.instagram_post_id == instagram_post_id)
            .first()
        )
    
    async def get_by_account(self, account_id: str, limit: int = None) -> List[InstagramPost]:
        """アカウント別投稿取得"""
        query = (
            self.db.query(InstagramPost)
            .filter(InstagramPost.account_id == account_id)
            .order_by(desc(InstagramPost.posted_at))
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_date_range(
        self, 
        account_id: str,
        start_date: date,
        end_date: date
    ) -> List[InstagramPost]:
        """日付範囲による投稿取得"""
        return (
            self.db.query(InstagramPost)
            .filter(
                and_(
                    InstagramPost.account_id == account_id,
                    func.date(InstagramPost.posted_at) >= start_date,
                    func.date(InstagramPost.posted_at) <= end_date
                )
            )
            .order_by(desc(InstagramPost.posted_at))
            .all()
        )
    
    async def get_by_specific_date(self, account_id: str, target_date: date) -> List[InstagramPost]:
        """特定日の投稿取得"""
        return (
            self.db.query(InstagramPost)
            .filter(
                and_(
                    InstagramPost.account_id == account_id,
                    func.date(InstagramPost.posted_at) == target_date
                )
            )
            .order_by(desc(InstagramPost.posted_at))
            .all()
        )
    
    async def get_by_media_type(
        self, 
        account_id: str, 
        media_type: str,
        limit: int = None
    ) -> List[InstagramPost]:
        """メディアタイプ別投稿取得"""
        query = (
            self.db.query(InstagramPost)
            .filter(
                and_(
                    InstagramPost.account_id == account_id,
                    InstagramPost.media_type == media_type
                )
            )
            .order_by(desc(InstagramPost.posted_at))
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def create(self, post_data: dict) -> InstagramPost:
        """新規投稿作成"""
        post = InstagramPost(**post_data)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    async def create_or_update(self, post_data: dict) -> InstagramPost:
        """投稿作成または更新（Instagram Post ID で判定）"""
        existing_post = await self.get_by_instagram_post_id(
            post_data['instagram_post_id']
        )
        
        if existing_post:
            # 更新
            for key, value in post_data.items():
                if hasattr(existing_post, key) and key != 'id':
                    setattr(existing_post, key, value)
            
            self.db.commit()
            self.db.refresh(existing_post)
            return existing_post
        else:
            # 新規作成
            return await self.create(post_data)
    
    async def update(self, post_id: str, post_data: dict) -> Optional[InstagramPost]:
        """投稿情報更新"""
        post = await self.get_by_id(post_id)
        if not post:
            return None
        
        for key, value in post_data.items():
            if hasattr(post, key) and key != 'id':
                setattr(post, key, value)
        
        self.db.commit()
        self.db.refresh(post)
        return post
    
    async def delete(self, post_id: str) -> bool:
        """投稿削除"""
        post = await self.get_by_id(post_id)
        if not post:
            return False
        
        self.db.delete(post)
        self.db.commit()
        return True
    
    async def get_posts_without_metrics(
        self, 
        account_id: str, 
        cutoff_date: date
    ) -> List[InstagramPost]:
        """メトリクスが未取得の投稿を取得"""
        from ..models.instagram_post_metrics import InstagramPostMetrics
        
        return (
            self.db.query(InstagramPost)
            .outerjoin(InstagramPostMetrics)
            .filter(
                and_(
                    InstagramPost.account_id == account_id,
                    InstagramPost.posted_at >= cutoff_date,
                    InstagramPostMetrics.id.is_(None)
                )
            )
            .order_by(desc(InstagramPost.posted_at))
            .all()
        )
    
    async def get_latest_by_account(self, account_id: str) -> Optional[InstagramPost]:
        """アカウントの最新投稿取得"""
        return (
            self.db.query(InstagramPost)
            .filter(InstagramPost.account_id == account_id)
            .order_by(desc(InstagramPost.posted_at))
            .first()
        )
    
    async def count_by_account(self, account_id: str) -> int:
        """アカウント別投稿数カウント"""
        return (
            self.db.query(InstagramPost)
            .filter(InstagramPost.account_id == account_id)
            .count()
        )
    
    async def count_by_date_range(
        self, 
        account_id: str,
        start_date: date,
        end_date: date
    ) -> int:
        """日付範囲での投稿数カウント"""
        return (
            self.db.query(InstagramPost)
            .filter(
                and_(
                    InstagramPost.account_id == account_id,
                    func.date(InstagramPost.posted_at) >= start_date,
                    func.date(InstagramPost.posted_at) <= end_date
                )
            )
            .count()
        )
    
    async def get_media_type_distribution(self, account_id: str) -> dict:
        """メディアタイプ別分布取得"""
        results = (
            self.db.query(
                InstagramPost.media_type,
                func.count(InstagramPost.id).label('count')
            )
            .filter(InstagramPost.account_id == account_id)
            .group_by(InstagramPost.media_type)
            .all()
        )
        
        return {result.media_type: result.count for result in results}