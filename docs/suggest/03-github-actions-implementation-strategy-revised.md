# GitHub Actions 日次データ取得実装戦略 (改訂版)

**作成日**: 2025-06-25  
**基準**: 既存のプロジェクト構造に合わせた実装計画  
**対象**: Instagram API 日次データ取得の自動化  

---

## 📂 現在の構造分析

### 既存プロジェクト構成
```
instagram-analysis-4/
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── api/v1/            # REST API エンドポイント
│   │   ├── core/              # 核となる設定・ユーティリティ
│   │   ├── models/            # SQLAlchemy モデル ✅
│   │   ├── repositories/      # データアクセス層
│   │   ├── schemas/           # Pydantic スキーマ
│   │   ├── services/          # ビジネスロジック
│   │   └── utils/             # ユーティリティ関数
│   ├── main.py                # FastAPI アプリケーション
│   └── requirements.txt
├── frontend/                  # Next.js フロントエンド
├── verification/              # API検証スクリプト ✅
└── docs/                      # ドキュメント ✅
```

---

## 🎯 実装戦略（既存構造活用版）

### 基本方針の修正
- **既存のバックエンド構造を最大限活用**
- **verification/ ディレクトリの知見を活用**
- **FastAPI の services/ 層にデータ取得ロジックを配置**
- **GitHub Actions は実行トリガーとしてシンプルに**

---

## 📁 ファイル配置計画

### 1. GitHub Actions ワークフロー
```
.github/
└── workflows/
    ├── daily-data-collection.yml        # メイン日次実行
    └── manual-data-collection.yml       # 手動実行用
```

### 2. サービス層の責任分離構成
```
backend/app/
├── services/
│   ├── api/                             # フロントエンド向けAPIサービス
│   │   ├── __init__.py
│   │   ├── instagram_account_service.py # アカウント情報API用
│   │   ├── instagram_analytics_service.py # 分析データAPI用
│   │   ├── instagram_post_service.py    # 投稿データAPI用
│   │   └── dashboard_service.py         # ダッシュボードAPI用
│   │
│   ├── data_collection/                 # データ収集専用サービス
│   │   ├── __init__.py
│   │   ├── instagram_api_client.py      # Instagram Graph API クライアント
│   │   ├── daily_collector_service.py   # 日次データ収集サービス
│   │   ├── post_collector_service.py    # 投稿データ収集サービス
│   │   ├── metrics_collector_service.py # メトリクス収集サービス
│   │   └── data_aggregator_service.py   # データ集約処理サービス
│   │
│   └── background/                      # バックグラウンドタスク
│       ├── __init__.py
│       ├── scheduler_service.py         # スケジュール管理
│       ├── monthly_summary_service.py   # 月次サマリー生成
│       └── notification_service.py      # 通知サービス
│
├── repositories/                        # モデルごとに個別ファイル
│   ├── instagram_account_repository.py  # InstagramAccount 専用
│   ├── instagram_post_repository.py     # InstagramPost 専用
│   ├── instagram_post_metrics_repository.py  # InstagramPostMetrics 専用
│   ├── instagram_daily_stats_repository.py   # InstagramDailyStats 専用
│   └── instagram_monthly_stats_repository.py # InstagramMonthlyStats 専用
│
├── schemas/                             # モデルごとに個別ファイル
│   ├── instagram_account_schema.py      # InstagramAccount スキーマ
│   ├── instagram_post_schema.py         # InstagramPost スキーマ
│   ├── instagram_post_metrics_schema.py # InstagramPostMetrics スキーマ
│   ├── instagram_daily_stats_schema.py  # InstagramDailyStats スキーマ
│   └── instagram_monthly_stats_schema.py # InstagramMonthlyStats スキーマ
│
├── core/
│   ├── instagram_config.py              # Instagram API 設定
│   └── database.py                      # DB接続設定（既存拡張）
│
└── utils/
    ├── encryption.py                    # トークン暗号化ユーティリティ
    ├── rate_limiter.py                  # API レート制限管理
    ├── date_utils.py                    # 日付関連ユーティリティ
    └── response_formatter.py           # APIレスポンス整形
```

### 3. データ収集エントリーポイント
```
backend/
├── scripts/
│   └── collect_daily_data.py            # GitHub Actions実行用スクリプト
└── requirements-data-collection.txt     # データ収集専用依存関係
```

---

## 🔧 具体的な実装内容

### 1. GitHub Actions ワークフロー

