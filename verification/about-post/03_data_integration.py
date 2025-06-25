#!/usr/bin/env python3
"""
Phase 3: データ統合検証
投稿データとメトリクスを統合してDB構造に適合するかを検証
エンゲージメント率の計算やデータ型の適合性を確認
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def load_previous_data():
    """前のPhaseで保存されたデータを読み込み"""
    try:
        # 投稿データ読み込み
        with open('posts_table_sample.json', 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        
        # メトリクスデータ読み込み
        with open('post_metrics_table_sample.json', 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        return posts_data, metrics_data
        
    except FileNotFoundError as e:
        print(f"❌ 前のPhaseのデータファイルが見つかりません: {e}")
        print("先に 01_get_posts_data.py と 02_get_post_metrics.py を実行してください")
        return None, None

def validate_data_types(posts_data, metrics_data):
    """データ型の適合性を検証"""
    
    print("🔍 データ型検証:")
    print("-" * 20)
    
    validation_results = {
        'posts': {'valid': 0, 'invalid': 0, 'issues': []},
        'metrics': {'valid': 0, 'invalid': 0, 'issues': []}
    }
    
    # postsテーブルのデータ型検証
    posts_schema = {
        'instagram_post_id': str,
        'media_type': str,
        'caption': (str, type(None)),
        'media_url': (str, type(None)),
        'posted_at': str,
        'thumbnail_url': (str, type(None)),
        'permalink': (str, type(None))
    }
    
    print("📝 postsテーブルのデータ型検証:")
    for i, post in enumerate(posts_data):
        valid = True
        for field, expected_type in posts_schema.items():
            value = post.get(field)
            if isinstance(expected_type, tuple):
                # 複数の型を許可（例：str or None）
                if not isinstance(value, expected_type):
                    validation_results['posts']['issues'].append(
                        f"投稿{i+1}: {field} の型が不正 (期待: {expected_type}, 実際: {type(value)})"
                    )
                    valid = False
            else:
                # 単一の型のみ許可
                if not isinstance(value, expected_type):
                    validation_results['posts']['issues'].append(
                        f"投稿{i+1}: {field} の型が不正 (期待: {expected_type}, 実際: {type(value)})"
                    )
                    valid = False
        
        if valid:
            validation_results['posts']['valid'] += 1
        else:
            validation_results['posts']['invalid'] += 1
    
    print(f"  ✅ 有効: {validation_results['posts']['valid']}件")
    print(f"  ❌ 無効: {validation_results['posts']['invalid']}件")
    
    # post_metricsテーブルのデータ型検証
    metrics_schema = {
        'post_id': str,
        'likes': int,
        'comments': int,
        'saves': int,
        'shares': int,
        'views': int,
        'reach': int,
        'impressions': int,
        'engagement_rate': (int, float),
        'recorded_at': str
    }
    
    print("\n📊 post_metricsテーブルのデータ型検証:")
    for i, metric in enumerate(metrics_data):
        valid = True
        for field, expected_type in metrics_schema.items():
            value = metric.get(field)
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    validation_results['metrics']['issues'].append(
                        f"メトリクス{i+1}: {field} の型が不正 (期待: {expected_type}, 実際: {type(value)})"
                    )
                    valid = False
            else:
                if not isinstance(value, expected_type):
                    validation_results['metrics']['issues'].append(
                        f"メトリクス{i+1}: {field} の型が不正 (期待: {expected_type}, 実際: {type(value)})"
                    )
                    valid = False
        
        if valid:
            validation_results['metrics']['valid'] += 1
        else:
            validation_results['metrics']['invalid'] += 1
    
    print(f"  ✅ 有効: {validation_results['metrics']['valid']}件")
    print(f"  ❌ 無効: {validation_results['metrics']['invalid']}件")
    
    return validation_results

def calculate_engagement_rates(metrics_data):
    """エンゲージメント率の計算検証"""
    
    print("\n📈 エンゲージメント率計算検証:")
    print("-" * 30)
    
    calculation_results = []
    
    for i, metric in enumerate(metrics_data):
        likes = metric.get('likes', 0)
        comments = metric.get('comments', 0)
        saves = metric.get('saves', 0)
        shares = metric.get('shares', 0)
        reach = metric.get('reach', 0)
        
        # 手動計算
        if reach > 0:
            total_engagement = likes + comments + saves + shares
            calculated_rate = (total_engagement / reach) * 100
        else:
            calculated_rate = 0.0
        
        # APIから取得した値
        api_rate = metric.get('engagement_rate', 0)
        
        # 差異の確認（小数点以下の誤差を考慮）
        difference = abs(calculated_rate - api_rate)
        is_consistent = difference < 0.1  # 0.1%以内の誤差は許容
        
        result = {
            'post_index': i + 1,
            'post_id': metric.get('post_id'),
            'likes': likes,
            'comments': comments,
            'saves': saves,
            'shares': shares,
            'reach': reach,
            'total_engagement': likes + comments + saves + shares,
            'calculated_rate': round(calculated_rate, 2),
            'api_rate': api_rate,
            'difference': round(difference, 2),
            'is_consistent': is_consistent
        }
        
        calculation_results.append(result)
        
        print(f"投稿{i+1}:")
        print(f"  エンゲージメント: {result['total_engagement']} / リーチ: {reach}")
        print(f"  計算値: {result['calculated_rate']}%")
        print(f"  API値: {result['api_rate']}%")
        print(f"  差異: {result['difference']}% {'✅' if is_consistent else '❌'}")
    
    # 統計情報
    consistent_count = sum(1 for r in calculation_results if r['is_consistent'])
    total_count = len(calculation_results)
    consistency_rate = (consistent_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n一貫性: {consistent_count}/{total_count} ({consistency_rate:.1f}%)")
    
    return calculation_results

def create_integrated_dataset(posts_data, metrics_data):
    """投稿データとメトリクスを統合してフロントエンド用のデータセットを作成"""
    
    print("\n🔗 データ統合:")
    print("-" * 15)
    
    integrated_data = []
    
    # メトリクスデータをpost_idでインデックス化
    metrics_by_post_id = {metric['post_id']: metric for metric in metrics_data}
    
    for post in posts_data:
        post_id = post.get('instagram_post_id')
        metrics = metrics_by_post_id.get(post_id)
        
        if metrics:
            # フロントエンド用の統合データ
            integrated_item = {
                'id': post_id,
                'date': post.get('posted_at', '').split('T')[0] if post.get('posted_at') else '',
                'thumbnail': post.get('media_url', ''),
                'type': map_media_type(post.get('media_type')),
                'reach': metrics.get('reach', 0),
                'likes': metrics.get('likes', 0),
                'comments': metrics.get('comments', 0),
                'shares': metrics.get('shares', 0),
                'saves': metrics.get('saves', 0),
                'views': metrics.get('views', 0),
                'impressions': metrics.get('impressions', 0),
                'engagement_rate': metrics.get('engagement_rate', 0.0),
                'caption': post.get('caption', ''),
                'media_url': post.get('media_url', ''),
                'permalink': post.get('permalink', '')
            }
            
            integrated_data.append(integrated_item)
            
            print(f"✅ 統合成功: {post_id}")
        else:
            print(f"❌ メトリクス未取得: {post_id}")
    
    print(f"\n統合結果: {len(integrated_data)}/{len(posts_data)} 件")
    
    return integrated_data

def map_media_type(api_media_type):
    """APIのmedia_typeをフロントエンド用の形式にマッピング"""
    mapping = {
        'IMAGE': 'Feed',
        'VIDEO': 'Feed',  # ここはReelsかFeedかの判定が必要
        'CAROUSEL_ALBUM': 'Feed',
        'STORY': 'Story'
    }
    return mapping.get(api_media_type, 'Feed')

def data_integration_verification():
    """データ統合検証のメイン関数"""
    
    print("=" * 50)
    print("Phase 3: データ統合検証")
    print("=" * 50)
    
    # 前のPhaseのデータを読み込み
    posts_data, metrics_data = load_previous_data()
    if not posts_data or not metrics_data:
        return False
    
    print(f"📊 データ読み込み完了:")
    print(f"  投稿データ: {len(posts_data)}件")
    print(f"  メトリクスデータ: {len(metrics_data)}件")
    
    # データ型検証
    validation_results = validate_data_types(posts_data, metrics_data)
    
    # エンゲージメント率計算検証
    calculation_results = calculate_engagement_rates(metrics_data)
    
    # データ統合
    integrated_data = create_integrated_dataset(posts_data, metrics_data)
    
    # 結果の保存
    results = {
        'validation_results': validation_results,
        'calculation_results': calculation_results,
        'integrated_data': integrated_data,
        'summary': {
            'posts_count': len(posts_data),
            'metrics_count': len(metrics_data),
            'integrated_count': len(integrated_data),
            'data_integrity': len(integrated_data) / len(posts_data) * 100 if posts_data else 0
        }
    }
    
    output_file = 'data_integration_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 統合検証結果を {output_file} に保存しました")
    
    # フロントエンド用データの保存
    frontend_file = 'frontend_compatible_data.json'
    with open(frontend_file, 'w', encoding='utf-8') as f:
        json.dump(integrated_data, f, ensure_ascii=False, indent=2)
    
    print(f"🎨 フロントエンド用データを {frontend_file} に保存しました")
    
    # 検証結果のサマリー
    print("\n📋 統合検証結果サマリー:")
    print("-" * 25)
    print(f"投稿データ取得率: {len(posts_data)}/{len(posts_data)} (100%)")
    print(f"メトリクス取得率: {len(metrics_data)}/{len(posts_data)} ({len(metrics_data)/len(posts_data)*100:.1f}%)")
    print(f"データ統合率: {len(integrated_data)}/{len(posts_data)} ({results['summary']['data_integrity']:.1f}%)")
    
    validation_success = (
        validation_results['posts']['invalid'] == 0 and 
        validation_results['metrics']['invalid'] == 0
    )
    
    if validation_success and len(integrated_data) > 0:
        print("✅ 統合検証成功: DB構造とAPI データが適合しています")
        return True
    else:
        print("❌ 統合検証失敗: DB構造の見直しが必要です")
        return False

if __name__ == "__main__":
    success = data_integration_verification()
    
    if success:
        print("\n" + "=" * 50)
        print("Phase 3 完了: データ統合検証 ✅")
        print("=" * 50)
        print("次のステップ: 04_response_analysis.py を実行してください")
    else:
        print("\n" + "=" * 50)
        print("Phase 3 失敗: データ統合検証 ❌")
        print("=" * 50)