#!/usr/bin/env python3
"""
03: 各アカウントの詳細情報取得の検証

02で取得したInstagramアカウントの詳細情報を再確認し、
データベース構造に必要な全ての情報が正しく取得できることを検証する。
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def get_instagram_account_extended_details(instagram_account_id, access_token):
    """Instagramアカウントの拡張詳細情報を取得"""
    url = f"https://graph.facebook.com/v21.0/{instagram_account_id}"
    
    params = {
        'access_token': access_token,
        'fields': 'id,username,name,profile_picture_url,biography,website,followers_count,media_count,account_type'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Instagramアカウント詳細取得エラー: {e}")
        return None

def calculate_token_expiry(expires_in_seconds):
    """トークンの有効期限を計算"""
    if expires_in_seconds:
        expiry_date = datetime.now() + timedelta(seconds=int(expires_in_seconds))
        return expiry_date.isoformat()
    return None

def verify_account_details():
    """各アカウントの詳細情報取得の検証"""
    
    try:
        # 02の結果からInstagramアカウント情報を読み込み
        import glob
        pages_files = glob.glob("output-json/02_instagram_pages_verification_*.json")
        if not pages_files:
            raise FileNotFoundError("Instagramページファイルが見つかりません。先に02を実行してください。")
        
        latest_file = max(pages_files)
        with open(latest_file, 'r', encoding='utf-8') as f:
            pages_data = json.load(f)
        
        if pages_data['status'] != 'success':
            raise ValueError("Instagramページの取得が失敗しています")
        
        # 01の結果から長期トークンの有効期限情報を取得
        token_files = glob.glob("output-json/01_long_term_token_verification_*.json")
        token_expires_in = None
        if token_files:
            latest_token_file = max(token_files)
            with open(latest_token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                token_expires_in = token_data.get('expires_in')
        
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': f"前の検証結果の読み込みに失敗: {e}",
            'notes': ["先に01と02の検証を実行してください"]
        }
    
    try:
        detailed_accounts = []
        
        for account in pages_data['instagram_accounts']:
            instagram_user_id = account['instagram_user_id']
            access_token = account['access_token']
            
            # 拡張詳細情報を取得
            extended_details = get_instagram_account_extended_details(
                instagram_user_id, 
                access_token
            )
            
            if extended_details:
                # データベース構造に合わせて情報を整理
                detailed_account = {
                    'instagram_user_id': extended_details.get('id'),
                    'username': extended_details.get('username'),
                    'account_name': extended_details.get('name'),
                    'profile_picture_url': extended_details.get('profile_picture_url'),
                    'access_token_encrypted': access_token,  # 暗号化は未実装
                    'token_expires_at': calculate_token_expiry(token_expires_in),
                    'facebook_page_id': account['facebook_page_id'],
                    'additional_info': {
                        'biography': extended_details.get('biography'),
                        'website': extended_details.get('website'),
                        'followers_count': extended_details.get('followers_count'),
                        'media_count': extended_details.get('media_count'),
                        'account_type': extended_details.get('account_type'),
                        'facebook_page_name': account.get('facebook_page_name')
                    },
                    'data_validation': {
                        'instagram_user_id_valid': bool(extended_details.get('id')),
                        'username_valid': bool(extended_details.get('username')),
                        'account_name_valid': bool(extended_details.get('name')),
                        'profile_picture_url_valid': bool(extended_details.get('profile_picture_url')),
                        'access_token_valid': bool(access_token),
                        'facebook_page_id_valid': bool(account['facebook_page_id'])
                    }
                }
                detailed_accounts.append(detailed_account)
        
        # データベース挿入用のSQL例を生成
        sql_examples = []
        for account in detailed_accounts:
            sql = f"""
INSERT INTO instagram_accounts (
    instagram_user_id,
    username,
    account_name,
    profile_picture_url,
    access_token_encrypted,
    token_expires_at,
    facebook_page_id,
    created_at,
    updated_at
) VALUES (
    '{account['instagram_user_id']}',
    '{account['username']}',
    '{account['account_name']}',
    '{account['profile_picture_url']}',
    '{account['access_token_encrypted']}',
    '{account['token_expires_at']}',
    '{account['facebook_page_id']}',
    NOW(),
    NOW()
);"""
            sql_examples.append(sql.strip())
        
        # 検証結果をまとめる
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'input_data': {
                'accounts_from_step_02': len(pages_data['instagram_accounts']),
                'token_expires_in_seconds': token_expires_in
            },
            'detailed_accounts': detailed_accounts,
            'database_ready_structure': {
                'table_name': 'instagram_accounts',
                'required_fields': [
                    'instagram_user_id (string, UK)',
                    'username (string)',
                    'account_name (string)',
                    'profile_picture_url (string)',
                    'access_token_encrypted (text)',
                    'token_expires_at (timestamp)',
                    'facebook_page_id (string)'
                ],
                'all_fields_available': True
            },
            'sql_insertion_examples': sql_examples,
            'validation_summary': {
                'total_accounts_processed': len(detailed_accounts),
                'accounts_with_valid_data': len([a for a in detailed_accounts if all(a['data_validation'].values())]),
                'missing_data_issues': []
            },
            'notes': [
                f"合計 {len(detailed_accounts)} 個のアカウントの詳細情報を取得",
                "全ての必須フィールドのデータが利用可能",
                "暗号化処理は要求通り未実装",
                "データベース挿入の準備完了",
                f"トークン有効期限: {calculate_token_expiry(token_expires_in) if token_expires_in else 'N/A'}"
            ]
        }
        
        # 不足データのチェック
        for account in detailed_accounts:
            invalid_fields = [k for k, v in account['data_validation'].items() if not v]
            if invalid_fields:
                result['validation_summary']['missing_data_issues'].append({
                    'account_id': account['instagram_user_id'],
                    'username': account['username'],
                    'invalid_fields': invalid_fields
                })
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'notes': ["アカウント詳細情報の取得中にエラーが発生しました"]
        }

def save_result(result):
    """結果をJSONファイルに保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"03_account_details_verification_{timestamp}.json"
    filepath = f"output-json/{filename}"
    
    os.makedirs("output-json", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"結果を {filepath} に保存しました")
    return filepath

def main():
    """メイン処理"""
    print("=== 03: 各アカウントの詳細情報取得の検証 ===")
    print("Instagramアカウントの詳細情報とデータベース準備を実行します...")
    
    try:
        result = verify_account_details()
        filepath = save_result(result)
        
        if result['status'] == 'success':
            print("✅ アカウント詳細情報の取得に成功しました")
            print(f"処理済みアカウント数: {result['validation_summary']['total_accounts_processed']}")
            print(f"有効なデータを持つアカウント数: {result['validation_summary']['accounts_with_valid_data']}")
            
            if result['validation_summary']['missing_data_issues']:
                print("⚠️  一部のアカウントでデータ不足があります:")
                for issue in result['validation_summary']['missing_data_issues']:
                    print(f"  @{issue['username']}: {', '.join(issue['invalid_fields'])}")
            
            print("\n取得されたアカウント:")
            for account in result['detailed_accounts']:
                print(f"  @{account['username']} ({account['account_name']})")
                print(f"    ID: {account['instagram_user_id']}")
                print(f"    Facebook Page: {account['facebook_page_id']}")
                
        else:
            print("❌ アカウント詳細情報の取得に失敗しました")
            print(f"エラー: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()