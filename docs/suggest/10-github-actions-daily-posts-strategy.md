# GitHub Actions 毎日投稿データ収集戦略

**作成日**: 2025-07-01  
**目的**: GitHub Actionsを使用した毎日のInstagram投稿データ自動収集システムの設計  
**対象**: 新規投稿データ＋メトリクス＋日次統計の定期収集  

---

## 📊 戦略概要

### 基本方針
1. **新規投稿重視**: 前回実行以降の新しい投稿を優先的に収集
2. **メトリクス更新**: 既存投稿のメトリクス（いいね・コメント数）も定期更新
3. **統計自動生成**: 収集データから日次統計を自動算出
4. **データ整合性**: 重複防止と欠損データ補完

### 収集対象データ
1. **新規投稿データ**: 投稿本体情報（画像・動画・キャプション等）
2. **投稿メトリクス**: いいね数・コメント数・ビュー数（API経由）
3. **投稿インサイト**: リーチ・保存・シェア数（API経由）
4. **日次統計**: 投稿数・エンゲージメント集計

---

## 🏗️ システム設計

### アーキテクチャ図
```
GitHub Actions (cron: 毎日複数回)
├── 1. 新規投稿検出・収集 (06:00, 12:00, 18:00, 24:00)
│   ├── 最新投稿データ取得
│   ├── 新規投稿判定・保存
│   ├── 投稿メトリクス収集
│   └── 投稿インサイト収集
├── 2. 既存投稿メトリクス更新 (21:00)
│   ├── 直近7日投稿のメトリクス更新
│   ├── 人気投稿のメトリクス更新
│   └── 古い投稿の定期更新
├── 3. 日次統計生成 (22:00)
│   ├── 当日投稿データ集約
│   ├── エンゲージメント計算
│   ├── メディアタイプ分析
│   └── instagram_daily_stats 更新
└── 4. 週次メンテナンス (日曜 02:00)
    ├── 全投稿メトリクス更新
    ├── データ品質チェック
    └── 統計データ再計算
```

### データフロー詳細
```
新規投稿収集フロー:
1. 最新20件の投稿データ取得 (API 1回)
2. 前回実行時刻との比較で新規投稿判定
3. 新規投稿の詳細データ保存
4. 新規投稿のメトリクス・インサイト収集 (API N回)
5. リアルタイム通知 (新規投稿があった場合)

既存投稿更新フロー:
1. 更新対象投稿の選定
   - 直近7日の全投稿
   - 月間上位エンゲージメント投稿
   - 最終更新から24時間経過投稿
2. 選定投稿のメトリクス・インサイト更新
3. 変更量の分析・アラート

日次統計生成フロー:
1. 当日投稿データの集約
2. エンゲージメント指標計算
3. 前日比・週間比の算出
4. 異常値検出・アラート
5. ダッシュボード用データ準備
```

---

## 📅 実行スケジュール設計

### 複数ワークフロー構成
```yaml
# 1. 新規投稿収集 - 高頻度実行
name: New Posts Collection
schedule:
  - cron: '0 21,3,9,15 * * *'  # 06:00, 12:00, 18:00, 24:00 JST

# 2. メトリクス更新 - 1日1回
name: Posts Metrics Update  
schedule:
  - cron: '0 12 * * *'  # 21:00 JST

# 3. 日次統計生成 - 1日1回
name: Daily Stats Generation
schedule:
  - cron: '0 13 * * *'  # 22:00 JST

# 4. 週次メンテナンス - 週1回
name: Weekly Posts Maintenance
schedule:
  - cron: '0 17 * * 0'  # 日曜 02:00 JST
```

