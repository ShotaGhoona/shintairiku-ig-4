# Instagram API トークン取得・セットアップガイド 2024

## 📋 概要

Instagram Graph APIを使用するためのアカウント登録から長期トークン取得までの完全なフローをドキュメント化しています。Meta for Developersでの初期セットアップから実装まで、開発者が必要とする全てのステップを詳細に解説します。

## 🚨 重要な2024年アップデート

### Instagram Basic Display API 廃止
- **2024年12月4日以降**: Instagram Basic Display APIへのリクエストはエラーを返すように
- **推奨対応**: Instagram Graph APIへの移行が必須

### 新しいInstagram API with Instagram Login
- **2024年7月23日リリース**: Facebookログイン不要の簡素化されたフロー
- オンボーディングステップの削減
- ビジネスアカウントの摩擦軽減

## 🔐 前提条件

### 必要なアカウント
1. **Instagram Business/Creatorアカウント**
   - 個人アカウントではアクセス不可
   - Instagram Businessアカウントの設定が必要

2. **Facebook Developerアカウント**
   - Meta for Developersプラットフォームでのアプリ管理
   - Facebook個人アカウントが必要

3. **Facebookページ（推奨）**
   - Instagram BusinessアカウントとFacebookページの連携
   - 一部機能でFacebookページ連携が必要

## 🚀 Step 1: Facebook Developer アカウント・アプリ作成

### 1.1 Facebook Developerアカウント作成
1. [Facebook for Developers](https://developers.facebook.com/)にアクセス
2. 個人のFacebookアカウントでログイン
3. 「My Apps」→ 「Create App」をクリック

### 1.2 アプリタイプ選択
```
アプリタイプ: "Business" または "Other"
用途: Instagram Business API連携
```

### 1.3 基本アプリ情報入力
```json
{
  "app_name": "Your App Name",
  "app_contact_email": "your-email@example.com",
  "app_purpose": "Instagram Business Analysis"
}
```

### 1.4 アプリ作成完了後の取得情報
- **App ID**: Facebook アプリケーションID
- **App Secret**: Facebook アプリケーションシークレット（サーバーサイドでのみ使用）

## 📱 Step 2: Instagram Product追加・設定

### 2.1 Instagram製品の追加
1. アプリダッシュボードで「Add Product」
2. 「Instagram」製品を選択
3. 「Set Up」をクリック

### 2.2 Instagram API選択
- **Instagram API with Facebook Login**: 従来の方法
- **Instagram API with Instagram Login**: 2024年新方式（推奨）

### 2.3 基本設定
```json
{
  "valid_oauth_redirect_uris": [
    "https://your-domain.com/auth/callback",
    "http://localhost:3000/auth/callback"
  ],
  "deauthorize_callback_url": "https://your-domain.com/auth/deauthorize",
  "data_deletion_request_callback_url": "https://your-domain.com/auth/delete"
}
```

## 🔑 Step 3: 短期トークン取得

### 3.1 Instagram Login フロー (2024年推奨)
```javascript
// Instagram Login URL
const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${APP_ID}&redirect_uri=${REDIRECT_URI}&scope=${SCOPE}&response_type=code`;

// 必要なスコープ
const scopes = [
  'instagram_business_basic',
  'instagram_business_manage_messages',
  'instagram_business_manage_comments',
  'instagram_business_content_publish'
].join(',');
```

### 3.2 認可コード取得
```javascript
// リダイレクト後のコールバック処理
const urlParams = new URLSearchParams(window.location.search);
const authCode = urlParams.get('code');
```

### 3.3 短期アクセストークン取得
```javascript
const getShortLivedToken = async (authCode) => {
  const response = await fetch('https://api.instagram.com/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      client_id: APP_ID,
      client_secret: APP_SECRET,
      grant_type: 'authorization_code',
      redirect_uri: REDIRECT_URI,
      code: authCode
    })
  });
  
  const data = await response.json();
  return {
    access_token: data.access_token,
    user_id: data.user_id
  };
};
```

## ⏰ Step 4: 長期トークンへの交換

### 4.1 短期→長期トークン交換
```javascript
const exchangeForLongLivedToken = async (shortLivedToken) => {
  const url = `https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=${APP_SECRET}&access_token=${shortLivedToken}`;
  
  const response = await fetch(url, { method: 'GET' });
  const data = await response.json();
  
  return {
    access_token: data.access_token,
    token_type: data.token_type,
    expires_in: data.expires_in // 約60日
  };
};
```

### 4.2 レスポンス例
```json
{
  "access_token": "long_lived_token_here",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

## 🔄 Step 5: トークンリフレッシュとメンテナンス

### 5.1 長期トークンのリフレッシュ
```javascript
const refreshLongLivedToken = async (currentToken) => {
  const url = `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${currentToken}`;
  
  const response = await fetch(url, { method: 'GET' });
  const data = await response.json();
  
  return {
    access_token: data.access_token,
    token_type: data.token_type,
    expires_in: data.expires_in
  };
};
```

### 5.2 トークン有効性チェック
```javascript
const validateToken = async (token) => {
  try {
    const response = await fetch(`https://graph.instagram.com/me?fields=id,username&access_token=${token}`);
    return response.ok;
  } catch (error) {
    return false;
  }
};
```

## 🏗️ Step 6: 実装例（Node.js/Express）

### 6.1 基本的なセットアップ
```javascript
const express = require('express');
const app = express();

