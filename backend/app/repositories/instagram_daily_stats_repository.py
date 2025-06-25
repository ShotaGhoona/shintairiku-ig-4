"""
Instagram Daily Stats Repository
InstagramDailyStats モデル専用のデータアクセス層
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from ..models.instagram_daily_stats import InstagramDailyStats


class InstagramDailyStatsRepository:
    """Instagram 日次統計専用リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self, account_id: str = None, limit: int = None) -> List[InstagramDailyStats]:
        """日次統計一覧取得"""
        query = self.db.query(InstagramDailyStats)
        
        if account_id:
            query = query.filter(InstagramDailyStats.account_id == account_id)
        
        query = query.order_by(desc(InstagramDailyStats.stats_date))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_id(self, stats_id: str) -> Optional[InstagramDailyStats]:
        """ID による日次統計取得"""
        return (
            self.db.query(InstagramDailyStats)
            .filter(InstagramDailyStats.id == stats_id)
            .first()
        )
    
    async def get_by_account(self, account_id: str, limit: int = None) -> List[InstagramDailyStats]:
        """アカウント別日次統計取得"""
        query = (
            self.db.query(InstagramDailyStats)
            .filter(InstagramDailyStats.account_id == account_id)
            .order_by(desc(InstagramDailyStats.stats_date))
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_date_range(
        self, 
        account_id: str,
        start_date: date,
        end_date: date
    ) -> List[InstagramDailyStats]:
        """日付範囲による日次統計取得"""
        return (
            self.db.query(InstagramDailyStats)
            .filter(
                and_(
                    InstagramDailyStats.account_id == account_id,
                    InstagramDailyStats.stats_date >= start_date,
                    InstagramDailyStats.stats_date <= end_date
                )
            )
            .order_by(desc(InstagramDailyStats.stats_date))
            .all()
        )
    
    async def get_by_specific_date(self, account_id: str, target_date: date) -> Optional[InstagramDailyStats]:
        """特定日の日次統計取得"""
        return (
            self.db.query(InstagramDailyStats)
            .filter(
                and_(
                    InstagramDailyStats.account_id == account_id,
                    InstagramDailyStats.stats_date == target_date
                )
            )
            .first()
        )
    
    async def create(self, stats_data: dict) -> InstagramDailyStats:
        """新規日次統計作成"""
        stats = InstagramDailyStats(**stats_data)
        self.db.add(stats)
        self.db.commit()
        self.db.refresh(stats)
        return stats
    
    async def create_or_update(self, stats_data: dict) -> InstagramDailyStats:
        """日次統計作成または更新（アカウントIDと日付で判定）"""
        existing_stats = await self.get_by_specific_date(
            stats_data['account_id'],
            stats_data['stats_date']
        )
        
        if existing_stats:
            # 更新
            for key, value in stats_data.items():
                if hasattr(existing_stats, key) and key != 'id':
                    setattr(existing_stats, key, value)
            
            self.db.commit()
            self.db.refresh(existing_stats)
            return existing_stats
        else:
            # 新規作成
            return await self.create(stats_data)
    
    async def update(self, stats_id: str, stats_data: dict) -> Optional[InstagramDailyStats]:
        """日次統計情報更新"""
        stats = await self.get_by_id(stats_id)
        if not stats:
            return None
        
        for key, value in stats_data.items():
            if hasattr(stats, key) and key != 'id':
                setattr(stats, key, value)
        
        self.db.commit()
        self.db.refresh(stats)
        return stats
    
    async def delete(self, stats_id: str) -> bool:
        """日次統計削除"""
        stats = await self.get_by_id(stats_id)
        if not stats:
            return False
        
        self.db.delete(stats)
        self.db.commit()
        return True
    
    async def get_latest_by_account(self, account_id: str) -> Optional[InstagramDailyStats]:
        """アカウントの最新日次統計取得"""
        return (
            self.db.query(InstagramDailyStats)
            .filter(InstagramDailyStats.account_id == account_id)
            .order_by(desc(InstagramDailyStats.stats_date))
            .first()
        )
    
    async def get_follower_growth_trend(
        self, 
        account_id: str, 
        days: int = 30
    ) -> List[InstagramDailyStats]:
        """フォロワー成長トレンド取得"""
        return (
            self.db.query(InstagramDailyStats)
            .filter(InstagramDailyStats.account_id == account_id)
            .order_by(desc(InstagramDailyStats.stats_date))
            .limit(days)
            .all()
        )
    
    async def calculate_growth_metrics(
        self, 
        account_id: str, 
        start_date: date, 
        end_date: date
    ) -> dict:
        """成長指標計算"""
        stats_list = await self.get_by_date_range(account_id, start_date, end_date)
        
        if not stats_list:
            return {
                'follower_growth': 0,
                'avg_daily_engagement': 0.0,
                'total_posts': 0,
                'avg_posts_per_day': 0.0
            }
        
        # 最新と最古のデータ
        latest = stats_list[0]
        oldest = stats_list[-1]
        
        follower_growth = latest.followers_count - oldest.followers_count
        total_posts = sum(stats.posts_count for stats in stats_list)
        avg_posts_per_day = total_posts / len(stats_list) if stats_list else 0
        
        # 平均エンゲージメント計算
        total_likes = sum(stats.total_likes for stats in stats_list)
        total_comments = sum(stats.total_comments for stats in stats_list)
        avg_daily_engagement = (total_likes + total_comments) / len(stats_list) if stats_list else 0
        
        return {
            'follower_growth': follower_growth,
            'avg_daily_engagement': avg_daily_engagement,
            'total_posts': total_posts,
            'avg_posts_per_day': round(avg_posts_per_day, 2)
        }
    
    async def get_data_quality_score(self, account_id: str, target_date: date) -> float:
        """データ品質スコア取得"""
        stats = await self.get_by_specific_date(account_id, target_date)
        
        if not stats:
            return 0.0
        
        score = 0.0
        max_score = 100.0
        
        # フォロワー数データ（30点）
        if stats.followers_count > 0:
            score += 30
        
        # 投稿データ（25点）
        if stats.posts_count > 0:
            score += 25
        
        # エンゲージメントデータ（25点）
        if stats.total_likes > 0 or stats.total_comments > 0:
            score += 25
        
        # リーチデータ（20点）
        if stats.reach > 0:
            score += 20
        
        return round(min(score, max_score), 2)
    
    async def bulk_create(self, stats_list: List[dict]) -> List[InstagramDailyStats]:
        """一括作成"""
        created_stats = []
        
        for stats_data in stats_list:
            stats = InstagramDailyStats(**stats_data)
            self.db.add(stats)
            created_stats.append(stats)
        
        self.db.commit()
        
        # refresh all objects
        for stats in created_stats:
            self.db.refresh(stats)
        
        return created_stats