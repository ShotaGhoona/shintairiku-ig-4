from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Date, Float, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base



class InstagramDailyStats(Base):
    """
    Instagram日次統計データモデル（シンプル版）
    
    計算可能な値は除外し、実際に取得・保存すべきRawデータのみ
    """
    __tablename__ = "instagram_daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("instagram_accounts.id"), nullable=False, index=True)
    stats_date = Column(Date, nullable=False, index=True)

    # === APIから直接取得する基本データ ===
    followers_count = Column(Integer, nullable=False, default=0)    # フォロワー数
    following_count = Column(Integer, nullable=False, default=0)    # フォロー数  
    media_count = Column(Integer, nullable=False, default=0)        # 総投稿数

    # === 当日の投稿数（新規投稿の検出用） ===
    posts_count = Column(Integer, default=0)                       # 当日投稿数

    # === 当日投稿の集計値（instagram_postsから集計） ===
    total_likes = Column(Integer, default=0)                       # 当日投稿の合計いいね
    total_comments = Column(Integer, default=0)                    # 当日投稿の合計コメント

    # === メタデータ ===
    media_type_distribution = Column(Text)                         # 当日投稿タイプ分布JSON
    data_sources = Column(Text)                                    # データソース情報JSON

    # === システム情報 ===
    created_at = Column(DateTime(timezone=True), default=func.now())

    # === リレーション ===
    # account = relationship("InstagramAccount", back_populates="daily_stats")

    # === 制約 ===
    __table_args__ = (
        UniqueConstraint('account_id', 'stats_date', name='uq_account_daily_stats'),
    )

    def __repr__(self):
        return f"<InstagramDailyStats(account_id={self.account_id}, stats_date={self.stats_date})>"