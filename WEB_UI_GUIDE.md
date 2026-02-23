# 웹 UI 실행 가이드

## Streamlit 웹 인터페이스

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 웹 앱 실행

```bash
streamlit run app.py
```

실행 후 자동으로 브라우저가 열립니다.
- 로컬 URL: http://localhost:8501
- 네트워크 URL: http://[your-ip]:8501

### 3. 사용 방법

1. **TXT 파일 업로드**: 개정이유문 드래그앤드롭
2. **HTML 파일 업로드**: 신구조문대비표 드래그앤드롭
3. **옵션 설정**: 
   - 작성 부서 (기본: 법 무 팀)
   - 작성일 (기본: 현재 날짜)
   - 파급효과 (선택 입력)
4. **변환 시작** 버튼 클릭
5. **DOCX 다운로드** 버튼으로 파일 저장

### 4. 특징

✅ 드래그앤드롭 파일 업로드  
✅ 실시간 미리보기 파싱 결과 확인  
✅ 사용자 정의 작성 부서, 날짜, 파급효과  
✅ 원클릭 다운로드 변환된 DOCX 파일  
✅ 반응형 디자인 모바일/태블릿 지원  

### 5. 트러블슈팅

#### 포트 충돌 시
```bash
streamlit run app.py --server.port 8502
```

#### 외부 접속 허용 시
```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 문의
법무팀 담당자
