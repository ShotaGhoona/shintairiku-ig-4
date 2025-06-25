#!/usr/bin/env python3
"""
Facebook/Instagram API検証スクリプト
90アカウント近くあるはずだが30しか取得できない問題を調査
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

def load_environment():
    """環境変数を読み込み"""
    load_dotenv()
    
    app_id = os.getenv('INSTAGRAM_APP_ID')
    app_secret = os.getenv('INSTAGRAM_APP_SECRET') 
    short_token = os.getenv('INSTAGRAM_SHORT_TOKEN')
    
    if not all([app_id, app_secret, short_token]):
        raise ValueError("必要な環境変数が設定されていません")
    
    return app_id, app_secret, short_token

def exchange_for_long_token(app_id, app_secret, short_token):
    """短期トークンを長期トークンに交換"""
    print("📌 Step 1: 短期トークンを長期トークンに交換中...")
    
    url = "https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"トークン交換失敗: {response.text}")
    
    data = response.json()
    long_token = data['access_token']
    print(f"✅ 長期トークン取得成功 (長さ: {len(long_token)})")
    return long_token

def get_all_pages_with_pagination(access_token):
    """ページネーション対応でFacebookページを全件取得"""
    print("📌 Step 2: 全Facebookページを取得中（ページネーション対応）...")
    
    all_pages = []
    url = "https://graph.facebook.com/v20.0/me/accounts"
    
    params = {
        'access_token': access_token,
        'fields': 'id,name,access_token,instagram_business_account',
        'limit': 100  # 最大リミット
    }
    
    page_count = 0
    while url:
        page_count += 1
        print(f"  📄 ページ {page_count} を取得中...")
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ エラー: {response.text}")
            break
            
        data = response.json()
        pages = data.get('data', [])
        
        print(f"    ✅ {len(pages)}件のページを取得")
        all_pages.extend(pages)
        
        # 次のページのURLを取得
        paging = data.get('paging', {})
        url = paging.get('next')
        if url:
            # paramsをNoneにして、URLに含まれるパラメータを使用
            params = None
            print(f"    🔄 次のページあり: {url[:100]}...")
        else:
            print("    🏁 最後のページに到達")
    
    print(f"✅ 全ページ取得完了: 総数 {len(all_pages)} ページ")
    return all_pages

def analyze_instagram_accounts(pages, access_token):
    """各ページのInstagramアカウント状況を詳細分析"""
    print("📌 Step 3: Instagramアカウント詳細分析...")
    
    instagram_pages = []
    no_instagram_pages = []
    instagram_errors = []
    
    for i, page in enumerate(pages, 1):
        page_name = page.get('name', 'Unknown')
        page_id = page.get('id')
        instagram_account_id = page.get('instagram_business_account', {}).get('id') if page.get('instagram_business_account') else None
        
        print(f"  [{i:3d}/{len(pages)}] {page_name}")
        
        if not instagram_account_id:
            print(f"    ❌ Instagramビジネスアカウント未接続")
            no_instagram_pages.append({
                'page_name': page_name,
                'page_id': page_id,
                'reason': 'instagram_business_account not found'
            })
            continue
        
        # Instagramアカウント詳細を取得してみる
        try:
            instagram_url = f"https://graph.facebook.com/v20.0/{instagram_account_id}"
            instagram_params = {
                'access_token': page.get('access_token', access_token),
                'fields': 'id,username,name,profile_picture_url,biography,followers_count,media_count'
            }
            
            instagram_response = requests.get(instagram_url, params=instagram_params)
            
            if instagram_response.status_code == 200:
                instagram_data = instagram_response.json()
                print(f"    ✅ Instagram: @{instagram_data.get('username', 'unknown')} (ID: {instagram_account_id})")
                print(f"        フォロワー: {instagram_data.get('followers_count', 'N/A')}, メディア: {instagram_data.get('media_count', 'N/A')}")
                
                instagram_pages.append({
                    'page_name': page_name,
                    'page_id': page_id,
                    'instagram_id': instagram_account_id,
                    'instagram_username': instagram_data.get('username'),
                    'followers_count': instagram_data.get('followers_count'),
                    'media_count': instagram_data.get('media_count')
                })
            else:
                error_data = instagram_response.json() if instagram_response.text else {'error': 'No response'}
                print(f"    ❌ Instagram取得エラー: {instagram_response.status_code}")
                print(f"        {error_data}")
                
                instagram_errors.append({
                    'page_name': page_name,
                    'page_id': page_id,
                    'instagram_id': instagram_account_id,
                    'error_code': instagram_response.status_code,
                    'error_message': error_data
                })
                
        except Exception as e:
            print(f"    ❌ 例外エラー: {str(e)}")
            instagram_errors.append({
                'page_name': page_name,
                'page_id': page_id,
                'instagram_id': instagram_account_id,
                'error': str(e)
            })
    
    return instagram_pages, no_instagram_pages, instagram_errors

def save_detailed_report(all_pages, instagram_pages, no_instagram_pages, instagram_errors):
    """詳細レポートをJSONファイルに保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"instagram_analysis_report_{timestamp}.json"
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_facebook_pages': len(all_pages),
            'instagram_connected_pages': len(instagram_pages),
            'pages_without_instagram': len(no_instagram_pages),
            'instagram_access_errors': len(instagram_errors)
        },
        'facebook_pages': all_pages,
        'instagram_connected': instagram_pages,
        'no_instagram_connection': no_instagram_pages,
        'instagram_errors': instagram_errors
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 詳細レポート保存: {filename}")
    return filename

