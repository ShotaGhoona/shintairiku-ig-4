"""
Instagram API Configuration
Instagram Graph API に関する設定とユーティリティ
"""
import os
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

# ログ設定
logger = logging.getLogger(__name__)

class InstagramConfig:
    """Instagram API 設定クラス"""
    
    # Instagram Graph API 設定
    BASE_URL = "https://graph.facebook.com"
    API_VERSION = "v23.0"
    
    # レート制限設定
    RATE_LIMIT_CALLS_PER_HOUR = 200  # 1時間あたりのAPI呼び出し制限
    RATE_LIMIT_SAFETY_MARGIN = 0.9   # 安全マージン（90%まで使用）
    
    # タイムアウト設定
    REQUEST_TIMEOUT_SECONDS = 30
    RETRY_MAX_ATTEMPTS = 3
    RETRY_DELAY_BASE = 60  # 秒
    
    # データ収集設定
    DEFAULT_POSTS_LIMIT = 25
    MAX_POSTS_LIMIT = 100
    INSIGHTS_MAX_PERIOD_DAYS = 93  # Insights API の最大期間
    
    # エラー処理設定
    CRITICAL_ERROR_CODES = [100, 190, 200]  # 致命的なエラーコード
    RETRY_ERROR_CODES = [1, 2, 4, 17, 341]  # リトライ可能なエラーコード
    
    def __init__(self):
        """設定の初期化"""
        self.facebook_app_id = os.getenv("FACEBOOK_APP_ID")
        self.facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET")
        
        # TODO: 暗号化実装時にはここで暗号化キーを取得
        # self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # 設定検証
        self._validate_config()
    
    def _validate_config(self) -> None:
        """設定の検証"""
        missing_vars = []
        
        if not self.facebook_app_id:
            missing_vars.append("FACEBOOK_APP_ID")
        if not self.facebook_app_secret:
            missing_vars.append("FACEBOOK_APP_SECRET")
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        else:
            logger.info("Instagram API configuration validated successfully")
    
    @property
    def api_base_url(self) -> str:
        """API ベースURL取得"""
        return f"{self.BASE_URL}/{self.API_VERSION}"
    
    def get_user_url(self, user_id: str) -> str:
        """ユーザー情報取得URL"""
        return f"{self.api_base_url}/{user_id}"
    
    def get_user_media_url(self, user_id: str) -> str:
        """ユーザーメディア取得URL"""
        return f"{self.api_base_url}/{user_id}/media"
    
    def get_user_insights_url(self, user_id: str) -> str:
        """ユーザーインサイト取得URL"""
        return f"{self.api_base_url}/{user_id}/insights"
    
    def get_media_insights_url(self, media_id: str) -> str:
        """メディアインサイト取得URL"""
        return f"{self.api_base_url}/{media_id}/insights"
    
    def get_common_headers(self) -> Dict[str, str]:
        """共通HTTPヘッダー"""
        return {
            "User-Agent": "Instagram-Analysis-App/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_default_params(self, access_token: str) -> Dict[str, str]:
        """デフォルトパラメータ"""
        return {
            "access_token": access_token
        }
    
    def get_basic_fields(self) -> str:
        """基本アカウント情報フィールド"""
        return "id,username,name,biography,website,profile_picture_url,followers_count,follows_count,media_count,is_published"
    
    def get_media_fields(self) -> str:
        """メディア情報フィールド"""
        return "id,media_type,caption,media_url,thumbnail_url,timestamp,permalink,username,like_count,comments_count,is_comment_enabled,shortcode"
    
    def get_available_insights_metrics(self) -> Dict[str, list]:
        """利用可能なインサイトメトリクス（検証済み）"""
        return {
            "account_metrics": [
                "follower_count",  # 日別フォロワー数変化
                "reach"           # 日別・週別リーチ数
            ],
            "media_metrics_all": [
                "likes",
                "comments", 
                "saved",
                "shares",
                "views",
                "reach",
                "total_interactions"
            ],
            "media_metrics_video": [
                "ig_reels_video_view_total_time",
                "ig_reels_avg_watch_time"
            ],
            "media_metrics_carousel": [
                "follows",
                "profile_visits",
                "profile_activity"
            ]
        }
    
    def get_unavailable_metrics(self) -> list:
        """取得不可能なメトリクス（検証済み）"""
        return [
            "impressions",        # v22以降廃止
            "profile_views",      # データなし
            "website_clicks",     # データなし
            "new_followers",      # 利用不可
            "accounts_engaged",   # データなし
            "total_interactions_account"  # アカウントレベルでは利用不可
        ]
    
    def calculate_rate_limit_delay(self, calls_made: int) -> int:
        """レート制限に基づく待機時間計算"""
        max_calls = int(self.RATE_LIMIT_CALLS_PER_HOUR * self.RATE_LIMIT_SAFETY_MARGIN)
        
        if calls_made >= max_calls:
            # 1時間待機
            return 3600
        elif calls_made >= max_calls * 0.8:
            # 80%を超えた場合は少し待機
            return 300
        else:
            return 0
    
    def is_critical_error(self, error_code: int) -> bool:
        """致命的エラーかどうか判定"""
        return error_code in self.CRITICAL_ERROR_CODES
    
    def is_retryable_error(self, error_code: int) -> bool:
        """リトライ可能エラーかどうか判定"""
        return error_code in self.RETRY_ERROR_CODES
    
    def get_retry_delay(self, attempt: int) -> int:
        """リトライ待機時間計算（指数バックオフ）"""
        return min(self.RETRY_DELAY_BASE * (2 ** (attempt - 1)), 3600)


# グローバル設定インスタンス
instagram_config = InstagramConfig()

# 設定値のエクスポート
API_BASE_URL = instagram_config.api_base_url
RATE_LIMIT_CALLS_PER_HOUR = instagram_config.RATE_LIMIT_CALLS_PER_HOUR
REQUEST_TIMEOUT = instagram_config.REQUEST_TIMEOUT_SECONDS

logger.info(f"Instagram configuration initialized - API URL: {API_BASE_URL}")