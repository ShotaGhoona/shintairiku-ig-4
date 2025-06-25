#!/usr/bin/env python3
"""
Instagram Graph API アカウントレベルインサイト詳細検証
フォロワー数、プロフィール訪問数など日別統計に必要なデータの取得可能性を詳しく検証
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def test_instagram_insights_api():
    """Instagram Insights API の詳細テスト"""
    
    print("🔍 Instagram Insights API 詳細検証")
    print("=" * 60)
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # 日別統計で必要と思われるメトリクス
    daily_stats_metrics = [
        # フォロワー系（日別統計の核となるデータ）
        'follower_count',           # フォロワー数
        'followers_count',          # フォロワー数（別名）
        'total_followers',          # 総フォロワー数
        
        # リーチ・露出系
        'reach',                    # リーチ数
        'impressions',              # インプレッション数
        'accounts_engaged',         # エンゲージメントアカウント数
        'accounts_reached',         # リーチアカウント数
        
        # プロフィール活動系
        'profile_views',            # プロフィール閲覧数
        'website_clicks',           # ウェブサイトクリック数
        'get_directions_clicks',    # 道順クリック数
        'phone_number_clicks',      # 電話番号クリック数
        'text_message_clicks',      # テキストメッセージクリック数
        'email_contacts',           # メール連絡数
        
        # エンゲージメント系
        'total_interactions',       # 総インタラクション数
        'likes',                    # いいね数
        'comments',                 # コメント数
        'shares',                   # シェア数
        'saves',                    # 保存数
        'saved',                    # 保存数（post検証で確認された正しい名前）
        
        # オーディエンス系
        'online_followers',         # オンラインフォロワー
        'audience_locale',          # オーディエンス地域
        'audience_country',         # オーディエンス国
        'audience_city',            # オーディエンス都市
        'audience_gender_age',      # オーディエンス性別・年齢
        
        # その他
        'video_views',              # 動画視聴数
        'story_exits',              # ストーリー離脱数
        'story_replies',            # ストーリー返信数
        'story_taps_forward',       # ストーリー早送りタップ数
        'story_taps_back',          # ストーリー戻しタップ数
    ]
    
    # 期間テストパターン
    today = datetime.now()
    periods_to_test = [
        {
            'name': 'yesterday',
            'since': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        },
        {
            'name': 'last_7_days',
            'since': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        },
        {
            'name': 'last_30_days',
            'since': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        },
        {
            'name': 'lifetime',
            'since': None,
            'until': None,
            'period': 'lifetime'
        }
    ]
    
    verification_results = {}
    
    for metric in daily_stats_metrics:
        print(f"\n📊 メトリクス検証: {metric}")
        
        metric_results = {
            'metric_name': metric,
            'available': False,
            'period_results': {},
            'best_period': None,
            'sample_data': None,
            'data_structure': None
        }
        
        for period_config in periods_to_test:
            period_name = period_config['name']
            
            try:
                params = {
                    'metric': metric,
                    'access_token': ACCESS_TOKEN
                }
                
                # 期間パラメータ設定
                if period_config['since'] and period_config['until']:
                    params['since'] = period_config['since']
                    params['until'] = period_config['until']
                
                if period_config['period'] != 'lifetime':
                    params['period'] = period_config['period']
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values and len(values) > 0:
                            # 成功！
                            value = values[0].get('value')
                            end_time = values[0].get('end_time')
                            
                            print(f"   ✅ {period_name}: {value} (期間: {end_time})")
                            
                            metric_results['available'] = True
                            metric_results['period_results'][period_name] = {
                                'status': 'success',
                                'value': value,
                                'end_time': end_time,
                                'metric_info': {
                                    'name': metric_data.get('name'),
                                    'period': metric_data.get('period'),
                                    'title': metric_data.get('title'),
                                    'description': metric_data.get('description')
                                },
                                'full_data': data  # デバッグ用
                            }
                            
                            # 最初に成功した期間をベストとして記録
                            if not metric_results['best_period']:
                                metric_results['best_period'] = period_name
                                metric_results['sample_data'] = value
                                metric_results['data_structure'] = metric_data
                        else:
                            print(f"   ⚪ {period_name}: データなし（values配列が空）")
                            metric_results['period_results'][period_name] = {
                                'status': 'no_values',
                                'response_structure': data
                            }
                    else:
                        print(f"   ⚪ {period_name}: データなし（data配列が空）")
                        metric_results['period_results'][period_name] = {
                            'status': 'no_data',
                            'response': data
                        }
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    error_code = error_data.get('error', {}).get('code', 'Unknown code')
                    
                    print(f"   ❌ {period_name}: {error_msg} (コード: {error_code})")
                    
                    metric_results['period_results'][period_name] = {
                        'status': 'error',
                        'error_message': error_msg,
                        'error_code': error_code,
                        'error_type': error_data.get('error', {}).get('type')
                    }
                    
                else:
                    print(f"   ❓ {period_name}: HTTP {response.status_code}")
                    metric_results['period_results'][period_name] = {
                        'status': 'http_error',
                        'status_code': response.status_code,
                        'response_text': response.text[:200]
                    }
                    
            except Exception as e:
                print(f"   💥 {period_name}: 例外 {str(e)[:50]}...")
                metric_results['period_results'][period_name] = {
                    'status': 'exception',
                    'error': str(e)
                }
        
        verification_results[metric] = metric_results
        
        # メトリクス全体の可用性表示
        if metric_results['available']:
            print(f"   🎯 {metric}: 利用可能 (推奨期間: {metric_results['best_period']})")
        else:
            print(f"   ❌ {metric}: 全期間で利用不可")
    
    return verification_results

def test_time_series_data():
    """時系列データの取得詳細テスト"""
    
    print(f"\n" + "=" * 60)
    print("📈 時系列データ取得テスト")
    print("=" * 60)
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # 利用可能と判明したメトリクスがあれば、詳細な時系列取得をテスト
    # まずは基本的なメトリクスで試行
    test_metrics = ['reach', 'profile_views', 'impressions', 'follower_count']
    
    today = datetime.now()
    
    # 詳細な期間テスト
    time_series_tests = [
        {
            'name': 'single_day',
            'description': '単日データ',
            'since': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        },
        {
            'name': 'weekly_breakdown',
            'description': '週間内訳',
            'since': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        },
        {
            'name': 'monthly_breakdown',
            'description': '月間内訳',
            'since': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'period': 'day'
        }
    ]
    
    time_series_results = {}
    
    for metric in test_metrics:
        print(f"\n📊 時系列テスト: {metric}")
        
        metric_time_results = {}
        
        for test_config in time_series_tests:
            test_name = test_config['name']
            
            try:
                params = {
                    'metric': metric,
                    'since': test_config['since'],
                    'until': test_config['until'],
                    'period': test_config['period'],
                    'access_token': ACCESS_TOKEN
                }
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values:
                            print(f"   ✅ {test_config['description']}: {len(values)}件のデータポイント")
                            
                            # 時系列データの詳細分析
                            value_analysis = {
                                'data_points': len(values),
                                'sample_values': values[:3],  # 最初の3件をサンプル
                                'date_range': {
                                    'first': values[0].get('end_time') if values else None,
                                    'last': values[-1].get('end_time') if values else None
                                },
                                'data_structure': metric_data
                            }
                            
                            metric_time_results[test_name] = {
                                'status': 'success',
                                'analysis': value_analysis
                            }
                            
                            # サンプルデータ表示
                            for i, value_data in enumerate(values[:3]):
                                end_time = value_data.get('end_time', 'N/A')
                                value = value_data.get('value', 'N/A')
                                print(f"     📅 {end_time}: {value}")
                            
                            if len(values) > 3:
                                print(f"     ... 他 {len(values) - 3} 件")
                        else:
                            print(f"   ⚪ {test_config['description']}: データなし")
                            metric_time_results[test_name] = {
                                'status': 'no_values'
                            }
                    else:
                        print(f"   ⚪ {test_config['description']}: 空レスポンス")
                        metric_time_results[test_name] = {
                            'status': 'empty_response'
                        }
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    print(f"   ❌ {test_config['description']}: {error_msg[:60]}...")
                    
                    metric_time_results[test_name] = {
                        'status': 'error',
                        'error_message': error_msg
                    }
                else:
                    print(f"   ❓ {test_config['description']}: HTTP {response.status_code}")
                    metric_time_results[test_name] = {
                        'status': 'http_error',
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                print(f"   💥 {test_config['description']}: {str(e)[:50]}...")
                metric_time_results[test_name] = {
                    'status': 'exception',
                    'error': str(e)
                }
        
        time_series_results[metric] = metric_time_results
    
    return time_series_results

def test_combined_metrics():
    """複数メトリクス同時取得テスト"""
    
    print(f"\n" + "=" * 60)
    print("🔄 複数メトリクス同時取得テスト")
    print("=" * 60)
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # 様々な組み合わせパターンをテスト
    metric_combinations = [
        {
            'name': 'basic_daily_stats',
            'description': '基本日別統計',
            'metrics': ['reach', 'profile_views', 'website_clicks']
        },
        {
            'name': 'follower_focused',
            'description': 'フォロワー関連',
            'metrics': ['follower_count', 'followers_count', 'total_followers']
        },
        {
            'name': 'engagement_focused',
            'description': 'エンゲージメント関連', 
            'metrics': ['likes', 'comments', 'shares', 'total_interactions']
        },
        {
            'name': 'profile_activity',
            'description': 'プロフィール活動',
            'metrics': ['profile_views', 'website_clicks', 'get_directions_clicks', 'phone_number_clicks']
        },
        {
            'name': 'comprehensive',
            'description': '包括的データ',
            'metrics': ['reach', 'impressions', 'profile_views', 'website_clicks', 'follower_count']
        }
    ]
    
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    combination_results = {}
    
    for combo in metric_combinations:
        combo_name = combo['name']
        metrics = combo['metrics']
        description = combo['description']
        
        print(f"\n🧪 組み合わせテスト: {description}")
        print(f"   メトリクス: {', '.join(metrics)}")
        
        try:
            params = {
                'metric': ','.join(metrics),
                'since': yesterday,
                'until': today_str,
                'period': 'day',
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(insights_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data'):
                    successful_metrics = []
                    metric_values = {}
                    
                    for metric_data in data['data']:
                        metric_name = metric_data.get('name')
                        values = metric_data.get('values', [])
                        
                        if values:
                            value = values[0].get('value')
                            successful_metrics.append(metric_name)
                            metric_values[metric_name] = value
                            print(f"   ✅ {metric_name}: {value}")
                        else:
                            print(f"   ⚪ {metric_name}: データなし")
                    
                    combination_results[combo_name] = {
                        'status': 'success',
                        'requested_metrics': metrics,
                        'successful_metrics': successful_metrics,
                        'failed_metrics': [m for m in metrics if m not in successful_metrics],
                        'metric_values': metric_values,
                        'success_rate': len(successful_metrics) / len(metrics),
                        'full_response': data
                    }
                    
                    print(f"   📊 成功率: {len(successful_metrics)}/{len(metrics)} ({len(successful_metrics)/len(metrics)*100:.1f}%)")
                else:
                    print(f"   ⚪ データなし")
                    combination_results[combo_name] = {
                        'status': 'no_data',
                        'requested_metrics': metrics
                    }
                    
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"   ❌ エラー: {error_msg[:60]}...")
                
                combination_results[combo_name] = {
                    'status': 'error',
                    'requested_metrics': metrics,
                    'error_message': error_msg
                }
            else:
                print(f"   ❓ HTTP {response.status_code}")
                combination_results[combo_name] = {
                    'status': 'http_error',
                    'requested_metrics': metrics,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            print(f"   💥 例外: {str(e)[:50]}...")
            combination_results[combo_name] = {
                'status': 'exception',
                'requested_metrics': metrics,
                'error': str(e)
            }
    
    return combination_results

def save_verification_results(insights_results, time_series_results, combination_results):
    """検証結果を保存"""
    
    output_dir = "output-json"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 総合結果
    comprehensive_results = {
        'verification_date': datetime.now().isoformat(),
        'instagram_user_id': INSTAGRAM_USER_ID,
        'insights_verification': insights_results,
        'time_series_verification': time_series_results,
        'combination_verification': combination_results,
        'summary': {
            'total_metrics_tested': len(insights_results),
            'available_metrics': len([r for r in insights_results.values() if r.get('available')]),
            'successful_combinations': len([r for r in combination_results.values() if r.get('status') == 'success'])
        }
    }
    
    # メイン結果ファイル
    main_file = f"{output_dir}/02_account_insights_verification_{timestamp}.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 検証結果を保存: {main_file}")
    
    # 利用可能メトリクスサマリー
    available_metrics = {
        metric: data for metric, data in insights_results.items() 
        if data.get('available')
    }
    
    if available_metrics:
        summary_file = f"{output_dir}/02_available_insights_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'verification_date': datetime.now().isoformat(),
                'available_metrics_count': len(available_metrics),
                'available_metrics': available_metrics,
                'recommended_combinations': [
                    combo for combo_name, combo in combination_results.items() 
                    if combo.get('status') == 'success' and combo.get('success_rate', 0) > 0.5
                ]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 利用可能メトリクスサマリー: {summary_file}")
        return main_file, summary_file
    
    return main_file, None

def main():
    """メイン実行関数"""
    
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN]):
        print("❌ 環境変数が不足しています")
        exit(1)
    
    print("🚀 Instagram Account Insights 詳細検証を開始します...")
    
    try:
        # 1. インサイトメトリクス詳細検証
        print("\n" + "🎯" * 20)
        insights_results = test_instagram_insights_api()
        
        # 2. 時系列データ取得テスト
        print("\n" + "🎯" * 20)
        time_series_results = test_time_series_data()
        
        # 3. 複数メトリクス同時取得テスト
        print("\n" + "🎯" * 20)
        combination_results = test_combined_metrics()
        
        # 4. 結果保存
        print("\n" + "=" * 60)
        main_file, summary_file = save_verification_results(
            insights_results, time_series_results, combination_results
        )
        
        # 5. 最終サマリー
        print("📋 Account Insights 検証結果サマリー")
        print("=" * 60)
        
        available_metrics = [
            metric for metric, data in insights_results.items() 
            if data.get('available')
        ]
        
        successful_combinations = [
            combo for combo, data in combination_results.items() 
            if data.get('status') == 'success'
        ]
        
        print(f"✅ 利用可能インサイトメトリクス: {len(available_metrics)}")
        for metric in available_metrics:
            best_period = insights_results[metric].get('best_period', 'N/A')
            sample_value = insights_results[metric].get('sample_data', 'N/A')
            print(f"   📊 {metric} (期間: {best_period}, サンプル値: {sample_value})")
        
        print(f"\n✅ 成功した組み合わせ: {len(successful_combinations)}")
        for combo in successful_combinations:
            success_rate = combination_results[combo].get('success_rate', 0)
            print(f"   🔄 {combo} (成功率: {success_rate*100:.1f}%)")
        
        print(f"\n" + "🎉" * 20)
        print("✅ Account Insights 詳細検証完了!")
        print(f"📁 詳細結果: {main_file}")
        if summary_file:
            print(f"📁 利用可能メトリクス: {summary_file}")
        print("🎉" * 20)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 検証中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)