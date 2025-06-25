#!/usr/bin/env python3
"""
Phase 4: レスポンス分析
APIの実際のレスポンス構造とフィールド値を詳細に確認
利用可能なメトリクス一覧や制約事項を調査
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

def analyze_media_endpoint():
    """/{ig-user-id}/mediaエンドポイントの詳細分析"""
    
    print("📊 Media エンドポイント分析:")
    print("-" * 30)
    
    url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    
    # 利用可能な全フィールドを試す
    all_fields = [
        'id', 'media_type', 'caption', 'media_url', 'thumbnail_url', 
        'timestamp', 'permalink', 'username', 'like_count', 'comments_count',
        'is_comment_enabled', 'shortcode', 'ig_id', 'owner'
    ]
    
    params = {
        'fields': ','.join(all_fields),
        'access_token': ACCESS_TOKEN,
        'limit': 3
    }
    
    try:
        response = requests.get(url, params=params)
        
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスヘッダー:")
        for key, value in response.headers.items():
            if key.lower() in ['x-app-usage', 'x-business-use-case-usage', 'content-type']:
                print(f"  {key}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ 取得成功:")
            print(f"取得件数: {len(data.get('data', []))}")
            
            # 各投稿の利用可能フィールドを確認
            posts = data.get('data', [])
            if posts:
                print(f"\n📝 利用可能フィールド (投稿1):")
                first_post = posts[0]
                for field in all_fields:
                    value = first_post.get(field)
                    status = "✅" if value is not None else "❌"
                    print(f"  {field}: {status} {type(value).__name__ if value is not None else 'None'}")
                
                # 実際の値のサンプル表示
                print(f"\n📋 フィールド値サンプル:")
                for field, value in first_post.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"  {field}: {value[:50]}...")
                    else:
                        print(f"  {field}: {value}")
            
            # ページネーション情報
            if 'paging' in data:
                paging = data['paging']
                print(f"\n🔄 ページネーション:")
                print(f"  次のページ: {'あり' if 'next' in paging else 'なし'}")
                print(f"  前のページ: {'あり' if 'previous' in paging else 'なし'}")
                if 'cursors' in paging:
                    print(f"  カーソル: {list(paging['cursors'].keys())}")
            
            return data
            
        else:
            print(f"❌ エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 例外エラー: {e}")
        return None

def analyze_insights_endpoint():
    """/{ig-media-id}/insightsエンドポイントの詳細分析"""
    
    print("\n📈 Insights エンドポイント分析:")
    print("-" * 30)
    
    # まず投稿IDを取得
    media_url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    media_params = {
        'fields': 'id,media_type',
        'access_token': ACCESS_TOKEN,
        'limit': 2
    }
    
    try:
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        posts = media_response.json().get('data', [])
        
        if not posts:
            print("❌ 投稿が見つかりません")
            return None
        
        # 利用可能な全メトリクスを試す
        all_metrics = [
            'likes', 'comments', 'saves', 'shares', 'views', 'reach', 'impressions',
            'engagement', 'total_interactions', 'profile_views', 'website_clicks',
            'follows', 'video_views', 'plays', 'story_exits', 'story_replies'
        ]
        
        results = {}
        
        for i, post in enumerate(posts):
            post_id = post.get('id')
            media_type = post.get('media_type')
            
            print(f"\n投稿 {i+1} (ID: {post_id}, Type: {media_type}):")
            
            insights_url = f"https://graph.facebook.com/{post_id}/insights"
            
            # 各メトリクスを個別にテスト
            available_metrics = []
            metric_values = {}
            
            for metric in all_metrics:
                try:
                    params = {
                        'metric': metric,
                        'access_token': ACCESS_TOKEN
                    }
                    
                    insights_response = requests.get(insights_url, params=params)
                    
                    if insights_response.status_code == 200:
                        insights_data = insights_response.json()
                        if insights_data.get('data'):
                            available_metrics.append(metric)
                            
                            # 値を取得
                            metric_data = insights_data['data'][0]
                            values = metric_data.get('values', [])
                            if values:
                                metric_values[metric] = values[0].get('value', 0)
                            
                    elif insights_response.status_code == 400:
                        # このメトリクスは利用不可
                        pass
                    else:
                        print(f"    ⚠️  {metric}: エラー {insights_response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ {metric}: 例外 {e}")
            
            print(f"  利用可能メトリクス ({len(available_metrics)}個):")
            for metric in available_metrics:
                value = metric_values.get(metric, 'N/A')
                print(f"    {metric}: {value}")
            
            print(f"  利用不可メトリクス:")
            unavailable = [m for m in all_metrics if m not in available_metrics]
            print(f"    {unavailable}")
            
            results[post_id] = {
                'media_type': media_type,
                'available_metrics': available_metrics,
                'metric_values': metric_values,
                'unavailable_metrics': unavailable
            }
        
        return results
        
    except Exception as e:
        print(f"❌ 例外エラー: {e}")
        return None

def analyze_rate_limits():
    """レート制限の状況を分析"""
    
    print("\n⚡ レート制限分析:")
    print("-" * 20)
    
    # 簡単なAPIコールでヘッダー情報を取得
    url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}"
    params = {
        'fields': 'id,username',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        
        # レート制限関連のヘッダーを確認
        rate_limit_headers = {}
        for header, value in response.headers.items():
            if 'usage' in header.lower() or 'limit' in header.lower():
                rate_limit_headers[header] = value
        
        print(f"レート制限関連ヘッダー:")
        if rate_limit_headers:
            for header, value in rate_limit_headers.items():
                print(f"  {header}: {value}")
                
                # x-app-usageの解析
                if header.lower() == 'x-app-usage':
                    try:
                        usage_data = json.loads(value)
                        print(f"    詳細:")
                        for key, val in usage_data.items():
                            print(f"      {key}: {val}")
                    except:
                        pass
        else:
            print("  レート制限ヘッダーが見つかりません")
        
        return rate_limit_headers
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def analyze_token_info():
    """アクセストークンの詳細情報を分析"""
    
    print("\n🔑 トークン情報分析:")
    print("-" * 20)
    
    # トークンの有効性確認
    url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}"
    params = {
        'fields': 'id,username,account_type,media_count',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ トークン有効:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ トークン無効: {response.status_code}")
            print(f"エラー: {response.text}")
        
        return data if response.status_code == 200 else None
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def response_analysis():
    """レスポンス分析のメイン関数"""
    
    print("=" * 50)
    print("Phase 4: レスポンス詳細分析")
    print("=" * 50)
    
    analysis_results = {}
    
    # 1. トークン情報確認
    token_info = analyze_token_info()
    analysis_results['token_info'] = token_info
    
    # 2. Media エンドポイント分析
    media_analysis = analyze_media_endpoint()
    analysis_results['media_analysis'] = media_analysis
    
    # 3. Insights エンドポイント分析
    insights_analysis = analyze_insights_endpoint()
    analysis_results['insights_analysis'] = insights_analysis
    
    # 4. レート制限分析
    rate_limit_info = analyze_rate_limits()
    analysis_results['rate_limit_info'] = rate_limit_info
    
    # 結果の保存
    output_file = 'api_response_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 詳細分析結果を {output_file} に保存しました")
    
    # サマリー作成
    print("\n📋 分析結果サマリー:")
    print("-" * 25)
    
    if token_info:
        print(f"✅ トークン有効 (ユーザー: {token_info.get('username', 'unknown')})")
    else:
        print("❌ トークン無効")
    
    if media_analysis:
        media_count = len(media_analysis.get('data', []))
        print(f"✅ メディア取得成功 ({media_count}件)")
    else:
        print("❌ メディア取得失敗")
    
    if insights_analysis:
        total_available_metrics = set()
        for post_data in insights_analysis.values():
            total_available_metrics.update(post_data.get('available_metrics', []))
        print(f"✅ メトリクス取得成功 (利用可能: {len(total_available_metrics)}種類)")
        print(f"   利用可能メトリクス: {list(total_available_metrics)}")
    else:
        print("❌ メトリクス取得失敗")
    
    return analysis_results

if __name__ == "__main__":
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN, USERNAME]):
        print("❌ 環境変数が不足しています。.envファイルを確認してください。")
        exit(1)
    
    results = response_analysis()
    
    if results:
        print("\n" + "=" * 50)
        print("Phase 4 完了: レスポンス詳細分析 ✅")
        print("=" * 50)
        print("全ての検証が完了しました。結果ファイルを確認してください。")
    else:
        print("\n" + "=" * 50)
        print("Phase 4 失敗: レスポンス詳細分析 ❌")
        print("=" * 50)