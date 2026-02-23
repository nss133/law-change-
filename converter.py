"""
법제처 자료 → DOCX 변환 메인 스크립트
"""

import sys
import os
from parser import LegalDocParser
from docx_generator import DocxGenerator

def convert_legal_doc(txt_file: str, html_file: str, output_file: str):
    print("=" * 60)
    print("법제처 입법자료 → DOCX 변환기")
    print("=" * 60)

    print("\n[1단계] 파일 파싱 중...")
    parser = LegalDocParser()

    if os.path.exists(txt_file):
        with open(txt_file, 'r', encoding='utf-8') as f:
            txt_content = f.read()
        parser.parse_txt(txt_content)
        print(f"  ✓ TXT 파일 파싱 완료: {txt_file}")
    else:
        print(f"  ✗ TXT 파일을 찾을 수 없습니다: {txt_file}")
        return

    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        parser.parse_html(html_content)
        print(f"  ✓ HTML 파일 파싱 완료: {html_file}")
    else:
        print(f"  ✗ HTML 파일을 찾을 수 없습니다: {html_file}")
        return

    parser.extract_main_contents()

    print("\n[2단계] DOCX 문서 생성 중...")
    generator = DocxGenerator()

    generator.add_title(parser.data['law_name'])
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
        print("사용법: python converter.py <txt_file> <html_file> <output_file>")
        print("예시: python converter.py input.txt input.html output.docx")
        sys.exit(1)

    txt_file = sys.argv[1]
    html_file = sys.argv[2]
    output_file = sys.argv[3]

    convert_legal_doc(txt_file, html_file, output_file)