#### `.github/workflows/daily-data-collection.yml`
```yaml
name: Daily Instagram Data Collection

on:
  schedule:
    - cron: '0 21 * * *'  # 毎日 06:00 JST (21:00 UTC)
  workflow_dispatch:       # 手動実行可能

jobs:
  collect-data:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-data-collection.txt
        
    - name: Run daily data collection
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        INSTAGRAM_ACCESS_TOKENS: ${{ secrets.INSTAGRAM_ACCESS_TOKENS }}
        FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
        FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
      run: |
        cd backend
        python scripts/collect_daily_data.py
        
    - name: Notify on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. データ収集メインスクリプト

#### `backend/scripts/collect_daily_data.py`
```python
"""
日次データ収集のエントリーポイント
GitHub Actions から実行される
"""
import sys
import os
from datetime import datetime, date
import asyncio

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.services.instagram.data_collector import InstagramDataCollector
from app.services.scheduler.daily_tasks import DailyTaskManager
from app.utils.notification import NotificationService
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """メイン実行関数"""
    start_time = datetime.now()
    target_date = date.today()
    
    logger.info(f"Starting daily data collection for {target_date}")
    
    try:
        # データベース接続
        db = next(get_db())
        
        # リポジトリ初期化
        from app.repositories.instagram_account_repository import InstagramAccountRepository
        from app.repositories.instagram_daily_stats_repository import InstagramDailyStatsRepository
        from app.repositories.instagram_monthly_stats_repository import InstagramMonthlyStatsRepository
        
        account_repo = InstagramAccountRepository(db)
        daily_stats_repo = InstagramDailyStatsRepository(db)
        monthly_stats_repo = InstagramMonthlyStatsRepository(db)
        
        # データ収集サービス初期化
        from app.services.data_collection.daily_collector_service import DailyCollectorService
        from app.services.background.scheduler_service import SchedulerService
        from app.services.background.notification_service import NotificationService
        
        data_collector = DailyCollectorService(
            account_repo, daily_stats_repo, monthly_stats_repo
        )
        scheduler = SchedulerService(monthly_stats_repo)
        notification = NotificationService()
        
        # 日次データ収集実行
        results = await data_collector.collect_all_accounts_data(target_date)
        
        # 月次サマリー更新（月末のみ）
        if target_date.day == 1:  # 翌月1日に前月サマリー生成
            await scheduler.generate_monthly_summaries(target_date)
        
        # 実行結果通知
        duration = datetime.now() - start_time
        await notification.send_success_notification(results, duration)
        
        logger.info(f"Daily data collection completed successfully in {duration}")
        
    except Exception as e:
        logger.error(f"Daily data collection failed: {str(e)}")
        
        # エラー通知
        from app.services.background.notification_service import NotificationService
        notification = NotificationService()
        await notification.send_error_notification(str(e))
        
        # GitHub Actions でエラーとして扱う
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. データ収集サービス実装

