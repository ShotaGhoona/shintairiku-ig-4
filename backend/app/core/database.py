"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging
from typing import Generator

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数から DATABASE_URL を取得
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wxsgwvbdtpeidjpmdhte:shintairiku@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
)

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is required")

# SQLAlchemy エンジンの作成
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Supabase向けの設定
        echo=False,  # SQLログを出力したい場合はTrueに
        pool_pre_ping=True,  # 接続の健全性チェック
        pool_recycle=3600,   # 1時間で接続をリサイクル
        connect_args={
            "sslmode": "require",  # SSL接続を強制
            "connect_timeout": 10   # 接続タイムアウト
        }
    )
    logger.info(f"Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

# セッション作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得するジェネレーター
    FastAPI の Depends で使用
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")

def get_db_sync() -> Session:
    """
    同期処理用のデータベースセッション取得
    スクリプトやバックグラウンドタスクで使用
    """
    db = SessionLocal()
    try:
        logger.debug("Synchronous database session created")
        return db
    except Exception as e:
        logger.error(f"Failed to create synchronous database session: {str(e)}")
        db.close()
        raise

def test_connection() -> bool:
    """
    データベース接続をテスト
    Returns:
        bool: 接続成功時は True、失敗時は False
    """
    try:
        db = get_db_sync()
        # 簡単なクエリでテスト
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def create_tables():
    """
    全テーブルを作成
    主に開発・テスト環境で使用
    """
    try:
        # モデルをインポートしてテーブル作成
        from ..models.instagram_account import InstagramAccount
        from ..models.instagram_post import InstagramPost
        from ..models.instagram_post_metrics import InstagramPostMetrics
        from ..models.instagram_daily_stats import InstagramDailyStats
        from ..models.instagram_monthly_stats import InstagramMonthlyStats
        
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        raise

def drop_tables():
    """
    全テーブルを削除
    注意: 本番環境では使用しないこと
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        raise

# 環境変数の追加設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY]):
    logger.warning("Some Supabase environment variables are missing")

logger.info(f"Database configuration loaded - URL: {DATABASE_URL[:50]}...")