"""
Error Handler
エラーハンドリングとリトライロジック
"""

import logging
import asyncio
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    async def retry_with_backoff(
        self, 
        func: Callable, 
        *args, 
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """指数バックオフによるリトライ実行"""
        
        retries = max_retries or self.max_retries
        
        for attempt in range(retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                if attempt == retries:
                    logger.error(f"Function {func.__name__} failed after {retries} retries: {e}")
                    raise
                
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
    
    def handle_api_error(self, error: Exception, context: str = "") -> str:
        """API エラーの分類と処理"""
        
        error_msg = str(error)
        error_type = type(error).__name__
        
        # Instagram API特有のエラーパターン
        if "OAuthException" in error_msg:
            if "access token" in error_msg.lower():
                return f"Access token error in {context}: {error_msg}"
            elif "rate limit" in error_msg.lower():
                return f"Rate limit exceeded in {context}: {error_msg}"
            else:
                return f"OAuth error in {context}: {error_msg}"
        
        elif "ConnectionError" in error_type:
            return f"Network connection error in {context}: {error_msg}"
        
        elif "TimeoutError" in error_type:
            return f"Request timeout in {context}: {error_msg}"
        
        elif "JSONDecodeError" in error_type:
            return f"Invalid API response in {context}: {error_msg}"
        
        else:
            return f"Unexpected error in {context}: {error_type} - {error_msg}"
    
    def should_retry_error(self, error: Exception) -> bool:
        """エラーがリトライ対象かどうか判定"""
        
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # リトライすべきエラー
        retry_patterns = [
            "timeout",
            "connection",
            "network",
            "temporarily unavailable",
            "rate limit"
        ]
        
        # リトライしないエラー
        no_retry_patterns = [
            "invalid token",
            "permission denied",
            "not found",
            "invalid parameter"
        ]
        
        # リトライしないエラーパターンをチェック
        for pattern in no_retry_patterns:
            if pattern in error_msg:
                return False
        
        # リトライするエラーパターンをチェック
        for pattern in retry_patterns:
            if pattern in error_msg:
                return True
        
        # デフォルトでは一部の例外タイプのみリトライ
        return error_type in [
            "ConnectionError",
            "TimeoutError", 
            "aiohttp.ClientError",
            "requests.exceptions.RequestException"
        ]

def handle_errors(max_retries: int = 3, base_delay: float = 1.0):
    """エラーハンドリングデコレータ"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = ErrorHandler(max_retries, base_delay)
            
            try:
                return await error_handler.retry_with_backoff(func, *args, **kwargs)
            except Exception as e:
                error_msg = error_handler.handle_api_error(e, func.__name__)
                logger.error(error_msg)
                raise
        
        return wrapper
    return decorator