# Account Insight Data 収集要件定義書

**作成日**: 2025-07-01  
**対象**: Instagram Daily Stats (アカウントレベル) の毎日自動収集  
**モデル**: `backend/app/models/instagram_daily_stats.py`  

---

## 📋 要件概要

### 目的
全アカウントの日次統計データを毎日自動収集し、`instagram_daily_stats` テーブルにレコードを追加する。

### 収集対象
- **全アクティブアカウント**: `instagram_accounts.is_active = true`
- **実行頻度**: 毎日1回
- **データ内容**: 基本アカウントデータ + 投稿集約データ

---

## 🏗️ ファイル構成

### GitHub Actions ワークフロー
```
.github/workflows/
└── daily-account-insights.yml
```

### スクリプトファイル
```
backend/scripts/
├── github_actions/
│   ├── __init__.py
│   ├── account_insights_collector.py
│   └── shared/
│       ├── __init__.py
│       ├── base_collector.py
│       ├── notification_service.py
│       └── error_handler.py
```

### 設定ファイル
```
backend/config/
└── github_actions/
    └── account_insights_config.py
```

---

## 📁 ワークフローファイル詳細

### `.github/workflows/daily-account-insights.yml`

```yaml
name: Daily Account Insights Collection

on:
  schedule:
    # 毎日 09:00 JST (UTC 00:00)
    - cron: '0 0 * * *'
  workflow_dispatch:
    inputs:
      target_date:
        description: '対象日付 (YYYY-MM-DD, 空の場合は今日)'
        required: false
        type: string
      target_accounts:
        description: '対象アカウント (カンマ区切り, 空の場合は全アカウント)'
        required: false
        type: string
      force_update:
        description: '既存データの強制上書き'
        required: false
        type: boolean
        default: false

jobs:
  collect-account-insights:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
      FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Setup Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
        
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r backend/requirements.txt
        
    - name: Validate environment
      run: |
        cd backend
        python -c "
        import os
        required_vars = ['DATABASE_URL', 'FACEBOOK_APP_ID', 'FACEBOOK_APP_SECRET']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            print(f'Missing required environment variables: {missing}')
            exit(1)
        print('Environment validation passed')
        "
        
    - name: Run account insights collection
      run: |
        cd backend
        python scripts/github_actions/account_insights_collector.py \
          --target-date "${{ github.event.inputs.target_date }}" \
          --target-accounts "${{ github.event.inputs.target_accounts }}" \
          --force-update ${{ github.event.inputs.force_update }} \
          --notify-slack \
          --log-level INFO
          
    - name: Upload execution logs
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: account-insights-logs-${{ github.run_id }}
        path: backend/logs/github_actions/
        retention-days: 30
        
    - name: Notify on failure
      if: failure()
      run: |
        cd backend
        python scripts/github_actions/shared/notification_service.py \
          --type failure \
          --workflow "daily-account-insights" \
          --run-id "${{ github.run_id }}" \
          --message "Account insights collection failed"
```

---

## 🔧 メインスクリプト実装

### `backend/scripts/github_actions/account_insights_collector.py`

