#!/usr/bin/env python3
"""
01: 長期トークン取得の検証

短期アクセストークンから長期アクセストークンへの変換を実装し、
結果をJSONファイルに保存する。
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def get_long_term_token():
    """短期トークンを長期トークンに変換"""
    app_id = os.getenv('INSTAGRAM_APP_ID')
    app_secret = os.getenv('INSTAGRAM_APP_SECRET')
    short_token = os.getenv('INSTAGRAM_SHORT_TOKEN')
    
    if not all([app_id, app_secret, short_token]):
        raise ValueError("必要な環境変数が設定されていません")
    
    # 長期トークン取得のエンドポイント
    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # 検証結果をまとめる
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'input_data': {
                'app_id': app_id,
                'app_secret_length': len(app_secret),
                'short_token_length': len(short_token)
            },
            'api_response': data,
            'long_term_token': data.get('access_token'),
            'expires_in': data.get('expires_in'),
            'token_type': data.get('token_type'),
            'notes': [
                "長期トークンの取得に成功",
                f"有効期限: {data.get('expires_in', 'N/A')}秒",
                "このトークンを使用してFacebookページの一覧を取得します"
            ]
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'response_text': getattr(e.response, 'text', 'N/A') if hasattr(e, 'response') else 'N/A'
        }

def save_result(result):
    """結果をJSONファイルに保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"01_long_term_token_verification_{timestamp}.json"
    filepath = f"output-json/{filename}"
    
    os.makedirs("output-json", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"結果を {filepath} に保存しました")
    return filepath

def main():
    """メイン処理"""
    print("=== 01: 長期トークン取得の検証 ===")
    print("短期トークンから長期トークンへの変換を実行します...")
    
    try:
        result = get_long_term_token()
        filepath = save_result(result)
        
        if result['status'] == 'success':
            print("✅ 長期トークンの取得に成功しました")
            print(f"トークン長: {len(result['long_term_token'])} 文字")
            print(f"有効期限: {result['expires_in']} 秒")
        else:
            print("❌ 長期トークンの取得に失敗しました")
            print(f"エラー: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()