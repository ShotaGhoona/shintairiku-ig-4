# Instagram予約投稿システム ディレクトリ構造設計

**作成日**: 2025-07-02  
**目的**: FastAPI + Next.js環境での予約投稿機能実装のためのディレクトリ構造設計  
**対象**: 現在のアプリケーション構造への統合

---

## 📋 現状分析

### 既存のアーキテクチャ
```
Backend (FastAPI):
- 5つのモデル (instagram_account, instagram_post, instagram_post_metrics, instagram_daily_stats, instagram_monthly_stats)
- Repository パターン採用
- API v1 構造 (/api/v1/*)
- サービス層での外部API統合

Frontend (Next.js):
- Feature-based ディレクトリ構造
- アカウント選択機能 (Header.tsx)
- 投稿分析、月間分析、年間分析画面
- AccountContext でアカウント管理
```

### 統合ポイント
1. **Header.tsx**: 既存のアカウント選択機能を活用
2. **API v1**: 新しいエンドポイントをapi_v1_routerに追加
3. **Models**: 新規scheduled_postsモデルを追加
4. **Feature構造**: 既存のfeature/配下に新機能追加

---

## 🏗️ 拡張ディレクトリ構造

### Backend追加ファイル

```
backend/
├── app/
│   ├── models/
│   │   ├── instagram_account.py               # (既存)
│   │   ├── instagram_post.py                  # (既存)
│   │   ├── instagram_post_metrics.py          # (既存)
│   │   ├── instagram_daily_stats.py           # (既存)
│   │   ├── instagram_monthly_stats.py         # (既存)
│   │   └── scheduled_post.py                  # 🆕 予約投稿モデル
│   │   └── migrations/
│   │       ├── 001-007_*.sql                  # (既存)
│   │       └── 008_create_scheduled_posts.sql # 🆕 予約投稿テーブル
│   │
│   ├── schemas/
│   │   ├── instagram_*.py                     # (既存)
│   │   ├── scheduled_post_schema.py           # 🆕 予約投稿スキーマ
│   │   └── media_upload_schema.py             # 🆕 メディアアップロードスキーマ
│   │
│   ├── repositories/
│   │   ├── instagram_*.py                     # (既存)
│   │   └── scheduled_post_repository.py       # 🆕 予約投稿リポジトリ
│   │
│   ├── services/
│   │   ├── api/                               # (既存)
│   │   │   ├── account_service.py
│   │   │   ├── post_insight_service.py
│   │   │   └── scheduled_post_service.py      # 🆕 予約投稿サービス
│   │   ├── data_collection/                   # (既存)
│   │   └── scheduling/                        # 🆕 スケジューリング関連
│   │       ├── __init__.py
│   │       ├── post_scheduler.py              # 🆕 投稿スケジューラー
│   │       ├── media_processor.py             # 🆕 メディア処理
│   │       └── instagram_publisher.py         # 🆕 Instagram投稿実行
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py                    # (既存 - 更新)
│   │       ├── accounts.py                    # (既存)
│   │       ├── post_insights.py               # (既存)
│   │       ├── account_setup.py               # (既存)
│   │       ├── scheduled_posts.py             # 🆕 予約投稿API
│   │       └── media_upload.py                # 🆕 メディアアップロードAPI
│   │
│   └── tasks/                                 # 🆕 バックグラウンドタスク
│       ├── __init__.py
│       ├── scheduler_tasks.py                 # 🆕 スケジューラータスク
│       └── cleanup_tasks.py                   # 🆕 クリーンアップタスク
│
├── storage/                                   # 🆕 メディアファイル保存
│   ├── uploads/
│   │   ├── images/
│   │   └── videos/
│   └── processed/
│       ├── thumbnails/
│       └── resized/
│
└── scripts/
    ├── github_actions/                        # (既存)
    └── scheduled_posts/                       # 🆕 予約投稿関連スクリプト
        ├── __init__.py
        ├── execute_scheduled_posts.py         # 🆕 定期実行スクリプト
        └── media_cleanup.py                   # 🆕 メディアクリーンアップ
```

