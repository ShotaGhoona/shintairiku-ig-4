from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("instagram_accounts.id"), nullable=False, index=True)
    instagram_post_id = Column(String(50), unique=True, nullable=False, index=True)
    media_type = Column(String(20), nullable=False, index=True)
    caption = Column(Text)
    media_url = Column(Text)
    thumbnail_url = Column(Text)
    permalink = Column(Text)
    posted_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # リレーション
#    account = relationship("InstagramAccount", back_populates="posts")
#    metrics = relationship("InstagramPostMetrics", back_populates="post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InstagramPost(id={self.id}, instagram_post_id={self.instagram_post_id}, media_type={self.media_type})>"