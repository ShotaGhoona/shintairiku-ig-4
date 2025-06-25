#!/usr/bin/env python3
"""
Phase 2: 投稿メトリクス取得検証
API エンドポイント: GET /{ig-media-id}/insights
post_metricsテーブルに必要なデータが取得できるかを検証
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
USERNAME = os.getenv('USERNAME')

def get_post_metrics():
    """投稿メトリクスデータを取得してpost_metricsテーブル用のデータ構造を検証"""
    
    print("=" * 50)
    print("Phase 2: 投稿メトリクス取得検証")
    print("=" * 50)
    
    # まず投稿一覧から投稿IDを取得
    print("🔄 投稿一覧から投稿IDを取得中...")
    
    media_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    media_params = {
        'fields': 'id,media_type',
        'access_token': ACCESS_TOKEN,
        'limit': 5  # テスト用に5件
    }
    
    try:
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        media_data = media_response.json()
        
        posts = media_data.get('data', [])
        if not posts:
            print("❌ 投稿データが見つかりません")
            return None
        
        print(f"✅ {len(posts)}件の投稿IDを取得")
        
        # post_metricsテーブルに必要なメトリクス
        metrics = [
            'likes',        # いいね数
            'comments',     # コメント数
            'saves',        # 保存数
            'shares',       # シェア数
            'views',        # 視聴回数（2024年新メトリクス）
            'reach',        # リーチ数
            'impressions'   # インプレッション数
        ]
        
        print("\n📊 post_metricsテーブル用データ検証:")
        print("-" * 40)
        
        all_metrics_data = []
        
        for i, post in enumerate(posts):
            post_id = post.get('id')
            media_type = post.get('media_type')
            
            print(f"\n投稿 {i+1} (ID: {post_id}, Type: {media_type}):")
            
            # メトリクス取得APIエンドポイント
            insights_url = f"https://graph.facebook.com/{post_id}/insights"
            insights_params = {
                'metric': ','.join(metrics),
                'access_token': ACCESS_TOKEN
            }
            
            try:
                print("  🔄 メトリクス取得中...")
                insights_response = requests.get(insights_url, params=insights_params)
                insights_response.raise_for_status()
                
                insights_data = insights_response.json()
                metrics_dict = {}
                
                # メトリクスデータの解析
                for metric_data in insights_data.get('data', []):
                    metric_name = metric_data.get('name')
                    values = metric_data.get('values', [])
                    
                    if values:
                        # 最新の値を取得（通常は配列の最初の要素）
                        metric_value = values[0].get('value', 0)
                        metrics_dict[metric_name] = metric_value
                
                # post_metricsテーブル用のデータ構造を確認
                post_metrics = {
                    'post_id': post_id,
                    'media_type': media_type,
                    'likes': metrics_dict.get('likes', 0),
                    'comments': metrics_dict.get('comments', 0),
                    'saves': metrics_dict.get('saves', 0),
                    'shares': metrics_dict.get('shares', 0),
                    'views': metrics_dict.get('views', 0),
                    'reach': metrics_dict.get('reach', 0),
                    'impressions': metrics_dict.get('impressions', 0),
                    'recorded_at': datetime.now().isoformat()
                }
                
                # エンゲージメント率の計算
                reach = post_metrics['reach']
                if reach > 0:
                    engagement = post_metrics['likes'] + post_metrics['comments'] + post_metrics['saves'] + post_metrics['shares']
                    engagement_rate = (engagement / reach) * 100
                    post_metrics['engagement_rate'] = round(engagement_rate, 2)
                else:
                    post_metrics['engagement_rate'] = 0.0
                
                all_metrics_data.append(post_metrics)
                
                # 取得結果表示
                print(f"  ✅ メトリクス取得成功:")
                print(f"    likes: {post_metrics['likes']}")
                print(f"    comments: {post_metrics['comments']}")
                print(f"    saves: {post_metrics['saves']}")
                print(f"    shares: {post_metrics['shares']}")
                print(f"    views: {post_metrics['views']}")
                print(f"    reach: {post_metrics['reach']}")
                print(f"    impressions: {post_metrics['impressions']}")
                print(f"    engagement_rate: {post_metrics['engagement_rate']}%")
                
                # 利用可能なメトリクス確認
                available_metrics = [data.get('name') for data in insights_data.get('data', [])]
                print(f"    利用可能なメトリクス: {available_metrics}")
                
                # 取得できなかったメトリクス確認
                missing_metrics = [metric for metric in metrics if metric not in available_metrics]
                if missing_metrics:
                    print(f"    ⚠️  取得できなかったメトリクス: {missing_metrics}")
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ メトリクス取得エラー: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"    レスポンスコード: {e.response.status_code}")
                    print(f"    レスポンス内容: {e.response.text}")
                continue
        
        # データ品質チェック
        print("\n🔍 メトリクスデータ品質チェック:")
        print("-" * 30)
        
        if all_metrics_data:
            # 各メトリクスの統計
            total_posts = len(all_metrics_data)
            metrics_stats = {}
            
            for metric in metrics:
                values = [data.get(metric, 0) for data in all_metrics_data if data.get(metric, 0) > 0]
                if values:
                    metrics_stats[metric] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': round(sum(values) / len(values), 2)
                    }
                else:
                    metrics_stats[metric] = {'count': 0, 'min': 0, 'max': 0, 'avg': 0}
            
            print(f"総投稿数: {total_posts}")
            print("\nメトリクス統計:")
            for metric, stats in metrics_stats.items():
                print(f"  {metric}: 有効データ{stats['count']}件, 平均{stats['avg']}, 範囲{stats['min']}-{stats['max']}")
            
            # エンゲージメント率の統計
            engagement_rates = [data.get('engagement_rate', 0) for data in all_metrics_data]
            avg_engagement = round(sum(engagement_rates) / len(engagement_rates), 2) if engagement_rates else 0
            print(f"\n平均エンゲージメント率: {avg_engagement}%")
            
            # 結果の保存
            output_file = 'post_metrics_verification.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 メトリクスデータを {output_file} に保存しました")
            
            # post_metricsテーブル用サンプルデータ
            sample_file = 'post_metrics_table_sample.json'
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics_data, f, ensure_ascii=False, indent=2)
            
            print(f"📝 post_metricsテーブル用サンプルデータを {sample_file} に保存しました")
            
            return all_metrics_data
        else:
            print("❌ メトリクスデータが取得できませんでした")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 投稿一覧取得エラー: {e}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

if __name__ == "__main__":
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN, USERNAME]):
        print("❌ 環境変数が不足しています。.envファイルを確認してください。")
        exit(1)
    
    result = get_post_metrics()
    
    if result:
        print("\n" + "=" * 50)
        print("Phase 2 完了: 投稿メトリクス取得検証 ✅")
        print("=" * 50)
        print("次のステップ: 03_data_integration.py を実行してください")
    else:
        print("\n" + "=" * 50)
        print("Phase 2 失敗: 投稿メトリクス取得検証 ❌")
        print("=" * 50)