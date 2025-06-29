# TTS Pronunciation Practice

A desktop application for practicing English pronunciation with text-to-speech and IPA (International Phonetic Alphabet) display. Features automatic clipboard monitoring, system tray integration, and a comprehensive IPA dictionary.

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

## Dependencies

- **pyttsx3**: Text-to-speech engine
- **eng-to-ipa**: English to IPA conversion
- **Pillow**: Image processing for icons
- **pystray**: System tray integration
- **pyperclip**: Clipboard monitoring
- **requests**: HTTP requests for auto-update functionality
- **pyinstaller**: For building executable (development)
- **tkinter**: GUI framework (included with Python)

## File Structure

```
tts-pronunciation-practice/
├── speak.py              # Main application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── build.py             # Build script for executable
├── LICENSE              # GPL-3.0 license
├── cmudict-0.7b-ipa.txt # Large IPA dictionary (auto-downloaded)
├── y_icon_temp.ico      # Application icon (auto-generated)
├── setup.iss            # Inno Setup script (auto-generated)
├── portable/            # Portable build output
│   └── TTS_Pronunciation_Practice.exe
├── dist/                # PyInstaller build output
│   └── TTS_Pronunciation_Practice.exe
└── installer/           # Installer build output
    └── TTS_Pronunciation_Practice_Setup.exe
```

## How It Works

1. **IPA Dictionary**: The app downloads a comprehensive CMU dictionary with 170,000+ English words and their IPA transcriptions
2. **Multiple Sources**: For words not in the main dictionary, it checks custom corrections and falls back to the eng-to-ipa library
3. **Text-to-Speech**: Uses pyttsx3 with Microsoft Zira voice (if available) for clear pronunciation
4. **Subprocess Isolation**: Each TTS session runs in a separate Python process for complete isolation and reliability
5. **Background Operation**: Runs in system tray with ultra-fast clipboard monitoring for seamless workflow
6. **Instant Stop**: Subprocess-based approach allows immediate termination of speech with no lingering state issues

## Auto-Update System

The application includes a comprehensive auto-update system:

### Automatic Updates
- **Startup Check**: Automatically checks for updates 2 seconds after application launch
- **Rate Limiting**: Only checks once per hour to avoid excessive API calls
- **Background Processing**: Update checks run in background threads without blocking the UI

### Manual Updates
- **Update Button**: Click "🔄 Check for Updates" in the main interface
- **System Tray**: Right-click tray icon and select "Check for Updates"
- **Status Feedback**: Shows "Checking for updates..." message during manual checks

### Update Dialog
When an update is available, a beautiful dialog appears with:
- **Version Comparison**: Shows current vs. new version
- **Release Notes**: Scrollable text with detailed update information
- **Download Options**: Direct link to GitHub release page
- **Skip Option**: Choose to skip the update for now

### Configuration
The update system is configured via constants in `speak.py`:
```python
REPO_OWNER = "needyamin"
REPO_NAME = "tts-pronunciation-practice"
CURRENT_VERSION = "1.0.0"  # Update this when releasing new versions
```

### GitHub Integration
- **API Endpoint**: Uses GitHub Releases API for version checking
- **Release Tags**: Expects version tags in format `v1.0.1`, `v1.1.0`, etc.
- **Release Notes**: Displays the release body text in the update dialog
- **Download Links**: Provides direct links to GitHub release pages

## Building Executable

### Quick Build (Recommended)

```bash
python build.py
```

This will:
- **Automatically install all requirements** from requirements.txt
- **Install PyInstaller** if needed
- **Download the IPA dictionary** if not present
- **Ask for build type**: Portable or Installer
- **Create standalone executable** and/or professional installer

### Build Options

When you run `python build.py`, you'll be prompted to choose:

#### Option 1: Portable Executable
- Creates a standalone `.exe` file
- No installation required
- Ready to run immediately
- Output: `portable/TTS_Pronunciation_Practice.exe`

#### Option 2: Professional Installer
- Creates both portable `.exe` and professional installer
- Requires Inno Setup 6 (automatically detected)
- Modern Windows installation wizard
- Desktop shortcuts, Start Menu integration
- Output: 
  - `dist/TTS_Pronunciation_Practice.exe` (portable)
  - `installer/TTS_Pronunciation_Practice_Setup.exe` (installer)

### Inno Setup Installation

For the professional installer option, you'll need Inno Setup 6:

1. **Download Inno Setup 6**: [https://jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php)
2. **Install Inno Setup 6** on your system
3. **Run the build script again**: `python build.py`

The build script will automatically detect Inno Setup and create a professional installer.

### Manual Build (Advanced)

If you prefer manual control:

```bash
# Install requirements manually
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name=TTS_Pronunciation_Practice speak.py
```

## Customization

### Adding Custom IPA Pronunciations

Edit the `CUSTOM_IPA` dictionary in `speak.py`:

```python
CUSTOM_IPA = {
    "yamin": "jɑːˈmiːn",
    "million": "ˈmɪl.jən",
    "billion": "ˈbɪl.jən",
    "yourword": "ˈjɔːr.wɜːrd"
}
```

### Voice Settings

Modify voice properties in the code:

```python
engine.setProperty('rate', 150)  # Speed (words per minute)
# Change voice selection logic for different voices
```

### Version Management

To release a new version:

1. **Update Version Number**: Change `CURRENT_VERSION` in `speak.py`:
   ```python
   CURRENT_VERSION = "1.0.1"  # Increment version number
   ```

2. **Create GitHub Release**: 
   - Tag the release with version (e.g., `v1.0.1`)
   - Add release notes in the description
   - Upload the new executable files

3. **Build New Executable**: Run `python build.py` to create updated executables

The auto-update system will automatically detect the new version and notify users.

## Troubleshooting

### Common Issues

1. **No sound**: Check your system's audio settings and ensure pyttsx3 is properly installed
2. **Missing IPA**: Some words may not have IPA transcriptions available
3. **Clipboard not working**: Ensure pyperclip is installed and clipboard access is allowed
4. **System tray not showing**: Check if pystray is properly installed
5. **Multiple tray icons**: The app now ensures only one tray icon exists

### Voice Issues

If the default voice doesn't work well:
- The app tries to use Microsoft Zira voice
- You can modify the voice selection logic in the code
- Different systems may have different available voices

### Debug Mode

The application includes debug output to help troubleshoot issues:
- Check console output for `[DEBUG]` messages
- These show clipboard detection, word processing, and speech status

## Development

### Adding Features

The code is well-structured and modular. Key areas for extension:
- `speak_text()`: Main pronunciation logic
- `clipboard_monitor()`: Clipboard detection
- `setup_tray()`: System tray functionality
- `update_history_ui()`: History display

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

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