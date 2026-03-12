@echo off
echo [Vibe-to-Spec] 서버를 시작합니다...

:: FastAPI 백엔드 (새 창으로)
start "FastAPI Backend" cmd /k "cd /d %~dp0 && uv run uvicorn api.main:app --reload"

:: 잠시 대기 후 Streamlit 프론트엔드 (새 창으로)
timeout /t 2 /nobreak > nul
start "Streamlit Frontend" cmd /k "cd /d %~dp0 && uv run streamlit run frontend/app.py"

echo.
echo ✅ 서버 실행 중!
echo    FastAPI:   http://127.0.0.1:8000
echo    Streamlit: http://localhost:8501
echo.
pause
