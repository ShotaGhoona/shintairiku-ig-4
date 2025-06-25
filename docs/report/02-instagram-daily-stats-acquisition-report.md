# Instagram日別統計データ取得レポート

**レポート番号**: 02  
**作成日**: 2025-06-25  
**検証範囲**: Instagram Graph API による日別統計データ取得可能性の包括的調査  
**目的**: バックエンドエンジニアが daily_stats テーブル相当のデータを取得する際の完全なガイド

---

## 📋 要約

Instagram Graph API を使用した日別統計データの取得可能性を包括的に調査しました。既存のDB設計に拘らず、実際に取得可能な全データを検証し、代替案を含む実装戦略を策定しました。

### 主要な発見
- ✅ **合計19要素**のデータが取得可能
- ✅ **Insights API**: 2個のメトリクス（follower_count, reach）
- ✅ **基本フィールド**: 11個のアカウント情報
- ✅ **投稿集約**: 6個の算出可能メトリクス
- ❌ 多くの期待されるメトリクス（profile_views, website_clicks等）は取得不可

---

## 🔍 検証手法

### 実施した調査
1. **エンドポイント探索**: 利用可能なAPI エンドポイントの全数調査
2. **メトリクス検証**: 各メトリクスの期間・パラメータ別詳細テスト
3. **基本フィールド調査**: アカウント情報の取得可能性検証
4. **投稿データ集約**: 投稿データからの日別統計算出可能性

### 検証環境
```
Instagram User ID: 17841455808057230
Account: yamasa_renovation
検証期間: 2025-06-25
API Version: Facebook Graph API v23.0
```

---

## 📊 取得可能データ完全リスト

### 1. Instagram Insights API メトリクス（2個）

#### ✅ follower_count（フォロワー数）
```http
GET https://graph.facebook.com/{ig-user-id}/insights
```

**パラメータ:**
```json
{
  "metric": "follower_count",
  "since": "2025-06-24",
  "until": "2025-06-25", 
  "period": "day",
  "access_token": "{access_token}"
}
```

**レスポンス例:**
```json
{
  "data": [
    {
      "name": "follower_count",
      "period": "day",
      "values": [
        {
          "value": 0,
          "end_time": "2025-06-24T07:00:00+0000"
        }
      ]
    }
  ]
}
```

**特徴:**
- 日別データ: 1件取得可能
- 週別データ: 対応不可
- データ型: integer

#### ✅ reach（リーチ数）
```http
GET https://graph.facebook.com/{ig-user-id}/insights
```

**パラメータ:**
```json
{
  "metric": "reach",
  "since": "2025-06-18",
  "until": "2025-06-25",
  "period": "day",
  "access_token": "{access_token}"
}
```

**レスポンス例:**
```json
{
  "data": [
    {
      "name": "reach", 
      "period": "day",
      "values": [
        {
          "value": 9766,
          "end_time": "2025-06-18T07:00:00+0000"
        },
        {
          "value": 11186,
          "end_time": "2025-06-19T07:00:00+0000"
        }
      ]
    }
  ]
}
```

**特徴:**
- 日別データ: 複数件取得可能（時系列）
- 週別データ: 最大7件取得可能
- データ型: integer

### 2. 基本アカウントフィールド（11個）

#### API エンドポイント
```http
GET https://graph.facebook.com/{ig-user-id}
```

#### 利用可能フィールド一覧

| フィールド | データ型 | 説明 | 日別統計での用途 |
|-----------|---------|------|----------------|
| `id` | string | Instagram User ID | 識別用 |
| `username` | string | ユーザーネーム | 表示用 |
| `name` | string | アカウント名 | 表示用 |
| `ig_id` | integer | Instagram ID（数値） | 識別用 |
| `media_count` | integer | 投稿数 | 日別投稿数計算 |
| `followers_count` | integer | フォロワー数 | **follower_count の代替** |
| `follows_count` | integer | フォロー数 | **following_count の代替** |
| `biography` | string | プロフィール文 | メタ情報 |
| `website` | string | ウェブサイトURL | メタ情報 |
| `profile_picture_url` | string | プロフィール画像URL | 表示用 |
| `is_published` | boolean | 公開状態 | メタ情報 |

#### 一括取得例
```http
GET https://graph.facebook.com/{ig-user-id}?fields=followers_count,follows_count,media_count,username,name
```