### API使用量計算
```
新規投稿収集 (1日4回):
- 基本データ: 1 call × 5 accounts = 5 calls
- 新規投稿 (平均): 2 posts × 5 accounts = 10 insights calls
- 合計: 15 calls × 4回 = 60 calls/日

メトリクス更新 (1日1回):
- 直近7日投稿: 平均30 posts × 5 accounts = 150 calls
- 制限内で実行 (分割処理)

日次統計生成:
- API使用なし (データベース内計算)

総使用量: 約210 calls/日 (制限200 calls/時間内で分散実行)
```

---

## 🛠️ 実装コンポーネント

### 1. 新規投稿収集ワークフロー

#### `.github/workflows/new-posts-collection.yml`
```yaml
name: New Posts Collection

on:
  schedule:
    - cron: '0 21,3,9,15 * * *'  # 4回/日
  workflow_dispatch:
    inputs:
      target_accounts:
        description: '対象アカウント (カンマ区切り)'
        required: false
        type: string

jobs:
  collect-new-posts:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        
    - name: Collect new posts
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
        FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        cd backend
        python scripts/new_posts_collector.py \
          --accounts "${{ github.event.inputs.target_accounts }}" \
          --notify-new-posts \
          --execution-mode new_posts
          
    - name: Upload logs
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: new-posts-logs-${{ github.run_id }}
        path: backend/logs/
        retention-days: 7
```

### 2. 新規投稿収集スクリプト

