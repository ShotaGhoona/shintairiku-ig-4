# Post Insight Data 収集要件定義書

**作成日**: 2025-07-01  
**対象**: Instagram 新規投稿データ＋インサイトの24時間以内自動収集  
**モデル**: `backend/app/models/instagram_post.py`, `backend/app/models/instagram_post_metrics.py`  

---

## 📋 要件概要

### 目的
24時間以内に投稿された新規投稿を検出し、投稿データとインサイトを自動収集する。

### 収集タイミング
- **検出頻度**: 1日2回 (06:00, 18:00 JST)
- **検出範囲**: 前回実行時刻以降の新規投稿
- **対象**: 全アクティブアカウント

### 収集対象データ
1. **投稿基本データ**: `instagram_post` テーブル
2. **投稿インサイト**: `instagram_post_metrics` テーブル

---

## 🏗️ ファイル構成

### GitHub Actions ワークフロー
```
.github/workflows/
└── new-posts-detection.yml
```

### スクリプトファイル
```
backend/scripts/
├── github_actions/
│   ├── new_posts_collector.py
│   └── shared/
│       ├── post_detector.py
│       ├── post_processor.py
│       └── execution_tracker.py
```

### 実行状態管理
```
backend/data/
└── execution_state/
    └── new_posts_last_execution.json
```

---

## 📁 ワークフローファイル詳細

### `.github/workflows/new-posts-detection.yml`

```yaml
name: New Posts Detection & Collection

on:
  schedule:
    # 1日4回実行: 06:00, 12:00, 18:00, 24:00 JST (UTC -9h)
    - cron: '0 21 * * *'  # 06:00 JST
    - cron: '0 9 * * *'   # 18:00 JST
  workflow_dispatch:
    inputs:
      target_accounts:
        description: '対象アカウント (カンマ区切り, 空の場合は全アカウント)'
        required: false
        type: string
      check_hours_back:
        description: '遡及時間 (時間, デフォルト: 8)'
        required: false
        type: number
        default: 8
      force_reprocess:
        description: '既存投稿の再処理を強制実行'
        required: false
        type: boolean
        default: false

jobs:
  detect-new-posts:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
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
        
    - name: Create execution state directory
      run: |
        mkdir -p backend/data/execution_state
        
    - name: Load previous execution state
      id: load-state
      run: |
        cd backend
        if [ -f "data/execution_state/new_posts_last_execution.json" ]; then
          echo "Previous execution state found"
          cat data/execution_state/new_posts_last_execution.json
        else
          echo "No previous execution state found - first run"
        fi
        
    - name: Run new posts detection
      run: |
        cd backend
        python scripts/github_actions/new_posts_collector.py \
          --target-accounts "${{ github.event.inputs.target_accounts }}" \
          --check-hours-back ${{ github.event.inputs.check_hours_back || 8 }} \
          --force-reprocess ${{ github.event.inputs.force_reprocess }} \
          --notify-new-posts \
          --log-level INFO
          
    - name: Save execution state
      if: always()
      run: |
        cd backend
        # 実行状態の保存（成功・失敗問わず）
        python -c "
        import json
        from datetime import datetime
        
        state = {
            'last_execution_time': datetime.now().isoformat(),
            'execution_id': '${{ github.run_id }}',
            'workflow_run': '${{ github.run_number }}',
            'trigger': '${{ github.event_name }}'
        }
        
        with open('data/execution_state/new_posts_last_execution.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        print('Execution state saved')
        "
        
    - name: Commit execution state
      if: always()
      run: |
        cd backend
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/execution_state/new_posts_last_execution.json
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Update new posts execution state [skip ci]"
          git push
        fi
        
    - name: Upload execution logs
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: new-posts-logs-${{ github.run_id }}
        path: backend/logs/github_actions/
        retention-days: 14
        
    - name: Notify on failure
      if: failure()
      run: |
        cd backend
        python scripts/github_actions/shared/notification_service.py \
          --type failure \
          --workflow "new-posts-detection" \
          --run-id "${{ github.run_id }}" \
          --message "New posts detection failed"
```

---

## 🔧 メインスクリプト実装

### `backend/scripts/github_actions/new_posts_collector.py`

