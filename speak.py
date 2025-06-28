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

# Path to the large IPA dictionary file
IPA_DICT_PATH = "cmudict-0.7b-ipa.txt"
IPA_DICT_URL = "https://raw.githubusercontent.com/menelik3/cmudict-ipa/master/cmudict-0.7b-ipa.txt"

# Custom IPA dictionary for special/corrected words
CUSTOM_IPA = {
    "yamin": "jɑːˈmiːn",
    "million": "ˈmɪl.jən",
    "billion": "ˈbɪl.jən"
}

# Looser IPA validation regex (includes more IPA symbols, diacritics, and punctuation)
IPA_REGEX = re.compile(r"^[ˈˌa-zA-Zɪʊəɔæɑɛʌθðŋʃʒɹɝɚɡɾɫʔʤʧːˑ˞ˠˤ̩̯̃ʼ˺ˈˌːˑ˞ˠˤ̩̯̃ʼ˺\.\s,\-]+$")

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
engine = pyttsx3.init()

# Set clear voice (adjust based on your system)
for voice in engine.getProperty('voices'):
    if "zira" in voice.name.lower():  # Choose Microsoft Zira if available
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 150)

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

# --- Update Check Constants ---
REPO_OWNER = "needyamin"
REPO_NAME = "tts-pronunciation-practice"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
CURRENT_VERSION = "1.0.0"  # Update as needed
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
    """Check for updates in background thread"""
    def update_checker():
        try:
            print("[DEBUG] Background update checker started")  # Debug output
            update_info = check_for_updates()
            print(f"[DEBUG] Update check result: {update_info}")  # Debug output
            if update_info:
                print("[DEBUG] Update available, showing dialog")  # Debug output
                # Show update dialog in main thread
                root.after(0, lambda: show_update_dialog(update_info))
            else:
                print("[DEBUG] No update available")  # Debug output
        except Exception as e:
            print(f"Background update check failed: {e}")
    
    # Start update check in background
    print("[DEBUG] Starting background update thread")  # Debug output
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
    print("[DEBUG] Quitting application...")
    should_run_clipboard = False
    is_speaking = False  # Stop any ongoing speech
    
    # Properly stop the tray icon
    if tray_icon:
        try:
            tray_icon.visible = False
            tray_icon.stop()
            print("[DEBUG] Tray icon stopped successfully")
        except Exception as e:
            print(f"Error stopping tray icon: {e}")
        finally:
            tray_icon = None
    
    # Destroy the main window
    if root:
        try:
            root.destroy()
        except Exception as e:
            print(f"Error destroying root window: {e}")
    
    print("[DEBUG] Application quit complete")
    sys.exit()

def show_window(icon, item):
    if root:
        root.after(0, root.deiconify)

def hide_window():
    if root:
        root.withdraw()
    # Ensure tray icon is visible (don't create new ones)
    global tray_icon
    if tray_icon and not tray_icon.visible:
        try:
            tray_icon.visible = True
        except Exception as e:
            print(f"Error making tray icon visible: {e}")

def on_closing():
    global is_speaking
    print("[DEBUG] Window closing (X button clicked)")
    is_speaking = False  # Stop any ongoing speech
    hide_window()

def setup_tray():
    global tray_icon
    # Only create tray icon if it doesn't already exist
    if tray_icon is None:
        try:
            menu = pystray.Menu(
                pystray.MenuItem('Show', show_window),
                pystray.MenuItem('Check for Updates', lambda: check_updates_in_background()),
                pystray.MenuItem('Quit', on_quit)
            )
            tray_icon = pystray.Icon("tts_pronunciation", create_image(), "TTS Pronunciation", menu)
            threading.Thread(target=tray_icon.run, daemon=True).start()
            print("[DEBUG] Tray icon created successfully")
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            tray_icon = None
    else:
        # If tray icon exists, just ensure it's visible
        if not tray_icon.visible:
            try:
                tray_icon.visible = True
                print("[DEBUG] Made existing tray icon visible")
            except Exception as e:
                print(f"Error making tray icon visible: {e}")
                # If there's an error, don't recreate - just log it

