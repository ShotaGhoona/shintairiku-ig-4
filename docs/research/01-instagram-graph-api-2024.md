# Instagram Graph API 2024 - 完全ガイド

## 📋 概要

Instagram Graph APIは、Instagram BusinessおよびCreatorアカウント専用のAPIで、メディア管理、コメント処理、ハッシュタグ検索、インサイト取得などの機能を提供します。2024年における最新の仕様と変更点を包括的にまとめています。

## 🆕 2024年の主要アップデート

### Graph API v21.0 リリース (2024年10月2日)
- エンドポイントの統合と簡素化
- 新しいメトリクス実装
- レガシーエンドポイントの廃止とマイグレーション要求

### 主要な変更点

#### 1. **エンドポイント統合**
- レガシーエンドポイントを`IG User`、`IG Media`、`IG Comment`オブジェクトに統合
- 設定された期限までのマイグレーションが必要

#### 2. **新しいViewsメトリクス**
- 2024年8月のアップデートでViewsが主要消費メトリクスに
- Reels、Live、Photos、Carousels、StoriesすべてでViewsメトリクスを提供

#### 3. **強化されたハッシュタグ検索**
- 改良されたコンテンツ発見機能
- マーケティング戦略の精密化が可能

#### 4. **詳細な分析機能**
- より詳細なアナリティクス
- サードパーティツールでのオーガニックコンテンツパフォーマンス追跡

## 🔐 認証とアクセス要件

### 必要条件
1. **Instagram Business/Creatorアカウント**
   - 個人アカウント（Consumer Account）ではアクセス不可
   - Facebookページとの連携が必要

2. **Facebook Developer Account**
   - Facebook for Developersでアプリ作成
   - アプリの審査と承認が必要

3. **プライバシーポリシー**
   - データ使用目的の明記
   - 有効なプライバシーポリシーの提供

### 認証フロー
```
Facebook Login → Instagram Business Account → API Access Token
```

## 📊 利用可能なエンドポイントとデータ

### 1. **メディア関連エンドポイント**

#### 取得可能なデータ
- **基本メディア情報**
  - ID、キャプション、メディアタイプ（画像/動画）
  - 投稿日時、パーマリンク
  - サムネイルURL、メディアURL

- **メディアメトリクス**
  - Views（新）- 全メディアタイプ対応
  - Likes、Comments、Shares
  - Reach、Impressions
  - Saved、Profile visits

#### 主要エンドポイント
```
GET /{ig-user-id}/media
GET /{ig-media-id}
POST /{ig-user-id}/media
POST /{ig-user-id}/media_publish
```

### 2. **コメント管理エンドポイント**

#### 機能
- コメントの取得・返信・削除
- コメントの非表示・表示
- コメントのモデレーション

#### エンドポイント
```
GET /{ig-media-id}/comments
POST /{ig-media-id}/comments
DELETE /{ig-comment-id}
POST /{ig-comment-id}/replies
```

#### レート制限
- `/media/comments`エンドポイント: **60書き込み/ユーザー/時間**

### 3. **ハッシュタグ検索エンドポイント**

#### 機能
- 特定ハッシュタグの公開投稿検索
- ビジネスアカウント関連ハッシュタグの発見
- ハッシュタグのメトリクス取得

#### 制限事項
- **30個のユニークハッシュタグ/7日間**
- リクエスト後7日間はカウントに含まれる

#### エンドポイント
```
GET /{ig-hashtag-id}
GET /{ig-hashtag-id}/top_media
GET /{ig-hashtag-id}/recent_media
```

### 4. **メンション検索エンドポイント**

#### 機能
- @メンションされた投稿の検索
- キャプション・コメント内のメンション検出
- メンションメディアのメタデータ取得

### 5. **ユーザー情報エンドポイント**

#### 取得可能データ
- **基本プロフィール情報**
  - ユーザーID、ユーザーネーム
  - アカウントタイプ（Business/Creator）
  - プロフィール画像URL

- **アカウントメトリクス**
  - フォロワー数、フォロー数
  - メディア数
  - プロフィールビュー数

#### エンドポイント
```
GET /{ig-user-id}
GET /{ig-user-id}/media
GET /{ig-user-id}/recently_searched_hashtags
```

### 6. **インサイト（分析）エンドポイント**

#### メディアインサイト
- Reach、Impressions、Engagement
- Views（動画・Reels）
- Saves、Shares
- Comments、Likes

#### プロフィールインサイト
- Profile views
- Reach、Impressions
- Website clicks
- Follower demographics

#### エンドポイント
```
GET /{ig-media-id}/insights
GET /{ig-user-id}/insights
```

## ⚡ レート制限（2024年最新）

