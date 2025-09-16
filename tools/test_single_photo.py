#!/usr/bin/env python3
"""
Test a single random photo with all vision models.
This ensures models are "blind" - only seeing the image with no contextual metadata.
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.test_models import VisionModelTester

def main():
    """Test one random photo with all models."""
    # Load environment variables
    load_dotenv("config/.env")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in config/.env")
        print("Please create config/.env file with your OpenRouter API key.")
        return 1

    print("🖼️  Testing Random Historical Photo with All Vision Models")
    print("="*60)
    print("Models will only see the image - no metadata or context")
    print("="*60 + "\n")

    # Initialize tester
    tester = VisionModelTester(api_key)

    # Test random photo with all models
    tester.test_random_photo_all_models(
        photos_dir="data/photos",
        metadata_file="data/metadata.json"
    )

    print("\n✅ Test complete! Check data/results/random_photo_test.json for full results.")
    return 0

if __name__ == "__main__":
    sys.exit(main())