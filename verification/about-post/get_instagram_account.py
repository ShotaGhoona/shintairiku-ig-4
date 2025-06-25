#!/usr/bin/env python3
"""
Facebookページトークンから正しいInstagram Business Account情報を取得
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def get_instagram_accounts():
    """Facebookページに関連付けられたInstagramアカウントを取得"""
    
    print("🔍 Instagram Business Account 情報取得")
    print("=" * 50)
    
    # まずFacebookページ情報を取得
    print("📄 Facebookページ情報取得中...")
    
    # Facebookページの基本情報
    page_url = "https://graph.facebook.com/me"
    page_params = {
        'fields': 'id,name,instagram_business_account',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(page_url, params=page_params)
        
        if response.status_code == 200:
            page_data = response.json()
            print(f"✅ Facebookページ情報:")
            print(f"  ページID: {page_data.get('id')}")
            print(f"  ページ名: {page_data.get('name')}")
            
            # Instagram Business Accountの確認
            instagram_account = page_data.get('instagram_business_account')
            if instagram_account:
                ig_account_id = instagram_account.get('id')
                print(f"  Instagram Business Account ID: {ig_account_id}")
                
                # Instagram Business Account の詳細情報を取得
                print(f"\n📱 Instagram Business Account 詳細取得中...")
                
                ig_url = f"https://graph.facebook.com/{ig_account_id}"
                ig_params = {
                    'fields': 'id,username,name,profile_picture_url,followers_count,media_count,website',
                    'access_token': ACCESS_TOKEN
                }
                
                ig_response = requests.get(ig_url, params=ig_params)
                
                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    print(f"✅ Instagram Account 詳細:")
                    print(f"  ID: {ig_data.get('id')}")
                    print(f"  ユーザー名: {ig_data.get('username')}")
                    print(f"  表示名: {ig_data.get('name')}")
                    print(f"  フォロワー数: {ig_data.get('followers_count')}")
                    print(f"  投稿数: {ig_data.get('media_count')}")
                    print(f"  プロフィール画像: {ig_data.get('profile_picture_url')}")
                    
                    # Instagram APIでメディア取得テスト
                    print(f"\n🧪 Instagram API テスト...")
                    test_instagram_api(ig_account_id)
                    
                    return {
                        'facebook_page_id': page_data.get('id'),
                        'facebook_page_name': page_data.get('name'),
                        'instagram_account_id': ig_data.get('id'),
                        'instagram_username': ig_data.get('username'),
                        'instagram_name': ig_data.get('name'),
                        'profile_picture_url': ig_data.get('profile_picture_url'),
                        'followers_count': ig_data.get('followers_count'),
                        'media_count': ig_data.get('media_count')
                    }
                else:
                    print(f"❌ Instagram Account 詳細取得失敗: {ig_response.status_code}")
                    print(f"エラー: {ig_response.text}")
            else:
                print("❌ Instagram Business Account が見つかりません")
                print("Facebookページに Instagram Business Account を関連付けてください")
        else:
            print(f"❌ Facebookページ情報取得失敗: {response.status_code}")
            print(f"エラー: {response.text}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    return None

def test_instagram_api(instagram_account_id):
    """取得したInstagram Account IDでAPI動作テスト"""
    
    print(f"Instagram Account ID: {instagram_account_id} でAPIテスト中...")
    
    # メディア一覧取得テスト
    media_url = f"https://graph.facebook.com/{instagram_account_id}/media"
    media_params = {
        'fields': 'id,media_type,caption,timestamp',
        'access_token': ACCESS_TOKEN,
        'limit': 3
    }
    
    try:
        response = requests.get(media_url, params=media_params)
        
        if response.status_code == 200:
            data = response.json()
            media_list = data.get('data', [])
            
            print(f"✅ メディア取得成功: {len(media_list)}件")
            
            for i, media in enumerate(media_list):
                print(f"  メディア{i+1}:")
                print(f"    ID: {media.get('id')}")
                print(f"    タイプ: {media.get('media_type')}")
                print(f"    投稿日: {media.get('timestamp')}")
                
                # メトリクス取得テスト
                test_insights(media.get('id'))
        else:
            print(f"❌ メディア取得失敗: {response.status_code}")
            print(f"エラー: {response.text}")
            
    except Exception as e:
        print(f"❌ メディア取得エラー: {e}")

def test_insights(media_id):
    """指定されたメディアのインサイト取得テスト"""
    
    insights_url = f"https://graph.facebook.com/{media_id}/insights"
    insights_params = {
        'metric': 'likes,comments,saves,shares',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(insights_url, params=insights_params)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('data', [])
            
            print(f"    📊 メトリクス ({len(metrics)}個):")
            for metric in metrics:
                name = metric.get('name')
                values = metric.get('values', [])
                value = values[0].get('value', 0) if values else 0
                print(f"      {name}: {value}")
        else:
            print(f"    ❌ メトリクス取得失敗: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ メトリクス取得エラー: {e}")

if __name__ == "__main__":
    if not ACCESS_TOKEN:
        print("❌ ACCESS_TOKEN が見つかりません")
        exit(1)
    
    account_info = get_instagram_accounts()
    
    if account_info:
        print(f"\n🎉 成功! 正しいアカウント情報:")
        print(f"INSTAGRAM_USER_ID={account_info['instagram_account_id']}")
        print(f"USERNAME={account_info['instagram_username']}")
        print(f"FACEBOOK_PAGE_ID={account_info['facebook_page_id']}")
        print(f"FACEBOOK_PAGE_NAME={account_info['facebook_page_name']}")
        
        # .envファイルの更新提案
        print(f"\n📝 .env ファイルを以下の内容に更新してください:")
        print(f"INSTAGRAM_USER_ID={account_info['instagram_account_id']}")
        print(f"USERNAME={account_info['instagram_username']}")
        print(f"FACEBOOK_PAGE_ID={account_info['facebook_page_id']}")
        print(f"FACEBOOK_PAGE_NAME={account_info['facebook_page_name']}")
        print(f"ACCESS_TOKEN={ACCESS_TOKEN}")
    else:
        print(f"\n❌ アカウント情報の取得に失敗しました")