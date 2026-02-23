"""
법제처 입법자료 → DOCX 변환기 (데스크톱 GUI)
- 더블클릭으로 실행 가능
- Streamlit/터미널 불필요
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import sys

# PyInstaller 번들 시 작업 디렉토리
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from parser import LegalDocParser
from docx_generator import DocxGenerator


def convert_document(txt_path: str, html_path: str, output_path: str,
                     write_date: str, dept: str, impact_text: str) -> str:
    """변환 로직 (app.py와 동일)"""
    parser = LegalDocParser()

    with open(txt_path, 'r', encoding='utf-8') as f:
        parser.parse_txt(f.read())

    with open(html_path, 'r', encoding='utf-8') as f:
        parser.parse_html(f.read())

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

    if impact_text.strip():
        final_impact = impact_text.strip()
    else:
        final_impact = f"{parser.data['law_name']} 개정에 따른 실무 영향을 면밀히 검토하여 관련 업무에 반영 바람."

    generator.add_section("2" if is_combined else "3", "파급효과", final_impact, is_bold=True)
    generator.add_section("3" if is_combined else "4", "신구조문 대비표")
    generator.add_comparison_table(parser.data['comparison_table'])

    generator.save(output_path)
    return parser.data['law_name']


class ConverterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("법제처 입법자료 → DOCX 변환기")
        self.root.geometry("560x520")
        self.root.resizable(True, True)

        self.txt_path = tk.StringVar()
        self.html_path = tk.StringVar()
        self.write_date = tk.StringVar(value=datetime.now().strftime("%y. %m."))
        self.dept = tk.StringVar(value="법 무 팀")

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # 제목
        title = ttk.Label(main, text="법제처 입법자료 → DOCX 변환기", font=("", 14, "bold"))
        title.pack(pady=(0, 16))

        # TXT 파일
        f1 = ttk.LabelFrame(main, text="1. 개정이유문 (TXT)", padding=10)
        f1.pack(fill=tk.X, pady=5)
        row1 = ttk.Frame(f1)
        row1.pack(fill=tk.X)
        ttk.Entry(row1, textvariable=self.txt_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row1, text="찾아보기", command=self._browse_txt).pack(side=tk.RIGHT)

        # HTML 파일
        f2 = ttk.LabelFrame(main, text="2. 신구조문대비표 (HTML)", padding=10)
        f2.pack(fill=tk.X, pady=5)
        row2 = ttk.Frame(f2)
        row2.pack(fill=tk.X)
        ttk.Entry(row2, textvariable=self.html_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row2, text="찾아보기", command=self._browse_html).pack(side=tk.RIGHT)

        # 작성일 / 부서
        f3 = ttk.LabelFrame(main, text="3. 옵션", padding=10)
        f3.pack(fill=tk.X, pady=5)
        opt_row = ttk.Frame(f3)
        opt_row.pack(fill=tk.X)
        ttk.Label(opt_row, text="작성일:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(opt_row, textvariable=self.write_date, width=12).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(opt_row, text="부서:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(opt_row, textvariable=self.dept, width=15).pack(side=tk.LEFT)

        # 파급효과
        f4 = ttk.LabelFrame(main, text="4. 파급효과 (선택, 비워두면 기본 문구 사용)", padding=10)
        f4.pack(fill=tk.BOTH, expand=True, pady=5)
        self.impact_text = tk.Text(f4, height=6, width=60, wrap=tk.WORD, font=("", 10))
        self.impact_text.pack(fill=tk.BOTH, expand=True)
        self.impact_text.insert("1.0", "실무에 미치는 영향을 간략히 작성하세요...")

        # 변환 버튼
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="변환하여 저장", command=self._convert, style="Accent.TButton").pack(padx=5)
        ttk.Button(btn_frame, text="닫기", command=self.root.quit).pack(padx=5)

        # 푸터
        footer = ttk.Label(main, text="법제처 입법자료 변환기 v1.0 | 법무팀 © 2026", font=("", 8), foreground="gray")
        footer.pack(side=tk.BOTTOM, pady=10)

    def _browse_txt(self):
        path = filedialog.askopenfilename(
            title="개정이유문 (TXT) 선택",
            filetypes=[("TXT 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if path:
            self.txt_path.set(path)

    def _browse_html(self):
        path = filedialog.askopenfilename(
            title="신구조문대비표 (HTML) 선택",
            filetypes=[("HTML 파일", "*.html;*.htm"), ("모든 파일", "*.*")]
        )
        if path:
            self.html_path.set(path)

    def _convert(self):
        txt_path = self.txt_path.get().strip()
        html_path = self.html_path.get().strip()

        if not txt_path:
            messagebox.showerror("오류", "개정이유문 (TXT) 파일을 선택해주세요.")
            return
        if not html_path:
            messagebox.showerror("오류", "신구조문대비표 (HTML) 파일을 선택해주세요.")
            return
        if not os.path.exists(txt_path):
            messagebox.showerror("오류", f"TXT 파일을 찾을 수 없습니다:\n{txt_path}")
            return
        if not os.path.exists(html_path):
            messagebox.showerror("오류", f"HTML 파일을 찾을 수 없습니다:\n{html_path}")
            return

        impact_text = self.impact_text.get("1.0", tk.END).strip()
        if impact_text == "실무에 미치는 영향을 간략히 작성하세요...":
            impact_text = ""

        # 기본 파일명 제안을 위해 파싱 (법령명 필요)
        try:
            parser = LegalDocParser()
            with open(txt_path, 'r', encoding='utf-8') as f:
                parser.parse_txt(f.read())
            default_name = f"{parser.data['law_name']}_시행안내.docx"
        except Exception:
            default_name = "시행안내.docx"

        output_path = filedialog.asksaveasfilename(
            title="저장할 DOCX 파일 선택",
            defaultextension=".docx",
            initialfile=default_name,
            filetypes=[("Word 문서", "*.docx"), ("모든 파일", "*.*")]
        )

        if not output_path:
            return

        try:
            law_name = convert_document(
                txt_path, html_path, output_path,
                self.write_date.get().strip(),
                self.dept.get().strip(),
                impact_text
            )
            messagebox.showinfo("완료", f"변환이 완료되었습니다.\n\n저장 위치: {output_path}")
        except Exception as e:
            messagebox.showerror("변환 오류", str(e))

    def run(self):
        self.root.mainloop()


def main():
    app = ConverterApp()
    app.run()


if __name__ == "__main__":
    main()
