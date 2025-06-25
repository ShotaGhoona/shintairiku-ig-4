-- Migration 006: Insert Story dummy data for testing
-- Add 2 story posts and their metrics for testing purposes

-- Insert Story posts
INSERT INTO instagram_posts (
    id,
    account_id,
    instagram_post_id,
    media_type,
    caption,
    media_url,
    thumbnail_url,
    permalink,
    posted_at,
    created_at
) VALUES 
(
    gen_random_uuid(),
    '6d7ce798-c83a-4ca6-a5a0-b5c099c7cb99',
    'story_dummy_001',
    'STORY',
    'ストーリー投稿テスト1: 日常の一コマをシェア',
    'https://example.com/story1.jpg',
    'https://example.com/story1_thumb.jpg',
    'https://instagram.com/stories/holz_bauhaus/story_dummy_001',
    '2025-06-25 08:00:00+00:00',
    NOW()
),
(
    gen_random_uuid(),
    '6d7ce798-c83a-4ca6-a5a0-b5c099c7cb99',
    'story_dummy_002',
    'STORY',
    'ストーリー投稿テスト2: 制作過程のタイムラプス',
    'https://example.com/story2.mp4',
    'https://example.com/story2_thumb.jpg',
    'https://instagram.com/stories/holz_bauhaus/story_dummy_002',
    '2025-06-25 12:00:00+00:00',
    NOW()
);

-- Insert metrics for story posts
-- Story 1 metrics
INSERT INTO instagram_post_metrics (
    id,
    post_id,
    likes,
    comments,
    saved,
    shares,
    views,
    reach,
    total_interactions,
    follows,
    profile_visits,
    profile_activity,
    video_view_total_time,
    avg_watch_time,
    engagement_rate,
    recorded_at
) VALUES (
    gen_random_uuid(),
    (SELECT id FROM instagram_posts WHERE instagram_post_id = 'story_dummy_001'),
    0,  -- Stories don't have likes
    0,  -- Stories don't have comments
    8,  -- Story saves
    12, -- Story shares
    145, -- Story views
    120, -- Story reach
    20,  -- Total interactions (shares + saves)
    2,   -- Follows from story
    15,  -- Profile visits
    8,   -- Profile activity
    0,   -- No video time for image story
    0,   -- No avg watch time
    16.67, -- Engagement rate: (20/120)*100
    '2025-06-25 00:00:00+00:00'
);

-- Story 2 metrics (video story)
INSERT INTO instagram_post_metrics (
    id,
    post_id,
    likes,
    comments,
    saved,
    shares,
    views,
    reach,
    total_interactions,
    follows,
    profile_visits,
    profile_activity,
    video_view_total_time,
    avg_watch_time,
    engagement_rate,
    recorded_at
) VALUES (
    gen_random_uuid(),
    (SELECT id FROM instagram_posts WHERE instagram_post_id = 'story_dummy_002'),
    0,   -- Stories don't have likes
    0,   -- Stories don't have comments
    15,  -- Story saves
    8,   -- Story shares
    95,  -- Story views
    78,  -- Story reach
    23,  -- Total interactions (shares + saves)
    1,   -- Follows from story
    12,  -- Profile visits
    6,   -- Profile activity
    4560000, -- Video view time in milliseconds (4.56 seconds total)
    48000,   -- Average watch time per view (48ms per view)
    29.49,   -- Engagement rate: (23/78)*100
    '2025-06-25 00:00:00+00:00'
);

-- Verify insertion
SELECT 
    p.instagram_post_id,
    p.media_type,
    p.caption,
    p.posted_at,
    m.views,
    m.reach,
    m.shares,
    m.saved,
    m.engagement_rate
FROM instagram_posts p
LEFT JOIN instagram_post_metrics m ON p.id = m.post_id
WHERE p.media_type = 'STORY'
ORDER BY p.posted_at DESC;