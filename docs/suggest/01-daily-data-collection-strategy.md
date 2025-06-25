# Instagram分析アプリ - 日別データ収集戦略

**作成日**: 2025-06-25  
**対象**: 一般的なInstagram分析アプリ開発  
**基準**: 実際のAPI検証結果に基づく実装可能データのみ  

---

## 📋 日別収集データ一覧

### 🏷️ 基本アカウント情報（毎日）
1. **フォロワー数** - followers_count
2. **フォロー数** - follows_count  
3. **総投稿数** - media_count
4. **プロフィール情報** - username, name, biography
5. **プロフィール画像** - profile_picture_url

### 📊 インサイトメトリクス（毎日）
6. **リーチ数** - reach（日別・週別）
7. **フォロワー数変化** - follower_count（日別変化量）

### 📝 投稿データ（毎日）
8. **新規投稿一覧** - 投稿基本情報
9. **新規投稿メトリクス** - 各投稿のパフォーマンス

### 📈 投稿集約データ（毎日算出）
10. **日別投稿数** - その日の投稿数
11. **日別いいね合計** - その日投稿されたコンテンツのいいね合計
12. **日別コメント合計** - その日投稿されたコンテンツのコメント合計
13. **メディアタイプ分布** - VIDEO/CAROUSEL/IMAGE の分布

### 🔄 既存投稿追跡（オプション）
14. **過去投稿メトリクス更新** - 直近1週間の投稿パフォーマンス変化

---

## 📊 詳細データ収集仕様

### 1. 基本アカウント情報収集

#### エンドポイント
```http
GET https://graph.facebook.com/{ig-user-id}
```

#### 取得フィールド
```json
{
  "fields": "id,username,name,biography,website,profile_picture_url,followers_count,follows_count,media_count,is_published"
}
```

#### 収集データ
| フィールド | データ型 | 用途 | 更新頻度 |
|-----------|---------|------|---------|
| `followers_count` | integer | フォロワー数推移 | 毎日 |
| `follows_count` | integer | フォロー数推移 | 毎日 |
| `media_count` | integer | 総投稿数推移 | 毎日 |
| `username` | string | アカウント識別 | 毎日 |
| `name` | string | 表示名変更追跡 | 毎日 |
| `biography` | string | プロフィール変更追跡 | 毎日 |
| `profile_picture_url` | string | プロフィール画像変更 | 毎日 |

#### 実装例
```python
def collect_daily_account_info(instagram_user_id, access_token):
    """日別基本アカウント情報収集"""
    url = f"https://graph.facebook.com/{instagram_user_id}"
    
    params = {
        'fields': 'followers_count,follows_count,media_count,username,name,biography,profile_picture_url',
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    return {
        'collection_date': datetime.now().date(),
        'followers_count': data.get('followers_count', 0),
        'follows_count': data.get('follows_count', 0),
        'media_count': data.get('media_count', 0),
        'username': data.get('username'),
        'name': data.get('name'),
        'biography': data.get('biography'),
        'profile_picture_url': data.get('profile_picture_url')
    }
```

---

### 2. インサイトメトリクス収集

#### エンドポイント
```http
GET https://graph.facebook.com/{ig-user-id}/insights
```

#### 取得可能メトリクス
```json
{
  "metric": "reach,follower_count",
  "since": "2025-06-24",
  "until": "2025-06-25",
  "period": "day"
}
```

#### 収集データ
| メトリクス | API名 | データ型 | 用途 | 期間 |
|-----------|-------|---------|------|------|
| リーチ数 | `reach` | integer | 日別リーチ推移 | day, week |
| フォロワー変化 | `follower_count` | integer | 日別フォロワー増減 | day |

#### 実装例
```python
def collect_daily_insights(instagram_user_id, access_token, target_date):
    """日別インサイトメトリクス収集"""
    url = f"https://graph.facebook.com/{instagram_user_id}/insights"
    
    params = {
        'metric': 'reach,follower_count',
        'since': target_date.strftime('%Y-%m-%d'),
        'until': target_date.strftime('%Y-%m-%d'),
        'period': 'day',
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        metrics = {}
        
        for metric_data in data.get('data', []):
            metric_name = metric_data.get('name')
            values = metric_data.get('values', [])
            if values:
                metrics[metric_name] = values[0].get('value', 0)
        
        return {
            'collection_date': target_date,
            'reach': metrics.get('reach', 0),
            'follower_count_change': metrics.get('follower_count', 0)
        }
        
    except Exception as e:
        logger.warning(f"Insights収集エラー: {e}")
        return {
            'collection_date': target_date,
            'reach': 0,
            'follower_count_change': 0
        }
```

---

### 3. 投稿データ収集

#### 新規投稿検出エンドポイント
```http
GET https://graph.facebook.com/{ig-user-id}/media
```