```python
#!/usr/bin/env python3
"""
Account Insights Collector for GitHub Actions
アカウントレベルインサイト（Daily Stats）の自動収集

実行例:
    python account_insights_collector.py --notify-slack
    python account_insights_collector.py --target-date 2025-07-01
    python account_insights_collector.py --target-accounts "123,456" --force-update
"""

import asyncio
import sys
import argparse
import logging
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from dataclasses import dataclass, field

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.database import get_db_sync
from app.repositories.instagram_account_repository import InstagramAccountRepository
from app.repositories.instagram_daily_stats_repository import InstagramDailyStatsRepository
from app.services.data_collection.instagram_api_client import InstagramAPIClient

from shared.base_collector import BaseCollector
from shared.notification_service import NotificationService
from shared.error_handler import ErrorHandler

@dataclass
class AccountInsightsResult:
    """アカウントインサイト収集結果"""
    execution_id: str
    target_date: date
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # 実行統計
    total_accounts: int = 0
    successful_accounts: int = 0
    failed_accounts: int = 0
    
    # データ統計
    stats_created: int = 0
    stats_updated: int = 0
    api_calls_made: int = 0
    
    # エラー情報
    errors: List[str] = field(default_factory=list)
    account_results: List[Dict] = field(default_factory=list)

class AccountInsightsCollector(BaseCollector):
    """アカウントインサイト収集クラス"""
    
    def __init__(self):
        super().__init__("account_insights")
        self.notification = NotificationService()
        self.error_handler = ErrorHandler()
        
    async def collect_daily_stats(
        self,
        target_date: date,
        target_accounts: Optional[List[str]] = None,
        force_update: bool = False
    ) -> AccountInsightsResult:
        """メイン処理: 日次統計データ収集"""
        
        execution_id = f"account_insights_{target_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}"
        result = AccountInsightsResult(
            execution_id=execution_id,
            target_date=target_date,
            started_at=datetime.now()
        )
        
        try:
            self.logger.info(f"🚀 Account insights collection started: {execution_id}")
            self.logger.info(f"📅 Target date: {target_date}")
            
            # データベース接続初期化
            await self._init_database()
            
            # 対象アカウント取得
            accounts = await self._get_target_accounts(target_accounts)
            result.total_accounts = len(accounts)
            
            self.logger.info(f"🎯 Target accounts: {result.total_accounts}")
            
            # アカウント別処理
            for account in accounts:
                account_result = await self._collect_account_stats(
                    account, target_date, force_update
                )
                
                result.account_results.append(account_result)
                
                if account_result['success']:
                    result.successful_accounts += 1
                    if account_result['created']:
                        result.stats_created += 1
                    else:
                        result.stats_updated += 1
                    result.api_calls_made += account_result['api_calls']
                else:
                    result.failed_accounts += 1
                    result.errors.append(
                        f"Account {account_result['username']}: {account_result['error']}"
                    )
                
                # アカウント間の待機（API制限対応）
                await asyncio.sleep(5)
            
            result.completed_at = datetime.now()
            
            # 実行結果ログ
            duration = (result.completed_at - result.started_at).total_seconds()
            success_rate = (result.successful_accounts / result.total_accounts * 100) if result.total_accounts > 0 else 0
            
            self.logger.info(f"✅ Collection completed in {duration:.1f}s")
            self.logger.info(f"📊 Success rate: {success_rate:.1f}% ({result.successful_accounts}/{result.total_accounts})")
            self.logger.info(f"📝 Stats created: {result.stats_created}, updated: {result.stats_updated}")
            self.logger.info(f"📞 API calls made: {result.api_calls_made}")
            
            return result
            
        except Exception as e:
            result.completed_at = datetime.now()
            error_msg = f"Critical error in account insights collection: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            return result
            
        finally:
            await self._cleanup_database()

    async def _collect_account_stats(
        self, 
        account, 
        target_date: date, 
        force_update: bool
    ) -> Dict[str, Any]:
        """単一アカウントの統計データ収集"""
        
        account_result = {
            'account_id': account.id,
            'instagram_user_id': account.instagram_user_id,
            'username': account.username,
            'success': False,
            'created': False,
            'api_calls': 0,
            'error': None
        }
        
        try:
            self.logger.info(f"🔄 Processing account: {account.username}")
            
            # 既存データチェック
            daily_stats_repo = InstagramDailyStatsRepository(self.db)
            existing_stats = await daily_stats_repo.get_by_specific_date(account.id, target_date)
            
            if existing_stats and not force_update:
                self.logger.info(f"⏭️ Skipping {account.username}: stats already exist for {target_date}")
                account_result['success'] = True
                account_result['created'] = False
                return account_result
            
            # API経由でデータ収集
            async with InstagramAPIClient() as api_client:
                # 1. 基本アカウントデータ取得
                basic_data = await api_client.get_basic_account_data(
                    account.instagram_user_id,
                    account.access_token_encrypted
                )
                account_result['api_calls'] += 1
                
                # 2. 全投稿データ取得
                all_posts = await self._fetch_all_posts(api_client, account)
                account_result['api_calls'] += 1
                
                # 3. 指定日の投稿をフィルタリング
                target_posts = self._filter_posts_by_date(all_posts, target_date)
                
                # 4. 統計データ計算
                stats_data = await self._calculate_daily_stats(
                    account.id,
                    target_date,
                    basic_data,
                    target_posts
                )
                
                # 5. データベース保存
                if existing_stats:
                    # 更新
                    await daily_stats_repo.update(existing_stats.id, stats_data)
                    account_result['created'] = False
                    self.logger.info(f"✏️ Updated stats for {account.username}: {target_date}")
                else:
                    # 新規作成
                    await daily_stats_repo.create(stats_data)
                    account_result['created'] = True
                    self.logger.info(f"✨ Created stats for {account.username}: {target_date}")
                
                account_result['success'] = True
                
        except Exception as e:
            account_result['error'] = str(e)
            self.logger.error(f"❌ Failed to process account {account.username}: {e}")
        
        return account_result

    async def _fetch_all_posts(self, api_client: InstagramAPIClient, account) -> List[Dict]:
        """全投稿データ取得"""
        url = api_client.config.get_user_media_url(account.instagram_user_id)
        all_posts = []
        next_url = None
        page_count = 0
        max_pages = 20  # 制限を設けて過度なAPI使用を防ぐ
        
        while page_count < max_pages:
            page_count += 1
            
            params = {
                'fields': 'id,media_type,timestamp,like_count,comments_count',
                'access_token': account.access_token_encrypted,
                'limit': 100
            }
            
            try:
                if next_url:
                    response = await api_client._make_request(next_url, {})
                else:
                    response = await api_client._make_request(url, params)
                
                posts = response.get('data', [])
                all_posts.extend(posts)
                
                self.logger.debug(f"Page {page_count}: {len(posts)} posts retrieved")
                
                # 次ページの確認
                paging = response.get('paging', {})
                next_url = paging.get('next')
                
                if not next_url:
                    break
                
                # レート制限対応
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Error fetching posts page {page_count}: {e}")
                break
        
        self.logger.info(f"Retrieved {len(all_posts)} total posts for {account.username}")
        return all_posts

    def _filter_posts_by_date(self, posts: List[Dict], target_date: date) -> List[Dict]:
        """指定日の投稿をフィルタリング"""
        filtered_posts = []
        
        for post in posts:
            timestamp = post.get('timestamp', '')
            if timestamp:
                try:
                    post_date_str = timestamp.split('T')[0]
                    post_date = date.fromisoformat(post_date_str)
                    if post_date == target_date:
                        filtered_posts.append(post)
                except:
                    continue
        
        self.logger.debug(f"Filtered to {len(filtered_posts)} posts for {target_date}")
        return filtered_posts

    async def _calculate_daily_stats(
        self,
        account_id: str,
        target_date: date,
        basic_data: Dict,
        target_posts: List[Dict]
    ) -> Dict[str, Any]:
        """日次統計データ計算"""
        
        # 投稿数・エンゲージメント計算
        posts_count = len(target_posts)
        total_likes = sum(p.get('like_count', 0) for p in target_posts)
        total_comments = sum(p.get('comments_count', 0) for p in target_posts)
        
        avg_likes_per_post = total_likes / posts_count if posts_count > 0 else 0.0
        avg_comments_per_post = total_comments / posts_count if posts_count > 0 else 0.0
        
        # メディアタイプ分布
        media_types = {}
        for post in target_posts:
            media_type = post.get('media_type', 'UNKNOWN')
            media_types[media_type] = media_types.get(media_type, 0) + 1
        
        return {
            'account_id': account_id,
            'stats_date': target_date,
            'followers_count': basic_data.get('followers_count', 0),
            'following_count': basic_data.get('follows_count', 0),
            'media_count': basic_data.get('media_count', 0),
            'posts_count': posts_count,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'media_type_distribution': json.dumps(media_types),
            'data_sources': json.dumps(['github_actions_daily_collection'])
        }

# CLI エントリーポイント
async def main():
    parser = argparse.ArgumentParser(description='Account Insights Collector')
    parser.add_argument('--target-date', help='対象日付 (YYYY-MM-DD)')
    parser.add_argument('--target-accounts', help='対象アカウント (カンマ区切り)')
    parser.add_argument('--force-update', action='store_true', help='既存データの強制上書き')
    parser.add_argument('--notify-slack', action='store_true', help='Slack通知を送信')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='ログレベル')
    
    args = parser.parse_args()
    
    # 対象日付の設定
    if args.target_date:
        try:
            target_date = date.fromisoformat(args.target_date)
        except ValueError:
            print(f"❌ Invalid date format: {args.target_date}")
            return 1
    else:
        target_date = date.today()
    
    # 対象アカウントの設定
    target_accounts = None
    if args.target_accounts:
        target_accounts = [acc.strip() for acc in args.target_accounts.split(',') if acc.strip()]
    
    # ログレベル設定
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 収集実行
    collector = AccountInsightsCollector()
    result = await collector.collect_daily_stats(
        target_date=target_date,
        target_accounts=target_accounts,
        force_update=args.force_update
    )
    
    # 結果表示
    print(f"\n{'='*60}")
    print("📊 ACCOUNT INSIGHTS COLLECTION RESULT")
    print(f"{'='*60}")
    print(f"📅 Target date: {target_date}")
    print(f"🎯 Accounts: {result.successful_accounts}/{result.total_accounts} succeeded")
    print(f"📝 Stats created: {result.stats_created}")
    print(f"✏️ Stats updated: {result.stats_updated}")
    print(f"📞 API calls: {result.api_calls_made}")
    
    if result.errors:
        print(f"❌ Errors ({len(result.errors)}):")
        for error in result.errors[:5]:  # 最初の5個のエラーのみ表示
            print(f"   {error}")
    
    duration = (result.completed_at - result.started_at).total_seconds()
    print(f"⏱️ Duration: {duration:.1f}s")
    print(f"{'='*60}")
    
    # Slack通知
    if args.notify_slack:
        await collector.notification.send_account_insights_result(result)
    
    # 失敗があった場合は exit code 1
    return 1 if result.failed_accounts > 0 else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

---

## 🔧 共通基底クラス

### `backend/scripts/github_actions/shared/base_collector.py`

```python
"""
Base Collector Class for GitHub Actions
GitHub Actions用の共通基底クラス
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import os

from app.core.database import get_db_sync
from app.repositories.instagram_account_repository import InstagramAccountRepository

class BaseCollector:
    """GitHub Actions用コレクターの基底クラス"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.db = None
        self.setup_logging()
        
    def setup_logging(self):
        """ログ設定"""
        log_dir = Path(__file__).parent.parent.parent.parent / "logs" / "github_actions"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{self.service_name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(self.service_name)
        
    async def _init_database(self):
        """データベース接続初期化"""
        if not self.db:
            self.db = get_db_sync()
            self.logger.info("Database connection initialized")
            
    async def _cleanup_database(self):
        """データベース接続クリーンアップ"""
        if self.db:
            self.db.close()
            self.db = None
            self.logger.info("Database connection closed")
            
    async def _get_target_accounts(self, target_accounts: Optional[List[str]] = None):
        """対象アカウント取得"""
        account_repo = InstagramAccountRepository(self.db)
        
        if target_accounts:
            # 指定アカウントのみ
            accounts = []
            for account_id in target_accounts:
                account = await account_repo.get_by_instagram_user_id(account_id)
                if account:
                    accounts.append(account)
                else:
                    self.logger.warning(f"Account not found: {account_id}")
        else:
            # 全アクティブアカウント
            accounts = await account_repo.get_active_accounts()
            
        self.logger.info(f"Target accounts retrieved: {len(accounts)}")
        return accounts
```

---

## 📊 注意点・制約事項

### 1. API制限への対応
```python
# アカウント間の待機時間
await asyncio.sleep(5)  # 5秒間隔

# ページング時の待機時間  
await asyncio.sleep(1)  # 1秒間隔

# 最大API使用量制御
max_pages = 20  # 1アカウントあたり最大20ページ
```

### 2. データ品質保証
```python
# 重複防止
existing_stats = await daily_stats_repo.get_by_specific_date(account.id, target_date)
if existing_stats and not force_update:
    return  # スキップ

# エラーハンドリング
try:
    # 処理
except Exception as e:
    # 個別エラーでも全体処理は継続
    continue
```

### 3. ログ・監視
```python
# 詳細な実行ログ
self.logger.info(f"✅ Collection completed in {duration:.1f}s")
self.logger.info(f"📊 Success rate: {success_rate:.1f}%")

# Slack通知
if args.notify_slack:
    await collector.notification.send_account_insights_result(result)
```

### 4. 設定管理
```yaml
# 環境変数
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
  FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## ✅ 実装チェックリスト

### Phase 1: 基本実装
- [ ] ワークフローファイル作成
- [ ] メインスクリプト実装
- [ ] 共通基底クラス作成
- [ ] 基本的なエラーハンドリング

### Phase 2: 機能強化
- [ ] 通知サービス実装
- [ ] 詳細ログ機能
- [ ] パフォーマンス最適化
- [ ] テストケース作成

### Phase 3: 運用準備
- [ ] 本番環境設定
- [ ] モニタリング設定
- [ ] ドキュメント整備
- [ ] 障害対応手順作成

---

**結論**: この要件定義により、Instagram Daily Stats の安定した自動収集システムを構築できます。毎日決まった時間に全アカウントの統計データを収集し、データベースに蓄積していくことで、長期的なアカウント分析が可能になります。