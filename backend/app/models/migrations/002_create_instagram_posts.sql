-- Migration: 002_create_instagram_posts.sql
-- Description: Create instagram_posts table
-- Created: 2025-06-25

CREATE TABLE instagram_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id) ON DELETE CASCADE,
    instagram_post_id VARCHAR(50) UNIQUE NOT NULL,
    media_type VARCHAR(20) NOT NULL,
    caption TEXT,
    media_url TEXT,
    thumbnail_url TEXT,
    permalink TEXT,
    posted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_instagram_posts_account_id ON instagram_posts(account_id);
CREATE INDEX idx_instagram_posts_instagram_post_id ON instagram_posts(instagram_post_id);
CREATE INDEX idx_instagram_posts_account_posted ON instagram_posts(account_id, posted_at DESC);
CREATE INDEX idx_instagram_posts_media_type ON instagram_posts(account_id, media_type);
CREATE INDEX idx_instagram_posts_posted_at ON instagram_posts(posted_at DESC);

-- コメント
COMMENT ON TABLE instagram_posts IS 'Instagram post basic information';
COMMENT ON COLUMN instagram_posts.instagram_post_id IS 'Instagram post ID from Graph API';
COMMENT ON COLUMN instagram_posts.media_type IS 'Media type: VIDEO, CAROUSEL_ALBUM, IMAGE';
COMMENT ON COLUMN instagram_posts.media_url IS 'Media file URL';
COMMENT ON COLUMN instagram_posts.thumbnail_url IS 'Thumbnail URL (for videos)';
COMMENT ON COLUMN instagram_posts.permalink IS 'Instagram post URL';
COMMENT ON COLUMN instagram_posts.posted_at IS 'Post publication timestamp';