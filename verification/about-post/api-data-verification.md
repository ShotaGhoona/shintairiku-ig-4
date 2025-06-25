# Meta API データ取得検証 - Posts & Post Metrics

## 検証スコープ

Meta Instagram Graph APIを実際に叩いて、設計したDB構造に必要なデータが取得できるかを検証する。

## 検証対象テーブル

### 1. postsテーブル
```sql
posts {
    uuid id PK
    uuid account_id FK  
    string instagram_post_id
    string media_type
    text caption
    string media_url
    timestamp posted_at
    timestamp created_at
}
```

### 2. post_metricsテーブル
```sql
post_metrics {
    uuid id PK
    uuid post_id FK
    integer likes
    integer comments
    integer saves
    integer shares
    integer views
    integer reach
    integer impressions
    decimal engagement_rate
    timestamp recorded_at
}
```

## 検証項目

### ✅ Phase 1: 投稿一覧取得検証
**API エンドポイント**: `GET /{ig-user-id}/media`

**取得すべきフィールド**:
- `id` → `instagram_post_id`
- `media_type` → `media_type`
- `caption` → `caption`
- `media_url` → `media_url`
- `timestamp` → `posted_at`

**検証コード**: `01_get_posts_data.py`

### ✅ Phase 2: 投稿メトリクス取得検証
**API エンドポイント**: `GET /{ig-media-id}/insights`

**取得すべきメトリクス**:
- `likes` → `likes`
- `comments` → `comments`
- `saves` → `saves`
- `shares` → `shares`
- `views` → `views` (2024年新メトリクス)
- `reach` → `reach`
- `impressions` → `impressions`

**検証コード**: `02_get_post_metrics.py`

### ✅ Phase 3: データ統合検証
**目的**: 投稿データとメトリクスを統合してDB構造に適合するか確認

**検証内容**:
- エンゲージメント率の計算: `(likes + comments + saves + shares) / reach * 100`
- データ型の適合性確認
- NULL値・異常値の処理

**検証コード**: `03_data_integration.py`

### ✅ Phase 4: 実際のレスポンス確認
**目的**: APIの実際のレスポンス構造とフィールド値を確認

**検証内容**:
- レスポンスJSONの構造確認
- 各フィールドのデータ型確認
- 利用可能なメトリクス一覧確認

**検証コード**: `04_response_analysis.py`

## 使用する認証情報

```python
# .env file
INSTAGRAM_USER_ID=17841455808057230
USERNAME=yamasa_renovation
ACCESS_TOKEN=EAARrfZCwPTGUBO1rcSMEAEXT6BZA4A8ehn20WxcfQrmg661d96L5PX2lxfzRUCL26T3Vab8ioi0cPbDuuqZCsZBYQ7S1ny1Xm8dFKIoHQlbypJCvgi7erfajPCwfWR9aZBRaQMVNDr6RDfK6er3B7cAdTabtJyLPA5J0VxofcOaC7PyT7aDy2lGMDHVeJVY6ndcMZD
```

## 期待する成果

1. **postsテーブル**: 投稿の基本情報が完全に取得できることを確認
2. **post_metricsテーブル**: 全ての必要なメトリクスが取得できることを確認
3. **データ品質**: 取得データがフロントエンド表示に適していることを確認
4. **API制約**: レート制限や権限で取得できないデータがないかを確認

この検証により、設計したDB構造がMeta APIから実際にデータを取得して運用可能かどうかを判定する。