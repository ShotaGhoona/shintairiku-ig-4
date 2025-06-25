// Post Insight API Types
// APIレスポンスと一致する型定義

export interface PostInsightData {
  id: string;                    // instagram_post_id
  date: string;                  // posted_at (ISO format)
  thumbnail: string;             // thumbnail_url || media_url
  type: "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM" | "STORY"; // direct from media_type
  caption: string;               // post caption
  media_url: string;             // media URL
  permalink: string;             // post permalink
  
  // メトリクス
  reach: number;                 // metrics.reach
  likes: number;                 // metrics.likes
  comments: number;              // metrics.comments
  shares: number;                // metrics.shares
  saves: number;                 // metrics.saved
  views: number;                 // metrics.views
  total_interactions: number;    // calculated total
  engagement_rate: number;       // calculated (likes + comments + shares + saves) / reach * 100
  view_rate?: number;            // calculated for VIDEO (views / reach * 100)
  
  // 動画専用メトリクス
  video_view_total_time?: number; // for VIDEO
  avg_watch_time?: number;       // for VIDEO
  
  // CAROUSEL/STORY専用メトリクス
  follows?: number;              // for CAROUSEL_ALBUM, STORY
  profile_visits?: number;       // for CAROUSEL_ALBUM, STORY
  profile_activity?: number;     // for CAROUSEL_ALBUM, STORY
  
  recorded_at?: string;          // ISO format
}

export interface PostInsightSummary {
  total_posts: number;
  avg_engagement_rate: number;
  total_reach: number;
  total_engagement: number;
  best_performing_post?: {
    id: string;
    engagement_rate: number;
    type: string;
  };
  media_type_distribution: Record<string, number>;
}

export interface PostInsightMeta {
  account_id: string;
  instagram_user_id: string;
  username: string;
  total_posts: number;
  date_range: {
    from: string | null;
    to: string | null;
  };
  filters: {
    media_type: string | null;
    limit: number | null;
  };
}

export interface PostInsightResponse {
  posts: PostInsightData[];
  summary: PostInsightSummary;
  meta: PostInsightMeta;
}

// フィルター用の型
export type MediaType = "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM" | "STORY";
export const mediaTypes: MediaType[] = ["IMAGE", "VIDEO", "CAROUSEL_ALBUM", "STORY"];

// UI表示用の型（レガシーサポート）
export type ContentType = "All" | MediaType;
export const contentTypes: ContentType[] = ["All", ...mediaTypes];

// メディアタイプ検証関数
export const validateMediaType = (mediaType: string): MediaType => {
  return mediaTypes.includes(mediaType as MediaType) 
    ? (mediaType as MediaType) 
    : "IMAGE"; // デフォルト
};

// フィルター関数
export const getFilteredData = (data: PostInsightData[], type: ContentType): PostInsightData[] => {
  if (type === "All") return data;
  return data.filter(post => post.type === type);
};

// API リクエストパラメータ
export interface PostInsightParams {
  account_id: string;
  from_date?: string;  // YYYY-MM-DD format
  to_date?: string;    // YYYY-MM-DD format
  media_type?: MediaType;
  limit?: number;
}

// エラーレスポンス
export interface ApiError {
  detail: string;
  message?: string;
  status_code?: number;
}