### Frontend追加ファイル

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                           # (既存)
│   │   ├── layout.tsx                         # (既存)
│   │   ├── post_insight/                      # (既存)
│   │   ├── monthly-insight/                   # (既存)
│   │   ├── yearly-insight/                    # (既存)
│   │   ├── setup/                             # (既存)
│   │   ├── scheduled-posts/                   # 🆕 予約投稿画面
│   │   │   ├── page.tsx                       # 🆕 予約投稿一覧
│   │   │   ├── create/
│   │   │   │   └── page.tsx                   # 🆕 新規予約投稿作成
│   │   │   ├── edit/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx               # 🆕 予約投稿編集
│   │   │   └── calendar/
│   │   │       └── page.tsx                   # 🆕 カレンダー表示
│   │   └── media-library/                     # 🆕 メディアライブラリ
│   │       └── page.tsx                       # 🆕 アップロード済みメディア管理
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx                     # (既存 - 更新)
│   │   │   └── Navigation.tsx                 # 🆕 ナビゲーション拡張
│   │   ├── ui/                                # (既存)
│   │   └── scheduled-posts/                   # 🆕 予約投稿専用コンポーネント
│   │       ├── PostForm.tsx                   # 🆕 投稿フォーム
│   │       ├── MediaUploader.tsx              # 🆕 メディアアップロード
│   │       ├── ScheduleSelector.tsx           # 🆕 日時選択
│   │       ├── PostPreview.tsx                # 🆕 投稿プレビュー
│   │       ├── PostsList.tsx                  # 🆕 予約投稿一覧
│   │       ├── PostCard.tsx                   # 🆕 投稿カード
│   │       ├── CalendarView.tsx               # 🆕 カレンダー表示
│   │       ├── StatusBadge.tsx                # 🆕 ステータス表示
│   │       └── ActionButtons.tsx              # 🆕 アクションボタン
│   │
│   ├── feature/
│   │   ├── post_insight/                      # (既存)
│   │   ├── monthly-insight/                   # (既存)
│   │   ├── yearly-insight/                    # (既存)
│   │   ├── setup/                             # (既存)
│   │   └── scheduled-posts/                   # 🆕 予約投稿機能
│   │       ├── index.tsx                      # 🆕 機能エクスポート
│   │       ├── components/
│   │       │   ├── CreatePostForm.tsx         # 🆕 投稿作成フォーム
│   │       │   ├── EditPostForm.tsx           # 🆕 投稿編集フォーム
│   │       │   ├── PostsListView.tsx          # 🆕 投稿一覧表示
│   │       │   ├── CalendarView.tsx           # 🆕 カレンダー表示
│   │       │   ├── MediaLibrary.tsx           # 🆕 メディアライブラリ
│   │       │   └── PostAnalytics.tsx          # 🆕 投稿分析(将来拡張)
│   │       ├── hooks/
│   │       │   ├── useScheduledPosts.ts       # 🆕 予約投稿フック
│   │       │   ├── useMediaUpload.ts          # 🆕 メディアアップロードフック
│   │       │   ├── usePostScheduler.ts        # 🆕 スケジューリングフック
│   │       │   └── useCalendar.ts             # 🆕 カレンダーフック
│   │       ├── services/
│   │       │   ├── scheduledPostsApi.ts       # 🆕 予約投稿API
│   │       │   ├── mediaUploadApi.ts          # 🆕 メディアアップロードAPI
│   │       │   └── instagramPublishApi.ts     # 🆕 Instagram投稿API
│   │       ├── types/
│   │       │   ├── scheduledPost.ts           # 🆕 予約投稿型定義
│   │       │   ├── mediaUpload.ts             # 🆕 メディアアップロード型
│   │       │   └── calendar.ts                # 🆕 カレンダー型定義
│   │       └── utils/
│   │           ├── dateUtils.ts               # 🆕 日時ユーティリティ
│   │           ├── mediaUtils.ts              # 🆕 メディアユーティリティ
│   │           └── validationUtils.ts         # 🆕 バリデーション
│   │
│   ├── contexts/
│   │   ├── AccountContext.tsx                 # (既存)
│   │   └── ScheduledPostContext.tsx           # 🆕 予約投稿コンテキスト
│   │
│   ├── hooks/
│   │   ├── useAccount.ts                      # (既存)
│   │   ├── use-mobile.ts                      # (既存)
│   │   └── useMediaUpload.ts                  # 🆕 メディアアップロード汎用フック
│   │
│   ├── lib/
│   │   ├── utils.ts                           # (既存)
│   │   ├── pdfExport.ts                       # (既存)
│   │   ├── mediaProcessing.ts                 # 🆕 メディア処理ライブラリ
│   │   └── dateTimeUtils.ts                   # 🆕 日時処理ライブラリ
│   │
│   ├── services/
│   │   ├── accountApi.ts                      # (既存)
│   │   └── uploadService.ts                   # 🆕 ファイルアップロードサービス
│   │
│   └── types/
│       ├── account.ts                         # (既存)
│       ├── scheduledPost.ts                   # 🆕 予約投稿関連型定義
│       └── media.ts                           # 🆕 メディア関連型定義
```

---

## 🔧 主要ファイルの実装内容

### Backend: 予約投稿モデル

```python
# backend/app/models/scheduled_post.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, func, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from ..core.database import Base

class PostStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO" 
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    REEL = "REEL"

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # メディア情報
    media_type = Column(Enum(MediaType), nullable=False)
    media_urls = Column(JSON, nullable=False)  # ['url1', 'url2'] for carousel
    caption = Column(Text)
    
    # スケジュール情報  
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    timezone = Column(String(50), default='Asia/Tokyo')
    
    # 状態管理
    status = Column(Enum(PostStatus), default=PostStatus.PENDING, index=True)
    published_at = Column(DateTime(timezone=True))
    instagram_post_id = Column(String(255))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # メタデータ
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
```

### Backend: 予約投稿API

```python
# backend/app/api/v1/scheduled_posts.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime

from ...schemas.scheduled_post_schema import (
    ScheduledPostCreate, ScheduledPostUpdate, ScheduledPostResponse
)
from ...services.api.scheduled_post_service import ScheduledPostService
from ...core.database import get_db

router = APIRouter(prefix="/scheduled-posts", tags=["scheduled-posts"])

@router.post("/", response_model=ScheduledPostResponse)
async def create_scheduled_post(
    account_id: str = Form(...),
    caption: str = Form(...),
    scheduled_time: datetime = Form(...),
    media_type: str = Form(...),
    files: List[UploadFile] = File(...),
    db = Depends(get_db)
):
    """予約投稿作成"""
    pass

@router.get("/", response_model=List[ScheduledPostResponse])
async def get_scheduled_posts(
    account_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db = Depends(get_db)
):
    """予約投稿一覧取得"""
    pass

@router.put("/{post_id}", response_model=ScheduledPostResponse) 
async def update_scheduled_post(
    post_id: str,
    update_data: ScheduledPostUpdate,
    db = Depends(get_db)
):
    """予約投稿更新"""
    pass

@router.delete("/{post_id}")
async def delete_scheduled_post(
    post_id: str,
    db = Depends(get_db)
):
    """予約投稿削除"""
    pass

@router.get("/calendar")
async def get_calendar_posts(
    account_id: str,
    year: int,
    month: int,
    db = Depends(get_db)
):
    """カレンダー用投稿取得"""
    pass
```

### Frontend: 予約投稿作成フォーム

```tsx
// frontend/src/feature/scheduled-posts/components/CreatePostForm.tsx
'use client';

import { useState } from 'react';
import { useAccount } from '@/hooks/useAccount';
import { useScheduledPosts } from '../hooks/useScheduledPosts';
import { MediaUploader } from '@/components/scheduled-posts/MediaUploader';
import { ScheduleSelector } from '@/components/scheduled-posts/ScheduleSelector';
import { PostPreview } from '@/components/scheduled-posts/PostPreview';

