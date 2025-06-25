# Instagram アカウントセットアップページ実装戦略（必要最低限版）

## 概要

検証結果を基に、`src/app/setup` ページを必要最低限で実装する。3つの入力値（App ID、App Secret、短期トークン）からInstagramアカウントを取得し、FastAPIバックエンド経由でデータベースに保存、右側のテーブルに表示する機能を構築する。

## 📋 要件定義

### 機能要件
- **左側**: 3つの値の入力フォーム + 実行ボタン
- **右側**: 取得されたアカウントの一覧テーブル
- **データ保存**: SupabaseのPostgreSQLに保存
- **リアルタイム更新**: 保存後、即座にテーブルに反映

### 入力データ
1. **Instagram App ID** (例: 1244097340722277)
2. **Instagram App Secret** (例: 344b93f86f0ddafbf44913f8720cbcb2)
3. **Instagram Short Token** (例: EAARrfZCwPTGU...)

### 出力データ（テーブル表示）
| フィールド | 型 | 説明 |
|---|---|---|
| instagram_user_id | string (UK) | InstagramユーザーID |
| username | string | @ユーザー名 |
| account_name | string | アカウント表示名 |
| profile_picture_url | string | プロフィール画像URL |
| access_token_encrypted | text | アクセストークン（暗号化なし） |
| token_expires_at | timestamp | トークン有効期限 |
| facebook_page_id | string | FacebookページID |
| created_at | timestamp | 作成日時 |
| updated_at | timestamp | 更新日時 |

## 🏗️ アーキテクチャ設計

### 技術スタック
- **フロントエンド**: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL (既存)
- **API連携**: Instagram Graph API
- **状態管理**: React useState (最低限)

### ディレクトリ構造（他ページを参考）
```
# フロントエンド（post_insightページを参考）
src/
├── app/
│   └── setup/
│       └── page.tsx                 # ルーティングページ（featureを呼び出すのみ）
└── feature/
    └── setup/
        ├── index.tsx               # メイン機能コンポーネント
        ├── components/
        │   ├── SetupForm.tsx       # 左側の入力フォーム
        │   └── AccountTable.tsx    # 右側のアカウントテーブル
        ├── services/
        │   └── setupApi.ts         # FastAPI連携
        ├── types/
        │   └── setup.ts            # 型定義
        └── hooks/
            └── useAccountSetup.ts  # データフェッチhook

# バックエンド（accounts.pyを参考）
backend/app/
├── api/v1/
│   └── account_setup.py            # アカウントセットアップAPI
├── services/api/
│   └── account_setup_service.py    # ビジネスロジック
├── schemas/
│   └── account_setup_schema.py     # Pydantic スキーマ
└── models/
    └── instagram_account.py        # 既存モデル使用
```

## 🗄️ データベース設計

### 既存テーブル活用: `instagram_accounts`

既存の `backend/app/models/instagram_account.py` を使用するため、新しいテーブル作成は不要。
必要に応じて既存モデルに検証で得られたフィールドが含まれているか確認する。

## 🔄 API フロー設計

### 1. Instagram API 呼び出しシーケンス
```
1. 短期トークン → 長期トークン変換
   POST https://graph.facebook.com/v21.0/oauth/access_token

2. Facebookページ一覧取得
   GET https://graph.facebook.com/v21.0/me/accounts

3. 各ページのInstagramアカウント取得
   GET https://graph.facebook.com/v21.0/{page-id}?fields=instagram_business_account

4. Instagramアカウント詳細取得
   GET https://graph.facebook.com/v21.0/{instagram-account-id}?fields=id,username,name,profile_picture_url
```

### 2. FastAPI エンドポイント設計

#### `POST /api/v1/account-setup`

**リクエスト**:
```python
class AccountSetupRequest(BaseModel):
    app_id: str
    app_secret: str
    short_token: str
```

**レスポンス**:
```python
class AccountSetupResponse(BaseModel):
    success: bool
    message: str
    accounts: List[InstagramAccount]
    errors: Optional[List[str]] = None
```

#### `GET /api/v1/accounts` (既存エンドポイント活用)

## 🎨 UI/UX 設計

