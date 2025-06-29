#!/usr/bin/env python3
"""
Simple test script to verify TTS functionality
"""

import pyttsx3
import time

def test_tts():
    """Test basic TTS functionality"""
    try:
        print("Initializing TTS engine...")
        engine = pyttsx3.init()
        
        print("Setting properties...")
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        print("Getting voices...")
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voices:")
        for i, voice in enumerate(voices):
            print(f"  {i+1}. {voice.name} ({voice.id})")
        
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        print("Testing speech...")
        engine.say("Hello, this is a test of the text to speech functionality.")
        engine.runAndWait()
        
        print("TTS test completed successfully!")
        return True
        
    except Exception as e:
        print(f"TTS test failed: {e}")
        return False

if __name__ == "__main__":
    print("TTS Pronunciation Practice - Test Script")
    print("=" * 50)
    
    success = test_tts()
    
    if success:
        print("\n✓ TTS is working correctly!")
    else:
        print("\n✗ TTS has issues that need to be resolved.")
    
    input("\nPress Enter to exit...") 