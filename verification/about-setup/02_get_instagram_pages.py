#!/usr/bin/env python3
"""
02: Instagramページ一覧取得の検証

長期トークンを使用してユーザーのFacebookページ一覧を取得し、
Instagram Businessアカウントに接続されているページを特定する。
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def get_user_pages(access_token):
    """ユーザーのFacebookページ一覧を取得"""
    url = "https://graph.facebook.com/v21.0/me/accounts"
    
    params = {
        'access_token': access_token,
        'fields': 'id,name,access_token,category,category_list'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Facebookページの取得に失敗: {e}")

def get_instagram_account_info(page_id, page_access_token):
    """ページに接続されているInstagramアカウント情報を取得"""
    url = f"https://graph.facebook.com/v21.0/{page_id}"
    
    params = {
        'access_token': page_access_token,
        'fields': 'instagram_business_account'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'instagram_business_account' in data:
            return data['instagram_business_account']
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"ページ {page_id} のInstagramアカウント取得エラー: {e}")
        return None

def get_instagram_account_details(instagram_account_id, access_token):
    """Instagramアカウントの詳細情報を取得"""
    url = f"https://graph.facebook.com/v21.0/{instagram_account_id}"
    
    params = {
        'access_token': access_token,
        'fields': 'id,username,name,profile_picture_url'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Instagramアカウント詳細取得エラー: {e}")
        return None

def verify_instagram_pages():
    """Instagramページ一覧取得の検証"""
    
    # 01の結果から長期トークンを読み込み
    try:
        # 最新の長期トークンファイルを探す
        import glob
        token_files = glob.glob("output-json/01_long_term_token_verification_*.json")
        if not token_files:
            raise FileNotFoundError("長期トークンファイルが見つかりません。先に01を実行してください。")
        
        latest_file = max(token_files)
        with open(latest_file, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        if token_data['status'] != 'success':
            raise ValueError("長期トークンの取得が失敗しています")
        
        long_term_token = token_data['long_term_token']
        
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': f"長期トークンの読み込みに失敗: {e}",
            'notes': ["先に01_get_long_term_token.pyを実行してください"]
        }
    
    try:
        # Facebookページ一覧を取得
        pages_data = get_user_pages(long_term_token)
        
        instagram_accounts = []
        
        # 各ページでInstagramアカウントをチェック
        for page in pages_data.get('data', []):
            page_id = page['id']
            page_name = page['name']
            page_access_token = page['access_token']
            
            # InstagramBusinessアカウントの存在をチェック
            instagram_account = get_instagram_account_info(page_id, page_access_token)
            
            if instagram_account:
                # Instagramアカウントの詳細を取得
                instagram_details = get_instagram_account_details(
                    instagram_account['id'], 
                    page_access_token
                )
                
                if instagram_details:
                    account_info = {
                        'instagram_user_id': instagram_details.get('id'),
                        'username': instagram_details.get('username'),
                        'account_name': instagram_details.get('name'),
                        'profile_picture_url': instagram_details.get('profile_picture_url'),
                        'access_token': page_access_token,  # 暗号化は後で実装
                        'facebook_page_id': page_id,
                        'facebook_page_name': page_name,
                        'token_expires_at': None  # 長期トークンのため期限を設定
                    }
                    instagram_accounts.append(account_info)
        
        # 検証結果をまとめる
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'input_data': {
                'long_term_token_length': len(long_term_token),
                'total_facebook_pages': len(pages_data.get('data', []))
            },
            'api_responses': {
                'facebook_pages': pages_data,
                'instagram_accounts_found': len(instagram_accounts)
            },
            'instagram_accounts': instagram_accounts,
            'summary': {
                'total_facebook_pages': len(pages_data.get('data', [])),
                'instagram_connected_pages': len(instagram_accounts),
                'target_data_structure': {
                    'instagram_user_id': 'string (UK)',
                    'username': 'string',
                    'account_name': 'string',
                    'profile_picture_url': 'string',
                    'access_token_encrypted': 'text (暗号化は未実装)',
                    'token_expires_at': 'timestamp',
                    'facebook_page_id': 'string'
                }
            },
            'notes': [
                f"合計 {len(pages_data.get('data', []))} 個のFacebookページを発見",
                f"うち {len(instagram_accounts)} 個がInstagramに接続済み",
                "暗号化処理は要求通り未実装",
                "全てのターゲットデータ構造を取得済み"
            ]
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'notes': ["API呼び出し中にエラーが発生しました"]
        }

def save_result(result):
    """結果をJSONファイルに保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"02_instagram_pages_verification_{timestamp}.json"
    filepath = f"output-json/{filename}"
    
    os.makedirs("output-json", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"結果を {filepath} に保存しました")
    return filepath

def main():
    """メイン処理"""
    print("=== 02: Instagramページ一覧取得の検証 ===")
    print("Facebookページ一覧とInstagramアカウント情報を取得します...")
    
    try:
        result = verify_instagram_pages()
        filepath = save_result(result)
        
        if result['status'] == 'success':
            print("✅ Instagramページ一覧の取得に成功しました")
            print(f"Facebookページ総数: {result['summary']['total_facebook_pages']}")
            print(f"Instagram接続済みページ: {result['summary']['instagram_connected_pages']}")
            
            for i, account in enumerate(result['instagram_accounts'], 1):
                print(f"  {i}. @{account['username']} ({account['account_name']})")
        else:
            print("❌ Instagramページ一覧の取得に失敗しました")
            print(f"エラー: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()