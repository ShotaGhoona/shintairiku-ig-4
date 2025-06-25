-- Migration 005: Create instagram_monthly_stats table
-- Monthly statistics for Instagram accounts

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE instagram_monthly_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id) ON DELETE CASCADE,
    stats_month DATE NOT NULL, -- 月初日で記録（2025-06-01など）
    
    -- アカウント基本指標
    avg_followers_count INTEGER DEFAULT 0,
    avg_following_count INTEGER DEFAULT 0,
    
    -- 成長指標
    follower_growth INTEGER DEFAULT 0,
    follower_growth_rate DECIMAL(5,2) DEFAULT 0.0,
    
    -- 投稿・エンゲージメント指標
    total_posts INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_reach INTEGER DEFAULT 0,
    avg_engagement_rate DECIMAL(5,2) DEFAULT 0.0,
    
    -- 分析データ
    best_performing_day DATE,
    engagement_trend TEXT, -- JSON文字列
    content_performance TEXT, -- JSON文字列
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 制約: 1つのアカウントにつき1月1回の統計記録
    CONSTRAINT uq_account_monthly_stats UNIQUE (account_id, stats_month)
);

-- インデックス作成
CREATE INDEX idx_monthly_stats_account_id ON instagram_monthly_stats(account_id);
CREATE INDEX idx_monthly_stats_month ON instagram_monthly_stats(stats_month);
CREATE INDEX idx_monthly_stats_followers ON instagram_monthly_stats(avg_followers_count);
CREATE INDEX idx_monthly_stats_growth ON instagram_monthly_stats(follower_growth_rate);
CREATE INDEX idx_monthly_stats_engagement ON instagram_monthly_stats(avg_engagement_rate);

-- コメント追加
COMMENT ON TABLE instagram_monthly_stats IS 'Instagram アカウントの月次統計データ';
COMMENT ON COLUMN instagram_monthly_stats.account_id IS 'アカウントID（外部キー）';
COMMENT ON COLUMN instagram_monthly_stats.stats_month IS '統計月（月初日）';
COMMENT ON COLUMN instagram_monthly_stats.avg_followers_count IS '月平均フォロワー数';
COMMENT ON COLUMN instagram_monthly_stats.avg_following_count IS '月平均フォロー数';
COMMENT ON COLUMN instagram_monthly_stats.follower_growth IS '月間フォロワー成長数';
COMMENT ON COLUMN instagram_monthly_stats.follower_growth_rate IS 'フォロワー成長率（%）';
COMMENT ON COLUMN instagram_monthly_stats.total_posts IS '月間総投稿数';
COMMENT ON COLUMN instagram_monthly_stats.total_likes IS '月間総いいね数';
COMMENT ON COLUMN instagram_monthly_stats.total_comments IS '月間総コメント数';
COMMENT ON COLUMN instagram_monthly_stats.total_reach IS '月間総リーチ数';
COMMENT ON COLUMN instagram_monthly_stats.avg_engagement_rate IS '平均エンゲージメント率（%）';
COMMENT ON COLUMN instagram_monthly_stats.best_performing_day IS '最高パフォーマンス日';
COMMENT ON COLUMN instagram_monthly_stats.engagement_trend IS 'エンゲージメント傾向（JSON文字列）';
COMMENT ON COLUMN instagram_monthly_stats.content_performance IS 'コンテンツパフォーマンス（JSON文字列）';

-- データ確認用のビュー作成
CREATE VIEW monthly_stats_summary AS
SELECT 
    TO_CHAR(ms.stats_month, 'YYYY-MM') as month_year,
    acc.username,
    ms.avg_followers_count,
    ms.follower_growth,
    ms.follower_growth_rate,
    ms.total_posts,
    ms.total_likes,
    ms.total_comments,
    ms.total_reach,
    ms.avg_engagement_rate,
    ms.best_performing_day,
    ms.created_at
FROM instagram_monthly_stats ms
JOIN instagram_accounts acc ON ms.account_id = acc.id
ORDER BY ms.stats_month DESC, acc.username;

-- 年間成長率計算用の関数作成
CREATE OR REPLACE FUNCTION calculate_yoy_growth(
    p_account_id UUID,
    p_target_month DATE
) RETURNS TABLE (
    follower_growth_yoy DECIMAL(5,2),
    engagement_growth_yoy DECIMAL(5,2),
    posts_growth_yoy DECIMAL(5,2)
) AS $$
DECLARE
    current_stats RECORD;
    previous_stats RECORD;
BEGIN
    -- 当月データ取得
    SELECT * INTO current_stats
    FROM instagram_monthly_stats
    WHERE account_id = p_account_id 
    AND stats_month = DATE_TRUNC('month', p_target_month);
    
    -- 前年同月データ取得
    SELECT * INTO previous_stats
    FROM instagram_monthly_stats
    WHERE account_id = p_account_id 
    AND stats_month = DATE_TRUNC('month', p_target_month - INTERVAL '1 year');
    
    -- 成長率計算
    IF current_stats IS NULL OR previous_stats IS NULL THEN
        RETURN QUERY SELECT 0.0::DECIMAL(5,2), 0.0::DECIMAL(5,2), 0.0::DECIMAL(5,2);
    ELSE
        RETURN QUERY SELECT 
            CASE 
                WHEN previous_stats.avg_followers_count > 0 THEN
                    ROUND(((current_stats.avg_followers_count - previous_stats.avg_followers_count)::DECIMAL / previous_stats.avg_followers_count * 100), 2)
                ELSE 0.0
            END::DECIMAL(5,2),
            CASE 
                WHEN previous_stats.avg_engagement_rate > 0 THEN
                    ROUND(((current_stats.avg_engagement_rate - previous_stats.avg_engagement_rate) / previous_stats.avg_engagement_rate * 100), 2)
                ELSE 0.0
            END::DECIMAL(5,2),
            CASE 
                WHEN previous_stats.total_posts > 0 THEN
                    ROUND(((current_stats.total_posts - previous_stats.total_posts)::DECIMAL / previous_stats.total_posts * 100), 2)
                ELSE 0.0
            END::DECIMAL(5,2);
    END IF;
END;
$$ LANGUAGE plpgsql;