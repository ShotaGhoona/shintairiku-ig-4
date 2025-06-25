#!/usr/bin/env python3
"""
利用可能な全メトリクスを網羅的に検証
DBカラムにとらわれず、実際に取得可能なデータを全て調査
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def explore_all_available_metrics():
    """利用可能な全メトリクスを網羅的に探索"""
    
    print("🔍 Instagram API 利用可能メトリクス全探索")
    print("=" * 60)
    
    # まず投稿を取得
    media_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    media_params = {
        'fields': 'id,media_type,caption',
        'access_token': ACCESS_TOKEN,
        'limit': 10
    }
    
    try:
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        posts = media_response.json().get('data', [])
        
        if not posts:
            print("❌ 投稿が見つかりません")
            return
        
        print(f"📊 {len(posts)}件の投稿で検証します")
        
        # 可能な限り多くのメトリクスを試す（公式ドキュメント + 推測）
        potential_metrics = [
            # 基本エンゲージメント
            'likes', 'comments', 'shares', 'saved', 'saves',
            
            # リーチ・インプレッション系
            'reach', 'impressions', 'frequency',
            
            # 視聴・再生系
            'views', 'video_views', 'plays', 'replays',
            'ig_reels_video_view_total_time', 'ig_reels_avg_watch_time',
            'clips_replays_count', 'ig_reels_aggregated_all_plays_count',
            
            # インタラクション系
            'total_interactions', 'engagement',
            
            # フォロー・プロフィール系
            'follows', 'profile_visits', 'profile_views', 'profile_activity',
            
            # ナビゲーション・行動系
            'navigation', 'website_clicks', 'get_directions_clicks',
            'phone_number_clicks', 'text_message_clicks', 'email_contacts',
            
            # Story専用（試してみる）
            'story_exits', 'story_replies', 'story_taps_forward', 'story_taps_back',
            
            # Reels専用
            'reel_comments', 'reel_likes', 'reel_plays', 'reel_reach',
            'reel_shares', 'reel_saves',
            
            # その他
            'replies', 'carousel_album_engagement', 'carousel_album_reach',
            'carousel_album_impressions', 'photo_view', 'video_view'
        ]
        
        # メディアタイプごとの結果を保存
        results_by_media_type = {}
        
        # 各投稿で全メトリクスをテスト
        for i, post in enumerate(posts):
            post_id = post.get('id')
            media_type = post.get('media_type')
            caption_preview = post.get('caption', '')[:50] + '...' if post.get('caption') else 'キャプションなし'
            
            print(f"\n📝 投稿 {i+1}: {media_type}")
            print(f"   ID: {post_id}")
            print(f"   キャプション: {caption_preview}")
            
            if media_type not in results_by_media_type:
                results_by_media_type[media_type] = {
                    'available_metrics': [],
                    'sample_values': {},
                    'error_messages': []
                }
            
            # 個別メトリクステスト
            print(f"   🧪 メトリクステスト:")
            
            available_metrics = []
            sample_values = {}
            
            for metric in potential_metrics:
                try:
                    insights_url = f"https://graph.facebook.com/{post_id}/insights"
                    insights_params = {
                        'metric': metric,
                        'access_token': ACCESS_TOKEN
                    }
                    
                    response = requests.get(insights_url, params=insights_params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data') and len(data['data']) > 0:
                            metric_data = data['data'][0]
                            values = metric_data.get('values', [])
                            if values and len(values) > 0:
                                value = values[0].get('value')
                                available_metrics.append(metric)
                                sample_values[metric] = value
                                print(f"     ✅ {metric}: {value}")
                            else:
                                print(f"     ⚪ {metric}: データなし")
                        else:
                            print(f"     ⚪ {metric}: 空レスポンス")
                    elif response.status_code == 400:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                        print(f"     ❌ {metric}: {error_msg}")
                    else:
                        print(f"     ❌ {metric}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"     ❌ {metric}: 例外 {str(e)[:50]}")
            
            # メディアタイプごとの結果を更新
            results_by_media_type[media_type]['available_metrics'] = list(set(
                results_by_media_type[media_type]['available_metrics'] + available_metrics
            ))
            results_by_media_type[media_type]['sample_values'].update(sample_values)
            
            print(f"   📊 利用可能: {len(available_metrics)}個のメトリクス")
            
            # 最初の3投稿で詳細チェックを行い、残りは概要のみ
            if i >= 2:
                print(f"   ... (詳細スキップ)")
                break
        
        # 結果のサマリー
        print(f"\n" + "=" * 60)
        print("📋 メディアタイプ別利用可能メトリクス サマリー")
        print("=" * 60)
        
        all_available_metrics = set()
        
        for media_type, data in results_by_media_type.items():
            available = data['available_metrics']
            all_available_metrics.update(available)
            
            print(f"\n📊 {media_type} ({len(available)}個のメトリクス):")
            for metric in sorted(available):
                sample_value = data['sample_values'].get(metric, 'N/A')
                print(f"  ✅ {metric}: {sample_value}")
        
        print(f"\n🎯 全体サマリー:")
        print(f"  利用可能メトリクス総数: {len(all_available_metrics)}個")
        print(f"  メディアタイプ数: {len(results_by_media_type)}種類")
        
        # 重要なメトリクスの確認
        important_metrics = {
            'likes': 'いいね数',
            'comments': 'コメント数', 
            'saved': '保存数',
            'saves': '保存数(別名)',
            'shares': 'シェア数',
            'views': '視聴回数',
            'reach': 'リーチ数',
            'impressions': 'インプレッション数',
            'total_interactions': '総インタラクション数'
        }
        
        print(f"\n🔍 重要メトリクスの利用可否:")
        for metric, description in important_metrics.items():
            status = "✅ 利用可能" if metric in all_available_metrics else "❌ 利用不可"
            print(f"  {metric} ({description}): {status}")
        
        # 詳細結果をファイルに保存
        detailed_results = {
            'exploration_date': datetime.now().isoformat(),
            'total_posts_tested': len(posts),
            'results_by_media_type': results_by_media_type,
            'all_available_metrics': list(all_available_metrics),
            'important_metrics_status': {
                metric: metric in all_available_metrics 
                for metric in important_metrics.keys()
            }
        }
        
        output_file = 'comprehensive_metrics_exploration.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細結果を {output_file} に保存しました")
        
        return detailed_results
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def test_combined_metrics():
    """複数メトリクスの同時取得テスト"""
    
    print(f"\n" + "=" * 60)
    print("🔄 複数メトリクス同時取得テスト")
    print("=" * 60)
    
    # 利用可能と分かったメトリクスの組み合わせをテスト
    metric_combinations = [
        # 基本セット
        ['likes', 'comments', 'shares'],
        # 拡張セット1
        ['likes', 'comments', 'shares', 'views', 'reach'],
        # 拡張セット2
        ['likes', 'comments', 'saved', 'shares', 'views', 'reach', 'total_interactions'],
        # 全部込み
        ['likes', 'comments', 'saved', 'shares', 'views', 'reach', 'impressions', 'total_interactions', 'follows']
    ]
    
    # テスト用の投稿ID取得
    media_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    media_params = {
        'fields': 'id,media_type',
        'access_token': ACCESS_TOKEN,
        'limit': 1
    }
    
    try:
        response = requests.get(media_url, params=media_params)
        response.raise_for_status()
        posts = response.json().get('data', [])
        
        if not posts:
            print("❌ テスト用投稿が見つかりません")
            return
        
        test_post_id = posts[0]['id']
        test_media_type = posts[0]['media_type']
        
        print(f"📝 テスト投稿: {test_post_id} ({test_media_type})")
        
        combination_results = []
        
        for i, metrics in enumerate(metric_combinations):
            print(f"\n🧪 組み合わせ {i+1}: {metrics}")
            
            insights_url = f"https://graph.facebook.com/{test_post_id}/insights"
            insights_params = {
                'metric': ','.join(metrics),
                'access_token': ACCESS_TOKEN
            }
            
            try:
                response = requests.get(insights_url, params=insights_params)
                
                if response.status_code == 200:
                    data = response.json()
                    metric_data = data.get('data', [])
                    
                    success_metrics = []
                    values = {}
                    
                    for metric_item in metric_data:
                        metric_name = metric_item.get('name')
                        metric_values = metric_item.get('values', [])
                        if metric_values:
                            value = metric_values[0].get('value')
                            success_metrics.append(metric_name)
                            values[metric_name] = value
                    
                    print(f"  ✅ 成功: {len(success_metrics)}/{len(metrics)} メトリクス")
                    for metric in success_metrics:
                        print(f"    {metric}: {values[metric]}")
                    
                    failed_metrics = [m for m in metrics if m not in success_metrics]
                    if failed_metrics:
                        print(f"  ❌ 失敗: {failed_metrics}")
                    
                    combination_results.append({
                        'metrics_requested': metrics,
                        'metrics_successful': success_metrics,
                        'metrics_failed': failed_metrics,
                        'values': values,
                        'success_rate': len(success_metrics) / len(metrics)
                    })
                    
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
                    combination_results.append({
                        'metrics_requested': metrics,
                        'metrics_successful': [],
                        'metrics_failed': metrics,
                        'error': response.text,
                        'success_rate': 0
                    })
                    
            except Exception as e:
                print(f"  ❌ 例外: {e}")
        
        # 最適な組み合わせを特定
        if combination_results:
            best_combination = max(combination_results, key=lambda x: x['success_rate'])
            print(f"\n🏆 最適な組み合わせ:")
            print(f"  メトリクス: {best_combination['metrics_successful']}")
            print(f"  成功率: {best_combination['success_rate']*100:.1f}%")
        
        return combination_results
        
    except Exception as e:
        print(f"❌ 組み合わせテストエラー: {e}")
        return []

if __name__ == "__main__":
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN]):
        print("❌ 環境変数が不足しています")
        exit(1)
    
    print("🚀 Instagram API メトリクス全探索を開始します...")
    
    # 1. 全メトリクス探索
    exploration_results = explore_all_available_metrics()
    
    # 2. 組み合わせテスト
    combination_results = test_combined_metrics()
    
    if exploration_results:
        print(f"\n" + "🎉" * 20)
        print("✅ メトリクス探索完了!")
        print("📁 comprehensive_metrics_exploration.json で詳細確認可能")
        print("🎉" * 20)
    else:
        print(f"\n❌ メトリクス探索に失敗しました")