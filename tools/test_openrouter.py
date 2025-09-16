#!/usr/bin/env python3
"""
Quick test of OpenRouter API connection with a single model.
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.test_models import VisionModelTester

def test_openrouter_connection():
    """Test OpenRouter connection with a simple text prompt."""
    # Load environment variables
    load_dotenv("config/.env")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in config/.env")
        print("Please copy config/.env.example to config/.env and add your API key.")
        return False

    print("🔍 Testing OpenRouter API connection...")

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        # Simple text-only test
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'OpenRouter connection successful!'"}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"✅ Success! Model responded: {result}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_connection()
    if success:
        print("\n🎉 OpenRouter is ready for vision model testing!")
        print("Run 'python run_full_test.py' to start the full pipeline.")
    else:
        print("\n🔧 Please fix the connection issue before proceeding.")
    sys.exit(0 if success else 1)