# Clipboard monitoring thread
def clipboard_monitor():
    global last_clipboard
    while should_run_clipboard:
        try:
            # Get clipboard content and ensure it's clean plain text
            current = pyperclip.paste()
            
            # Convert to string and clean thoroughly
            if isinstance(current, str):
                # Remove all formatting and get clean text
                cleaned_current = current.strip()
                # Remove any special characters that might be formatting artifacts
                cleaned_current = re.sub(r'[\r\n\t]', ' ', cleaned_current)  # Replace newlines/tabs with spaces
                cleaned_current = re.sub(r'\s+', ' ', cleaned_current)  # Replace multiple spaces with single space
                cleaned_current = cleaned_current.strip()  # Final trim
            else:
                cleaned_current = ""
            
            # Process ANY non-empty content - no restrictions at all
            if cleaned_current != last_clipboard and cleaned_current and len(cleaned_current) > 0:
                print(f"[DEBUG] Clipboard detected: '{cleaned_current}'")  # Debug output
                last_clipboard = cleaned_current
                # Process any copied content, regardless of window state or content
                root.after(0, lambda: auto_paste_word(cleaned_current))
        except Exception as e:
            print(f"Clipboard error: {e}")
            pass
        time.sleep(0.01)  # Extremely fast - check every 10ms for instant response

def auto_paste_word(word):
    print(f"[DEBUG] auto_paste_word called with: '{word}'")  # Debug output
    
    # Process ANY content that is not completely empty - no restrictions
    if word and len(word) > 0:
        print(f"[DEBUG] Processing word: '{word}'")  # Debug output
        
        # Immediately stop any current speech
        global is_speaking
        if is_speaking:
            is_speaking = False
            speak_btn.config(text="🔊 Speak", bg="#1a73e8")
            stop_btn.grid_remove()
        
        # Clean the word thoroughly - remove all formatting and extra characters
        cleaned_word = word.strip()
        # Remove any remaining formatting artifacts
        cleaned_word = re.sub(r'[\r\n\t]', ' ', cleaned_word)  # Replace newlines/tabs with spaces
        cleaned_word = re.sub(r'\s+', ' ', cleaned_word)  # Replace multiple spaces with single space
        cleaned_word = cleaned_word.strip()  # Final trim
        
        print(f"[DEBUG] Cleaned word: '{cleaned_word}'")  # Debug output
        
        # Process ANY non-empty content - no validation restrictions
        if cleaned_word and len(cleaned_word) > 0:
            entry.delete(0, tk.END)
            entry.insert(0, cleaned_word)
            entry.focus_set()  # Focus the entry field
            
            print(f"[DEBUG] Starting speech for: '{cleaned_word}'")  # Debug output
            # Always start speaking immediately - no restrictions
            speak_text()
        else:
            print(f"[DEBUG] Cleaned word is empty, skipping")  # Debug output
    else:
        print(f"[DEBUG] Word is completely empty, skipping")  # Debug output

def stop_speech():
    """Stop current speech if any"""
    global is_speaking
    if is_speaking:
        is_speaking = False
        speak_btn.config(text="🔊 Speak", bg="#1a73e8")
        stop_btn.grid_remove()  # Hide stop button
        # Note: pyttsx3 doesn't have a direct stop method, but we can prevent new speech

# --- End System Tray and Clipboard Monitoring ---

def speak_in_thread(text):
    """Speak text in a separate thread to prevent GUI freezing"""
    global is_speaking
    try:
        is_speaking = True
        # Create a new engine instance for this thread
        thread_engine = pyttsx3.init()
        
        # Set the same properties as the main engine
        for voice in thread_engine.getProperty('voices'):
            if "zira" in voice.name.lower():
                thread_engine.setProperty('voice', voice.id)
                break
        thread_engine.setProperty('rate', 150)
        
        # Speak the text
        thread_engine.say(text)
        thread_engine.runAndWait()
        
        # Clean up
        thread_engine.stop()
    except Exception as e:
        print(f"Speech error: {e}")
        # Show error in UI
        if root:
            root.after(0, lambda: ipa_label.config(text=f"Speech Error: {str(e)[:30]}...", fg="red"))
    finally:
        is_speaking = False
        # Update UI to show speech is complete
        if root:
            root.after(0, lambda: speak_btn.config(text="🔊 Speak", bg="#1a73e8"))
            root.after(0, lambda: stop_btn.grid_remove())  # Hide stop button
            print('[DEBUG] Stop button hidden after speech ends')

