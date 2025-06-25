"""
Post Insight Schema
投稿インサイトAPI用のPydanticスキーマ定義
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

class PostInsightData(BaseModel):
    """投稿インサイトデータ"""
    id: str = Field(..., description="Instagram投稿ID")
    date: str = Field(..., description="投稿日時（ISO形式）")
    thumbnail: str = Field(..., description="サムネイルURL")
    type: str = Field(..., description="メディアタイプ", pattern="^(IMAGE|VIDEO|CAROUSEL_ALBUM|STORY)$")
    caption: str = Field("", description="キャプション")
    media_url: str = Field("", description="メディアURL")
    permalink: str = Field("", description="パーマリンク")
    
    # 基本メトリクス
    reach: int = Field(0, description="リーチ数")
    likes: int = Field(0, description="いいね数")
    comments: int = Field(0, description="コメント数")
    shares: int = Field(0, description="シェア数")
    saves: int = Field(0, description="保存数")
    views: int = Field(0, description="ビュー数")
    total_interactions: int = Field(0, description="総インタラクション数")
    engagement_rate: float = Field(0.0, description="エンゲージメント率（%）")
    
    # 条件付きメトリクス
    view_rate: Optional[float] = Field(None, description="視聴率（%、VIDEO専用）")
    video_view_total_time: Optional[int] = Field(None, description="総視聴時間（ミリ秒、VIDEO専用）")
    avg_watch_time: Optional[int] = Field(None, description="平均視聴時間（ミリ秒、VIDEO専用）")
    follows: Optional[int] = Field(None, description="フォロー数（CAROUSEL_ALBUM/STORY専用）")
    profile_visits: Optional[int] = Field(None, description="プロフィール訪問数（CAROUSEL_ALBUM/STORY専用）")
    profile_activity: Optional[int] = Field(None, description="プロフィールアクティビティ（CAROUSEL_ALBUM/STORY専用）")
    
    recorded_at: Optional[str] = Field(None, description="メトリクス記録日時（ISO形式）")

    class Config:
        schema_extra = {
            "example": {
                "id": "17923488201091269",
                "date": "2025-06-24T10:00:52+00:00",
                "thumbnail": "https://example.com/thumbnail.jpg",
                "type": "CAROUSEL_ALBUM",
                "caption": "梅雨時期の洗濯を楽にするアイデア",
                "media_url": "https://example.com/media.jpg",
                "permalink": "https://instagram.com/p/xyz123",
                "reach": 78,
                "likes": 24,
                "comments": 0,
                "shares": 0,
                "saves": 0,
                "views": 122,
                "total_interactions": 24,
                "engagement_rate": 30.77,
                "view_rate": None,
                "video_view_total_time": None,
                "avg_watch_time": None,
                "follows": 0,
                "profile_visits": 1,
                "profile_activity": 0,
                "recorded_at": "2025-06-25T00:00:00+00:00"
            }
        }

class PostInsightSummary(BaseModel):
    """投稿インサイトサマリー"""
    total_posts: int = Field(..., description="総投稿数")
    avg_engagement_rate: float = Field(..., description="平均エンゲージメント率（%）")
    total_reach: int = Field(..., description="総リーチ数")
    total_engagement: int = Field(..., description="総エンゲージメント数")
    best_performing_post: Optional[Dict[str, Any]] = Field(None, description="最高パフォーマンス投稿")
    media_type_distribution: Dict[str, int] = Field(..., description="メディアタイプ別分布")

    class Config:
        schema_extra = {
            "example": {
                "total_posts": 32,
                "avg_engagement_rate": 15.45,
                "total_reach": 5678,
                "total_engagement": 876,
                "best_performing_post": {
                    "id": "17923488201091269",
                    "engagement_rate": 30.77,
                    "type": "CAROUSEL_ALBUM"
                },
                "media_type_distribution": {
                    "IMAGE": 15,
                    "VIDEO": 10,
                    "CAROUSEL_ALBUM": 5,
                    "STORY": 2
                }
            }
        }

class PostInsightMeta(BaseModel):
    """投稿インサイトメタデータ"""
    account_id: str = Field(..., description="アカウントUUID")
    instagram_user_id: str = Field(..., description="Instagram User ID")
    username: str = Field(..., description="ユーザー名")
    total_posts: int = Field(..., description="取得した投稿数")
    date_range: Dict[str, Optional[str]] = Field(..., description="日付範囲")
    filters: Dict[str, Any] = Field(..., description="適用されたフィルター")

class PostInsightResponse(BaseModel):
    """投稿インサイトAPIレスポンス"""
    posts: List[PostInsightData] = Field(..., description="投稿インサイトデータリスト")
    summary: PostInsightSummary = Field(..., description="サマリー統計")
    meta: PostInsightMeta = Field(..., description="メタデータ")

    class Config:
        schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": "17923488201091269",
                        "date": "2025-06-24T10:00:52+00:00",
                        "thumbnail": "https://example.com/thumbnail.jpg",
                        "type": "CAROUSEL_ALBUM",
                        "caption": "梅雨時期の洗濯を楽にするアイデア",
                        "reach": 78,
                        "likes": 24,
                        "engagement_rate": 30.77
                    }
                ],
                "summary": {
                    "total_posts": 32,
                    "avg_engagement_rate": 15.45,
                    "total_reach": 5678,
                    "total_engagement": 876
                },
                "meta": {
                    "account_id": "6d7ce798-c83a-4ca6-a5a0-b5c099c7cb99",
                    "instagram_user_id": "17841402015304577",
                    "username": "holz_bauhaus",
                    "total_posts": 32
                }
            }
        }

# クエリパラメータ用スキーマ
class PostInsightQueryParams(BaseModel):
    """投稿インサイトクエリパラメータ"""
    account_id: str = Field(..., description="アカウントID（UUIDまたはInstagram User ID）")
    from_date: Optional[date] = Field(None, description="開始日付（YYYY-MM-DD）")
    to_date: Optional[date] = Field(None, description="終了日付（YYYY-MM-DD）")
    media_type: Optional[str] = Field(None, description="メディアタイプフィルター", pattern="^(IMAGE|VIDEO|CAROUSEL_ALBUM|STORY)$")
    limit: Optional[int] = Field(None, description="最大取得件数", ge=1, le=1000)

# エラーレスポンス用スキーマ
class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    error: str = Field(..., description="エラーメッセージ")
    detail: Optional[str] = Field(None, description="詳細情報")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Account not found",
                "detail": "No account found with ID: invalid_id"
            }
        }