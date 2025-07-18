"""
Instagram Daily Stats Schema
Instagram 日次統計用のPydanticスキーマ定義
"""
from typing import Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class InstagramDailyStatsBase(BaseModel):
    """Instagram日次統計ベースフィールド（シンプル版）"""
    account_id: str = Field(..., description="アカウントID")
    stats_date: date = Field(..., description="統計日付")
    followers_count: int = Field(0, description="フォロワー数")
    following_count: int = Field(0, description="フォロー数")
    media_count: int = Field(0, description="総投稿数")
    posts_count: int = Field(0, description="当日投稿数")
    total_likes: int = Field(0, description="当日投稿の合計いいね数")
    total_comments: int = Field(0, description="当日投稿の合計コメント数")
    media_type_distribution: Optional[str] = Field(None, description="当日投稿タイプ分布（JSON文字列）")
    data_sources: Optional[str] = Field(None, description="データソース情報（JSON文字列）")

class InstagramDailyStatsCreate(InstagramDailyStatsBase):
    """Instagram日次統計作成用スキーマ"""
    pass

class InstagramDailyStatsUpdate(BaseModel):
    """Instagram日次統計更新用スキーマ"""
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    posts_count: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    media_type_distribution: Optional[str] = None
    data_sources: Optional[str] = None

class InstagramDailyStatsResponse(InstagramDailyStatsBase):
    """Instagram日次統計レスポンス用スキーマ"""
    id: str = Field(..., description="統計ID")
    created_at: datetime = Field(..., description="作成日時")
    
    class Config:
        from_attributes = True

class InstagramDailyStatsList(BaseModel):
    """Instagram日次統計リスト用スキーマ"""
    stats: list[InstagramDailyStatsResponse] = Field(default_factory=list, description="統計リスト")
    total_count: int = Field(0, description="総件数")
    
class InstagramDailyStatsAnalytics(BaseModel):
    """Instagram日次統計分析用スキーマ（計算フィールド含む）"""
    period_start: date = Field(..., description="期間開始日")
    period_end: date = Field(..., description="期間終了日")
    avg_followers: float = Field(0.0, description="期間平均フォロワー数")
    follower_growth_total: int = Field(0, description="期間フォロワー成長数")
    follower_growth_rate: float = Field(0.0, description="フォロワー成長率（%）")
    avg_daily_posts: float = Field(0.0, description="平均日次投稿数")
    total_posts: int = Field(0, description="期間総投稿数")
    total_likes: int = Field(0, description="期間総いいね数")
    total_comments: int = Field(0, description="期間総コメント数")
    avg_likes_per_post: float = Field(0.0, description="投稿あたり平均いいね数（計算値）")
    avg_comments_per_post: float = Field(0.0, description="投稿あたり平均コメント数（計算値）")
    engagement_rate: float = Field(0.0, description="エンゲージメント率（%）（計算値）")
    best_performing_day: Optional[date] = Field(None, description="最高エンゲージメント日")
    
class BulkDailyStatsCreate(BaseModel):
    """Instagram日次統計一括作成用スキーマ"""
    stats_list: list[InstagramDailyStatsCreate] = Field(..., description="統計データリスト")
    
    class Config:
        schema_extra = {
            "example": {
                "stats_list": [
                    {
                        "account_id": "6d7ce798-c83a-4ca6-a5a0-b5c099c7cb99",
                        "stats_date": "2025-07-01",
                        "followers_count": 1250,
                        "following_count": 150,
                        "media_count": 125,
                        "posts_count": 3,
                        "total_likes": 450,
                        "total_comments": 25,
                        "media_type_distribution": "{\"IMAGE\": 2, \"VIDEO\": 1}",
                        "data_sources": "[\"github_actions_daily_collection\"]"
                    }
                ]
            }
        }