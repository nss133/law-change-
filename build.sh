#!/bin/bash
# Mac/Linux 빌드 스크립트
# 사용: ./build.sh

set -e
cd "$(dirname "$0")"

echo "=== 법제처 입법자료 변환기 빌드 ==="

if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller가 설치되어 있지 않습니다."
    echo "설치: pip install pyinstaller"
    exit 1
fi

# venv 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

pyinstaller --clean build.spec

echo ""
echo "빌드 완료! 실행 파일: dist/LegalDocConverter (Mac: dist/LegalDocConverter.app)"
echo "팀원에게 dist 폴더의 실행 파일을 배포하세요."
