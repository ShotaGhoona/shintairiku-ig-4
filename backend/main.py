from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re

from app.api.v1 import api_v1_router

app = FastAPI(
    title="Instagram Analysis API",
    description="FastAPI backend for Instagram Analysis application",
    version="1.0.0",
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