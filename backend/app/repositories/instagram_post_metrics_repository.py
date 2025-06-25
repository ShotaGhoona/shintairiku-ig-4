"""
Instagram Post Metrics Repository
InstagramPostMetrics モデル専用のデータアクセス層
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date

from ..models.instagram_post_metrics import InstagramPostMetrics


class InstagramPostMetricsRepository:
    """Instagram 投稿メトリクス専用リポジトリ"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self, post_id: str = None) -> List[InstagramPostMetrics]:
        """メトリクス一覧取得"""
        query = self.db.query(InstagramPostMetrics)
        
        if post_id:
            query = query.filter(InstagramPostMetrics.post_id == post_id)
        
        return query.order_by(desc(InstagramPostMetrics.recorded_at)).all()
    
    async def get_by_id(self, metrics_id: str) -> Optional[InstagramPostMetrics]:
        """ID によるメトリクス取得"""
        return (
            self.db.query(InstagramPostMetrics)
            .filter(InstagramPostMetrics.id == metrics_id)
            .first()
        )
    
    async def get_by_post(self, post_id: str) -> List[InstagramPostMetrics]:
        """投稿別メトリクス取得"""
        return (
            self.db.query(InstagramPostMetrics)
            .filter(InstagramPostMetrics.post_id == post_id)
            .order_by(desc(InstagramPostMetrics.recorded_at))
            .all()
        )
    
    async def get_latest_by_post(self, post_id: str) -> Optional[InstagramPostMetrics]:
        """投稿の最新メトリクス取得"""
        return (
            self.db.query(InstagramPostMetrics)
            .filter(InstagramPostMetrics.post_id == post_id)
            .order_by(desc(InstagramPostMetrics.recorded_at))
            .first()
        )
    
    async def get_by_date_range(
        self,
        post_id: str,
        start_date: date,
        end_date: date
    ) -> List[InstagramPostMetrics]:
        """日付範囲によるメトリクス取得"""
        return (
            self.db.query(InstagramPostMetrics)
            .filter(
                and_(
                    InstagramPostMetrics.post_id == post_id,
                    func.date(InstagramPostMetrics.recorded_at) >= start_date,
                    func.date(InstagramPostMetrics.recorded_at) <= end_date
                )
            )
            .order_by(desc(InstagramPostMetrics.recorded_at))
            .all()
        )
    
    async def get_by_specific_date(self, post_id: str, target_date: date) -> Optional[InstagramPostMetrics]:
        """特定日のメトリクス取得"""
        return (
            self.db.query(InstagramPostMetrics)
            .filter(
                and_(
                    InstagramPostMetrics.post_id == post_id,
                    func.date(InstagramPostMetrics.recorded_at) == target_date
                )
            )
            .first()
        )
    
    async def create(self, metrics_data: dict) -> InstagramPostMetrics:
        """新規メトリクス作成"""
        # エンゲージメント率を計算
        if 'engagement_rate' not in metrics_data or metrics_data['engagement_rate'] == 0:
            metrics_data['engagement_rate'] = self._calculate_engagement_rate(metrics_data)
        
        metrics = InstagramPostMetrics(**metrics_data)
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        return metrics
    
    async def create_or_update_daily(self, metrics_data: dict) -> InstagramPostMetrics:
        """日別メトリクス作成または更新"""
        post_id = metrics_data['post_id']
        today = date.today()
        
        existing_metrics = await self.get_by_specific_date(post_id, today)
        
        if existing_metrics:
            # 今日のメトリクスが既に存在する場合は更新
            return await self.update(existing_metrics.id, metrics_data)
        else:
            # 存在しない場合は新規作成
            return await self.create(metrics_data)
    
    async def update(self, metrics_id: str, metrics_data: dict) -> Optional[InstagramPostMetrics]:
        """メトリクス更新"""
        metrics = await self.get_by_id(metrics_id)
        if not metrics:
            return None
        
        # エンゲージメント率を再計算
        if any(key in metrics_data for key in ['likes', 'comments', 'saved', 'shares', 'reach']):
            combined_data = {**metrics.__dict__, **metrics_data}
            metrics_data['engagement_rate'] = self._calculate_engagement_rate(combined_data)
        
        for key, value in metrics_data.items():
            if hasattr(metrics, key) and key != 'id':
                setattr(metrics, key, value)
        
        self.db.commit()
        self.db.refresh(metrics)
        return metrics
    
    async def delete(self, metrics_id: str) -> bool:
        """メトリクス削除"""
        metrics = await self.get_by_id(metrics_id)
        if not metrics:
            return False
        
        self.db.delete(metrics)
        self.db.commit()
        return True
    
    async def get_top_performing_posts(
        self,
        account_id: str = None,
        metric: str = 'engagement_rate',
        limit: int = 10
    ) -> List[InstagramPostMetrics]:
        """高パフォーマンス投稿取得"""
        from ..models.instagram_post import InstagramPost
        
        query = (
            self.db.query(InstagramPostMetrics)
            .join(InstagramPost, InstagramPostMetrics.post_id == InstagramPost.id)
        )
        
        if account_id:
            query = query.filter(InstagramPost.account_id == account_id)
        
        # メトリクスによる並び替え
        if hasattr(InstagramPostMetrics, metric):
            query = query.order_by(desc(getattr(InstagramPostMetrics, metric)))
        else:
            query = query.order_by(desc(InstagramPostMetrics.engagement_rate))
        
        return query.limit(limit).all()
    
    async def get_metrics_summary(self, post_ids: List[str]) -> Dict[str, Any]:
        """メトリクス集計取得"""
        if not post_ids:
            return {}
        
        # 各投稿の最新メトリクスを取得
        from sqlalchemy import distinct
        
        subquery = (
            self.db.query(
                InstagramPostMetrics.post_id,
                func.max(InstagramPostMetrics.recorded_at).label('max_recorded_at')
            )
            .filter(InstagramPostMetrics.post_id.in_(post_ids))
            .group_by(InstagramPostMetrics.post_id)
            .subquery()
        )
        
        latest_metrics = (
            self.db.query(InstagramPostMetrics)
            .join(
                subquery,
                and_(
                    InstagramPostMetrics.post_id == subquery.c.post_id,
                    InstagramPostMetrics.recorded_at == subquery.c.max_recorded_at
                )
            )
            .all()
        )
        
        if not latest_metrics:
            return {}
        
        # 集計計算
        total_likes = sum(m.likes for m in latest_metrics)
        total_comments = sum(m.comments for m in latest_metrics)
        total_saved = sum(m.saved for m in latest_metrics)
        total_shares = sum(m.shares for m in latest_metrics)
        total_views = sum(m.views for m in latest_metrics)
        total_reach = sum(m.reach for m in latest_metrics)
        
        avg_engagement_rate = sum(m.engagement_rate for m in latest_metrics) / len(latest_metrics)
        
        return {
            'total_posts': len(latest_metrics),
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_saved': total_saved,
            'total_shares': total_shares,
            'total_views': total_views,
            'total_reach': total_reach,
            'avg_likes_per_post': total_likes / len(latest_metrics),
            'avg_comments_per_post': total_comments / len(latest_metrics),
            'avg_engagement_rate': round(avg_engagement_rate, 2)
        }
    
    def _calculate_engagement_rate(self, metrics_data: dict) -> float:
        """エンゲージメント率計算"""
        likes = metrics_data.get('likes', 0) or 0
        comments = metrics_data.get('comments', 0) or 0
        saved = metrics_data.get('saved', 0) or 0
        shares = metrics_data.get('shares', 0) or 0
        reach = metrics_data.get('reach', 0) or 0
        
        if reach == 0:
            return 0.0
        
        total_engagement = likes + comments + saved + shares
        engagement_rate = (total_engagement / reach) * 100
        
        return round(engagement_rate, 2)