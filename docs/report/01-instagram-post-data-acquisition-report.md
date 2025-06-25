# Instagram投稿データ取得レポート

**レポート番号**: 01  
**作成日**: 2025-06-25  
**検証範囲**: Instagram Graph API による投稿データとメトリクス取得  
**目的**: バックエンドエンジニアが Instagram API を使用して投稿関連データを取得する際の完全なガイド

---

## 📋 要約

Instagram Graph API（Facebook Graph API経由）を使用して、投稿一覧と投稿メトリクスを取得する方法を詳細に検証しました。本レポートは、実際のAPIテストに基づく実用的な実装ガイドです。

### 主要な発見
- ✅ 投稿基本情報は完全に取得可能
- ✅ 重要メトリクス（いいね、コメント、保存、シェア、リーチ、視聴回数）は取得可能
- ❌ インプレッション数は取得不可
- ⚠️ メディアタイプにより利用可能メトリクスが異なる

---

## 🔐 認証設定

### 必要な情報
```env
INSTAGRAM_USER_ID=17841455808057230
USERNAME=yamasa_renovation
FACEBOOK_PAGE_ID=103295771313100
FACEBOOK_PAGE_NAME=ヤマサリノベ
ACCESS_TOKEN=EAARrfZCwPTGUBO1rcSMEAEXT6BZA4A8ehn20WxcfQrmg661d96L5PX2lxfzRUCL26T3Vab8ioi0cPbDuuqZCsZBYQ7S1ny1Xm8dFKIoHQlbypJCvgi7erfajPCwfWR9aZBRaQMVNDr6RDfK6er3B7cAdTabtJyLPA5J0VxofcOaC7PyT7aDy2lGMDHVeJVY6ndcMZD
```

### 重要な注意点
- **エンドポイント**: `graph.facebook.com` を使用（`graph.instagram.com` ではない）
- **トークンタイプ**: Facebook Page Token（Instagram Graph APIへのアクセスに使用）
- **権限**: `instagram_basic`, `instagram_manage_insights` が必要

---

## 📊 API エンドポイント仕様

### 1. 投稿一覧取得

#### エンドポイント
```http
GET https://graph.facebook.com/{ig-user-id}/media
```

#### 必要パラメータ
```json
{
  "fields": "id,media_type,caption,media_url,thumbnail_url,timestamp,permalink",
  "access_token": "{access_token}",
  "limit": 25
}
```

#### レスポンス例
```json
{
  "data": [
    {
      "id": "18399578410113164",
      "media_type": "VIDEO",
      "caption": "投稿のキャプションテキスト...",
      "media_url": "https://scontent-nrt1-1.cdninstagram.com/...",
      "thumbnail_url": "https://scontent-nrt1-2.cdninstagram.com/...",
      "timestamp": "2025-06-20T10:02:26+0000",
      "permalink": "https://www.instagram.com/reel/DLHlcq-PimC/"
    }
  ],
  "paging": {
    "cursors": {
      "before": "...",
      "after": "..."
    },
    "next": "https://graph.facebook.com/..."
  }
}
```

#### 利用可能フィールド
| フィールド | データ型 | 説明 | DB列名 |
|-----------|---------|------|--------|
| `id` | string | Instagram投稿ID | `instagram_post_id` |
| `media_type` | string | メディアタイプ | `media_type` |
| `caption` | string | キャプション | `caption` |
| `media_url` | string | メディアURL | `media_url` |
| `thumbnail_url` | string | サムネイルURL | `thumbnail_url` |
| `timestamp` | string | 投稿日時 | `posted_at` |
| `permalink` | string | Instagram投稿URL | `permalink` |

#### メディアタイプ
- `VIDEO` - 動画投稿（Reels含む）
- `CAROUSEL_ALBUM` - カルーセル投稿（複数画像）
- `IMAGE` - 単一画像投稿

---

### 2. 投稿メトリクス取得

#### エンドポイント
```http
GET https://graph.facebook.com/{ig-media-id}/insights
```

#### 必要パラメータ
```json
{
  "metric": "likes,comments,saved,shares,views,reach,total_interactions",
  "access_token": "{access_token}"
}
```

#### レスポンス例
```json
{
  "data": [
    {
      "name": "likes",
      "period": "lifetime",
      "values": [
        {
          "value": 9
        }
      ],
      "title": "Likes",
      "description": "Total number of likes"
    }
  ]
}
```

---

## 📈 利用可能メトリクス詳細

