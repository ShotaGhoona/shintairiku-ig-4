// Post Insight API Client
// バックエンドAPIとの通信を担当

import { PostInsightResponse, PostInsightParams, ApiError } from '../types/postInsight';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class PostInsightApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 投稿インサイトデータを取得
   */
  async getPostInsights(params: PostInsightParams): Promise<PostInsightResponse> {
    try {
      const url = new URL(`${this.baseUrl}/api/v1/posts/insights`);
      
      // クエリパラメータを追加
      url.searchParams.append('account_id', params.account_id);
      
      if (params.from_date) {
        url.searchParams.append('from_date', params.from_date);
      }
      
      if (params.to_date) {
        url.searchParams.append('to_date', params.to_date);
      }
      
      if (params.media_type) {
        url.searchParams.append('media_type', params.media_type);
      }
      
      if (params.limit) {
        url.searchParams.append('limit', params.limit.toString());
      }

      console.log('API Request URL:', url.toString());

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        // エラーレスポンスの詳細を取得
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data: PostInsightResponse = await response.json();
      console.log('API Response received:', { 
        postsCount: data.posts.length, 
        summary: data.summary,
        meta: data.meta 
      });
      
      return data;
      
    } catch (error) {
      console.error('Post Insight API Error:', error);
      
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('Unknown error occurred while fetching post insights');
      }
    }
  }

  /**
   * アカウント有効性チェック（簡易版）
   */
  async checkAccountAvailability(accountId: string): Promise<boolean> {
    try {
      // 少量のデータで接続テスト
      await this.getPostInsights({ 
        account_id: accountId, 
        limit: 1 
      });
      return true;
    } catch (error) {
      console.warn('Account availability check failed:', error);
      return false;
    }
  }

  /**
   * 利用可能なメディアタイプを取得（統計から推測）
   */
  async getAvailableMediaTypes(accountId: string): Promise<string[]> {
    try {
      const data = await this.getPostInsights({ 
        account_id: accountId,
        limit: 100  // サンプルサイズ
      });
      
      const mediaTypes = Object.keys(data.summary.media_type_distribution);
      return mediaTypes.sort();
      
    } catch (error) {
      console.warn('Failed to get available media types:', error);
      return ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']; // デフォルト
    }
  }
}

// シングルトンインスタンス
export const postInsightApi = new PostInsightApiClient();

// 名前付きエクスポート（テスト用）
export { PostInsightApiClient };

// デフォルトエクスポート
export default postInsightApi;