```python
#!/usr/bin/env python3
"""
New Posts Collector for GitHub Actions
24時間以内の新規投稿検出・収集

実行例:
    python new_posts_collector.py --notify-new-posts
    python new_posts_collector.py --target-accounts "123,456" --check-hours-back 6
    python new_posts_collector.py --force-reprocess
"""

import asyncio
import sys
import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from dataclasses import dataclass, field

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.database import get_db_sync
from app.repositories.instagram_account_repository import InstagramAccountRepository
from app.repositories.instagram_post_repository import InstagramPostRepository
from app.repositories.instagram_post_metrics_repository import InstagramPostMetricsRepository
from app.services.data_collection.instagram_api_client import InstagramAPIClient

from shared.base_collector import BaseCollector
from shared.notification_service import NotificationService
from shared.post_detector import PostDetector
from shared.post_processor import PostProcessor
from shared.execution_tracker import ExecutionTracker

@dataclass
class NewPostsResult:
    """新規投稿収集結果"""
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # 実行統計
    total_accounts: int = 0
    successful_accounts: int = 0
    failed_accounts: int = 0
    
    # 検出統計
    total_posts_checked: int = 0
    new_posts_found: int = 0
    new_posts_saved: int = 0
    insights_collected: int = 0
    
    # API使用統計
    api_calls_made: int = 0
    
    # エラー情報
    errors: List[str] = field(default_factory=list)
    account_results: List[Dict] = field(default_factory=list)
    new_posts_details: List[Dict] = field(default_factory=list)

class NewPostsCollector(BaseCollector):
    """新規投稿収集クラス"""
    
    def __init__(self):
        super().__init__("new_posts")
        self.notification = NotificationService()
        self.post_detector = PostDetector()
        self.post_processor = PostProcessor()
        self.execution_tracker = ExecutionTracker()
        
    async def detect_and_collect(
        self,
        target_accounts: Optional[List[str]] = None,
        check_hours_back: int = 8,
        force_reprocess: bool = False
    ) -> NewPostsResult:
        """メイン処理: 新規投稿検出・収集"""
        
        execution_id = f"new_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = NewPostsResult(
            execution_id=execution_id,
            started_at=datetime.now()
        )
        
        try:
            self.logger.info(f"🚀 New posts detection started: {execution_id}")
            
            # 前回実行時刻の取得
            last_execution_time = self.execution_tracker.get_last_execution_time()
            
            # チェック開始時刻の決定
            if last_execution_time and not force_reprocess:
                check_from = last_execution_time
                self.logger.info(f"📅 Checking posts since last execution: {check_from}")
            else:
                check_from = datetime.now() - timedelta(hours=check_hours_back)
                self.logger.info(f"📅 Checking posts from {check_hours_back} hours back: {check_from}")
            
            # データベース接続初期化
            await self._init_database()
            
            # 対象アカウント取得
            accounts = await self._get_target_accounts(target_accounts)
            result.total_accounts = len(accounts)
            
            self.logger.info(f"🎯 Target accounts: {result.total_accounts}")
            
            # アカウント別処理
            for account in accounts:
                account_result = await self._detect_account_new_posts(
                    account, check_from, force_reprocess
                )
                
                result.account_results.append(account_result)
                
                if account_result['success']:
                    result.successful_accounts += 1
                    result.total_posts_checked += account_result['posts_checked']
                    result.new_posts_found += account_result['new_posts_found']
                    result.new_posts_saved += account_result['new_posts_saved']
                    result.insights_collected += account_result['insights_collected']
                    result.api_calls_made += account_result['api_calls']
                    
                    # 新規投稿詳細を記録
                    for post_detail in account_result['new_posts_details']:
                        result.new_posts_details.append(post_detail)
                else:
                    result.failed_accounts += 1
                    result.errors.append(
                        f"Account {account_result['username']}: {account_result['error']}"
                    )
                
                # アカウント間の待機（API制限対応）
                await asyncio.sleep(3)
            
            result.completed_at = datetime.now()
            
            # 実行時刻の更新
            self.execution_tracker.update_last_execution_time(result.started_at)
            
            # 実行結果ログ
            duration = (result.completed_at - result.started_at).total_seconds()
            success_rate = (result.successful_accounts / result.total_accounts * 100) if result.total_accounts > 0 else 0
            
            self.logger.info(f"✅ Detection completed in {duration:.1f}s")
            self.logger.info(f"📊 Success rate: {success_rate:.1f}% ({result.successful_accounts}/{result.total_accounts})")
            self.logger.info(f"🆕 New posts found: {result.new_posts_found}")
            self.logger.info(f"💾 New posts saved: {result.new_posts_saved}")
            self.logger.info(f"📈 Insights collected: {result.insights_collected}")
            self.logger.info(f"📞 API calls made: {result.api_calls_made}")
            
            return result
            
        except Exception as e:
            result.completed_at = datetime.now()
            error_msg = f"Critical error in new posts detection: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            return result
            
        finally:
            await self._cleanup_database()

    async def _detect_account_new_posts(
        self, 
        account, 
        check_from: datetime,
        force_reprocess: bool
    ) -> Dict[str, Any]:
        """単一アカウントの新規投稿検出"""
        
        account_result = {
            'account_id': account.id,
            'instagram_user_id': account.instagram_user_id,
            'username': account.username,
            'success': False,
            'posts_checked': 0,
            'new_posts_found': 0,
            'new_posts_saved': 0,
            'insights_collected': 0,
            'api_calls': 0,
            'new_posts_details': [],
            'error': None
        }
        
        try:
            self.logger.info(f"🔍 Checking account: {account.username}")
            
            async with InstagramAPIClient() as api_client:
                # 最新投稿データ取得（最大50件）
                recent_posts = await self._fetch_recent_posts(api_client, account, limit=50)
                account_result['api_calls'] += 1
                account_result['posts_checked'] = len(recent_posts)
                
                # 新規投稿の検出
                new_posts = await self.post_detector.detect_new_posts(
                    recent_posts, 
                    check_from, 
                    account.id,
                    force_reprocess
                )
                account_result['new_posts_found'] = len(new_posts)
                
                if new_posts:
                    self.logger.info(f"🆕 Found {len(new_posts)} new posts for {account.username}")
                    
                    # 新規投稿の処理
                    for post_data in new_posts:
                        try:
                            # 投稿データ保存
                            saved_post = await self.post_processor.save_post_data(
                                account.id, post_data
                            )
                            
                            if saved_post:
                                account_result['new_posts_saved'] += 1
                                
                                # 投稿インサイト収集
                                insights = await api_client.get_post_insights(
                                    post_data['id'],
                                    account.access_token_encrypted,
                                    post_data.get('media_type', 'IMAGE')
                                )
                                account_result['api_calls'] += 1
                                
                                if insights:
                                    await self.post_processor.save_post_insights(
                                        saved_post.id, insights
                                    )
                                    account_result['insights_collected'] += 1
                                
                                # 新規投稿詳細を記録
                                post_detail = {
                                    'account_username': account.username,
                                    'post_id': post_data['id'],
                                    'media_type': post_data.get('media_type'),
                                    'timestamp': post_data.get('timestamp'),
                                    'permalink': post_data.get('permalink'),
                                    'caption_preview': (post_data.get('caption', '') or '')[:100] + '...' if post_data.get('caption') else None,
                                    'insights_collected': insights is not None
                                }
                                account_result['new_posts_details'].append(post_detail)
                                
                                self.logger.info(
                                    f"✅ Saved new post: {post_data['id']} "
                                    f"({post_data.get('media_type')}) "
                                    f"- insights: {'✓' if insights else '✗'}"
                                )
                                
                                # API制限対応（投稿間の待機）
                                await asyncio.sleep(2)
                                
                        except Exception as e:
                            self.logger.error(f"❌ Failed to process new post {post_data['id']}: {e}")
                            continue
                else:
                    self.logger.info(f"📭 No new posts found for {account.username}")
                
                account_result['success'] = True
                
        except Exception as e:
            account_result['error'] = str(e)
            self.logger.error(f"❌ Failed to check account {account.username}: {e}")
        
        return account_result

    async def _fetch_recent_posts(
        self, 
        api_client: InstagramAPIClient, 
        account, 
        limit: int = 50
    ) -> List[Dict]:
        """最新投稿データ取得"""
        
        url = api_client.config.get_user_media_url(account.instagram_user_id)
        
        params = {
            'fields': 'id,media_type,permalink,caption,timestamp,like_count,comments_count,media_url,thumbnail_url',
            'access_token': account.access_token_encrypted,
            'limit': min(limit, 100)  # API制限に合わせる
        }
        
        try:
            response = await api_client._make_request(url, params)
            posts = response.get('data', [])
            
            self.logger.debug(f"Retrieved {len(posts)} recent posts for {account.username}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Failed to fetch recent posts for {account.username}: {e}")
            return []

# CLI エントリーポイント
async def main():
    parser = argparse.ArgumentParser(description='New Posts Collector')
    parser.add_argument('--target-accounts', help='対象アカウント (カンマ区切り)')
    parser.add_argument('--check-hours-back', type=int, default=8, help='遡及時間 (時間)')
    parser.add_argument('--force-reprocess', action='store_true', help='既存投稿の再処理を強制実行')
    parser.add_argument('--notify-new-posts', action='store_true', help='新規投稿をSlack通知')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='ログレベル')
    
    args = parser.parse_args()
    
    # 対象アカウントの設定
    target_accounts = None
    if args.target_accounts:
        target_accounts = [acc.strip() for acc in args.target_accounts.split(',') if acc.strip()]
    
    # ログレベル設定
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 検出・収集実行
    collector = NewPostsCollector()
    result = await collector.detect_and_collect(
        target_accounts=target_accounts,
        check_hours_back=args.check_hours_back,
        force_reprocess=args.force_reprocess
    )
    
    # 結果表示
    print(f"\n{'='*60}")
    print("🆕 NEW POSTS DETECTION RESULT")
    print(f"{'='*60}")
    print(f"🎯 Accounts: {result.successful_accounts}/{result.total_accounts} succeeded")
    print(f"📊 Posts checked: {result.total_posts_checked}")
    print(f"🆕 New posts found: {result.new_posts_found}")
    print(f"💾 New posts saved: {result.new_posts_saved}")
    print(f"📈 Insights collected: {result.insights_collected}")
    print(f"📞 API calls: {result.api_calls_made}")
    
    # 新規投稿詳細表示
    if result.new_posts_details:
        print(f"\n📝 New Posts Details:")
        for post in result.new_posts_details[:10]:  # 最初の10件のみ表示
            print(f"   @{post['account_username']}: {post['media_type']} - {post['insights_collected'] and '📊' or '❌'}")
    
    if result.errors:
        print(f"\n❌ Errors ({len(result.errors)}):")
        for error in result.errors[:5]:
            print(f"   {error}")
    
    duration = (result.completed_at - result.started_at).total_seconds()
    print(f"\n⏱️ Duration: {duration:.1f}s")
    print(f"{'='*60}")
    
    # Slack通知（新規投稿があった場合のみ）
    if args.notify_new_posts and result.new_posts_found > 0:
        await collector.notification.send_new_posts_notification(result)
    
    # 失敗があった場合は exit code 1
    return 1 if result.failed_accounts > 0 else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

---

## 🔧 支援クラス実装

### `backend/scripts/github_actions/shared/post_detector.py`

```python
"""
Post Detector
新規投稿検出ロジック
"""

