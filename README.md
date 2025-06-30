# TTS Pronunciation Practice

A desktop application for practicing English pronunciation with text-to-speech and IPA (International Phonetic Alphabet) display. Features automatic clipboard monitoring, system tray integration, a comprehensive IPA dictionary, and auto-update.

**GitHub Repository**: [https://github.com/needyamin/tts-pronunciation-practice](https://github.com/needyamin/tts-pronunciation-practice)

## Features

- **Text-to-Speech**: Hear the pronunciation of any English word
- **IPA Display**: See the International Phonetic Alphabet pronunciation
- **Smart Dictionary**: Uses multiple sources for accurate IPA:
  - Large CMU dictionary (170,000+ words)
  - Custom corrections for specific words
  - Fallback to eng-to-ipa library
- **Ultra-Fast Clipboard Monitoring**: Automatically detects and processes copied text within 10ms
- **System Tray**: Runs in background with system tray icon (single instance)
- **History**: Clickable history of previously looked-up words
- **Modern UI**: Clean, intuitive interface with beautiful design
- **Subprocess-Based TTS**: Each speech session runs in complete isolation for maximum reliability
- **Instant Stop Control**: Stop button responds immediately and terminates speech instantly
- **Auto-Clean Text**: Automatically removes formatting and extra spaces
- **Auto-Update System**: Automatic and manual update checks with GitHub integration
- **Auto Start on Windows Login**: Enable/disable from Settings to launch the app automatically when Windows starts

## Screenshots

The application features a clean interface with:
- Word input field with speak and stop buttons
- Large IPA pronunciation display
- Scrollable history of previous words
- System tray icon for background operation

## Installation

### Prerequisites

- Python 3.7 or higher
- Windows 10/11 (tested on Windows)

### Option 1: From Source (Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/needyamin/tts-pronunciation-practice.git
   cd tts-pronunciation-practice
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python speak.py
   ```

### Option 2: From Executable (End Users)

#### Portable Version
- Download `TTS_Pronunciation_Practice.exe`
- Double-click to run immediately
- No installation required

#### Installer Version
- Download `TTS_Pronunciation_Practice_Setup.exe`
- Run the installer
- Follow the installation wizard
- Launch from Start Menu or Desktop shortcut

### Building Your Own Executable

See the [Building Executable](#building-executable) section for detailed instructions on creating your own portable or installer versions.

## Usage

### Basic Usage

1. **Type a word** in the input field
2. **Press Enter** or click the "🔊 Speak" button
3. **Hear the pronunciation** and see the IPA transcription

### Advanced Features

- **Ultra-Fast Clipboard Monitoring**: Copy any text to clipboard and it will automatically appear in the input field within 10ms
- **System Tray**: Right-click the tray icon to show/hide the window or quit
- **History**: Click on any word in the history to look it up again
- **Clear**: Use the "✖" button to clear the input field
- **Stop Speech**: Use the "⏹ Stop" button (appears during speech) to cancel ongoing pronunciation
- **Auto-Update**: Automatic update checks on startup and manual checks via button or system tray
- **Update Notifications**: Beautiful update dialog with release notes and download links

### Keyboard Shortcuts

- `Enter`: Speak the current word
- `Ctrl+C`: Copy any text to clipboard (auto-detected within 10ms)

# Settings File Location

- **When running from source**: Settings are saved in `asset/settings.json` in the project directory.
- **When running as an EXE**: Settings are saved in a user-writable directory:
  - On Windows: `%APPDATA%/TTS-Pronunciation-Practice/settings.json`
  - On other systems: `~/TTS-Pronunciation-Practice/settings.json`
- This ensures settings can always be saved, even if the EXE is in a protected folder.

## Dependencies

- **pyttsx3**: Text-to-speech engine
- **eng-to-ipa**: English to IPA conversion
- **Pillow**: Image processing for icons
- **pystray**: System tray integration
- **pyperclip**: Clipboard monitoring
- **requests**: HTTP requests for auto-update functionality
- **pyinstaller**: For building executable (development)
- **tkinter**: GUI framework (included with Python)
- **pywin32**: For Windows auto-start shortcut (Windows only)

## File Structure

```
tts-pronunciation-practice/
├── speak.py                  # Main application
├── build.py                  # Build script for executable
├── LICENSE                   # GPL-3.0 license
├── README.md                 # This file
├── asset/
│   ├── cmudict-0.7b-ipa.txt  # Large IPA dictionary (auto-downloaded)
│   ├── settings.json          # User settings
│   ├── requirements.txt       # Python dependencies
│   ├── y_icon_temp.ico        # Application icon (auto-generated)
│   └── github_profile.png     # Profile image for About dialog
├── build_exe/
│   ├── dist/
│   │   └── TTS_Pronunciation_Practice.exe      # Portable EXE build
│   ├── build_exe/
│   │   └── installer/
│   │       └── TTS_Pronunciation_Practice_Setup.exe  # Installer EXE
│   ├── setup.iss             # Inno Setup script
│   ├── speak.spec            # PyInstaller spec file
│   └── ...                   # Other build artifacts
└── .update_check             # (Optional) Update check timestamp
```

## How It Works

1. **IPA Dictionary**: The app uses a comprehensive CMU dictionary with 170,000+ English words and their IPA transcriptions
2. **Multiple Sources**: For words not in the main dictionary, it checks custom corrections and falls back to the eng-to-ipa library
3. **Text-to-Speech**: Uses pyttsx3 with Microsoft Zira voice (if available) for clear pronunciation
4. **Subprocess Isolation**: Each TTS session runs in a separate Python process for complete isolation and reliability
5. **Background Operation**: Runs in system tray with ultra-fast clipboard monitoring for seamless workflow
6. **Instant Stop**: Subprocess-based approach allows immediate termination of speech with no lingering state issues
7. **Auto Start**: Optionally launches automatically on Windows login (enable in Settings)

## Auto-Update System

- **Startup Check**: Automatically checks for updates after application launch
- **Manual Updates**: Click "Check for Updates" in the Help menu
- **Update Dialog**: Shows current vs. new version, release notes, and download/install options
- **Silent/Automatic Update**: Optionally downloads and installs the latest version automatically

## Building Executable

- Run `python build.py` to build a portable EXE and/or installer
- Output EXE: `build_exe/dist/TTS_Pronunciation_Practice.exe`
- Output Installer: `build_exe/build_exe/installer/TTS_Pronunciation_Practice_Setup.exe`

## Troubleshooting

- **No sound**: Check your system's audio settings and ensure pyttsx3 is properly installed
- **Clipboard not working**: Ensure pyperclip is installed and clipboard access is allowed
- **System tray not showing**: Check if pystray is properly installed
- **Auto start not working**: Ensure pywin32 is installed and you have permission to create shortcuts

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- CMU Pronouncing Dictionary for the comprehensive IPA data
- eng-to-ipa library for fallback IPA conversion
- All the open-source libraries that make this possible
- GitHub community for hosting and collaboration

## Support

If you encounter any issues or have questions:
- Check the [GitHub Issues](https://github.com/needyamin/tts-pronunciation-practice/issues) page
- Create a new issue with detailed information
- Include debug output if available 