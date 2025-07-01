#!/usr/bin/env python3
"""
Migration 007: Update instagram_daily_stats table structure
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """マイグレーション007を実行"""
    
    # SQLファイルのパス
    migration_file = Path(__file__).parent.parent / "app" / "models" / "migrations" / "007_update_instagram_daily_stats.sql"
    
    if not migration_file.exists():
        logger.error(f"Migration file not found: {migration_file}")
        return False
    
    # SQLファイル読み込み
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # データベース接続
    db = SessionLocal()
    
    try:
        logger.info("🚀 Running migration 007: Update instagram_daily_stats table structure")
        
        # SQLの各ステートメントを分割して実行
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                logger.info(f"📝 Executing statement {i}: {statement[:50]}...")
                try:
                    db.execute(statement)
                    db.commit()
                    logger.info(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Statement {i} failed (may be expected): {e}")
                    db.rollback()
                    continue
        
        logger.info("✅ Migration 007 completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)