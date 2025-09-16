#!/usr/bin/env python3
"""
Main script to run the complete archival photo vision model testing pipeline.
"""

import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from download_photos import WikimediaDownloader
from test_models import VisionModelTester
from evaluate_results import ResultsEvaluator
from utils import setup_logging

def main():
    """Main function to run the complete testing pipeline."""
    parser = argparse.ArgumentParser(description="Archival Photo Vision Model Testing")
    parser.add_argument("--skip-download", action="store_true", help="Skip photo download phase")
    parser.add_argument("--skip-testing", action="store_true", help="Skip model testing phase")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip evaluation phase")
    parser.add_argument("--photos", type=int, default=50, help="Number of photos to download")
    parser.add_argument("--api-key", type=str, help="OpenRouter API key (or set OPENROUTER_API_KEY env var)")

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging()

    # Load environment variables
    load_dotenv("config/.env")

    # Get API key
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")

    print("🏛️  Archival Photo Vision Model Testing Pipeline")
    print("=" * 60)

    # Phase 1: Download Photos
    if not args.skip_download:
        print("\n📥 Phase 1: Downloading Historical Photos")
        print("-" * 40)

        if os.path.exists("data/metadata.json"):
            logger.info("Photos already downloaded. Use --skip-download to skip this phase.")
        else:
            downloader = WikimediaDownloader()
            downloader.download_from_categories(target_count=args.photos)

        print("✅ Photo download complete")

    # Phase 2: Test Vision Models
    if not args.skip_testing:
        print("\n🔍 Phase 2: Testing Vision Models")
        print("-" * 40)

        if not api_key:
            print("❌ Error: OpenRouter API key required for testing phase.")
            print("   Set OPENROUTER_API_KEY environment variable or use --api-key flag.")
            return 1

        if os.path.exists("data/results/model_test_results.json"):
            logger.info("Model tests already completed. Use --skip-testing to skip this phase.")
        else:
            tester = VisionModelTester(api_key)
            tester.test_all_models(
                photos_dir="data/photos",
                metadata_file="data/metadata.json"
            )

        print("✅ Model testing complete")

    # Phase 3: Evaluate Results
    if not args.skip_evaluation:
        print("\n📊 Phase 3: Evaluating Results")
        print("-" * 40)

        evaluator = ResultsEvaluator()
        evaluator.generate_all_reports()

        print("✅ Evaluation complete")

    print("\n🎉 Pipeline Complete!")
    print("\nGenerated Files:")
    print("- data/photos/           - Downloaded historical photos")
    print("- data/metadata.json     - Photo metadata")
    print("- data/results/          - Model test results")
    print("- reports/               - Evaluation reports and analysis")

    print("\nNext Steps:")
    print("1. Review reports/evaluation_report.md for findings")
    print("2. Use reports/manual_evaluation_template.xlsx for detailed scoring")
    print("3. Check data/results/cost_analysis.json for cost projections")

    return 0

if __name__ == "__main__":
    sys.exit(main())