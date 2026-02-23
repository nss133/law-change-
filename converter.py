"""
법제처 자료 → DOCX 변환 메인 스크립트
"""

import sys
import os
from parser import LegalDocParser, read_reason_doc
from docx_generator import DocxGenerator

def convert_legal_doc(reason_file: str, table_file: str, output_file: str):
    """reason_file: 개정이유문 (TXT 또는 PDF). table_file: 신구조문대비표 (HTML 또는 PDF)."""
    print("=" * 60)
    print("법제처 입법자료 → DOCX 변환기")
    print("=" * 60)

    print("\n[1단계] 파일 파싱 중...")
    parser = LegalDocParser()

    if not os.path.exists(reason_file):
        print(f"  ✗ 개정이유문 파일을 찾을 수 없습니다: {reason_file}")
        return
    reason_text = read_reason_doc(reason_file)
    parser.parse_txt(reason_text)
    print(f"  ✓ 개정이유문 파싱 완료: {reason_file}")

    if not os.path.exists(table_file):
        print(f"  ✗ 신구조문대비표 파일을 찾을 수 없습니다: {table_file}")
        return
    if table_file.lower().endswith('.pdf'):
        parser.parse_pdf(table_file)
        print(f"  ✓ PDF 파일 파싱 완료: {table_file}")
    else:
        with open(table_file, 'r', encoding='utf-8') as f:
            parser.parse_html(f.read())
        print(f"  ✓ HTML 파일 파싱 완료: {table_file}")

    parser.extract_main_contents()

    print("\n[2단계] DOCX 문서 생성 중...")
    generator = DocxGenerator()

    doc_type = parser.data.get('doc_type', 'enforcement')
    if doc_type == 'gosi':
        title_suffix = "고시 규정변경예고 안내"
    elif doc_type == 'notice':
        title_suffix = "입법예고 안내"
    else:
        title_suffix = "시행 안내"
    generator.add_title(f"{parser.data['law_name']} {title_suffix}")
    generator.add_metadata(
        parser.data['enforcement_date'],
        parser.data['law_number'],
        parser.data['amendment_date']
    )

    is_combined = parser.data.get('is_combined_format', True)

    if is_combined:
        reason_paragraphs = parser.data.get('amendment_reason_paragraphs', [])
        if reason_paragraphs:
            generator.add_section("1", "개정이유 및 주요내용", reason_paragraphs)
        else:
            generator.add_section("1", "개정이유 및 주요내용", parser.data['amendment_reason'])
    else:
        reason_paragraphs = parser.data.get('amendment_reason_paragraphs', [])
        if reason_paragraphs:
            generator.add_section("1", "개정이유", reason_paragraphs)
        else:
            generator.add_section("1", "개정이유", parser.data['amendment_reason'])
        generator.add_section("2", "주요내용")
        generator.add_main_contents(
            contents=[],
            intro_paragraphs=parser.data.get('main_contents_from_txt')
        )

    impact_text = f"{parser.data['law_name']} 개정에 따른 실무 영향을 면밀히 검토하여 관련 업무에 반영 바람."
    generator.add_section("2" if is_combined else "3", "파급효과", impact_text, is_bold=True)

    generator.add_section("3" if is_combined else "4", "신구조문 대비표")
    generator.add_comparison_table(parser.data['comparison_table'])

    print("\n[3단계] 파일 저장 중...")
    generator.save(output_file)

    print("\n" + "=" * 60)
    print("✅ 변환 완료!")
    print(f"📄 출력 파일: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("사용법: python converter.py <개정이유문_TXT또는PDF> <신구조문대비표_HTML또는PDF> <output_file>")
        print("예시(시행): python converter.py input.txt input.html output.docx")
        print("예시(입법예고): python converter.py notice.pdf comparison.pdf output.docx")
        sys.exit(1)

    reason_file = sys.argv[1]
    table_file = sys.argv[2]
    output_file = sys.argv[3]

    convert_legal_doc(reason_file, table_file, output_file)
