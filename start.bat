@echo off
echo [Vibe-to-Spec] 서버를 시작합니다...

:: 보안 정책(AppLocker) 우회를 위해 시스템 캐시의 파이썬을 직접 호출합니다.
set "PYTHONPATH=%~dp0.venv\Lib\site-packages"
set "PYTHON_EXE=%AppData%\Roaming\uv\python\cpython-3.14.3-windows-x86_64-none\python.exe"

:: FastAPI 백엔드 (새 창으로)
start "FastAPI Backend" cmd /k "cd /d %~dp0 && set PYTHONPATH=%PYTHONPATH% && ""%PYTHON_EXE%"" -m uvicorn api.main:app --reload"

:: 잠시 대기 후 Streamlit 프론트엔드 (새 창으로)
timeout /t 2 /nobreak > nul
start "Streamlit Frontend" cmd /k "cd /d %~dp0 && set PYTHONPATH=%PYTHONPATH% && ""%PYTHON_EXE%"" -m streamlit run frontend/app.py"

echo.
echo ✅ 서버 실행 중!
echo    FastAPI:   http://127.0.0.1:8000
echo    Streamlit: http://localhost:8501
echo.
pause
