// Account Management Hook
// アカウント管理のカスタムフック

import { useCallback } from 'react';
import { useAccountContext } from '../contexts/AccountContext';
import { accountApi } from '../services/accountApi';
import { 
  UseAccountReturn, 
  TokenValidationResponse,
  AccountStatus
} from '../types/account';

/**
 * アカウント管理フック
 * グローバルアカウント状態とAPI操作を提供
 */
export function useAccount(): UseAccountReturn {
  const context = useAccountContext();
  
  if (!context) {
    throw new Error('useAccount must be used within an AccountProvider');
  }

  const {
    selectedAccount,
    accounts,
    loading,
    error,
    refreshAccounts,
    clearError,
    getAccountById,
    getValidAccounts,
    getAccountSummary,
    selectAccount: contextSelectAccount,
  } = context;

  // アカウント選択（IDベース）
  const selectAccount = useCallback((accountId: string): void => {
    const account = getAccountById(accountId);
    if (account) {
      contextSelectAccount(account);
    } else {
      console.warn(`Account not found: ${accountId}`);
    }
  }, [getAccountById, contextSelectAccount]);

  // Instagram User IDでアカウント選択
  const selectAccountByInstagramId = useCallback((instagramUserId: string): void => {
    const account = accounts.find(acc => acc.instagram_user_id === instagramUserId);
    if (account) {
      contextSelectAccount(account);
    } else {
      console.warn(`Account not found by Instagram ID: ${instagramUserId}`);
    }
  }, [accounts, contextSelectAccount]);

  // トークン検証
  const validateToken = useCallback(async (accountId: string): Promise<TokenValidationResponse | null> => {
    try {
      const account = getAccountById(accountId);
      if (!account) {
        console.warn(`Account not found for token validation: ${accountId}`);
        return null;
      }

      console.log(`Validating token for account: ${account.username}`);
      const result = await accountApi.validateToken(accountId);
      
      // アカウント一覧を更新（トークン情報が変更された可能性）
      setTimeout(() => refreshAccounts(), 100);
      
      return result;
    } catch (error) {
      console.error('Token validation failed:', error);
      return null;
    }
  }, [getAccountById, refreshAccounts]);

  // アカウント状態取得
  const getAccountStatus = useCallback(async (accountId: string): Promise<AccountStatus | null> => {
    try {
      const account = getAccountById(accountId);
      if (!account) {
        console.warn(`Account not found for status check: ${accountId}`);
        return null;
      }

      console.log(`Getting status for account: ${account.username}`);
      const result = await accountApi.getAccountStatus(accountId);
      
      return result;
    } catch (error) {
      console.error('Account status check failed:', error);
      return null;
    }
  }, [getAccountById]);

  return {
    // 状態
    selectedAccount,
    accounts,
    loading,
    error,
    
    // アクション
    selectAccount,
    selectAccountByInstagramId,
    refreshAccounts,
    clearError,
    
    // ヘルパー
    getAccountById,
    getValidAccounts,
    getAccountSummary,
    
    // API操作
    validateToken,
    getAccountStatus,
  };
}

/**
 * 軽量版アカウントフック
 * 読み取り専用の基本情報のみ
 */
export function useAccountInfo() {
  const { selectedAccount, accounts, loading, error, getAccountById, getValidAccounts } = useAccount();
  
  return {
    selectedAccount,
    accounts,
    loading,
    error,
    getAccountById,
    getValidAccounts,
  };
}

/**
 * 選択アカウント専用フック
 * 現在選択されているアカウントの操作のみ
 */
export function useSelectedAccount() {
  const { 
    selectedAccount, 
    loading, 
    error, 
    validateToken, 
    getAccountStatus,
    getAccountSummary 
  } = useAccount();

  // 選択アカウントのトークン検証
  const validateSelectedToken = useCallback(async (): Promise<TokenValidationResponse | null> => {
    if (!selectedAccount) {
      console.warn('No account selected for token validation');
      return null;
    }
    
    return validateToken(selectedAccount.id);
  }, [selectedAccount, validateToken]);

  // 選択アカウントの状態取得
  const getSelectedAccountStatus = useCallback(async (): Promise<AccountStatus | null> => {
    if (!selectedAccount) {
      console.warn('No account selected for status check');
      return null;
    }
    
    return getAccountStatus(selectedAccount.id);
  }, [selectedAccount, getAccountStatus]);

  // 選択アカウントのサマリー
  const selectedAccountSummary = selectedAccount ? getAccountSummary(selectedAccount) : null;

  return {
    selectedAccount,
    selectedAccountSummary,
    loading,
    error,
    validateSelectedToken,
    getSelectedAccountStatus,
    isSelected: !!selectedAccount,
    hasValidToken: selectedAccount?.is_token_valid ?? false,
  };
}

/**
 * アカウント一覧管理フック
 * アカウント一覧の操作に特化
 */
export function useAccountList() {
  const { 
    accounts, 
    loading, 
    error, 
    refreshAccounts, 
    clearError,
    getValidAccounts,
    getAccountSummary 
  } = useAccount();

  // サマリー一覧作成
  const accountSummaries = accounts.map(account => getAccountSummary(account));
  
  // アクティブアカウント一覧
  const activeAccounts = accounts.filter(account => account.is_active);
  
  // トークン警告レベル別統計
  const tokenStats = {
    total: accounts.length,
    active: activeAccounts.length,
    valid: accounts.filter(acc => acc.is_token_valid).length,
    warning: accounts.filter(acc => 
      acc.days_until_expiry !== undefined && 
      acc.days_until_expiry <= 7 && 
      acc.days_until_expiry > 1
    ).length,
    critical: accounts.filter(acc => 
      acc.days_until_expiry !== undefined && 
      acc.days_until_expiry <= 1
    ).length,
    expired: accounts.filter(acc => !acc.is_token_valid).length,
  };

  return {
    accounts,
    accountSummaries,
    activeAccounts,
    validAccounts: getValidAccounts(),
    tokenStats,
    loading,
    error,
    refreshAccounts,
    clearError,
    hasAccounts: accounts.length > 0,
    hasActiveAccounts: activeAccounts.length > 0,
  };
}

// デフォルトエクスポート
export default useAccount;