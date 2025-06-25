// Account Types
// バックエンドAPIレスポンスと一致するアカウント関連型定義

export interface InstagramAccount {
  id: string;                    // UUID
  instagram_user_id: string;     // Instagram User ID
  username: string;              // @なしのユーザー名
  account_name?: string;         // 表示名
  profile_picture_url?: string;  // プロフィール画像
  facebook_page_id?: string;     // Facebook Page ID
  is_active: boolean;            // アクティブ状態
  token_expires_at?: string;     // トークン有効期限（ISO format）
  created_at: string;            // 作成日時（ISO format）
  updated_at: string;            // 更新日時（ISO format）
  
  // UI用の追加フィールド
  is_token_valid: boolean;       // トークン有効性
  days_until_expiry?: number;    // 期限までの日数
  
  // 統計情報（オプション）
  latest_follower_count?: number;   // 最新フォロワー数
  latest_following_count?: number;  // 最新フォロー数
  total_posts?: number;             // 投稿数
  data_quality_score?: number;     // データ品質スコア
  last_synced_at?: string;          // 最終同期日時（ISO format）
}

export interface AccountListResponse {
  accounts: InstagramAccount[];
  total: number;
  active_count: number;
}

export interface AccountDetailResponse extends InstagramAccount {
  facebook_page_id?: string;
}

export interface TokenValidationResponse {
  account_id: string;
  is_valid: boolean;
  expires_at?: string;           // ISO format
  days_until_expiry?: number;
  warning_level: 'none' | 'warning' | 'critical' | 'expired';
  needs_refresh: boolean;
}

export interface AccountStatus {
  account_id: string;
  username: string;
  is_active: boolean;
  connection_status: 'connected' | 'disconnected';
  token_status: {
    is_valid: boolean;
    warning_level: string;
    expires_at?: string;
    days_until_expiry?: number;
  };
  data_status: {
    total_posts?: number;
    last_synced_at?: string;
    data_quality_score?: number;
  };
  created_at: string;
  updated_at: string;
}

// API リクエストパラメータ
export interface GetAccountsParams {
  active_only?: boolean;
  include_metrics?: boolean;
}

// エラーレスポンス
export interface ApiError {
  detail: string;
  message?: string;
  status_code?: number;
}

// UI用のヘルパー型
export type TokenWarningLevel = 'none' | 'warning' | 'critical' | 'expired';

export interface AccountSummary {
  id: string;
  username: string;
  displayName: string;           // account_name || username
  avatar: string;                // profile_picture_url with fallback
  isActive: boolean;
  tokenWarning: TokenWarningLevel;
  daysUntilExpiry?: number;
}

// Context用の型
export interface AccountContextValue {
  // 状態
  selectedAccount: InstagramAccount | null;
  accounts: InstagramAccount[];
  loading: boolean;
  error: string | null;
  
  // アクション
  selectAccount: (account: InstagramAccount) => void;
  refreshAccounts: () => Promise<void>;
  clearError: () => void;
  
  // ヘルパー
  getAccountById: (id: string) => InstagramAccount | undefined;
  getValidAccounts: () => InstagramAccount[];
  getAccountSummary: (account: InstagramAccount) => AccountSummary;
}

// Hook用の型
export interface UseAccountOptions {
  autoFetch?: boolean;
  cacheTime?: number;
  selectedAccountId?: string;     // 初期選択アカウント
}

export interface UseAccountReturn extends Omit<AccountContextValue, 'selectAccount'> {
  selectAccount: (accountId: string) => void;
  selectAccountByInstagramId: (instagramUserId: string) => void;
  validateToken: (accountId: string) => Promise<TokenValidationResponse | null>;
  getAccountStatus: (accountId: string) => Promise<AccountStatus | null>;
}