from datetime import datetime
from typing import List, Dict, Any
import logging

from app.repositories.instagram_post_repository import InstagramPostRepository

class PostDetector:
    """投稿検出クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def detect_new_posts(
        self,
        api_posts: List[Dict],
        check_from: datetime,
        account_id: str,
        force_reprocess: bool = False
    ) -> List[Dict]:
        """新規投稿検出"""
        
        new_posts = []
        
        for post in api_posts:
            # タイムスタンプチェック
            if not self._is_within_timeframe(post, check_from):
                continue
            
            # 既存投稿チェック（force_reprocessの場合はスキップ）
            if not force_reprocess:
                if await self._post_exists_in_db(post['id']):
                    continue
            
            new_posts.append(post)
        
        return new_posts
    
    def _is_within_timeframe(self, post: Dict, check_from: datetime) -> bool:
        """投稿が指定時刻以降かチェック"""
        timestamp_str = post.get('timestamp', '')
        if not timestamp_str:
            return False
        
        try:
            # ISO 8601 format: "2025-07-01T10:30:45+0000"
            post_datetime = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return post_datetime >= check_from
        except ValueError:
            self.logger.warning(f"Invalid timestamp format: {timestamp_str}")
            return False
    
    async def _post_exists_in_db(self, instagram_post_id: str) -> bool:
        """投稿がデータベースに存在するかチェック"""
        # 注意: この実装では毎回DBアクセスが発生するため、
        # 実際の実装では事前に既存投稿IDリストを取得して
        # メモリ上でチェックする方が効率的
        
        from app.core.database import get_db_sync
        db = get_db_sync()
        try:
            post_repo = InstagramPostRepository(db)
            existing_post = await post_repo.get_by_instagram_post_id(instagram_post_id)
            return existing_post is not None
        finally:
            db.close()
```

### `backend/scripts/github_actions/shared/execution_tracker.py`

```python
"""
Execution Tracker
実行状態管理
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

