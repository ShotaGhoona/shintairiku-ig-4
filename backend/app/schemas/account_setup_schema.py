"""
Account Setup Schema
アカウントセットアップ用のPydanticスキーマ
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from .instagram_account_schema import InstagramAccountResponse


class AccountSetupRequest(BaseModel):
    """アカウントセットアップリクエストスキーマ"""
    app_id: str = Field(..., description="Instagram App ID", min_length=1)
    app_secret: str = Field(..., description="Instagram App Secret", min_length=1)
    short_token: str = Field(..., description="Instagram Short-lived Token", min_length=1)
    
    @validator('app_id')
    def validate_app_id(cls, v):
        """App IDのバリデーション"""
        if not v.isdigit():
            raise ValueError('App ID must be numeric')
        return v
    
    @validator('app_secret')
    def validate_app_secret(cls, v):
        """App Secretのバリデーション"""
        if len(v) < 16:
            raise ValueError('App Secret must be at least 16 characters')
        return v
    
    @validator('short_token')
    def validate_short_token(cls, v):
        """Short Tokenのバリデーション"""
        if len(v) < 50:
            raise ValueError('Short Token must be at least 50 characters')
        if not v.startswith('EAA'):
            raise ValueError('Short Token should start with EAA')
        return v


class DiscoveredAccount(BaseModel):
    """発見されたアカウント情報"""
    instagram_user_id: str = Field(..., description="Instagram User ID")
    username: str = Field(..., description="Instagram username")
    account_name: Optional[str] = Field(None, description="Account display name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    facebook_page_id: str = Field(..., description="Facebook Page ID")
    facebook_page_name: Optional[str] = Field(None, description="Facebook Page name")
    access_token: str = Field(..., description="Page access token")
    is_new: bool = Field(..., description="Whether this is a newly discovered account")


class AccountSetupResponse(BaseModel):
    """アカウントセットアップレスポンススキーマ"""
    success: bool = Field(..., description="Setup success status")
    message: str = Field(..., description="Response message")
    accounts_discovered: int = Field(0, description="Number of accounts discovered")
    accounts_created: int = Field(0, description="Number of new accounts created")
    accounts_updated: int = Field(0, description="Number of existing accounts updated")
    discovered_accounts: List[DiscoveredAccount] = Field(default_factory=list, description="List of discovered accounts")
    created_accounts: List[InstagramAccountResponse] = Field(default_factory=list, description="List of created accounts")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")
    
    @property
    def has_errors(self) -> bool:
        """エラーがあるかどうか"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """警告があるかどうか"""
        return len(self.warnings) > 0


class TokenExchangeResult(BaseModel):
    """トークン交換結果"""
    success: bool = Field(..., description="Token exchange success")
    long_term_token: Optional[str] = Field(None, description="Long-term access token")
    expires_in: Optional[int] = Field(None, description="Token expires in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class FacebookPageInfo(BaseModel):
    """Facebookページ情報"""
    page_id: str = Field(..., description="Facebook Page ID")
    page_name: str = Field(..., description="Facebook Page name")
    page_access_token: str = Field(..., description="Page access token")
    category: Optional[str] = Field(None, description="Page category")
    instagram_account_id: Optional[str] = Field(None, description="Connected Instagram account ID")


class InstagramAccountDetails(BaseModel):
    """Instagramアカウント詳細"""
    instagram_user_id: str = Field(..., description="Instagram User ID")
    username: Optional[str] = Field(None, description="Instagram username")
    name: Optional[str] = Field(None, description="Account display name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    biography: Optional[str] = Field(None, description="Account biography")
    website: Optional[str] = Field(None, description="Website URL")
    followers_count: Optional[int] = Field(None, description="Follower count")
    media_count: Optional[int] = Field(None, description="Media count")
    account_type: Optional[str] = Field(None, description="Account type")


class AccountSetupStep(BaseModel):
    """セットアップステップ情報"""
    step_name: str = Field(..., description="Step name")
    status: str = Field(..., description="Step status: pending, running, completed, failed")
    message: Optional[str] = Field(None, description="Step message")
    started_at: Optional[datetime] = Field(None, description="Step start time")
    completed_at: Optional[datetime] = Field(None, description="Step completion time")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'running', 'completed', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class AccountSetupProgress(BaseModel):
    """アカウントセットアップ進捗"""
    current_step: int = Field(0, description="Current step number")
    total_steps: int = Field(4, description="Total number of steps")
    steps: List[AccountSetupStep] = Field(default_factory=list, description="List of setup steps")
    overall_status: str = Field("pending", description="Overall status")
    started_at: Optional[datetime] = Field(None, description="Setup start time")
    completed_at: Optional[datetime] = Field(None, description="Setup completion time")
    
    @property
    def progress_percentage(self) -> float:
        """進捗率を計算"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
    
    @property
    def is_completed(self) -> bool:
        """完了しているかどうか"""
        return self.overall_status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """失敗しているかどうか"""
        return self.overall_status == "failed"