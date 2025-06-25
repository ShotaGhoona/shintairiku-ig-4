// 年間分析用ダミーデータ

export interface MonthlyAnalytics {
  month: string;
  follower_count: number | null;
  following_count: number | null;
  reach: number;
  impressions: number;
  profile_views: number;
  website_clicks: number;
  likes: number;
  comments: number;
  saves: number;
  shares: number;
}

export const yearlyAnalyticsData: MonthlyAnalytics[] = [
  {
    month: "1月",
    follower_count: 8500,
    following_count: 1200,
    reach: 45000,
    impressions: 89000,
    profile_views: 3200,
    website_clicks: 450,
    likes: 2800,
    comments: 340,
    saves: 520,
    shares: 180
  },
  {
    month: "2月",
    follower_count: 8750,
    following_count: 1180,
    reach: 48000,
    impressions: 95000,
    profile_views: 3400,
    website_clicks: 520,
    likes: 3100,
    comments: 380,
    saves: 580,
    shares: 210
  },
  {
    month: "3月",
    follower_count: 9200,
    following_count: 1150,
    reach: 52000,
    impressions: 105000,
    profile_views: 3800,
    website_clicks: 680,
    likes: 3500,
    comments: 420,
    saves: 650,
    shares: 250
  },
  {
    month: "4月",
    follower_count: 9600,
    following_count: 1120,
    reach: 55000,
    impressions: 112000,
    profile_views: 4100,
    website_clicks: 750,
    likes: 3800,
    comments: 460,
    saves: 720,
    shares: 280
  },
  {
    month: "5月",
    follower_count: 10100,
    following_count: 1100,
    reach: 58000,
    impressions: 118000,
    profile_views: 4300,
    website_clicks: 820,
    likes: 4200,
    comments: 510,
    saves: 800,
    shares: 320
  },
  {
    month: "6月",
    follower_count: 10500,
    following_count: 1080,
    reach: 61000,
    impressions: 125000,
    profile_views: 4600,
    website_clicks: 890,
    likes: 4500,
    comments: 550,
    saves: 850,
    shares: 350
  },
  {
    month: "7月",
    follower_count: 11000,
    following_count: 1050,
    reach: 65000,
    impressions: 135000,
    profile_views: 5000,
    website_clicks: 950,
    likes: 4900,
    comments: 590,
    saves: 920,
    shares: 380
  },
  {
    month: "8月",
    follower_count: 11400,
    following_count: 1030,
    reach: 68000,
    impressions: 142000,
    profile_views: 5200,
    website_clicks: 1020,
    likes: 5200,
    comments: 620,
    saves: 980,
    shares: 420
  },
  {
    month: "9月",
    follower_count: 11800,
    following_count: 1010,
    reach: 70000,
    impressions: 148000,
    profile_views: 5400,
    website_clicks: 1100,
    likes: 5500,
    comments: 650,
    saves: 1050,
    shares: 450
  },
  {
    month: "10月",
    follower_count: 12300,
    following_count: 990,
    reach: 74000,
    impressions: 155000,
    profile_views: 5800,
    website_clicks: 1180,
    likes: 5900,
    comments: 690,
    saves: 1120,
    shares: 480
  },
  {
    month: "11月",
    follower_count: 12700,
    following_count: 970,
    reach: 77000,
    impressions: 162000,
    profile_views: 6100,
    website_clicks: 1250,
    likes: 6200,
    comments: 720,
    saves: 1180,
    shares: 510
  },
  {
    month: "12月",
    follower_count: 13200,
    following_count: 950,
    reach: 80000,
    impressions: 170000,
    profile_views: 6400,
    website_clicks: 1320,
    likes: 6600,
    comments: 760,
    saves: 1250,
    shares: 540
  }
];

export const yearlyMetrics = {
  totalGrowth: {
    followers: 4700,
    following: -250,
    reach: 35000,
    impressions: 81000
  },
  averageEngagement: {
    likes: 4883,
    comments: 563,
    saves: 886,
    shares: 365
  },
  bestMonth: {
    reach: "12月",
    engagement: "12月",
    growth: "7月"
  }
};