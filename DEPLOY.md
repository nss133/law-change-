# 배포 가이드

## 1단계: 실행 파일 만들기 (한 번만)

배포 담당자 PC에서만 수행합니다. **Python이 설치된 환경**이 필요합니다.

```bash
# 1. 프로젝트 폴더로 이동
cd legal_doc_converter

# 2. 가상환경 활성화 (있는 경우)
source venv/bin/activate   # Mac/Linux
# 또는  venv\Scripts\activate   # Windows

# 3. PyInstaller 설치
pip install pyinstaller

# 4. 빌드 실행
pyinstaller --clean build_streamlit.spec
```

## 2단계: 배포할 파일

빌드가 완료되면 **아래 폴더/파일**을 팀원에게 전달합니다.

| 플랫폼 | 경로 | 전달할 것 |
|--------|------|-----------|
| **Mac** | `dist/LegalDocConverter` | 이 파일 하나 |
| **Windows** | `dist/LegalDocConverter.exe` | 이 파일 하나 |

- 이메일로 첨부
- 또는 공유 드라이브/폴더에 업로드

## 3단계: 팀원 사용 방법

1. 받은 파일을 **바탕화면이나 원하는 폴더**에 저장
2. **더블클릭**으로 실행
3. 잠시 후 브라우저가 자동으로 열림
4. 파일 업로드 → 변환 → 다운로드

### 주의사항
- **Python 설치 불필요**
- **인터넷 불필요** (완전 로컬 동작)
- 실행 시 **브라우저가 자동**으로 열림
- 프로그램을 종료하려면 **터미널 창**(있다면) 또는 작업 관리자에서 종료
