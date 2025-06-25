# Instagram API 完全ガイド - 公式API種類と取得可能データ一覧

**作成日**: 2025-06-25  
**対象者**: 開発者・データアナリスト・プロダクトマネージャー  
**目的**: Instagram 公式APIの全体像把握とデータ取得戦略策定  

---

## 📋 要約

Instagram（Meta）が提供する公式APIの完全ガイドです。実際のAPI検証に基づき、各APIで取得可能なデータ、制約、実装上の注意点を詳細にまとめています。Instagram分析ツール・ソーシャルメディア管理ツール・マーケティングツールの開発に必要な情報を網羅しています。

---

## 🏗️ Instagram API エコシステム概要

### API体系図
```
Meta for Developers
├── Instagram Graph API (Main)
│   ├── Instagram Business Account (推奨)
│   └── Instagram Creator Account
├── Instagram Basic Display API (個人用・非推奨)
├── Facebook Graph API (Instagram連携)
└── Webhooks (リアルタイム通知)
```

### 認証・権限体系
```
Facebook App
├── Instagram Business Account
│   ├── Facebook Page (必須)
│   └── Long-lived Access Token
├── 権限 (App Review 必要)
│   ├── instagram_basic
│   ├── instagram_manage_insights
│   ├── instagram_manage_comments
│   └── instagram_content_publish
└── レート制限
    ├── 200 calls/hour/user (標準)
    └── 4800 calls/hour/app (最大)
```

---

## 📊 Instagram Graph API（メイン API）

### 基本仕様
- **対象**: Instagram Business Account・Creator Account
- **認証**: Facebook Page との連携必須
- **エンドポイント**: `https://graph.facebook.com/{version}/`
- **現在バージョン**: v23.0 (2025年6月時点)

### 利用可能データカテゴリ

#### 1. アカウント基本情報
| データ | エンドポイント | 権限 | 説明 |
|--------|---------------|------|------|
| アカウントID | `/{ig-user-id}` | instagram_basic | Instagram User ID |
| ユーザーネーム | `/{ig-user-id}?fields=username` | instagram_basic | @から始まるユーザー名 |
| アカウント名 | `/{ig-user-id}?fields=name` | instagram_basic | 表示名 |
| プロフィール画像 | `/{ig-user-id}?fields=profile_picture_url` | instagram_basic | プロフィール画像URL |
| バイオグラフィー | `/{ig-user-id}?fields=biography` | instagram_basic | プロフィール文 |
| ウェブサイト | `/{ig-user-id}?fields=website` | instagram_basic | プロフィールリンク |
| フォロワー数 | `/{ig-user-id}?fields=followers_count` | instagram_basic | フォロワー数 |
| フォロー数 | `/{ig-user-id}?fields=follows_count` | instagram_basic | フォロー中数 |
| 投稿数 | `/{ig-user-id}?fields=media_count` | instagram_basic | 総投稿数 |

**サンプルレスポンス:**
```json
{
  "id": "17841455808057230",
  "username": "example_account",
  "name": "Example Business",
  "followers_count": 1250,
  "follows_count": 180,
  "media_count": 245,
  "biography": "Official account of Example Business",
  "website": "https://example.com",
  "profile_picture_url": "https://scontent.cdninstagram.com/..."
}
```

#### 2. 投稿データ（Media）

##### 投稿一覧取得
```http
GET /{ig-user-id}/media
```

**取得可能フィールド:**
| フィールド | データ型 | 説明 | 全メディア | VIDEO | CAROUSEL | IMAGE |
|-----------|---------|------|----------|-------|----------|-------|
| `id` | string | 投稿ID | ✅ | ✅ | ✅ | ✅ |
| `media_type` | string | メディアタイプ | ✅ | ✅ | ✅ | ✅ |
| `media_url` | string | メディアURL | ✅ | ✅ | ✅ | ✅ |
| `thumbnail_url` | string | サムネイルURL | ❌ | ✅ | ✅ | ❌ |
| `permalink` | string | Instagram投稿URL | ✅ | ✅ | ✅ | ✅ |
| `caption` | string | キャプション | ✅ | ✅ | ✅ | ✅ |
| `timestamp` | string | 投稿日時 | ✅ | ✅ | ✅ | ✅ |
| `username` | string | ユーザーネーム | ✅ | ✅ | ✅ | ✅ |
| `like_count` | integer | いいね数 | ✅ | ✅ | ✅ | ✅ |
| `comments_count` | integer | コメント数 | ✅ | ✅ | ✅ | ✅ |
| `is_comment_enabled` | boolean | コメント有効 | ✅ | ✅ | ✅ | ✅ |
| `shortcode` | string | 短縮コード | ✅ | ✅ | ✅ | ✅ |
| `ig_id` | string | Instagram投稿ID | ✅ | ✅ | ✅ | ✅ |

