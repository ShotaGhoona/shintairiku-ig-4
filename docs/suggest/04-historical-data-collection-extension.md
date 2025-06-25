# 過去データ取得機能拡張提案

## 概要
現在のPhase 2システムは日次データ収集に特化していますが、初回設定時や遡及データ収集のために過去の投稿データとメトリクスを一括取得する機能が必要です。

## 要件分析

### 取得可能な過去データ
- **投稿データ**: Instagram APIで無制限に遡及可能
- **投稿メトリクス**: 過去の投稿のインサイトデータも取得可能
- **アカウント統計**: 過去の日次統計は取得不可（現在値のみ）

### 制約事項
- **レート制限**: 200コール/時間（既存と同じ）
- **API制限**: メディアインサイトは投稿後一定期間のみ利用可能
- **データ整合性**: 重複データの回避が必要

## 提案アーキテクチャ

### フォルダ構成
```
backend/app/services/
├── data_collection/
│   ├── daily_collector_service.py          # 既存
│   ├── historical_collector_service.py     # 新規：過去データ収集
│   ├── batch_processor_service.py          # 新規：バッチ処理管理
│   └── data_deduplication_service.py       # 新規：重複排除
├── background/
│   ├── historical_sync_job.py              # 新規：過去データ同期ジョブ
│   └── progress_tracker_service.py         # 新規：進捗管理
└── utils/
    ├── date_range_generator.py             # 新規：日付範囲生成
    └── rate_limiter.py                     # 新規：レート制限管理

scripts/
├── collect_daily_data.py                   # 既存
├── collect_historical_data.py              # 新規：過去データ収集スクリプト
└── sync_historical_posts.py               # 新規：投稿データ同期

.github/workflows/
├── daily-data-collection.yml              # 既存
└── historical-data-sync.yml               # 新規：過去データ同期ワークフロー
```

## 実装詳細

### 1. HistoricalCollectorService
**場所**: `app/services/data_collection/historical_collector_service.py`

**機能**:
- 指定期間の過去投稿データ一括取得
- 投稿メトリクスの遡及取得
- 進捗管理とレート制限対応
- エラー時の中断・再開機能

**主要メソッド**:
```python
async def collect_historical_posts(
    account_id: str,
    start_date: date,
    end_date: date = None,
    chunk_size: int = 100
) -> HistoricalCollectionResult

async def collect_post_metrics_batch(
    post_ids: List[str],
    account_id: str
) -> Dict[str, PostMetrics]

async def resume_from_checkpoint(
    collection_id: str
) -> HistoricalCollectionResult
```

### 2. BatchProcessorService
**場所**: `app/services/data_collection/batch_processor_service.py`

**機能**:
- 大量データのチャンク分割処理
- レート制限を考慮した並列処理
- プログレス追跡とチェックポイント機能

**主要メソッド**:
```python
async def process_in_batches(
    items: List[Any],
    processor_func: Callable,
    batch_size: int = 50,
    rate_limit_delay: int = 60
) -> BatchProcessResult

async def create_checkpoint(
    collection_id: str,
    progress_data: Dict
) -> None
```

### 3. DataDeduplicationService
**場所**: `app/services/data_collection/data_deduplication_service.py`

**機能**:
- 既存データとの重複チェック
- 更新対象データの特定
- データマージ処理

**主要メソッド**:
```python
async def find_existing_posts(
    account_id: str,
    instagram_post_ids: List[str]
) -> Dict[str, InstagramPost]

async def merge_post_data(
    existing_post: InstagramPost,
    new_data: Dict
) -> InstagramPost
```

### 4. スクリプト層

#### collect_historical_data.py
**場所**: `scripts/collect_historical_data.py`

**機能**:
```bash
# 過去30日間の投稿データ取得
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 30

# 指定期間の投稿データ取得
python3 scripts/collect_historical_data.py --account 17841402015304577 --from 2024-01-01 --to 2024-12-31

# 全投稿データ取得（レート制限考慮）
python3 scripts/collect_historical_data.py --account 17841402015304577 --all-posts

# 中断された収集の再開
python3 scripts/collect_historical_data.py --resume collection-id-12345
```

**主要機能**:
- コマンドライン引数による柔軟な期間指定
- 進捗表示とETA計算
- エラー時の自動リトライ
- チェックポイントからの再開

#### sync_historical_posts.py
**場所**: `scripts/sync_historical_posts.py`

**機能**:
```bash
# メトリクスが未取得の投稿を検索して取得
python3 scripts/sync_historical_posts.py --account 17841402015304577 --missing-metrics

# 古いメトリクスの更新
python3 scripts/sync_historical_posts.py --account 17841402015304577 --update-older-than 30

# 特定投稿のメトリクス再取得
python3 scripts/sync_historical_posts.py --post-ids 17923488201091269,17923488201091270
```

### 5. GitHub Actions ワークフロー

#### historical-data-sync.yml
**場所**: `.github/workflows/historical-data-sync.yml`

**機能**:
- 手動トリガーによる過去データ収集
- 新規アカウント追加時の初期データ収集
- 週次での投稿メトリクス更新

```yaml
name: Historical Data Sync
on:
  workflow_dispatch:
    inputs:
      account_id:
        description: 'Instagram User ID'
        required: true
      days_back:
        description: 'Days to collect backwards'
        default: '30'
      include_metrics:
        description: 'Include post metrics'
        type: boolean
        default: true

jobs:
  historical-sync:
    runs-on: ubuntu-latest
    steps:
      - name: Collect Historical Data
        run: python3 scripts/collect_historical_data.py --account ${{ inputs.account_id }} --days ${{ inputs.days_back }}
```

## データモデル拡張

### 新規テーブル: collection_progress
```sql
CREATE TABLE collection_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES instagram_accounts(id),
    collection_type VARCHAR(50) NOT NULL, -- 'historical_posts', 'post_metrics'
    start_date DATE,
    end_date DATE,
    total_items INTEGER,
    processed_items INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed', 'paused'
    checkpoint_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 実装フェーズ

### Phase 1: 基本機能
1. `HistoricalCollectorService` 実装
2. `collect_historical_data.py` スクリプト作成
3. 基本的な過去投稿データ取得機能

### Phase 2: 拡張機能
1. `BatchProcessorService` 実装
2. チェックポイント・再開機能
3. 進捗管理とエラーハンドリング

### Phase 3: 自動化
1. GitHub Actions ワークフロー
2. 定期的なメトリクス更新
3. 新規アカウント自動初期化

## レート制限対策

### 戦略
1. **チャンク分割**: 100投稿ずつバッチ処理
2. **待機時間**: API呼び出し間に適切な間隔
3. **優先度制御**: 新しい投稿を優先取得
4. **並列制御**: 複数アカウントの場合の調整

### 推定処理時間
- **100投稿**: 約30分（メトリクス含む）
- **1年分（365投稿）**: 約3時間
- **全履歴（1000投稿）**: 約8時間

## 運用メリット

### 1. 初期セットアップ
- 新規アカウント追加時の過去データ一括取得
- 既存分析との統合

### 2. データ補完
- 欠損データの遡及取得
- システム障害時のデータ復旧

### 3. 分析精度向上
- 長期トレンド分析の精度向上
- より詳細な投稿パフォーマンス分析

## まとめ

この拡張により、日次データ収集システムと並行して過去データも効率的に取得できるようになります。既存のアーキテクチャを活用しつつ、新機能を段階的に追加することで、リスクを最小化して機能拡張を実現できます。