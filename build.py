#!/usr/bin/env python3
"""
Build script for TTS Pronunciation Practice application
Creates a standalone executable using PyInstaller
Supports both portable and installer modes with Inno Setup
"""

import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path

def get_user_choice():
    """Get user choice for build type"""
    print("TTS Pronunciation Practice - Build Options")
    print("=" * 50)
    print("1. Portable Executable (standalone .exe file)")
    print("2. Installer (creates both .exe and installer)")
    print("=" * 50)
    
    while True:
        try:
            choice = input("Select build type (1 or 2): ").strip()
            if choice == "1":
                return "portable"
            elif choice == "2":
                return "installer"
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nBuild cancelled.")
            sys.exit(0)

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("Installing requirements...")
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("✗ requirements.txt not found")
            return False
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def check_inno_setup():
    """Check if Inno Setup is installed"""
    # Check common Inno Setup installation paths
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    for path in inno_paths:
        if os.path.exists(path):
            print(f"✓ Inno Setup found at: {path}")
            return path
    
    print("✗ Inno Setup not found. Please install Inno Setup 6 from:")
    print("  https://jrsoftware.org/isinfo.php")
    print("  Or use portable mode instead.")
    return None

def download_ipa_dict():
    """Download the IPA dictionary if not present"""
    ipa_dict_path = "cmudict-0.7b-ipa.txt"
    ipa_dict_url = "https://raw.githubusercontent.com/menelik3/cmudict-ipa/master/cmudict-0.7b-ipa.txt"
    
    if not os.path.exists(ipa_dict_path):
        print("Downloading IPA dictionary...")
        try:
            urllib.request.urlretrieve(ipa_dict_url, ipa_dict_path)
            print("✓ IPA dictionary downloaded successfully")
        except Exception as e:
            print(f"✗ Failed to download IPA dictionary: {e}")
            return False
    else:
        print("✓ IPA dictionary already exists")
    return True

