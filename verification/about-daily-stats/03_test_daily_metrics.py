#!/usr/bin/env python3
"""
Instagram Graph API 日別メトリクス実際の取得テスト
実際にDBの daily_stats テーブルに必要なデータが取得可能かを実証
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def test_daily_stats_requirements():
    """daily_statsテーブル要件に基づくメトリクス取得テスト"""
    
    print("🎯 daily_stats テーブル要件メトリクス取得テスト")
    print("=" * 60)
    
    # DBスキーマ要件（docs/suggest/db/02-simple-instagram-db-design.mdより）
    daily_stats_requirements = {
        'followers_count': {
            'description': 'フォロワー数',
            'db_column': 'followers_count',
            'api_candidates': ['follower_count', 'followers_count', 'total_followers'],
            'required': True,
            'data_type': 'integer'
        },
        'following_count': {
            'description': 'フォロー数',
            'db_column': 'following_count', 
            'api_candidates': ['following_count', 'follows_count', 'total_following'],
            'required': True,
            'data_type': 'integer'
        },
        'new_followers': {
            'description': '新規フォロワー数',
            'db_column': 'new_followers',
            'api_candidates': ['new_followers', 'follower_growth', 'followers_gained'],
            'required': False,
            'data_type': 'integer'
        },
        'profile_views': {
            'description': 'プロフィール閲覧数',
            'db_column': 'profile_views',
            'api_candidates': ['profile_views', 'profile_visits'],
            'required': True,
            'data_type': 'integer'
        },
        'website_clicks': {
            'description': 'ウェブサイトクリック数',
            'db_column': 'website_clicks',
            'api_candidates': ['website_clicks', 'website_taps'],
            'required': False,
            'data_type': 'integer'
        },
        'reach': {
            'description': 'リーチ数',
            'db_column': 'reach',
            'api_candidates': ['reach', 'accounts_reached'],
            'required': False,
            'data_type': 'integer'
        }
    }
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    requirement_test_results = {}
    
    for req_name, req_info in daily_stats_requirements.items():
        print(f"\n📊 要件テスト: {req_info['description']} ({req_name})")
        print(f"   DB列: {req_info['db_column']}")
        print(f"   必須: {'Yes' if req_info['required'] else 'No'}")
        print(f"   候補API: {', '.join(req_info['api_candidates'])}")
        
        req_results = {
            'requirement_name': req_name,
            'db_column': req_info['db_column'],
            'description': req_info['description'],
            'required': req_info['required'],
            'api_candidates': req_info['api_candidates'],
            'successful_api': None,
            'api_test_results': {},
            'recommended_implementation': None
        }
        
        # 各候補APIをテスト
        for api_metric in req_info['api_candidates']:
            print(f"   🧪 APIテスト: {api_metric}")
            
            try:
                params = {
                    'metric': api_metric,
                    'since': yesterday,
                    'until': today_str,
                    'period': 'day',
                    'access_token': ACCESS_TOKEN
                }
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values and len(values) > 0:
                            value = values[0].get('value')
                            end_time = values[0].get('end_time')
                            
                            print(f"     ✅ 成功: {value} (日時: {end_time})")
                            
                            req_results['api_test_results'][api_metric] = {
                                'status': 'success',
                                'value': value,
                                'end_time': end_time,
                                'metric_info': {
                                    'name': metric_data.get('name'),
                                    'title': metric_data.get('title'),
                                    'description': metric_data.get('description'),
                                    'period': metric_data.get('period')
                                }
                            }
                            
                            # 最初に成功したAPIを推奨として記録
                            if not req_results['successful_api']:
                                req_results['successful_api'] = api_metric
                                req_results['recommended_implementation'] = {
                                    'api_metric': api_metric,
                                    'sample_value': value,
                                    'data_validation': {
                                        'is_numeric': isinstance(value, (int, float)),
                                        'is_positive': value >= 0 if isinstance(value, (int, float)) else False,
                                        'value_type': type(value).__name__
                                    }
                                }
                        else:
                            print(f"     ⚪ データなし")
                            req_results['api_test_results'][api_metric] = {
                                'status': 'no_data'
                            }
                    else:
                        print(f"     ⚪ 空レスポンス")
                        req_results['api_test_results'][api_metric] = {
                            'status': 'empty_response'
                        }
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    print(f"     ❌ エラー: {error_msg[:40]}...")
                    
                    req_results['api_test_results'][api_metric] = {
                        'status': 'error',
                        'error_message': error_msg
                    }
                else:
                    print(f"     ❓ HTTP {response.status_code}")
                    req_results['api_test_results'][api_metric] = {
                        'status': 'http_error',
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                print(f"     💥 例外: {str(e)[:30]}...")
                req_results['api_test_results'][api_metric] = {
                    'status': 'exception',
                    'error': str(e)
                }
        
        # 要件の実現可能性評価
        if req_results['successful_api']:
            print(f"   🎯 実現可能: {req_results['successful_api']} で取得可能")
        else:
            if req_info['required']:
                print(f"   ❌ 実現不可: 必須要件だが取得不可")
            else:
                print(f"   ⚠️  実現不可: オプション要件、取得不可")
        
        requirement_test_results[req_name] = req_results
    
    return requirement_test_results

def test_time_range_data():
    """時間範囲別データ取得テスト（daily_statsの蓄積パターン検証）"""
    
    print(f"\n" + "=" * 60)
    print("📅 時間範囲別データ取得テスト")
    print("=" * 60)
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # 利用可能と判明したメトリクスを使用
    test_metrics = ['reach', 'profile_views']  # 基本的なメトリクス
    
    today = datetime.now()
    
    # 様々な時間範囲でテスト
    time_range_tests = [
        {
            'name': 'last_1_day',
            'description': '過去1日',
            'since': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'expected_points': 1
        },
        {
            'name': 'last_3_days',
            'description': '過去3日',
            'since': (today - timedelta(days=3)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'expected_points': 3
        },
        {
            'name': 'last_7_days',
            'description': '過去7日（1週間）',
            'since': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'expected_points': 7
        },
        {
            'name': 'last_14_days',
            'description': '過去14日（2週間）',
            'since': (today - timedelta(days=14)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'expected_points': 14
        },
        {
            'name': 'last_30_days',
            'description': '過去30日（1ヶ月）',
            'since': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'until': today.strftime('%Y-%m-%d'),
            'expected_points': 30
        }
    ]
    
    time_range_results = {}
    
    for metric in test_metrics:
        print(f"\n📊 メトリクス: {metric}")
        
        metric_time_results = {}
        
        for time_test in time_range_tests:
            test_name = time_test['name']
            
            print(f"   🗓️  {time_test['description']} ({time_test['since']} to {time_test['until']})")
            
            try:
                params = {
                    'metric': metric,
                    'since': time_test['since'],
                    'until': time_test['until'],
                    'period': 'day',
                    'access_token': ACCESS_TOKEN
                }
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values:
                            actual_points = len(values)
                            expected_points = time_test['expected_points']
                            
                            print(f"     ✅ データ取得: {actual_points}件 (期待: {expected_points}件)")
                            
                            # データポイント分析
                            data_analysis = {
                                'actual_data_points': actual_points,
                                'expected_data_points': expected_points,
                                'data_completeness': actual_points / expected_points if expected_points > 0 else 0,
                                'date_range_analysis': {
                                    'first_date': values[0].get('end_time') if values else None,
                                    'last_date': values[-1].get('end_time') if values else None
                                },
                                'sample_values': [
                                    {
                                        'date': v.get('end_time'),
                                        'value': v.get('value')
                                    } for v in values[:5]  # 最初の5件
                                ],
                                'value_statistics': {
                                    'min': min(v.get('value', 0) for v in values),
                                    'max': max(v.get('value', 0) for v in values),
                                    'total': sum(v.get('value', 0) for v in values)
                                }
                            }
                            
                            # サンプルデータ表示
                            for i, value_data in enumerate(values[:3]):
                                date = value_data.get('end_time', 'N/A')
                                value = value_data.get('value', 'N/A')
                                print(f"       📅 {date}: {value}")
                            
                            if len(values) > 3:
                                print(f"       ... 他 {len(values) - 3} 件")
                            
                            metric_time_results[test_name] = {
                                'status': 'success',
                                'analysis': data_analysis
                            }
                        else:
                            print(f"     ⚪ データなし")
                            metric_time_results[test_name] = {
                                'status': 'no_data'
                            }
                    else:
                        print(f"     ⚪ 空レスポンス")
                        metric_time_results[test_name] = {
                            'status': 'empty_response'
                        }
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    print(f"     ❌ エラー: {error_msg[:50]}...")
                    
                    metric_time_results[test_name] = {
                        'status': 'error',
                        'error_message': error_msg
                    }
                else:
                    print(f"     ❓ HTTP {response.status_code}")
                    metric_time_results[test_name] = {
                        'status': 'http_error',
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                print(f"     💥 例外: {str(e)[:50]}...")
                metric_time_results[test_name] = {
                    'status': 'exception',
                    'error': str(e)
                }
        
        time_range_results[metric] = metric_time_results
    
    return time_range_results

def test_basic_account_fields():
    """基本アカウントフィールド取得テスト（フォロワー数などの代替取得）"""
    
    print(f"\n" + "=" * 60)
    print("👤 基本アカウントフィールド取得テスト")
    print("=" * 60)
    
    account_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}"
    
    # daily_statsで必要な可能性があるフィールド
    account_fields_to_test = [
        'id', 'username', 'name', 'account_type',
        'media_count', 'followers_count', 'follows_count',
        'profile_picture_url', 'biography', 'website'
    ]
    
    print("基本アカウント情報で daily_stats 要件をカバーできるかテスト")
    
    field_test_results = {}
    
    # 個別フィールドテスト
    for field in account_fields_to_test:
        print(f"\n📝 フィールドテスト: {field}")
        
        try:
            params = {
                'fields': field,
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(account_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                value = data.get(field)
                
                print(f"   ✅ 取得成功: {value}")
                
                field_test_results[field] = {
                    'status': 'success',
                    'value': value,
                    'data_type': type(value).__name__,
                    'daily_stats_relevance': {
                        'followers_count': field == 'followers_count',
                        'following_count': field == 'follows_count',
                        'can_substitute_insights': field in ['followers_count', 'follows_count']
                    }
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"   ❌ エラー: {error_msg[:50]}...")
                
                field_test_results[field] = {
                    'status': 'error',
                    'error_message': error_msg
                }
                
        except Exception as e:
            print(f"   💥 例外: {str(e)[:50]}...")
            field_test_results[field] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # 複数フィールド同時取得テスト
    print(f"\n🔄 複数フィールド同時取得テスト")
    
    successful_fields = [
        field for field, result in field_test_results.items() 
        if result.get('status') == 'success'
    ]
    
    if successful_fields:
        try:
            params = {
                'fields': ','.join(successful_fields),
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(account_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 同時取得成功: {len(data)}フィールド")
                
                # daily_stats要件との対応関係
                daily_stats_mapping = {
                    'followers_count': data.get('followers_count'),
                    'following_count': data.get('follows_count')
                }
                
                print(f"   📊 daily_stats対応:")
                for db_field, value in daily_stats_mapping.items():
                    if value is not None:
                        print(f"     {db_field}: {value}")
                    else:
                        print(f"     {db_field}: データなし")
                
                field_test_results['combined_fetch'] = {
                    'status': 'success',
                    'all_fields': data,
                    'daily_stats_mapping': daily_stats_mapping
                }
            else:
                print(f"   ❌ 同時取得失敗: HTTP {response.status_code}")
                field_test_results['combined_fetch'] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            print(f"   💥 同時取得例外: {str(e)[:50]}...")
            field_test_results['combined_fetch'] = {
                'status': 'exception',
                'error': str(e)
            }
    
    return field_test_results

def generate_implementation_recommendations(requirement_results, time_range_results, field_results):
    """実装推奨事項の生成"""
    
    print(f"\n" + "=" * 60)
    print("🎯 daily_stats テーブル実装推奨事項")
    print("=" * 60)
    
    recommendations = {
        'implementation_feasibility': 'unknown',
        'required_fields_coverage': 0,
        'field_implementations': {},
        'alternative_approaches': [],
        'data_collection_strategy': {},
        'limitations': []
    }
    
    # 必須フィールドの実現可能性チェック
    required_fields = [
        name for name, info in requirement_results.items() 
        if info.get('required', False)
    ]
    
    implementable_required = [
        name for name in required_fields 
        if requirement_results[name].get('successful_api') or 
           (name == 'followers_count' and field_results.get('followers_count', {}).get('status') == 'success') or
           (name == 'following_count' and field_results.get('follows_count', {}).get('status') == 'success')
    ]
    
    coverage = len(implementable_required) / len(required_fields) if required_fields else 1
    recommendations['required_fields_coverage'] = coverage
    
    print(f"必須フィールドカバー率: {coverage*100:.1f}% ({len(implementable_required)}/{len(required_fields)})")
    
    # フィールド別実装方法
    for field_name, req_info in requirement_results.items():
        field_impl = {
            'db_column': req_info['db_column'],
            'required': req_info['required'],
            'implementation_method': 'none',
            'api_source': None,
            'fallback_options': []
        }
        
        # Insights APIで取得可能
        if req_info.get('successful_api'):
            field_impl['implementation_method'] = 'insights_api'
            field_impl['api_source'] = req_info['successful_api']
            print(f"✅ {field_name}: Insights API ({req_info['successful_api']})")
        
        # 基本フィールドで代替可能
        elif field_name == 'followers_count' and field_results.get('followers_count', {}).get('status') == 'success':
            field_impl['implementation_method'] = 'basic_field'
            field_impl['api_source'] = 'followers_count'
            field_impl['fallback_options'].append('basic_account_field')
            print(f"✅ {field_name}: 基本フィールド (followers_count)")
            
        elif field_name == 'following_count' and field_results.get('follows_count', {}).get('status') == 'success':
            field_impl['implementation_method'] = 'basic_field'
            field_impl['api_source'] = 'follows_count'
            field_impl['fallback_options'].append('basic_account_field')
            print(f"✅ {field_name}: 基本フィールド (follows_count)")
        
        # 取得不可
        else:
            field_impl['implementation_method'] = 'unavailable'
            if req_info['required']:
                print(f"❌ {field_name}: 取得不可（必須フィールド）")
            else:
                print(f"⚠️ {field_name}: 取得不可（オプション）")
        
        recommendations['field_implementations'][field_name] = field_impl
    
    # 実装可能性の総合評価
    if coverage >= 1.0:
        recommendations['implementation_feasibility'] = 'fully_feasible'
        print(f"\n🎉 実装可能性: 完全実現可能")
    elif coverage >= 0.8:
        recommendations['implementation_feasibility'] = 'mostly_feasible'
        print(f"\n✅ 実装可能性: ほぼ実現可能")
    elif coverage >= 0.5:
        recommendations['implementation_feasibility'] = 'partially_feasible'
        print(f"\n⚠️ 実装可能性: 部分的に実現可能")
    else:
        recommendations['implementation_feasibility'] = 'limited_feasible'
        print(f"\n❌ 実装可能性: 限定的")
    
    # データ収集戦略
    successful_insights = [
        name for name, info in requirement_results.items()
        if info.get('successful_api')
    ]
    
    if successful_insights:
        recommendations['data_collection_strategy']['insights_api'] = {
            'metrics': [requirement_results[name]['successful_api'] for name in successful_insights],
            'recommended_frequency': 'daily',
            'recommended_time': 'early_morning',
            'batch_size': len(successful_insights)
        }
    
    basic_field_available = any([
        field_results.get('followers_count', {}).get('status') == 'success',
        field_results.get('follows_count', {}).get('status') == 'success'
    ])
    
    if basic_field_available:
        recommendations['data_collection_strategy']['basic_fields'] = {
            'fields': ['followers_count', 'follows_count'],
            'recommended_frequency': 'daily',
            'can_substitute_insights': True
        }
    
    return recommendations

def save_daily_metrics_results(requirement_results, time_range_results, field_results, recommendations):
    """日別メトリクステスト結果を保存"""
    
    output_dir = "output-json"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 総合結果
    comprehensive_results = {
        'test_date': datetime.now().isoformat(),
        'instagram_user_id': INSTAGRAM_USER_ID,
        'daily_stats_requirements_test': requirement_results,
        'time_range_data_test': time_range_results,
        'basic_account_fields_test': field_results,
        'implementation_recommendations': recommendations,
        'summary': {
            'total_requirements_tested': len(requirement_results),
            'implementable_requirements': len([r for r in requirement_results.values() if r.get('successful_api') or r.get('requirement_name') in ['followers_count', 'following_count']]),
            'required_fields_coverage': recommendations.get('required_fields_coverage', 0),
            'implementation_feasibility': recommendations.get('implementation_feasibility', 'unknown')
        }
    }
    
    # メイン結果ファイル
    main_file = f"{output_dir}/03_daily_metrics_test_{timestamp}.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 日別メトリクステスト結果を保存: {main_file}")
    
    # 実装ガイド
    implementation_guide = {
        'test_date': datetime.now().isoformat(),
        'feasibility_assessment': recommendations.get('implementation_feasibility'),
        'required_coverage': recommendations.get('required_fields_coverage'),
        'implementation_methods': recommendations.get('field_implementations'),
        'data_collection_strategy': recommendations.get('data_collection_strategy'),
        'sql_suggestions': {
            'table_creation': 'Based on available fields, modify daily_stats table schema',
            'data_insertion': 'Use combination of Insights API and basic fields',
            'fallback_strategy': 'Implement graceful degradation for unavailable metrics'
        }
    }
    
    guide_file = f"{output_dir}/03_daily_stats_implementation_guide_{timestamp}.json"
    with open(guide_file, 'w', encoding='utf-8') as f:
        json.dump(implementation_guide, f, ensure_ascii=False, indent=2)
    
    print(f"💾 実装ガイドを保存: {guide_file}")
    
    return main_file, guide_file

def main():
    """メイン実行関数"""
    
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN]):
        print("❌ 環境変数が不足しています")
        exit(1)
    
    print("🚀 Instagram Daily Metrics 実取得テストを開始します...")
    
    try:
        # 1. daily_stats要件テスト
        print("\n" + "🎯" * 20)
        requirement_results = test_daily_stats_requirements()
        
        # 2. 時間範囲別データ取得テスト
        print("\n" + "🎯" * 20)
        time_range_results = test_time_range_data()
        
        # 3. 基本アカウントフィールドテスト
        print("\n" + "🎯" * 20)
        field_results = test_basic_account_fields()
        
        # 4. 実装推奨事項生成
        print("\n" + "🎯" * 20)
        recommendations = generate_implementation_recommendations(
            requirement_results, time_range_results, field_results
        )
        
        # 5. 結果保存
        print("\n" + "=" * 60)
        main_file, guide_file = save_daily_metrics_results(
            requirement_results, time_range_results, field_results, recommendations
        )
        
        # 6. 最終サマリー
        print("📋 Daily Metrics テスト結果サマリー")
        print("=" * 60)
        
        implementable = [
            name for name, info in requirement_results.items()
            if info.get('successful_api') or name in ['followers_count', 'following_count']
        ]
        
        required_implementable = [
            name for name, info in requirement_results.items()
            if info.get('required') and (info.get('successful_api') or name in ['followers_count', 'following_count'])
        ]
        
        required_total = len([
            name for name, info in requirement_results.items()
            if info.get('required')
        ])
        
        print(f"✅ 実装可能要件: {len(implementable)}/{len(requirement_results)}")
        print(f"✅ 必須要件カバー: {len(required_implementable)}/{required_total}")
        print(f"📊 実装可能性: {recommendations.get('implementation_feasibility', 'unknown')}")
        
        print(f"\n📋 実装可能フィールド:")
        for name in implementable:
            method = recommendations['field_implementations'][name]['implementation_method']
            api_source = recommendations['field_implementations'][name]['api_source']
            print(f"   ✅ {name}: {method} ({api_source})")
        
        print(f"\n" + "🎉" * 20)
        print("✅ Daily Metrics 実取得テスト完了!")
        print(f"📁 詳細結果: {main_file}")
        print(f"📁 実装ガイド: {guide_file}")
        print("🎉" * 20)
        
        return True
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)