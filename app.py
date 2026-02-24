"""
법제처 입법자료 → DOCX 변환기 웹 UI
"""

import streamlit as st
import os
import tempfile
from parser import LegalDocParser, read_reason_doc
from docx_generator import DocxGenerator
from datetime import datetime

st.set_page_config(
    page_title="법제처 입법자료 변환기",
    page_icon="📄",
    layout="wide"
)

st.title("📄 법제처 입법자료 → DOCX 변환기")
st.markdown("---")

with st.sidebar:
    st.header("📌 사용 안내")
    st.markdown("""
    ### 변환 절차
    1. **TXT 파일** 업로드 (개정이유문)
    2. **HTML 파일** 업로드 (신구조문대비표)
    3. **파급효과** 내용 입력 (선택)
    4. **변환 시작** 버튼 클릭
    5. **DOCX 다운로드**

    ---

    ### 입력 파일 형식
    - **TXT**: 법제처 개정이유 및 개정문
    - **HTML**: 신구조문대비표

    ---

    ### 출력 형식
    - 회사 표준 보고서 양식
    - 제목, 개정이유, 주요내용, 파급효과, 신구조문대비표 포함
    """)

    st.markdown("---")
    st.info("💡 문의: 법무팀")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 1단계: 파일 업로드")

    reason_file = st.file_uploader(
        "개정이유문 (TXT 또는 PDF)",
        type=['txt', 'pdf'],
        help="법제처 개정이유·입법예고·규정변경예고 문 (TXT 또는 PDF)"
    )

    table_file = st.file_uploader(
        "신구조문대비표 (HTML 또는 PDF)",
        type=['html', 'htm', 'pdf'],
        help="시행안내: HTML / 입법예고: PDF"
    )

with col2:
    st.subheader("⚙️ 2단계: 옵션 설정")

    dept = st.text_input(
        "작성 부서",
        value="법 무 팀",
        help="보고서 상단에 표시될 부서명"
    )

    today = datetime.now().strftime("%y. %m.")
    write_date = st.text_input(
        "작성일",
        value=today,
        help="보고서 작성일 (예: 25. 01.)"
    )

    impact_text = st.text_area(
        "파급효과 (선택사항)",
        height=150,
        help="파급효과를 직접 입력하거나 비워두면 기본 템플릿 사용",
        placeholder="실무에 미치는 영향을 간략히 작성하세요..."
    )

st.markdown("---")

if st.button("🚀 변환 시작", type="primary", use_container_width=True):

    if not reason_file or not table_file:
        st.error("⚠️ 개정이유문(TXT/PDF)과 신구조문대비표(HTML 또는 PDF) 파일을 모두 업로드해주세요.")
    else:
        with st.spinner("🔄 변환 중입니다..."):
            try:
                reason_content = read_reason_doc(reason_file.getvalue(), filename=reason_file.name)

                table_suffix = '.pdf' if table_file.name.lower().endswith('.pdf') else '.html'
                with tempfile.NamedTemporaryFile(delete=False, suffix=table_suffix) as tmp_table:
                    tmp_table.write(table_file.getvalue())
                    tmp_table_path = tmp_table.name

                parser = LegalDocParser()
                parser.parse_txt(reason_content)

                if table_suffix == '.pdf':
                    parser.parse_pdf(tmp_table_path)
                else:
                    with open(tmp_table_path, 'r', encoding='utf-8') as f:
                        parser.parse_html(f.read())

                parser.extract_main_contents()

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
                    parser.data['amendment_date'],
                    date=write_date,
                    dept=dept
                )

                is_combined = parser.data.get('is_combined_format', True)

                if is_combined:
                    # 통합형: 1. 개정이유 및 주요내용 → 2. 파급효과 → 3. 신구조문 대비표
                    reason_paragraphs = parser.data.get('amendment_reason_paragraphs', [])
                    if reason_paragraphs:
                        generator.add_section("1", "개정이유 및 주요내용", reason_paragraphs)
                    else:
                        generator.add_section("1", "개정이유 및 주요내용", parser.data['amendment_reason'])
                else:
                    # 분리형: 1. 개정이유 → 2. 주요내용 → [3. 의견제출기한] → 4. 파급효과 → 5. 신구조문 대비표
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
                    # 입법예고/고시: 3. 의견제출기한 (날짜만)
                    opinion_deadline = parser.data.get('opinion_deadline', '')
                    if opinion_deadline:
                        generator.add_section("3", "의견제출기한", opinion_deadline)

                if impact_text.strip():
                    final_impact = impact_text.strip()
                else:
                    final_impact = f"{parser.data['law_name']} 개정에 따른 실무 영향을 면밀히 검토하여 관련 업무에 반영 바람."

                sec_impact = "2" if is_combined else "4"
                sec_table = "3" if is_combined else "5"
                generator.add_section(sec_impact, "파급효과", final_impact, is_bold=True)
                generator.add_section(sec_table, "신구조문 대비표")
                generator.add_comparison_table(parser.data['comparison_table'])

                doc_type = parser.data.get('doc_type', 'enforcement')
                if doc_type == 'gosi':
                    suffix = "고시_규정변경예고안내"
                elif doc_type == 'notice':
                    suffix = "입법예고안내"
                else:
                    suffix = "시행안내"
                output_filename = f"{parser.data['law_name']}_{suffix}.docx"
                output_path = os.path.join(tempfile.gettempdir(), output_filename)
                generator.save(output_path)

                os.unlink(tmp_table_path)

                st.success("✅ 변환이 완료되었습니다!")

                with st.expander("📋 파싱 결과 미리보기"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("법령명", parser.data['law_name'])
                    with col_b:
                        st.metric("시행일", parser.data['enforcement_date'])
                    with col_c:
                        st.metric("주요내용 항목", len(parser.data['main_contents']))

                    st.markdown("**개정 이유 (요약)**")
                    st.info(parser.data['amendment_reason'][:200] + "...")

                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="📥 DOCX 다운로드",
                        data=f,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )

                os.unlink(output_path)

            except Exception as e:
                st.error(f"❌ 변환 중 오류가 발생했습니다: {str(e)}")
                st.exception(e)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>법제처 입법자료 변환기 v1.0 | 법무팀 © 2026</p>
</div>
""", unsafe_allow_html=True)