def print_summary(instagram_pages, no_instagram_pages, instagram_errors):
    """結果サマリーを表示"""
    print("\n" + "="*60)
    print("📊 分析結果サマリー")
    print("="*60)
    
    total_pages = len(instagram_pages) + len(no_instagram_pages) + len(instagram_errors)
    
    print(f"📈 総Facebookページ数: {total_pages}")
    print(f"✅ Instagramアカウント正常取得: {len(instagram_pages)}")
    print(f"❌ Instagram未接続: {len(no_instagram_pages)}")
    print(f"⚠️  Instagramアクセスエラー: {len(instagram_errors)}")
    
    if instagram_errors:
        print(f"\n⚠️  エラー詳細:")
        for error in instagram_errors[:5]:  # 最初の5件のみ表示
            print(f"  - {error['page_name']}: {error.get('error_code', 'Exception')}")
        if len(instagram_errors) > 5:
            print(f"  ... 他 {len(instagram_errors) - 5} 件")
    
    print(f"\n🎯 実際に取得可能なInstagramアカウント数: {len(instagram_pages)}")
    
    if len(instagram_pages) < 90:
        print(f"\n🔍 なぜ90アカウントに届かないのか:")
        print(f"  - Instagram未接続ページ: {len(no_instagram_pages)} 件")
        print(f"  - アクセスエラー: {len(instagram_errors)} 件")
        print(f"  - 合計不足分: {90 - len(instagram_pages)} 件")

def main():
    """メイン処理"""
    try:
        print("🚀 Instagram分析スクリプト開始")
        print("="*60)
        
        # 環境変数読み込み
        app_id, app_secret, short_token = load_environment()
        print(f"🔑 App ID: {app_id}")
        
        # 長期トークン取得
        long_token = exchange_for_long_token(app_id, app_secret, short_token)
        
        # 全ページ取得（ページネーション対応）
        all_pages = get_all_pages_with_pagination(long_token)
        
        # Instagram詳細分析
        instagram_pages, no_instagram_pages, instagram_errors = analyze_instagram_accounts(all_pages, long_token)
        
        # レポート保存
        report_file = save_detailed_report(all_pages, instagram_pages, no_instagram_pages, instagram_errors)
        
        # サマリー表示
        print_summary(instagram_pages, no_instagram_pages, instagram_errors)
        
        print(f"\n✅ 分析完了! 詳細は {report_file} を確認してください")
        
    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()