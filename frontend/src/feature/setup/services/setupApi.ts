/**
 * Setup API Service
 * アカウントセットアップ用のAPI連携サービス
 */

import { SetupFormData, SetupResponse, AccountListResponse } from '../types/setup';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class SetupApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * アカウントセットアップを実行
   */
  async setupAccounts(data: SetupFormData): Promise<SetupResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/account-setup/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 登録済みアカウント一覧を取得
   */
  async getAccounts(activeOnly: boolean = true): Promise<AccountListResponse> {
    const params = new URLSearchParams({
      active_only: activeOnly.toString(),
      include_metrics: 'false',
    });

    const response = await fetch(`${this.baseURL}/api/v1/account-setup/discovered-accounts?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * セットアップ状況を確認
   */
  async getSetupStatus(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/account-setup/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 認証情報の事前検証
   */
  async validateCredentials(appId: string, appSecret: string): Promise<any> {
    const params = new URLSearchParams({
      app_id: appId,
      app_secret: appSecret,
    });

    const response = await fetch(`${this.baseURL}/api/v1/account-setup/validate-credentials?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}

// シングルトンインスタンス
export const setupApiService = new SetupApiService();

// 型安全なAPI呼び出し関数
export const setupApi = {
  /**
   * アカウントセットアップ
   */
  setupAccounts: async (data: SetupFormData): Promise<SetupResponse> => {
    return setupApiService.setupAccounts(data);
  },

  /**
   * アカウント一覧取得
   */
  getAccounts: async (activeOnly: boolean = true): Promise<AccountListResponse> => {
    return setupApiService.getAccounts(activeOnly);
  },

  /**
   * セットアップ状況取得
   */
  getSetupStatus: async (): Promise<any> => {
    return setupApiService.getSetupStatus();
  },

  /**
   * 認証情報検証
   */
  validateCredentials: async (appId: string, appSecret: string): Promise<any> => {
    return setupApiService.validateCredentials(appId, appSecret);
  },
};

export default setupApi;