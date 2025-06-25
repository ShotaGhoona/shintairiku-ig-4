#!/usr/bin/env python3
"""
Historical Data Collection Script
過去の投稿データとメトリクスを一括収集するスクリプト

Usage:
    # 過去30日間のデータ収集
    python scripts/collect_historical_data.py --account 17841402015304577 --days 30

    # 指定期間のデータ収集
    python scripts/collect_historical_data.py --account 17841402015304577 --from 2024-01-01 --to 2024-12-31

    # 全投稿データ収集
    python scripts/collect_historical_data.py --account 17841402015304577 --all-posts

    # メトリクスのみ収集
    python scripts/collect_historical_data.py --account 17841402015304577 --missing-metrics

    # 投稿のみ（メトリクスなし）
    python scripts/collect_historical_data.py --account 17841402015304577 --days 30 --no-metrics
"""

import asyncio
import sys
import argparse
import logging
import os
from datetime import datetime, date, timedelta
from typing import Optional
import json

# プロジェクトルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.data_collection.historical_collector_service import create_historical_collector
from app.core.database import test_connection

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('historical_collection.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description='Instagram Historical Data Collection Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 過去30日間のデータ収集
  python scripts/collect_historical_data.py --account 17841402015304577 --days 30

  # 指定期間のデータ収集
  python scripts/collect_historical_data.py --account 17841402015304577 --from 2024-01-01 --to 2024-12-31

  # 全投稿データ収集（メトリクス含む）
  python scripts/collect_historical_data.py --account 17841402015304577 --all-posts

  # メトリクスが欠損している投稿のメトリクスのみ収集
  python scripts/collect_historical_data.py --account 17841402015304577 --missing-metrics

  # 投稿データのみ収集（メトリクスなし）
  python scripts/collect_historical_data.py --account 17841402015304577 --days 30 --no-metrics

  # 最大100投稿まで
  python scripts/collect_historical_data.py --account 17841402015304577 --all-posts --max-posts 100

  # 詳細ログ出力
  python scripts/collect_historical_data.py --account 17841402015304577 --days 7 --verbose
        """
    )
    
    parser.add_argument(
        '--account',
        type=str,
        required=True,
        help='Instagram User ID (必須)',
        metavar='USER_ID'
    )
    
    # 期間指定オプション（排他的）
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--days',
        type=int,
        help='過去N日間のデータ収集',
        metavar='N'
    )
    
    date_group.add_argument(
        '--all-posts',
        action='store_true',
        help='全投稿データ収集'
    )
    
    date_group.add_argument(
        '--missing-metrics',
        action='store_true',
        help='メトリクス未取得投稿のメトリクスのみ収集'
    )
    
    parser.add_argument(
        '--from',
        dest='from_date',
        type=str,
        help='開始日付 (YYYY-MM-DD形式)',
        metavar='YYYY-MM-DD'
    )
    
    parser.add_argument(
        '--to',
        dest='to_date',
        type=str,
        help='終了日付 (YYYY-MM-DD形式)',
        metavar='YYYY-MM-DD'
    )
    
    parser.add_argument(
        '--max-posts',
        type=int,
        help='最大投稿数制限',
        metavar='N'
    )
    
    parser.add_argument(
        '--no-metrics',
        action='store_true',
        help='メトリクス取得をスキップ'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=50,
        help='バッチサイズ（デフォルト: 50）',
        metavar='N'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログ出力'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='結果をJSONファイルに出力',
        metavar='output.json'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライラン実行（API呼び出しのみ、データベース保存なし）'
    )
    
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='確認プロンプトをスキップ'
    )
    
    return parser.parse_args()

def validate_date(date_string: str) -> date:
    """日付文字列の検証"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD format.")

