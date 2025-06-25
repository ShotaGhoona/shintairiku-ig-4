from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Date, Float, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class InstagramDailyStats(Base):
    __tablename__ = "instagram_daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("instagram_accounts.id"), nullable=False, index=True)
    stats_date = Column(Date, nullable=False, index=True)

    # アカウント基本指標
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    # インサイト指標
    reach = Column(Integer, default=0)
    follower_count_change = Column(Integer, default=0)

    # 投稿関連指標
    posts_count = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)

    # 平均値
    avg_likes_per_post = Column(Float, default=0.0)
    avg_comments_per_post = Column(Float, default=0.0)

    # メタデータ（JSON文字列として保存）
    data_sources = Column(Text)
    media_type_distribution = Column(Text)

    created_at = Column(DateTime(timezone=True), default=func.now())

    # リレーション
    # account = relationship("InstagramAccount", back_populates="daily_stats")

    # 制約: 1つのアカウントにつき1日1回の統計記録
    __table_args__ = (
        UniqueConstraint('account_id', 'stats_date', name='uq_account_daily_stats'),
    )

    def __repr__(self):
        return f"<InstagramDailyStats(id={self.id}, account_id={self.account_id}, stats_date={self.stats_date})>"