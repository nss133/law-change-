"""
법제처 입법자료 → DOCX 변환기 웹 UI
"""

import streamlit as st
import os
import tempfile
from parser import LegalDocParser
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

    txt_file = st.file_uploader(
        "개정이유문 (TXT 파일)",
        type=['txt'],
        help="법제처 개정이유 및 개정문이 포함된 TXT 파일"
    )

    html_file = st.file_uploader(
        "신구조문대비표 (HTML 파일)",
        type=['html', 'htm'],
        help="신구조문대비표 HTML 파일"
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

    if not txt_file or not html_file:
        st.error("⚠️ TXT 파일과 HTML 파일을 모두 업로드해주세요.")
    else:
        with st.spinner("🔄 변환 중입니다..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_txt:
                    tmp_txt.write(txt_file.getvalue())
                    tmp_txt_path = tmp_txt.name

                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_html:
                    tmp_html.write(html_file.getvalue())
                    tmp_html_path = tmp_html.name

                parser = LegalDocParser()

                with open(tmp_txt_path, 'r', encoding='utf-8') as f:
                    txt_content = f.read()
                parser.parse_txt(txt_content)

                with open(tmp_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                parser.parse_html(html_content)

                parser.extract_main_contents()

                generator = DocxGenerator()
                generator.add_title(parser.data['law_name'])
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
                    # 분리형: 1. 개정이유 → 2. 주요내용 → 3. 파급효과 → 4. 신구조문 대비표
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

                if impact_text.strip():
                    final_impact = impact_text.strip()
                else:
                    final_impact = f"{parser.data['law_name']} 개정에 따른 실무 영향을 면밀히 검토하여 관련 업무에 반영 바람."

                generator.add_section("2" if is_combined else "3", "파급효과", final_impact, is_bold=True)
                generator.add_section("3" if is_combined else "4", "신구조문 대비표")
                generator.add_comparison_table(parser.data['comparison_table'])

                output_filename = f"{parser.data['law_name']}_시행안내.docx"
                output_path = os.path.join(tempfile.gettempdir(), output_filename)
                generator.save(output_path)

                os.unlink(tmp_txt_path)
                os.unlink(tmp_html_path)

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