#### `backend/scripts/new_posts_collector.py`
```python
#!/usr/bin/env python3
"""
New Instagram Posts Collector
新規Instagram投稿の自動収集とメトリクス取得

Usage:
    python scripts/new_posts_collector.py --execution-mode new_posts
    python scripts/new_posts_collector.py --execution-mode metrics_update
    python scripts/new_posts_collector.py --execution-mode daily_stats
"""

import asyncio
import sys
import argparse
import logging
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class PostCollectionResult:
    """投稿収集結果"""
    execution_id: str
    execution_mode: str  # new_posts, metrics_update, daily_stats
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_accounts: int = 0
    successful_accounts: int = 0
    failed_accounts: int = 0
    
    # 新規投稿収集結果
    new_posts_found: int = 0
    new_posts_saved: int = 0
    new_posts_insights_collected: int = 0
    
    # メトリクス更新結果
    posts_updated: int = 0
    metrics_collected: int = 0
    
    # 日次統計結果
    daily_stats_created: int = 0
    
    total_api_calls: int = 0
    errors: List[str] = field(default_factory=list)
    account_results: List[Dict] = field(default_factory=list)

class NewPostsCollector:
    """新規投稿収集サービス"""
    
    def __init__(self):
        self.db = None
        self.setup_logging()
        
    def setup_logging(self):
        """ログ設定"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    log_dir / f"posts_collection_{datetime.now().strftime('%Y%m%d')}.log"
                )
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def execute(
        self, 
        execution_mode: str,
        target_accounts: Optional[List[str]] = None,
        **kwargs
    ) -> PostCollectionResult:
        """実行モード別のメイン処理"""
        
        execution_id = f"{execution_mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = PostCollectionResult(
            execution_id=execution_id,
            execution_mode=execution_mode,
            started_at=datetime.now()
        )
        
        try:
            self.logger.info(f"🚀 Posts collection started: {execution_mode} - {execution_id}")
            
            # データベース接続
            await self._init_database()
            
            # モード別実行
            if execution_mode == "new_posts":
                await self._collect_new_posts(result, target_accounts)
            elif execution_mode == "metrics_update":
                await self._update_posts_metrics(result, target_accounts)
            elif execution_mode == "daily_stats":
                await self._generate_daily_stats(result, target_accounts)
            elif execution_mode == "weekly_maintenance":
                await self._weekly_maintenance(result, target_accounts)
            else:
                raise ValueError(f"Unknown execution mode: {execution_mode}")
            
            result.completed_at = datetime.now()
            self.logger.info(f"✅ Posts collection completed: {execution_mode}")
            
            return result
            
        except Exception as e:
            result.completed_at = datetime.now()
            result.errors.append(f"Critical error: {str(e)}")
            self.logger.error(f"❌ Posts collection failed: {e}", exc_info=True)
            return result
        
        finally:
            if self.db:
                self.db.close()

    async def _collect_new_posts(
        self, 
        result: PostCollectionResult, 
        target_accounts: Optional[List[str]]
    ):
        """新規投稿収集処理"""
        
        accounts = await self._get_target_accounts(target_accounts)
        result.total_accounts = len(accounts)
        
        self.logger.info(f"📊 New posts collection for {result.total_accounts} accounts")
        
        for account in accounts:
            account_result = await self._collect_account_new_posts(account)
            result.account_results.append(account_result)
            
            if account_result['success']:
                result.successful_accounts += 1
                result.new_posts_found += account_result['new_posts_found']
                result.new_posts_saved += account_result['new_posts_saved']
                result.new_posts_insights_collected += account_result['insights_collected']
                result.total_api_calls += account_result['api_calls']
            else:
                result.failed_accounts += 1
                result.errors.append(
                    f"Account {account_result['account_id']}: {account_result.get('error')}"
                )

    async def _collect_account_new_posts(self, account) -> Dict[str, Any]:
        """単一アカウントの新規投稿収集"""
        
        account_result = {
            'account_id': account.instagram_user_id,
            'username': account.username,
            'success': False,
            'api_calls': 0,
            'new_posts_found': 0,
            'new_posts_saved': 0,
            'insights_collected': 0,
            'error': None
        }
        
        try:
            async with InstagramAPIClient() as api_client:
                # 1. 最新投稿データ取得
                recent_posts = await api_client.get_recent_posts(
                    account.instagram_user_id,
                    account.access_token_encrypted,
                    limit=20  # 最新20件をチェック
                )
                account_result['api_calls'] += 1
                
                # 2. 最後の実行時刻取得
                last_execution = await self._get_last_execution_time(account.id, 'new_posts')
                
                # 3. 新規投稿判定
                new_posts = []
                for post in recent_posts:
                    post_timestamp = self._parse_timestamp(post.get('timestamp'))
                    if post_timestamp and post_timestamp > last_execution:
                        # データベースに存在しないかチェック
                        existing_post = await self._check_post_exists(post['id'])
                        if not existing_post:
                            new_posts.append(post)
                
                account_result['new_posts_found'] = len(new_posts)
                self.logger.info(f"📝 Account {account.username}: {len(new_posts)} new posts found")
                
                # 4. 新規投稿の保存
                for post in new_posts:
                    try:
                        # 投稿データ保存
                        saved_post = await self._save_post_data(account.id, post)
                        if saved_post:
                            account_result['new_posts_saved'] += 1
                            
                            # 投稿インサイト取得・保存
                            insights = await api_client.get_post_insights(
                                post['id'],
                                account.access_token_encrypted,
                                post.get('media_type', 'IMAGE')
                            )
                            account_result['api_calls'] += 1
                            
                            if insights:
                                await self._save_post_insights(saved_post.id, insights)
                                account_result['insights_collected'] += 1
                            
                            # API制限対応
                            await asyncio.sleep(3)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to process new post {post['id']}: {e}")
                        continue
                
                # 5. 実行時刻更新
                await self._update_execution_time(account.id, 'new_posts')
                
                account_result['success'] = True
                
                if new_posts:
                    self.logger.info(
                        f"✅ Account {account.username}: "
                        f"{account_result['new_posts_saved']} new posts saved, "
                        f"{account_result['insights_collected']} insights collected"
                    )
                
        except Exception as e:
            account_result['error'] = str(e)
            self.logger.error(f"❌ Account {account.username} new posts failed: {e}")
        
        return account_result

    async def _update_posts_metrics(
        self, 
        result: PostCollectionResult, 
        target_accounts: Optional[List[str]]
    ):
        """既存投稿のメトリクス更新処理"""
        
        accounts = await self._get_target_accounts(target_accounts)
        result.total_accounts = len(accounts)
        
        self.logger.info(f"📊 Posts metrics update for {result.total_accounts} accounts")
        
        for account in accounts:
            account_result = await self._update_account_posts_metrics(account)
            result.account_results.append(account_result)
            
            if account_result['success']:
                result.successful_accounts += 1
                result.posts_updated += account_result['posts_updated']
                result.metrics_collected += account_result['metrics_collected']
                result.total_api_calls += account_result['api_calls']
            else:
                result.failed_accounts += 1
                result.errors.append(
                    f"Account {account_result['account_id']}: {account_result.get('error')}"
                )

    async def _update_account_posts_metrics(self, account) -> Dict[str, Any]:
        """単一アカウントの投稿メトリクス更新"""
        
        account_result = {
            'account_id': account.instagram_user_id,
            'username': account.username,
            'success': False,
            'api_calls': 0,
            'posts_updated': 0,
            'metrics_collected': 0,
            'error': None
        }
        
        try:
            # 更新対象投稿の選定
            target_posts = await self._select_posts_for_update(account.id)
            
            self.logger.info(f"📈 Account {account.username}: updating {len(target_posts)} posts")
            
            async with InstagramAPIClient() as api_client:
                for post in target_posts:
                    try:
                        # 投稿の基本メトリクス取得（最新のいいね・コメント数）
                        post_data = await api_client.get_post_data(
                            post.instagram_post_id,
                            account.access_token_encrypted
                        )
                        account_result['api_calls'] += 1
                        
                        # 投稿インサイト取得
                        insights = await api_client.get_post_insights(
                            post.instagram_post_id,
                            account.access_token_encrypted,
                            post.media_type
                        )
                        account_result['api_calls'] += 1
                        
                        # データベース更新
                        if post_data:
                            await self._update_post_basic_metrics(post.id, post_data)
                            account_result['posts_updated'] += 1
                        
                        if insights:
                            await self._update_post_insights(post.id, insights)
                            account_result['metrics_collected'] += 1
                        
                        # API制限対応 (重要: メトリクス更新は大量実行のため)
                        await asyncio.sleep(4)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to update post {post.instagram_post_id}: {e}")
                        continue
            
            account_result['success'] = True
            self.logger.info(
                f"✅ Account {account.username}: "
                f"{account_result['posts_updated']} posts updated, "
                f"{account_result['metrics_collected']} insights updated"
            )
            
        except Exception as e:
            account_result['error'] = str(e)
            self.logger.error(f"❌ Account {account.username} metrics update failed: {e}")
        
        return account_result

    async def _select_posts_for_update(self, account_id: str) -> List:
        """メトリクス更新対象投稿の選定"""
        
        # 更新優先度の設定
        update_criteria = [
            # 1. 直近7日の全投稿
            {
                'name': 'recent_posts',
                'query': 'posted_at >= NOW() - INTERVAL \'7 days\'',
                'priority': 1
            },
            # 2. 月間上位エンゲージメント投稿 (トップ20)
            {
                'name': 'top_engagement',
                'query': '''
                    posted_at >= NOW() - INTERVAL '30 days'
                    ORDER BY (
                        SELECT COALESCE(likes, 0) + COALESCE(comments, 0) 
                        FROM instagram_post_metrics 
                        WHERE post_id = instagram_posts.id 
                        ORDER BY recorded_at DESC LIMIT 1
                    ) DESC
                    LIMIT 20
                ''',
                'priority': 2
            },
            # 3. 最終更新から24時間経過投稿
            {
                'name': 'outdated_metrics',
                'query': '''
                    posted_at >= NOW() - INTERVAL '30 days'
                    AND id NOT IN (
                        SELECT post_id FROM instagram_post_metrics 
                        WHERE recorded_at >= NOW() - INTERVAL '24 hours'
                    )
                ''',
                'priority': 3
            }
        ]
        
        selected_posts = []
        total_selected = 0
        max_posts_per_account = 50  # API制限を考慮
        
        for criteria in update_criteria:
            if total_selected >= max_posts_per_account:
                break
                
            posts = await self._query_posts_by_criteria(account_id, criteria['query'])
            remaining_slots = max_posts_per_account - total_selected
            
            # 既に選択済みの投稿を除外
            new_posts = [p for p in posts if p not in selected_posts][:remaining_slots]
            selected_posts.extend(new_posts)
            total_selected += len(new_posts)
            
            self.logger.debug(
                f"Selected {len(new_posts)} posts from criteria: {criteria['name']}"
            )
        
        return selected_posts

    async def _generate_daily_stats(
        self, 
        result: PostCollectionResult, 
        target_accounts: Optional[List[str]]
    ):
        """日次統計生成処理"""
        
        accounts = await self._get_target_accounts(target_accounts)
        result.total_accounts = len(accounts)
        
        target_date = date.today()
        self.logger.info(f"📊 Daily stats generation for {target_date}")
        
        for account in accounts:
            try:
                # 既存の日次統計作成関数を流用
                daily_stats = await self._create_daily_stats_from_posts(
                    account.id, target_date, target_date
                )
                
                if daily_stats['success_days'] > 0:
                    result.daily_stats_created += 1
                    result.successful_accounts += 1
                    
                    self.logger.info(
                        f"✅ Account {account.username}: daily stats created for {target_date}"
                    )
                else:
                    result.failed_accounts += 1
                    result.errors.append(f"Account {account.username}: failed to create daily stats")
                    
            except Exception as e:
                result.failed_accounts += 1
                result.errors.append(f"Account {account.username}: {str(e)}")
                self.logger.error(f"❌ Daily stats failed for {account.username}: {e}")

    async def send_new_posts_notification(self, result: PostCollectionResult):
        """新規投稿通知 (投稿があった場合のみ)"""
        if not SLACK_WEBHOOK_URL or result.new_posts_found == 0:
            return
        
        try:
            message = {
                "text": f"🆕 New Instagram Posts Detected!",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {
                                "title": "New Posts Summary",
                                "value": f"📝 {result.new_posts_found} new posts found\n💾 {result.new_posts_saved} posts saved\n📊 {result.new_posts_insights_collected} insights collected",
                                "short": False
                            }
                        ]
                    }
                ]
            }
            
            # アカウント別詳細
            for account_result in result.account_results:
                if account_result.get('new_posts_found', 0) > 0:
                    message["attachments"][0]["fields"].append({
                        "title": f"@{account_result['username']}",
                        "value": f"{account_result['new_posts_found']} new posts",
                        "short": True
                    })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(SLACK_WEBHOOK_URL, json=message) as response:
                    if response.status == 200:
                        self.logger.info("📢 New posts notification sent")
                        
        except Exception as e:
            self.logger.error(f"❌ New posts notification error: {e}")

# CLI エントリーポイント
async def main():
    parser = argparse.ArgumentParser(description='Instagram Posts Collector')
    parser.add_argument('--execution-mode', 
                       choices=['new_posts', 'metrics_update', 'daily_stats', 'weekly_maintenance'],
                       required=True, help='実行モード')
    parser.add_argument('--accounts', help='対象アカウント (カンマ区切り)')
    parser.add_argument('--notify-new-posts', action='store_true', help='新規投稿をSlack通知')
    parser.add_argument('--notify-results', action='store_true', help='実行結果をSlack通知')
    
    args = parser.parse_args()
    
    collector = NewPostsCollector()
    
    target_accounts = None
    if args.accounts:
        target_accounts = [acc.strip() for acc in args.accounts.split(',') if acc.strip()]
    
    result = await collector.execute(
        execution_mode=args.execution_mode,
        target_accounts=target_accounts
    )
    
    # 結果表示
    print(f"\n{'='*60}")
    print(f"📊 POSTS COLLECTION RESULT - {args.execution_mode.upper()}")
    print(f"{'='*60}")
    print(f"🎯 Accounts: {result.successful_accounts}/{result.total_accounts} succeeded")
    
    if args.execution_mode == 'new_posts':
        print(f"🆕 New posts found: {result.new_posts_found}")
        print(f"💾 New posts saved: {result.new_posts_saved}")
        print(f"📊 Insights collected: {result.new_posts_insights_collected}")
    elif args.execution_mode == 'metrics_update':
        print(f"📈 Posts updated: {result.posts_updated}")
        print(f"📊 Metrics collected: {result.metrics_collected}")
    elif args.execution_mode == 'daily_stats':
        print(f"📋 Daily stats created: {result.daily_stats_created}")
    
    print(f"📞 API calls: {result.total_api_calls}")
    
    if result.errors:
        print(f"❌ Errors: {len(result.errors)}")
        for error in result.errors[:3]:
            print(f"   {error}")
    
    duration = (result.completed_at - result.started_at).total_seconds()
    print(f"⏱️ Duration: {duration:.1f}s")
    print(f"{'='*60}")
    
    # 通知送信
    if args.notify_new_posts and args.execution_mode == 'new_posts':
        await collector.send_new_posts_notification(result)
    
    if args.notify_results:
        await collector.send_execution_notification(result)
    
    # 失敗があった場合は exit code 1
    return 1 if result.failed_accounts > 0 else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

### 3. メトリクス更新ワークフロー

#### `.github/workflows/posts-metrics-update.yml`
```yaml
name: Posts Metrics Update