#### 取得フィールド
```json
{
  "fields": "id,media_type,caption,media_url,thumbnail_url,timestamp,permalink,username,like_count,comments_count,is_comment_enabled,shortcode",
  "limit": 25
}
```

#### 投稿メトリクス取得エンドポイント
```http
GET https://graph.facebook.com/{ig-media-id}/insights
```

#### 取得メトリクス
```json
{
  "metric": "likes,comments,saved,shares,views,reach,total_interactions"
}
```

#### 収集データ
| カテゴリ | フィールド | データ型 | 用途 |
|---------|-----------|---------|------|
| **投稿基本** | instagram_post_id | string | 投稿識別 |
| **投稿基本** | media_type | string | コンテンツタイプ分析 |
| **投稿基本** | caption | text | コンテンツ分析 |
| **投稿基本** | posted_at | datetime | 投稿時間分析 |
| **メトリクス** | likes | integer | エンゲージメント分析 |
| **メトリクス** | comments | integer | エンゲージメント分析 |
| **メトリクス** | saved | integer | 保存行動分析 |
| **メトリクス** | shares | integer | 拡散分析 |
| **メトリクス** | views | integer | 視聴分析 |
| **メトリクス** | reach | integer | リーチ分析 |

#### 実装例
```python
def collect_daily_posts(instagram_user_id, access_token, target_date):
    """日別新規投稿収集"""
    
    # 1. 投稿一覧取得
    media_url = f"https://graph.facebook.com/{instagram_user_id}/media"
    media_params = {
        'fields': 'id,media_type,caption,media_url,thumbnail_url,timestamp,permalink,like_count,comments_count',
        'access_token': access_token,
        'limit': 25
    }
    
    response = requests.get(media_url, params=media_params)
    response.raise_for_status()
    posts = response.json().get('data', [])
    
    # 2. 当日投稿のフィルタリング
    target_date_str = target_date.strftime('%Y-%m-%d')
    daily_posts = []
    
    for post in posts:
        post_date = post.get('timestamp', '').split('T')[0]
        if post_date == target_date_str:
            
            # 3. 投稿メトリクス取得
            insights = get_post_insights(post['id'], access_token, post['media_type'])
            
            daily_posts.append({
                'post_data': post,
                'metrics': insights,
                'collection_date': target_date
            })
    
    return daily_posts

def get_post_insights(post_id, access_token, media_type):
    """投稿メトリクス取得"""
    url = f"https://graph.facebook.com/{post_id}/insights"
    
    # メディアタイプ別メトリクス
    base_metrics = ['likes', 'comments', 'saved', 'shares', 'views', 'reach', 'total_interactions']
    
    if media_type == 'VIDEO':
        metrics = base_metrics + ['ig_reels_video_view_total_time', 'ig_reels_avg_watch_time']
    elif media_type == 'CAROUSEL_ALBUM':
        metrics = base_metrics + ['follows', 'profile_visits', 'profile_activity']
    else:
        metrics = base_metrics
    
    params = {
        'metric': ','.join(metrics),
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        metrics_dict = {}
        
        for metric_data in data.get('data', []):
            metric_name = metric_data.get('name')
            values = metric_data.get('values', [])
            if values:
                metrics_dict[metric_name] = values[0].get('value', 0)
        
        return metrics_dict
        
    except Exception as e:
        logger.error(f"投稿メトリクス取得エラー: {e}")
        return {}
```

---

### 4. 投稿集約データ算出

#### 算出項目
| 項目 | 算出方法 | 用途 |
|------|---------|------|
| `daily_posts_count` | その日の投稿数カウント | 投稿頻度分析 |
| `daily_total_likes` | その日投稿のいいね合計 | 日別エンゲージメント |
| `daily_total_comments` | その日投稿のコメント合計 | 日別コミュニケーション |
| `daily_avg_likes_per_post` | いいね合計 ÷ 投稿数 | 投稿品質分析 |
| `daily_avg_comments_per_post` | コメント合計 ÷ 投稿数 | エンゲージメント率 |
| `media_type_distribution` | タイプ別投稿数分布 | コンテンツ戦略分析 |

#### 実装例
```python
def calculate_daily_aggregation(daily_posts, target_date):
    """日別投稿集約データ算出"""
    
    if not daily_posts:
        return {
            'collection_date': target_date,
            'posts_count': 0,
            'total_likes': 0,
            'total_comments': 0,
            'avg_likes_per_post': 0,
            'avg_comments_per_post': 0,
            'media_type_distribution': '{}'
        }
    
    # 基本集計
    posts_count = len(daily_posts)
    total_likes = sum(post['metrics'].get('likes', 0) for post in daily_posts)
    total_comments = sum(post['metrics'].get('comments', 0) for post in daily_posts)
    
    # 平均値算出
    avg_likes = total_likes / posts_count if posts_count > 0 else 0
    avg_comments = total_comments / posts_count if posts_count > 0 else 0
    
    # メディアタイプ分布
    from collections import Counter
    media_types = [post['post_data'].get('media_type') for post in daily_posts]
    media_distribution = dict(Counter(media_types))
    
    return {
        'collection_date': target_date,
        'posts_count': posts_count,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avg_likes_per_post': round(avg_likes, 2),
        'avg_comments_per_post': round(avg_comments, 2),
        'media_type_distribution': json.dumps(media_distribution)
    }
```

