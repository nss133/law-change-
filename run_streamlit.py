"""
Streamlit 앱 실행 래퍼 - PyInstaller 빌드용
- 더블클릭 시 Streamlit 서버 시작 + 브라우저 자동 열기
"""

import sys
import webbrowser
import threading
import time
import os

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)

# app.py 경로
APP_PATH = os.path.join(BASE_DIR, 'app.py')
if not os.path.exists(APP_PATH):
    APP_PATH = 'app.py'


def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:8501')


def main():
    # Streamlit CLI로 직접 실행 (subprocess 불필요)
    sys.argv = [
        'streamlit', 'run', APP_PATH,
        '--server.headless', 'true',
        '--server.port', '8501',
        '--browser.gatherUsageStats', 'false',
    ]

    # 브라우저 자동 열기 (별도 스레드)
    threading.Thread(target=open_browser, daemon=True).start()

    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == '__main__':
    main()
