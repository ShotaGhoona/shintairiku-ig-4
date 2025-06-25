#!/usr/bin/env python3
"""
Instagram Graph API 取得可能データ完全網羅調査
DB構造に拘らず、実際に取得可能な全てのデータを詳細にリストアップ
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def get_all_available_insights_metrics():
    """利用可能な全Insightsメトリクスを体系的に調査"""
    
    print("🔍 Instagram Insights API 全利用可能メトリクス調査")
    print("=" * 60)
    
    insights_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/insights"
    
    # エラーメッセージから取得した実際に利用可能なメトリクス一覧
    # (前回の検証で得られたエラーメッセージより)
    confirmed_available_metrics = [
        'impressions',           # v22以降廃止だが一覧には含まれている
        'reach',                 # ✅ 利用可能確認済み
        'follower_count',        # ✅ 利用可能確認済み
        'website_clicks',        # パラメータ指定が必要
        'profile_views',         # パラメータ指定が必要
        'online_followers',      # 期間指定に制限あり
        'accounts_engaged',      # パラメータ指定が必要
        'total_interactions',    # パラメータ指定が必要
        'likes',                 # パラメータ指定が必要
        'comments',              # パラメータ指定が必要
        'shares',                # パラメータ指定が必要
        'saves',                 # パラメータ指定が必要
        'replies',               # 新メトリクス
        'engaged_audience_demographics',    # デモグラフィック系
        'reached_audience_demographics',    # デモグラフィック系
        'follower_demographics',           # デモグラフィック系
        'follows_and_unfollows',           # フォロー関連
        'profile_links_taps',              # プロフィールリンク
        'views',                           # 視聴関連
        'threads_likes',                   # Threads関連
        'threads_replies',                 # Threads関連
        'reposts',                         # Threads関連
        'quotes',                          # Threads関連
        'threads_followers',               # Threads関連
        'threads_follower_demographics',   # Threads関連
        'content_views',                   # コンテンツ関連
        'threads_views'                    # Threads関連
    ]
    
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    # 期間設定のテストパターン
    period_tests = [
        {
            'name': 'day_period',
            'params': {
                'since': yesterday,
                'until': today_str,
                'period': 'day'
            }
        },
        {
            'name': 'lifetime_no_period',
            'params': {
                # lifetime の場合は period パラメータ不要
            }
        },
        {
            'name': 'week_period',
            'params': {
                'since': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
                'until': today_str,
                'period': 'week'
            }
        }
    ]
    
    # metric_type の追加テスト
    metric_type_tests = ['total_value', 'daily_value']
    
    comprehensive_results = {}
    
    for metric in confirmed_available_metrics:
        print(f"\n📊 詳細調査: {metric}")
        
        metric_results = {
            'metric_name': metric,
            'available_configurations': [],
            'successful_calls': 0,
            'best_configuration': None,
            'sample_data': None,
            'data_characteristics': {},
            'period_compatibility': {},
            'metric_type_compatibility': {}
        }
        
        # 基本的な期間テスト
        for period_test in period_tests:
            period_name = period_test['name']
            base_params = period_test['params'].copy()
            
            print(f"   🗓️  期間テスト: {period_name}")
            
            # 基本パラメータでテスト
            try:
                params = {
                    'metric': metric,
                    'access_token': ACCESS_TOKEN,
                    **base_params
                }
                
                response = requests.get(insights_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and len(data['data']) > 0:
                        metric_data = data['data'][0]
                        values = metric_data.get('values', [])
                        
                        if values:
                            config_key = f"{period_name}_basic"
                            success_info = {
                                'configuration': config_key,
                                'period_type': period_name,
                                'metric_type': 'default',
                                'params': params,
                                'data_points': len(values),
                                'sample_value': values[0].get('value'),
                                'sample_end_time': values[0].get('end_time'),
                                'metric_info': {
                                    'name': metric_data.get('name'),
                                    'title': metric_data.get('title'),
                                    'description': metric_data.get('description'),
                                    'period': metric_data.get('period')
                                }
                            }
                            
                            metric_results['available_configurations'].append(success_info)
                            metric_results['successful_calls'] += 1
                            metric_results['period_compatibility'][period_name] = True
                            
                            if not metric_results['best_configuration']:
                                metric_results['best_configuration'] = config_key
                                metric_results['sample_data'] = success_info
                            
                            print(f"     ✅ 成功: {len(values)}件のデータ, サンプル値: {values[0].get('value')}")
                        else:
                            print(f"     ⚪ データなし")
                            metric_results['period_compatibility'][period_name] = 'no_data'
                    else:
                        print(f"     ⚪ 空レスポンス")
                        metric_results['period_compatibility'][period_name] = 'empty'
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '')
                    
                    # metric_type パラメータが必要かチェック
                    if 'metric_type=total_value' in error_msg:
                        print(f"     🔄 metric_type必要: total_value を試行")
                        
                        # metric_type を追加してリトライ
                        for metric_type in metric_type_tests:
                            try:
                                retry_params = params.copy()
                                retry_params['metric_type'] = metric_type
                                
                                retry_response = requests.get(insights_url, params=retry_params)
                                
                                if retry_response.status_code == 200:
                                    retry_data = retry_response.json()
                                    if retry_data.get('data') and len(retry_data['data']) > 0:
                                        retry_metric_data = retry_data['data'][0]
                                        retry_values = retry_metric_data.get('values', [])
                                        
                                        if retry_values:
                                            config_key = f"{period_name}_{metric_type}"
                                            success_info = {
                                                'configuration': config_key,
                                                'period_type': period_name,
                                                'metric_type': metric_type,
                                                'params': retry_params,
                                                'data_points': len(retry_values),
                                                'sample_value': retry_values[0].get('value'),
                                                'sample_end_time': retry_values[0].get('end_time'),
                                                'metric_info': {
                                                    'name': retry_metric_data.get('name'),
                                                    'title': retry_metric_data.get('title'),
                                                    'description': retry_metric_data.get('description'),
                                                    'period': retry_metric_data.get('period')
                                                }
                                            }
                                            
                                            metric_results['available_configurations'].append(success_info)
                                            metric_results['successful_calls'] += 1
                                            metric_results['period_compatibility'][period_name] = True
                                            metric_results['metric_type_compatibility'][metric_type] = True
                                            
                                            if not metric_results['best_configuration']:
                                                metric_results['best_configuration'] = config_key
                                                metric_results['sample_data'] = success_info
                                            
                                            print(f"     ✅ 成功 ({metric_type}): {len(retry_values)}件, 値: {retry_values[0].get('value')}")
                                            break
                                        else:
                                            print(f"     ⚪ データなし ({metric_type})")
                                
                            except Exception as e:
                                print(f"     💥 例外 ({metric_type}): {str(e)[:30]}...")
                    
                    elif 'incompatible' in error_msg.lower():
                        print(f"     ❌ 期間非対応: {error_msg[:50]}...")
                        metric_results['period_compatibility'][period_name] = 'incompatible'
                    else:
                        print(f"     ❌ エラー: {error_msg[:50]}...")
                        metric_results['period_compatibility'][period_name] = 'error'
                else:
                    print(f"     ❓ HTTP {response.status_code}")
                    metric_results['period_compatibility'][period_name] = f'http_{response.status_code}'
                    
            except Exception as e:
                print(f"     💥 例外: {str(e)[:50]}...")
                metric_results['period_compatibility'][period_name] = 'exception'
        
        # データ特性分析
        if metric_results['available_configurations']:
            print(f"   📈 データ特性分析")
            
            # 最も多くのデータポイントを持つ設定を選択
            best_config = max(
                metric_results['available_configurations'],
                key=lambda x: x.get('data_points', 0)
            )
            
            metric_results['data_characteristics'] = {
                'max_data_points': best_config.get('data_points', 0),
                'value_type': type(best_config.get('sample_value')).__name__,
                'has_time_series': best_config.get('data_points', 0) > 1,
                'requires_metric_type': any(
                    config.get('metric_type') != 'default' 
                    for config in metric_results['available_configurations']
                ),
                'supported_periods': [
                    period for period, status in metric_results['period_compatibility'].items()
                    if status is True
                ]
            }
            
            print(f"     最大データポイント: {metric_results['data_characteristics']['max_data_points']}")
            print(f"     値の型: {metric_results['data_characteristics']['value_type']}")
            print(f"     時系列データ: {metric_results['data_characteristics']['has_time_series']}")
            print(f"     metric_type必要: {metric_results['data_characteristics']['requires_metric_type']}")
        
        comprehensive_results[metric] = metric_results
        
        # メトリクス全体の可用性表示
        if metric_results['successful_calls'] > 0:
            print(f"   🎯 {metric}: {metric_results['successful_calls']}通りの設定で利用可能")
        else:
            print(f"   ❌ {metric}: 全設定で利用不可")
    
    return comprehensive_results

def get_all_basic_account_fields():
    """基本アカウントフィールドの完全調査"""
    
    print(f"\n" + "=" * 60)
    print("👤 基本アカウントフィールド完全調査")
    print("=" * 60)
    
    account_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}"
    
    # Instagram Graph API ドキュメントベースの可能性があるフィールド
    potential_fields = [
        # 基本情報
        'id', 'username', 'name', 'biography', 'website',
        'profile_picture_url', 'account_type',
        
        # カウント系
        'media_count', 'followers_count', 'follows_count',
        
        # ビジネス情報
        'business_discovery', 'category', 'contact_info',
        
        # ショッピング
        'shopping_product_tag_eligibility', 'shopping_review_status',
        
        # その他
        'ig_id', 'is_private', 'is_published'
    ]
    
    field_results = {}
    
    print("基本アカウントフィールドの個別調査:")
    
    # 個別フィールドテスト
    for field in potential_fields:
        print(f"\n📝 フィールド調査: {field}")
        
        try:
            params = {
                'fields': field,
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(account_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                value = data.get(field)
                
                print(f"   ✅ 取得成功")
                print(f"   データ型: {type(value).__name__}")
                print(f"   値: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                
                field_results[field] = {
                    'status': 'success',
                    'value': value,
                    'data_type': type(value).__name__,
                    'value_length': len(str(value)) if value else 0,
                    'is_useful_for_daily_stats': field in [
                        'followers_count', 'follows_count', 'media_count', 
                        'username', 'name', 'account_type'
                    ]
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"   ❌ エラー: {error_msg[:50]}...")
                
                field_results[field] = {
                    'status': 'error',
                    'error_message': error_msg,
                    'error_code': error_data.get('error', {}).get('code')
                }
                
        except Exception as e:
            print(f"   💥 例外: {str(e)[:50]}...")
            field_results[field] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # 成功したフィールドの一括取得テスト
    successful_fields = [
        field for field, result in field_results.items() 
        if result.get('status') == 'success'
    ]
    
    print(f"\n🔄 一括取得テスト ({len(successful_fields)}フィールド)")
    
    if successful_fields:
        try:
            params = {
                'fields': ','.join(successful_fields),
                'access_token': ACCESS_TOKEN
            }
            
            response = requests.get(account_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 一括取得成功: {len(data)}フィールド")
                
                field_results['batch_fetch'] = {
                    'status': 'success',
                    'fields_count': len(data),
                    'all_data': data
                }
            else:
                print(f"   ❌ 一括取得失敗: HTTP {response.status_code}")
                field_results['batch_fetch'] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
        except Exception as e:
            print(f"   💥 一括取得例外: {str(e)[:50]}...")
            field_results['batch_fetch'] = {
                'status': 'exception',
                'error': str(e)
            }
    
    return field_results

def analyze_post_data_aggregation():
    """投稿データの集約による日別統計の可能性調査"""
    
    print(f"\n" + "=" * 60)
    print("📊 投稿データ集約による日別統計分析")
    print("=" * 60)
    
    media_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    
    # 投稿データから集約可能なメトリクス
    print("投稿データから日別統計へ集約可能な要素:")
    
    try:
        # 最近の投稿を取得
        params = {
            'fields': 'id,timestamp,media_type,like_count,comments_count',
            'access_token': ACCESS_TOKEN,
            'limit': 50  # 過去50件の投稿
        }
        
        response = requests.get(media_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            
            print(f"   📋 取得投稿数: {len(posts)}")
            
            if posts:
                # 日別集約分析
                daily_aggregation = {}
                
                for post in posts:
                    timestamp = post.get('timestamp', '')
                    if timestamp:
                        # 日付のみ抽出 (YYYY-MM-DD)
                        post_date = timestamp.split('T')[0]
                        
                        if post_date not in daily_aggregation:
                            daily_aggregation[post_date] = {
                                'posts_count': 0,
                                'total_likes': 0,
                                'total_comments': 0,
                                'media_types': set()
                            }
                        
                        daily_aggregation[post_date]['posts_count'] += 1
                        daily_aggregation[post_date]['total_likes'] += post.get('like_count', 0)
                        daily_aggregation[post_date]['total_comments'] += post.get('comments_count', 0)
                        daily_aggregation[post_date]['media_types'].add(post.get('media_type', 'unknown'))
                
                print(f"\n   📈 日別集約結果 (最近{len(daily_aggregation)}日分):")
                
                aggregation_results = {}
                
                for date, stats in sorted(daily_aggregation.items(), reverse=True)[:7]:  # 最新7日分表示
                    media_types_list = list(stats['media_types'])
                    print(f"     📅 {date}:")
                    print(f"       投稿数: {stats['posts_count']}")
                    print(f"       いいね合計: {stats['total_likes']}")
                    print(f"       コメント合計: {stats['total_comments']}")
                    print(f"       メディアタイプ: {', '.join(media_types_list)}")
                    
                    aggregation_results[date] = {
                        'posts_count': stats['posts_count'],
                        'total_likes': stats['total_likes'],
                        'total_comments': stats['total_comments'],
                        'media_types': media_types_list,
                        'avg_likes_per_post': stats['total_likes'] / stats['posts_count'] if stats['posts_count'] > 0 else 0,
                        'avg_comments_per_post': stats['total_comments'] / stats['posts_count'] if stats['posts_count'] > 0 else 0
                    }
                
                # 集約の可能性評価
                potential_daily_metrics = {
                    'daily_posts_count': '日別投稿数',
                    'daily_total_likes': '日別いいね合計',
                    'daily_total_comments': '日別コメント合計',
                    'daily_avg_likes_per_post': '日別投稿あたり平均いいね数',
                    'daily_avg_comments_per_post': '日別投稿あたり平均コメント数',
                    'daily_media_type_distribution': '日別メディアタイプ分布'
                }
                
                print(f"\n   🎯 投稿集約で作成可能な日別メトリクス:")
                for metric_key, description in potential_daily_metrics.items():
                    print(f"     ✅ {metric_key}: {description}")
                
                return {
                    'status': 'success',
                    'daily_aggregation_sample': aggregation_results,
                    'potential_metrics': potential_daily_metrics,
                    'data_availability': {
                        'posts_analyzed': len(posts),
                        'date_range_days': len(daily_aggregation),
                        'can_create_time_series': len(daily_aggregation) > 1
                    }
                }
            else:
                print("   ❌ 投稿データなし")
                return {'status': 'no_posts'}
        else:
            print(f"   ❌ 投稿取得失敗: HTTP {response.status_code}")
            return {'status': 'error', 'status_code': response.status_code}
            
    except Exception as e:
        print(f"   💥 例外: {str(e)}")
        return {'status': 'exception', 'error': str(e)}

def generate_comprehensive_summary(insights_results, fields_results, aggregation_results):
    """包括的な利用可能データサマリー生成"""
    
    print(f"\n" + "=" * 60)
    print("📋 取得可能データ完全サマリー")
    print("=" * 60)
    
    # Insights API サマリー
    available_insights = [
        metric for metric, result in insights_results.items()
        if result.get('successful_calls', 0) > 0
    ]
    
    insights_by_category = {
        'フォロワー関連': ['follower_count', 'follows_and_unfollows', 'follower_demographics'],
        'エンゲージメント関連': ['likes', 'comments', 'shares', 'saves', 'total_interactions'],
        'リーチ・視聴関連': ['reach', 'views', 'content_views'],
        'プロフィール活動': ['profile_views', 'website_clicks', 'profile_links_taps'],
        'デモグラフィック': ['engaged_audience_demographics', 'reached_audience_demographics'],
        'Threads関連': ['threads_likes', 'threads_replies', 'threads_followers', 'threads_views'],
        'その他': ['online_followers', 'replies', 'reposts', 'quotes']
    }
    
    print("🎯 Instagram Insights API 利用可能メトリクス:")
    
    total_available_insights = 0
    categorized_available = {}
    
    for category, metrics in insights_by_category.items():
        available_in_category = [m for m in metrics if m in available_insights]
        if available_in_category:
            print(f"\n   📊 {category} ({len(available_in_category)}個):")
            categorized_available[category] = []
            
            for metric in available_in_category:
                result = insights_results[metric]
                best_config = result.get('best_configuration', 'N/A')
                data_points = result.get('data_characteristics', {}).get('max_data_points', 0)
                requires_metric_type = result.get('data_characteristics', {}).get('requires_metric_type', False)
                
                config_note = f"({best_config}"
                if requires_metric_type:
                    config_note += ", metric_type必要"
                config_note += ")"
                
                print(f"     ✅ {metric}: {data_points}pts {config_note}")
                
                categorized_available[category].append({
                    'metric': metric,
                    'max_data_points': data_points,
                    'best_configuration': best_config,
                    'requires_metric_type': requires_metric_type,
                    'configurations_count': result.get('successful_calls', 0)
                })
                
                total_available_insights += 1
    
    # 基本フィールドサマリー
    available_fields = [
        field for field, result in fields_results.items()
        if result.get('status') == 'success' and field != 'batch_fetch'
    ]
    
    print(f"\n🏷️  基本アカウントフィールド ({len(available_fields)}個):")
    
    field_categories = {
        '識別情報': ['id', 'username', 'name', 'ig_id'],
        '数値データ': ['media_count', 'followers_count', 'follows_count'],
        'プロフィール情報': ['biography', 'website', 'profile_picture_url'],
        'ビジネス情報': ['account_type', 'category', 'contact_info'],
        'その他': []
    }
    
    for field in available_fields:
        categorized = False
        for category, category_fields in field_categories.items():
            if field in category_fields:
                categorized = True
                break
        if not categorized:
            field_categories['その他'].append(field)
    
    for category, fields in field_categories.items():
        category_available = [f for f in fields if f in available_fields]
        if category_available:
            print(f"   📝 {category}: {', '.join(category_available)}")
    
    # 投稿集約サマリー
    if aggregation_results.get('status') == 'success':
        potential_metrics = aggregation_results.get('potential_metrics', {})
        data_info = aggregation_results.get('data_availability', {})
        
        print(f"\n📈 投稿データ集約による日別メトリクス ({len(potential_metrics)}個):")
        print(f"   📋 分析可能投稿数: {data_info.get('posts_analyzed', 0)}")
        print(f"   📅 日付範囲: {data_info.get('date_range_days', 0)}日分")
        print(f"   🔄 時系列作成可能: {'Yes' if data_info.get('can_create_time_series') else 'No'}")
        
        for metric_key, description in potential_metrics.items():
            print(f"   ✅ {metric_key}: {description}")
    
    # 総合評価
    print(f"\n" + "🎉" * 20)
    print("📊 取得可能データ総合評価")
    print("🎉" * 20)
    
    print(f"✅ Insights API メトリクス: {total_available_insights}個")
    print(f"✅ 基本アカウントフィールド: {len(available_fields)}個")
    
    if aggregation_results.get('status') == 'success':
        aggregation_metrics_count = len(aggregation_results.get('potential_metrics', {}))
        print(f"✅ 投稿集約メトリクス: {aggregation_metrics_count}個")
        total_metrics = total_available_insights + len(available_fields) + aggregation_metrics_count
    else:
        print(f"❌ 投稿集約メトリクス: 利用不可")
        total_metrics = total_available_insights + len(available_fields)
    
    print(f"🎯 合計利用可能データ要素: {total_metrics}個")
    
    # 実装推奨事項
    print(f"\n💡 実装推奨事項:")
    print(f"   🔄 日次データ収集に最適: {len([m for m in available_insights if 'follower_count' in m or 'reach' in m])}個のメトリクス")
    print(f"   📊 ダッシュボード表示可能: 全{total_metrics}要素")
    print(f"   📈 時系列分析可能: Insights API + 投稿集約")
    
    return {
        'insights_metrics': categorized_available,
        'basic_fields': available_fields,
        'aggregation_metrics': aggregation_results.get('potential_metrics', {}),
        'total_available_elements': total_metrics,
        'implementation_readiness': 'high' if total_metrics > 20 else 'medium' if total_metrics > 10 else 'low'
    }

def save_comprehensive_results(insights_results, fields_results, aggregation_results, summary):
    """包括的結果を保存"""
    
    output_dir = "output-json"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 包括的結果
    comprehensive_data = {
        'analysis_date': datetime.now().isoformat(),
        'instagram_user_id': INSTAGRAM_USER_ID,
        'insights_api_analysis': insights_results,
        'basic_fields_analysis': fields_results,
        'post_aggregation_analysis': aggregation_results,
        'comprehensive_summary': summary,
        'metadata': {
            'total_insights_tested': len(insights_results),
            'available_insights': len([r for r in insights_results.values() if r.get('successful_calls', 0) > 0]),
            'total_fields_tested': len([f for f in fields_results.keys() if f != 'batch_fetch']),
            'available_fields': len([r for r in fields_results.values() if r.get('status') == 'success' and isinstance(r, dict)]),
            'aggregation_feasible': aggregation_results.get('status') == 'success'
        }
    }
    
    # メインファイル
    main_file = f"{output_dir}/04_comprehensive_available_data_{timestamp}.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 包括的分析結果を保存: {main_file}")
    
    # 実装ガイド専用ファイル
    implementation_guide = {
        'analysis_date': datetime.now().isoformat(),
        'available_data_elements': summary['total_available_elements'],
        'implementation_readiness': summary['implementation_readiness'],
        'recommended_daily_collection': {
            'insights_api': [
                metric for metric in insights_results.keys()
                if insights_results[metric].get('successful_calls', 0) > 0 and
                   any(period in insights_results[metric].get('period_compatibility', {})
                       for period in ['day_period'])
            ],
            'basic_fields': [
                field for field in fields_results.keys()
                if fields_results[field].get('status') == 'success' and field != 'batch_fetch' and
                   fields_results[field].get('is_useful_for_daily_stats', False)
            ],
            'post_aggregation': list(aggregation_results.get('potential_metrics', {}).keys()) if aggregation_results.get('status') == 'success' else []
        },
        'api_call_strategy': {
            'insights_frequency': 'daily',
            'basic_fields_frequency': 'daily',
            'post_aggregation_frequency': 'daily',
            'recommended_collection_time': 'early_morning_jst'
        }
    }
    
    guide_file = f"{output_dir}/04_implementation_ready_data_guide_{timestamp}.json"
    with open(guide_file, 'w', encoding='utf-8') as f:
        json.dump(implementation_guide, f, ensure_ascii=False, indent=2)
    
    print(f"💾 実装ガイドを保存: {guide_file}")
    
    return main_file, guide_file

def main():
    """メイン実行関数"""
    
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN]):
        print("❌ 環境変数が不足しています")
        exit(1)
    
    print("🚀 Instagram API 取得可能データ完全調査を開始します...")
    print("📋 DB構造に拘らず、実際に取得可能な全データを網羅的に調査")
    
    try:
        # 1. Insights API 全メトリクス調査
        print("\n" + "🎯" * 20)
        insights_results = get_all_available_insights_metrics()
        
        # 2. 基本アカウントフィールド完全調査
        print("\n" + "🎯" * 20)
        fields_results = get_all_basic_account_fields()
        
        # 3. 投稿データ集約分析
        print("\n" + "🎯" * 20)
        aggregation_results = analyze_post_data_aggregation()
        
        # 4. 包括的サマリー生成
        print("\n" + "🎯" * 20)
        summary = generate_comprehensive_summary(insights_results, fields_results, aggregation_results)
        
        # 5. 結果保存
        print("\n" + "=" * 60)
        main_file, guide_file = save_comprehensive_results(
            insights_results, fields_results, aggregation_results, summary
        )
        
        print(f"\n" + "🎉" * 30)
        print("✅ Instagram API 取得可能データ完全調査完了!")
        print(f"📁 詳細結果: {main_file}")
        print(f"📁 実装ガイド: {guide_file}")
        print("📊 これで実際に取得可能な全データが判明しました！")
        print("🎉" * 30)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 調査中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)