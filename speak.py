import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import eng_to_ipa as ipa
import os
import urllib.request
import re
import threading
import time
import pystray
from PIL import Image, ImageDraw, ImageFont
import sys
import pyperclip
import requests
import json
from pathlib import Path

# Check for multiple instances
def check_single_instance():
    """Check if another instance is already running"""
    import socket
    try:
        # Try to bind to a specific port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 12345))  # Use a specific port
        sock.close()
        return True  # No other instance running
    except OSError:
        # Port is already in use, another instance is running
        return False

def cleanup_stray_processes():
    """Clean up any stray TTS-related processes"""
    try:
        import psutil
        current_pid = os.getpid()
        
        # Look for other Python processes that might be TTS-related
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] != current_pid:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('speak' in arg.lower() for arg in cmdline):
                        print(f"Found potential stray process: {proc.info['pid']}")
                        # Don't kill it automatically, just log it
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        # psutil not available, skip this check
        pass
    except Exception as e:
        print(f"Error checking for stray processes: {e}")

# Check if another instance is running
if not check_single_instance():
    try:
        # Try to show a message box
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showwarning("Application Already Running", 
                              "TTS Pronunciation Practice is already running.\nPlease close the existing instance first.")
        root.destroy()
    except:
        pass
    sys.exit(1)

# Clean up any stray processes
cleanup_stray_processes()

# Path to the large IPA dictionary file
IPA_DICT_PATH = os.path.join("asset", "cmudict-0.7b-ipa.txt")
IPA_DICT_URL = "https://raw.githubusercontent.com/menelik3/cmudict-ipa/master/cmudict-0.7b-ipa.txt"

# Custom IPA dictionary for special/corrected words
CUSTOM_IPA = {
    "yamin": "jɑːˈmiːn",
    "million": "ˈmɪl.jən",
    "billion": "ˈbɪl.jən"
}

# Looser IPA validation regex (includes more IPA symbols, diacritics, and punctuation)
IPA_REGEX = re.compile(r"^[ˈˌa-zA-Zɪʊəɔæɑɛʌθðŋʃʒɹɝɚɡɾɫʔʤʧːˑ˞ˠˤ̩̯̃ʼ˺ˈˌːˑ˞ˠˤ̩̯̃ʼ˺\.\s,\-]+$")

# Global settings variables
settings = {
    'tts_enabled': True,
    'clipboard_monitoring': True,
    'auto_speak': True,
    'speech_rate': 150,
    'voice_name': 'zira',
    'volume': 1.0,  # Volume level (0.0 to 1.0)
    'show_ipa': True  # Whether to show IPA pronunciation
}

# Settings file path
SETTINGS_FILE = Path(os.path.join("asset", "settings.json"))

def load_settings():
    """Load settings from file"""
    global settings
    try:
        settings_file = Path(os.path.join("asset", "settings.json"))
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Update settings with loaded values, keeping defaults for missing keys
                for key, value in loaded_settings.items():
                    if key in settings:
                        # Ensure proper type conversion
                        if key in ['tts_enabled', 'clipboard_monitoring', 'auto_speak', 'show_ipa']:
                            settings[key] = bool(value)
                        elif key == 'speech_rate':
                            settings[key] = int(value)
                        elif key == 'volume':
                            settings[key] = float(value)
                        else:
                            settings[key] = value
                print(f"Settings loaded from: {settings_file.absolute()}")
                print(f"Loaded settings: {settings}")
        else:
            # Create default settings file if it doesn't exist
            print(f"Settings file not found, creating default: {settings_file.absolute()}")
            save_settings_to_file()
    except Exception as e:
        print(f"Failed to load settings: {e}")
        # Create default settings file
        save_settings_to_file()

