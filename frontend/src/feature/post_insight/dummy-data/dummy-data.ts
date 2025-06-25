// 投稿インサイト用ダミーデータ

export interface PostInsight {
  id: string;
  date: string;
  thumbnail: string;
  type: "Story" | "Feed" | "Reels";
  reach: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  engagement_rate: number;
  view_rate?: number; // Reelsのみ
}

export const postInsightsData: PostInsight[] = [
  {
    id: "1",
    date: "2024-12-01",
    thumbnail: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop",
    type: "Feed",
    reach: 2500,
    likes: 189,
    comments: 23,
    shares: 12,
    saves: 45,
    engagement_rate: 10.8,
    view_rate: undefined
  },
  {
    id: "2", 
    date: "2024-12-02",
    thumbnail: "https://images.unsplash.com/photo-1445205170230-053b83016050?w=100&h=100&fit=crop",
    type: "Reels",
    reach: 8500,
    likes: 456,
    comments: 78,
    shares: 34,
    saves: 89,
    engagement_rate: 7.7,
    view_rate: 65.3
  },
  {
    id: "3",
    date: "2024-12-02",
    thumbnail: "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=100&h=100&fit=crop",
    type: "Story",
    reach: 1800,
    likes: 0,
    comments: 0,
    shares: 8,
    saves: 0,
    engagement_rate: 0.4,
    view_rate: 78.9
  },
  {
    id: "4",
    date: "2024-12-03",
    thumbnail: "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=100&h=100&fit=crop",
    type: "Feed",
    reach: 3200,
    likes: 245,
    comments: 31,
    shares: 18,
    saves: 67,
    engagement_rate: 11.3,
    view_rate: undefined
  },
  {
    id: "5",
    date: "2024-12-04",
    thumbnail: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=100&h=100&fit=crop",
    type: "Reels",
    reach: 12000,
    likes: 678,
    comments: 92,
    shares: 45,
    saves: 123,
    engagement_rate: 7.8,
    view_rate: 58.2
  },
  {
    id: "6",
    date: "2024-12-05",
    thumbnail: "https://images.unsplash.com/photo-1460306855393-0410f61241c7?w=100&h=100&fit=crop",
    type: "Story",
    reach: 2100,
    likes: 0,
    comments: 0,
    shares: 12,
    saves: 0,
    engagement_rate: 0.6,
    view_rate: 82.1
  },
  {
    id: "7",
    date: "2024-12-06",
    thumbnail: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=100&h=100&fit=crop",
    type: "Feed",
    reach: 2800,
    likes: 201,
    comments: 28,
    shares: 15,
    saves: 52,
    engagement_rate: 10.6,
    view_rate: undefined
  },
  {
    id: "8",
    date: "2024-12-07",
    thumbnail: "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=100&h=100&fit=crop",
    type: "Reels",
    reach: 9800,
    likes: 523,
    comments: 67,
    shares: 29,
    saves: 98,
    engagement_rate: 7.3,
    view_rate: 62.8
  },
  {
    id: "9",
    date: "2024-12-08",
    thumbnail: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop",
    type: "Story",
    reach: 1950,
    likes: 0,
    comments: 0,
    shares: 9,
    saves: 0,
    engagement_rate: 0.5,
    view_rate: 75.6
  },
  {
    id: "10",
    date: "2024-12-09",
    thumbnail: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=100&h=100&fit=crop",
    type: "Feed",
    reach: 3500,
    likes: 278,
    comments: 35,
    shares: 21,
    saves: 71,
    engagement_rate: 11.6,
    view_rate: undefined
  },
  {
    id: "11",
    date: "2024-12-10",
    thumbnail: "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=100&h=100&fit=crop",
    type: "Reels",
    reach: 11500,
    likes: 634,
    comments: 84,
    shares: 38,
    saves: 112,
    engagement_rate: 7.5,
    view_rate: 59.7
  },
  {
    id: "12",
    date: "2024-12-11",
    thumbnail: "https://images.unsplash.com/photo-1493770348161-369560ae357d?w=100&h=100&fit=crop",
    type: "Story",
    reach: 2200,
    likes: 0,
    comments: 0,
    shares: 11,
    saves: 0,
    engagement_rate: 0.5,
    view_rate: 79.3
  },
  {
    id: "13",
    date: "2024-12-12",
    thumbnail: "https://images.unsplash.com/photo-1543362906-acfc16c67564?w=100&h=100&fit=crop",
    type: "Feed",
    reach: 2900,
    likes: 221,
    comments: 29,
    shares: 16,
    saves: 58,
    engagement_rate: 11.2,
    view_rate: undefined
  },
  {
    id: "14",
    date: "2024-12-13",
    thumbnail: "https://images.unsplash.com/photo-1464454709131-ffd692591ee5?w=100&h=100&fit=crop",
    type: "Reels",
    reach: 10200,
    likes: 567,
    comments: 73,
    shares: 32,
    saves: 101,
    engagement_rate: 7.6,
    view_rate: 61.4
  },
  {
    id: "15",
    date: "2024-12-14",
    thumbnail: "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=100&h=100&fit=crop",
    type: "Story",
    reach: 1850,
    likes: 0,
    comments: 0,
    shares: 7,
    saves: 0,
    engagement_rate: 0.4,
    view_rate: 76.8
  }
];

export const contentTypes = ["All", "Story", "Feed", "Reels"] as const;
export type ContentType = typeof contentTypes[number];

export const getFilteredData = (data: PostInsight[], type: ContentType) => {
  if (type === "All") return data;
  return data.filter(post => post.type === type);
};

export const postMetrics = {
  totalPosts: postInsightsData.length,
  avgEngagementRate: Math.round((postInsightsData.reduce((sum, post) => sum + post.engagement_rate, 0) / postInsightsData.length) * 10) / 10,
  totalReach: postInsightsData.reduce((sum, post) => sum + post.reach, 0),
  totalEngagement: postInsightsData.reduce((sum, post) => sum + post.likes + post.comments + post.shares + post.saves, 0),
  bestPerformingPost: postInsightsData.reduce((best, current) => 
    current.engagement_rate > best.engagement_rate ? current : best
  )
};