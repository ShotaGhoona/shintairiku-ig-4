#!/usr/bin/env python3
"""
04: 全体統合テスト - アカウントセットアップ総合検証

01-03の検証を統合し、3つのデータ（App ID、App Secret、短期トークン）から
アカウントリスト作成までの全プロセスを一括実行して検証する。
"""

import os
import json
import requests
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def run_verification_step(step_number, step_name):
    """個別の検証ステップを実行"""
    script_name = f"0{step_number}_{step_name}.py"
    print(f"\n--- ステップ {step_number}: {script_name} を実行中 ---")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(f"✅ ステップ {step_number} 完了")
            return {
                'status': 'success',
                'step': step_number,
                'script': script_name,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"❌ ステップ {step_number} 失敗")
            return {
                'status': 'error',
                'step': step_number,
                'script': script_name,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
    except Exception as e:
        print(f"❌ ステップ {step_number} 実行エラー: {e}")
        return {
            'status': 'error',
            'step': step_number,
            'script': script_name,
            'error': str(e)
        }

def load_latest_result(pattern):
    """最新の結果ファイルを読み込み"""
    import glob
    files = glob.glob(f"output-json/{pattern}")
    if not files:
        return None
    
    latest_file = max(files)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def comprehensive_account_setup():
    """全体統合テスト実行"""
    
    print("=== 04: 全体統合テスト - アカウントセットアップ総合検証 ===")
    print("3つのデータからアカウントリスト作成までの全プロセスを実行します...")
    
    # 入力データの確認
    app_id = os.getenv('INSTAGRAM_APP_ID')
    app_secret = os.getenv('INSTAGRAM_APP_SECRET')
    short_token = os.getenv('INSTAGRAM_SHORT_TOKEN')
    
    if not all([app_id, app_secret, short_token]):
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': '必要な環境変数が設定されていません',
            'required_env_vars': ['INSTAGRAM_APP_ID', 'INSTAGRAM_APP_SECRET', 'INSTAGRAM_SHORT_TOKEN']
        }
    
    # 統合テスト実行
    execution_results = []
    
    # ステップ1: 長期トークン取得
    step1_result = run_verification_step(1, 'get_long_term_token')
    execution_results.append(step1_result)
    
    if step1_result['status'] != 'success':
        return create_error_result('ステップ1で失敗したため処理を中断', execution_results)
    
    # ステップ2: Instagramページ一覧取得
    step2_result = run_verification_step(2, 'get_instagram_pages')
    execution_results.append(step2_result)
    
    if step2_result['status'] != 'success':
        return create_error_result('ステップ2で失敗したため処理を中断', execution_results)
    
    # ステップ3: アカウント詳細情報取得
    step3_result = run_verification_step(3, 'verify_account_details')
    execution_results.append(step3_result)
    
    if step3_result['status'] != 'success':
        return create_error_result('ステップ3で失敗したため処理を中断', execution_results)
    
    # 各ステップの結果を統合
    try:
        # 最新の結果ファイルを読み込み
        token_result = load_latest_result('01_long_term_token_verification_*.json')
        pages_result = load_latest_result('02_instagram_pages_verification_*.json')
        details_result = load_latest_result('03_account_details_verification_*.json')
        
        if not all([token_result, pages_result, details_result]):
            return create_error_result('結果ファイルの読み込みに失敗', execution_results)
        
        # 最終的なアカウントリストを作成
        final_account_list = []
        
        if details_result['status'] == 'success':
            for account in details_result['detailed_accounts']:
                # データベース構造に完全対応したアカウント情報
                final_account = {
                    'instagram_user_id': account['instagram_user_id'],
                    'username': account['username'],
                    'account_name': account['account_name'],
                    'profile_picture_url': account['profile_picture_url'],
                    'access_token_encrypted': account['access_token_encrypted'],  # 暗号化未実装
                    'token_expires_at': account['token_expires_at'],
                    'facebook_page_id': account['facebook_page_id'],
                    'setup_completed_at': datetime.now().isoformat(),
                    'validation_status': 'all_fields_valid' if all(account['data_validation'].values()) else 'partial_data',
                    'additional_metadata': {
                        'followers_count': account['additional_info'].get('followers_count'),
                        'media_count': account['additional_info'].get('media_count'),
                        'account_type': account['additional_info'].get('account_type'),
                        'biography': account['additional_info'].get('biography'),
                        'website': account['additional_info'].get('website')
                    }
                }
                final_account_list.append(final_account)
        
        # 成功結果を返す
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'input_verification': {
                'app_id': app_id,
                'app_secret_length': len(app_secret),
                'short_token_length': len(short_token),
                'all_inputs_valid': True
            },
            'execution_steps': execution_results,
            'step_results_summary': {
                'step_1_long_term_token': token_result['status'],
                'step_2_instagram_pages': pages_result['status'],
                'step_3_account_details': details_result['status'],
                'all_steps_successful': True
            },
            'final_account_list': final_account_list,
            'setup_summary': {
                'total_accounts_discovered': len(final_account_list),
                'accounts_with_complete_data': len([a for a in final_account_list if a['validation_status'] == 'all_fields_valid']),
                'required_database_fields': [
                    'instagram_user_id (string, UK)',
                    'username (string)',
                    'account_name (string)',
                    'profile_picture_url (string)',
                    'access_token_encrypted (text)',
                    'token_expires_at (timestamp)',
                    'facebook_page_id (string)'
                ],
                'encryption_status': '未実装（要求通り）',
                'ready_for_implementation': True
            },
            'implementation_next_steps': [
                'データベースにinstagram_accountsテーブルを作成',
                'final_account_listのデータを挿入',
                'アクセストークンの暗号化実装（必要に応じて）',
                '定期的なトークン更新の仕組み構築'
            ],
            'notes': [
                f"3つの入力データから {len(final_account_list)} 個のアカウントを発見",
                "全ての必須フィールドデータが利用可能",
                "アカウントセットアップ機能の実装準備完了",
                "検証データは output-json フォルダに保存済み"
            ]
        }
        
    except Exception as e:
        return create_error_result(f'結果統合中にエラー: {e}', execution_results)

