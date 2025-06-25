"""
Instagram Monthly Stats Schema
Instagram 月次統計用のPydanticスキーマ定義
"""
from typing import Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class InstagramMonthlyStatsBase(BaseModel):
    """Instagram月次統計ベースフィールド"""
    account_id: str = Field(..., description="アカウントID")
    stats_month: date = Field(..., description="統計月（月初日）")
    avg_followers_count: int = Field(0, description="平均フォロワー数")
    avg_following_count: int = Field(0, description="平均フォロー数")
    follower_growth: int = Field(0, description="月間フォロワー成長数")
    follower_growth_rate: float = Field(0.0, description="フォロワー成長率（%）")
    total_posts: int = Field(0, description="月間総投稿数")
    total_likes: int = Field(0, description="月間総いいね数")
    total_comments: int = Field(0, description="月間総コメント数")
    total_reach: int = Field(0, description="月間総リーチ数")
    avg_engagement_rate: float = Field(0.0, description="平均エンゲージメント率")
    best_performing_day: Optional[date] = Field(None, description="最高パフォーマンス日")
    engagement_trend: Optional[str] = Field(None, description="エンゲージメント傾向（JSON文字列）")
    content_performance: Optional[str] = Field(None, description="コンテンツパフォーマンス（JSON文字列）")

class InstagramMonthlyStatsCreate(InstagramMonthlyStatsBase):
    """Instagram月次統計作成用スキーマ"""
    pass

class InstagramMonthlyStatsUpdate(BaseModel):
    """Instagram月次統計更新用スキーマ"""
    avg_followers_count: Optional[int] = None
    avg_following_count: Optional[int] = None
    follower_growth: Optional[int] = None
    follower_growth_rate: Optional[float] = None
    total_posts: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_reach: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    best_performing_day: Optional[date] = None
    engagement_trend: Optional[str] = None
    content_performance: Optional[str] = None

class InstagramMonthlyStatsResponse(InstagramMonthlyStatsBase):
    """Instagram月次統計レスポンス用スキーマ"""
    id: str = Field(..., description="統計ID")
    created_at: datetime = Field(..., description="作成日時")
    
    class Config:
        from_attributes = True

class InstagramMonthlyStatsList(BaseModel):
    """Instagram月次統計リスト用スキーマ"""
    stats: list[InstagramMonthlyStatsResponse] = Field(default_factory=list, description="統計リスト")
    total_count: int = Field(0, description="総件数")

class InstagramMonthlyStatsComparison(BaseModel):
    """Instagram月次統計比較用スキーマ"""
    current_month: InstagramMonthlyStatsResponse = Field(..., description="当月データ")
    previous_month: Optional[InstagramMonthlyStatsResponse] = Field(None, description="前月データ")
    growth_metrics: Dict[str, float] = Field(default_factory=dict, description="成長指標")
    
class InstagramMonthlyTrend(BaseModel):
    """Instagram月次トレンド分析用スキーマ"""
    months: list[InstagramMonthlyStatsResponse] = Field(..., description="月次データリスト")
    trend_analysis: Dict[str, Any] = Field(default_factory=dict, description="トレンド分析")
    forecasting: Optional[Dict[str, Any]] = Field(None, description="予測データ")
    
class BulkMonthlyStatsCreate(BaseModel):
    """Instagram月次統計一括作成用スキーマ"""
    stats_list: list[InstagramMonthlyStatsCreate] = Field(..., description="統計データリスト")
    
    class Config:
        schema_extra = {
            "example": {
                "stats_list": [
                    {
                        "account_id": "6d7ce798-c83a-4ca6-a5a0-b5c099c7cb99",
                        "stats_month": "2025-06-01",
                        "avg_followers_count": 1200,
                        "follower_growth": 50,
                        "follower_growth_rate": 4.35,
                        "total_posts": 25,
                        "total_likes": 1200,
                        "total_comments": 85,
                        "avg_engagement_rate": 8.5
                    }
                ]
            }
        }