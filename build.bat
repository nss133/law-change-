@echo off
REM Windows 빌드 스크립트
REM 사용: build.bat

cd /d "%~dp0"

echo === 법제처 입법자료 변환기 빌드 ===

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller가 설치되어 있지 않습니다.
    echo 설치: pip install pyinstaller
    pause
    exit /b 1
)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

pyinstaller --clean build.spec

echo.
echo 빌드 완료! 실행 파일: dist\LegalDocConverter.exe
echo 팀원에게 dist 폴더의 실행 파일을 배포하세요.
pause
