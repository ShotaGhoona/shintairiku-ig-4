from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, func, UniqueConstraint, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class InstagramPostMetrics(Base):
    __tablename__ = "instagram_post_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("instagram_posts.id", ondelete="CASCADE"), nullable=False, index=True)

    # 全メディア共通メトリクス
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saved = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)

    # CAROUSEL専用メトリクス
    follows = Column(Integer, default=0)
    profile_visits = Column(Integer, default=0)
    profile_activity = Column(Integer, default=0)

    # VIDEO専用メトリクス
    video_view_total_time = Column(BigInteger, default=0)
    avg_watch_time = Column(Integer, default=0)

    # 計算値
    engagement_rate = Column(DECIMAL(5, 2), default=0)

    recorded_at = Column(DateTime(timezone=True), default=func.now(), index=True)

    # リレーション（一時的にコメントアウト）
    # post = relationship("InstagramPost", back_populates="metrics")

    # 制約: 1つの投稿につき1日1回のメトリクス記録
    __table_args__ = (
        UniqueConstraint('post_id', 'recorded_at', name='uq_post_metrics_daily'),
    )

    def __repr__(self):
        return f"<InstagramPostMetrics(id={self.id}, post_id={self.post_id}, likes={self.likes}, engagement_rate={self.engagement_rate})>"