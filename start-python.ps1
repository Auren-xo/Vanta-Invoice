if (-not (Test-Path '.env')) { Write-Host 'Create .env from .env.example and set your PostgreSQL password first.' -ForegroundColor Yellow; exit 1 }
& .\.venv\Scripts\python.exe backend-python\init_database.py
& .\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend-python --reload --port 8000