**メディアタイプ:**
- `VIDEO`: 動画投稿（Reels含む）
- `CAROUSEL_ALBUM`: カルーセル投稿（複数画像・動画）
- `IMAGE`: 単一画像投稿

**サンプルレスポンス:**
```json
{
  "data": [
    {
      "id": "18399578410113164",
      "media_type": "VIDEO",
      "media_url": "https://scontent.cdninstagram.com/...",
      "thumbnail_url": "https://scontent.cdninstagram.com/...",
      "permalink": "https://www.instagram.com/reel/ABC123/",
      "caption": "Check out our latest product!",
      "timestamp": "2025-06-20T10:02:26+0000",
      "username": "example_account",
      "like_count": 125,
      "comments_count": 8,
      "is_comment_enabled": true
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

##### カルーセル投稿の子要素取得
```http
GET /{ig-media-id}/children
```

カルーセル投稿の個別画像・動画を取得可能。

#### 3. 投稿メトリクス（Insights）

##### 基本メトリクス取得
```http
GET /{ig-media-id}/insights
```

**利用可能メトリクス:**

| メトリクス | API名 | データ型 | 全メディア | VIDEO | CAROUSEL | IMAGE | 説明 |
|-----------|-------|---------|----------|-------|----------|-------|------|
| いいね数 | `likes` | integer | ✅ | ✅ | ✅ | ✅ | いいね数 |
| コメント数 | `comments` | integer | ✅ | ✅ | ✅ | ✅ | コメント数 |
| 保存数 | `saved` | integer | ✅ | ✅ | ✅ | ✅ | 保存数 |
| シェア数 | `shares` | integer | ✅ | ✅ | ✅ | ✅ | シェア数 |
| 視聴回数 | `views` | integer | ✅ | ✅ | ✅ | ✅ | 視聴回数 |
| リーチ数 | `reach` | integer | ✅ | ✅ | ✅ | ✅ | リーチしたアカウント数 |
| 総インタラクション | `total_interactions` | integer | ✅ | ✅ | ✅ | ✅ | 全エンゲージメント合計 |
| フォロー数 | `follows` | integer | ❌ | ❌ | ✅ | ❌ | この投稿からのフォロー |
| プロフィール訪問 | `profile_visits` | integer | ❌ | ❌ | ✅ | ❌ | プロフィール訪問数 |
| プロフィール活動 | `profile_activity` | integer | ❌ | ❌ | ✅ | ❌ | プロフィールでの活動 |
| 総視聴時間 | `ig_reels_video_view_total_time` | integer | ❌ | ✅ | ❌ | ❌ | 総視聴時間（ミリ秒） |
| 平均視聴時間 | `ig_reels_avg_watch_time` | integer | ❌ | ✅ | ❌ | ❌ | 平均視聴時間（ミリ秒） |

**❌ 利用不可メトリクス（v22以降）:**
- `impressions`: インプレッション数（廃止済み）

**サンプルレスポンス:**
```json
{
  "data": [
    {
      "name": "likes",
      "period": "lifetime",
      "values": [
        {
          "value": 125
        }
      ],
      "title": "Likes",
      "description": "Total number of likes"
    },
    {
      "name": "reach",
      "period": "lifetime", 
      "values": [
        {
          "value": 1847
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that saw the post"
    }
  ]
}
```

#### 4. アカウントレベルインサイト

##### アカウント統計取得
```http
GET /{ig-user-id}/insights
```

**利用可能メトリクス:**

| カテゴリ | メトリクス | API名 | 期間対応 | 説明 |
|---------|-----------|-------|---------|------|
| **フォロワー** | フォロワー数変化 | `follower_count` | day | 日別フォロワー数変化 |
| **リーチ** | リーチ数 | `reach` | day, week | アカウントリーチ数 |

**期間指定パラメータ:**
```json
{
  "metric": "reach,profile_views",
  "since": "2025-06-20",
  "until": "2025-06-25", 
  "period": "day"
}
```

**❌ 実際の検証で利用不可と判明:**

| メトリクス | API名 | エラー内容 | 検証結果 |
|-----------|-------|-----------|---------|
| プロフィール閲覧 | `profile_views` | metric_type=total_value 必要 | データなし |
| ウェブサイトクリック | `website_clicks` | metric_type=total_value 必要 | データなし |
| 総インタラクション | `total_interactions` | metric_type=total_value 必要 | データなし |
| いいね | `likes` | metric_type=total_value 必要 | データなし |
| コメント | `comments` | metric_type=total_value 必要 | データなし |
| シェア | `shares` | metric_type=total_value 必要 | データなし |
| 保存 | `saves` | metric_type=total_value 必要 | データなし |

**共通パターン:** 多くのメトリクスで `metric_type=total_value` パラメータが必要と表示されるが、実際に指定してもデータが返されない

**✅ 確実に利用可能:**
- `follower_count`: 日別のフォロワー数変化
- `reach`: 日別・週別のリーチ数

#### 5. コメント管理

##### コメント取得
```http
GET /{ig-media-id}/comments
```

**取得可能データ:**
- コメントID
- コメント本文
- コメント投稿者
- 投稿日時
- いいね数
- 返信コメント

##### コメント投稿・削除
```http
POST /{ig-media-id}/comments
DELETE /{ig-comment-id}
```

**必要権限:** `instagram_manage_comments`

#### 6. ハッシュタグ検索

##### ハッシュタグ投稿検索
```http
GET /ig_hashtag_search?q={hashtag}
GET /{ig-hashtag-id}/top_media
GET /{ig-hashtag-id}/recent_media
```

**制限事項:**
- ビジネスアカウントの投稿のみ
- 限定的なデータのみ取得可能

#### 7. メンション取得

##### メンション投稿取得
```http
GET /{ig-user-id}?fields=business_discovery.username({username}){media}
```

**制限事項:**
- 公開アカウントのみ
- 限定的なデータ

---

## 📱 Instagram Basic Display API（個人用・非推奨）

### 概要
- **対象**: 個人アカウント
- **用途**: 個人の写真・動画表示のみ
- **制限**: 分析機能なし、商用利用非推奨
- **現状**: 新規申請受付停止予定

### 取得可能データ
- 基本プロフィール情報
- 投稿画像・動画
- 基本的な投稿情報のみ

**注意**: ビジネス用途では Instagram Graph API の使用が強く推奨されます。

---

## 🔗 Facebook Graph API（Instagram連携）

### Instagram関連エンドポイント

#### Facebook Page経由でのInstagram連携
```http
GET /{page-id}?fields=instagram_business_account
```

#### Instagram投稿のFacebook連携
```http
POST /{page-id}/photos
POST /{page-id}/videos
```

---

## 🔔 Webhooks（リアルタイム通知）

### 利用可能な通知イベント

| イベント | 説明 | 用途 |
|---------|------|------|
| `comments` | 新規コメント | リアルタイム応対 |
| `mentions` | メンション | ブランド監視 |
| `story_insights` | ストーリー統計 | リアルタイム分析 |

### 設定例
```javascript
// Webhook エンドポイント設定
app.post('/webhook', (req, res) => {
  const body = req.body;
  
  if (body.object === 'instagram') {
    body.entry.forEach(entry => {
      entry.changes.forEach(change => {
        if (change.field === 'comments') {
          // 新規コメント処理
          handleNewComment(change.value);
        }
      });
    });
  }
  
  res.status(200).send('EVENT_RECEIVED');
});
```

---

## ⚡ レート制限・制約事項

### API制限

| 制限タイプ | 制限値 | 説明 |
|-----------|-------|------|
| **ユーザーレベル** | 200 calls/hour | 1ユーザーあたりの時間制限 |
| **アプリレベル** | 4,800 calls/hour | 1アプリあたりの時間制限 |
| **同時接続** | 600 calls/600秒 | 短時間での集中アクセス制限 |

### レート制限監視
```http
X-Business-Use-Case-Usage: {
  "business_account_id": [
    {
      "type": "instagram",
      "call_count": 15,
      "total_cputime": 10,
      "total_time": 25,
      "estimated_time_to_regain_access": 0
    }
  ]
}
```

### データ取得制限

#### 投稿データ
- **履歴制限**: 通常2年間程度
- **ページネーション**: 25件/リクエスト（推奨）
- **フィールド制限**: 1リクエストあたり最大指定可能フィールド数

#### インサイトデータ
- **期間制限**: 最大93日間
- **メトリクス制限**: 1リクエストあたり複数メトリクス指定可能
- **リアルタイム性**: 数時間の遅延あり

---

## 🛠️ 実装ベストプラクティス

### 1. 認証・権限管理

#### 長期アクセストークン取得
```python
def get_long_lived_token(short_lived_token):
    """短期トークンを長期トークンに変換"""
    url = "https://graph.facebook.com/oauth/access_token"
    
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token
    }
    
    response = requests.get(url, params=params)
    return response.json()['access_token']
```

#### トークン有効性チェック
```python
def validate_access_token(access_token):
    """アクセストークンの有効性確認"""
    url = f"https://graph.facebook.com/me?access_token={access_token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except:
        return False
```

### 2. エラーハンドリング

#### 主要エラーパターン
```python
def handle_api_errors(response):
    """Instagram API エラーハンドリング"""
    
    if response.status_code == 400:
        error_data = response.json()
        error_code = error_data.get('error', {}).get('code')
        
        if error_code == 100:
            # パラメータエラー
            return "invalid_parameters"
        elif error_code == 190:
            # 認証エラー
            return "invalid_token"
        elif error_code == 4:
            # レート制限
            return "rate_limit_exceeded"
    
    elif response.status_code == 429:
        # レート制限（HTTP レベル）
        return "rate_limit_exceeded"
    
    return "unknown_error"
```

### 3. データ収集最適化

#### バッチ処理実装
```python
def batch_collect_post_insights(post_ids, access_token):
    """複数投稿のインサイトを効率的に取得"""
    
    insights_data = {}
    batch_size = 25  # レート制限を考慮
    
    for i in range(0, len(post_ids), batch_size):
        batch = post_ids[i:i + batch_size]
        
        for post_id in batch:
            try:
                insights = get_post_insights(post_id, access_token)
                insights_data[post_id] = insights
                
                # レート制限対策
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to get insights for {post_id}: {e}")
                continue
    
    return insights_data
```

#### キャッシュ戦略
```python
class InstagramDataCache:
    """Instagram データキャッシュ管理"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = {
            'profile_data': 3600,      # 1時間
            'post_data': 86400,        # 24時間  
            'insights_data': 21600     # 6時間
        }
    
    def get_cached_data(self, key, data_type):
        """キャッシュからデータ取得"""
        cached = self.redis.get(f"instagram:{data_type}:{key}")
        if cached:
            return json.loads(cached)
        return None
    
    def cache_data(self, key, data, data_type):
        """データをキャッシュに保存"""
        cache_key = f"instagram:{data_type}:{key}"
        ttl = self.cache_ttl.get(data_type, 3600)
        
        self.redis.setex(
            cache_key,
            ttl,
            json.dumps(data, ensure_ascii=False)
        )
```

---

## 🎯 用途別実装パターン

### 1. ソーシャルメディア分析ツール

#### 必要API組み合わせ
```python
class InstagramAnalyticsTool:
    """Instagram分析ツール"""
    
    def get_account_overview(self, instagram_user_id):
        """アカウント概要取得"""
        # 基本情報 + 直近30日のインサイト
        account_data = self.get_basic_account_data(instagram_user_id)
        insights_data = self.get_account_insights(instagram_user_id, period='30days')
        
        return {
            'profile': account_data,
            'performance': insights_data
        }
    
    def get_content_performance(self, instagram_user_id, limit=50):
        """コンテンツパフォーマンス分析"""
        posts = self.get_recent_posts(instagram_user_id, limit)
        
        performance_data = []
        for post in posts:
            insights = self.get_post_insights(post['id'])
            performance_data.append({
                'post': post,
                'metrics': insights
            })
        
        return performance_data
```

### 2. コンテンツ管理ツール

#### 投稿スケジューリング
```python
class InstagramContentManager:
    """Instagramコンテンツ管理"""
    
    def schedule_post(self, media_url, caption, publish_time):
        """投稿スケジューリング"""
        # Container作成
        container_id = self.create_media_container(media_url, caption)
        
        # スケジュール設定（外部スケジューラーと連携）
        scheduler.schedule_task(
            task_func=self.publish_container,
            args=[container_id],
            run_time=publish_time
        )
    
    def publish_container(self, container_id):
        """コンテナ公開"""
        url = f"https://graph.facebook.com/{self.user_id}/media_publish"
        
        data = {
            'creation_id': container_id,
            'access_token': self.access_token
        }
        
        response = requests.post(url, data=data)
        return response.json()
```

### 3. カスタマーサポートツール

#### メンション・コメント監視
```python
class InstagramCustomerSupport:
    """Instagramカスタマーサポート"""
    
    def monitor_mentions_and_comments(self):
        """メンション・コメント監視"""
        # Webhook経由でリアルタイム取得
        self.setup_webhooks(['comments', 'mentions'])
        
    def respond_to_comment(self, comment_id, response_text):
        """コメント返信"""
        url = f"https://graph.facebook.com/{comment_id}/replies"
        
        data = {
            'message': response_text,
            'access_token': self.access_token
        }
        
        response = requests.post(url, data=data)
        return response.json()
```

---

## 📊 データ活用戦略

### 1. KPI設定指針

#### 基本KPI
- **エンゲージメント率**: (likes + comments + saves + shares) / reach × 100
- **フォロワー成長率**: 新規フォロワー / 総フォロワー × 100
- **コンテンツ効果**: 投稿タイプ別パフォーマンス比較

#### 高度な分析指標
- **視聴完了率**: (avg_watch_time / video_length) × 100 (VIDEO投稿)
- **プロフィール転換率**: profile_visits / reach × 100 (CAROUSEL投稿)
- **ブランド認知度**: mentions + branded_hashtag_usage

### 2. データ収集頻度推奨

| データタイプ | 推奨頻度 | API使用量 | 用途 |
|-------------|---------|-----------|------|
| **基本アカウント情報** | 1日1回 | 低 | ダッシュボード更新 |
| **投稿データ** | 6時間毎 | 中 | 新規投稿検知 |
| **投稿インサイト** | 1日1回 | 高 | パフォーマンス分析 |
| **アカウントインサイト** | 1日1回 | 低 | トレンド分析 |
| **コメント** | リアルタイム | 低 | カスタマーサポート |

---

## 🔮 将来の展望・制限事項

### API進化の傾向
1. **プライバシー強化**: より厳格な権限管理
2. **商用利用重視**: ビジネス機能の充実
3. **リアルタイム性向上**: Webhook機能拡充
4. **AI統合**: 自動分析機能の追加

### 注意すべき制限
1. **データ保持期間**: 2年程度で過去データにアクセス不可
2. **メトリクス廃止・制限**: 
   - `impressions`: v22以降完全廃止
   - `profile_views`, `website_clicks`: API上は存在するがデータなし
   - アカウントレベルの多くのエンゲージメントメトリクス利用不可
3. **App Review**: 新規権限取得の審査厳格化
4. **料金化可能性**: 将来的な有料化の可能性

### 代替手段・補完戦略
1. **スクレイピング禁止**: 公式API以外の手段は利用規約違反
2. **サードパーティツール**: Hootsuite、Sprout Social等の活用
3. **マルチプラットフォーム**: Twitter、TikTok等の並行活用
4. **独自データ**: ウェブサイト流入等の自社データ統合

---

## 📚 参考資料・リンク

### 公式ドキュメント
- [Meta for Developers](https://developers.facebook.com/)
- [Instagram Graph API Reference](https://developers.facebook.com/docs/instagram-api/)
- [Instagram Platform Policy](https://developers.facebook.com/docs/instagram-platform-policy/)
- [Facebook App Review](https://developers.facebook.com/docs/app-review/)

### 開発者リソース
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/) - API テストツール
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) - トークン検証ツール
- [Webhook Testing](https://developers.facebook.com/tools/webhooks/) - Webhook テストツール

### コミュニティ・サポート
- [Meta Developers Community](https://developers.facebook.com/community/)
- [Stack Overflow - Instagram API](https://stackoverflow.com/questions/tagged/instagram-api)
- [GitHub - Instagram API Examples](https://github.com/topics/instagram-api)

---

**最終更新**: 2025-06-25  
**検証環境**: Instagram Graph API v23.0  
**検証アカウント**: Instagram Business Account