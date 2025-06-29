# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['speak.py'],
    pathex=[],
    binaries=[],
    datas=[('cmudict-0.7b-ipa.txt', '.')],
    hiddenimports=['pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'pyttsx3.drivers.nsss', 'pyttsx3.drivers.espeak', 'pystray._util_win32', 'PIL._tkinter_finder', 'eng_to_ipa', 'pyperclip', 'threading', 'time', 're'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TTS_Pronunciation_Practice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['y_icon_temp.ico'],
)
