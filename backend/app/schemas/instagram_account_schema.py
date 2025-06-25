"""
Instagram Account Schema
InstagramAccount モデル用のPydanticスキーマ
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class InstagramAccountBase(BaseModel):
    """Instagram アカウント基底スキーマ"""
    instagram_user_id: str = Field(..., description="Instagram Business Account ID")
    username: str = Field(..., min_length=1, max_length=100, description="Instagram username")
    account_name: Optional[str] = Field(None, max_length=200, description="Account display name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    facebook_page_id: Optional[str] = Field(None, max_length=50, description="Associated Facebook Page ID")
    is_active: bool = Field(True, description="Account active status")


class InstagramAccountCreate(InstagramAccountBase):
    """Instagram アカウント作成スキーマ"""
    access_token_encrypted: str = Field(..., description="Encrypted long-lived access token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    
    @validator('username')
    def validate_username(cls, v):
        """ユーザーネームのバリデーション"""
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, dots, and underscores')
        return v.lower()
    
    @validator('instagram_user_id')
    def validate_instagram_user_id(cls, v):
        """Instagram User ID のバリデーション"""
        if not v.isdigit():
            raise ValueError('Instagram User ID must be numeric')
        return v


class InstagramAccountUpdate(BaseModel):
    """Instagram アカウント更新スキーマ"""
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    account_name: Optional[str] = Field(None, max_length=200)
    profile_picture_url: Optional[str] = None
    access_token_encrypted: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    facebook_page_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not v.replace('_', '').replace('.', '').isalnum():
                raise ValueError('Username must contain only alphanumeric characters, dots, and underscores')
            return v.lower()
        return v


class InstagramAccountResponse(InstagramAccountBase):
    """Instagram アカウント応答スキーマ"""
    id: uuid.UUID = Field(..., description="Account UUID")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    created_at: datetime = Field(..., description="Account creation time")
    updated_at: datetime = Field(..., description="Last update time")
    
    # Header用の追加フィールド
    is_token_valid: bool = Field(..., description="Token validity status")
    days_until_expiry: Optional[int] = Field(None, description="Days until token expires")
    
    class Config:
        from_attributes = True


class InstagramAccountBasicInfo(BaseModel):
    """Instagram アカウント基本情報スキーマ（APIレスポンス用）"""
    id: uuid.UUID
    username: str
    account_name: Optional[str]
    profile_picture_url: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class InstagramAccountWithStats(InstagramAccountResponse):
    """Instagram アカウント統計付きスキーマ"""
    latest_follower_count: Optional[int] = Field(None, description="Latest follower count")
    latest_following_count: Optional[int] = Field(None, description="Latest following count")
    total_posts: Optional[int] = Field(None, description="Total posts count")
    data_quality_score: Optional[float] = Field(None, description="Data collection quality score")
    last_synced_at: Optional[datetime] = Field(None, description="Last sync time")


class AccountListResponse(BaseModel):
    """アカウント一覧レスポンススキーマ"""
    accounts: list[InstagramAccountWithStats] = Field(..., description="Account list")
    total: int = Field(..., description="Total number of accounts")
    active_count: int = Field(..., description="Number of active accounts")
    
    class Config:
        from_attributes = True


class AccountDetailResponse(InstagramAccountWithStats):
    """アカウント詳細レスポンススキーマ"""
    facebook_page_id: Optional[str] = Field(None, description="Facebook Page ID")
    
    class Config:
        from_attributes = True


class TokenUpdateRequest(BaseModel):
    """トークン更新リクエストスキーマ"""
    access_token: str = Field(..., description="New access token (will be encrypted)")
    expires_in: Optional[int] = Field(None, description="Token expires in seconds")


class TokenValidationResponse(BaseModel):
    """トークン検証応答スキーマ"""
    account_id: uuid.UUID = Field(..., description="Account ID")
    is_valid: bool = Field(..., description="Token validity status")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    days_until_expiry: Optional[int] = Field(None, description="Days until token expires")
    warning_level: str = Field(..., description="Warning level: none, warning, critical, expired")
    needs_refresh: bool = Field(False, description="Whether token needs refresh")
    
    @validator('warning_level')
    def validate_warning_level(cls, v):
        allowed_levels = ['none', 'warning', 'critical', 'expired']
        if v not in allowed_levels:
            raise ValueError(f'Warning level must be one of: {", ".join(allowed_levels)}')
        return v


class AccountActivationRequest(BaseModel):
    """アカウント有効化リクエストスキーマ"""
    is_active: bool = Field(..., description="Active status to set")
    reason: Optional[str] = Field(None, description="Reason for status change")


class BulkAccountOperation(BaseModel):
    """一括アカウント操作スキーマ"""
    account_ids: list[uuid.UUID] = Field(..., description="List of account IDs")
    operation: str = Field(..., description="Operation type: activate, deactivate, refresh_tokens")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'refresh_tokens']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v


class AccountSummary(BaseModel):
    """アカウント概要スキーマ"""
    total_accounts: int = Field(..., description="Total number of accounts")
    active_accounts: int = Field(..., description="Number of active accounts")
    inactive_accounts: int = Field(..., description="Number of inactive accounts")
    tokens_expiring_soon: int = Field(..., description="Number of tokens expiring within 7 days")
    avg_data_quality: Optional[float] = Field(None, description="Average data quality score")


class AccountConnectionTest(BaseModel):
    """アカウント接続テストスキーマ"""
    account_id: uuid.UUID = Field(..., description="Account ID to test")
    test_basic_info: bool = Field(True, description="Test basic account info retrieval")
    test_insights: bool = Field(True, description="Test insights API access")
    test_posts: bool = Field(True, description="Test posts data access")


class AccountConnectionTestResult(BaseModel):
    """アカウント接続テスト結果スキーマ"""
    account_id: uuid.UUID
    overall_status: str = Field(..., description="Overall connection status: success, partial, failed")
    basic_info_status: str = Field(..., description="Basic info test status")
    insights_status: str = Field(..., description="Insights API test status") 
    posts_status: str = Field(..., description="Posts data test status")
    error_messages: list[str] = Field(default_factory=list, description="Error messages if any")
    api_calls_used: int = Field(0, description="Number of API calls used in test")
    
    @validator('overall_status', 'basic_info_status', 'insights_status', 'posts_status')
    def validate_status(cls, v):
        allowed_statuses = ['success', 'failed', 'not_tested']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v