def save_settings_to_file():
    """Save settings to file"""
    try:
        with open(os.path.join("asset", "settings.json"), 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        print(f"Settings saved to: {Path(os.path.join('asset', 'settings.json')).absolute()}")
        
        if Path(os.path.join("asset", "settings.json")).exists():
            file_size = Path(os.path.join("asset", "settings.json")).stat().st_size
        else:
            pass
            
    except Exception as e:
        print(f"Failed to save settings: {e}")
        try:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
            json.dump(settings, temp_file, indent=2, ensure_ascii=False)
            temp_file.close()
            
            import shutil
            shutil.move(temp_file.name, os.path.join("asset", "settings.json"))
            print(f"Settings saved using alternative method: {Path(os.path.join('asset', 'settings.json')).absolute()}")
        except Exception as e2:
            print(f"Alternative save method also failed: {e2}")

# Load settings on startup
load_settings()

# Ensure settings file exists
if not Path(os.path.join("asset", "settings.json")).exists():
    print("Creating initial settings file...")
    save_settings_to_file()

def cleanup_all_engines():
    """Clean up all active TTS engines"""
    global active_engines, current_speech_engine, global_engine, singleton_engine, engine_in_use
    
    with engine_lock:
        # Stop and cleanup all tracked engines
        for engine in active_engines:
            try:
                if engine:
                    engine.stop()
            except Exception as e:
                print(f"Error stopping engine: {e}")
        
        # Clean up singleton engine
        if singleton_engine:
            try:
                singleton_engine.stop()
            except Exception as e:
                print(f"Error stopping singleton engine: {e}")
            singleton_engine = None
            engine_in_use = False
        
        # Clear the lists
        active_engines.clear()
        current_speech_engine = None
        global_engine = None

def create_tts_engine():
    """Create a new TTS engine with proper configuration - Singleton approach"""
    global singleton_engine, engine_in_use
    
    with engine_lock:
        # If we already have a singleton engine and it's not in use, reuse it
        if singleton_engine and not engine_in_use:
            try:
                # Test if the engine is still working
                singleton_engine.setProperty('rate', settings['speech_rate'])
                singleton_engine.setProperty('volume', settings['volume'])
                engine_in_use = True
                return singleton_engine
            except Exception as e:
                print(f"Singleton engine test failed, creating new one: {e}")
                # Engine is broken, create a new one
                try:
                    singleton_engine.stop()
                except:
                    pass
                singleton_engine = None
        
        # Create new engine
        try:
            new_engine = pyttsx3.init()
            
            # Set properties
            new_engine.setProperty('rate', settings['speech_rate'])
            new_engine.setProperty('volume', settings['volume'])
            
            # Set voice
            voices = new_engine.getProperty('voices')
            if voices:
                # Try to find the preferred voice
                voice_found = False
                for voice in voices:
                    if settings['voice_name'].lower() in voice.name.lower():
                        new_engine.setProperty('voice', voice.id)
                        voice_found = True
                        break
                
                # If preferred voice not found, use the first available
                if not voice_found:
                    new_engine.setProperty('voice', voices[0].id)
            
            # Set as singleton
            singleton_engine = new_engine
            engine_in_use = True
            
            # Track this engine
            active_engines.append(new_engine)
            
            return new_engine
            
        except Exception as e:
            print(f"Failed to create TTS engine: {e}")
            return None

def release_tts_engine(engine):
    """Release the TTS engine back to the pool"""
    global engine_in_use
    
    with engine_lock:
        if engine == singleton_engine:
            engine_in_use = False

def is_valid_english_ipa(s):
    # Only allow strings that are likely to be English IPA
    return bool(IPA_REGEX.match(s))

# Load the large IPA dictionary
large_ipa_dict = {}
def load_large_ipa_dict():
    global large_ipa_dict
    # Download the file if not present
    if not os.path.exists(IPA_DICT_PATH):
        try:
            print("Downloading large IPA dictionary...")
            urllib.request.urlretrieve(IPA_DICT_URL, IPA_DICT_PATH)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download IPA dictionary: {e}")
            return
    # Parse the file
    try:
        with open(IPA_DICT_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith(";"):
                    parts = line.strip().split("  ")
                    if len(parts) == 2:
                        word, ipa_val = parts
                        large_ipa_dict[word.lower()] = ipa_val
    except Exception as e:
        print(f"Failed to load IPA dictionary: {e}")

load_large_ipa_dict()

# Initialize pyttsx3
try:
    # Clean up any existing engines first
    cleanup_all_engines()
    
    engine = pyttsx3.init()
    
    # Set voice and rate based on settings
    # Find the voice by name
    selected_voice_id = None
    for voice in engine.getProperty('voices'):
        if settings['voice_name'].lower() in voice.name.lower():
            selected_voice_id = voice.id
            break

    # If no matching voice found, use the first available
    if not selected_voice_id:
        voices = engine.getProperty('voices')
        if voices:
            selected_voice_id = voices[0].id

    if selected_voice_id:
        engine.setProperty('voice', selected_voice_id)

    engine.setProperty('rate', settings['speech_rate'])
    engine.setProperty('volume', settings['volume'])
    
    # Set as the main engine
    singleton_engine = engine
    active_engines.append(engine)
    
except Exception as e:
    print(f"Failed to initialize TTS engine: {e}")
    engine = None

# Store history
history = []

# --- System Tray and Clipboard Monitoring ---
tray_icon = None
root = None
last_clipboard = ""
clipboard_thread = None
should_run_clipboard = True

# Thread-safe variables for speech
speech_thread = None
is_speaking = False
current_speech_engine = None
speech_lock = threading.Lock()
global_engine = None
# Add engine management variables
engine_lock = threading.Lock()
active_engines = []  # Track all active engines for cleanup
# Add singleton engine management
singleton_engine = None
engine_in_use = False

# --- Update Check Constants ---
REPO_OWNER = "needyamin"
REPO_NAME = "tts-pronunciation-practice"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
CURRENT_VERSION = "1.0.1"  # Update as needed
UPDATE_CHECK_FILE = Path(".update_check")

def compare_versions(v1, v2):
    def parse(v):
        return [int(x) for x in v.split('.') if x.isdigit()]
    return parse(v1) > parse(v2)

def debug_update_check(log):
    """Debug function to check update system status"""
    try:
        log("\n=== DEBUG: Update System Status ===")
        log(f"\nRepository Configuration:")
        log(f"Owner: {REPO_OWNER}")
        log(f"Name: {REPO_NAME}")
        log(f"API URL: {GITHUB_API_URL}")
        log(f"Current Version: {CURRENT_VERSION}")
        log(f"\nUpdate Check File Status:")
        if UPDATE_CHECK_FILE.exists():
            with open(UPDATE_CHECK_FILE, 'r') as f:
                last_check = float(f.read().strip())
                time_since_last_check = time.time() - last_check
                log(f"Last check: {time.ctime(last_check)}")
                log(f"Time since last check: {time_since_last_check/3600:.2f} hours")
        else:
            log("Update check file not found")
        log(f"\nTesting GitHub API Connection:")
        try:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'TTS-Pronunciation-Practice'
            }
            response = requests.get(GITHUB_API_URL, headers=headers)
            log(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release.get('tag_name', '').lstrip('v')
                log(f"Latest Release: {latest_version}")
                log(f"Release Details: {json.dumps(latest_release, indent=2)}")
            else:
                log(f"API Error: {response.text}")
        except Exception as e:
            log(f"API Connection Error: {str(e)}")
        log(f"\nTesting Version Comparison:")
        test_versions = [
            ("1.0.15", "1.0.14")
        ]
        for v1, v2 in test_versions:
            result = compare_versions(v1, v2)
            log(f"Compare {v1} > {v2}: {result}")
        log("\n=== DEBUG COMPLETED ===\n")
    except Exception as e:
        log(f"Debug Error: {str(e)}")

def check_for_updates():
    """Check for updates from GitHub releases"""
    try:
        # Check if we should skip this update check (to avoid too frequent checks)
        if UPDATE_CHECK_FILE.exists():
            with open(UPDATE_CHECK_FILE, 'r') as f:
                last_check = float(f.read().strip())
                # Only check once per hour
                if time.time() - last_check < 3600:
                    return None
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TTS-Pronunciation-Practice'
        }
        
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            
            # Save the check time
            with open(UPDATE_CHECK_FILE, 'w') as f:
                f.write(str(time.time()))
            
            # Compare versions
            if compare_versions(latest_version, CURRENT_VERSION):
                return {
                    'version': latest_version,
                    'url': latest_release.get('html_url', ''),
                    'body': latest_release.get('body', ''),
                    'download_url': latest_release.get('zipball_url', '')
                }
    except Exception as e:
        print(f"Update check failed: {e}")
    
    return None

def show_update_dialog(update_info):
    """Show update dialog to user"""
    if not root:
        return
    
    update_window = tk.Toplevel(root)
    update_window.title("Update Available")
    update_window.geometry("500x400")
    update_window.resizable(False, False)
    update_window.configure(bg="#f5f5f5")
    update_window.transient(root)
    update_window.grab_set()
    
    # Center the window
    update_window.update_idletasks()
    x = (update_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (update_window.winfo_screenheight() // 2) - (400 // 2)
    update_window.geometry(f"500x400+{x}+{y}")
    
    # Header
    header = tk.Label(update_window, text="🎉 Update Available!", font=("Segoe UI", 16, "bold"), 
                     bg="#f5f5f5", fg="#1a73e8")
    header.pack(pady=(20, 10))
    
    # Version info
    version_frame = tk.Frame(update_window, bg="#f5f5f5")
    version_frame.pack(pady=5)
    
    tk.Label(version_frame, text="Current Version:", font=("Segoe UI", 11), 
            bg="#f5f5f5", fg="#666").pack(side="left")
    tk.Label(version_frame, text=CURRENT_VERSION, font=("Segoe UI", 11, "bold"), 
            bg="#f5f5f5", fg="#333").pack(side="left", padx=(5, 20))
    
    tk.Label(version_frame, text="New Version:", font=("Segoe UI", 11), 
            bg="#f5f5f5", fg="#666").pack(side="left")
    tk.Label(version_frame, text=update_info['version'], font=("Segoe UI", 11, "bold"), 
            bg="#f5f5f5", fg="#1a73e8").pack(side="left", padx=(5, 0))
    
    # Release notes
    notes_frame = tk.Frame(update_window, bg="#f5f5f5")
    notes_frame.pack(pady=10, fill="both", expand=True, padx=20)
    
    tk.Label(notes_frame, text="What's New:", font=("Segoe UI", 12, "bold"), 
            bg="#f5f5f5", fg="#333").pack(anchor="w")
    
    # Scrollable text for release notes
    text_frame = tk.Frame(notes_frame, bg="#f5f5f5")
    text_frame.pack(fill="both", expand=True, pady=(5, 0))
    
    text_widget = tk.Text(text_frame, height=10, wrap="word", font=("Segoe UI", 10),
                         bg="white", fg="#333", relief="solid", bd=1)
    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Insert release notes
    notes = update_info.get('body', 'No release notes available.')
    text_widget.insert("1.0", notes)
    text_widget.config(state="disabled")
    
    # Buttons
    button_frame = tk.Frame(update_window, bg="#f5f5f5")
    button_frame.pack(pady=20)
    
    def download_update():
        import webbrowser
        webbrowser.open(update_info['url'])
        update_window.destroy()
    
    def skip_update():
        update_window.destroy()
    
    download_btn = tk.Button(button_frame, text="📥 Download Update", font=("Segoe UI", 12, "bold"),
                            bg="#1a73e8", fg="white", command=download_update,
                            relief="flat", padx=20, pady=8)
    download_btn.pack(side="left", padx=(0, 10))
    
    skip_btn = tk.Button(button_frame, text="Skip for Now", font=("Segoe UI", 12),
                        bg="#e0e0e0", fg="#333", command=skip_update,
                        relief="flat", padx=20, pady=8)
    skip_btn.pack(side="left")

def check_updates_in_background():
    def update_checker():
        try:
            update_info = check_for_updates()
            if update_info:
                root.after(0, lambda: show_update_dialog(update_info))
        except Exception as e:
            print(f"Background update check failed: {e}")
    
    threading.Thread(target=update_checker, daemon=True).start()

# Create a beautiful 'Y' logo for the tray and window icon
def create_image():
    image = Image.new('RGBA', (64, 64), color=(245, 245, 245, 0))
    d = ImageDraw.Draw(image)
    # Draw a colored circle background
    d.ellipse((4, 4, 60, 60), fill=(26, 115, 232, 255))
    # Draw a bold 'Y' in the center
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    text = "Y"
    try:
        # Pillow >= 8.0.0
        bbox = d.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Older Pillow fallback
        text_width, text_height = d.textsize(text, font=font)
    x = (64 - text_width) // 2
    y = (64 - text_height) // 2 - 2
    d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return image

def on_quit(icon, item):
    global should_run_clipboard, is_speaking, tray_icon
    should_run_clipboard = False
    is_speaking = False
    
    # Clean up all engines before exiting
    cleanup_all_engines()
    
    if tray_icon:
        try:
            tray_icon.visible = False
            tray_icon.stop()
        except Exception as e:
            print(f"Error stopping tray icon: {e}")
        finally:
            tray_icon = None
    
    if root:
        try:
            root.destroy()
        except Exception as e:
            print(f"Error destroying root window: {e}")
    
    sys.exit()

def show_window(icon, item):
    if root:
        root.after(0, root.deiconify)

def hide_window():
    if root:
        root.withdraw()
    global tray_icon
    if tray_icon and not tray_icon.visible:
        try:
            tray_icon.visible = True
        except Exception as e:
            print(f"Error making tray icon visible: {e}")

def on_closing():
    global is_speaking
    is_speaking = False
    
    # Clean up all engines when closing
    cleanup_all_engines()
    
    hide_window()

def setup_tray():
    global tray_icon
    if tray_icon is None:
        try:
            menu = pystray.Menu(
                pystray.MenuItem('Show', show_window),
                pystray.MenuItem('Quit', on_quit)
            )
            tray_icon = pystray.Icon("tts_pronunciation", create_image(), "TTS Pronunciation", menu)
            threading.Thread(target=tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            tray_icon = None
    else:
        if not tray_icon.visible:
            try:
                tray_icon.visible = True
            except Exception as e:
                print(f"Error making tray icon visible: {e}")

# Clipboard monitoring thread
def clipboard_monitor():
    global last_clipboard
    while should_run_clipboard:
        try:
            if not settings['clipboard_monitoring']:
                time.sleep(0.1)
                continue
                
            current = pyperclip.paste()
            
            if isinstance(current, str):
                cleaned_current = current.strip()
                cleaned_current = re.sub(r'[\r\n\t]', ' ', cleaned_current)
                cleaned_current = re.sub(r'\s+', ' ', cleaned_current)
                cleaned_current = cleaned_current.strip()
            else:
                cleaned_current = ""
            
            if cleaned_current != last_clipboard and cleaned_current and len(cleaned_current) > 0:
                last_clipboard = cleaned_current
                root.after(0, lambda: auto_paste_word(cleaned_current))
        except Exception as e:
            print(f"Clipboard error: {e}")
            pass
        time.sleep(0.01)

def auto_paste_word(word):
    if word and len(word) > 0:
        global is_speaking
        if is_speaking:
            is_speaking = False
            speak_btn.config(text="🔊 Speak", bg="#1a73e8")
            stop_btn.grid_remove()
        
        cleaned_word = word.strip()
        cleaned_word = re.sub(r'[\r\n\t]', ' ', cleaned_word)
        cleaned_word = re.sub(r'\s+', ' ', cleaned_word)
        cleaned_word = cleaned_word.strip()
        
        if cleaned_word and len(cleaned_word) > 0:
            entry.delete(0, tk.END)
            entry.insert(0, cleaned_word)
            entry.focus_set()
            
            if settings['auto_speak']:
                speak_text()

def stop_speech():
    global is_speaking, current_speech_engine, speech_thread, global_engine
    is_speaking = False
    
    # Clean up all engines properly
    cleanup_all_engines()
    
    speak_btn.config(text="🔊 Speak", bg="#1a73e8")
    stop_btn.grid_remove()
    
    # Force kill any running thread
    if speech_thread and speech_thread.is_alive():
        try:
            speech_thread.join(timeout=0.1)
        except Exception:
            pass
    speech_thread = None
    
    # Force cleanup
    import gc
    gc.collect()
    
    # Reset all state completely
    is_speaking = False

def speak_text(event=None):
    global speech_thread, is_speaking, current_speech_engine, global_engine
    
    if not settings['tts_enabled']:
        messagebox.showinfo("TTS Disabled", "Text-to-Speech is currently disabled in settings.")
        return
    
    # Always clean up any existing engines before starting
    cleanup_all_engines()
    
    # Reset state
    is_speaking = False
    
    if speech_thread and speech_thread.is_alive():
        try:
            speech_thread.join(timeout=0.05)
        except:
            pass
    speech_thread = None
    
    # Reduced delay for faster response
    time.sleep(0.05)
    
    text = entry.get().strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter some text.")
        return

    if text not in history:
        history.insert(0, text)
        update_history_ui()

    speak_btn.config(text="🔊 Speaking...", bg="#ff9800")
    stop_btn.grid()
    
    # Show initializing message
    ipa_label.config(text="Initializing TTS engine...", fg="#ff9800")
    
    # Use threading approach for complete isolation
    speech_thread = threading.Thread(target=speak_in_thread, args=(text,), daemon=True)
    speech_thread.start()

def speak_in_thread(text):
    """Thread function using threading approach"""
    global is_speaking
    
    try:
        is_speaking = True
        
        # Clear initializing message and show IPA
        if root:
            root.after(0, lambda: show_ipa_for_text(text))
        
        # Check if we should still speak
        if not is_speaking:
            return
        
        # Use threading approach
        success = speak_with_thread(text)
        
        if not success:
            if root:
                root.after(0, lambda: ipa_label.config(text="TTS failed", fg="red"))
        
    except Exception as e:
        if root:
            root.after(0, lambda: ipa_label.config(text=f"Error: {str(e)[:30]}...", fg="red"))
    finally:
        is_speaking = False
        
        if root:
            root.after(0, lambda: speak_btn.config(text="🔊 Speak", bg="#1a73e8"))
            root.after(0, lambda: stop_btn.grid_remove())

def speak_with_thread(text):
    """Use threading approach to run TTS in complete isolation"""
    global current_speech_engine
    
    try:
        # Create a new engine instance using our management system
        current_speech_engine = create_tts_engine()
        
        if not current_speech_engine:
            return False
        
        # Check if we should still speak before starting
        if not is_speaking:
            return False
        
        # Speak the text
        current_speech_engine.say(text)
        current_speech_engine.runAndWait()
        return True
        
    except Exception as e:
        error_msg = f"TTS Error: {str(e)[:50]}..."
        print(f"TTS Error: {e}")
        if root:
            root.after(0, lambda: ipa_label.config(text=error_msg, fg="red"))
        return False
    finally:
        # Release the engine back to the pool instead of destroying it
        if current_speech_engine:
            release_tts_engine(current_speech_engine)
        current_speech_engine = None

def show_ipa_for_text(text):
    """Display IPA for the given text"""
    if settings['show_ipa']:
        words = text.split()
        if len(words) == 1:
            word_lower = text.lower()
            ipa_result = None
            if word_lower in large_ipa_dict:
                ipa_result = large_ipa_dict[word_lower]
            elif word_lower in CUSTOM_IPA:
                ipa_result = CUSTOM_IPA[word_lower]
            else:
                try:
                    ipa_result = ipa.convert(text)
                    if ipa_result == text:
                        ipa_result = None
                except Exception as e:
                    ipa_result = None
            if ipa_result and is_valid_english_ipa(ipa_result):
                ipa_label.config(text=ipa_result, fg="#1a73e8")
            else:
                if ipa_result:
                    ipa_label.config(text=f"(Not found, raw: {ipa_result})", fg="red")
                else:
                    ipa_label.config(text="(Not found)", fg="red")
        else:
            ipa_label.config(text="(Enter a single English word)", fg="red")
    else:
        ipa_label.config(text="", fg="#1a73e8")

def on_history_click(word):
    entry.delete(0, tk.END)
    entry.insert(0, word)
    entry.focus_set()
    speak_text()

def clear_entry():
    entry.delete(0, tk.END)
    ipa_label.config(text="", fg="#1a73e8")

def clear_history():
    global history
    history.clear()
    update_history_ui()

def show_settings():
    """Show settings dialog"""
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("520x580")  # Increased height to ensure buttons are visible
    settings_window.resizable(False, False)
    settings_window.configure(bg="#f5f5f5")
    settings_window.transient(root)
    settings_window.grab_set()
    
    # Center the window
    settings_window.update_idletasks()
    x = (settings_window.winfo_screenwidth() // 2) - (520 // 2)
    y = (settings_window.winfo_screenheight() // 2) - (580 // 2)
    settings_window.geometry(f"520x580+{x}+{y}")
    
    # Create main container
    main_container = tk.Frame(settings_window, bg="#f5f5f5")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Header
    header = tk.Label(main_container, text="⚙️ Settings", font=("Segoe UI", 16, "bold"), 
                     bg="#f5f5f5", fg="#333")
    header.pack(pady=(0, 20))
    
    # Create content frame
    content_frame = tk.Frame(main_container, bg="#f5f5f5")
    content_frame.pack(fill="both", expand=True)
    
    # Text-to-Speech Settings Section
    tts_frame = tk.LabelFrame(content_frame, text="Text-to-Speech", font=("Segoe UI", 12, "bold"),
                             bg="#f5f5f5", fg="#333", relief="solid", bd=1)
    tts_frame.pack(fill="x", pady=(0, 15))
    
    # TTS Enable/Disable
    tts_enabled_var = tk.BooleanVar(value=settings['tts_enabled'])
    tts_check = tk.Checkbutton(tts_frame, text="Enable Text-to-Speech", 
                              variable=tts_enabled_var, font=("Segoe UI", 11),
                              bg="#f5f5f5", fg="#333", selectcolor="#e3eafc")
    tts_check.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Auto-speak on clipboard
    auto_speak_var = tk.BooleanVar(value=settings['auto_speak'])
    auto_speak_check = tk.Checkbutton(tts_frame, text="Auto-speak when text is copied", 
                                     variable=auto_speak_var, font=("Segoe UI", 11),
                                     bg="#f5f5f5", fg="#333", selectcolor="#e3eafc")
    auto_speak_check.pack(anchor="w", padx=15, pady=(0, 5))
    
    # Speech Rate
    rate_frame = tk.Frame(tts_frame, bg="#f5f5f5")
    rate_frame.pack(fill="x", padx=15, pady=(0, 10))
    
    tk.Label(rate_frame, text="Speech Rate:", font=("Segoe UI", 11), 
            bg="#f5f5f5", fg="#333").pack(side="left")
    
    rate_var = tk.IntVar(value=settings['speech_rate'])
    rate_scale = tk.Scale(rate_frame, from_=50, to=300, orient="horizontal", 
                         variable=rate_var, font=("Segoe UI", 10),
                         bg="#f5f5f5", fg="#333", highlightthickness=0)
    rate_scale.pack(side="left", padx=(10, 0), fill="x", expand=True)
    
    # Volume Control
    volume_frame = tk.Frame(tts_frame, bg="#f5f5f5")
    volume_frame.pack(fill="x", padx=15, pady=(0, 10))
    
    tk.Label(volume_frame, text="Volume:", font=("Segoe UI", 11), 
            bg="#f5f5f5", fg="#333").pack(side="left")
    
    volume_var = tk.DoubleVar(value=settings['volume'])
    volume_scale = tk.Scale(volume_frame, from_=0.0, to=1.0, orient="horizontal", 
                           variable=volume_var, font=("Segoe UI", 10),
                           bg="#f5f5f5", fg="#333", highlightthickness=0,
                           resolution=0.1)
    volume_scale.pack(side="left", padx=(10, 0), fill="x", expand=True)
    
    # Voice Selection
    voice_frame = tk.Frame(tts_frame, bg="#f5f5f5")
    voice_frame.pack(fill="x", padx=15, pady=(0, 10))
    
    tk.Label(voice_frame, text="Voice:", font=("Segoe UI", 11), 
            bg="#f5f5f5", fg="#333").pack(side="left")
    
    # Get available voices with their IDs
    available_voices = []
    voice_id_map = {}
    
    try:
        # Try to get voices from the main engine
        if engine:
            for voice in engine.getProperty('voices'):
                voice_name = voice.name
                available_voices.append(voice_name)
                voice_id_map[voice_name] = voice.id
        else:
            # If main engine failed, try to create a temporary one
            temp_engine = pyttsx3.init()
            for voice in temp_engine.getProperty('voices'):
                voice_name = voice.name
                available_voices.append(voice_name)
                voice_id_map[voice_name] = voice.id
            temp_engine.stop()
    except Exception as e:
        print(f"Failed to get available voices: {e}")
        # Add a default voice option
        available_voices = ["Default Voice"]
        voice_id_map["Default Voice"] = "default"
    
    # Find the current voice name based on the stored voice_name
    current_voice_name = None
    for voice_name in available_voices:
        if settings['voice_name'].lower() in voice_name.lower():
            current_voice_name = voice_name
            break
    
    # If no match found, use the first available voice
    if not current_voice_name and available_voices:
        current_voice_name = available_voices[0]
    
    voice_var = tk.StringVar(value=current_voice_name if current_voice_name else "")
    voice_combo = ttk.Combobox(voice_frame, textvariable=voice_var, 
                              values=available_voices, font=("Segoe UI", 10),
                              state="readonly", width=30)
    voice_combo.pack(side="left", padx=(10, 0))
    
    # Clipboard Settings Section
    clipboard_frame = tk.LabelFrame(content_frame, text="Clipboard Monitoring", font=("Segoe UI", 12, "bold"),
                                   bg="#f5f5f5", fg="#333", relief="solid", bd=1)
    clipboard_frame.pack(fill="x", pady=(0, 15))
    
    # Clipboard Enable/Disable
    clipboard_enabled_var = tk.BooleanVar(value=settings['clipboard_monitoring'])
    clipboard_check = tk.Checkbutton(clipboard_frame, text="Monitor clipboard for copied text", 
                                    variable=clipboard_enabled_var, font=("Segoe UI", 11),
                                    bg="#f5f5f5", fg="#333", selectcolor="#e3eafc")
    clipboard_check.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Show IPA setting
    show_ipa_var = tk.BooleanVar(value=settings['show_ipa'])
    show_ipa_check = tk.Checkbutton(clipboard_frame, text="Show IPA pronunciation", 
                                   variable=show_ipa_var, font=("Segoe UI", 11),
                                   bg="#f5f5f5", fg="#333", selectcolor="#e3eafc")
    show_ipa_check.pack(anchor="w", padx=15, pady=(0, 10))
    
    # Buttons - Fixed at bottom of window
    button_frame = tk.Frame(settings_window, bg="#f5f5f5")
    button_frame.pack(side="bottom", fill="x", padx=25, pady=25)
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#f5f5f5")
    button_container.pack(expand=True)
    
    def save_settings():
        global settings  # Ensure we're updating the global settings
        
        # Debug: Print current values before saving
        print(f"[DEBUG] Current UI values:")
        print(f"  TTS Enabled: {tts_enabled_var.get()}")
        print(f"  Clipboard Monitoring: {clipboard_enabled_var.get()}")
        print(f"  Auto Speak: {auto_speak_var.get()}")
        print(f"  Show IPA: {show_ipa_var.get()}")
        print(f"  Speech Rate: {rate_var.get()}")
        print(f"  Volume: {volume_var.get()}")
        print(f"  Voice: {voice_var.get()}")
        
        # Update global settings with proper type conversion
        settings['tts_enabled'] = bool(tts_enabled_var.get())
        settings['clipboard_monitoring'] = bool(clipboard_enabled_var.get())
        settings['auto_speak'] = bool(auto_speak_var.get())
        settings['speech_rate'] = int(rate_var.get())
        settings['volume'] = float(volume_var.get())
        settings['show_ipa'] = bool(show_ipa_var.get())
        
        # Debug: Print settings after update
        print(f"[DEBUG] Settings after update:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        # Handle voice selection
        selected_voice_name = voice_var.get()
        if selected_voice_name and selected_voice_name in voice_id_map:
            settings['voice_name'] = selected_voice_name
            # Update the main engine voice
            if engine is not None:
                engine.setProperty('voice', voice_id_map[selected_voice_name])
        
        # Update engine properties immediately
        if engine is not None:
            engine.setProperty('rate', settings['speech_rate'])
            engine.setProperty('volume', settings['volume'])
        
        # Save settings to file immediately
        print(f"[DEBUG] Attempting to save settings to: {SETTINGS_FILE.absolute()}")
        
        # Force save with error handling
        try:
            # Save directly to asset directory
            with open(os.path.join("asset", "settings.json"), 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Settings saved directly to asset/settings.json")
            
            # Also try the original method
            save_settings_to_file()
            
        except Exception as e:
            print(f"[DEBUG] Direct save failed: {e}")
            save_settings_to_file()
        
        # Verify settings were saved
        if Path(os.path.join("asset", "settings.json")).exists():
            print(f"[DEBUG] Settings file exists after save")
            # Read back the file to verify content
            try:
                with open(os.path.join("asset", "settings.json"), 'r', encoding='utf-8') as f:
                    saved_content = json.load(f)
                print(f"[DEBUG] File content after save: {saved_content}")
                messagebox.showinfo("Settings Saved", f"Settings have been saved successfully!")
            except Exception as e:
                print(f"[DEBUG] Error reading saved file: {e}")
                messagebox.showwarning("Settings Warning", f"Settings saved but could not verify: {e}")
        else:
            print(f"[DEBUG] Settings file does not exist after save attempt")
            messagebox.showwarning("Settings Warning", "Settings may not have been saved properly. Please check the console for errors.")
        
        settings_window.destroy()
    
    def reset_settings():
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset to defaults
            settings['tts_enabled'] = True
            settings['clipboard_monitoring'] = True
            settings['auto_speak'] = True
            settings['speech_rate'] = 150
            settings['voice_name'] = 'zira'
            settings['volume'] = 1.0
            settings['show_ipa'] = True
            
            # Update UI
            tts_enabled_var.set(True)
            clipboard_enabled_var.set(True)
            auto_speak_var.set(True)
            rate_var.set(150)
            volume_var.set(1.0)
            show_ipa_var.set(True)
            
            # Reset voice selection
            current_voice_name = None
            for voice_name in available_voices:
                if 'zira' in voice_name.lower():
                    current_voice_name = voice_name
                    break
            if not current_voice_name and available_voices:
                current_voice_name = available_voices[0]
            voice_var.set(current_voice_name if current_voice_name else "")
            
            # Save to file
            save_settings_to_file()
            
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults!")
    
    def cancel_settings():
        settings_window.destroy()
    
    save_btn = tk.Button(button_container, text="💾 Save", font=("Segoe UI", 13, "bold"),
                        bg="#1a73e8", fg="white", command=save_settings,
                        relief="flat", padx=35, pady=12, cursor="hand2",
                        activebackground="#1761b0", activeforeground="white",
                        width=12, height=1)
    save_btn.pack(side="left", padx=(0, 15))
    
    cancel_btn = tk.Button(button_container, text="Cancel", font=("Segoe UI", 13),
                          bg="#e0e0e0", fg="#333", command=cancel_settings,
                          relief="flat", padx=35, pady=12, cursor="hand2",
                          activebackground="#bdbdbd", activeforeground="#333",
                          width=12, height=1)
    cancel_btn.pack(side="left")

def show_about():
    """Show about dialog"""
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("400x300")
    about_window.resizable(False, False)
    about_window.configure(bg="#f5f5f5")
    about_window.transient(root)
    about_window.grab_set()
    
    # Center the window
    about_window.update_idletasks()
    x = (about_window.winfo_screenwidth() // 2) - (400 // 2)
    y = (about_window.winfo_screenheight() // 2) - (300 // 2)
    about_window.geometry(f"400x300+{x}+{y}")
    
    # Content
    tk.Label(about_window, text="TTS Pronunciation Practice", font=("Segoe UI", 16, "bold"), 
            bg="#f5f5f5", fg="#333").pack(pady=(30, 10))
    
    tk.Label(about_window, text=f"Version {CURRENT_VERSION}", font=("Segoe UI", 12), 
            bg="#f5f5f5", fg="#666").pack(pady=(0, 20))
    
    tk.Label(about_window, text="A tool for practicing English pronunciation\nwith text-to-speech and IPA display.", 
            font=("Segoe UI", 11), bg="#f5f5f5", fg="#333", justify="center").pack(pady=(0, 20))
    
    tk.Label(about_window, text="Created by Yamin", font=("Segoe UI", 10), 
            bg="#f5f5f5", fg="#666").pack(pady=(0, 20))
    
    # Close button
    close_btn = tk.Button(about_window, text="Close", font=("Segoe UI", 12),
                         bg="#1a73e8", fg="white", command=about_window.destroy,
                         relief="flat", padx=20, pady=8)
    close_btn.pack()

def show_update_status():
    """Show update status in a separate window"""
    update_window = tk.Toplevel(root)
    update_window.title("Check for Updates")
    update_window.geometry("500x400")
    update_window.resizable(False, False)
    update_window.configure(bg="#f5f5f5")
    update_window.transient(root)
    update_window.grab_set()
    
    # Center the window
    update_window.update_idletasks()
    x = (update_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (update_window.winfo_screenheight() // 2) - (400 // 2)
    update_window.geometry(f"500x400+{x}+{y}")
    
    # Header
    header = tk.Label(update_window, text="🔄 Check for Updates", font=("Segoe UI", 16, "bold"), 
                     bg="#f5f5f5", fg="#333")
    header.pack(pady=(20, 10))
    
    # Status label
    status_label = tk.Label(update_window, text="Checking for updates...", font=("Segoe UI", 12), 
                           bg="#f5f5f5", fg="#666")
    status_label.pack(pady=(10, 20))
    
    # Content frame
    content_frame = tk.Frame(update_window, bg="#f5f5f5")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Text widget for update information
    text_widget = tk.Text(content_frame, height=15, wrap="word", font=("Segoe UI", 10),
                         bg="white", fg="#333", relief="solid", bd=1, state="disabled")
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Button frame
    button_frame = tk.Frame(update_window, bg="#f5f5f5")
    button_frame.pack(pady=20)
    
    # Store update info for download button
    current_update_info = [None]
    
    def check_updates():
        """Check for updates and display results"""
        status_label.config(text="Checking for updates...", fg="#1a73e8")
        text_widget.config(state="normal")
        text_widget.delete(1.0, tk.END)
        text_widget.config(state="disabled")
        
        def update_checker():
            try:
                update_info = check_for_updates()
                current_update_info[0] = update_info  # Store for download button
                
                if update_info:
                    # Update available
                    root.after(0, lambda: status_label.config(text="Update Available!", fg="#34a853"))
                    root.after(0, lambda: text_widget.config(state="normal"))
                    root.after(0, lambda: text_widget.delete(1.0, tk.END))
                    root.after(0, lambda: text_widget.insert(1.0, f"New version available: {update_info['version']}\n\n"))
                    root.after(0, lambda: text_widget.insert(tk.END, f"Current version: {CURRENT_VERSION}\n\n"))
                    root.after(0, lambda: text_widget.insert(tk.END, "What's new:\n"))
                    root.after(0, lambda: text_widget.insert(tk.END, update_info.get('body', 'No release notes available.')))
                    root.after(0, lambda: text_widget.config(state="disabled"))
                    
                    # Show download button
                    download_btn.config(state="normal")
                else:
                    # No update available
                    root.after(0, lambda: status_label.config(text="No updates available", fg="#666"))
                    root.after(0, lambda: text_widget.config(state="normal"))
                    root.after(0, lambda: text_widget.delete(1.0, tk.END))
                    root.after(0, lambda: text_widget.insert(1.0, f"You are using the latest version: {CURRENT_VERSION}\n\n"))
                    root.after(0, lambda: text_widget.insert(tk.END, "No updates are currently available."))
                    root.after(0, lambda: text_widget.config(state="disabled"))
                    
                    # Hide download button
                    download_btn.config(state="disabled")
            except Exception as e:
                root.after(0, lambda: status_label.config(text="Error checking for updates", fg="#d32f2f"))
                root.after(0, lambda: text_widget.config(state="normal"))
                root.after(0, lambda: text_widget.delete(1.0, tk.END))
                root.after(0, lambda: text_widget.insert(1.0, f"Error checking for updates:\n{str(e)}"))
                root.after(0, lambda: text_widget.config(state="disabled"))
                root.after(0, lambda: download_btn.config(state="disabled"))
        
        threading.Thread(target=update_checker, daemon=True).start()
    
    def download_update():
        """Open download link"""
        if current_update_info[0]:
            import webbrowser
            webbrowser.open(current_update_info[0]['url'])
    
    def close_window():
        update_window.destroy()
    
    # Buttons
    check_btn = tk.Button(button_frame, text="🔄 Check Again", font=("Segoe UI", 12, "bold"),
                         bg="#1a73e8", fg="white", command=check_updates,
                         relief="flat", padx=20, pady=8)
    check_btn.pack(side="left", padx=(0, 10))
    
    download_btn = tk.Button(button_frame, text="📥 Download", font=("Segoe UI", 12),
                            bg="#34a853", fg="white", command=download_update,
                            relief="flat", padx=20, pady=8, state="disabled")
    download_btn.pack(side="left", padx=(0, 10))
    
    close_btn = tk.Button(button_frame, text="Close", font=("Segoe UI", 12),
                         bg="#e0e0e0", fg="#333", command=close_window,
                         relief="flat", padx=20, pady=8)
    close_btn.pack(side="left")
    
    # Start checking for updates immediately
    check_updates()

def create_menu_bar():
    """Create the top menu bar"""
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Clear History", command=clear_history)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=on_closing)
    
    # Edit Menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Clear Entry", command=clear_entry)
    edit_menu.add_command(label="Copy IPA", command=lambda: pyperclip.copy(ipa_label.cget("text")))
    
    # Settings Menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Preferences", command=show_settings)
    
    # Help Menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Check for Updates", command=show_update_status)
    help_menu.add_separator()
    help_menu.add_command(label="About", command=show_about)

# GUI Setup
try:
    root = tk.Tk()
    root.title("TTS Pronunciation Practice")
    root.geometry("650x500")  # Optimized size for perfect fit
    root.resizable(False, False)
    root.configure(bg="#f5f5f5")

    # Create menu bar
    create_menu_bar()

    # Set the main window icon as well
    try:
        import os
        icon_path = os.path.join("asset", "y_icon_temp.ico")
        if not os.path.exists(icon_path):
            icon_img = create_image()
            icon_img.save(icon_path)
        root.iconbitmap(icon_path)
    except Exception:
        pass

    header = tk.Label(root, text="Type a word to hear and see its pronunciation", font=("Segoe UI", 14, "bold"), bg="#f5f5f5", fg="#333")
    header.pack(pady=(5, 8))  # Reduced top padding from 10 to 5

    entry_frame = tk.Frame(root, bg="#f5f5f5")
    entry_frame.pack(pady=2)

    entry = tk.Entry(entry_frame, font=("Segoe UI", 18), width=18, justify="center", relief="solid", bd=2)
    entry.grid(row=0, column=0, padx=(0, 8))
    entry.bind("<Return>", speak_text)

    speak_btn = tk.Button(entry_frame, text="🔊 Speak", font=("Segoe UI", 13, "bold"), bg="#1a73e8", fg="white", activebackground="#1761b0", activeforeground="white", command=speak_text, relief="flat", padx=12, pady=2)
    speak_btn.grid(row=0, column=1)

    stop_btn = tk.Button(entry_frame, text="⏹ Stop", font=("Segoe UI", 13, "bold"), bg="#ff5722", fg="white", activebackground="#d84315", activeforeground="white", command=stop_speech, relief="flat", padx=12, pady=2)
    stop_btn.grid(row=0, column=2, padx=(8, 8))
    stop_btn.grid_remove()  # Hide initially

    clear_btn = tk.Button(entry_frame, text="✖", font=("Segoe UI", 13), bg="#e57373", fg="white", activebackground="#c62828", activeforeground="white", command=clear_entry, relief="flat", padx=8, pady=2)
    clear_btn.grid(row=0, column=3, padx=(0, 0))

    pronun_frame = tk.Frame(root, bg="#f5f5f5")
    pronun_frame.pack(pady=(18, 8))

    pronun_label = tk.Label(pronun_frame, text="IPA Pronunciation", font=("Segoe UI", 12, "bold"), bg="#f5f5f5", fg="#333")
    pronun_label.pack()

    ipa_label = tk.Label(pronun_frame, text="", font=("Segoe UI", 28, "bold"), fg="#1a73e8", bg="#f5f5f5")
    ipa_label.pack(pady=(2, 0))

    sep = ttk.Separator(root, orient='horizontal')
    sep.pack(fill='x', pady=10)

    # --- Smart, scrollable clickable history UI ---
    history_label = tk.Label(root, text="History:", font=("Segoe UI", 11), bg="#f5f5f5", fg="#555")
    history_label.pack(pady=(2, 0))

    history_frame_container = tk.Frame(root, bg="#f5f5f5")
    history_frame_container.pack(pady=(0, 8), fill='x', expand=False)

    history_canvas = tk.Canvas(history_frame_container, height=150, bg="#f5f5f5", highlightthickness=0)  # Reduced height from 200 to 150
    history_scrollbar = tk.Scrollbar(history_frame_container, orient="vertical", command=history_canvas.yview)
    history_inner_frame = tk.Frame(history_canvas, bg="#f5f5f5")

    history_inner_frame.bind(
        "<Configure>",
        lambda e: history_canvas.configure(
            scrollregion=history_canvas.bbox("all")
        )
    )
    history_canvas.create_window((0, 0), window=history_inner_frame, anchor="nw")
    history_canvas.configure(yscrollcommand=history_scrollbar.set)
    history_canvas.pack(side="left", fill="both", expand=True)
    history_scrollbar.pack(side="right", fill="y")

    def update_history_ui():
        # Clear previous widgets
        for widget in history_inner_frame.winfo_children():
            widget.destroy()
        def resize_buttons(event=None):
            width = history_canvas.winfo_width()
            for btn in history_inner_frame.winfo_children():
                btn.config(width=width)
        for idx, item in enumerate(history):
            def make_callback(word=item):
                return lambda: on_history_click(word)
            btn = tk.Button(
                history_inner_frame,
                text=item,
                font=("Segoe UI", 11),
                bg="#e3eafc" if idx % 2 == 0 else "#f5f5f5",
                fg="#1a73e8",
                relief="flat",
                cursor="hand2",
                anchor="w",
                command=make_callback(item),
                padx=8, pady=2
            )
            btn.pack(fill='x', expand=True, pady=1, padx=2)
        # Bind resize event
        history_canvas.bind('<Configure>', lambda e: resize_buttons())
        resize_buttons()

    # Setup system tray and clipboard monitoring
    root.protocol("WM_DELETE_WINDOW", on_closing)
    setup_tray()
    clipboard_thread = threading.Thread(target=clipboard_monitor, daemon=True)
    clipboard_thread.start()

    # Check for updates in background
    check_updates_in_background()

except Exception as e:
    print(f"Failed to initialize GUI: {e}")
    try:
        messagebox.showerror("Initialization Error", f"Failed to start the application:\n{str(e)}")
    except:
        pass
    sys.exit(1)

root.mainloop()
