# GitHub Actions 毎日インサイトデータ収集戦略

**作成日**: 2025-07-01  
**目的**: GitHub Actionsを使用した毎日のInstagramインサイトデータ自動収集システムの設計  
**対象**: 投稿レベルインサイト＋基本アカウントデータの定期収集  

---

## 📊 戦略概要

### 基本方針
1. **段階的実装**: インサイト収集 → 投稿データ収集 → 統合システム
2. **API制限遵守**: 200コール/時間の制限内での効率的な収集
3. **エラー耐性**: 部分的失敗でも継続可能な設計
4. **モニタリング**: 実行状況とデータ品質の可視化

### 収集対象データ
1. **投稿インサイト**: likes, views, reach, saved, shares など
2. **基本アカウントデータ**: followers_count, following_count, media_count
3. **新規投稿検出**: 前回実行以降の新しい投稿

---

## 🏗️ システム設計

### アーキテクチャ図
```
GitHub Actions (cron)
├── 1. 環境設定・認証
├── 2. 全アカウント取得
├── 3. アカウント別処理（並列）
│   ├── 基本データ収集
│   ├── 新規投稿検出
│   ├── 投稿インサイト収集
│   └── データベース保存
├── 4. エラーハンドリング
├── 5. 実行結果通知
└── 6. ログ・監視
```

### データフロー
```
1. GitHub Actions Trigger (毎日 09:00 JST)
   ↓
2. PostgreSQL接続・全アカウント取得
   ↓
3. 各アカウントで並列処理:
   a) 基本アカウントデータ取得 (API 1回)
   b) 最新投稿データ取得 (API 1回)
   c) 新規投稿のインサイト取得 (API N回)
   d) 既存投稿のインサイト更新 (API M回)
   ↓
4. instagram_daily_stats 更新
   ↓
5. 実行結果をSlack/Email通知
```

---

## 📅 実行スケジュール設計

### メインスケジュール
```yaml
# .github/workflows/daily-insights-collection.yml
on:
  schedule:
    - cron: '0 0 * * *'  # 毎日 09:00 JST (UTC 00:00)
  workflow_dispatch:     # 手動実行も可能
```

### アカウント処理の時間配分
```
全体制限: 200コール/時間 = 約18秒/コール
アカウント数: 5アカウント想定

1アカウントあたり:
- 基本データ: 1 API call
- 投稿一覧: 1 API call  
- 投稿インサイト: 平均5投稿 × 1 call = 5 API calls
- 合計: 7 API calls/アカウント

総使用量: 5アカウント × 7 calls = 35 calls
実行時間: 35 × 18秒 = 10.5分（十分余裕あり）
```

---

## 🛠️ 実装コンポーネント

### 1. GitHub Actions ワークフローファイル

#### `.github/workflows/daily-insights-collection.yml`
```yaml
name: Daily Instagram Insights Collection

on:
  schedule:
    - cron: '0 0 * * *'  # 毎日 09:00 JST
  workflow_dispatch:
    inputs:
      target_accounts:
        description: '対象アカウント (カンマ区切り、空の場合は全アカウント)'
        required: false
        type: string
      force_all_posts:
        description: '全投稿のインサイト更新を強制実行'
        required: false
        type: boolean
        default: false

jobs:
  collect-insights:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
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
        
    - name: Run daily insights collection
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        FACEBOOK_APP_ID: ${{ secrets.FACEBOOK_APP_ID }}
        FACEBOOK_APP_SECRET: ${{ secrets.FACEBOOK_APP_SECRET }}
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        cd backend
        python scripts/daily_insights_collector.py \
          --accounts "${{ github.event.inputs.target_accounts }}" \
          --force-all-posts ${{ github.event.inputs.force_all_posts }} \
          --notify-slack
          
    - name: Upload execution logs
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: daily-insights-logs-${{ github.run_id }}
        path: backend/logs/
        retention-days: 30
```

### 2. 専用収集スクリプト

