#!/usr/bin/env python3
"""
アクセストークンの詳細チェック
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')

def check_token_debug():
    """トークンの詳細情報をデバッグ"""
    
    print("🔍 アクセストークン詳細チェック")
    print("=" * 40)
    
    # トークンの基本情報
    print(f"トークン長: {len(ACCESS_TOKEN) if ACCESS_TOKEN else 'None'}")
    print(f"Instagram User ID: {INSTAGRAM_USER_ID}")
    print(f"トークンプレフィックス: {ACCESS_TOKEN[:20] if ACCESS_TOKEN else 'None'}...")
    print()
    
    # Facebook Graph APIでトークン情報を確認
    debug_url = "https://graph.facebook.com/debug_token"
    params = {
        'input_token': ACCESS_TOKEN,
        'access_token': ACCESS_TOKEN  # 自分のトークンで自分のトークンを確認
    }
    
    try:
        print("🔄 Facebook Token Debug API 確認中...")
        response = requests.get(debug_url, params=params)
        
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token_data = data.get('data', {})
            
            print("\n✅ トークン情報:")
            print(f"  有効: {token_data.get('is_valid', False)}")
            print(f"  アプリID: {token_data.get('app_id')}")
            print(f"  ユーザーID: {token_data.get('user_id')}")
            print(f"  有効期限: {token_data.get('expires_at', 'なし')}")
            print(f"  スコープ: {token_data.get('scopes', [])}")
        
    except Exception as e:
        print(f"❌ トークンデバッグエラー: {e}")
    
    # 直接Instagram APIで基本確認
    print("\n🔄 Instagram API 基本確認...")
    
    # 最もシンプルなエンドポイントでテスト
    test_url = f"https://graph.instagram.com/me"
    test_params = {
        'fields': 'id,username',
        'access_token': ACCESS_TOKEN
    }
    
    try:
        response = requests.get(test_url, params=test_params)
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Instagram API 接続成功:")
            print(f"  ID: {data.get('id')}")
            print(f"  ユーザー名: {data.get('username')}")
        else:
            print("\n❌ Instagram API 接続失敗")
            
    except Exception as e:
        print(f"❌ Instagram API エラー: {e}")

if __name__ == "__main__":
    if not ACCESS_TOKEN:
        print("❌ ACCESS_TOKEN が見つかりません")
        exit(1)
    
    check_token_debug()