export const CreatePostForm = () => {
  const { selectedAccount } = useAccount();
  const { createScheduledPost, loading } = useScheduledPosts();
  
  const [formData, setFormData] = useState({
    caption: '',
    scheduledTime: null,
    mediaFiles: [],
    mediaType: 'IMAGE'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccount) return;
    
    try {
      await createScheduledPost({
        accountId: selectedAccount.id,
        ...formData
      });
      // 成功処理
    } catch (error) {
      // エラーハンドリング
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <MediaUploader
        files={formData.mediaFiles}
        onChange={(files) => setFormData(prev => ({ ...prev, mediaFiles: files }))}
        mediaType={formData.mediaType}
        onMediaTypeChange={(type) => setFormData(prev => ({ ...prev, mediaType: type }))}
      />
      
      <div>
        <label className="block text-sm font-medium mb-2">キャプション</label>
        <textarea
          value={formData.caption}
          onChange={(e) => setFormData(prev => ({ ...prev, caption: e.target.value }))}
          className="w-full p-3 border rounded-lg"
          rows={4}
          maxLength={2200}
          placeholder="投稿のキャプションを入力..."
        />
      </div>
      
      <ScheduleSelector
        value={formData.scheduledTime}
        onChange={(time) => setFormData(prev => ({ ...prev, scheduledTime: time }))}
      />
      
      <PostPreview formData={formData} />
      
      <button
        type="submit"
        disabled={loading || !formData.mediaFiles.length || !formData.scheduledTime}
        className="w-full py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50"
      >
        {loading ? '作成中...' : '予約投稿を作成'}
      </button>
    </form>
  );
};
```

### Frontend: カレンダー表示

```tsx
// frontend/src/feature/scheduled-posts/components/CalendarView.tsx
'use client';

import { useState } from 'react';
import { Calendar } from '@/components/ui/calendar';
import { useCalendar } from '../hooks/useCalendar';
import { PostCard } from '@/components/scheduled-posts/PostCard';

export const CalendarView = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const { postsForDate, loading } = useCalendar(selectedDate);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1">
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={(date) => date && setSelectedDate(date)}
          className="rounded-md border"
        />
      </div>
      
      <div className="lg:col-span-2">
        <h3 className="text-lg font-semibold mb-4">
          {selectedDate.toLocaleDateString('ja-JP')} の予約投稿
        </h3>
        
        {loading ? (
          <div>読み込み中...</div>
        ) : postsForDate.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            この日の予約投稿はありません
          </div>
        ) : (
          <div className="space-y-4">
            {postsForDate.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

### Header.tsx更新 (ナビゲーション追加)

```tsx
// frontend/src/components/common/Header.tsx (更新部分)
export default function Header() {
  // ... 既存のコード

  return (
    <header className="flex justify-between items-center p-4 border-b" style={{ backgroundColor: '#c0b487', color: '#ffffff' }}>
      <nav className="flex items-center gap-2">
        <Button variant="outline" asChild className="border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white">
          <Link href="/post_insight">投稿分析</Link>
        </Button>
        <Button variant="outline" asChild className="border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white">
          <Link href="/scheduled-posts">予約投稿</Link>
        </Button>
        <Button variant="outline" asChild className="border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white">
          <Link href="/scheduled-posts/calendar">投稿カレンダー</Link>
        </Button>
      </nav>
      {/* ... 既存のアカウント選択部分 */}
    </header>
  );
}
```

---

## 🔄 API設計

### RESTful API エンドポイント

```yaml
予約投稿管理:
  POST   /api/v1/scheduled-posts           # 予約投稿作成
  GET    /api/v1/scheduled-posts           # 予約投稿一覧取得
  GET    /api/v1/scheduled-posts/{id}      # 予約投稿詳細取得
  PUT    /api/v1/scheduled-posts/{id}      # 予約投稿更新
  DELETE /api/v1/scheduled-posts/{id}      # 予約投稿削除

カレンダー:
  GET    /api/v1/scheduled-posts/calendar  # カレンダー用データ取得

メディア管理:
  POST   /api/v1/media/upload              # メディアアップロード
  GET    /api/v1/media                     # メディア一覧取得
  DELETE /api/v1/media/{id}                # メディア削除

システム:
  POST   /api/v1/scheduled-posts/execute   # 手動実行 (テスト用)
  GET    /api/v1/scheduled-posts/status    # システム状態確認
```

---

## 📦 依存関係・新規パッケージ

### Backend追加パッケージ

```txt
# requirements.txt に追加
celery>=5.3.0              # バックグラウンドタスク
redis>=5.0.0               # Celeryブローカー  
Pillow>=10.0.0             # 画像処理
python-multipart>=0.0.6    # ファイルアップロード
aiofiles>=23.0.0           # 非同期ファイル操作
python-magic>=0.4.27       # ファイルタイプ判定
```

### Frontend追加パッケージ

```json
// package.json に追加
{
  "dependencies": {
    "react-dropzone": "^14.2.3",           // ファイルドロップ
    "react-calendar": "^4.6.0",            // カレンダーコンポーネント  
    "date-fns": "^2.30.0",                 // 日時操作
    "react-hook-form": "^7.48.0",          // フォーム管理
    "zod": "^3.22.4",                      // バリデーション
    "react-query": "^4.36.1",              // データフェッチング
    "react-image-crop": "^10.1.8",         // 画像クロップ
    "sharp": "^0.32.6"                     // 画像処理 (サーバーサイド)
  }
}
```

---

## 🚀 実装優先順位

### Phase 1: 基本機能 (2-3週間)
```markdown
1. データベースマイグレーション
2. 基本的なCRUD API
3. 簡易フォーム画面
4. メディアアップロード機能
```

### Phase 2: スケジューリング (2週間)  
```markdown
1. バックグラウンドタスク設定
2. Instagram API投稿機能
3. スケジューラー実装
4. エラーハンドリング
```

### Phase 3: UI/UX改善 (2週間)
```markdown
1. カレンダー表示
2. 投稿プレビュー
3. 詳細なステータス管理
4. レスポンシブデザイン
```

### Phase 4: 運用機能 (1週間)
```markdown
1. ログ・監視機能
2. メディアクリーンアップ
3. 権限管理
4. API制限対応
```

---

## 🎯 統合ポイント

### 既存機能との統合
1. **アカウント管理**: Header.tsxのアカウント選択機能をそのまま活用
2. **認証・権限**: 既存のinstagram_accountモデルのaccess_token_encryptedを使用
3. **API構造**: 既存のapi_v1_routerに新エンドポイントを追加
4. **UI/UXパターン**: 既存のfeature構造とコンポーネント設計パターンを踏襲

### 新機能の独立性
1. **モジュラー設計**: scheduled-posts機能は独立したモジュールとして実装
2. **設定分離**: 予約投稿特有の設定は専用の設定ファイルで管理
3. **テストの分離**: 既存機能への影響を最小限に抑えた単体テスト

---

この設計により、既存のFastAPI + Next.jsアプリケーションに予約投稿機能を効率的に統合できます。段階的な実装により、リスクを最小限に抑えながら機能追加が可能です。