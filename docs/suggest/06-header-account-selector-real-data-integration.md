# Headerアカウント選択機能の実データ統合戦略

## 現状分析

### 現在のHeader構造
```
frontend/src/components/common/Header.tsx
├── ダミーアカウントデータ（4つのアカウント）
├── アカウント選択Popover UI
├── 選択状態管理
└── PDF エクスポート機能
```

### ダミーデータ構造（現状）
```typescript
const dummyAccounts = [
  {
    id: "1",
    username: "@fashion_store_tokyo",
    name: "Fashion Store Tokyo", 
    avatar: "https://images.unsplash.com/...",
    isActive: true,
  },
  // ... 他3つのアカウント
];
```

### バックエンドデータ構造
```sql
-- instagram_accounts テーブル
- id: UUID（主キー）
- instagram_user_id: Instagram User ID
- username: アカウント名（@なし）
- account_name: 表示名
- account_type: PERSONAL | BUSINESS
- profile_picture_url: プロフィール画像URL
- is_active: アクティブ状態
- access_token: アクセストークン（暗号化予定）
- token_expires_at: トークン有効期限
- followers_count: フォロワー数
- following_count: フォロー数
- posts_count: 投稿数
```

## 課題と要件

### 1. データソース移行
- **課題**: ダミーデータから実データベースへの移行
- **要件**: リアルタイムなアカウント情報の表示

### 2. アカウント選択連携
- **課題**: アカウント選択が各機能に伝播されていない
- **要件**: 選択アカウントのグローバル状態管理

### 3. 動的アカウント管理
- **課題**: 固定の4アカウントから動的なアカウント数への対応
- **要件**: アカウント追加・削除機能への対応

### 4. アクセストークン管理
- **課題**: トークン有効期限のハンドリング
- **要件**: 期限切れアカウントの視覚的識別

## 実装戦略

### Phase 1: アカウントAPIクライアント実装

#### 1.1. Account API Service 作成
```
frontend/src/services/
└── accountApi.ts              # アカウント取得APIクライアント
```

**主な機能:**
- `getActiveAccounts()`: アクティブアカウント一覧取得
- `getAccountDetails(id)`: 特定アカウント詳細取得
- `checkTokenValidity()`: トークン有効性確認

#### 1.2. アカウント用型定義
```
frontend/src/types/
└── account.ts                 # アカウント関連型定義
```

**型定義内容:**
```typescript
interface InstagramAccount {
  id: string;                    // UUID
  instagram_user_id: string;     // Instagram User ID
  username: string;              // @なしのユーザー名
  account_name: string;          // 表示名
  account_type: 'PERSONAL' | 'BUSINESS';
  profile_picture_url?: string;  // プロフィール画像
  is_active: boolean;            // アクティブ状態
  token_expires_at: string;      // トークン有効期限（ISO format）
  followers_count: number;       // フォロワー数
  following_count: number;       // フォロー数
  posts_count: number;           // 投稿数
  
  // UI用の追加フィールド
  is_token_valid: boolean;       // トークン有効性
  last_sync_at?: string;         // 最終同期日時
}
```

### Phase 2: グローバル状態管理実装

#### 2.1. Account Context 作成
```
frontend/src/contexts/
└── AccountContext.tsx         # アカウント選択状態管理
```

**Context機能:**
- 選択中アカウントの状態管理
- アカウント一覧の状態管理
- アカウント変更時の全機能への通知

#### 2.2. Account Hook 作成
```
frontend/src/hooks/
└── useAccount.ts              # アカウント管理カスタムフック
```

**Hook機能:**
```typescript
interface UseAccountReturn {
  // 状態
  selectedAccount: InstagramAccount | null;
  accounts: InstagramAccount[];
  loading: boolean;
  error: string | null;
  
  // アクション
  selectAccount: (account: InstagramAccount) => void;
  refreshAccounts: () => Promise<void>;
  
  // ヘルパー
  getAccountById: (id: string) => InstagramAccount | undefined;
  getValidAccounts: () => InstagramAccount[];
}
```

### Phase 3: Header コンポーネント更新

#### 3.1. Header の実データ対応
**変更内容:**
- ダミーデータ削除
- `useAccount` フック統合
- リアルタイムアカウントリスト表示
- トークン有効期限警告表示

#### 3.2. UI改善項目
- **アカウント状態表示**: トークン有効期限の視覚化
- **エラーハンドリング**: アカウント取得失敗時の表示
- **ローディング状態**: アカウント読み込み中表示
- **リフレッシュ機能**: 手動でアカウント情報更新

### Phase 4: 各機能との連携実装

#### 4.1. Post Insight との連携
**現在:**
```typescript
// 固定のアカウントID
account_id: "17841402015304577"
```

