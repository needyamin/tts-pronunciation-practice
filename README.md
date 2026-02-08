# TTS Pronunciation Practice

A modern desktop application built with Electron for practicing English pronunciation using Text-to-Speech (TTS) and IPA (International Phonetic Alphabet) display.

## Features

- **Text-to-Speech:** Hear the pronunciation of any English word or phrase.
- **IPA Display:** View the phonetic transcription of words.
- **Voice Selection:** Choose from installed system voices.
- **Clipboard Monitoring:** Automatically detect copied text and speak/display IPA (configurable).
- **History:** Keep track of recently practiced words.
- **Customizable:** Adjust speech rate, volume, and toggle features via settings.
- **System Tray:** Minimizes to the system tray for easy access.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/needyamin/tts-pronunciation-practice.git
    cd tts-pronunciation-practice
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

## Usage

### Running Locally

To start the application in development mode:

```bash
npm start
```

### Building the Application

To build the standalone executable (portable version):

```bash
npm run pack
```

The build output will be located in the `release-builds/` directory. You will find a folder named `tts-pronunciation-win32-x64` containing the executable `tts-pronunciation.exe`.

## Technologies Used

- **Electron:** Cross-platform desktop application framework.
- **Web Speech API:** Native browser speech synthesis.
- **CMU Dict:** Source for IPA pronunciation data.
- **Electron Store:** Persistent settings management.

## License

This project is licensed under the ISC License.