def create_spec_file():
    """Create a PyInstaller spec file for the application"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['speak.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cmudict-0.7b-ipa.txt', '.'),
        ('y_icon_temp.ico', '.') if os.path.exists('y_icon_temp.ico') else None,
    ],
    hiddenimports=[
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'pyttsx3.drivers.nsss',
        'pyttsx3.drivers.espeak',
        'pystray._util_win32',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'eng_to_ipa',
        'pyperclip',
        'threading',
        'time',
        're',
        'json',
        'pathlib',
        'urllib.request',
        'requests',
        'pystray',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'socket',
        'psutil',
        'subprocess',
        'tempfile',
        'platform',
        'pkg_resources',
        'setuptools',
        'distutils',
        'encodings',
        'codecs',
        'locale',
        'os',
        'sys',
        'gc',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'multiprocessing',
        'concurrent.futures',
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
)
'''
    
    # Clean up None entries from datas
    spec_content = spec_content.replace("('y_icon_temp.ico', '.') if os.path.exists('y_icon_temp.ico') else None,", "")
    spec_content = spec_content.replace("icon='y_icon_temp.ico' if os.path.exists('y_icon_temp.ico') else None,", "")
    
    with open('speak.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ PyInstaller spec file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build using comprehensive spec file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "speak_comprehensive.spec"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def create_inno_setup_script():
    """Create Inno Setup script for installer"""
    # Check if LICENSE file exists
    license_line = "LicenseFile=LICENSE" if os.path.exists("LICENSE") else ";LicenseFile=LICENSE  ; License file not found"
    
    inno_script = f'''[Setup]
AppName=TTS Pronunciation Practice
AppVersion=1.0
AppPublisher=needyamin
AppPublisherURL=https://github.com/needyamin/tts-pronunciation-practice
AppSupportURL=https://github.com/needyamin/tts-pronunciation-practice/issues
AppUpdatesURL=https://github.com/needyamin/tts-pronunciation-practice
DefaultDirName={{autopf}}\\TTS Pronunciation Practice
DefaultGroupName=TTS Pronunciation Practice
AllowNoIcons=yes
{license_line}
OutputDir=installer
OutputBaseFilename=TTS_Pronunciation_Practice_Setup
SetupIconFile=y_icon_temp.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\\TTS_Pronunciation_Practice.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "cmudict-0.7b-ipa.txt"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "y_icon_temp.ico"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\TTS Pronunciation Practice"; Filename: "{{app}}\\TTS_Pronunciation_Practice.exe"
Name: "{{group}}\\{{cm:UninstallProgram,TTS Pronunciation Practice}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\TTS Pronunciation Practice"; Filename: "{{app}}\\TTS_Pronunciation_Practice.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\TTS Pronunciation Practice"; Filename: "{{app}}\\TTS_Pronunciation_Practice.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\TTS_Pronunciation_Practice.exe"; Description: "{{cm:LaunchProgram,TTS Pronunciation Practice}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
'''
    
    with open('setup.iss', 'w', encoding='utf-8') as f:
        f.write(inno_script)
    
    print("✓ Inno Setup script created")

def build_installer(inno_path):
    """Build installer using Inno Setup"""
    print("Building installer...")
    
    # Create installer directory
    if not os.path.exists('installer'):
        os.makedirs('installer')
    
    # Build installer
    cmd = [inno_path, "setup.iss"]
    try:
        subprocess.check_call(cmd)
        print("✓ Installer built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Installer build failed: {e}")
        return False

def create_portable_package():
    """Create portable package with executable and dependencies"""
    print("Creating portable package...")
    
    # Create portable directory
    portable_dir = "portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    os.makedirs(portable_dir)
    
    # Copy executable
    if os.path.exists("dist/TTS_Pronunciation_Practice.exe"):
        shutil.copy2("dist/TTS_Pronunciation_Practice.exe", portable_dir)
        print("✓ Portable executable created")
        return True
    else:
        print("✗ Executable not found")
        return False

def main():
    """Main build process"""
    print("TTS Pronunciation Practice - Build Script")
    print("=" * 50)
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("✗ This build script is designed for Windows only")
        return False
    
    # Get user choice
    build_type = get_user_choice()
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Check/install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Step 3: Download IPA dictionary
    if not download_ipa_dict():
        print("Warning: IPA dictionary not available, but continuing...")
    
    # Step 4: Create spec file
    create_spec_file()
    
    # Step 5: Build executable
    if not build_executable():
        return False
    
    # Step 6: Handle build type
    if build_type == "installer":
        # Check for Inno Setup
        inno_path = check_inno_setup()
        if inno_path:
            create_inno_setup_script()
            if build_installer(inno_path):
                print("\n" + "=" * 50)
                print("INSTALLER BUILD COMPLETED SUCCESSFULLY!")
                print("=" * 50)
                print("\nFiles created:")
                print("- dist/TTS_Pronunciation_Practice.exe (Portable executable)")
                print("- installer/TTS_Pronunciation_Practice_Setup.exe (Installer)")
                print("\nTo install:")
                print("1. Run TTS_Pronunciation_Practice_Setup.exe")
                print("2. Follow the installation wizard")
                print("\nTo run portable version:")
                print("- Double-click TTS_Pronunciation_Practice.exe")
            else:
                print("Installer build failed, but portable executable is available.")
        else:
            print("Inno Setup not found. Creating portable package only.")
            create_portable_package()
    else:  # portable
        create_portable_package()
        print("\n" + "=" * 50)
        print("PORTABLE BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\nFiles created:")
        print("- portable/TTS_Pronunciation_Practice.exe (Portable executable)")
        print("\nTo run:")
        print("- Double-click TTS_Pronunciation_Practice.exe")
    
    print("\nGitHub Repository:")
    print("https://github.com/needyamin/tts-pronunciation-practice")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1) 