**変更後:**
```typescript
// 選択されたアカウントIDを動的に取得
const { selectedAccount } = useAccount();
account_id: selectedAccount?.instagram_user_id || null
```

#### 4.2. 他機能への拡張
- **Monthly Insight**: 選択アカウントでのフィルタリング
- **Yearly Insight**: 選択アカウントでのフィルタリング
- **Media Type Insight**: 選択アカウントでのフィルタリング

## データマッピング戦略

### API レスポンス変換
```typescript
// バックエンドレスポンス → フロントエンド型変換
const transformAccountData = (apiAccount: any): InstagramAccount => {
  return {
    id: apiAccount.id,
    instagram_user_id: apiAccount.instagram_user_id,
    username: apiAccount.username,
    account_name: apiAccount.account_name || apiAccount.username,
    account_type: apiAccount.account_type,
    profile_picture_url: apiAccount.profile_picture_url,
    is_active: apiAccount.is_active,
    token_expires_at: apiAccount.token_expires_at,
    followers_count: apiAccount.followers_count || 0,
    following_count: apiAccount.following_count || 0,
    posts_count: apiAccount.posts_count || 0,
    
    // 計算フィールド
    is_token_valid: new Date(apiAccount.token_expires_at) > new Date(),
    last_sync_at: apiAccount.updated_at,
  };
};
```

### プロフィール画像ハンドリング
```typescript
const getProfileImageUrl = (account: InstagramAccount): string => {
  const placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNGM0Y0RjYiLz4KPHBhdGggZD0iTTggMjRDOCAyMC42ODYzIDEwLjY4NjMgMTggMTQgMThIMTRDMTcuMzEzNyAxOCAyMCAyMC42ODYzIDIwIDI0VjI0SDhWMjRaIiBmaWxsPSIjOUNBM0FGIi8+CjxjaXJjbGUgY3g9IjE2IiBjeT0iMTIiIHI9IjQiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+Cg==';
  
  // プロフィール画像の有効性確認
  if (!account.profile_picture_url || 
      account.profile_picture_url.includes('example.com')) {
    return placeholder;
  }
  
  return account.profile_picture_url;
};
```

## バックエンドAPI拡張

### 現状分析

**✅ 既に存在するもの:**
- `InstagramAccountRepository`: 完全なCRUD操作対応
- `InstagramAccount`モデル: 必要なフィールド定義済み
- データベーステーブル: `instagram_accounts`

**❌ 不足しているもの:**
- アカウントAPI エンドポイント（`/api/v1/accounts`）
- アカウント用サービス層（`AccountService`）
- アカウント用Pydanticスキーマ

### 実装が必要なバックエンドコンポーネント

#### 1. Account Service 実装
```
backend/app/services/api/
└── account_service.py          # アカウント管理ビジネスロジック
```

**主な機能:**
```python
class AccountService:
    async def get_active_accounts(self) -> List[AccountResponse]
    async def get_account_details(self, account_id: str) -> AccountDetailResponse
    async def validate_token(self, account_id: str) -> TokenValidationResponse
    async def calculate_account_metrics(self, account_id: str) -> AccountMetrics
```

#### 2. Account API Schema 実装
```
backend/app/schemas/
└── account_schema.py           # アカウント用Pydanticスキーマ
```

**スキーマ定義:**
```python
class AccountResponse(BaseModel):
    id: str
    instagram_user_id: str
    username: str
    account_name: Optional[str]
    profile_picture_url: Optional[str]
    is_active: bool
    token_expires_at: Optional[datetime]
    is_token_valid: bool
    
    # 統計情報（オプション）
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    last_synced_at: Optional[datetime] = None

class AccountDetailResponse(AccountResponse):
    facebook_page_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
class TokenValidationResponse(BaseModel):
    account_id: str
    is_valid: bool
    expires_at: Optional[datetime]
    days_until_expiry: Optional[int]
    warning_level: str  # "none", "warning", "critical", "expired"
```

#### 3. Account API Endpoints 実装
```
backend/app/api/v1/
└── accounts.py                 # アカウントAPIエンドポイント
```

**APIエンドポイント:**

##### GET /api/v1/accounts
```python
@router.get("/", response_model=AccountListResponse)
async def get_accounts(
    active_only: bool = True,
    include_metrics: bool = False,
    db: Session = Depends(get_db)
):
    """アカウント一覧取得"""
```

##### GET /api/v1/accounts/{account_id}
```python
@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account_details(
    account_id: str,
    db: Session = Depends(get_db)
):
    """アカウント詳細取得"""
```

##### POST /api/v1/accounts/{account_id}/validate-token
```python
@router.post("/{account_id}/validate-token", response_model=TokenValidationResponse)
async def validate_account_token(
    account_id: str,
    db: Session = Depends(get_db)
):
    """トークン有効性確認"""
```

#### 4. モデル拡張（必要に応じて）

