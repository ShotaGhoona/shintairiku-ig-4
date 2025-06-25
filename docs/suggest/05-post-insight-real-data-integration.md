# Post Insight ダミーデータから実データへの置き換え戦略

## 現状分析

### フロントエンド構造
```
frontend/src/feature/post_insight/
├── components/
│   ├── PostInsightChart.tsx    # チャート表示コンポーネント
│   └── PostInsightTable.tsx    # テーブル表示コンポーネント
├── dummy-data/
│   └── dummy-data.ts           # 現在のダミーデータ定義
├── hooks/                      # 空フォルダ
├── services/                   # 空フォルダ
├── types/                      # 空フォルダ
└── index.tsx                   # メインコンポーネント
```

### ダミーデータ構造（現状）
```typescript
interface PostInsight {
  id: string;
  date: string;
  thumbnail: string;
  type: "Story" | "Feed" | "Reels";  // ← 変更予定
  reach: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  engagement_rate: number;
  view_rate?: number; // VIDEOのみ
}
```

### バックエンドデータ構造
```sql
-- instagram_posts テーブル
- instagram_post_id: Instagram投稿ID
- media_type: IMAGE, VIDEO, CAROUSEL_ALBUM, STORY（将来対応）
- caption: キャプション
- media_url: メディアURL
- thumbnail_url: サムネイルURL
- posted_at: 投稿日時

-- instagram_post_metrics テーブル
- likes: いいね数
- comments: コメント数
- saved: 保存数
- shares: シェア数
- views: ビュー数
- reach: リーチ数
- video_view_total_time: 動画視聴時間
- avg_watch_time: 平均視聴時間
```

## Instagram API メディアタイプ

### 標準的な media_type 値
- **IMAGE**: 単一画像投稿
- **VIDEO**: 単一動画投稿（Reels含む）
- **CAROUSEL_ALBUM**: 複数画像・動画のスライド投稿
- **STORY**: ストーリー投稿（将来の日次収集で対応予定）

## データマッピング戦略

### 1. メディアタイプの統一（マッピングなし）
- **変更前**: `Story`, `Feed`, `Reels`
- **変更後**: `IMAGE`, `VIDEO`, `CAROUSEL_ALBUM`, `STORY`
- **メリット**: APIと完全一致、将来のSTORY対応が容易

### 2. エンゲージメント率の計算
- **フロントエンド**: `engagement_rate` として直接使用
- **バックエンド**: 計算式による算出が必要
  ```
  engagement_rate = (likes + comments + shares + saved) / reach * 100
  ```

### 3. 視聴率（view_rate）の計算
- **VIDEO**のみ: `views / reach * 100`
- **その他**: 未定義

### 4. サムネイル画像
- **バックエンド**: `thumbnail_url`（VIDEOのみ存在）
- **フロントエンド**: 全投稿でサムネイル表示が前提
- **対応**: `media_url`をfallbackとして使用

## 実装戦略

### Phase 1: バックエンドAPI設計・実装

#### 1.1. API Endpoint 設計
```
GET /api/posts/insights?account_id={uuid}&from={date}&to={date}&type={type}
```

#### 1.2. レスポンス形式
```typescript
interface PostInsightResponse {
  posts: PostInsightData[];
  summary: {
    totalPosts: number;
    avgEngagementRate: number;
    totalReach: number;
    totalEngagement: number;
  };
}

interface PostInsightData {
  id: string;                    // instagram_post_id
  date: string;                  // posted_at (ISO format)
  thumbnail: string;             // thumbnail_url || media_url
  type: "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM" | "STORY"; // direct from media_type
  reach: number;                 // metrics.reach
  likes: number;                 // metrics.likes
  comments: number;              // metrics.comments
  shares: number;                // metrics.shares
  saves: number;                 // metrics.saved
  views: number;                 // metrics.views
  engagement_rate: number;       // calculated
  view_rate?: number;            // calculated for VIDEO
  video_view_total_time?: number; // for VIDEO
  avg_watch_time?: number;       // for VIDEO
}
```

