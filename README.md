# 법제처 입법자료 → DOCX 변환기

## 개요
법제처에서 발표하는 입법예고자료(개정이유문, 신구조문대비표)를 
회사 내부 보고용 표준 양식 DOCX 파일로 자동 변환하는 도구입니다.

## ✨ 데스크톱 앱 (추천)

**더블클릭으로 실행! 터미널·브라우저 불필요**

```bash
python app_gui.py
```

또는 **실행 파일**로 배포 (아래 [배포 방법](#배포-방법) 참고)

---

## 설치 방법

### 1. Python 설치
Python 3.8 이상이 필요합니다.

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 사용 방법

### 🖥️ 방법 1: 데스크톱 GUI (추천)

```bash
python app_gui.py
```

- 파일 선택 → 변환하여 저장 → 완료
- Python만 설치되어 있으면 바로 실행

### 🌐 방법 2: 웹 UI

```bash
streamlit run app.py
```

브라우저에서 파일을 드래그앤드롭하여 변환

### 💻 방법 3: 커맨드라인

```bash
python converter.py <txt파일> <html파일> <출력파일.docx>
```

**예시:**
```bash
python converter.py test_input.txt test_input.html output.docx
```

---

## 출력 형식
표준 보고서 양식:
1. 제목 및 메타데이터
2. 개정 이유
3. 주요내용 (가, 나, 다... 형식)
4. 파급효과
5. 신구조문 대비표

---

## 빠른 시작 🚀

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 웹 UI 실행
streamlit run app.py

# 3. 브라우저에서 http://localhost:8501 접속

# 4. 파일 업로드 → 변환 → 다운로드!
```

---

## 배포 방법 (팀원 공유)

Python 없이 **실행 파일**로 배포하려면:

### 1. PyInstaller 설치

```bash
pip install pyinstaller
```

### 2. 빌드 실행

- **Mac/Linux**: `./build.sh`
- **Windows**: `build.bat` 더블클릭

### 3. 배포

- `dist/` 폴더 안의 **LegalDocConverter** (Mac: .app, Windows: .exe)를 팀원에게 전달
- 더블클릭만 하면 사용 가능 (별도 설치 불필요)

---

## 문의
법무팀 담당자에게 문의 바랍니다.
