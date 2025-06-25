/**
 * Setup feature type definitions
 */

// フォーム入力データ
export interface SetupFormData {
  app_id: string;
  app_secret: string;
  short_token: string;
}

// 発見されたアカウント情報
export interface DiscoveredAccount {
  instagram_user_id: string;
  username: string;
  account_name?: string;
  profile_picture_url?: string;
  facebook_page_id: string;
  facebook_page_name?: string;
  access_token: string;
  is_new: boolean;
}

// 作成されたアカウント情報
export interface CreatedAccount {
  id: string;
  instagram_user_id: string;
  username: string;
  account_name?: string;
  profile_picture_url?: string;
  facebook_page_id?: string;
  is_active: boolean;
  token_expires_at?: string;
  created_at: string;
  updated_at: string;
  is_token_valid: boolean;
  days_until_expiry?: number;
}

// セットアップAPIレスポンス
export interface SetupResponse {
  success: boolean;
  message: string;
  accounts_discovered: number;
  accounts_created: number;
  accounts_updated: number;
  discovered_accounts: DiscoveredAccount[];
  created_accounts: CreatedAccount[];
  errors: string[];
  warnings: string[];
}

// アカウント一覧レスポンス
export interface AccountListResponse {
  accounts: CreatedAccount[];
  total: number;
  active_count: number;
}

// セットアップフォームのバリデーションエラー
export interface SetupFormErrors {
  app_id?: string;
  app_secret?: string;
  short_token?: string;
  general?: string;
}

// セットアップ状態
export type SetupStatus = 'idle' | 'loading' | 'success' | 'error';

// テーブル表示用のアカウント情報
export interface AccountTableRow {
  id: string;
  instagram_user_id: string;
  username: string;
  account_name?: string;
  profile_picture_url?: string;
  facebook_page_id?: string;
  is_active: boolean;
  token_status: 'valid' | 'warning' | 'expired';
  days_until_expiry?: number;
  created_at: string;
}

// セットアップサービスオプション
export interface SetupServiceOptions {
  baseURL?: string;
  timeout?: number;
}