on:
  schedule:
    - cron: '0 12 * * *'  # 21:00 JST
  workflow_dispatch:

jobs:
  update-metrics:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        
    - name: Update posts metrics
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
        FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        cd backend
        python scripts/new_posts_collector.py \
          --execution-mode metrics_update \
          --notify-results
```

### 4. 日次統計生成ワークフロー

#### `.github/workflows/daily-stats-generation.yml`
```yaml
name: Daily Stats Generation

on:
  schedule:
    - cron: '0 13 * * *'  # 22:00 JST
  workflow_dispatch:

jobs:
  generate-stats:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        
    - name: Generate daily stats
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: |
        cd backend
        python scripts/new_posts_collector.py \
          --execution-mode daily_stats \
          --notify-results
```

---

## 📊 データ品質管理

### 1. 重複防止機能
```python
async def _check_post_exists(self, instagram_post_id: str) -> bool:
    """投稿の重複チェック"""
    existing_post = await self.post_repo.get_by_instagram_post_id(instagram_post_id)
    return existing_post is not None

async def _handle_duplicate_detection(self, post_data: Dict) -> str:
    """重複検出時の処理"""
    # 既存投稿のメトリクス更新
    # タイムスタンプ比較で最新データかチェック
    # 必要に応じて上書き更新
