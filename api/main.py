"""
FastAPI 앱 진입점
/api/chat 엔드포인트로 Streamlit 프론트엔드와 통신합니다.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.chat import router as chat_router

app = FastAPI(
    title="Vibe-to-Spec API",
    description="바이브 코딩 아이디어를 Agent-ready 스펙으로 변환하는 API",
    version="0.1.0",
)

# Streamlit 로컬 개발 시 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "vibe-to-spec"}
