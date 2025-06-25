"""
Instagram Monthly Stats Repository
InstagramMonthlyStats モデル専用のデータアクセス層
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from ..models.instagram_monthly_stats import InstagramMonthlyStats


class InstagramMonthlyStatsRepository:
    """Instagram 月次統計専用リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self, account_id: str = None, limit: int = None) -> List[InstagramMonthlyStats]:
        """月次統計一覧取得"""
        query = self.db.query(InstagramMonthlyStats)
        
        if account_id:
            query = query.filter(InstagramMonthlyStats.account_id == account_id)
        
        query = query.order_by(desc(InstagramMonthlyStats.stats_month))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_id(self, stats_id: str) -> Optional[InstagramMonthlyStats]:
        """ID による月次統計取得"""
        return (
            self.db.query(InstagramMonthlyStats)
            .filter(InstagramMonthlyStats.id == stats_id)
            .first()
        )
    
    async def get_by_account(self, account_id: str, limit: int = None) -> List[InstagramMonthlyStats]:
        """アカウント別月次統計取得"""
        query = (
            self.db.query(InstagramMonthlyStats)
            .filter(InstagramMonthlyStats.account_id == account_id)
            .order_by(desc(InstagramMonthlyStats.stats_month))
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_by_month_range(
        self, 
        account_id: str,
        start_month: date,
        end_month: date
    ) -> List[InstagramMonthlyStats]:
        """月範囲による月次統計取得"""
        return (
            self.db.query(InstagramMonthlyStats)
            .filter(
                and_(
                    InstagramMonthlyStats.account_id == account_id,
                    InstagramMonthlyStats.stats_month >= start_month,
                    InstagramMonthlyStats.stats_month <= end_month
                )
            )
            .order_by(desc(InstagramMonthlyStats.stats_month))
            .all()
        )
    
    async def get_by_specific_month(self, account_id: str, target_month: date) -> Optional[InstagramMonthlyStats]:
        """特定月の月次統計取得"""
        return (
            self.db.query(InstagramMonthlyStats)
            .filter(
                and_(
                    InstagramMonthlyStats.account_id == account_id,
                    InstagramMonthlyStats.stats_month == target_month
                )
            )
            .first()
        )
    
    async def create(self, stats_data: dict) -> InstagramMonthlyStats:
        """新規月次統計作成"""
        stats = InstagramMonthlyStats(**stats_data)
        self.db.add(stats)
        self.db.commit()
        self.db.refresh(stats)
        return stats
    
    async def create_or_update(self, stats_data: dict) -> InstagramMonthlyStats:
        """月次統計作成または更新（アカウントIDと月で判定）"""
        existing_stats = await self.get_by_specific_month(
            stats_data['account_id'],
            stats_data['stats_month']
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
    
    async def update(self, stats_id: str, stats_data: dict) -> Optional[InstagramMonthlyStats]:
        """月次統計情報更新"""
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
        """月次統計削除"""
        stats = await self.get_by_id(stats_id)
        if not stats:
            return False
        
        self.db.delete(stats)
        self.db.commit()
        return True
    
    async def get_latest_by_account(self, account_id: str) -> Optional[InstagramMonthlyStats]:
        """アカウントの最新月次統計取得"""
        return (
            self.db.query(InstagramMonthlyStats)
            .filter(InstagramMonthlyStats.account_id == account_id)
            .order_by(desc(InstagramMonthlyStats.stats_month))
            .first()
        )
    
    async def get_yearly_trend(
        self, 
        account_id: str, 
        year: int
    ) -> List[InstagramMonthlyStats]:
        """年間トレンド取得"""
        start_month = date(year, 1, 1)
        end_month = date(year, 12, 1)
        
        return await self.get_by_month_range(account_id, start_month, end_month)
    
    async def calculate_year_over_year_growth(
        self, 
        account_id: str, 
        target_month: date
    ) -> dict:
        """前年同月比成長率計算"""
        current_stats = await self.get_by_specific_month(account_id, target_month)
        
        # 前年同月
        previous_year_month = date(target_month.year - 1, target_month.month, 1)
        previous_stats = await self.get_by_specific_month(account_id, previous_year_month)
        
        if not current_stats or not previous_stats:
            return {
                'follower_growth_yoy': 0.0,
                'engagement_growth_yoy': 0.0,
                'posts_growth_yoy': 0.0
            }
        
        # フォロワー成長率
        follower_growth_yoy = 0.0
        if previous_stats.avg_followers_count > 0:
            follower_growth_yoy = (
                (current_stats.avg_followers_count - previous_stats.avg_followers_count) / 
                previous_stats.avg_followers_count * 100
            )
        
        # エンゲージメント成長率
        engagement_growth_yoy = 0.0
        if previous_stats.avg_engagement_rate > 0:
            engagement_growth_yoy = (
                (current_stats.avg_engagement_rate - previous_stats.avg_engagement_rate) / 
                previous_stats.avg_engagement_rate * 100
            )
        
        # 投稿数成長率
        posts_growth_yoy = 0.0
        if previous_stats.total_posts > 0:
            posts_growth_yoy = (
                (current_stats.total_posts - previous_stats.total_posts) / 
                previous_stats.total_posts * 100
            )
        
        return {
            'follower_growth_yoy': round(follower_growth_yoy, 2),
            'engagement_growth_yoy': round(engagement_growth_yoy, 2),
            'posts_growth_yoy': round(posts_growth_yoy, 2)
        }
    
    async def get_top_performing_months(
        self, 
        account_id: str, 
        limit: int = 12,
        metric: str = 'avg_engagement_rate'
    ) -> List[InstagramMonthlyStats]:
        """トップパフォーマンス月取得"""
        order_column = getattr(InstagramMonthlyStats, metric, InstagramMonthlyStats.avg_engagement_rate)
        
        return (
            self.db.query(InstagramMonthlyStats)
            .filter(InstagramMonthlyStats.account_id == account_id)
            .order_by(desc(order_column))
            .limit(limit)
            .all()
        )
    
    async def calculate_seasonal_trends(
        self, 
        account_id: str, 
        years: int = 2
    ) -> dict:
        """季節トレンド分析"""
        # 過去N年のデータを取得
        end_date = date.today().replace(day=1)
        start_date = date(end_date.year - years, 1, 1)
        
        stats_list = await self.get_by_month_range(account_id, start_date, end_date)
        
        # 季節別グルーピング
        seasons = {
            'spring': [3, 4, 5],    # 春
            'summer': [6, 7, 8],    # 夏
            'autumn': [9, 10, 11],  # 秋
            'winter': [12, 1, 2]    # 冬
        }
        
        seasonal_data = {}
        
        for season_name, months in seasons.items():
            season_stats = [s for s in stats_list if s.stats_month.month in months]
            
            if season_stats:
                avg_engagement = sum(s.avg_engagement_rate for s in season_stats) / len(season_stats)
                avg_followers_growth = sum(s.follower_growth for s in season_stats) / len(season_stats)
                avg_posts = sum(s.total_posts for s in season_stats) / len(season_stats)
                
                seasonal_data[season_name] = {
                    'avg_engagement_rate': round(avg_engagement, 2),
                    'avg_followers_growth': round(avg_followers_growth, 2),
                    'avg_posts': round(avg_posts, 2),
                    'months_count': len(season_stats)
                }
        
        return seasonal_data
    
    async def bulk_create(self, stats_list: List[dict]) -> List[InstagramMonthlyStats]:
        """一括作成"""
        created_stats = []
        
        for stats_data in stats_list:
            stats = InstagramMonthlyStats(**stats_data)
            self.db.add(stats)
            created_stats.append(stats)
        
        self.db.commit()
        
        # refresh all objects
        for stats in created_stats:
            self.db.refresh(stats)
        
        return created_stats