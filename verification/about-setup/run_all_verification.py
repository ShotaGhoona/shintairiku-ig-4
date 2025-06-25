#!/usr/bin/env python3
"""
アカウントセットアップ検証 - 統合実行スクリプト

このスクリプトは01-04の全ての検証を順次実行し、
3つのデータからアカウントリスト作成までの全プロセスを検証します。

使用方法:
1. .envファイルにINSTAGRAM_APP_ID、INSTAGRAM_APP_SECRET、INSTAGRAM_SHORT_TOKENを設定
2. python run_all_verification.py を実行

結果はoutput-jsonフォルダに保存されます。
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """個別スクリプトを実行"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"📝 実行スクリプト: {script_name}")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, script_name], cwd='.')
        
        if result.returncode == 0:
            print(f"\n✅ {description} - 完了")
            return True
        else:
            print(f"\n❌ {description} - 失敗 (終了コード: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n❌ {description} - 実行エラー: {e}")
        return False

def check_environment():
    """環境変数の確認"""
    required_vars = ['INSTAGRAM_APP_ID', 'INSTAGRAM_APP_SECRET', 'INSTAGRAM_SHORT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ 必要な環境変数が設定されていません:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n.envファイルに以下の形式で設定してください:")
        print("INSTAGRAM_APP_ID=your_app_id")
        print("INSTAGRAM_APP_SECRET=your_app_secret")
        print("INSTAGRAM_SHORT_TOKEN=your_short_token")
        return False
    
    print("✅ 環境変数の確認完了")
    for var in required_vars:
        value = os.getenv(var)
        print(f"  {var}: {'設定済み' if value else '未設定'} ({len(value)}文字)" if value else f"  {var}: 未設定")
    
    return True

def main():
    """メイン実行処理"""
    print("🚀 Instagram アカウントセットアップ検証を開始します")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 環境変数確認
    if not check_environment():
        return False
    
    # 実行するスクリプトのリスト
    scripts = [
        ('01_get_long_term_token.py', '01: 長期トークン取得の検証'),
        ('02_get_instagram_pages.py', '02: Instagramページ一覧取得の検証'),
        ('03_verify_account_details.py', '03: 各アカウントの詳細情報取得の検証'),
        ('04_comprehensive_account_setup.py', '04: 全体統合テスト')
    ]
    
    # 各スクリプトを順次実行
    success_count = 0
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"\n⚠️  {script_name} で失敗しました。処理を継続します...")
    
    # 実行結果サマリー
    print(f"\n{'='*60}")
    print("📊 実行結果サマリー")
    print('='*60)
    print(f"✅ 成功: {success_count}/{len(scripts)} スクリプト")
    print(f"❌ 失敗: {len(scripts) - success_count}/{len(scripts)} スクリプト")
    
    if success_count == len(scripts):
        print("\n🎉 全ての検証が成功しました！")
        print("📁 結果ファイルは output-json フォルダに保存されています")
        print("🚀 アカウントセットアップ機能の実装準備が完了しました")
    else:
        print("\n⚠️  一部の検証で問題が発生しました")
        print("📁 成功した検証の結果は output-json フォルダで確認できます")
    
    print(f"⏰ 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
    
    return success_count == len(scripts)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)