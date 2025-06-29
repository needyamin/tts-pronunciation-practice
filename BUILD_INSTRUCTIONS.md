# TTS Pronunciation Practice - Build Instructions

## Issues Fixed

The following issues have been resolved in this version:

1. **Multiple GUI Windows**: Removed subprocess approach that was causing multiple Python instances
2. **Python Errors**: Replaced subprocess TTS with threading approach for better compatibility
3. **Single Instance Check**: Added socket-based check to prevent multiple application instances
4. **Better Error Handling**: Improved error handling throughout the application

## Building the Application

### Prerequisites

1. Python 3.7 or higher
2. All requirements from `requirements.txt`
3. PyInstaller (will be installed automatically)
4. Inno Setup 6 (optional, for installer creation)

### Quick Build

1. Run the build script:
   ```bash
   python build.py
   ```

2. Choose your build type:
   - Option 1: Portable executable (standalone .exe)
   - Option 2: Installer (creates both .exe and installer)

### Manual Build

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Build with PyInstaller:
   ```bash
   pyinstaller speak.spec
   ```

3. The executable will be in the `dist/` folder.

## Testing

### Test TTS Functionality

Before building, test the TTS functionality:

```bash
python test_speak.py
```

This will verify that:
- TTS engine initializes correctly
- Voices are available
- Speech synthesis works

### Test the Application

1. Run the Python version:
   ```bash
   python speak.py
   ```

2. Test basic functionality:
   - Type a word and press Enter
   - Check if IPA pronunciation appears
   - Verify TTS works without errors

## Troubleshooting

### Common Issues

1. **"No module named 'pyttsx3'"**
   - Install: `pip install pyttsx3`

2. **"No module named 'eng_to_ipa'"**
   - Install: `pip install eng_to_ipa`

3. **TTS not working in compiled executable**
   - Ensure all hidden imports are included in `speak.spec`
   - Check that the IPA dictionary file is included

4. **Multiple windows opening**
   - The single instance check should prevent this
   - If it still happens, check for multiple Python processes

### Debug Mode

To run with console output for debugging:

1. Edit `speak.spec` and change `console=False` to `console=True`
2. Rebuild the application
3. Run the executable to see console output

## File Structure

```
Pronunciation/
├── speak.py              # Main application
├── speak.spec            # PyInstaller specification
├── build.py              # Build script
├── test_speak.py         # TTS test script
├── requirements.txt      # Python dependencies
├── cmudict-0.7b-ipa.txt  # IPA dictionary
├── settings.json         # User settings (created automatically)
└── installer/            # Installer output (if using Inno Setup)
```

## Version Information

- Current Version: 1.0.0
- Build Date: Updated with fixes
- Python Compatibility: 3.7+

## Support

If you encounter issues:

1. Run `test_speak.py` to verify TTS functionality
2. Check console output for error messages
3. Ensure all dependencies are installed
4. Try running the Python version first before building 