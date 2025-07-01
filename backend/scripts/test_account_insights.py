#!/usr/bin/env python3
"""
Account Insights Test Script
アカウントインサイトの実験・検証用スクリプト

Usage:
    python scripts/test_account_insights.py
"""

import asyncio
import sys
import os
from datetime import datetime, date
import json

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import get_db_sync
from app.repositories.instagram_account_repository import InstagramAccountRepository
from app.services.data_collection.instagram_api_client import InstagramAPIClient

async def test_account_insights():
    """アカウントインサイト実験"""
    
    print("🧪 アカウントインサイトテストを開始します...")
    print("="*60)
    
    # データベース接続
    db = get_db_sync()
    account_repo = InstagramAccountRepository(db)
    
    try:
        # アクティブアカウント取得
        accounts = await account_repo.get_active_accounts()
        print(f"📊 アクティブアカウント: {len(accounts)} アカウント")
        
        if not accounts:
            print("❌ アクティブアカウントが見つかりません")
            return
        
        # 各アカウントでテスト
        for i, account in enumerate(accounts, 1):
            print(f"\n🔍 アカウント: {i}/{len(accounts)}: {account.username}")
            print("-" * 40)
            
            await test_single_account(account)
            
            # アカウント間の待機
            if i < len(accounts):
                print("⏱️ 次のアカウントへの移行を10秒待ちます...")
                await asyncio.sleep(10)
    
    finally:
        db.close()

async def test_single_account(account):
    """単一アカウントのテスト"""
    
    print(f"📝 アカウント情報:")
    print(f"   ID: {account.id}")
    print(f"   Instagram User ID: {account.instagram_user_id}")
    print(f"   Username: {account.username}")
    print(f"   Token Length: {len(account.access_token_encrypted)} chars")
    
    try:
        async with InstagramAPIClient() as api_client:
            
            # 1. 基本アカウントデータ取得テスト
            print(f"\n1️⃣ 基本アカウントデータ取得テスト...")
            try:
                basic_data = await api_client.get_basic_account_data(
                    account.instagram_user_id,
                    account.access_token_encrypted
                )
                
                print(f"   ✅ 基本データ取得成功:")
                print(f"      Followers: {basic_data.get('followers_count', 'N/A')}")
                print(f"      Following: {basic_data.get('follows_count', 'N/A')}")
                print(f"      Media Count: {basic_data.get('media_count', 'N/A')}")
                print(f"      Username: {basic_data.get('username', 'N/A')}")
                print(f"      Account Name: {basic_data.get('name', 'N/A')}")
                
            except Exception as e:
                print(f"   ❌ 基本データ取得失敗: {e}")
                return  # 基本データが取れない場合は他のテストもスキップ
            
            # 2. アカウントインサイト取得テスト（今日）
            print(f"\n2️⃣ アカウントインサイト取得テスト（今日）...")
            today = date.today()
            
            try:
                insights_today = await api_client.get_insights_metrics(
                    account.instagram_user_id,
                    account.access_token_encrypted,
                    today
                )
                
                print(f"   📅 Date: {today}")
                if insights_today:
                    print(f"   ✅ アカウントインサイト取得成功:")
                    for metric, value in insights_today.items():
                        print(f"      {metric}: {value}")
                else:
                    print(f"   ⚠️ アカウントインサイトが空です（データが返されませんでした）")
                    
            except Exception as e:
                print(f"   ❌ アカウントインサイト取得失敗: {e}")
            
            # 3. アカウントインサイト取得テスト（昨日）
            print(f"\n3️⃣ アカウントインサイト取得テスト（昨日）...")
            yesterday = date.today().replace(day=date.today().day - 1) if date.today().day > 1 else date.today()
            
            try:
                insights_yesterday = await api_client.get_insights_metrics(
                    account.instagram_user_id,
                    account.access_token_encrypted,
                    yesterday
                )
                
                print(f"   📅 Date: {yesterday}")
                if insights_yesterday:
                    print(f"   ✅ アカウントインサイト取得成功:")
                    for metric, value in insights_yesterday.items():
                        print(f"      {metric}: {value}")
                else:
                    print(f"   ⚠️ アカウントインサイトが空です（データが返されませんでした）")
                    
            except Exception as e:
                print(f"   ❌ アカウントインサイト取得失敗: {e}")
            
            # 4. 最新投稿データ取得テスト（参考）
            print(f"\n4️⃣ 最新投稿データ取得テスト（参考）...")
            try:
                url = api_client.config.get_user_media_url(account.instagram_user_id)
                params = {
                    'fields': 'id,media_type,timestamp,like_count,comments_count',
                    'access_token': account.access_token_encrypted,
                    'limit': 5
                }
                
                response = await api_client._make_request(url, params)
                posts = response.get('data', [])
                
                print(f"   ✅ 最新投稿データ取得成功: {len(posts)} 投稿")
                for i, post in enumerate(posts, 1):
                    timestamp = post.get('timestamp', '')
                    post_date = timestamp.split('T')[0] if timestamp else 'Unknown'
                    print(f"      Post {i}: {post.get('media_type')} on {post_date} - {post.get('like_count', 0)} likes")
                    
            except Exception as e:
                print(f"   ❌ 最新投稿データ取得失敗: {e}")
            
            # 5. 日次統計データ計算テスト
            print(f"\n5️⃣ 日次統計データ計算テスト...")
            try:
                # 今日の投稿をフィルタリング
                today_posts = []
                for post in posts:
                    timestamp = post.get('timestamp', '')
                    if timestamp:
                        try:
                            post_date_str = timestamp.split('T')[0]
                            post_date = date.fromisoformat(post_date_str)
                            if post_date == today:
                                today_posts.append(post)
                        except:
                            continue
                
                # 統計計算
                posts_count = len(today_posts)
                total_likes = sum(p.get('like_count', 0) for p in today_posts)
                total_comments = sum(p.get('comments_count', 0) for p in today_posts)
                avg_likes = total_likes / posts_count if posts_count > 0 else 0.0
                avg_comments = total_comments / posts_count if posts_count > 0 else 0.0
                
                print(f"   📊 Daily Stats for {today}:")
                print(f"      Posts: {posts_count}")
                print(f"      Total Likes: {total_likes}")
                print(f"      Total Comments: {total_comments}")
                print(f"      Avg Likes/Post: {avg_likes:.2f}")
                print(f"      Avg Comments/Post: {avg_comments:.2f}")
                
            except Exception as e:
                print(f"   ❌ 日次統計データ計算失敗: {e}")
    
    except Exception as e:
        print(f"❌ Overall test failed for {account.username}: {e}")

async def main():
    """メイン実行"""
    try:
        await test_account_insights()
        
        print(f"\n{'='*60}")
        print("🏁 テストが完了しました！")
        print("="*60)
        
    except Exception as e:
        print(f"❌ テストに失敗しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)