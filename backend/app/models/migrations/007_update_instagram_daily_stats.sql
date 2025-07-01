-- Migration: Update instagram_daily_stats table structure
-- Date: 2025-07-01
-- Purpose: Simplify table structure based on API test results

-- Add new column
ALTER TABLE instagram_daily_stats ADD COLUMN IF NOT EXISTS media_count INTEGER DEFAULT 0;

-- Remove columns that are no longer needed (if they exist)
ALTER TABLE instagram_daily_stats DROP COLUMN IF EXISTS reach;
ALTER TABLE instagram_daily_stats DROP COLUMN IF EXISTS follower_count_change;
ALTER TABLE instagram_daily_stats DROP COLUMN IF EXISTS avg_likes_per_post;
ALTER TABLE instagram_daily_stats DROP COLUMN IF EXISTS avg_comments_per_post;

-- Update column comments for clarity
COMMENT ON COLUMN instagram_daily_stats.media_count IS 'Total number of posts by the account';
COMMENT ON COLUMN instagram_daily_stats.posts_count IS 'Number of posts made on this specific date';
COMMENT ON COLUMN instagram_daily_stats.total_likes IS 'Total likes on posts made on this specific date';
COMMENT ON COLUMN instagram_daily_stats.total_comments IS 'Total comments on posts made on this specific date';