#### 1.3. ビジネスロジック実装場所
```
backend/app/services/api/
└── post_insight_service.py     # 投稿インサイトAPIサービス
```

### Phase 2: フロントエンド実データ連携

#### 2.1. API Client 作成
```
frontend/src/feature/post_insight/services/
└── postInsightApi.ts           # API呼び出しサービス
```

#### 2.2. Custom Hook 作成
```
frontend/src/feature/post_insight/hooks/
└── usePostInsights.ts          # データフェッチング・状態管理
```

#### 2.3. Type定義更新
```
frontend/src/feature/post_insight/types/
└── postInsight.ts              # 型定義（APIレスポンスと一致）
```

### Phase 3: UI/UX調整

#### 3.1. メディアタイプ対応
- APIの標準形式に統一: `IMAGE`, `VIDEO`, `CAROUSEL_ALBUM`, `STORY`
- フィルタータブも対応する形式に変更
- `STORY`は将来データ対応時まで空状態で表示

#### 3.2. データ表示調整
- サムネイル表示エラー対応
- エンゲージメント率の動的計算表示
- 動画メトリクス（視聴時間）の追加表示

#### 3.3. フィルタリング機能強化
- 日付範囲選択の実装
- アカウント選択機能（将来の複数アカウント対応）

## 実装詳細

### データ変換ロジック

#### メディアタイプ（マッピングなし）
```typescript
// APIのmedia_typeをそのまま使用
type MediaType = "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM" | "STORY";

const validateMediaType = (mediaType: string): MediaType => {
  const validTypes: MediaType[] = ["IMAGE", "VIDEO", "CAROUSEL_ALBUM", "STORY"];
  return validTypes.includes(mediaType as MediaType) 
    ? (mediaType as MediaType) 
    : "IMAGE"; // デフォルト
};
```

#### エンゲージメント率計算
```typescript
const calculateEngagementRate = (
  likes: number,
  comments: number,
  shares: number,
  saves: number,
  reach: number
): number => {
  if (reach === 0) return 0;
  return Number(((likes + comments + shares + saves) / reach * 100).toFixed(2));
};
```

#### 視聴率計算（VIDEO専用）
```typescript
const calculateViewRate = (views: number, reach: number): number => {
  if (reach === 0) return 0;
  return Number((views / reach * 100).toFixed(2));
};
```

### エラーハンドリング戦略

#### 1. 画像読み込みエラー
```typescript
const getThumbnailUrl = (thumbnailUrl?: string, mediaUrl?: string): string => {
  return thumbnailUrl || mediaUrl || '/placeholder-image.jpg';
};
```

#### 2. データ欠損対応
```typescript
const defaultMetrics = {
  likes: 0,
  comments: 0,
  shares: 0,
  saves: 0,
  reach: 0,
  views: 0,
  engagement_rate: 0
};
```

#### 3. API エラー処理
- ローディング状態管理
- エラーメッセージ表示
- リトライ機能

## 期待される改善効果

### 1. データの信頼性向上
- 実際のInstagramデータの反映
- リアルタイムなパフォーマンス分析

### 2. 分析精度向上
- 正確なエンゲージメント率計算
- 実際の投稿パフォーマンス比較

### 3. UX向上
- 実際のサムネイル表示
- より詳細なメトリクス情報
- 柔軟な期間フィルタリング

## 実装スケジュール

### Week 1: バックエンドAPI実装
- PostInsightService実装
- APIエンドポイント作成
- データ変換ロジック実装

### Week 2: フロントエンド連携実装
- API Client実装
- Custom Hook作成
- Type定義更新

### Week 3: UI/UX調整・テスト
- コンポーネント調整
- エラーハンドリング実装
- エンドツーエンドテスト

### Week 4: 最適化・リファクタリング
- パフォーマンス最適化
- コード品質向上
- ドキュメント更新

---

**Next Action**: Phase 1のバックエンドAPI実装から開始