### 全メディアタイプ共通
| メトリクス名 | データ型 | 説明 | DB列名 |
|-------------|---------|------|--------|
| `likes` | integer | いいね数 | `likes` |
| `comments` | integer | コメント数 | `comments` |
| `saved` | integer | 保存数 | `saved` |
| `shares` | integer | シェア数 | `shares` |
| `views` | integer | 視聴回数 | `views` |
| `reach` | integer | リーチ数 | `reach` |
| `total_interactions` | integer | 総インタラクション数 | `total_interactions` |

### VIDEO専用メトリクス
| メトリクス名 | データ型 | 説明 | DB列名 |
|-------------|---------|------|--------|
| `ig_reels_video_view_total_time` | bigint | 総視聴時間（ミリ秒） | `ig_reels_video_view_total_time` |
| `ig_reels_avg_watch_time` | integer | 平均視聴時間（ミリ秒） | `ig_reels_avg_watch_time` |

### CAROUSEL_ALBUM専用メトリクス
| メトリクス名 | データ型 | 説明 | DB列名 |
|-------------|---------|------|--------|
| `follows` | integer | フォロー数 | `follows` |
| `profile_visits` | integer | プロフィール訪問数 | `profile_visits` |
| `profile_activity` | integer | プロフィールアクティビティ | `profile_activity` |

### 利用不可能なメトリクス
- ❌ `impressions` - インプレッション数
- ❌ `saves` - 正しくは `saved`

---

## 🗄️ データベース設計

### posts テーブル
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES instagram_accounts(id),
    instagram_post_id VARCHAR(50) UNIQUE NOT NULL,
    media_type VARCHAR(20) NOT NULL,
    caption TEXT,
    media_url TEXT,
    thumbnail_url TEXT,
    permalink TEXT,
    posted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_posts_account_posted ON posts(account_id, posted_at DESC);
CREATE INDEX idx_posts_media_type ON posts(account_id, media_type, posted_at DESC);
CREATE UNIQUE INDEX idx_posts_instagram_id ON posts(instagram_post_id);
```

### post_metrics テーブル
```sql
CREATE TABLE post_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    saved INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    total_interactions INTEGER DEFAULT 0,
    follows INTEGER DEFAULT 0,
    profile_visits INTEGER DEFAULT 0,
    profile_activity INTEGER DEFAULT 0,
    ig_reels_video_view_total_time BIGINT DEFAULT 0,
    ig_reels_avg_watch_time INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_post_metrics_post_recorded ON post_metrics(post_id, recorded_at DESC);
CREATE INDEX idx_post_metrics_engagement_rate ON post_metrics(engagement_rate DESC);
```

---

## 💻 実装例

### Python実装例

#### 投稿一覧取得
```python
import requests
from datetime import datetime

