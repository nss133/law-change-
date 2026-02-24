"""
법제처 입법자료 파싱 모듈
- 개정이유문: TXT 또는 PDF
- HTML 파일: 신구조문대비표 (시행안내)
- PDF 파일: 신구조문대비표 (입법예고/고시)
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Union

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def _skip_comparison_row(old_text: str, new_text: str) -> bool:
    """연락처·부처명 등 대비표에 불필요한 행 스킵"""
    if not (old_text or new_text):
        return True
    skip_terms = (
        "연락처", "전화", "팩스", "전자우편", "일반우편",
        "기획행정실", "금융소비자정책과", "중소금융과",
        "의안 소관 부서명", "문서보안"
    )
    return any(t in old_text or t in new_text for t in skip_terms)


def read_reason_doc(source: Union[str, bytes], filename: str = None) -> str:
    """개정이유문 내용 추출. source=파일경로(str) 또는 내용(bytes), filename=업로드 시 파일명."""
    if isinstance(source, bytes):
        if filename and filename.lower().endswith(".pdf"):
            if pdfplumber is None:
                raise ImportError("PDF 개정이유문을 위해 pip install pdfplumber 가 필요합니다.")
            import io
            with pdfplumber.open(io.BytesIO(source)) as pdf:
                parts = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
                return "\n".join(parts)
        return source.decode("utf-8", errors="replace")
    # source is file path
    if str(source).lower().endswith(".pdf"):
        if pdfplumber is None:
            raise ImportError("PDF 개정이유문을 위해 pip install pdfplumber 가 필요합니다.")
        with pdfplumber.open(source) as pdf:
            parts = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts)
    with open(source, "r", encoding="utf-8") as f:
        return f.read()

class LegalDocParser:
    """법제처 자료 파싱 클래스"""

    def __init__(self):
        self.data = {
            'law_name': '',
            'doc_type': 'enforcement',  # enforcement | notice
            'enforcement_date': '',
            'law_number': '',
            'amendment_date': '',
            'amendment_reason': '',
            'main_contents': [],
            'impact_analysis': '',
            'comparison_table': []
        }

    def parse_txt(self, txt_content: str) -> Dict:
        """TXT 파일에서 개정이유 추출"""
        lines = txt_content.strip().split('\n')

        # 고시 규정변경예고 / 입법예고문 형식 검사 (동일 구조: 1.개정이유, 2.주요내용, 3.의견제출)
        for line in lines[:15]:
            if '규정변경예고' in line:
                return self._parse_notice_style_txt(lines, doc_type='gosi')
            if '입법예고' in line:
                return self._parse_notice_style_txt(lines, doc_type='notice')

        # 법령명 추출
        self.data['law_name'] = lines[0].strip() if lines else ''

        # 시행일, 법률번호 추출
        for line in lines[:5]:
            if '[시행' in line and '[법률' in line:
                enforcement_match = re.search(r'\[시행\s+([^\]]+)\]', line)
                law_number_match = re.search(r'\[법률\s+제(\d+)호,\s+([^,]+),\s+([^\]]+)\]', line)

                if enforcement_match:
                    self.data['enforcement_date'] = enforcement_match.group(1).strip()
                if law_number_match:
                    self.data['law_number'] = law_number_match.group(1).strip()
                    self.data['amendment_date'] = law_number_match.group(2).strip()

        # 개정이유 및 주요내용 추출 (문단 단위로 분리)
        reason_start = False
        reason_paragraphs = []  # 문단별로 저장
        current_paragraph = []
        in_main_contents = False
        main_contents_from_txt = []  # TXT에 별도 주요내용 섹션이 있는 경우
        is_combined_format = True  # "개정이유 및 주요내용" 통합형인 경우

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # "개정이유 및 주요내용" 통합형 섹션
            if '◇ 개정이유 및 주요내용' in line:
                reason_start = True
                is_combined_format = True
                continue

            # "개정이유" 단독 섹션
            if '개정이유' in line and '주요내용' not in line:
                reason_start = True
                continue

            # "주요내용" 별도 섹션 (개정이유와 분리된 경우)
            if reason_start and ('◇ 주요내용' in line or '▶ 주요내용' in line or line_stripped == '주요내용'):
                if current_paragraph:
                    reason_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                in_main_contents = True
                is_combined_format = False
                continue

            if reason_start:
                if '>> 개정문' in line or (line_stripped and line.startswith('<법제처')):
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        if in_main_contents:
                            main_contents_from_txt.append(para_text)
                        else:
                            reason_paragraphs.append(para_text)
                    break
                if line_stripped:
                    current_paragraph.append(line_stripped)
                else:
                    # 빈 줄 = 문단 구분
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        if in_main_contents:
                            main_contents_from_txt.append(para_text)
                        else:
                            reason_paragraphs.append(para_text)
                        current_paragraph = []
        else:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                if in_main_contents:
                    main_contents_from_txt.append(para_text)
                else:
                    reason_paragraphs.append(para_text)

        # 기존 호환: 단일 문자열도 유지 (문단 리스트 + 통합 문자열)
        self.data['amendment_reason'] = ' '.join(reason_paragraphs).strip()
        self.data['amendment_reason_paragraphs'] = [p for p in reason_paragraphs if p]
        self.data['main_contents_from_txt'] = main_contents_from_txt
        self.data['is_combined_format'] = is_combined_format

        return self.data

    def _parse_notice_style_txt(self, lines: List[str], doc_type: str) -> Dict:
        """입법예고/고시 규정변경예고 TXT에서 개정이유·주요내용 추출 (1.개정이유, 2.주요내용, 3.의견제출)"""
        self.data['doc_type'] = doc_type

        # 법령명: 「...」 안의 내용 우선 사용
        for line in lines:
            m = re.search(r'「(.+?)」', line)
            if m:
                self.data['law_name'] = m.group(1).strip()
                break
        if not self.data['law_name'] and lines:
            self.data['law_name'] = lines[0].strip()

        # 고시 규정변경예고: 제목용 법령명에서 ' 일부개정고시안' 등 제거
        if doc_type == 'gosi':
            self.data['law_name'] = re.sub(r'\s*일부개정고시안\s*$', '', self.data['law_name'])

        # 구간 인덱스 찾기
        idx_reason = idx_main = idx_etc = idx_etc_end = None
        for i, line in enumerate(lines):
            if idx_reason is None and re.search(r'1\.\s*개정이유', line):
                idx_reason = i
            elif idx_main is None and re.search(r'2\.\s*주요내용', line):
                idx_main = i
            elif idx_etc is None and re.search(r'3\.\s*의견제출', line):
                idx_etc = i
            elif idx_etc is not None and idx_etc_end is None and re.search(r'4\.\s*그\s*밖의\s*사항', line):
                idx_etc_end = i

        if idx_reason is None:
            idx_reason = 0
        if idx_main is None:
            idx_main = len(lines)
        if idx_etc is None:
            idx_etc = len(lines)
        if idx_etc_end is None:
            idx_etc_end = len(lines)

        reason_lines = [l.strip() for l in lines[idx_reason + 1:idx_main] if l.strip()]
        main_lines = [l.strip() for l in lines[idx_main + 1:idx_etc] if l.strip()]
        etc_lines = [l.strip() for l in lines[idx_etc + 1:idx_etc_end] if l.strip()]

        reason_text = ' '.join(reason_lines).strip()
        main_text = ' '.join(main_lines).strip()

        # 3. 의견제출에서 마감일만 추출 (예: 2026년 3월 4일 → 2026. 3. 4.)
        opinion_deadline = ''
        etc_full = ' '.join(etc_lines)
        m = re.search(r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일', etc_full)
        if m:
            opinion_deadline = f"{m.group(1)}. {int(m.group(2))}. {int(m.group(3))}."

        self.data['amendment_reason'] = reason_text
        self.data['amendment_reason_paragraphs'] = [reason_text] if reason_text else []
        self.data['main_contents_from_txt'] = [main_text] if main_text else []
        self.data['opinion_deadline'] = opinion_deadline
        self.data['is_combined_format'] = False

        return self.data

    def parse_html(self, html_content: str) -> List[Tuple]:
        """HTML 신구조문대비표 파싱"""
        soup = BeautifulSoup(html_content, 'html.parser')

        tables = soup.find_all('table')
        comparison_data = []

        for table in tables:
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all(['td', 'th'])

                if len(cols) >= 2:
                    old_text = cols[0].get_text(separator='\n').strip()
                    new_text = cols[1].get_text(separator='\n').strip()

                    if _skip_comparison_row(old_text, new_text):
                        continue
                    if '시행' not in old_text or len(old_text) > 100:
                        comparison_data.append((old_text, new_text))

        self.data['comparison_table'] = comparison_data
        return comparison_data

    def parse_pdf(self, pdf_source: Union[str, bytes]) -> List[Tuple[str, str]]:
        """PDF 신구조문대비표 파싱 (입법예고용). 현행/개정안 2열 표 추출."""
        if pdfplumber is None:
            raise ImportError("PDF 파싱을 위해 pip install pdfplumber 가 필요합니다.")

        comparison_data = []
        is_path = isinstance(pdf_source, str)

        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    if not table:
                        continue
                    for row in table:
                        cells = [c.strip() if c else "" for c in (row or [])]
                        if len(cells) >= 2:
                            old_t, new_t = cells[0].replace("\n", " ").strip() if cells[0] else "", cells[1].replace("\n", " ").strip() if cells[1] else ""
                            if not old_t and not new_t:
                                continue
                            if _skip_comparison_row(old_t, new_t):
                                continue
                            if "시행" in old_t and "시행" in new_t and len(old_t) < 100 and len(new_t) < 100:
                                continue
                            comparison_data.append((old_t, new_t))

        self.data['comparison_table'] = comparison_data
        return comparison_data

    def extract_main_contents(self) -> List[Dict]:
        """신구조문대비표에서 주요내용 추출"""
        main_contents = []
        last_article = None

        for idx, (old_text, new_text) in enumerate(self.data['comparison_table']):
            # 현행과 같음 = 변경 없음, 스킵
            if '현행과 같음' in new_text or '생 략' in new_text:
                article_match = re.search(r'제(\d+조[^\(]*)', new_text)
                if article_match:
                    last_article = article_match.group(1)
                continue

            # 조문 번호: 현재 행 또는 이전 행에서 추출
            article_match = re.search(r'제(\d+조[^\(]*)', new_text)
            if article_match:
                last_article = article_match.group(1)
                article_num = last_article
            elif last_article and ('<신 설>' in old_text or '신 설' in old_text or '<삭 제>' in new_text or '삭 제' in new_text):
                article_num = last_article
            else:
                continue

            change_type = '개정'
            if '<신 설>' in old_text or '신 설' in old_text:
                change_type = '신설'
            elif '<삭 제>' in new_text or '삭 제' in new_text:
                change_type = '삭제'

            content = {
                'article': article_num,
                'type': change_type,
                'old': old_text[:300],
                'new': new_text[:300],
                'description': self._generate_description(article_num, change_type, old_text, new_text)
            }

            main_contents.append(content)

        self.data['main_contents'] = main_contents
        return main_contents

    def _generate_description(self, article: str, change_type: str, old: str, new: str) -> str:
        """조문별 설명 자동 생성"""
        if change_type == '신설':
            return f"{article} 신설"
        elif change_type == '삭제':
            return f"{article} 삭제"
        else:
            return f"{article} 개정"
