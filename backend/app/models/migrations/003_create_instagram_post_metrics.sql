-- Migration: 003_create_instagram_post_metrics.sql
-- Description: Create instagram_post_metrics table
-- Created: 2025-06-25

CREATE TABLE instagram_post_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES instagram_posts(id) ON DELETE CASCADE,
    
    -- 全メディア共通メトリクス（✅取得可能）
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    saved INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    total_interactions INTEGER DEFAULT 0,
    
    -- CAROUSEL専用メトリクス（✅取得可能）
    follows INTEGER DEFAULT 0,
    profile_visits INTEGER DEFAULT 0,
    profile_activity INTEGER DEFAULT 0,
    
    -- VIDEO専用メトリクス（✅取得可能）
    video_view_total_time BIGINT DEFAULT 0,
    avg_watch_time INTEGER DEFAULT 0,
    
    -- 計算値
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス: 1つの投稿につき1日1回のメトリクス記録（アプリケーションレベルで制御）

-- インデックス
CREATE INDEX idx_instagram_post_metrics_post_id ON instagram_post_metrics(post_id);
CREATE INDEX idx_instagram_post_metrics_recorded_at ON instagram_post_metrics(recorded_at DESC);
CREATE INDEX idx_instagram_post_metrics_engagement_rate ON instagram_post_metrics(engagement_rate DESC);
CREATE INDEX idx_instagram_post_metrics_likes ON instagram_post_metrics(likes DESC);
CREATE INDEX idx_instagram_post_metrics_reach ON instagram_post_metrics(reach DESC);

-- コメント
COMMENT ON TABLE instagram_post_metrics IS 'Instagram post performance metrics (API verified data only)';
COMMENT ON COLUMN instagram_post_metrics.likes IS 'Number of likes';
COMMENT ON COLUMN instagram_post_metrics.comments IS 'Number of comments';
COMMENT ON COLUMN instagram_post_metrics.saved IS 'Number of saves (API field: saved)';
COMMENT ON COLUMN instagram_post_metrics.shares IS 'Number of shares';
COMMENT ON COLUMN instagram_post_metrics.views IS 'Number of views';
COMMENT ON COLUMN instagram_post_metrics.reach IS 'Number of unique accounts reached';
COMMENT ON COLUMN instagram_post_metrics.total_interactions IS 'Total interactions';
COMMENT ON COLUMN instagram_post_metrics.follows IS 'Follows from this post (CAROUSEL only)';
COMMENT ON COLUMN instagram_post_metrics.profile_visits IS 'Profile visits from this post (CAROUSEL only)';
COMMENT ON COLUMN instagram_post_metrics.profile_activity IS 'Profile activity from this post (CAROUSEL only)';
COMMENT ON COLUMN instagram_post_metrics.video_view_total_time IS 'Total video view time in milliseconds (VIDEO only)';
COMMENT ON COLUMN instagram_post_metrics.avg_watch_time IS 'Average watch time in milliseconds (VIDEO only)';
COMMENT ON COLUMN instagram_post_metrics.engagement_rate IS 'Calculated engagement rate: (likes+comments+saved+shares)/reach*100';