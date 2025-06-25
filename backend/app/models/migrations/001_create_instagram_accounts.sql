-- Migration: 001_create_instagram_accounts.sql
-- Description: Create instagram_accounts table
-- Created: 2025-06-25

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE instagram_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instagram_user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    account_name VARCHAR(200),
    profile_picture_url TEXT,
    access_token_encrypted TEXT NOT NULL,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    facebook_page_id VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_instagram_accounts_instagram_user_id ON instagram_accounts(instagram_user_id);
CREATE INDEX idx_instagram_accounts_active ON instagram_accounts(is_active) WHERE is_active = true;
CREATE INDEX idx_instagram_accounts_created_at ON instagram_accounts(created_at);

-- コメント
COMMENT ON TABLE instagram_accounts IS 'Instagram Business Account information';
COMMENT ON COLUMN instagram_accounts.instagram_user_id IS 'Instagram Business Account ID from Graph API';
COMMENT ON COLUMN instagram_accounts.access_token_encrypted IS 'Encrypted long-lived access token';
COMMENT ON COLUMN instagram_accounts.token_expires_at IS 'Access token expiration time (approximately 60 days)';
COMMENT ON COLUMN instagram_accounts.facebook_page_id IS 'Associated Facebook Page ID';
COMMENT ON COLUMN instagram_accounts.is_active IS 'Account active status for data collection';