```

### 2. データ整合性チェック
```python
async def _validate_post_data(self, post_data: Dict) -> bool:
    """投稿データの妥当性検証"""
    required_fields = ['id', 'timestamp', 'media_type']
    
    for field in required_fields:
        if not post_data.get(field):
            self.logger.warning(f"Missing required field: {field}")
            return False
    
    # タイムスタンプ形式チェック
    try:
        self._parse_timestamp(post_data['timestamp'])
    except:
        self.logger.warning(f"Invalid timestamp format: {post_data['timestamp']}")
        return False
    
    return True
```

### 3. 欠損データ補完
```python
async def _handle_missing_metrics(self, post_id: str):
    """メトリクス欠損時の補完処理"""
    # 基本メトリクスが取得できない場合のデフォルト値設定
    # 過去のメトリクス履歴からの推定
    # 手動確認フラグの設定
```

---

## 📈 パフォーマンス最適化

### 1. API制限最適化
```python
class APIRateLimiter:
    """API制限管理クラス"""
    
    def __init__(self):
        self.calls_per_hour = 200
        self.calls_made = 0
        self.hour_start = datetime.now()
    
    async def wait_if_needed(self):
        """必要に応じて待機"""
        current_time = datetime.now()
        
        # 1時間経過したらリセット
        if (current_time - self.hour_start).seconds >= 3600:
            self.calls_made = 0
            self.hour_start = current_time
        
        # 制限に近づいた場合は待機
        if self.calls_made >= self.calls_per_hour - 10:
            wait_time = 3600 - (current_time - self.hour_start).seconds
            if wait_time > 0:
                await asyncio.sleep(wait_time)
