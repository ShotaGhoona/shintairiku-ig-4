// Account API Client
// バックエンドアカウントAPIとの通信を担当

import {
  InstagramAccount,
  AccountListResponse,
  AccountDetailResponse,
  TokenValidationResponse,
  AccountStatus,
  GetAccountsParams,
  ApiError
} from '../types/account';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class AccountApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * アカウント一覧を取得
   */
  async getAccounts(params: GetAccountsParams = {}): Promise<AccountListResponse> {
    try {
      const url = new URL(`${this.baseUrl}/api/v1/accounts`);
      
      // クエリパラメータを追加
      if (params.active_only !== undefined) {
        url.searchParams.append('active_only', params.active_only.toString());
      }
      
      if (params.include_metrics !== undefined) {
        url.searchParams.append('include_metrics', params.include_metrics.toString());
      }

      console.log('Account API Request URL:', url.toString());

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data: AccountListResponse = await response.json();
      console.log('Account API Response received:', { 
        accountsCount: data.accounts.length, 
        total: data.total,
        activeCount: data.active_count 
      });
      
      return data;
      
    } catch (error) {
      console.error('Account API Error:', error);
      
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('Unknown error occurred while fetching accounts');
      }
    }
  }

  /**
   * アカウント詳細を取得
   */
  async getAccountDetails(accountId: string): Promise<AccountDetailResponse> {
    try {
      const url = `${this.baseUrl}/api/v1/accounts/${accountId}`;
      
      console.log('Account Details API Request:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Account not found: ${accountId}`);
        }
        
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data: AccountDetailResponse = await response.json();
      console.log('Account Details Response received:', { 
        accountId: data.id, 
        username: data.username 
      });
      
      return data;
      
    } catch (error) {
      console.error('Account Details API Error:', error);
      
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('Unknown error occurred while fetching account details');
      }
    }
  }

  /**
   * トークン有効性を確認
   */
  async validateToken(accountId: string): Promise<TokenValidationResponse> {
    try {
      const url = `${this.baseUrl}/api/v1/accounts/${accountId}/validate-token`;
      
      console.log('Token Validation API Request:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Account not found: ${accountId}`);
        }
        
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data: TokenValidationResponse = await response.json();
      console.log('Token Validation Response received:', { 
        accountId: data.account_id, 
        isValid: data.is_valid,
        warningLevel: data.warning_level 
      });
      
      return data;
      
    } catch (error) {
      console.error('Token Validation API Error:', error);
      
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('Unknown error occurred while validating token');
      }
    }
  }

  /**
   * アカウント状態を取得
   */
  async getAccountStatus(accountId: string): Promise<AccountStatus> {
    try {
      const url = `${this.baseUrl}/api/v1/accounts/${accountId}/status`;
      
      console.log('Account Status API Request:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Account not found: ${accountId}`);
        }
        
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData: ApiError = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }

      const data: AccountStatus = await response.json();
      console.log('Account Status Response received:', { 
        accountId: data.account_id, 
        connectionStatus: data.connection_status 
      });
      
      return data;
      
    } catch (error) {
      console.error('Account Status API Error:', error);
      
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('Unknown error occurred while fetching account status');
      }
    }
  }

  /**
   * アクティブアカウントの簡易チェック
   */
  async checkActiveAccounts(): Promise<boolean> {
    try {
      const data = await this.getAccounts({ active_only: true });
      return data.active_count > 0;
    } catch (error) {
      console.warn('Active accounts check failed:', error);
      return false;
    }
  }

  /**
   * アカウントをInstagram User IDで検索
   */
  async findAccountByInstagramId(instagramUserId: string): Promise<InstagramAccount | null> {
    try {
      // まず詳細取得を試行（Instagram User IDでの検索）
      const accountDetail = await this.getAccountDetails(instagramUserId);
      return accountDetail;
    } catch (error) {
      // 見つからない場合は一覧から検索
      try {
        const accounts = await this.getAccounts({ active_only: false, include_metrics: false });
        const account = accounts.accounts.find(acc => acc.instagram_user_id === instagramUserId);
        return account || null;
      } catch (listError) {
        console.warn('Failed to find account by Instagram ID:', error);
        return null;
      }
    }
  }
}

// シングルトンインスタンス
export const accountApi = new AccountApiClient();

// 名前付きエクスポート（テスト用）
export { AccountApiClient };

// デフォルトエクスポート
export default accountApi;