**現在のモデルに不足している可能性があるフィールド:**
```python
# instagram_account.pyに追加検討
class InstagramAccount(Base):
    # 既存フィールド...
    
    # 統計情報フィールド（追加検討）
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0) 
    posts_count = Column(Integer, default=0)
    last_synced_at = Column(DateTime(timezone=True))
    
    # ステータス管理フィールド（追加検討）
    account_type = Column(String(20), default="PERSONAL")  # PERSONAL | BUSINESS
    collection_status = Column(String(20), default="active")  # active | failed | paused
    last_error_message = Column(Text)
```

### 実装順序

#### Phase 1: スキーマ・サービス実装
1. `account_schema.py` - Pydanticスキーマ定義
2. `account_service.py` - ビジネスロジック実装
3. モデル拡張（必要に応じて）

#### Phase 2: APIエンドポイント実装
1. `accounts.py` - FastAPIエンドポイント実装
2. `main.py` - ルーター登録
3. APIテスト実装

#### Phase 3: 統計情報拡張
1. アカウント統計計算ロジック
2. 定期的な統計更新機能
3. パフォーマンス最適化

### レスポンス例

#### GET /api/v1/accounts
```json
{
  "accounts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "instagram_user_id": "17841402015304577", 
      "username": "fashion_store_tokyo",
      "account_name": "Fashion Store Tokyo",
      "profile_picture_url": "https://scontent-nrt1-1.cdninstagram.com/...",
      "is_active": true,
      "token_expires_at": "2024-12-31T23:59:59Z",
      "is_token_valid": true,
      "followers_count": 1250,
      "following_count": 180,
      "posts_count": 45,
      "last_synced_at": "2024-06-25T10:30:00Z"
    }
  ],
  "total": 1,
  "active_count": 1
}
```

#### POST /api/v1/accounts/{account_id}/validate-token
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_valid": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "days_until_expiry": 180,
  "warning_level": "none"
}
```

## エラーハンドリング戦略

### 1. トークン期限切れ
```typescript
const TokenExpiryWarning = ({ account }: { account: InstagramAccount }) => {
  const daysUntilExpiry = getDaysUntilExpiry(account.token_expires_at);
  
  if (daysUntilExpiry <= 7) {
    return (
      <div className="flex items-center gap-1 text-orange-600">
        <AlertTriangle className="h-3 w-3" />
        <span className="text-xs">
          {daysUntilExpiry <= 0 ? '期限切れ' : `${daysUntilExpiry}日後に期限切れ`}
        </span>
      </div>
    );
  }
  return null;
};
```

### 2. アカウント取得失敗
```typescript
const AccountLoadError = ({ onRetry }: { onRetry: () => void }) => (
  <div className="p-4 text-center">
    <p className="text-sm text-muted-foreground mb-2">
      アカウント情報の取得に失敗しました
    </p>
    <Button size="sm" variant="outline" onClick={onRetry}>
      再試行
    </Button>
  </div>
);
```

### 3. 選択アカウントなし
```typescript
const NoAccountSelected = () => (
  <div className="p-4 text-center text-sm text-muted-foreground">
    アカウントを選択してください
  </div>
);
```

## セキュリティ考慮事項

### 1. アクセストークン保護
- フロントエンドではトークンを直接扱わない
- APIリクエストはサーバー経由で実行
- トークン更新は自動化

### 2. プロフィール画像セキュリティ
- Instagram CDN からの画像のみ許可
- 外部ホストの画像はプレースホルダーに置換

## パフォーマンス最適化

### 1. アカウントデータキャッシュ
```typescript
const ACCOUNT_CACHE_TIME = 5 * 60 * 1000; // 5分

// SWR/React Queryでキャッシュ管理
const { data: accounts } = useSWR(
  '/api/accounts', 
  fetchAccounts,
  { refreshInterval: ACCOUNT_CACHE_TIME }
);
```

### 2. 画像遅延読み込み
```typescript
<Avatar className="w-6 h-6">
  <AvatarImage 
    src={getProfileImageUrl(account)} 
    alt={account.account_name}
    loading="lazy"
  />
  <AvatarFallback>{account.account_name.charAt(0)}</AvatarFallback>
</Avatar>
```

## 実装スケジュール

### Week 1: API・型定義・Context実装
- AccountApi サービス実装
- 型定義作成
- AccountContext・useAccount フック実装

### Week 2: Header更新・連携実装
- Header コンポーネント実データ対応
- Post Insight との連携実装
- エラーハンドリング実装

### Week 3: 他機能連携・最適化
- 残り機能への連携実装
- パフォーマンス最適化
- セキュリティ対応

### Week 4: テスト・リファクタリング
- エンドツーエンドテスト
- エラーケーステスト
- コード品質向上

---

**Next Action**: Phase 1のAPI・型定義・Context実装から開始