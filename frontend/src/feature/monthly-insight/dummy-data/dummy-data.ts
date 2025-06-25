// 月間分析用ダミーデータ

export interface DailyAnalytics {
  date: number;
  new_followers: number;
  impressions: number;
  reach: number;
  profile_views: number;
  website_clicks: number;
}

export const monthlyAnalyticsData: DailyAnalytics[] = [
  { date: 1, new_followers: 15, impressions: 2800, reach: 1850, profile_views: 180, website_clicks: 45 },
  { date: 2, new_followers: 23, impressions: 3200, reach: 2100, profile_views: 220, website_clicks: 52 },
  { date: 3, new_followers: 18, impressions: 2950, reach: 1920, profile_views: 195, website_clicks: 38 },
  { date: 4, new_followers: 32, impressions: 3800, reach: 2450, profile_views: 285, website_clicks: 68 },
  { date: 5, new_followers: 28, impressions: 3650, reach: 2350, profile_views: 265, website_clicks: 61 },
  { date: 6, new_followers: 19, impressions: 3100, reach: 2000, profile_views: 210, website_clicks: 43 },
  { date: 7, new_followers: 25, impressions: 3400, reach: 2200, profile_views: 240, website_clicks: 55 },
  { date: 8, new_followers: 41, impressions: 4200, reach: 2750, profile_views: 320, website_clicks: 78 },
  { date: 9, new_followers: 35, impressions: 3900, reach: 2580, profile_views: 295, website_clicks: 72 },
  { date: 10, new_followers: 22, impressions: 3300, reach: 2150, profile_views: 225, website_clicks: 48 },
  { date: 11, new_followers: 29, impressions: 3700, reach: 2400, profile_views: 270, website_clicks: 63 },
  { date: 12, new_followers: 38, impressions: 4100, reach: 2680, profile_views: 310, website_clicks: 75 },
  { date: 13, new_followers: 33, impressions: 3850, reach: 2520, profile_views: 285, website_clicks: 69 },
  { date: 14, new_followers: 26, impressions: 3500, reach: 2280, profile_views: 250, website_clicks: 58 },
  { date: 15, new_followers: 31, impressions: 3750, reach: 2450, profile_views: 275, website_clicks: 65 },
  { date: 16, new_followers: 44, impressions: 4400, reach: 2900, profile_views: 340, website_clicks: 82 },
  { date: 17, new_followers: 37, impressions: 4000, reach: 2620, profile_views: 300, website_clicks: 73 },
  { date: 18, new_followers: 24, impressions: 3400, reach: 2200, profile_views: 235, website_clicks: 51 },
  { date: 19, new_followers: 30, impressions: 3650, reach: 2380, profile_views: 265, website_clicks: 62 },
  { date: 20, new_followers: 42, impressions: 4300, reach: 2820, profile_views: 325, website_clicks: 79 },
  { date: 21, new_followers: 36, impressions: 3950, reach: 2580, profile_views: 290, website_clicks: 71 },
  { date: 22, new_followers: 27, impressions: 3550, reach: 2320, profile_views: 255, website_clicks: 59 },
  { date: 23, new_followers: 34, impressions: 3800, reach: 2480, profile_views: 280, website_clicks: 67 },
  { date: 24, new_followers: 39, impressions: 4150, reach: 2720, profile_views: 315, website_clicks: 76 },
  { date: 25, new_followers: 45, impressions: 4500, reach: 2950, profile_views: 350, website_clicks: 85 },
  { date: 26, new_followers: 28, impressions: 3600, reach: 2350, profile_views: 260, website_clicks: 60 },
  { date: 27, new_followers: 32, impressions: 3750, reach: 2450, profile_views: 275, website_clicks: 64 },
  { date: 28, new_followers: 40, impressions: 4200, reach: 2750, profile_views: 320, website_clicks: 77 },
  { date: 29, new_followers: 35, impressions: 3900, reach: 2550, profile_views: 295, website_clicks: 70 },
  { date: 30, new_followers: 29, impressions: 3650, reach: 2380, profile_views: 265, website_clicks: 61 },
  { date: 31, new_followers: 33, impressions: 3800, reach: 2480, profile_views: 280, website_clicks: 66 }
];

export const monthlyMetrics = {
  totalNewFollowers: monthlyAnalyticsData.reduce((sum, day) => sum + day.new_followers, 0),
  avgDailyImpressions: Math.round(monthlyAnalyticsData.reduce((sum, day) => sum + day.impressions, 0) / monthlyAnalyticsData.length),
  avgDailyReach: Math.round(monthlyAnalyticsData.reduce((sum, day) => sum + day.reach, 0) / monthlyAnalyticsData.length),
  totalProfileViews: monthlyAnalyticsData.reduce((sum, day) => sum + day.profile_views, 0),
  totalWebsiteClicks: monthlyAnalyticsData.reduce((sum, day) => sum + day.website_clicks, 0),
  bestDay: {
    followers: monthlyAnalyticsData.reduce((best, current) => 
      current.new_followers > best.new_followers ? current : best
    ),
    impressions: monthlyAnalyticsData.reduce((best, current) => 
      current.impressions > best.impressions ? current : best
    )
  }
};