```

### 2. 並列処理最適化
```python
async def _process_accounts_parallel(self, accounts: List, max_concurrent: int = 2):
    """アカウント並列処理"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(account):
        async with semaphore:
            result = await self._process_account(account)
            # アカウント間の適切な間隔
            await asyncio.sleep(10)
            return result
    
    tasks = [process_with_limit(account) for account in accounts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

---

## 🔔 通知・アラート設計

### 1. 新規投稿リアルタイム通知
```json
{
  "text": "🆕 New Instagram Posts Detected!",
  "attachments": [
    {
      "color": "good",
      "fields": [
        {
          "title": "@username",
          "value": "2 new posts",
          "short": true
        }
      ]
    }
  ]
}
```

### 2. エラー・異常検知アラート
```json
{
  "text": "⚠️ Instagram Collection Alert",
  "attachments": [
    {
      "color": "warning",
      "fields": [
        {
          "title": "API Rate Limit Warning",
          "value": "Approaching 200 calls/hour limit",
          "short": false
        }
      ]
    }
  ]
}
```

### 3. 週次サマリーレポート
```json
{
  "text": "📊 Weekly Instagram Collection Report",
  "attachments": [
    {
      "color": "good",
      "fields": [
        {
          "title": "Collection Summary (Week)",
          "value": "🆕 142 new posts\n📈 1,580 metrics updated\n📊 35 daily stats generated",
          "short": false
        }
      ]
    }
  ]
}
```

---

## 🚀 段階的ロールアウト計画

### Phase 1: 新規投稿収集 (Week 1)
1. ✅ 新規投稿検出ロジック実装
2. ✅ 基本的な投稿データ保存
3. ✅ 新規投稿通知機能
4. ✅ 手動実行でのテスト

### Phase 2: メトリクス収集強化 (Week 2)
1. ✅ 投稿インサイト収集実装
2. ✅ メトリクス更新優先度設定
3. ✅ API制限対応強化
4. ✅ エラーハンドリング改善

### Phase 3: 自動統計生成 (Week 3)
1. ✅ 日次統計自動生成
2. ✅ データ品質チェック機能
3. ✅ 異常値検出・アラート
4. ✅ 週次メンテナンス実装

### Phase 4: 運用最適化 (Week 4)
1. ✅ パフォーマンス監視
2. ✅ 自動スケーリング
3. ✅ レポート自動生成
4. ✅ ダッシュボード連携

---

## ⚠️ 運用上の注意点

### 1. API制限管理
- 新規投稿収集: 60 calls/日
- メトリクス更新: 150 calls/日
- 合計: 210 calls/日 (制限内で余裕あり)

### 2. ストレージ考慮
- 画像/動画ファイルはURLのみ保存
- メタデータのみデータベース保存
- 古いメトリクス履歴の定期削除

### 3. 障害時の対応
- 部分的失敗時の継続処理
- 手動復旧用スクリプト準備
- データバックアップ戦略

---

**結論**: この戦略により、新規投稿の即座な検出から既存投稿のメトリクス維持、統計データの自動生成まで、包括的なInstagram投稿データ収集システムを構築できます。GitHub Actionsの複数ワークフローを活用し、効率的で信頼性の高いデータ収集を実現します。