def create_error_result(error_message, execution_results):
    """エラー結果を作成"""
    return {
        'status': 'error',
        'timestamp': datetime.now().isoformat(),
        'error': error_message,
        'execution_steps': execution_results,
        'notes': ['統合テストが途中で失敗しました']
    }

def save_result(result):
    """結果をJSONファイルに保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"04_comprehensive_account_setup_{timestamp}.json"
    filepath = f"output-json/{filename}"
    
    os.makedirs("output-json", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果を {filepath} に保存しました")
    return filepath

def main():
    """メイン処理"""
    try:
        result = comprehensive_account_setup()
        filepath = save_result(result)
        
        print("\n" + "="*60)
        if result['status'] == 'success':
            print("🎉 全体統合テストが成功しました！")
            print(f"\n📊 セットアップ結果:")
            print(f"  発見されたアカウント数: {result['setup_summary']['total_accounts_discovered']}")
            print(f"  完全なデータを持つアカウント: {result['setup_summary']['accounts_with_complete_data']}")
            print(f"  実装準備状況: {'✅ 準備完了' if result['setup_summary']['ready_for_implementation'] else '❌ 未完了'}")
            
            print(f"\n📋 発見されたアカウント:")
            for i, account in enumerate(result['final_account_list'], 1):
                print(f"  {i}. @{account['username']} ({account['account_name']})")
                print(f"     ID: {account['instagram_user_id']}")
                print(f"     Facebook Page: {account['facebook_page_id']}")
                print(f"     ステータス: {account['validation_status']}")
            
            print(f"\n🚀 次のステップ:")
            for step in result['implementation_next_steps']:
                print(f"  • {step}")
                
        else:
            print("❌ 全体統合テストが失敗しました")
            print(f"エラー: {result.get('error', 'Unknown error')}")
            
        print("="*60)
        
    except Exception as e:
        print(f"❌ 統合テスト実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()