#### `backend/scripts/daily_insights_collector.py`
```python
#!/usr/bin/env python3
"""
Daily Instagram Insights Collector for GitHub Actions
毎日のInstagramインサイトデータ収集（GitHub Actions専用）

Usage:
    python scripts/daily_insights_collector.py --notify-slack
    python scripts/daily_insights_collector.py --accounts "123,456" --force-all-posts
"""

import asyncio
import sys
import argparse
import logging
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json
import aiohttp
from dataclasses import dataclass

# 環境変数読み込み
DATABASE_URL = os.getenv('DATABASE_URL')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

@dataclass
class DailyCollectionResult:
    """日次収集結果"""
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_accounts: int = 0
    successful_accounts: int = 0
    failed_accounts: int = 0
    total_api_calls: int = 0
    new_posts_found: int = 0
    insights_collected: int = 0
    errors: List[str] = None
    account_results: List[Dict] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.account_results is None:
            self.account_results = []

class DailyInsightsCollector:
    """毎日のインサイト収集サービス"""
    
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
                    log_dir / f"daily_insights_{datetime.now().strftime('%Y%m%d')}.log"
                )
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def collect_daily_insights(
        self, 
        target_accounts: Optional[List[str]] = None,
        force_all_posts: bool = False
    ) -> DailyCollectionResult:
        """毎日のインサイト収集メイン処理"""
        
        execution_id = f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = DailyCollectionResult(
            execution_id=execution_id,
            started_at=datetime.now()
        )
        
        try:
            self.logger.info(f"🚀 Daily insights collection started: {execution_id}")
            
            # データベース接続
            await self._init_database()
            
            # アカウント取得
            accounts = await self._get_target_accounts(target_accounts)
            result.total_accounts = len(accounts)
            
            self.logger.info(f"📊 Target accounts: {result.total_accounts}")
            
            # 並列処理でアカウント別収集
            tasks = []
            for account in accounts:
                task = self._collect_account_insights(account, force_all_posts)
                tasks.append(task)
            
            # 並列実行（ただしAPI制限を考慮して制御）
            account_results = await self._execute_with_rate_limit(tasks)
            
            # 結果集約
            for account_result in account_results:
                result.account_results.append(account_result)
                if account_result.get('success', False):
                    result.successful_accounts += 1
                    result.total_api_calls += account_result.get('api_calls', 0)
                    result.new_posts_found += account_result.get('new_posts', 0)
                    result.insights_collected += account_result.get('insights_collected', 0)
                else:
                    result.failed_accounts += 1
                    result.errors.append(
                        f"Account {account_result.get('account_id')}: {account_result.get('error')}"
                    )
            
            result.completed_at = datetime.now()
            self.logger.info(f"✅ Daily insights collection completed: {execution_id}")
            
            return result
            
        except Exception as e:
            result.completed_at = datetime.now()
            result.errors.append(f"Critical error: {str(e)}")
            self.logger.error(f"❌ Daily insights collection failed: {e}", exc_info=True)
            return result
        
        finally:
            if self.db:
                self.db.close()

    async def _collect_account_insights(
        self, 
        account, 
        force_all_posts: bool
    ) -> Dict[str, Any]:
        """単一アカウントのインサイト収集"""
        
        account_result = {
            'account_id': account.instagram_user_id,
            'username': account.username,
            'success': False,
            'api_calls': 0,
            'new_posts': 0,
            'insights_collected': 0,
            'error': None
        }
        
        try:
            async with InstagramAPIClient() as api_client:
                # 1. 基本アカウントデータ収集
                basic_data = await api_client.get_basic_account_data(
                    account.instagram_user_id,
                    account.access_token_encrypted
                )
                account_result['api_calls'] += 1
                
                # 2. 最新投稿データ取得
                recent_posts = await api_client.get_recent_posts(
                    account.instagram_user_id,
                    account.access_token_encrypted,
                    limit=20  # 最新20件をチェック
                )
                account_result['api_calls'] += 1
                
                # 3. 新規投稿検出
                new_posts = await self._detect_new_posts(account.id, recent_posts)
                account_result['new_posts'] = len(new_posts)
                
                # 4. インサイト収集対象決定
                if force_all_posts:
                    # 全投稿のインサイト更新
                    target_posts = recent_posts[:10]  # 最新10件
                else:
                    # 新規投稿 + 最近の投稿のみ
                    target_posts = new_posts
                    # 直近3日の投稿も更新対象に追加
                    cutoff_date = date.today() - timedelta(days=3)
                    for post in recent_posts:
                        post_date = self._parse_post_date(post.get('timestamp'))
                        if post_date and post_date >= cutoff_date:
                            if post not in target_posts:
                                target_posts.append(post)
                
                # 5. 投稿インサイト収集
                insights_collected = 0
                for post in target_posts:
                    try:
                        insights = await api_client.get_post_insights(
                            post['id'],
                            account.access_token_encrypted,
                            post.get('media_type', 'IMAGE')
                        )
                        account_result['api_calls'] += 1
                        
                        if insights:
                            await self._save_post_insights(account.id, post, insights)
                            insights_collected += 1
                        
                        # API制限対応
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        self.logger.warning(f"Post insights failed for {post['id']}: {e}")
                        continue
                
                account_result['insights_collected'] = insights_collected
                
                # 6. 日次統計更新
                await self._update_daily_stats(account, basic_data, recent_posts)
                
                account_result['success'] = True
                self.logger.info(
                    f"✅ Account {account.username}: "
                    f"{account_result['new_posts']} new posts, "
                    f"{account_result['insights_collected']} insights collected"
                )
                
        except Exception as e:
            account_result['error'] = str(e)
            self.logger.error(f"❌ Account {account.username} failed: {e}")
        
        return account_result

    async def _execute_with_rate_limit(self, tasks: List) -> List[Dict]:
        """レート制限を考慮した並列実行"""
        results = []
        
        # セマフォで同時実行数を制限
        semaphore = asyncio.Semaphore(2)  # 最大2アカウント同時処理
        
        async def limited_task(task):
            async with semaphore:
                result = await task
                # アカウント間の待機
                await asyncio.sleep(5)
                return result
        
        # 並列実行
        limited_tasks = [limited_task(task) for task in tasks]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # 例外処理
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'account_id': f'unknown_{i}',
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def send_slack_notification(self, result: DailyCollectionResult):
        """Slack通知送信"""
        if not SLACK_WEBHOOK_URL:
            return
        
        try:
            duration = (result.completed_at - result.started_at).total_seconds()
            success_rate = (result.successful_accounts / result.total_accounts * 100) if result.total_accounts > 0 else 0
            
            # 成功・失敗で色を分ける
            color = "good" if result.failed_accounts == 0 else "warning" if result.successful_accounts > 0 else "danger"
            
            message = {
                "attachments": [
                    {
                        "color": color,
                        "title": "📊 Daily Instagram Insights Collection Result",
                        "fields": [
                            {
                                "title": "Summary",
                                "value": f"✅ {result.successful_accounts}/{result.total_accounts} accounts succeeded ({success_rate:.1f}%)",
                                "short": False
                            },
                            {
                                "title": "Data Collected",
                                "value": f"🆕 {result.new_posts_found} new posts\n📈 {result.insights_collected} insights collected",
                                "short": True
                            },
                            {
                                "title": "API Usage",
                                "value": f"📞 {result.total_api_calls} API calls\n⏱️ {duration:.1f}s execution time",
                                "short": True
                            }
                        ],
                        "footer": f"Execution ID: {result.execution_id}",
                        "ts": int(result.completed_at.timestamp())
                    }
                ]
            }
            
            # エラーがある場合は詳細を追加
            if result.errors:
                error_text = "\n".join(result.errors[:5])  # 最初の5個のエラーのみ
                if len(result.errors) > 5:
                    error_text += f"\n... and {len(result.errors) - 5} more errors"
                
                message["attachments"][0]["fields"].append({
                    "title": "Errors",
                    "value": f"```{error_text}```",
                    "short": False
                })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(SLACK_WEBHOOK_URL, json=message) as response:
                    if response.status == 200:
                        self.logger.info("📢 Slack notification sent successfully")
                    else:
                        self.logger.error(f"❌ Slack notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ Slack notification error: {e}")

# CLI エントリーポイント
async def main():
    parser = argparse.ArgumentParser(description='Daily Instagram Insights Collector')
    parser.add_argument('--accounts', help='対象アカウント (カンマ区切り)')
    parser.add_argument('--force-all-posts', action='store_true', help='全投稿のインサイト更新を強制実行')
    parser.add_argument('--notify-slack', action='store_true', help='Slack通知を送信')
    
    args = parser.parse_args()
    
    collector = DailyInsightsCollector()
    
    target_accounts = None
    if args.accounts:
        target_accounts = [acc.strip() for acc in args.accounts.split(',') if acc.strip()]
    
    result = await collector.collect_daily_insights(
        target_accounts=target_accounts,
        force_all_posts=args.force_all_posts
    )
    
    # 結果表示
    print(f"\n{'='*60}")
    print("📊 DAILY INSIGHTS COLLECTION RESULT")
    print(f"{'='*60}")
    print(f"🎯 Accounts: {result.successful_accounts}/{result.total_accounts} succeeded")
    print(f"🆕 New posts: {result.new_posts_found}")
    print(f"📈 Insights collected: {result.insights_collected}")
    print(f"📞 API calls: {result.total_api_calls}")
    
    if result.errors:
        print(f"❌ Errors: {len(result.errors)}")
        for error in result.errors[:3]:
            print(f"   {error}")
    
    duration = (result.completed_at - result.started_at).total_seconds()
    print(f"⏱️ Duration: {duration:.1f}s")
    print(f"{'='*60}")
    
    # Slack通知
    if args.notify_slack:
        await collector.send_slack_notification(result)
    
    # 失敗があった場合は exit code 1
    return 1 if result.failed_accounts > 0 else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

---

## 🔐 シークレット管理

### GitHub Secrets 設定
```
DATABASE_URL=postgresql://user:pass@host:port/db
FACEBOOK_APP_ID=your_facebook_app_id  
FACEBOOK_APP_SECRET=your_facebook_app_secret
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 環境変数セキュリティ
- データベースパスワードは暗号化
- API キーは GitHub Secrets で管理
- ログにシークレット情報は出力しない

