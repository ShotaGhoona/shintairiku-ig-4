#!/usr/bin/env python3
"""
Instagram Graph API での日別統計データ取得可能エンドポイント全探索
月間分析画面で使用する日別データの取得可能性を検証
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def explore_account_insights():
    """アカウントレベルのインサイト取得可能性を探索"""
    
    print("🔍 Instagram アカウントインサイト エンドポイント探索")
    print("=" * 60)
    
    # 可能性があるエンドポイント
    potential_endpoints = [
        # Instagram Graph API
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights",
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media_insights",
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/analytics",
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/stats",
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/daily_stats",
        
        # Facebook Graph API (Instagram関連)
        f"https://graph.facebook.com/{INSTAGRAM_USER_ID}",
        f"https://graph.facebook.com/v23.0/{INSTAGRAM_USER_ID}/insights",
        f"https://graph.facebook.com/v23.0/{INSTAGRAM_USER_ID}/media_insights",
    ]
    
    results = {}
    
    for endpoint in potential_endpoints:
        print(f"\n🧪 テスト中: {endpoint}")
        
        try:
            # 基本的なパラメータでテスト
            params = {
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(endpoint, params=params)
            status_code = response.status_code
            
            print(f"   ステータス: {status_code}")
            
            if status_code == 200:
                data = response.json()
                print(f"   ✅ 成功! データ取得可能")
                print(f"   レスポンス構造: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
                results[endpoint] = {
                    'status': 'success',
                    'status_code': status_code,
                    'data_structure': list(data.keys()) if isinstance(data, dict) else str(type(data)),
                    'sample_data': data if len(str(data)) < 500 else str(data)[:500] + "..."
                }
                
            elif status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ Bad Request: {error_msg}")
                
                results[endpoint] = {
                    'status': 'bad_request',
                    'status_code': status_code,
                    'error_message': error_msg,
                    'error_type': error_data.get('error', {}).get('type', 'Unknown')
                }
                
            elif status_code == 403:
                print(f"   🔒 権限なし: このエンドポイントは利用不可")
                results[endpoint] = {
                    'status': 'permission_denied',
                    'status_code': status_code
                }
                
            else:
                print(f"   ❓ その他のレスポンス: {status_code}")
                results[endpoint] = {
                    'status': 'other',
                    'status_code': status_code,
                    'response_text': response.text[:200] if response.text else "No content"
                }
                
        except Exception as e:
            print(f"   💥 例外発生: {str(e)[:100]}")
            results[endpoint] = {
                'status': 'exception',
                'error': str(e)
            }
    
    return results

def explore_insights_metrics():
    """インサイトAPIで利用可能なメトリクスを探索"""
    
    print(f"\n" + "=" * 60)
    print("🎯 Instagram インサイトメトリクス探索")
    print("=" * 60)
    
    # アカウントレベルで利用可能な可能性があるメトリクス
    potential_metrics = [
        # フォロワー系
        'follower_count', 'followers_count', 'total_followers',
        'new_followers', 'follower_demographics', 'follower_growth',
        
        # リーチ・インプレッション系
        'reach', 'impressions', 'total_reach', 'daily_reach',
        'accounts_engaged', 'accounts_reached',
        
        # プロフィール系
        'profile_views', 'profile_visits', 'profile_activity',
        'website_clicks', 'get_directions_clicks', 'phone_number_clicks',
        'email_contacts', 'text_message_clicks',
        
        # エンゲージメント系
        'total_interactions', 'likes', 'comments', 'shares', 'saves',
        'engagement', 'engagement_rate',
        
        # コンテンツ系
        'posts_count', 'stories_count', 'reels_count',
        
        # その他
        'online_followers', 'audience_locale', 'audience_country',
        'audience_city', 'audience_gender_age'
    ]
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # 期間指定テスト
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    period_tests = [
        ('day', yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')),
        ('week', week_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')),
        ('days_28', (today - timedelta(days=28)).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')),
        ('lifetime', None, None)
    ]
    
    metric_results = {}
    
    for metric in potential_metrics:
        print(f"\n📊 メトリクステスト: {metric}")
        
        metric_results[metric] = {
            'periods_tested': {},
            'available': False,
            'best_period': None
        }
        
        for period_name, since, until in period_tests:
            try:
                params = {
                    'metric': metric,
                    'access_token': ACCESS_TOKEN
                }
                
                # 期間パラメータ追加（lifetimeの場合は不要）
                if since and until:
                    params['since'] = since
                    params['until'] = until
                    params['period'] = period_name if period_name != 'days_28' else 'day'
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values:
                            value = values[0].get('value', 'N/A')
                            print(f"   ✅ {period_name}: {value}")
                            
                            metric_results[metric]['periods_tested'][period_name] = {
                                'status': 'success',
                                'value': value,
                                'period_info': metric_data.get('period'),
                                'title': metric_data.get('title'),
                                'description': metric_data.get('description')
                            }
                            metric_results[metric]['available'] = True
                            if not metric_results[metric]['best_period']:
                                metric_results[metric]['best_period'] = period_name
                        else:
                            print(f"   ⚪ {period_name}: データなし")
                            metric_results[metric]['periods_tested'][period_name] = {
                                'status': 'no_data'
                            }
                    else:
                        print(f"   ⚪ {period_name}: 空レスポンス")
                        metric_results[metric]['periods_tested'][period_name] = {
                            'status': 'empty_response'
                        }
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    print(f"   ❌ {period_name}: {error_msg[:50]}...")
                    
                    metric_results[metric]['periods_tested'][period_name] = {
                        'status': 'error',
                        'error_message': error_msg
                    }
                else:
                    print(f"   ❓ {period_name}: HTTP {response.status_code}")
                    metric_results[metric]['periods_tested'][period_name] = {
                        'status': 'http_error',
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                print(f"   💥 {period_name}: 例外 {str(e)[:30]}...")
                metric_results[metric]['periods_tested'][period_name] = {
                    'status': 'exception',
                    'error': str(e)
                }
        
        # メトリクスが利用不可の場合のみ表示
        if not metric_results[metric]['available']:
            print(f"   ❌ {metric}: 全期間で利用不可")
    
    return metric_results

def test_basic_account_info():
    """基本的なアカウント情報取得テスト"""
    
    print(f"\n" + "=" * 60)
    print("👤 基本アカウント情報取得テスト")
    print("=" * 60)
    
    # 基本情報エンドポイント
    basic_info_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}"
    
    # 取得可能フィールドをテスト
    potential_fields = [
        'account_type', 'id', 'media_count', 'username',
        'name', 'profile_picture_url', 'biography', 'website',
        'followers_count', 'follows_count', 'media_count',
        'business_discovery'
    ]
    
    results = {}
    
    # 個別フィールドテスト
    for field in potential_fields:
        try:
            params = {
                'fields': field,
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(basic_info_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {field}: {data.get(field, 'N/A')}")
                results[field] = {
                    'status': 'success',
                    'value': data.get(field)
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"❌ {field}: {error_msg[:50]}...")
                results[field] = {
                    'status': 'error',
                    'error': error_msg
                }
                
        except Exception as e:
            print(f"💥 {field}: {str(e)[:50]}...")
            results[field] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # 複数フィールド同時取得テスト
    print(f"\n🔄 複数フィールド同時取得テスト")
    successful_fields = [field for field, result in results.items() if result['status'] == 'success']
    
    if successful_fields:
        try:
            params = {
                'fields': ','.join(successful_fields),
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(basic_info_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 同時取得成功: {len(data)} フィールド")
                results['combined_fields'] = {
                    'status': 'success',
                    'fields': successful_fields,
                    'data': data
                }
            else:
                print(f"❌ 同時取得失敗: HTTP {response.status_code}")
                results['combined_fields'] = {
                    'status': 'failed',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            print(f"💥 同時取得例外: {str(e)[:50]}...")
            results['combined_fields'] = {
                'status': 'exception',
                'error': str(e)
            }
    
    return results

def save_results_to_json(endpoint_results, metric_results, account_info_results):
    """探索結果をJSONファイルに保存"""
    
    output_dir = "output-json"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 統合結果
    comprehensive_results = {
        'exploration_date': datetime.now().isoformat(),
        'instagram_user_id': INSTAGRAM_USER_ID,
        'endpoint_exploration': endpoint_results,
        'metrics_exploration': metric_results,
        'account_info_exploration': account_info_results,
        'summary': {
            'total_endpoints_tested': len(endpoint_results),
            'successful_endpoints': len([r for r in endpoint_results.values() if r.get('status') == 'success']),
            'total_metrics_tested': len(metric_results),
            'available_metrics': len([r for r in metric_results.values() if r.get('available')]),
            'successful_fields': len([r for r in account_info_results.values() if r.get('status') == 'success' and isinstance(r, dict)])
        }
    }
    
    # メイン結果ファイル
    main_file = f"{output_dir}/01_daily_stats_endpoints_exploration_{timestamp}.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 探索結果を保存: {main_file}")
    
    # 利用可能メトリクスのみ抽出
    available_metrics = {
        metric: data for metric, data in metric_results.items() 
        if data.get('available')
    }
    
    if available_metrics:
        available_file = f"{output_dir}/01_available_daily_metrics_{timestamp}.json"
        with open(available_file, 'w', encoding='utf-8') as f:
            json.dump({
                'exploration_date': datetime.now().isoformat(),
                'available_metrics': available_metrics,
                'count': len(available_metrics)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 利用可能メトリクス抽出: {available_file}")
    
    return main_file, available_file if available_metrics else None

def main():
    """メイン実行関数"""
    
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN]):
        print("❌ 環境変数が不足しています")
        exit(1)
    
    print("🚀 Instagram Daily Stats エンドポイント探索を開始します...")
    
    try:
        # 1. エンドポイント探索
        print("\n" + "🎯" * 20)
        endpoint_results = explore_account_insights()
        
        # 2. メトリクス探索
        print("\n" + "🎯" * 20)
        metric_results = explore_insights_metrics()
        
        # 3. 基本アカウント情報テスト
        print("\n" + "🎯" * 20)
        account_info_results = test_basic_account_info()
        
        # 4. 結果保存
        print("\n" + "=" * 60)
        main_file, available_file = save_results_to_json(
            endpoint_results, metric_results, account_info_results
        )
        
        # 5. サマリー表示
        print("📋 探索結果サマリー")
        print("=" * 60)
        
        successful_endpoints = [
            endpoint for endpoint, result in endpoint_results.items() 
            if result.get('status') == 'success'
        ]
        
        available_metrics = [
            metric for metric, data in metric_results.items() 
            if data.get('available')
        ]
        
        successful_fields = [
            field for field, result in account_info_results.items() 
            if result.get('status') == 'success' and isinstance(result, dict)
        ]
        
        print(f"✅ 利用可能エンドポイント: {len(successful_endpoints)}")
        for endpoint in successful_endpoints:
            print(f"   📍 {endpoint}")
        
        print(f"\n✅ 利用可能メトリクス: {len(available_metrics)}")
        for metric in available_metrics:
            best_period = metric_results[metric].get('best_period', 'N/A')
            print(f"   📊 {metric} (期間: {best_period})")
        
        print(f"\n✅ 利用可能フィールド: {len(successful_fields)}")
        for field in successful_fields:
            value = account_info_results[field].get('value', 'N/A')
            value_str = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
            print(f"   📝 {field}: {value_str}")
        
        print(f"\n" + "🎉" * 20)
        print("✅ Daily Stats エンドポイント探索完了!")
        print(f"📁 詳細結果: {main_file}")
        if available_file:
            print(f"📁 利用可能メトリクス: {available_file}")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"\n❌ 探索中にエラーが発生しました: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)