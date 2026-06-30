$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
& .\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8001
