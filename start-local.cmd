@echo off
setlocal

set "PROJECT_ROOT=%~dp0"

if not exist "%PROJECT_ROOT%server\venv\Scripts\activate.bat" (
    echo Backend virtual environment not found at server\venv.
    echo Create it or update start-local.cmd to use your environment path.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%client\package.json" (
    echo Frontend project not found at client\package.json.
    pause
    exit /b 1
)

start "Support AI Backend" /D "%PROJECT_ROOT%server" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver"
start "Support AI Ticket Worker" /D "%PROJECT_ROOT%server" cmd /k "call venv\Scripts\activate.bat && python manage.py run_ticket_worker"
start "Support AI Frontend" /D "%PROJECT_ROOT%client" cmd /k "npm run dev"

echo Started backend, ticket worker, and frontend in separate windows.
endlocal