---

### 5. 既存投稿追跡（オプション機能）

#### 目的
過去投稿への継続的なエンゲージメント（遅れていいね等）を追跡

#### 対象期間
直近1週間の投稿（API制限を考慮）

#### 実装戦略
```python
def track_existing_posts_performance(instagram_user_id, access_token, target_date):
    """既存投稿パフォーマンス追跡"""
    
    # 直近1週間の投稿を対象
    week_ago = target_date - timedelta(days=7)
    
    # 追跡対象投稿取得
    recent_posts = get_posts_in_date_range(
        instagram_user_id, 
        access_token, 
        week_ago, 
        target_date - timedelta(days=1)
    )
    
    performance_changes = []
    
    for post in recent_posts:
        # 現在のメトリクス取得
        current_metrics = get_post_insights(post['id'], access_token, post['media_type'])
        
        # 前日のメトリクスと比較
        previous_metrics = get_stored_metrics(post['id'], target_date - timedelta(days=1))
        
        if previous_metrics:
            changes = calculate_metrics_delta(current_metrics, previous_metrics)
            performance_changes.append({
                'post_id': post['id'],
                'date': target_date,
                'metrics_changes': changes
            })
    
    return performance_changes
```

---

## 🔄 データ収集スケジュール

### 毎日実行（推奨時間: 早朝6:00 JST）
```python
def daily_data_collection_pipeline(account_configs, target_date):
    """日別データ収集パイプライン"""
    
    for account in account_configs:
        try:
            logger.info(f"データ収集開始: {account['username']} - {target_date}")
            
            # 1. 基本アカウント情報（必須）
            account_info = collect_daily_account_info(
                account['instagram_user_id'], 
                account['access_token']
            )
            
            # 2. インサイトメトリクス（オプション）
            insights_data = collect_daily_insights(
                account['instagram_user_id'], 
                account['access_token'], 
                target_date
            )
            
            # 3. 新規投稿データ（必須）
            daily_posts = collect_daily_posts(
                account['instagram_user_id'], 
                account['access_token'], 
                target_date
            )
            
            # 4. 投稿集約データ算出
            aggregation_data = calculate_daily_aggregation(daily_posts, target_date)
            
            # 5. 既存投稿追跡（オプション）
            if account.get('track_existing_posts', False):
                performance_changes = track_existing_posts_performance(
                    account['instagram_user_id'], 
                    account['access_token'], 
                    target_date
                )
            
            # 6. データベース保存
            save_daily_data(
                account['id'], 
                account_info, 
                insights_data, 
                aggregation_data,
                daily_posts
            )
            
            logger.info(f"データ収集完了: {account['username']}")
            
        except Exception as e:
            logger.error(f"データ収集エラー: {account['username']} - {e}")
            continue
```

---

## 📊 API使用量見積もり

### 1アカウントあたりの日次API使用量
| データタイプ | API コール数 | 説明 |
|-------------|-------------|------|
| 基本アカウント情報 | 1 | 基本フィールド一括取得 |
| インサイトメトリクス | 1 | reach, follower_count |
| 新規投稿取得 | 1 | 直近25件投稿 |
| 新規投稿メトリクス | 1-5 | その日の投稿数に依存 |
| 既存投稿追跡 | 0-25 | オプション機能 |
| **合計** | **4-32** | **平均 8-10 コール/日** |

### レート制限対応
- **制限**: 200コール/時間/ユーザー
- **対応可能アカウント数**: 20-25アカウント/時間
- **推奨バッチサイズ**: 10アカウント/時間（安全マージン）

---

## 🎯 分析アプリでの活用例

### ダッシュボード表示
```typescript
interface DailyAnalytics {
  date: string;
  followers_count: number;
  follower_growth: number;
  reach: number;
  posts_count: number;
  total_engagement: number;
  avg_engagement_rate: number;
  top_performing_post: PostSummary;
}
```

### 週次・月次レポート
- フォロワー成長率推移
- エンゲージメント率トレンド
- 投稿頻度 vs パフォーマンス相関
- メディアタイプ別効果分析

### アラート機能
- フォロワー数急減検知
- エンゲージメント率低下警告
- 投稿パフォーマンス異常検知

この戦略により、**実際に取得可能なデータのみを使用した実用的なInstagram分析アプリ**を構築できます。