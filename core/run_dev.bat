@echo off
echo 🔧 Запуск DEV-бота

cd /d %~dp0..

set PYTHONPATH=%CD%
set PY_EXE=%CD%\.venv\Scripts\python.exe

echo [DEBUG] PYTHON USED:
%PY_EXE% -V

copy dev.env .env > nul

call "%PY_EXE%" -m app.main

del .env

pause