#### `backend/app/services/data_collection/daily_collector_service.py`
```python
"""
Instagram データ収集サービス
verification/ の知見を活用した実装
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy.orm import Session

from .instagram_api_client import InstagramAPIClient
from .data_aggregator_service import DataAggregatorService
from ...core.instagram_config import InstagramConfig
from ...utils.rate_limiter import RateLimiter
import logging

logger = logging.getLogger(__name__)

class DailyCollectorService:
    """Instagram 日次データ収集サービス"""
    
    def __init__(
        self, 
        account_repo: 'InstagramAccountRepository',
        daily_stats_repo: 'InstagramDailyStatsRepository', 
        monthly_stats_repo: 'InstagramMonthlyStatsRepository'
    ):
        self.account_repo = account_repo
        self.daily_stats_repo = daily_stats_repo
        self.monthly_stats_repo = monthly_stats_repo
        self.api_client = InstagramAPIClient()
        self.aggregator = DataAggregatorService()
        self.rate_limiter = RateLimiter()
        
    async def collect_all_accounts_data(self, target_date: date) -> Dict[str, Any]:
        """全アカウントの日次データ収集"""
        
        # アクティブなアカウント取得
        accounts = await self.account_repo.get_active_accounts()
        
        if not accounts:
            logger.warning("No active Instagram accounts found")
            return {"success": 0, "failed": 0, "accounts": []}
        
        logger.info(f"Found {len(accounts)} active accounts for data collection")
        
        results = {
            "success": 0,
            "failed": 0,
            "accounts": [],
            "api_calls_used": 0
        }
        
        # アカウント並行処理（レート制限考慮）
        semaphore = asyncio.Semaphore(3)  # 最大3並行
        
        tasks = [
            self._collect_account_data_with_limit(account, target_date, semaphore)
            for account in accounts
        ]
        
        account_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果集計
        for i, result in enumerate(account_results):
            if isinstance(result, Exception):
                logger.error(f"Account {accounts[i].username} failed: {result}")
                results["failed"] += 1
                results["accounts"].append({
                    "username": accounts[i].username,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                results["success"] += 1
                results["api_calls_used"] += result.get("api_calls", 0)
                results["accounts"].append(result)
        
        return results
    
    async def _collect_account_data_with_limit(
        self, 
        account, 
        target_date: date, 
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """レート制限を考慮したアカウントデータ収集"""
        
        async with semaphore:
            return await self._collect_account_data(account, target_date)
    
    async def _collect_account_data(self, account, target_date: date) -> Dict[str, Any]:
        """個別アカウントのデータ収集"""
        
        logger.info(f"Collecting data for account: {account.username}")
        
        try:
            # アクセストークン復号化
            access_token = self._decrypt_token(account.access_token_encrypted)
            
            # レート制限チェック
            await self.rate_limiter.check_rate_limit(account.id)
            
            api_calls_count = 0
            data_sources = []
            
            # 1. 基本アカウントデータ取得（最優先）
            basic_data = await self.api_client.get_basic_account_data(
                account.instagram_user_id, 
                access_token
            )
            api_calls_count += 1
            data_sources.append("basic_fields")
            
            # 2. Insights API データ取得（オプション）
            insights_data = {}
            try:
                insights_data = await self.api_client.get_insights_metrics(
                    account.instagram_user_id,
                    access_token,
                    target_date
                )
                api_calls_count += 1
                data_sources.append("insights_api")
            except Exception as e:
                logger.warning(f"Insights API failed for {account.username}: {e}")
                insights_data = {"reach": 0, "follower_count": 0}
            
            # 3. 投稿データ取得・集約（オプション）
            posts_aggregation = {}
            try:
                posts_data = await self.api_client.get_posts_for_date(
                    account.instagram_user_id,
                    access_token,
                    target_date
                )
                api_calls_count += 1
                
                posts_aggregation = self.aggregator.aggregate_daily_posts(
                    posts_data, target_date
                )
                data_sources.append("post_aggregation")
                
            except Exception as e:
                logger.warning(f"Posts aggregation failed for {account.username}: {e}")
                posts_aggregation = {
                    "posts_count": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "avg_likes_per_post": 0,
                    "avg_comments_per_post": 0,
                    "media_type_distribution": "{}"
                }
            
            # 4. 日次統計データ作成
            daily_stats_data = {
                "account_id": account.id,
                "stats_date": target_date,
                "followers_count": basic_data.get("followers_count", 0),
                "following_count": basic_data.get("follows_count", 0),
                "reach": insights_data.get("reach", 0),
                "follower_count_change": insights_data.get("follower_count", 0),
                "data_sources": str(data_sources),
                **posts_aggregation
            }
            
            # 5. データベース保存
            await self.daily_stats_repo.save_daily_stats(daily_stats_data)
            
            # レート制限記録
            await self.rate_limiter.record_api_usage(account.id, api_calls_count)
            
            logger.info(f"Successfully collected data for {account.username}")
            
            return {
                "username": account.username,
                "status": "success",
                "api_calls": api_calls_count,
                "data_sources": data_sources,
                "followers_count": daily_stats_data["followers_count"],
                "posts_count": daily_stats_data["posts_count"]
            }
            
        except Exception as e:
            logger.error(f"Failed to collect data for {account.username}: {str(e)}")
            raise e
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """アクセストークン復号化"""
        from ...utils.encryption import decrypt_token
        return decrypt_token(encrypted_token)
```

### 4. Instagram API クライアント実装