### ページレイアウト
```
┌─────────────────────────────────────────────────────────────┐
│ Instagram アカウントセットアップ                               │
├─────────────────────┬───────────────────────────────────────┤
│ 📝 アカウント登録    │ 📊 登録済みアカウント一覧                 │
│                     │                                       │
│ App ID             │ ┌─────────────────────────────────────┐ │
│ [入力フィールド]     │ │ @username | Account Name | Page ID │ │
│                     │ ├─────────────────────────────────────┤ │
│ App Secret         │ │ @ghoona.ai.inc | Ghoona | 533...   │ │
│ [入力フィールド]     │ │ @kanetake_net | カネタケ | 221...    │ │
│                     │ │ @yamasa_renovation | ヤマサリノベ   │ │
│ Short Token        │ └─────────────────────────────────────┘ │
│ [テキストエリア]     │                                       │
│                     │ 🔄 リアルタイム更新                    │
│ [🚀 アカウント取得]  │ 📈 取得済み: 5件                      │
└─────────────────────┴───────────────────────────────────────┘
```

### コンポーネント設計

#### SetupForm.tsx
```typescript
interface SetupFormProps {
  onSubmit: (data: SetupFormData) => Promise<void>;
  loading: boolean;
}

interface SetupFormData {
  app_id: string;
  app_secret: string;
  short_token: string;
}
```

#### AccountTable.tsx
```typescript
interface AccountTableProps {
  accounts: InstagramAccount[];
  loading: boolean;
  onRefresh: () => void;
}

interface InstagramAccount {
  id: number;
  instagram_user_id: string;
  username: string;
  account_name: string;
  profile_picture_url: string;
  facebook_page_id: string;
  created_at: string;
}
```

## 🔧 必要最低限の実装手順

### Step 1: バックエンド実装 (FastAPI)
1. **アカウントセットアップAPIエンドポイント作成**
   - `backend/app/api/v1/account_setup.py`
   - 検証コードの03_verify_account_details.pyロジックを移植
   - 既存のaccounts.pyを参考に実装

2. **スキーマ定義**
   - `backend/app/schemas/account_setup_schema.py`
   - リクエスト・レスポンスの型定義

3. **サービス層実装**
   - `backend/app/services/api/account_setup_service.py`
   - Instagram API呼び出しロジック

### Step 2: フロントエンド実装
1. **基本構造作成**
   - `src/app/setup/page.tsx` (ルーティングのみ)
   - `src/feature/setup/index.tsx` (メイン機能)

2. **最低限のコンポーネント**
   - 入力フォーム（3つのフィールド）
   - テーブル表示（取得アカウント一覧）
   - ローディング・エラー表示

3. **API連携**
   - FastAPI呼び出し
   - 基本的な状態管理

### Step 3: 統合テスト
1. **基本動作確認**
   - フォーム入力 → API呼び出し → DB保存 → テーブル表示

## 🛡️ エラーハンドリング戦略

### API レベル
- **Instagram API エラー**: トークン期限切れ、権限不足
- **データベースエラー**: 接続エラー、制約違反
- **ネットワークエラー**: タイムアウト、接続失敗

### UI レベル
- **入力バリデーション**: 必須項目、形式チェック
- **ローディング状態**: 処理中の表示
- **成功・失敗メッセージ**: ユーザーフィードバック

### エラー表示例
```typescript
// 成功時
toast.success(`${accounts.length}件のアカウントを取得しました`);

// エラー時
toast.error('Instagram API でエラーが発生しました。トークンを確認してください。');

// 警告時
toast.warning('一部のアカウントで詳細情報を取得できませんでした。');
```

## 🎯 必要最低限の成果物

### 実装範囲
1. ✅ **バックエンドAPI** - アカウントセットアップエンドポイント
2. ✅ **フロントエンド画面** - 左右2カラムの基本レイアウト
3. ✅ **データベース連携** - 既存テーブルへの保存
4. ✅ **基本エラーハンドリング** - 最低限のエラー表示

### 除外項目（将来実装）
- 高度なバリデーション
- リアルタイム更新
- 詳細なエラーメッセージ
- UIの細かい調整
- パフォーマンス最適化

## 📦 追加パッケージ

フロントエンドは既存のshadcn/uiコンポーネントを活用し、新しいパッケージは最小限に抑える。

## 🌟 成功指標

1. **機能性**: 3つの入力から正確にアカウント取得
2. **パフォーマンス**: API 呼び出し〜表示まで10秒以内
3. **信頼性**: エラー率5%未満
4. **ユーザビリティ**: 直感的な操作フロー

---

この戦略に基づいて段階的に実装を進めることで、検証結果を活用した実用的なアカウントセットアップページを構築できます。