**レスポンス例:**
```json
{
  "followers_count": 455,
  "follows_count": 17,
  "media_count": 411,
  "username": "yamasa_renovation",
  "name": "ヤマサリノベ | 鹿児島市 / 姶良市 / 日置市 | リノベーション / リフォーム",
  "id": "17841455808057230"
}
```

### 3. 投稿データ集約メトリクス（6個）

#### データ取得方法
```http
GET https://graph.facebook.com/{ig-user-id}/media
```

**パラメータ:**
```json
{
  "fields": "id,timestamp,media_type,like_count,comments_count",
  "access_token": "{access_token}",
  "limit": 50
}
```

#### 算出可能な日別メトリクス

| メトリクス | 算出方法 | データ型 | 説明 |
|-----------|---------|---------|------|
| `daily_posts_count` | 日別投稿数をカウント | integer | その日の投稿数 |
| `daily_total_likes` | 日別いいね数を合計 | integer | その日投稿されたコンテンツのいいね合計 |
| `daily_total_comments` | 日別コメント数を合計 | integer | その日投稿されたコンテンツのコメント合計 |
| `daily_avg_likes_per_post` | いいね合計 ÷ 投稿数 | decimal | その日の投稿あたり平均いいね数 |
| `daily_avg_comments_per_post` | コメント合計 ÷ 投稿数 | decimal | その日の投稿あたり平均コメント数 |
| `daily_media_type_distribution` | メディアタイプ別集計 | json | VIDEO/CAROUSEL_ALBUM/IMAGE の分布 |

#### 集約処理例（Python）
```python
from datetime import datetime
from collections import defaultdict

def aggregate_posts_by_date(posts):
    daily_stats = defaultdict(lambda: {
        'posts_count': 0,
        'total_likes': 0,
        'total_comments': 0,
        'media_types': set()
    })
    
    for post in posts:
        timestamp = post.get('timestamp', '')
        if timestamp:
            post_date = timestamp.split('T')[0]  # YYYY-MM-DD
            
            daily_stats[post_date]['posts_count'] += 1
            daily_stats[post_date]['total_likes'] += post.get('like_count', 0)
            daily_stats[post_date]['total_comments'] += post.get('comments_count', 0)
            daily_stats[post_date]['media_types'].add(post.get('media_type', 'unknown'))
    
    # 平均値計算
    for date, stats in daily_stats.items():
        if stats['posts_count'] > 0:
            stats['avg_likes_per_post'] = stats['total_likes'] / stats['posts_count']
            stats['avg_comments_per_post'] = stats['total_comments'] / stats['posts_count']
        else:
            stats['avg_likes_per_post'] = 0
            stats['avg_comments_per_post'] = 0
        
        stats['media_type_distribution'] = dict(
            Counter(stats['media_types'])
        )
    
    return daily_stats
```

---

## ❌ 取得不可能なデータ

### 期待されていたが利用不可のメトリクス

| メトリクス | 理由 | エラーメッセージ |
|-----------|------|----------------|
| `impressions` | v22以降廃止 | "Starting from version 22 and above, the impressions metric is no longer supported" |
| `profile_views` | データなし | "should be specified with parameter metric_type=total_value" → データなし |
| `website_clicks` | データなし | "should be specified with parameter metric_type=total_value" → データなし |
| `new_followers` | 利用不可 | "metric[0] must be one of the following values..." |
| `accounts_engaged` | データなし | "should be specified with parameter metric_type=total_value" → データなし |
| `total_interactions` | データなし | "should be specified with parameter metric_type=total_value" → データなし |

### Threads関連メトリクス
```
threads_likes, threads_replies, threads_followers, etc.
→ "is/are not supported on this Instagram account"
```

---

## 💻 実装ガイド

### データ収集戦略

#### 1. 日次データ収集アーキテクチャ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Insights API │    │  Basic Fields   │    │ Post Aggregation│
│                 │    │                 │    │                 │
│ • follower_count│    │ • followers_count│   │ • daily_posts   │
│ • reach         │    │ • follows_count │    │ • daily_likes   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                      ┌─────────────────┐
                      │ Daily Stats DB  │
                      │                 │
                      │ Combined Data   │
                      └─────────────────┘
```

#### 2. 推奨実装順序

##### フェーズ1: 基本実装
```python
def collect_daily_basic_data(instagram_user_id, access_token, target_date):
    """基本的な日別データ収集"""
    
    # 1. 基本アカウント情報取得
    account_data = get_basic_account_fields(instagram_user_id, access_token)
    
    # 2. Insights メトリクス取得
    insights_data = get_insights_metrics(instagram_user_id, access_token, target_date)
    
    # 3. データ統合
    daily_stats = {
        'stats_date': target_date,
        'followers_count': account_data.get('followers_count'),
        'following_count': account_data.get('follows_count'),
        'reach': insights_data.get('reach', 0),
        'follower_count_change': insights_data.get('follower_count', 0)
    }
    
    return daily_stats
