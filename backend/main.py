from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import re

from app.api.v1 import api_v1_router

app = FastAPI(
    title="Instagram Analysis API",
    description="FastAPI backend for Instagram Analysis application",
    version="1.0.0",
    redirect_slashes=False,  # trailing slashのリダイレクトを無効化
)

# CORS設定 - Vercelの全ドメインを許可
def is_vercel_domain(origin: str) -> bool:
    """Vercelドメインかどうかを判定"""
    vercel_patterns = [
        r"^https://localhost:3000$",
        r"^http://localhost:3000$", 
        r"^https://shintairiku-ig-4.*\.vercel\.app$",
        r"^https://.*\.vercel\.app$"
    ]
    return any(re.match(pattern, origin) for pattern in vercel_patterns)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost:3000|.*\.vercel\.app)$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["*"],
)

# HTTPS強制ミドルウェア（本番環境用）
@app.middleware("http")
async def force_https(request: Request, call_next):
    # RailwayのHTTPSヘッダーをチェック
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto and forwarded_proto == "https":
        # HTTPSの場合は通常処理
        response = await call_next(request)
        return response
    elif "railway.app" in str(request.url):
        # Railwayでのみ強制リダイレクト
        https_url = str(request.url).replace("http://", "https://", 1)
        return RedirectResponse(url=https_url, status_code=301)
    else:
        # localhost等は通常処理
        response = await call_next(request)
        return response

# API ルーター統合
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {"message": "Instagram Analysis API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)