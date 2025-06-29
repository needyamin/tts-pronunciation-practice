# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all necessary modules
a = Analysis(
    ['speak.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cmudict-0.7b-ipa.txt', '.'),
        ('y_icon_temp.ico', '.') if os.path.exists('y_icon_temp.ico') else None,
    ],
    hiddenimports=[
        # Core TTS modules
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'pyttsx3.drivers.nsss',
        'pyttsx3.drivers.espeak',
        
        # GUI modules
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        
        # System tray
        'pystray',
        'pystray._util_win32',
        
        # IPA and clipboard
        'eng_to_ipa',
        'pyperclip',
        
        # Networking and requests
        'requests',
        'urllib.request',
        
        # System modules
        'subprocess',
        'tempfile',
        'platform',
        'socket',
        'psutil',
        'threading',
        'time',
        're',
        'json',
        'pathlib',
        'os',
        'sys',
        'gc',
        
        # Package management
        'pkg_resources',
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
        'pkg_resources.extern',
        'pkg_resources.extern.packaging',
        'pkg_resources.extern.packaging.version',
        'pkg_resources.extern.packaging.specifiers',
        'pkg_resources.extern.packaging.requirements',
        'pkg_resources.extern.pyparsing',
        'pkg_resources._vendor',
        'pkg_resources._vendor.packaging',
        'pkg_resources._vendor.packaging.version',
        'pkg_resources._vendor.packaging.specifiers',
        'pkg_resources._vendor.packaging.requirements',
        'pkg_resources._vendor.pyparsing',
        
        # Setuptools and distutils
        'setuptools',
        'distutils',
        
        # Encoding and locale
        'encodings',
        'codecs',
        'locale',
        
        # Additional system modules
        'ctypes',
        'ctypes.wintypes',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'multiprocessing',
        'concurrent.futures',
        'test',
        'unittest',
        'doctest',
    ],
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
    icon='y_icon_temp.ico' if os.path.exists('y_icon_temp.ico') else None,
    optimize=0,
    collect_submodules=['pyttsx3', 'pystray', 'PIL', 'requests', 'pkg_resources'],
) 