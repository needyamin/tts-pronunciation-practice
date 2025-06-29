#!/usr/bin/env python3
"""
Test script for TTS engine management
"""

import pyttsx3
import threading
import time

def test_engine_management():
    """Test the engine management system"""
    print("Testing TTS Engine Management")
    print("=" * 40)
    
    # Test 1: Create engine
    print("1. Creating TTS engine...")
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        print("✓ Engine created successfully")
    except Exception as e:
        print(f"✗ Failed to create engine: {e}")
        return False
    
    # Test 2: Test speech
    print("2. Testing speech...")
    try:
        engine.say("Test one")
        engine.runAndWait()
        print("✓ Speech test successful")
    except Exception as e:
        print(f"✗ Speech test failed: {e}")
        return False
    
    # Test 3: Test engine reuse
    print("3. Testing engine reuse...")
    try:
        engine.say("Test two")
        engine.runAndWait()
        print("✓ Engine reuse successful")
    except Exception as e:
        print(f"✗ Engine reuse failed: {e}")
        return False
    
    # Test 4: Test cleanup
    print("4. Testing cleanup...")
    try:
        engine.stop()
        print("✓ Engine cleanup successful")
    except Exception as e:
        print(f"✗ Engine cleanup failed: {e}")
        return False
    
    print("\n✓ All tests passed!")
    return True

def test_multiple_engines():
    """Test creating multiple engines to see if it causes issues"""
    print("\nTesting Multiple Engine Creation")
    print("=" * 40)
    
    engines = []
    
    try:
        for i in range(3):
            print(f"Creating engine {i+1}...")
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.5)
            engines.append(engine)
            print(f"✓ Engine {i+1} created")
        
        # Test speech with each engine
        for i, engine in enumerate(engines):
            print(f"Testing speech with engine {i+1}...")
            engine.say(f"Test from engine {i+1}")
            engine.runAndWait()
            print(f"✓ Engine {i+1} speech successful")
        
        # Cleanup
        for i, engine in enumerate(engines):
            print(f"Cleaning up engine {i+1}...")
            engine.stop()
            print(f"✓ Engine {i+1} cleaned up")
        
        print("\n✓ Multiple engine test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Multiple engine test failed: {e}")
        return False

if __name__ == "__main__":
    print("TTS Engine Management Test")
    print("=" * 50)
    
    # Test basic engine management
    success1 = test_engine_management()
    
    # Test multiple engines
    success2 = test_multiple_engines()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Engine management is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    input("\nPress Enter to exit...") 