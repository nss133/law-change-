"""
법제처 입법자료 파싱 모듈
- TXT 파일: 개정이유 및 개정문
- HTML 파일: 신구조문대비표
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

class LegalDocParser:
    """법제처 자료 파싱 클래스"""

    def __init__(self):
        self.data = {
            'law_name': '',
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

                    if '시행' not in old_text or len(old_text) > 100:
                        comparison_data.append((old_text, new_text))

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
