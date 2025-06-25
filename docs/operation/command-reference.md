# コマンドリファレンス

## 日次データ収集スクリプト

### `collect_daily_data.py`

Instagram の日次データを収集するスクリプトです。

#### 基本構文
```bash
python3 scripts/collect_daily_data.py [OPTIONS]
```

#### オプション一覧

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `--date` | - | 対象日付 (YYYY-MM-DD) | 昨日 |
| `--accounts` | - | 対象アカウント (カンマ区切り) | 全アクティブアカウント |
| `--dry-run` | - | ドライラン実行 | False |
| `--verbose` | - | 詳細ログ出力 | False |
| `--output` | - | 結果のJSON出力先 | なし |

#### 使用例

```bash
# 基本実行（昨日分データ収集）
python3 scripts/collect_daily_data.py

# 特定日付のデータ収集
python3 scripts/collect_daily_data.py --date 2025-06-20

# 特定アカウントのみ
python3 scripts/collect_daily_data.py --accounts 17841402015304577

# 複数アカウント
python3 scripts/collect_daily_data.py --accounts 17841402015304577,18234567890123456

# ドライラン（データベース保存なし）
python3 scripts/collect_daily_data.py --dry-run

# 詳細ログ付き実行
python3 scripts/collect_daily_data.py --verbose

# 結果をJSONファイルに保存
python3 scripts/collect_daily_data.py --output daily_result.json
```

#### 戻り値
- `0`: 成功
- `1`: エラーまたは失敗したアカウントあり
- `130`: ユーザー中断

---

## 過去データ収集スクリプト

### `collect_historical_data.py`

Instagram の過去データを一括収集するスクリプトです。

#### 基本構文
```bash
python3 scripts/collect_historical_data.py --account ACCOUNT_ID [OPTIONS]
```

#### 必須オプション

| オプション | 説明 |
|-----------|------|
| `--account` | Instagram User ID (必須) |

#### 期間指定オプション（排他的）

| オプション | 説明 | 例 |
|-----------|------|---|
| `--days N` | 過去N日間 | `--days 30` |
| `--all-posts` | 全投稿データ | `--all-posts` |
| `--missing-metrics` | メトリクス未取得投稿のメトリクスのみ | `--missing-metrics` |

#### 日付範囲オプション

| オプション | 説明 | 形式 |
|-----------|------|------|
| `--from` | 開始日付 | YYYY-MM-DD |
| `--to` | 終了日付 | YYYY-MM-DD |

#### その他のオプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `--max-posts` | - | 最大投稿数制限 | なし |
| `--no-metrics` | - | メトリクス取得をスキップ | False |
| `--chunk-size` | - | バッチサイズ | 50 |
| `--verbose` | - | 詳細ログ出力 | False |
| `--output` | - | 結果のJSON出力先 | なし |
| `--dry-run` | - | ドライラン実行 | False |
| `--yes` | `-y` | 確認プロンプトをスキップ | False |

#### 使用例

##### 基本的な使用例
```bash
# 過去30日間のデータ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 30 -y

# 過去1週間のデータ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 7 -y

# 全投稿データ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --all-posts -y
```

##### 期間指定
```bash
# 指定期間のデータ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --from 2024-01-01 --to 2024-12-31 -y

# 特定の月のデータ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --from 2024-06-01 --to 2024-06-30 -y
```

##### 制限付き実行
```bash
# 最大100投稿まで
python3 scripts/collect_historical_data.py --account 17841402015304577 --all-posts --max-posts 100 -y

# 投稿データのみ（メトリクスなし）
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 90 --no-metrics -y

# 小さなチャンクサイズで実行（レート制限対策）
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 30 --chunk-size 25 -y
```

##### メトリクス補完
```bash
# メトリクスが未取得の投稿のメトリクスのみ収集
python3 scripts/collect_historical_data.py --account 17841402015304577 --missing-metrics -y
```

##### デバッグ・テスト用
```bash
# ドライラン（データベース保存なし）
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 7 --dry-run

# 詳細ログ付き
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 7 --verbose -y

# 結果をJSONファイルに保存
python3 scripts/collect_historical_data.py --account 17841402015304577 --days 7 --output historical_result.json -y
```

#### 戻り値
- `0`: 成功
- `1`: エラーまたは失敗した投稿あり
- `130`: ユーザー中断

---

## 一般的なワークフロー

### 新規アカウント追加時
```bash
# 1. 過去30日間の基本データ取得
python3 scripts/collect_historical_data.py --account NEW_ACCOUNT_ID --days 30 -y

# 2. 必要に応じて全投稿データ取得
python3 scripts/collect_historical_data.py --account NEW_ACCOUNT_ID --all-posts --max-posts 500 -y

# 3. 日次収集の動作確認
python3 scripts/collect_daily_data.py --accounts NEW_ACCOUNT_ID --dry-run
```

### データ補完作業
```bash
# 1. 欠損期間の特定とデータ再取得
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --from 2025-06-01 --to 2025-06-15 -y

# 2. メトリクス未取得投稿の補完
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --missing-metrics -y

# 3. 補完結果の確認
python3 scripts/collect_daily_data.py --accounts ACCOUNT_ID --dry-run --verbose
```

### 大量データ処理
```bash
# 1. 投稿データのみ高速取得
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --all-posts --no-metrics -y

# 2. メトリクスを分割して取得
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --missing-metrics -y

# 3. 結果確認
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --days 1 --output status.json -y
```

---

## エラーハンドリング

### 一般的なエラーと対処法

#### アクセストークンエラー
```bash
# エラー例
ERROR: Invalid access token

# 対処法: アカウント情報確認
python3 scripts/collect_daily_data.py --accounts ACCOUNT_ID --dry-run --verbose
```

#### レート制限エラー
```bash
# エラー例
WARNING: Rate limit approached

# 対処法: チャンクサイズを小さくして再実行
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --days 30 --chunk-size 10 -y
```

#### ネットワークエラー
```bash
# エラー例
ERROR: Network error during API request

# 対処法: 少し待ってから再実行
sleep 60
python3 scripts/collect_historical_data.py --account ACCOUNT_ID --days 7 -y
```

### デバッグコマンド
```bash
# データベース接続テスト
python3 -c "from app.core.database import test_connection; print('DB OK' if test_connection() else 'DB Error')"

# 環境変数確認
python3 -c "import os; print('DATABASE_URL:', bool(os.getenv('DATABASE_URL')))"

# アカウント情報確認
python3 -c "
from app.core.database import get_db_sync
from app.repositories.instagram_account_repository import InstagramAccountRepository
db = get_db_sync()
repo = InstagramAccountRepository(db)
import asyncio
print(asyncio.run(repo.get_all()))
"
```

---

*最終更新: 2025-06-25*  
*バージョン: 1.0*