class ExecutionTracker:
    """実行状態追跡クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state_file = Path(__file__).parent.parent.parent.parent / "data" / "execution_state" / "new_posts_last_execution.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_last_execution_time(self) -> Optional[datetime]:
        """前回実行時刻取得"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                last_time_str = state.get('last_execution_time')
                if last_time_str:
                    return datetime.fromisoformat(last_time_str)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to load execution state: {e}")
            return None
    
    def update_last_execution_time(self, execution_time: datetime):
        """実行時刻更新"""
        try:
            state = {
                'last_execution_time': execution_time.isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"Execution state updated: {execution_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to update execution state: {e}")
```

---

## 🔔 通知機能

### 新規投稿通知メッセージ例
```json
{
  "text": "🆕 New Instagram Posts Detected!",
  "attachments": [
    {
      "color": "good",
      "fields": [
        {
          "title": "Summary",
          "value": "📝 3 new posts found across 2 accounts",
          "short": false
        },
        {
          "title": "@username1",
          "value": "2 new posts (CAROUSEL_ALBUM)",
          "short": true
        },
        {
          "title": "@username2", 
          "value": "1 new post (VIDEO)",
          "short": true
        }
      ],
      "footer": "Instagram Posts Monitor",
      "ts": 1625123456
    }
  ]
}
```

---

## 📊 注意点・制約事項

### 1. Story投稿の制限
```python
# Stories は24時間で消失するため、API経由では取得困難
# 通常の投稿（フィード投稿）のみが対象
```

### 2. タイムスタンプ精度
```python
# Instagram APIのタイムスタンプは秒単位
# 同一秒内の複数投稿は検出順序が不定
post_datetime = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
```

### 3. API制限管理
```python
# 頻繁な実行によるAPI制限対策
await asyncio.sleep(2)  # 投稿間待機
await asyncio.sleep(3)  # アカウント間待機