def setup_logging(verbose: bool):
    """ログレベル設定"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('app').setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled")

def calculate_date_range(args) -> tuple[Optional[date], Optional[date]]:
    """引数から日付範囲を計算"""
    start_date = None
    end_date = None
    
    if args.days:
        end_date = date.today()
        start_date = end_date - timedelta(days=args.days)
    elif args.from_date or args.to_date:
        if args.from_date:
            start_date = validate_date(args.from_date)
        if args.to_date:
            end_date = validate_date(args.to_date)
    elif args.all_posts:
        # 全投稿（日付制限なし）
        pass
    elif args.missing_metrics:
        # 過去30日間のメトリクス未取得投稿
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    else:
        # デフォルト: 過去7日間
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        logger.info("No date range specified, defaulting to last 7 days")
    
    return start_date, end_date

def estimate_duration(
    total_posts: Optional[int],
    include_metrics: bool,
    chunk_size: int
) -> str:
    """処理時間の見積もり"""
    if not total_posts:
        return "Unknown"
    
    # 基本処理時間（投稿あたり0.5秒）
    base_time = total_posts * 0.5
    
    # メトリクス取得時間（投稿あたり1秒）
    if include_metrics:
        base_time += total_posts * 1.0
    
    # チャンク間待機時間
    chunks = (total_posts + chunk_size - 1) // chunk_size
    chunk_delay = (chunks - 1) * 2  # チャンク間2秒待機
    
    total_seconds = base_time + chunk_delay
    
    if total_seconds < 60:
        return f"{total_seconds:.0f} seconds"
    elif total_seconds < 3600:
        return f"{total_seconds/60:.1f} minutes"
    else:
        return f"{total_seconds/3600:.1f} hours"

def print_collection_plan(args, start_date: Optional[date], end_date: Optional[date]):
    """収集計画の表示"""
    print("\n" + "="*60)
    print("📊 HISTORICAL DATA COLLECTION PLAN")
    print("="*60)
    
    print(f"🎯 Account: {args.account}")
    
    if args.missing_metrics:
        print(f"📋 Mode: Missing metrics collection")
        print(f"📅 Period: Last 30 days (metrics only)")
    elif args.all_posts:
        print(f"📋 Mode: All historical posts")
        print(f"📅 Period: All available data")
    else:
        print(f"📋 Mode: Historical posts + metrics")
        print(f"📅 Period: {start_date} to {end_date}")
    
    if args.max_posts:
        print(f"🔢 Max posts: {args.max_posts}")
    
    print(f"📦 Chunk size: {args.chunk_size}")
    print(f"📈 Include metrics: {not args.no_metrics and not args.missing_metrics}")
    
    if args.dry_run:
        print(f"🧪 Mode: DRY RUN (no database writes)")
    
    print("="*60)

def format_result_summary(result) -> dict:
    """結果サマリーの整形"""
    return {
        'account_id': result.account_id,
        'collection_type': result.collection_type,
        'date_range': {
            'start_date': result.start_date.isoformat() if result.start_date else None,
            'end_date': result.end_date.isoformat() if result.end_date else None
        },
        'statistics': {
            'total_items': result.total_items,
            'processed_items': result.processed_items,
            'success_items': result.success_items,
            'failed_items': result.failed_items,
            'success_rate': round(result.success_items / result.total_items * 100, 1) if result.total_items > 0 else 0
        },
        'timing': {
            'started_at': result.started_at.isoformat(),
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
            'duration_seconds': result.duration_seconds,
            'duration_formatted': format_duration(result.duration_seconds)
        },
        'error_message': result.error_message
    }

def format_duration(seconds: float) -> str:
    """秒数を読みやすい形式に変換"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def print_result_summary(result):
    """実行結果サマリーを表示"""
    print("\n" + "="*60)
    print("📊 HISTORICAL COLLECTION SUMMARY")
    print("="*60)
    
    print(f"🎯 Account: {result.account_id}")
    print(f"📋 Type: {result.collection_type}")
    print(f"⏱️  Duration: {format_duration(result.duration_seconds)}")
    print(f"📊 Total Items: {result.total_items}")
    print(f"✅ Processed: {result.processed_items}")
    print(f"🎉 Success: {result.success_items}")
    print(f"❌ Failed: {result.failed_items}")
    
    if result.total_items > 0:
        success_rate = (result.success_items / result.total_items) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if result.error_message:
        print(f"💥 Error: {result.error_message}")
    
    print("="*60)

async def main():
    """メイン処理"""
    args = parse_arguments()
    
    # ログレベル設定
    setup_logging(args.verbose)
    
    # 環境変数チェック
    required_env_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return 1
    
    logger.info("Starting Instagram historical data collection script")
    
    try:
        # データベース接続テスト
        logger.info("Testing database connection...")
        if not test_connection():
            logger.error("Database connection failed")
            return 1
        logger.info("Database connection successful")
        
        # 日付範囲計算
        start_date, end_date = calculate_date_range(args)
        
        # 収集計画表示
        print_collection_plan(args, start_date, end_date)
        
        # 確認プロンプト（ドライランでない場合）
        if not args.dry_run and not args.yes:
            response = input("\nProceed with historical data collection? (y/N): ")
            if response.lower() != 'y':
                print("Collection cancelled.")
                return 0
        
        # データ収集実行
        collector = create_historical_collector()
        
        if args.missing_metrics:
            logger.info("🚀 Starting missing metrics collection...")
            result = await collector.collect_missing_metrics(
                account_id=args.account,
                days_back=30
            )
        else:
            logger.info("🚀 Starting historical posts collection...")
            result = await collector.collect_historical_posts(
                account_id=args.account,
                start_date=start_date,
                end_date=end_date,
                max_posts=args.max_posts,
                include_metrics=not args.no_metrics,
                chunk_size=args.chunk_size
            )
        
        # 結果表示
        print_result_summary(result)
        
        # JSONファイル出力
        if args.output:
            output_data = format_result_summary(result)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {args.output}")
        
        # 失敗した場合は exit code 1
        if result.error_message or result.failed_items > 0:
            logger.warning(f"Collection completed with issues")
            return 1
        
        logger.info("Historical data collection completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Critical error in historical data collection: {str(e)}", exc_info=True)
        return 1

def cli_entry_point():
    """CLI エントリーポイント"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli_entry_point()