def speak_text(event=None):
    global speech_thread, is_speaking
    
    # Hide stop button if not speaking
    stop_btn.grid_remove()
    
    # Prevent multiple simultaneous speech requests
    if is_speaking:
        return
    
    text = entry.get().strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter some text.")
        return

    print(f"[DEBUG] speak_text called with: '{text}'")  # Debug output

    # Save to history
    if text not in history:
        history.insert(0, text)
        update_history_ui()

    # Update UI to show speech is starting
    speak_btn.config(text="🔊 Speaking...", bg="#ff9800")
    stop_btn.grid()  # Show stop button
    
    print(f"[DEBUG] Starting speech thread for: '{text}'")  # Debug output
    
    # Start speech in separate thread
    speech_thread = threading.Thread(target=speak_in_thread, args=(text,), daemon=True)
    speech_thread.start()

    # Show pronunciation using large IPA dict, custom IPA, or eng_to_ipa
    words = text.split()
    if len(words) == 1:
        word_lower = text.lower()
        ipa_result = None
        # 1. Check large IPA dictionary
        if word_lower in large_ipa_dict:
            ipa_result = large_ipa_dict[word_lower]
        # 2. Check custom IPA
        elif word_lower in CUSTOM_IPA:
            ipa_result = CUSTOM_IPA[word_lower]
        # 3. Fallback to eng_to_ipa
        else:
            try:
                ipa_result = ipa.convert(text)
                if ipa_result == text:
                    ipa_result = None
            except Exception as e:
                print(f"IPA conversion error: {e}")
                ipa_result = None
        # Validate IPA result
        if ipa_result and is_valid_english_ipa(ipa_result):
            ipa_label.config(text=ipa_result, fg="#1a73e8")
        else:
            if ipa_result:
                ipa_label.config(text=f"(Not found, raw: {ipa_result})", fg="red")
            else:
                ipa_label.config(text="(Not found)", fg="red")
    else:
        ipa_label.config(text="(Enter a single English word)", fg="red")

def on_history_click(word):
    entry.delete(0, tk.END)
    entry.insert(0, word)
    entry.focus_set()
    speak_text()

def clear_entry():
    entry.delete(0, tk.END)
    ipa_label.config(text="", fg="#1a73e8")

# GUI Setup
root = tk.Tk()
root.title("TTS Pronunciation Practice")
root.geometry("650x540")  # Reduced height from 580 to 540 since footer is smaller
root.resizable(False, False)
root.configure(bg="#f5f5f5")

# Set the main window icon as well
try:
    icon_img = create_image()
    icon_img.save("y_icon_temp.ico")
    root.iconbitmap("y_icon_temp.ico")
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

# --- Footer with Update Button ---
# Add separator before footer
footer_separator = ttk.Separator(root, orient='horizontal')
footer_separator.pack(fill='x', pady=(10, 0))  # Reduced padding

footer_frame = tk.Frame(root, bg="#f8f9fa", relief="flat", bd=1)
footer_frame.pack(side="bottom", fill="x", pady=(0, 0))

# Create a container for the update button and status
update_container = tk.Frame(footer_frame, bg="#f8f9fa", height=70)  # Increased height from 60 to 70
update_container.pack(fill="x", padx=20, pady=15)  # Increased padding from 12 to 15
update_container.pack_propagate(False)  # Maintain fixed height

def manual_update_check():
    """Manual update check triggered by button"""
    print("[DEBUG] Update button clicked!")  # Debug output
    print("[DEBUG] Starting manual update check...")  # Debug output
    check_updates_in_background()
    # Show a brief message
    update_status.config(text="Checking for updates...", fg="#1a73e8")
    print("[DEBUG] Status message set to 'Checking for updates...'")  # Debug output
    root.after(3000, lambda: update_status.config(text="", fg="#1a73e8"))

# Update button with smaller, thinner styling
update_btn = tk.Button(update_container, text="🔄 Check for Updates", 
                      font=("Segoe UI", 9, "bold"),  # Reduced font size
                      bg="#34a853", fg="white", 
                      command=manual_update_check,
                      relief="flat", padx=12, pady=3,  # Reduced padding for thinner look
                      cursor="hand2",
                      activebackground="#2d8a47",
                      activeforeground="white")
update_btn.pack(pady=(0, 6))  # Reduced padding

# Status label with more space
update_status = tk.Label(update_container, text="", 
                        font=("Segoe UI", 8),  # Reduced font size
                        bg="#f8f9fa", fg="#1a73e8",
                        wraplength=400,  # Allow text wrapping
                        justify="center")
update_status.pack(pady=(0, 3))  # Reduced padding

# Setup system tray and clipboard monitoring
root.protocol("WM_DELETE_WINDOW", on_closing)
setup_tray()
clipboard_thread = threading.Thread(target=clipboard_monitor, daemon=True)
clipboard_thread.start()

# Check for updates on startup (after a short delay)
root.after(2000, check_updates_in_background)

root.mainloop()
