# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 빌드 설정
# 실행: pyinstaller build.spec

block_cipher = None

a = Analysis(
    ['app_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['parser', 'docx_generator', 'docx', 'bs4', 'lxml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['streamlit'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LegalDocConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
