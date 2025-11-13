#!/usr/bin/env python
"""Test Gemini API configuration and initialization."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing Gemini Configuration")
print("=" * 60)

# Test 1: Check if .env file exists
env_file = Path(__file__).parent / '.env'
print(f"\n1. .env file exists: {env_file.exists()}")
if env_file.exists():
    print(f"   Location: {env_file}")

# Test 2: Load environment and check GEMINI_API_KEY
from dotenv import load_dotenv
import os

load_dotenv(env_file)
gemini_key = os.getenv('GEMINI_API_KEY')
print(f"\n2. GEMINI_API_KEY from environment:")
print(f"   Found: {bool(gemini_key)}")
if gemini_key:
    print(f"   First 20 chars: {gemini_key[:20]}...")

# Test 3: Check Config
from src.utils.config import Config
print(f"\n3. Config.GEMINI_API_KEY:")
print(f"   Found: {bool(Config.GEMINI_API_KEY)}")
if Config.GEMINI_API_KEY:
    print(f"   First 20 chars: {Config.GEMINI_API_KEY[:20]}...")
print(f"   Config.has_gemini(): {Config.has_gemini()}")

# Test 4: Check if google-generativeai is installed
try:
    import google.generativeai as genai
    print(f"\n4. google-generativeai package:")
    print(f"   Installed: ✅")
except ImportError as e:
    print(f"\n4. google-generativeai package:")
    print(f"   Installed: ❌")
    print(f"   Error: {e}")
    sys.exit(1)

# Test 5: Try to initialize GeminiEnhancer
print(f"\n5. Initializing GeminiEnhancer:")
try:
    from src.generators.gemini_enhancer import GeminiEnhancer
    enhancer = GeminiEnhancer()
    print(f"   Created: ✅")
    print(f"   is_available(): {enhancer.is_available()}")
    print(f"   model: {enhancer.model}")
except Exception as e:
    print(f"   Failed: ❌")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Try to create CampaignAutopilot
print(f"\n6. Initializing CampaignAutopilot:")
try:
    from src.autopilot import CampaignAutopilot
    autopilot = CampaignAutopilot()
    print(f"   Created: ✅")
    print(f"   gemini_enhancer: {autopilot.gemini_enhancer}")
    if autopilot.gemini_enhancer:
        print(f"   gemini_enhancer.is_available(): {autopilot.gemini_enhancer.is_available()}")
    else:
        print(f"   gemini_enhancer: None (not initialized)")
except Exception as e:
    print(f"   Failed: ❌")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
