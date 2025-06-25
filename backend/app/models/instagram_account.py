from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instagram_user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    account_name = Column(String(200))
    profile_picture_url = Column(Text)
    access_token_encrypted = Column(Text, nullable=False)
    token_expires_at = Column(DateTime(timezone=True))
    facebook_page_id = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # リレーション（一時的にコメントアウト）
#    # posts = relationship("InstagramPost", back_populates="account", cascade="all, delete-orphan")
#    # daily_stats = relationship("InstagramDailyStats", back_populates="account", cascade="all, delete-orphan")
#    # monthly_stats = relationship("InstagramMonthlyStats", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InstagramAccount(id={self.id}, username={self.username})>"