// 環境変数
const {
  INSTAGRAM_APP_ID,
  INSTAGRAM_APP_SECRET,
  REDIRECT_URI
} = process.env;

// 認証開始エンドポイント
app.get('/auth/instagram', (req, res) => {
  const scope = 'instagram_business_basic,instagram_business_manage_messages';
  const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${INSTAGRAM_APP_ID}&redirect_uri=${REDIRECT_URI}&scope=${scope}&response_type=code`;
  
  res.redirect(authUrl);
});

// コールバック処理
app.get('/auth/callback', async (req, res) => {
  const { code } = req.query;
  
  try {
    // 短期トークン取得
    const shortToken = await getShortLivedToken(code);
    
    // 長期トークンに交換
    const longToken = await exchangeForLongLivedToken(shortToken.access_token);
    
    // データベースに保存
    await saveUserToken(shortToken.user_id, longToken.access_token);
    
    res.json({ success: true, message: 'Authentication successful' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### 6.2 トークン管理クラス
```javascript
class InstagramTokenManager {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
  }

  async exchangeForLongLived(shortToken) {
    const url = `https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=${this.appSecret}&access_token=${shortToken}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Token exchange failed');
    }
    
    return await response.json();
  }

  async refreshToken(longLivedToken) {
    const url = `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${longLivedToken}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Token refresh failed');
    }
    
    return await response.json();
  }

  async validateToken(token) {
    try {
      const response = await fetch(`https://graph.instagram.com/me?fields=id,username&access_token=${token}`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
```

## 📊 Step 7: ユーザー情報・メディア取得

### 7.1 基本ユーザー情報取得
```javascript
const getUserInfo = async (accessToken) => {
  const fields = 'id,username,account_type,media_count';
  const response = await fetch(`https://graph.instagram.com/me?fields=${fields}&access_token=${accessToken}`);
  return await response.json();
};
```

### 7.2 ユーザーメディア取得
```javascript
const getUserMedia = async (userId, accessToken) => {
  const fields = 'id,caption,media_type,media_url,thumbnail_url,timestamp,permalink';
  const response = await fetch(`https://graph.instagram.com/${userId}/media?fields=${fields}&access_token=${accessToken}`);
  return await response.json();
};
```

## 🔒 セキュリティ考慮事項

### 7.1 App Secretの保護
```javascript
// ❌ 危険: クライアントサイドでApp Secretを使用
const badExample = {
  clientSecret: 'your_app_secret' // 絶対にクライアントサイドに含めない
};

// ✅ 安全: サーバーサイドのみでApp Secretを使用
const goodExample = async (code) => {
  // サーバーサイドでのみ実行
  const response = await fetch('/api/exchange-token', {
    method: 'POST',
    body: JSON.stringify({ code }),
    headers: { 'Content-Type': 'application/json' }
  });
};
```

### 7.2 トークンの安全な保存
```javascript
// データベース設計例
const userTokenSchema = {
  user_id: 'string',
  instagram_user_id: 'string',
  access_token: 'encrypted_string', // 暗号化必須
  expires_at: 'timestamp',
  created_at: 'timestamp',
  updated_at: 'timestamp'
};
```

## 📱 Step 8: フロントエンド実装例（React）

### 8.1 Instagram認証コンポーネント
```jsx
import React, { useState } from 'react';

const InstagramAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState(null);

  const handleInstagramLogin = () => {
    setIsLoading(true);
    const authUrl = `/auth/instagram`;
    window.location.href = authUrl;
  };

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/instagram/status');
      const data = await response.json();
      setAuthStatus(data);
    } catch (error) {
      console.error('Auth status check failed:', error);
    }
  };

  return (
    <div className="instagram-auth">
      {!authStatus?.connected ? (
        <button 
          onClick={handleInstagramLogin}
          disabled={isLoading}
          className="bg-primary-color text-white px-6 py-3 rounded-lg"
        >
          {isLoading ? 'Processing...' : 'Connect Instagram Account'}
        </button>
      ) : (
        <div className="connected-status">
          <p>✅ Instagram Account Connected</p>
          <p>Username: @{authStatus.username}</p>
          <button onClick={() => setAuthStatus(null)}>
            Disconnect
          </button>
        </div>
      )}
    </div>
  );
};

export default InstagramAuth;
```

## 🔧 Step 9: トラブルシューティング

### 9.1 よくあるエラーと対処法

#### Error: "Invalid redirect URI"
```json
{
  "error_type": "OAuthException",
  "code": 400,
  "error_message": "Invalid redirect_uri"
}
```
**対処法**: Facebook DeveloperでリダイレクトURIが正確に設定されているか確認

#### Error: "Invalid client_secret"
```json
{
  "error": {
    "message": "Invalid client_secret",
    "type": "OAuthException",
    "code": 1
  }
}
```
**対処法**: App Secretが正確か、サーバーサイドで実行されているか確認

#### Error: "Rate limit exceeded"
```json
{
  "error": {
    "message": "Application request limit reached",
    "type": "OAuthException",
    "code": 4
  }
}
```
**対処法**: レート制限（200コール/時間）を考慮した実装

### 9.2 デバッグのためのテスト用エンドポイント
```javascript
// トークンテスト用
app.get('/test/token/:token', async (req, res) => {
  const { token } = req.params;
  
  try {
    const userInfo = await getUserInfo(token);
    res.json({ 
      valid: true, 
      user: userInfo,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(400).json({ 
      valid: false, 
      error: error.message 
    });
  }
});
```

## 📋 チェックリスト

### 初期セットアップ
- [ ] Facebook Developerアカウント作成
- [ ] Instagram Businessアカウント準備
- [ ] Facebookアプリ作成
- [ ] Instagram製品追加・設定
- [ ] リダイレクトURI設定
- [ ] プライバシーポリシー準備

### 実装
- [ ] 認証フロー実装
- [ ] 短期トークン取得
- [ ] 長期トークン交換
- [ ] トークンリフレッシュ機能
- [ ] エラーハンドリング
- [ ] セキュリティ対策

### テスト
- [ ] 認証フロー動作確認
- [ ] トークン有効性チェック
- [ ] API呼び出しテスト
- [ ] エラーケース確認
- [ ] レート制限対応確認

## 🚀 本番デプロイ前の最終確認

### 必須項目
1. **App Review申請完了**
   - 必要な権限申請
   - 使用目的の詳細説明
   - プライバシーポリシーの確認

2. **セキュリティチェック**
   - App Secretの環境変数化
   - HTTPS設定完了
   - トークン暗号化実装

3. **監視・ログ設定**
   - API使用量監視
   - エラーログ記録
   - トークン期限監視

---

## 📚 参考資料

- [Meta for Developers - Instagram Platform](https://developers.facebook.com/docs/instagram-platform/)
- [Instagram API with Instagram Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/)
- [Access Token Reference](https://developers.facebook.com/docs/instagram-platform/reference/access_token/)

**最終更新**: 2024年12月23日  
**対応API Version**: v21.0