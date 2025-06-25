"""
Instagram Post Metrics Schema
InstagramPostMetrics モデル用のPydanticスキーマ
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
import uuid


class InstagramPostMetricsBase(BaseModel):
    """Instagram 投稿メトリクス基底スキーマ"""
    # 全メディア共通メトリクス
    likes: int = Field(0, ge=0, description="Number of likes")
    comments: int = Field(0, ge=0, description="Number of comments")
    saved: int = Field(0, ge=0, description="Number of saves")
    shares: int = Field(0, ge=0, description="Number of shares")
    views: int = Field(0, ge=0, description="Number of views")
    reach: int = Field(0, ge=0, description="Number of unique accounts reached")
    total_interactions: int = Field(0, ge=0, description="Total interactions")
    
    # CAROUSEL専用メトリクス
    follows: Optional[int] = Field(None, ge=0, description="Follows from this post (CAROUSEL only)")
    profile_visits: Optional[int] = Field(None, ge=0, description="Profile visits from this post (CAROUSEL only)")
    profile_activity: Optional[int] = Field(None, ge=0, description="Profile activity from this post (CAROUSEL only)")
    
    # VIDEO専用メトリクス
    video_view_total_time: Optional[int] = Field(None, ge=0, description="Total video view time in milliseconds (VIDEO only)")
    avg_watch_time: Optional[int] = Field(None, ge=0, description="Average watch time in milliseconds (VIDEO only)")
    
    # 計算値
    engagement_rate: float = Field(0, ge=0, le=1000, description="Engagement rate percentage")


class InstagramPostMetricsCreate(InstagramPostMetricsBase):
    """Instagram 投稿メトリクス作成スキーマ"""
    post_id: uuid.UUID = Field(..., description="Post UUID")
    recorded_at: Optional[datetime] = Field(None, description="Recording timestamp (defaults to now)")


class InstagramPostMetricsUpdate(BaseModel):
    """Instagram 投稿メトリクス更新スキーマ"""
    likes: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    saved: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)
    views: Optional[int] = Field(None, ge=0)
    reach: Optional[int] = Field(None, ge=0)
    total_interactions: Optional[int] = Field(None, ge=0)
    follows: Optional[int] = Field(None, ge=0)
    profile_visits: Optional[int] = Field(None, ge=0)
    profile_activity: Optional[int] = Field(None, ge=0)
    video_view_total_time: Optional[int] = Field(None, ge=0)
    avg_watch_time: Optional[int] = Field(None, ge=0)


class InstagramPostMetricsResponse(InstagramPostMetricsBase):
    """Instagram 投稿メトリクス応答スキーマ"""
    id: uuid.UUID = Field(..., description="Metrics UUID")
    post_id: uuid.UUID = Field(..., description="Post UUID")
    recorded_at: datetime = Field(..., description="Recording timestamp")
    
    class Config:
        from_attributes = True


class MetricsComparison(BaseModel):
    """メトリクス比較スキーマ"""
    current_value: float = Field(..., description="Current metric value")
    previous_value: Optional[float] = Field(None, description="Previous metric value")
    change_value: Optional[float] = Field(None, description="Absolute change")
    change_percentage: Optional[float] = Field(None, description="Percentage change")
    trend: Optional[str] = Field(None, description="Trend direction: up, down, stable")
    
    @validator('trend')
    def validate_trend(cls, v):
        if v is not None and v not in ['up', 'down', 'stable']:
            raise ValueError('Trend must be one of: up, down, stable')
        return v


class PostMetricsHistory(BaseModel):
    """投稿メトリクス履歴スキーマ"""
    post_id: uuid.UUID
    metrics_history: List[InstagramPostMetricsResponse] = Field(..., description="Metrics history ordered by date")
    
    # トレンド分析
    likes_trend: MetricsComparison = Field(..., description="Likes trend analysis")
    comments_trend: MetricsComparison = Field(..., description="Comments trend analysis")
    engagement_rate_trend: MetricsComparison = Field(..., description="Engagement rate trend analysis")
    
    # 統計サマリー
    total_data_points: int = Field(..., description="Number of data points")
    collection_period_days: int = Field(..., description="Data collection period in days")
    avg_daily_growth: Dict[str, float] = Field(..., description="Average daily growth rates")


class PostMetricsAggregation(BaseModel):
    """投稿メトリクス集計スキーマ"""
    period_start: date = Field(..., description="Aggregation period start")
    period_end: date = Field(..., description="Aggregation period end")
    posts_count: int = Field(..., description="Number of posts in period")
    
    # 合計値
    total_likes: int = Field(0, description="Total likes in period")
    total_comments: int = Field(0, description="Total comments in period")
    total_saved: int = Field(0, description="Total saves in period")
    total_shares: int = Field(0, description="Total shares in period")
    total_views: int = Field(0, description="Total views in period")
    total_reach: int = Field(0, description="Total reach in period")
    
    # 平均値
    avg_likes_per_post: float = Field(0, description="Average likes per post")
    avg_comments_per_post: float = Field(0, description="Average comments per post")
    avg_engagement_rate: float = Field(0, description="Average engagement rate")
    
    # パフォーマンス指標
    best_performing_post: Optional[Dict[str, Any]] = Field(None, description="Best performing post data")
    worst_performing_post: Optional[Dict[str, Any]] = Field(None, description="Worst performing post data")
    engagement_rate_variance: float = Field(0, description="Engagement rate variance")


class MetricsCollectionRequest(BaseModel):
    """メトリクス収集リクエストスキーマ"""
    post_ids: List[uuid.UUID] = Field(..., description="List of post IDs to collect metrics for")
    force_refresh: bool = Field(False, description="Force refresh existing metrics")
    collect_video_metrics: bool = Field(True, description="Collect video-specific metrics")
    collect_carousel_metrics: bool = Field(True, description="Collect carousel-specific metrics")


class MetricsCollectionResponse(BaseModel):
    """メトリクス収集応答スキーマ"""
    total_posts: int = Field(..., description="Total posts processed")
    successful_collections: int = Field(..., description="Successful metrics collections")
    failed_collections: int = Field(..., description="Failed metrics collections")
    api_calls_used: int = Field(..., description="API calls used")
    
    # 詳細結果
    collected_metrics: List[InstagramPostMetricsResponse] = Field(..., description="Successfully collected metrics")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Collection errors")
    
    # 実行時間
    execution_time_seconds: float = Field(..., description="Total execution time")


class MetricsAnalysis(BaseModel):
    """メトリクス分析スキーマ"""
    post_id: uuid.UUID
    analysis_date: datetime = Field(..., description="Analysis performed date")
    
    # パフォーマンス分析
    performance_score: float = Field(..., ge=0, le=100, description="Overall performance score")
    engagement_quality: str = Field(..., description="Engagement quality rating")
    reach_efficiency: float = Field(..., description="Reach efficiency percentage")
    
    # ベンチマーク比較
    vs_account_average: Dict[str, float] = Field(..., description="Comparison with account average")
    vs_media_type_average: Dict[str, float] = Field(..., description="Comparison with media type average")
    vs_posting_time_average: Dict[str, float] = Field(..., description="Comparison with same posting time average")
    
    # 詳細インサイト
    strengths: List[str] = Field(..., description="Performance strengths")
    weaknesses: List[str] = Field(..., description="Performance weaknesses")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    
    @validator('engagement_quality')
    def validate_engagement_quality(cls, v):
        allowed_qualities = ['excellent', 'good', 'average', 'poor']
        if v not in allowed_qualities:
            raise ValueError(f'Engagement quality must be one of: {", ".join(allowed_qualities)}')
        return v


class VideoMetricsDetail(BaseModel):
    """動画メトリクス詳細スキーマ"""
    post_id: uuid.UUID
    
    # 基本視聴メトリクス
    total_views: int = Field(..., description="Total video views")
    total_view_time_ms: int = Field(..., description="Total view time in milliseconds")
    avg_watch_time_ms: int = Field(..., description="Average watch time in milliseconds")
    
    # 計算値
    total_view_time_minutes: float = Field(..., description="Total view time in minutes")
    avg_watch_time_seconds: float = Field(..., description="Average watch time in seconds")
    completion_rate: Optional[float] = Field(None, description="Video completion rate percentage")
    retention_rate: Optional[float] = Field(None, description="Average retention rate")
    
    # 比較データ
    view_performance: str = Field(..., description="View performance rating")
    retention_performance: str = Field(..., description="Retention performance rating")


class CarouselMetricsDetail(BaseModel):
    """カルーセルメトリクス詳細スキーマ"""
    post_id: uuid.UUID
    
    # カルーセル固有メトリクス
    total_interactions: int = Field(..., description="Total interactions")
    follows_gained: int = Field(..., description="Follows gained from this post")
    profile_visits_generated: int = Field(..., description="Profile visits generated")
    profile_actions: int = Field(..., description="Profile actions taken")
    
    # 変換率
    interaction_to_follow_rate: float = Field(..., description="Interaction to follow conversion rate")
    view_to_profile_visit_rate: float = Field(..., description="View to profile visit conversion rate")
    profile_visit_to_follow_rate: float = Field(..., description="Profile visit to follow conversion rate")
    
    # パフォーマンス評価
    conversion_performance: str = Field(..., description="Conversion performance rating")
    engagement_depth: str = Field(..., description="Engagement depth rating")


class MetricsTrend(BaseModel):
    """メトリクストレンドスキーマ"""
    metric_name: str = Field(..., description="Metric name")
    data_points: List[Dict[str, Any]] = Field(..., description="Trend data points with dates and values")
    
    # トレンド統計
    trend_direction: str = Field(..., description="Overall trend direction")
    slope: float = Field(..., description="Trend slope (change per day)")
    correlation_coefficient: float = Field(..., description="Correlation coefficient (-1 to 1)")
    
    # 予測
    predicted_next_value: Optional[float] = Field(None, description="Predicted next value")
    confidence_interval: Optional[List[float]] = Field(None, description="95% confidence interval")
    
    @validator('trend_direction')
    def validate_trend_direction(cls, v):
        allowed_directions = ['increasing', 'decreasing', 'stable', 'volatile']
        if v not in allowed_directions:
            raise ValueError(f'Trend direction must be one of: {", ".join(allowed_directions)}')
        return v