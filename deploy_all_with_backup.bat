@echo off
set COMMENT=Автокоммит перед прод-деплоем

echo 🔄 Коммит всех изменений в dev
git checkout dev
git add .
git commit -m "%COMMENT%"
git push

echo 🔁 Переход в main и слияние
git checkout main
git pull
git merge dev
git push

echo 💾 Создание бэкапа
set "datetime=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "datetime=%datetime: =0%_%RANDOM%"
powershell Compress-Archive -Path * -DestinationPath "backups\backup_%datetime%.zip"

echo 🚀 Деплой на Fly.io
flyctl deploy

pause