def get_posts(instagram_user_id: str, access_token: str, limit: int = 25):
    """投稿一覧を取得"""
    url = f"https://graph.facebook.com/{instagram_user_id}/media"
    
    params = {
        'fields': 'id,media_type,caption,media_url,thumbnail_url,timestamp,permalink',
        'access_token': access_token,
        'limit': limit
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    posts = []
    
    for post in data.get('data', []):
        posts.append({
            'instagram_post_id': post.get('id'),
            'media_type': post.get('media_type'),
            'caption': post.get('caption'),
            'media_url': post.get('media_url'),
            'thumbnail_url': post.get('thumbnail_url'),
            'permalink': post.get('permalink'),
            'posted_at': datetime.fromisoformat(
                post.get('timestamp', '').replace('Z', '+00:00')
            )
        })
    
    return posts, data.get('paging')
```

#### メトリクス取得
```python
def get_post_metrics(post_id: str, access_token: str, media_type: str):
    """投稿メトリクスを取得"""
    url = f"https://graph.facebook.com/{post_id}/insights"
    
    # メディアタイプ別メトリクス
    base_metrics = ['likes', 'comments', 'saved', 'shares', 'views', 'reach', 'total_interactions']
    
    if media_type == 'VIDEO':
        metrics = base_metrics + ['ig_reels_video_view_total_time', 'ig_reels_avg_watch_time']
    elif media_type == 'CAROUSEL_ALBUM':
        metrics = base_metrics + ['follows', 'profile_visits', 'profile_activity']
    else:
        metrics = base_metrics
    
    params = {
        'metric': ','.join(metrics),
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        metrics_dict = {}
        
        for metric_data in data.get('data', []):
            metric_name = metric_data.get('name')
            values = metric_data.get('values', [])
            if values:
                metrics_dict[metric_name] = values[0].get('value', 0)
        
        # エンゲージメント率計算
        reach = metrics_dict.get('reach', 0)
        if reach > 0:
            engagement = (
                metrics_dict.get('likes', 0) + 
                metrics_dict.get('comments', 0) + 
                metrics_dict.get('saved', 0) + 
                metrics_dict.get('shares', 0)
            )
            metrics_dict['engagement_rate'] = round((engagement / reach) * 100, 2)
        else:
            metrics_dict['engagement_rate'] = 0.0
        
        return metrics_dict
        
    except requests.exceptions.RequestException as e:
        print(f"メトリクス取得エラー (Post ID: {post_id}): {e}")
        return {}
```

#### 統合処理
```python
def sync_posts_and_metrics(instagram_user_id: str, access_token: str):
    """投稿とメトリクスを同期"""
    
    # 1. 投稿一覧取得
    posts, paging = get_posts(instagram_user_id, access_token)
    
    print(f"取得した投稿数: {len(posts)}")
    
    # 2. 各投稿のメトリクス取得
    for post in posts:
        post_id = post['instagram_post_id']
        media_type = post['media_type']
        
        print(f"メトリクス取得中: {post_id} ({media_type})")
        
        metrics = get_post_metrics(post_id, access_token, media_type)
        
        if metrics:
            # 3. データベース保存（実装に応じて）
            save_post_to_db(post)
            save_metrics_to_db(post_id, metrics)
            print(f"✅ 保存完了: {post_id}")
        else:
            print(f"❌ メトリクス取得失敗: {post_id}")
    
    return posts
```

---

## ⚡ レート制限とパフォーマンス

### レート制限
- **基本制限**: 200コール/時間/ユーザー
- **監視方法**: レスポンスヘッダー `x-business-use-case-usage` を確認

### レスポンスヘッダー例
```json
{
  "x-business-use-case-usage": {
    "102556855985346": [
      {
        "type": "instagram",
        "call_count": 1,
        "total_cputime": 1,
        "total_time": 1,
        "estimated_time_to_regain_access": 0
      }
    ]
  }
}
```

### 最適化推奨事項
1. **バッチ処理**: 25件ずつ投稿を取得
2. **並列処理**: メトリクス取得を並列化（レート制限内で）
3. **キャッシュ**: 取得済みデータのキャッシュ
4. **差分更新**: 新しい投稿のみ取得

---

## 🔧 エラーハンドリング

### 主要なエラーケース

#### 1. 認証エラー
```json
{
  "error": {
    "message": "Invalid OAuth access token",
    "type": "OAuthException",
    "code": 190
  }
}
```
**対処**: アクセストークンの更新

#### 2. レート制限エラー
```json
{
  "error": {
    "message": "Application request limit reached",
    "type": "OAuthException", 
    "code": 4
  }
}
```
**対処**: 1時間待機後リトライ

#### 3. メトリクス利用不可エラー
```json
{
  "error": {
    "message": "The Media Insights API does not support the impressions metric",
    "type": "OAuthException",
    "code": 100
  }
}
```
**対処**: 利用可能メトリクスのみ取得

### エラーハンドリング実装例
```python
import time
from requests.exceptions import HTTPError

def api_call_with_retry(url, params, max_retries=3):
    """レート制限対応APIコール"""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:  # レート制限
                print("レート制限に達しました。1時間待機します...")
                time.sleep(3600)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except HTTPError as e:
            if e.response.status_code == 400:
                # メトリクス利用不可の場合
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', '')
                if 'does not support' in error_msg:
                    print(f"メトリクス利用不可: {error_msg}")
                    return None
            
            if attempt == max_retries - 1:
                raise
            
            time.sleep(2 ** attempt)  # 指数バックオフ
    
    return None
```

---

## 📊 実装チェックリスト

### 必須実装項目
- [ ] 投稿一覧取得機能
- [ ] メトリクス取得機能
- [ ] データベース保存機能
- [ ] エラーハンドリング
- [ ] レート制限対応
- [ ] ページネーション対応

### データ品質確保
- [ ] 必須フィールドの検証
- [ ] データ型変換の実装
- [ ] 重複データの防止
- [ ] NULL値の適切な処理

### パフォーマンス最適化
- [ ] バッチ処理の実装
- [ ] 非同期処理の検討
- [ ] キャッシュ機能の実装
- [ ] インデックスの設定

### 監視・ログ
- [ ] API使用量の監視
- [ ] エラーログの記録
- [ ] データ取得状況の追跡

---

## 🚀 次のステップ

1. **アカウント管理API**: ユーザー情報とプロフィールメトリクス取得
2. **日別統計API**: 月間分析用のデイリーデータ取得
3. **リアルタイム更新**: Webhookを使用したリアルタイムデータ同期

---

## 📚 参考資料

- [Meta for Developers - Instagram Platform](https://developers.facebook.com/docs/instagram-platform/)
- [Instagram Graph API Reference](https://developers.facebook.com/docs/instagram-api/)
- [Media Insights API](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

**検証ファイル**: `/verification/about-post/`  
**最終更新**: 2025-06-25