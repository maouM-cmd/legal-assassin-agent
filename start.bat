@echo off
cd /d %~dp0
.\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8001
