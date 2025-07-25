# Instagram Analysis Database Schema

**確定日**: 2025-06-25  
**バージョン**: 1.0  
**基準**: API検証結果に基づく取得可能データのみ  

---

## テーブル構成

### 1. instagram_accounts
Instagram アカウント情報

### 2. instagram_posts  
Instagram 投稿データ

### 3. instagram_post_metrics
投稿のパフォーマンスメトリクス

### 4. instagram_daily_stats
日別統計データ

### 5. instagram_monthly_stats
月別サマリーデータ

---

## ER図

```mermaid
erDiagram
    instagram_accounts {
        uuid id PK
        string instagram_user_id UK
        string username
        string account_name
        string profile_picture_url
        text access_token_encrypted
        timestamp token_expires_at
        string facebook_page_id
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    instagram_posts {
        uuid id PK
        uuid account_id FK
        string instagram_post_id UK
        string media_type
        text caption
        string media_url
        string thumbnail_url
        string permalink
        timestamp posted_at
        timestamp created_at
    }

    instagram_post_metrics {
        uuid id PK
        uuid post_id FK
        integer likes
        integer comments
        integer saved
        integer shares
        integer views
        integer reach
        integer total_interactions
        integer follows
        integer profile_visits
        integer profile_activity
        bigint video_view_total_time
        integer avg_watch_time
        decimal engagement_rate
        timestamp recorded_at
    }

    instagram_daily_stats {
        uuid id PK
        uuid account_id FK
        date stats_date UK
        integer followers_count
        integer following_count
        integer media_count
        integer posts_count
        integer total_likes
        integer total_comments
        text media_type_distribution
        text data_sources
        timestamp created_at
    }

    instagram_monthly_stats {
        uuid id PK
        uuid account_id FK
        integer year
        integer month
        integer avg_followers
        integer total_posts
        integer total_likes
        integer total_comments
        integer total_reach
        decimal avg_engagement_rate
        integer data_quality_score
        timestamp created_at
    }

    instagram_accounts ||--o{ instagram_posts : "has"
    instagram_accounts ||--o{ instagram_daily_stats : "tracks"
    instagram_accounts ||--o{ instagram_monthly_stats : "summarizes"
    instagram_posts ||--|| instagram_post_metrics : "measures"
```

---

## データ取得マッピング

| データ種別 | API エンドポイント | API フィールド | DB テーブル.フィールド |
|-----------|------------------|---------------|---------------------|
| **基本情報** | `/{ig-user-id}` | `followers_count` | `instagram_daily_stats.followers_count` |
| **基本情報** | `/{ig-user-id}` | `follows_count` | `instagram_daily_stats.following_count` |
| **基本情報** | `/{ig-user-id}` | `media_count` | `instagram_daily_stats.media_count` |
| **投稿** | `/{ig-user-id}/media` | `like_count` | 集約 → `instagram_daily_stats.total_likes` |
| **投稿** | `/{ig-user-id}/media` | `comments_count` | 集約 → `instagram_daily_stats.total_comments` |
| **投稿** | `/{ig-user-id}/media` | 投稿数カウント | 集約 → `instagram_daily_stats.posts_count` |
| **投稿メトリクス** | `/{ig-media-id}/insights` | `likes` | `instagram_post_metrics.likes` |
| **投稿メトリクス** | `/{ig-media-id}/insights` | `saved` | `instagram_post_metrics.saved` |

---

## API制限対応

- **1日2コール**: 基本フィールド(1) + 投稿(1) ※Insightsは取得不可のため削除
- **エラー耐性**: 基本フィールド優先、投稿データ失敗時も継続
- **レート制限**: 200コール/時間 → 100アカウント/日対応可能

## 変更履歴

### v1.1 (2025-07-01)
- `instagram_daily_stats`テーブルをシンプル化
- 取得不可能なInsightsフィールド削除: `reach`, `follower_count_change`
- 計算可能フィールド削除: `avg_likes_per_post`, `avg_comments_per_post`
- APIテスト結果に基づく現実的な構造に変更