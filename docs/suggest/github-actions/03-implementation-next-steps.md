# GitHub Actions 実装完了後の次のステップ

**作成日**: 2025-07-01  
**対象**: GitHub Actions自動収集システムの運用開始  

---

## 🚀 やらないといけないこと（必須）

### 1. GitHub Secrets の設定
リポジトリの `Settings > Secrets and variables > Actions` で設定：

```
DATABASE_URL=postgresql://user:password@host:port/database
```

オプション（Slack通知を使う場合）：
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 2. Repository メソッドの非同期化確認
以下のRepositoryメソッドが `async def` になっているか確認：

```python
# app/repositories/instagram_account_repository.py
async def get_active_accounts(self)
async def get_by_instagram_user_id(self, instagram_user_id: str)

# app/repositories/instagram_daily_stats_repository.py  
async def get_by_specific_date(self, account_id: str, target_date: date)
async def create(self, stats_data: dict)
async def update(self, stats_id: str, stats_data: dict)

# app/repositories/instagram_post_repository.py
async def get_by_instagram_post_id(self, instagram_post_id: str)
async def create(self, post_data: dict)

# app/repositories/instagram_post_metrics_repository.py
async def create(self, metrics_data: dict)
```

### 3. 初回動作テスト
```bash
cd backend

# アカウントインサイト収集テスト
python scripts/github_actions/account_insights_collector.py --target-date 2025-07-01

# 新規投稿収集テスト  
python scripts/github_actions/new_posts_collector.py --check-hours-back 24
```

---

## ✅ 完了確認

1. **GitHub Secrets設定完了** □
2. **Repository非同期化確認完了** □  
3. **手動テスト成功** □
4. **GitHub Actions有効化** □

---

## 🎯 運用開始

上記4つが完了すれば、以下が自動実行されます：

- **毎日09:00**: アカウント日次統計収集
- **毎日06:00, 18:00**: 新規投稿検出・収集

---

## 📞 問題が発生した場合

1. **GitHub Actions の Logs を確認**
2. **`backend/logs/github_actions/` のログファイルを確認**
3. **Slack通知（設定した場合）を確認**