@echo off
echo [🔁] 서버와 ngrok 자동 실행을 시작합니다...

REM ▶ Python 서버 실행 (백그라운드로 새 창)
start "" cmd /k "python server.py"

REM ▶ ngrok 실행 (같은 폴더에 ngrok.exe 있어야 함)
timeout /t 2
start "" cmd /k ".\ngrok.exe http 5000"

echo [✅] 서버와 ngrok이 모두 실행되었습니다.
pause
