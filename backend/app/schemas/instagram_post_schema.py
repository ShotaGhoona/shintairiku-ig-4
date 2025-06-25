"""
Instagram Post Schema
InstagramPost モデル用のPydanticスキーマ
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid


class MediaType(str, Enum):
    """メディアタイプ列挙"""
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    IMAGE = "IMAGE"


class InstagramPostBase(BaseModel):
    """Instagram 投稿基底スキーマ"""
    instagram_post_id: str = Field(..., description="Instagram post ID from API")
    media_type: MediaType = Field(..., description="Media type")
    caption: Optional[str] = Field(None, description="Post caption")
    media_url: Optional[str] = Field(None, description="Media file URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL (for videos)")
    permalink: Optional[str] = Field(None, description="Instagram post URL")
    posted_at: datetime = Field(..., description="Post publication timestamp")


class InstagramPostCreate(InstagramPostBase):
    """Instagram 投稿作成スキーマ"""
    account_id: uuid.UUID = Field(..., description="Account UUID")
    
    @validator('instagram_post_id')
    def validate_instagram_post_id(cls, v):
        """Instagram Post ID のバリデーション"""
        if not v.isdigit():
            raise ValueError('Instagram Post ID must be numeric')
        return v
    
    @validator('media_url', 'thumbnail_url', 'permalink')
    def validate_urls(cls, v):
        """URL のバリデーション"""
        if v is not None and v.strip() == '':
            return None
        return v


class InstagramPostUpdate(BaseModel):
    """Instagram 投稿更新スキーマ"""
    caption: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    
    @validator('media_url', 'thumbnail_url', 'permalink')
    def validate_urls(cls, v):
        if v is not None and v.strip() == '':
            return None
        return v


class InstagramPostResponse(InstagramPostBase):
    """Instagram 投稿応答スキーマ"""
    id: uuid.UUID = Field(..., description="Post UUID")
    account_id: uuid.UUID = Field(..., description="Account UUID")
    created_at: datetime = Field(..., description="Post creation time in database")
    
    class Config:
        from_attributes = True


class InstagramPostWithMetrics(InstagramPostResponse):
    """Instagram 投稿メトリクス付きスキーマ"""
    # 最新メトリクス情報
    latest_likes: Optional[int] = Field(None, description="Latest likes count")
    latest_comments: Optional[int] = Field(None, description="Latest comments count")
    latest_saved: Optional[int] = Field(None, description="Latest saved count")
    latest_shares: Optional[int] = Field(None, description="Latest shares count")
    latest_views: Optional[int] = Field(None, description="Latest views count")
    latest_reach: Optional[int] = Field(None, description="Latest reach count")
    latest_engagement_rate: Optional[float] = Field(None, description="Latest engagement rate")
    metrics_last_updated: Optional[datetime] = Field(None, description="Last metrics update time")


class PostPerformanceMetrics(BaseModel):
    """投稿パフォーマンスメトリクススキーマ"""
    post_id: uuid.UUID
    instagram_post_id: str
    media_type: MediaType
    posted_at: datetime
    
    # エンゲージメントメトリクス
    likes: int = Field(0, description="Likes count")
    comments: int = Field(0, description="Comments count")
    saved: int = Field(0, description="Saved count")
    shares: int = Field(0, description="Shares count")
    views: int = Field(0, description="Views count")
    reach: int = Field(0, description="Reach count")
    engagement_rate: float = Field(0, description="Engagement rate percentage")
    
    # VIDEO専用メトリクス
    video_view_total_time: Optional[int] = Field(None, description="Total video view time in milliseconds")
    avg_watch_time: Optional[int] = Field(None, description="Average watch time in milliseconds")
    
    # CAROUSEL専用メトリクス
    follows: Optional[int] = Field(None, description="Follows from this post")
    profile_visits: Optional[int] = Field(None, description="Profile visits from this post")


class PostsListRequest(BaseModel):
    """投稿一覧リクエストスキーマ"""
    account_id: Optional[uuid.UUID] = Field(None, description="Filter by account ID")
    media_type: Optional[MediaType] = Field(None, description="Filter by media type")
    start_date: Optional[datetime] = Field(None, description="Filter from this date")
    end_date: Optional[datetime] = Field(None, description="Filter to this date")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Number of posts to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of posts to skip")
    sort_by: Optional[str] = Field("posted_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc or desc")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['posted_at', 'created_at', 'media_type']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(allowed_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v


class PostsListResponse(BaseModel):
    """投稿一覧応答スキーマ"""
    posts: List[InstagramPostWithMetrics] = Field(..., description="List of posts")
    total: int = Field(..., description="Total number of posts")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")
    has_more: bool = Field(..., description="Whether there are more posts")


class PostAnalytics(BaseModel):
    """投稿分析データスキーマ"""
    post_id: uuid.UUID
    
    # パフォーマンス指標
    performance_score: float = Field(..., description="Overall performance score (0-100)")
    engagement_quality: str = Field(..., description="Engagement quality: excellent, good, average, poor")
    reach_efficiency: float = Field(..., description="Reach efficiency percentage")
    
    # 比較データ
    vs_account_average: dict = Field(..., description="Comparison with account average")
    vs_media_type_average: dict = Field(..., description="Comparison with same media type average")
    
    # 推奨事項
    recommendations: List[str] = Field(default_factory=list, description="Performance improvement recommendations")


class PostCollectionRequest(BaseModel):
    """投稿データ収集リクエストスキーマ"""
    account_id: uuid.UUID = Field(..., description="Account ID to collect posts for")
    target_date: Optional[datetime] = Field(None, description="Specific date to collect (default: today)")
    include_metrics: bool = Field(True, description="Whether to collect metrics")
    force_refresh: bool = Field(False, description="Force refresh existing data")


class PostCollectionResponse(BaseModel):
    """投稿データ収集応答スキーマ"""
    account_id: uuid.UUID
    collection_date: datetime
    
    # 収集結果
    posts_collected: int = Field(..., description="Number of posts collected")
    new_posts: int = Field(..., description="Number of new posts")
    updated_posts: int = Field(..., description="Number of updated posts")
    metrics_collected: int = Field(..., description="Number of metrics collected")
    
    # API使用量
    api_calls_used: int = Field(..., description="API calls used")
    
    # エラー情報
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")


class MediaTypeDistribution(BaseModel):
    """メディアタイプ分布スキーマ"""
    VIDEO: int = Field(0, description="Number of video posts")
    CAROUSEL_ALBUM: int = Field(0, description="Number of carousel posts")
    IMAGE: int = Field(0, description="Number of image posts")
    total: int = Field(0, description="Total number of posts")
    
    def calculate_percentages(self) -> dict:
        """各メディアタイプの割合を計算"""
        if self.total == 0:
            return {"VIDEO": 0, "CAROUSEL_ALBUM": 0, "IMAGE": 0}
        
        return {
            "VIDEO": round((self.VIDEO / self.total) * 100, 1),
            "CAROUSEL_ALBUM": round((self.CAROUSEL_ALBUM / self.total) * 100, 1),
            "IMAGE": round((self.IMAGE / self.total) * 100, 1)
        }


class PostsSummary(BaseModel):
    """投稿概要スキーマ"""
    account_id: uuid.UUID
    total_posts: int = Field(..., description="Total number of posts")
    
    # メディアタイプ分布
    media_distribution: MediaTypeDistribution = Field(..., description="Media type distribution")
    
    # 期間統計
    posts_last_7_days: int = Field(0, description="Posts in last 7 days")
    posts_last_30_days: int = Field(0, description="Posts in last 30 days")
    
    # 平均パフォーマンス
    avg_likes: float = Field(0, description="Average likes per post")
    avg_comments: float = Field(0, description="Average comments per post")
    avg_engagement_rate: float = Field(0, description="Average engagement rate")
    
    # 最新投稿情報
    latest_post_date: Optional[datetime] = Field(None, description="Most recent post date")
    posting_frequency: float = Field(0, description="Posts per week average")