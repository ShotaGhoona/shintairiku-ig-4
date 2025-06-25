#!/usr/bin/env python3
"""
Meta API データ取得検証の実行スクリプト
全4つのPhaseを順次実行してDB設計の妥当性を検証
"""

import subprocess
import sys
import os
from datetime import datetime

def run_phase(script_name, phase_name):
    """指定されたPhaseスクリプトを実行"""
    
    print(f"\n🚀 {phase_name} 開始...")
    print("=" * 60)
    
    try:
        # Pythonスクリプトを実行
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ エラー出力:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {phase_name} 完了")
            return True
        else:
            print(f"❌ {phase_name} 失敗 (終了コード: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {phase_name} 実行エラー: {e}")
        return False

def main():
    """検証の実行"""
    
    print("🔍 Meta Instagram API データ取得検証")
    print("=" * 60)
    print(f"実行開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 検証対象のフェーズ
    phases = [
        ("01_get_posts_data.py", "Phase 1: 投稿一覧取得検証"),
        ("02_get_post_metrics.py", "Phase 2: 投稿メトリクス取得検証"),
        ("03_data_integration.py", "Phase 3: データ統合検証"),
        ("04_response_analysis.py", "Phase 4: レスポンス詳細分析")
    ]
    
    results = []
    
    # 各フェーズを順次実行
    for script, phase_name in phases:
        success = run_phase(script, phase_name)
        results.append((phase_name, success))
        
        if not success:
            print(f"\n⚠️ {phase_name}で問題が発生しました。")
            user_input = input("続行しますか？ (y/N): ")
            if user_input.lower() != 'y':
                print("検証を中止します。")
                break
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("🏁 検証結果サマリー")
    print("=" * 60)
    
    for phase_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status} {phase_name}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n📊 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 全ての検証が成功しました！")
        print("設計したDB構造はMeta APIから必要なデータを取得できます。")
    else:
        print(f"\n⚠️ {total_count - success_count}個のフェーズで問題が発生しました。")
        print("DB設計の見直しやAPI制約の確認が必要です。")
    
    print(f"\n実行終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 生成されたファイルの一覧
    generated_files = [
        'posts_data_verification.json',
        'posts_table_sample.json',
        'post_metrics_verification.json',
        'post_metrics_table_sample.json',
        'data_integration_results.json',
        'frontend_compatible_data.json',
        'api_response_analysis.json'
    ]
    
    existing_files = [f for f in generated_files if os.path.exists(f)]
    
    if existing_files:
        print(f"\n📁 生成されたファイル ({len(existing_files)}個):")
        for file in existing_files:
            file_size = os.path.getsize(file)
            print(f"  - {file} ({file_size} bytes)")

if __name__ == "__main__":
    # 必要なパッケージの確認
    try:
        import requests
        import dotenv
    except ImportError as e:
        print(f"❌ 必要なパッケージがインストールされていません: {e}")
        print("以下のコマンドでインストールしてください:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # .envファイルの確認
    if not os.path.exists('.env'):
        print("❌ .envファイルが見つかりません。")
        print("Instagram API の認証情報を .env ファイルに設定してください。")
        sys.exit(1)
    
    main()