```

##### フェーズ2: 投稿集約追加
```python
def collect_daily_comprehensive_data(instagram_user_id, access_token, target_date):
    """包括的な日別データ収集"""
    
    # フェーズ1の基本データ
    daily_stats = collect_daily_basic_data(instagram_user_id, access_token, target_date)
    
    # 投稿データ集約
    posts_data = get_posts_for_date(instagram_user_id, access_token, target_date)
    aggregated_posts = aggregate_posts_by_date(posts_data)
    
    # 投稿集約データを統合
    if target_date in aggregated_posts:
        daily_stats.update({
            'posts_count': aggregated_posts[target_date]['posts_count'],
            'total_likes': aggregated_posts[target_date]['total_likes'], 
            'total_comments': aggregated_posts[target_date]['total_comments'],
            'avg_likes_per_post': aggregated_posts[target_date]['avg_likes_per_post'],
            'avg_comments_per_post': aggregated_posts[target_date]['avg_comments_per_post']
        })
    
    return daily_stats
```

#### 3. API呼び出し関数実装

##### Insights API 呼び出し
```python
def get_insights_metrics(instagram_user_id, access_token, target_date):
    """Insights メトリクス取得"""
    
    url = f"https://graph.facebook.com/{instagram_user_id}/insights"
    
    # 複数メトリクス同時取得
    params = {
        'metric': 'follower_count,reach',
        'since': target_date,
        'until': target_date,
        'period': 'day',
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    # メトリクス値を辞書に変換
    metrics = {}
    for metric_data in data.get('data', []):
        metric_name = metric_data.get('name')
        values = metric_data.get('values', [])
        if values:
            metrics[metric_name] = values[0].get('value', 0)
    
    return metrics
```

##### 基本フィールド取得
```python
def get_basic_account_fields(instagram_user_id, access_token):
    """基本アカウントフィールド取得"""
    
    url = f"https://graph.facebook.com/{instagram_user_id}"
    
    params = {
        'fields': 'followers_count,follows_count,media_count,username,name',
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()
```

#### 4. データベース設計（修正版）

##### 実際に取得可能なデータに基づくテーブル設計
```sql
CREATE TABLE daily_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES instagram_accounts(id),
    stats_date DATE NOT NULL,
    
    -- 基本アカウント情報から取得
    followers_count INTEGER NOT NULL,           -- 基本フィールドから
    following_count INTEGER NOT NULL,           -- 基本フィールドから (follows_count)
    
    -- Insights API から取得
    reach INTEGER DEFAULT 0,                    -- Insights API
    follower_count_change INTEGER DEFAULT 0,   -- Insights API (follower_count)
    
    -- 投稿集約から算出
    posts_count INTEGER DEFAULT 0,             -- 投稿集約
    total_likes INTEGER DEFAULT 0,             -- 投稿集約
    total_comments INTEGER DEFAULT 0,          -- 投稿集約
    avg_likes_per_post DECIMAL(8,2) DEFAULT 0, -- 投稿集約
    avg_comments_per_post DECIMAL(8,2) DEFAULT 0, -- 投稿集約
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(account_id, stats_date)
);

-- インデックス
CREATE INDEX idx_daily_stats_account_date ON daily_stats(account_id, stats_date);
CREATE INDEX idx_daily_stats_date ON daily_stats(stats_date);
```

##### 取得不可能なフィールドの削除
```sql
-- 以下のフィールドは削除
-- profile_views        (取得不可)
-- website_clicks       (取得不可)  
-- new_followers        (取得不可)
```

---

## ⚡ パフォーマンスとレート制限

### API制限
- **基本制限**: 200コール/時間/ユーザー
- **推奨頻度**: 1日1回（早朝実行）
- **必要コール数**: 
  - Insights API: 1コール（複数メトリクス同時取得）
  - 基本フィールド: 1コール
  - 投稿データ: 1コール（50件まで）
  - **合計**: 3コール/日

### 最適化戦略
1. **複数メトリクス同時取得**: `follower_count,reach` を1回のAPIコールで取得
2. **基本フィールド優先**: followers_count は基本フィールドから取得（より安定）
3. **投稿データキャッシュ**: 1日1回取得して集約データを算出
4. **エラー処理**: Insights API が利用不可の場合は基本フィールドで代替

---

## 🔧 エラーハンドリング

### 主要なエラーパターン

#### 1. メトリクスデータなし
```json
{
  "data": [
    {
      "name": "follower_count",
      "values": []
    }
  ]
}
```
**対処**: 基本フィールドの `followers_count` で代替

#### 2. API制限エラー  
```json
{
  "error": {
    "message": "Application request limit reached",
    "type": "OAuthException",
    "code": 4
  }
}
```
**対処**: 1時間待機後リトライ、または基本フィールドで代替

#### 3. メトリクス利用不可
```json
{
  "error": {
    "message": "The following metrics should be specified with parameter metric_type=total_value",
    "type": "OAuthException", 
    "code": 100
  }
}
```
**対処**: そのメトリクスをスキップ、代替データで補完

### エラーハンドリング実装例
```python
def robust_daily_stats_collection(instagram_user_id, access_token, target_date):
    """堅牢な日別データ収集"""
    
    daily_stats = {
        'stats_date': target_date,
        'data_sources': []
    }
    
    try:
        # 1. 基本フィールド取得（最も安定）
        account_data = get_basic_account_fields(instagram_user_id, access_token)
        daily_stats.update({
            'followers_count': account_data.get('followers_count', 0),
            'following_count': account_data.get('follows_count', 0)
        })
        daily_stats['data_sources'].append('basic_fields')
        
    except Exception as e:
        logger.error(f"基本フィールド取得エラー: {e}")
        return None
    
    try:
        # 2. Insights API 取得（オプション）
        insights_data = get_insights_metrics(instagram_user_id, access_token, target_date)
        daily_stats.update({
            'reach': insights_data.get('reach', 0),
            'follower_count_change': insights_data.get('follower_count', 0)
        })
        daily_stats['data_sources'].append('insights_api')
        
    except Exception as e:
        logger.warning(f"Insights API エラー、基本データのみ使用: {e}")
        daily_stats.update({
            'reach': 0,
            'follower_count_change': 0
        })
    
    try:
        # 3. 投稿集約（オプション）
        posts_data = get_posts_for_date(instagram_user_id, access_token, target_date)
        aggregated = aggregate_posts_by_date(posts_data)
        
        if target_date in aggregated:
            daily_stats.update(aggregated[target_date])
            daily_stats['data_sources'].append('post_aggregation')
        
    except Exception as e:
        logger.warning(f"投稿集約エラー: {e}")
    
    return daily_stats
```

---

## 📊 実装チェックリスト

### 必須実装項目
- [ ] 基本アカウントフィールド取得機能
- [ ] Insights API 呼び出し機能
- [ ] 投稿データ取得・集約機能  
- [ ] 日別データ統合処理
- [ ] データベース保存機能
- [ ] エラーハンドリング
- [ ] ログ機能

### データ品質確保
- [ ] NULL値の適切な処理
- [ ] データ型変換の実装
- [ ] 重複データの防止（UNIQUE制約）
- [ ] 日付検証

### パフォーマンス最適化
- [ ] 複数メトリクス同時取得
- [ ] レート制限対応
- [ ] キャッシュ機能（投稿データ）
- [ ] インデックス設定

### 監視・運用
- [ ] API使用量の監視
- [ ] データ収集状況の追跡
- [ ] エラーアラート設定
- [ ] データ品質レポート

---

## 🚀 次のステップ

### 短期（1-2週間）
1. **基本実装**: フェーズ1の実装（基本フィールド + Insights API）
2. **テスト環境構築**: 開発環境でのデータ収集テスト
3. **エラーハンドリング**: 堅牢性の確保

### 中期（1ヶ月）
1. **投稿集約実装**: フェーズ2の実装
2. **運用監視**: ログ・アラート機能
3. **データ品質**: 異常値検知・修正機能

### 長期（3ヶ月）
1. **analytics機能拡張**: ストーリーデータ取得検討
2. **パフォーマンス最適化**: 大量データ処理対応
3. **リアルタイム化**: Webhook活用検討

---

## 📚 参考資料

- [Meta for Developers - Instagram Platform](https://developers.facebook.com/docs/instagram-platform/)
- [Instagram Graph API Reference](https://developers.facebook.com/docs/instagram-api/)
- [Instagram Insights API](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)

**検証ファイル**: `/verification/about-daily-stats/`  
**検証結果**: `/verification/about-daily-stats/output-json/`  
**最終更新**: 2025-06-25