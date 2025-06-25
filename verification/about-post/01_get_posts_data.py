#!/usr/bin/env python3
"""
Phase 1: 投稿一覧取得検証
API エンドポイント: GET /{ig-user-id}/media
postsテーブルに必要なデータが取得できるかを検証
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

def get_posts_data():
    """投稿一覧データを取得してpostsテーブル用のデータ構造を検証"""
    
    print("=" * 50)
    print("Phase 1: 投稿一覧取得検証")
    print("=" * 50)
    print(f"Instagram User ID: {INSTAGRAM_USER_ID}")
    print(f"Username: {USERNAME}")
    print()
    
    # APIエンドポイント (Facebook Graph APIを使用)
    url = f"https://graph.facebook.com/{INSTAGRAM_USER_ID}/media"
    
    # postsテーブルに必要なフィールド
    fields = [
        'id',           # instagram_post_id
        'media_type',   # media_type
        'caption',      # caption
        'media_url',    # media_url
        'thumbnail_url', # サムネイル（動画用）
        'timestamp',    # posted_at
        'permalink'     # 投稿URL
    ]
    
    params = {
        'fields': ','.join(fields),
        'access_token': ACCESS_TOKEN,
        'limit': 10  # テスト用に10件に制限
    }
    
    try:
        print("🔄 APIリクエスト送信中...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print("✅ APIリクエスト成功!")
        print(f"取得件数: {len(data.get('data', []))}")
        print()
        
        # レスポンス構造の確認
        print("📊 レスポンス構造:")
        print(f"- data: {type(data.get('data'))} (投稿配列)")
        if 'paging' in data:
            print(f"- paging: {type(data.get('paging'))} (ページネーション情報)")
        print()
        
        # 各投稿データの詳細確認
        posts = data.get('data', [])
        
        print("📝 postsテーブル用データ検証:")
        print("-" * 40)
        
        for i, post in enumerate(posts[:3]):  # 最初の3件を詳細表示
            print(f"\n投稿 {i+1}:")
            
            # postsテーブルの各フィールドを確認
            instagram_post_id = post.get('id')
            media_type = post.get('media_type')
            caption = post.get('caption', '')
            media_url = post.get('media_url')
            thumbnail_url = post.get('thumbnail_url')
            timestamp = post.get('timestamp')
            permalink = post.get('permalink')
            
            print(f"  instagram_post_id: {instagram_post_id}")
            print(f"  media_type: {media_type}")
            print(f"  caption: {caption[:50]}..." if caption else "  caption: None")
            print(f"  media_url: {media_url[:50]}..." if media_url else "  media_url: None")
            print(f"  thumbnail_url: {thumbnail_url[:50]}..." if thumbnail_url else "  thumbnail_url: None")
            print(f"  timestamp: {timestamp}")
            print(f"  permalink: {permalink}")
            
            # posted_atの変換テスト
            if timestamp:
                try:
                    posted_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    print(f"  posted_at (変換後): {posted_at}")
                except Exception as e:
                    print(f"  posted_at 変換エラー: {e}")
        
        # データ品質チェック
        print("\n🔍 データ品質チェック:")
        print("-" * 30)
        
        required_fields = ['id', 'media_type', 'timestamp']
        missing_data = []
        
        for post in posts:
            for field in required_fields:
                if field not in post or post[field] is None:
                    missing_data.append(f"投稿ID {post.get('id', 'unknown')}: {field}が欠損")
        
        if missing_data:
            print("❌ 必須フィールドの欠損:")
            for issue in missing_data[:5]:  # 最初の5件のみ表示
                print(f"  - {issue}")
        else:
            print("✅ 必須フィールドは全て存在")
        
        # media_type の分布確認
        media_types = {}
        for post in posts:
            media_type = post.get('media_type', 'UNKNOWN')
            media_types[media_type] = media_types.get(media_type, 0) + 1
        
        print(f"\n📊 メディアタイプ分布:")
        for media_type, count in media_types.items():
            print(f"  - {media_type}: {count}件")
        
        # 結果の保存
        output_file = 'posts_data_verification.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 結果を {output_file} に保存しました")
        
        # postsテーブル用のサンプルデータ生成
        posts_table_data = []
        for post in posts:
            post_data = {
                'instagram_post_id': post.get('id'),
                'media_type': post.get('media_type'),
                'caption': post.get('caption'),
                'media_url': post.get('media_url'),
                'posted_at': post.get('timestamp'),
                'thumbnail_url': post.get('thumbnail_url'),
                'permalink': post.get('permalink')
            }
            posts_table_data.append(post_data)
        
        # サンプルデータ保存
        sample_file = 'posts_table_sample.json'
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(posts_table_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 postsテーブル用サンプルデータを {sample_file} に保存しました")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ APIリクエストエラー: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"レスポンスコード: {e.response.status_code}")
            print(f"レスポンス内容: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

if __name__ == "__main__":
    if not all([INSTAGRAM_USER_ID, ACCESS_TOKEN, USERNAME]):
        print("❌ 環境変数が不足しています。.envファイルを確認してください。")
        exit(1)
    
    result = get_posts_data()
    
    if result:
        print("\n" + "=" * 50)
        print("Phase 1 完了: 投稿一覧取得検証 ✅")
        print("=" * 50)
        print("次のステップ: 02_get_post_metrics.py を実行してください")
    else:
        print("\n" + "=" * 50)
        print("Phase 1 失敗: 投稿一覧取得検証 ❌")
        print("=" * 50)