# 1回の実行でのAPI使用量制御
limit = min(50, 100)  # 最新50件のみチェック
```

### 4. データ整合性
```python
# 重複投稿の防止
if await self._post_exists_in_db(post['id']):
    continue

# エラー時の部分的失敗許容
try:
    # 投稿処理
except Exception as e:
    continue  # 他の投稿処理は継続
```

### 5. 実行状態管理
```python
# GitHub Actions での実行状態永続化
# data/execution_state/ ディレクトリをGitにコミット
git add data/execution_state/new_posts_last_execution.json
git commit -m "Update execution state [skip ci]"
```

---

## ✅ 実装チェックリスト

### Phase 1: 基本実装
- [ ] ワークフローファイル作成
- [ ] メインスクリプト実装
- [ ] 新規投稿検出ロジック
- [ ] 実行状態管理機能

### Phase 2: データ収集強化
- [ ] 投稿データ保存機能
- [ ] インサイト収集機能
- [ ] エラーハンドリング強化
- [ ] API制限対応

### Phase 3: 通知・監視
- [ ] 新規投稿Slack通知
- [ ] 実行結果ログ
- [ ] 障害時アラート
- [ ] 実行統計レポート

### Phase 4: 運用最適化
- [ ] パフォーマンス最適化
- [ ] データ品質チェック
- [ ] 自動復旧機能
- [ ] モニタリングダッシュボード

---

**結論**: この要件定義により、24時間以内の新規投稿を効率的に検出・収集するシステムを構築できます。1日2回の定期実行により、リアルタイム性を保ちながらAPI制限内で安定した運用が可能です。