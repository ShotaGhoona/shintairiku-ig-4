-- Migration 004: Create instagram_daily_stats table
-- Daily statistics for Instagram accounts

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE instagram_daily_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id) ON DELETE CASCADE,
    stats_date DATE NOT NULL,
    
    -- アカウント基本指標
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    
    -- インサイト指標
    reach INTEGER DEFAULT 0,
    follower_count_change INTEGER DEFAULT 0,
    
    -- 投稿関連指標
    posts_count INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    
    -- 平均値
    avg_likes_per_post DECIMAL(10,2) DEFAULT 0.0,
    avg_comments_per_post DECIMAL(10,2) DEFAULT 0.0,
    
    -- メタデータ（JSON文字列として保存）
    data_sources TEXT,
    media_type_distribution TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 制約: 1つのアカウントにつき1日1回の統計記録
    CONSTRAINT uq_account_daily_stats UNIQUE (account_id, stats_date)
);

-- インデックス作成
CREATE INDEX idx_daily_stats_account_id ON instagram_daily_stats(account_id);
CREATE INDEX idx_daily_stats_date ON instagram_daily_stats(stats_date);
CREATE INDEX idx_daily_stats_followers ON instagram_daily_stats(followers_count);
CREATE INDEX idx_daily_stats_reach ON instagram_daily_stats(reach);

-- コメント追加
COMMENT ON TABLE instagram_daily_stats IS 'Instagram アカウントの日次統計データ';
COMMENT ON COLUMN instagram_daily_stats.account_id IS 'アカウントID（外部キー）';
COMMENT ON COLUMN instagram_daily_stats.stats_date IS '統計日付';
COMMENT ON COLUMN instagram_daily_stats.followers_count IS 'フォロワー数';
COMMENT ON COLUMN instagram_daily_stats.following_count IS 'フォロー数';
COMMENT ON COLUMN instagram_daily_stats.reach IS 'リーチ数';
COMMENT ON COLUMN instagram_daily_stats.follower_count_change IS 'フォロワー数変化';
COMMENT ON COLUMN instagram_daily_stats.posts_count IS '日次投稿数';
COMMENT ON COLUMN instagram_daily_stats.total_likes IS '総いいね数';
COMMENT ON COLUMN instagram_daily_stats.total_comments IS '総コメント数';
COMMENT ON COLUMN instagram_daily_stats.avg_likes_per_post IS '投稿あたり平均いいね数';
COMMENT ON COLUMN instagram_daily_stats.avg_comments_per_post IS '投稿あたり平均コメント数';
COMMENT ON COLUMN instagram_daily_stats.data_sources IS 'データソース（JSON文字列）';
COMMENT ON COLUMN instagram_daily_stats.media_type_distribution IS 'メディアタイプ分布（JSON文字列）';

-- データ確認用のビュー作成
CREATE VIEW daily_stats_summary AS
SELECT 
    ds.stats_date,
    acc.username,
    ds.followers_count,
    ds.follower_count_change,
    ds.posts_count,
    ds.total_likes,
    ds.total_comments,
    ds.reach,
    CASE 
        WHEN ds.posts_count > 0 THEN ROUND(ds.total_likes::DECIMAL / ds.posts_count, 2)
        ELSE 0 
    END as avg_likes_per_post_calculated,
    ds.created_at
FROM instagram_daily_stats ds
JOIN instagram_accounts acc ON ds.account_id = acc.id
ORDER BY ds.stats_date DESC, acc.username;