### 現在のレート制限
- **一般的な制限**: **200コール/ユーザー/時間**
- **コメントエンドポイント**: **60書き込み/ユーザー/時間**
- **Business Use Case (BUC)制限**: 24時間でリセット

### 重要な変更
- 以前の5,000リクエスト/時間から大幅削減
- プライバシー保護とデータセキュリティ強化のため

### レート制限の対処
```http
HTTP Status: 429 Too Many Requests
```
- リアルタイムの使用統計はレスポンスヘッダーに含まれる
- アプリレベルでの計算: 100ユーザー × 200コール = 20,000コール/時間

## 🚀 コンテンツ公開機能

### 公開可能なメディア
1. **写真（単体・カルーセル）**
2. **動画**
3. **Reels**
4. **Stories**

### 公開制限
- **25投稿/24時間**
- メディアコンテナ作成 → 公開の2段階プロセス

### 公開フロー
```javascript
// 1. メディアコンテナ作成
POST /{ig-user-id}/media
{
  "image_url": "https://example.com/image.jpg",
  "caption": "投稿キャプション #hashtag"
}

// 2. メディア公開
POST /{ig-user-id}/media_publish
{
  "creation_id": "{creation-id}"
}
```

## 🔒 必要な権限（Permissions）

### 基本権限
1. **`instagram_basic`**
   - 基本的なプロフィール情報とメディアへのアクセス
   - 公開情報の読み取り

2. **`manage_pages`**
   - ハッシュタグ検索API使用に必須
   - Instagram Businessアカウントデータアクセス

### 追加権限（用途別）
- **`instagram_manage_comments`**: コメント管理
- **`instagram_manage_insights`**: インサイトアクセス
- **`instagram_content_publish`**: コンテンツ公開

## 📏 制限事項と注意点

### API制限
1. **アカウント制限**
   - Consumer Account（個人アカウント）はアクセス不可
   - Business/Creatorアカウントのみ

2. **機能制限**
   - 結果のソート機能なし
   - カーソルベースのページネーション（一部制限あり）
   - 一度に取得可能なメディア: 最大50件/リクエスト

3. **データ制限**
   - 投稿されたコンテンツのみアクセス可能
   - プライベートアカウントのデータは取得不可

### セキュリティ考慮事項
- アクセストークンの適切な管理
- HTTPS必須
- Webhook検証の実装推奨

## 💡 ベストプラクティス

### 1. **レート制限対策**
```javascript
// レート制限チェック
const checkRateLimit = (response) => {
  const remaining = response.headers['x-app-usage'];
  if (remaining && JSON.parse(remaining).call_count > 90) {
    // 90%到達時の処理
    await delay(3600000); // 1時間待機
  }
};
```

### 2. **エラーハンドリング**
```javascript
try {
  const response = await fetch(apiUrl);
  if (response.status === 429) {
    // レート制限対処
    await handleRateLimit();
  }
} catch (error) {
  console.error('API Error:', error);
}
```

### 3. **データキャッシュ戦略**
- 頻繁にアクセスするデータのキャッシュ
- TTL（Time To Live）の適切な設定
- Redis等のキャッシュストア活用

## 🔄 マイグレーション対応

### レガシーAPIからの移行
1. **エンドポイントマッピング**
   - 旧APIエンドポイントの新APIへの対応確認
   - フィールド名の変更対応

2. **権限の再設定**
   - 新しい権限要求の追加
   - アプリ審査の再実行

3. **テスト環境での検証**
   - 本番環境移行前の十分なテスト
   - レート制限の影響確認

## 📈 活用例

### 1. **ソーシャルメディア管理ツール**
- 複数アカウントの投稿管理
- コメントの一括管理
- パフォーマンス分析

### 2. **インフルエンサーマーケティング**
- エンゲージメント分析
- ハッシュタグパフォーマンス追跡
- オーディエンス分析

### 3. **Eコマース連携**
- 商品タグ付き投稿
- ショッピング機能連携
- 売上トラッキング

## 🚧 今後の展望

### 予想される変更
- さらなるプライバシー強化
- AI/ML機能の統合
- リアルタイム機能の拡充

### 開発者への推奨事項
- 定期的なドキュメント確認
- API バージョンアップへの迅速対応
- 代替手段の検討と準備

---

## 📚 参考リンク

- [Meta for Developers - Instagram Platform](https://developers.facebook.com/docs/instagram-platform/)
- [Instagram Graph API Reference](https://developers.facebook.com/docs/instagram-api/)
- [Graph API Changelog](https://developers.facebook.com/docs/graph-api/changelog/)

**最終更新**: 2024年12月23日
**API Version**: v21.0