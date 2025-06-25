from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Date, Float, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class InstagramMonthlyStats(Base):
    __tablename__ = "instagram_monthly_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("instagram_accounts.id"), nullable=False, index=True)
    stats_month = Column(Date, nullable=False, index=True)  # 月初日で記録

    # アカウント基本指標
    avg_followers_count = Column(Integer, default=0)
    avg_following_count = Column(Integer, default=0)

    # 成長指標
    follower_growth = Column(Integer, default=0)
    follower_growth_rate = Column(Float, default=0.0)

    # 投稿・エンゲージメント指標
    total_posts = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)

    # 分析データ
    best_performing_day = Column(Date)
    engagement_trend = Column(Text)  # JSON文字列
    content_performance = Column(Text)  # JSON文字列

    created_at = Column(DateTime(timezone=True), default=func.now())

    # リレーション
    # account = relationship("InstagramAccount", back_populates="monthly_stats")

    # 制約: 1つのアカウントにつき1月1回の統計記録
    __table_args__ = (
        UniqueConstraint('account_id', 'stats_month', name='uq_account_monthly_stats'),
    )

    def __repr__(self):
        return f"<InstagramMonthlyStats(id={self.id}, account_id={self.account_id}, stats_month={self.stats_month})>"