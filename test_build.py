#!/usr/bin/env python3
"""
Test script to verify build configuration
"""

import os
import sys
import subprocess

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    modules_to_test = [
        'tkinter',
        'pyttsx3',
        'eng_to_ipa',
        'PIL',
        'pystray',
        'pyperclip',
        'requests',
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
        'threading',
        'time',
        're',
        'json',
        'pathlib',
        'urllib.request',
        'socket',
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def test_pyinstaller():
    """Test PyInstaller installation and basic functionality"""
    print("\nTesting PyInstaller...")
    
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        
        # Test basic PyInstaller functionality
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ PyInstaller version: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ PyInstaller test failed: {result.stderr}")
            return False
            
    except ImportError:
        print("✗ PyInstaller is not installed")
        return False

def test_spec_file():
    """Test that the spec file exists and is valid"""
    print("\nTesting spec file...")
    
    spec_files = ['speak.spec', 'speak_comprehensive.spec']
    
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            print(f"✓ {spec_file} exists")
            
            # Test basic syntax
            try:
                with open(spec_file, 'r') as f:
                    content = f.read()
                    # Basic syntax check
                    if 'Analysis(' in content and 'EXE(' in content:
                        print(f"✓ {spec_file} appears to be valid")
                    else:
                        print(f"✗ {spec_file} appears to be invalid")
                        return False
            except Exception as e:
                print(f"✗ Error reading {spec_file}: {e}")
                return False
        else:
            print(f"✗ {spec_file} not found")
            return False
    
    return True

def main():
    """Run all tests"""
    print("Build Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("PyInstaller", test_pyinstaller),
        ("Spec Files", test_spec_file),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Build configuration is ready.")
        print("\nTo build the executable, run:")
        print("  python build.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before building.")
    
    return all_passed

if __name__ == "__main__":
    main() 