#### `backend/app/services/data_collection/instagram_api_client.py`
```python
"""
Instagram Graph API クライアント
verification/about-daily-stats の知見を活用
"""
import aiohttp
import asyncio
from datetime import date
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class InstagramAPIClient:
    """Instagram Graph API クライアント"""
    
    BASE_URL = "https://graph.facebook.com"
    API_VERSION = "v23.0"
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_basic_account_data(
        self, 
        instagram_user_id: str, 
        access_token: str
    ) -> Dict[str, Any]:
        """基本アカウントデータ取得（最も安定）"""
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/{instagram_user_id}"
        
        params = {
            'fields': 'followers_count,follows_count,media_count,username,name',
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_insights_metrics(
        self,
        instagram_user_id: str,
        access_token: str,
        target_date: date
    ) -> Dict[str, Any]:
        """Insights メトリクス取得（verification結果基準）"""
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/{instagram_user_id}/insights"
        
        params = {
            'metric': 'follower_count,reach',  # 検証で利用可能と確認済み
            'since': target_date.strftime('%Y-%m-%d'),
            'until': target_date.strftime('%Y-%m-%d'),
            'period': 'day',
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # レスポンス解析
                metrics = {}
                for metric_data in data.get('data', []):
                    metric_name = metric_data.get('name')
                    values = metric_data.get('values', [])
                    if values:
                        metrics[metric_name] = values[0].get('value', 0)
                
                return metrics
    
    async def get_posts_for_date(
        self,
        instagram_user_id: str,
        access_token: str,
        target_date: date
    ) -> List[Dict[str, Any]]:
        """指定日の投稿データ取得"""
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/{instagram_user_id}/media"
        
        params = {
            'fields': 'id,timestamp,media_type,like_count,comments_count,caption',
            'access_token': access_token,
            'limit': 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # 指定日の投稿をフィルタリング
                target_date_str = target_date.strftime('%Y-%m-%d')
                daily_posts = []
                
                for post in data.get('data', []):
                    post_date = post.get('timestamp', '').split('T')[0]
                    if post_date == target_date_str:
                        daily_posts.append(post)
                
                return daily_posts
```

---

## 🚀 実装順序（責任分離サービス構成版）

### Phase 1: 基本構造・リポジトリ層構築 (3-4日)
1. **GitHub Actions ワークフロー作成**
2. **5つのリポジトリファイル作成**
   - `instagram_account_repository.py`
   - `instagram_post_repository.py` 
   - `instagram_post_metrics_repository.py`
   - `instagram_daily_stats_repository.py`
   - `instagram_monthly_stats_repository.py`
3. **5つのスキーマファイル作成**
   - `instagram_account_schema.py`
   - `instagram_post_schema.py`
   - `instagram_post_metrics_schema.py` 
   - `instagram_daily_stats_schema.py`
   - `instagram_monthly_stats_schema.py`

### Phase 2: データ収集サービス層実装 (3-4日)
1. **services/data_collection/ ディレクトリ作成**
2. **instagram_api_client.py 実装**
3. **daily_collector_service.py 実装**
4. **data_aggregator_service.py 実装**
5. **InstagramAccountRepository・DailyStatsRepository の基本メソッド実装**
6. **1アカウントでの動作確認**

### Phase 3: バックグラウンドサービス・API サービス (3-4日)
1. **services/background/ ディレクトリ作成**
2. **notification_service.py 実装**
3. **scheduler_service.py 実装**
4. **services/api/ ディレクトリ作成（フロントエンド連携準備）**
5. **残りリポジトリ実装**
6. **複数アカウント並行処理**

### Phase 4: 運用・監視・フロントエンド連携 (2-3日)
1. **エラーハンドリング・レート制限対応強化**
2. **月次サマリー自動生成**
3. **Slack通知・ログ管理**
4. **APIサービス層実装（instagram_analytics_service.py等）**
5. **運用ドキュメント・監視ダッシュボード**

---

## 💡 既存構造活用のメリット

### ✅ 活用できる既存資産
- **models/**: 既に作成済みの5つのSQLAlchemyモデル
- **verification/**: 実際のAPI検証結果とコード
- **backend/app/**: FastAPIの既存アーキテクチャ
- **docs/**: 包括的なAPI調査結果

### ✅ 責任分離サービス構成のメリット
- **明確な責任分離**: データ収集・API・バックグラウンド処理で役割分担
- **保守性**: 各サービスの責任範囲が明確
- **拡張性**: フロントエンド連携とデータ収集が独立して拡張可能
- **テスト性**: 機能別の単体テストが書きやすい
- **チーム開発**: フロントエンド開発者とバックエンド開発者が並行作業可能

### ✅ 段階的実装の利点
- **リスク軽減**: 小さな単位でのテスト・検証
- **早期フィードバック**: 各段階での動作確認
- **柔軟性**: 必要に応じた仕様変更が容易

---

この改訂版戦略により、既存のプロジェクト構造を最大限活用しながら、効率的で保守しやすい日次データ取得システムを構築できます。