---

## 📈 監視・アラート設計

### 1. 実行状況監視
```python
# 実行メトリクス
- 成功率: successful_accounts / total_accounts
- API使用量: total_api_calls (上限200/時間)
- 実行時間: duration (目標10分以内)
- 新規投稿検出数: new_posts_found
```

### 2. Slack通知内容
```
✅ 成功時: 簡潔なサマリー
⚠️ 部分失敗: 失敗アカウントとエラー内容
❌ 完全失敗: 詳細なエラー情報とスタックトレース
```

### 3. ログ管理
```
- GitHub Actions logs: 30日間保持
- 詳細ログファイル: artifacts として保存
- エラーログ: Slack に即座に通知
```

---

## 🚀 段階的ロールアウト計画

### Phase 1: 基本実装 (Week 1)
1. ✅ GitHub Actions ワークフロー作成
2. ✅ `daily_insights_collector.py` 基本実装
3. ✅ データベース接続・基本データ収集
4. ✅ 手動実行でのテスト

### Phase 2: インサイト収集 (Week 2)  
1. ✅ 投稿インサイト収集機能
2. ✅ 新規投稿検出ロジック
3. ✅ API制限対応・エラーハンドリング
4. ✅ 本番環境でのテスト実行

### Phase 3: 通知・監視 (Week 3)
1. ✅ Slack通知機能
2. ✅ 詳細ログ出力
3. ✅ パフォーマンス最適化
4. ✅ 自動実行スケジュール開始

### Phase 4: 拡張機能 (Week 4)
1. ✅ 投稿データ収集統合
2. ✅ 月次レポート自動生成
3. ✅ ダッシュボード連携
4. ✅ 運用最適化

---

## ⚠️ リスク対策

### 1. API制限対策
- セマフォによる同時実行制御
- アカウント間の適切な待機時間
- エラー時の指数バックオフ

### 2. データ品質保証
- 重複データの検出・防止
- 欠損データの補完ロジック
- データ整合性チェック

### 3. 障害対応
- 部分的失敗でも処理継続
- 自動リトライ機能
- 手動復旧手順の文書化

---

**結論**: この戦略により、安定した毎日のInstagramインサイトデータ収集システムを構築できます。GitHub Actionsの無料枠内で運用可能で、拡張性とメンテナンス性を確保した設計となっています。