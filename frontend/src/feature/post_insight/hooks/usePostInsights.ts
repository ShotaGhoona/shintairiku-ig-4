// Post Insights Custom Hook
// データフェッチング・状態管理・エラーハンドリング

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { PostInsightResponse, PostInsightParams, PostInsightData, MediaType } from '../types/postInsight';
import { postInsightApi } from '../services/postInsightApi';

interface UsePostInsightsState {
  data: PostInsightResponse | null;
  posts: PostInsightData[];
  loading: boolean;
  error: string | null;
  lastFetched: Date | null;
}

interface UsePostInsightsOptions {
  // 自動フェッチ設定
  autoFetch?: boolean;
  // キャッシュ時間（ミリ秒）
  cacheTime?: number;
  // リトライ設定
  retryCount?: number;
  retryDelay?: number;
}

interface UsePostInsightsReturn extends UsePostInsightsState {
  // データフェッチ関数
  fetchData: (params?: Partial<PostInsightParams>) => Promise<void>;
  
  // フィルタリング関数
  filterByMediaType: (mediaType: MediaType | 'All') => PostInsightData[];
  
  // リフレッシュ関数
  refresh: () => Promise<void>;
  
  // エラークリア
  clearError: () => void;
  
  // ローディング状態操作
  setLoading: (loading: boolean) => void;
}

const DEFAULT_OPTIONS: UsePostInsightsOptions = {
  autoFetch: true,
  cacheTime: 5 * 60 * 1000, // 5分
  retryCount: 3,
  retryDelay: 1000, // 1秒
};

export function usePostInsights(
  initialParams: PostInsightParams,
  options: UsePostInsightsOptions = {}
): UsePostInsightsReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  const [state, setState] = useState<UsePostInsightsState>({
    data: null,
    posts: [],
    loading: false,
    error: null,
    lastFetched: null,
  });

  // 現在のパラメータ状態
  const [currentParams, setCurrentParams] = useState<PostInsightParams>(initialParams);
  const currentParamsRef = useRef<PostInsightParams>(currentParams);
  const hasFetchedRef = useRef<boolean>(false);

  // データフェッチ関数（リトライ機能付き）
  const fetchData = useCallback(async (
    params?: Partial<PostInsightParams>,
    retryCount = opts.retryCount || 0
  ): Promise<void> => {
    const fetchParams = { ...currentParamsRef.current, ...params };

    // account_idが空の場合は処理を中止
    if (!fetchParams.account_id || fetchParams.account_id.trim() === '') {
      console.warn('Account ID is empty, skipping API call');
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: 'アカウントが選択されていません' 
      }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    hasFetchedRef.current = true;

    try {
      console.log('Fetching post insights with params:', fetchParams);
      
      const response = await postInsightApi.getPostInsights(fetchParams);
      
      setState(prev => ({
        ...prev,
        data: response,
        posts: response.posts,
        loading: false,
        error: null,
        lastFetched: new Date(),
      }));

      console.log('Post insights fetched successfully:', {
        postsCount: response.posts.length,
        summary: response.summary
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      console.error('Failed to fetch post insights:', error);

      // リトライロジック
      if (retryCount > 0) {
        console.log(`Retrying in ${opts.retryDelay}ms... (${retryCount} retries left)`);
        
        setTimeout(() => {
          fetchData(params, retryCount - 1);
        }, opts.retryDelay);
        
        return;
      }

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  }, [opts.retryCount, opts.retryDelay]);

  // メディアタイプによるフィルタリング
  const filterByMediaType = useCallback((mediaType: MediaType | 'All'): PostInsightData[] => {
    if (!state.posts.length) return [];
    
    if (mediaType === 'All') {
      return state.posts;
    }
    
    return state.posts.filter(post => post.type === mediaType);
  }, [state.posts]);

  // リフレッシュ関数
  const refresh = useCallback(async (): Promise<void> => {
    hasFetchedRef.current = false; // フェッチ状態をリセット
    await fetchData();
  }, [fetchData]);

  // エラークリア
  const clearError = useCallback((): void => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // ローディング状態操作
  const setLoading = useCallback((loading: boolean): void => {
    setState(prev => ({ ...prev, loading }));
  }, []);


  // initialParamsを安定化してオブジェクト再作成を防ぐ
  const stableInitialParams = useMemo(() => ({
    account_id: initialParams.account_id,
    from_date: initialParams.from_date,
    to_date: initialParams.to_date,
    media_type: initialParams.media_type,
    limit: initialParams.limit
  }), [
    initialParams.account_id,
    initialParams.from_date,
    initialParams.to_date,
    initialParams.media_type,
    initialParams.limit
  ]);

  // パラメータが更新された時にcurrentParamsを更新
  useEffect(() => {
    setCurrentParams(stableInitialParams);
    currentParamsRef.current = stableInitialParams;
    hasFetchedRef.current = false; // パラメータ変更時はフェッチ状態をリセット
  }, [stableInitialParams]);

  // currentParamsとrefを同期
  useEffect(() => {
    currentParamsRef.current = currentParams;
  }, [currentParams]);

  // 初期データフェッチ（autoFetch が有効な場合）
  useEffect(() => {
    if (opts.autoFetch && currentParams.account_id && !hasFetchedRef.current) {
      fetchData();
    }
  }, [opts.autoFetch, currentParams.account_id, fetchData]);

  return {
    ...state,
    fetchData,
    filterByMediaType,
    refresh,
    clearError,
    setLoading,
  };
}

// 軽量版フック（リアルタイム更新不要な場合）
export function usePostInsightsStatic(
  params: PostInsightParams
): Pick<UsePostInsightsReturn, 'data' | 'posts' | 'loading' | 'error' | 'fetchData'> {
  const { data, posts, loading, error, fetchData } = usePostInsights(params, {
    autoFetch: true,
    cacheTime: 10 * 60 * 1000, // 10分キャッシュ
  });

  return { data, posts, loading, error, fetchData };
}