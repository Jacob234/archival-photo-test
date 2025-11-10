"""
Vision model testing module for archival photo analysis.

This module provides comprehensive vision model testing capabilities using OpenRouter API.
It supports testing multiple AI vision models on historical photographs for archival
cataloging purposes. The system ensures blind testing by providing only images to models
without any contextual metadata.

Main functionality:
- Single and batch photo testing across multiple vision models
- Cost tracking and performance analysis
- Blind testing methodology (no metadata context provided to models)
- Comprehensive result formatting (JSON, CSV, Markdown)
- Unique filename generation to preserve test history
- Intermediate backup saving during long test runs

Example:
    Basic usage for random single photo testing:

    >>> from src.test_models import VisionModelTester
    >>> tester = VisionModelTester(api_key="your_key")
    >>> tester.test_random_photo_all_models("data/photos", "data/metadata.json")
"""

import os
import json
import time
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

# Compatibility fix for OpenRouter with newer httpx versions
try:
    from openai import OpenAI
    import openai
    from openai._base_client import SyncHttpxClientWrapper

    # Create a custom wrapper that removes the problematic 'proxies' argument
    class CustomHttpxClientWrapper(SyncHttpxClientWrapper):
        def __init__(self, *args, **kwargs):
            kwargs.pop("proxies", None)  # Remove the unsupported 'proxies' argument
            super().__init__(*args, **kwargs)

    # Apply the wrapper
    openai._base_client.SyncHttpxClientWrapper = CustomHttpxClientWrapper
except Exception:
    # Fallback to standard import if patch fails
    from openai import OpenAI

from utils import (
    setup_logging,
    load_json,
    save_json,
    calculate_cost,
    ensure_directory,
    convert_json_results_to_csv,
    flatten_photo_test_results
)

class VisionModelTester:
    """
    Tests multiple vision models for archival photo analysis via OpenRouter API.

    This class handles the complete workflow of testing vision models on historical photos:
    1. Connects to OpenRouter API for unified model access
    2. Tests photos with standardized archival cataloging prompt
    3. Ensures blind testing by excluding metadata from model input
    4. Tracks costs, performance metrics, and success rates
    5. Generates comprehensive reports in multiple formats
    6. Preserves test history with unique filename generation

    Attributes:
        MODELS: Dictionary of supported vision models with pricing
        ARCHIVAL_PROMPT: Standardized prompt for archival photo analysis
        client: OpenRouter API client instance
        results_dir: Directory for saving test results
        logger: Configured logger instance
    """

    # Model configurations with pricing (per 1K tokens)
    # All models accessible via OpenRouter API
    # Pricing as of 2025 - verify current rates at https://openrouter.ai/models
    MODELS = {
        # ===== FREE TIER ($0 - unlimited testing!) =====
        "gemini-2.0-flash-free": {
            "name": "google/gemini-2.0-flash-exp:free",
            "description": "Gemini 2.0 Flash Experimental - FREE Google vision model",
            "pricing": {"input_per_1k": 0, "output_per_1k": 0},
            "local_capable": False
        },
        "qwen2.5-vl-32b-free": {
            "name": "qwen/qwen2.5-vl-32b-instruct:free",
            "description": "Qwen2.5-VL 32B - FREE, excellent for documents/diagrams",
            "pricing": {"input_per_1k": 0, "output_per_1k": 0},
            "local_capable": True  # Can download and run locally
        },
        "llama-4-scout-free": {
            "name": "meta-llama/llama-4-scout:free",
            "description": "Llama 4 Scout - FREE Meta vision model",
            "pricing": {"input_per_1k": 0, "output_per_1k": 0},
            "local_capable": True
        },

        # ===== ULTRA-BUDGET TIER (< $0.10 per 1M input tokens) =====
        "llama-3.2-11b-vision": {
            "name": "meta-llama/llama-3.2-11b-vision-instruct",
            "description": "Llama 3.2 11B Vision - Excellent local-capable model",
            "pricing": {"input_per_1k": 0.000049, "output_per_1k": 0.000049},
            "local_capable": True
        },
        "qwen2.5-vl-32b": {
            "name": "qwen/qwen2.5-vl-32b-instruct",
            "description": "Qwen2.5-VL 32B - Outstanding document understanding",
            "pricing": {"input_per_1k": 0.00005, "output_per_1k": 0.00022},
            "local_capable": True
        },
        "gemini-2.0-flash-lite": {
            "name": "google/gemini-2.0-flash-lite-001",
            "description": "Gemini 2.0 Flash Lite - Ultra-efficient Google model",
            "pricing": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
            "local_capable": False
        },
        "qwen2.5-vl-72b": {
            "name": "qwen/qwen2.5-vl-72b-instruct",
            "description": "Qwen2.5-VL 72B - Larger model, better quality",
            "pricing": {"input_per_1k": 0.00008, "output_per_1k": 0.00033},
            "local_capable": True
        },
        "pixtral-12b": {
            "name": "mistralai/pixtral-12b",
            "description": "Pixtral 12B - Mistral's vision model, local-capable",
            "pricing": {"input_per_1k": 0.0001, "output_per_1k": 0.0001},
            "local_capable": True
        },

        # ===== BUDGET TIER ($0.10-$1 per 1M input tokens) =====
        "gemini-2.0-flash": {
            "name": "google/gemini-2.0-flash-001",
            "description": "Gemini 2.0 Flash - Latest Google vision model",
            "pricing": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
            "local_capable": False
        },
        "gpt-4o-mini": {
            "name": "openai/gpt-4o-mini",
            "description": "GPT-4o Mini - Cost-optimized OpenAI vision model",
            "pricing": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
            "local_capable": False
        },
        "claude-3.5-haiku": {
            "name": "anthropic/claude-3.5-haiku",
            "description": "Claude 3.5 Haiku - Fast, affordable Anthropic model",
            "pricing": {"input_per_1k": 0.0008, "output_per_1k": 0.004},
            "local_capable": False
        },

        # ===== MID TIER ($1-$5 per 1M input tokens) =====
        "claude-3.5-sonnet": {
            "name": "anthropic/claude-3.5-sonnet",
            "description": "Claude 3.5 Sonnet - High-performance Anthropic model",
            "pricing": {"input_per_1k": 0.003, "output_per_1k": 0.015},
            "local_capable": False
        },

        # ===== PREMIUM TIER ($5+ per 1M input tokens) =====
        "gpt-4o": {
            "name": "openai/gpt-4o",
            "description": "GPT-4o - Flagship OpenAI vision model",
            "pricing": {"input_per_1k": 0.0025, "output_per_1k": 0.010},
            "local_capable": False
        },
        "claude-3-opus": {
            "name": "anthropic/claude-3-opus",
            "description": "Claude 3 Opus - Most powerful Anthropic vision model",
            "pricing": {"input_per_1k": 0.015, "output_per_1k": 0.075},
            "local_capable": False
        }
    }

    # Note: For LOCAL vision models (LLaVA, Qwen2-VL, Pixtral, Llama 3.2 Vision):
    # These models can run on consumer hardware but require different setup:
    # - Option 1: Run via Ollama (ollama.ai) with models like llava:7b, llama3.2-vision
    # - Option 2: Use vLLM or text-generation-inference for production deployment
    # - Option 3: Run with Hugging Face Transformers directly
    # Pros: Zero API costs, data privacy, no rate limits
    # Cons: Requires GPU (8GB+ VRAM), slower than cloud APIs, manual setup
    #
    # To add local models, you would need to:
    # 1. Set up Ollama or similar inference server
    # 2. Create separate client/method for local model inference
    # 3. Add models to MODELS dict with "local" provider type
    #
    # Recommended local models for archival photo analysis:
    # - Qwen2.5-VL-7B: Excellent document/diagram understanding
    # - Llama-3.2-11B-Vision: Good general vision capabilities
    # - LLaVA-NeXT: Strong multimodal reasoning
    # - Pixtral-12B: Good instruction following

    ARCHIVAL_PROMPT = """Describe this historical photograph in detail for archival cataloging in TOML. Include:

- People: number, apparent age, clothing, activities
- Setting: location type, time period indicators, notable objects
- Photo quality: condition, clarity, any damage
- Historical context: estimated decade, cultural/social elements
- Archival value: what makes this photo historically significant

Be specific and detailed in your description to help with future research and cataloging."""

    def __init__(self, api_key: str, results_dir: str = "data/results"):
        """
        Initialize the vision model tester.

        Args:
            api_key: OpenRouter API key
            results_dir: Directory to save results
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.results_dir = results_dir
        self.logger = setup_logging()
        ensure_directory(self.results_dir)

    def encode_image(self, image_path: str) -> str:
        """
        Encode image file to base64.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def test_single_photo(self, image_path: str, model_key: str) -> Dict[str, Any]:
        """
        Test a single photo with a specific model.

        Args:
            image_path: Path to image file
            model_key: Model key from MODELS dict

        Returns:
            Dictionary with test results
        """
        model_config = self.MODELS[model_key]
        start_time = time.time()

        try:
            # Encode image
            base64_image = self.encode_image(image_path)

            # Prepare message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.ARCHIVAL_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            # Make API call
            response = self.client.chat.completions.create(
                model=model_config["name"],
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )

            end_time = time.time()

            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage

            # Calculate cost
            token_usage = {
                "input": usage.prompt_tokens,
                "output": usage.completion_tokens
            }
            cost = calculate_cost(token_usage, model_config["pricing"])

            return {
                "success": True,
                "model": model_key,
                "model_name": model_config["name"],
                "response": content,
                "processing_time": end_time - start_time,
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": cost,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            end_time = time.time()
            self.logger.error(f"Error testing {model_key} on {image_path}: {e}")

            return {
                "success": False,
                "model": model_key,
                "model_name": model_config["name"],
                "error": str(e),
                "processing_time": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            }

    def test_all_models(self, photos_dir: str, metadata_file: str) -> None:
        """
        Run comprehensive testing of all photos with all configured models.

        This method performs batch testing of the entire photo collection against
        all available vision models. It provides progress tracking, intermediate
        backups, and generates comprehensive results in multiple formats.

        Args:
            photos_dir: Directory containing downloaded photos
            metadata_file: Path to metadata JSON file from download phase

        Results:
            - Raw JSON results (model_test_results.json)
            - CSV summary for analysis (model_comparison.csv)
            - Cost analysis report (cost_analysis.json)
            - Intermediate backups every 5 photos
        """
        # Load metadata
        metadata = load_json(metadata_file)

        if not metadata:
            self.logger.error("No metadata found. Please download photos first.")
            return

        # Initialize results
        all_results = []
        total_tests = len(metadata) * len(self.MODELS)

        self.logger.info(f"Starting tests: {len(metadata)} photos × {len(self.MODELS)} models = {total_tests} tests")

        # Progress bar for all tests
        pbar = tqdm(total=total_tests, desc="Testing models")

        # Test each photo with each model
        for photo_meta in metadata:
            image_path = os.path.join(photos_dir, photo_meta["local_filename"])

            if not os.path.exists(image_path):
                self.logger.warning(f"Image not found: {image_path}")
                pbar.update(len(self.MODELS))
                continue

            photo_results = {
                "photo_id": photo_meta.get("local_filename", "unknown"),
                "wikimedia_title": photo_meta.get("wikimedia_title", ""),
                "decade": photo_meta.get("decade", "unknown"),
                "photo_type": photo_meta.get("photo_type", "unknown"),
                "description": photo_meta.get("description", ""),
                "model_results": {}
            }

            # Test with each model
            for model_key in self.MODELS.keys():
                result = self.test_single_photo(image_path, model_key)
                photo_results["model_results"][model_key] = result

                pbar.update(1)
                pbar.set_description(f"Testing {model_key}")

                # Rate limiting
                time.sleep(1)

            all_results.append(photo_results)

            # Save intermediate results (backup)
            if len(all_results) % 5 == 0:
                self._save_intermediate_results(all_results)

        pbar.close()

        # Save final results
        self._save_final_results(all_results)

    def _save_intermediate_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Save intermediate results as timestamped backup.

        Creates backup files during long test runs to prevent data loss.
        Called automatically every 5 photos during batch testing.

        Args:
            results: Current accumulated test results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.results_dir, f"backup_results_{timestamp}.json")
        save_json(results, backup_file)

    def _save_final_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Save final results in multiple formats for comprehensive analysis.

        Generates three output formats:
        1. Raw JSON for programmatic access
        2. CSV summary for spreadsheet analysis
        3. Cost analysis for budget planning

        Args:
            results: Complete test results from all photos and models
        """
        # Save raw JSON results
        json_file = os.path.join(self.results_dir, "model_test_results.json")
        save_json(results, json_file)

        # Create CSV summary
        self._create_csv_summary(results)

        # Create cost analysis
        self._create_cost_analysis(results)

        # Export to comprehensive CSV format
        self.export_results_to_csv(json_file)

        self.logger.info(f"Results saved to {self.results_dir}")

    def _create_csv_summary(self, results: List[Dict[str, Any]]) -> None:
        """
        Create CSV summary for spreadsheet analysis and data export.

        Flattens the nested JSON results into a tabular format suitable for
        analysis in spreadsheet applications. Includes photo metadata,
        model performance metrics, and truncated responses.

        Args:
            results: Complete test results from all photos and models
        """
        csv_data = []

        for photo_data in results:
            base_row = {
                "photo_id": photo_data["photo_id"],
                "wikimedia_title": photo_data["wikimedia_title"],
                "decade": photo_data["decade"],
                "photo_type": photo_data["photo_type"],
                "description": photo_data.get("description", "")[:100] + "..." if len(photo_data.get("description", "")) > 100 else photo_data.get("description", "")
            }

            # Add results for each model
            for model_key, model_result in photo_data["model_results"].items():
                row = base_row.copy()
                row.update({
                    "model": model_key,
                    "model_name": model_result.get("model_name", ""),
                    "success": model_result.get("success", False),
                    "response_length": len(model_result.get("response", "")),
                    "processing_time": model_result.get("processing_time", 0),
                    "input_tokens": model_result.get("input_tokens", 0),
                    "output_tokens": model_result.get("output_tokens", 0),
                    "cost_usd": model_result.get("cost_usd", 0),
                    "response": model_result.get("response", "")[:200] + "..." if len(model_result.get("response", "")) > 200 else model_result.get("response", "")
                })
                csv_data.append(row)

        # Save to CSV
        df = pd.DataFrame(csv_data)
        csv_file = os.path.join(self.results_dir, "model_comparison.csv")
        df.to_csv(csv_file, index=False)

    def _create_cost_analysis(self, results: List[Dict[str, Any]]) -> None:
        """
        Generate comprehensive cost and performance analysis by model.

        Calculates key metrics for budget planning and model comparison:
        - Total and per-photo costs for each model
        - Success rates and processing times
        - Projected costs for larger datasets (per 1000 photos)

        Args:
            results: Complete test results from all photos and models
        """
        cost_summary = {}

        for model_key in self.MODELS.keys():
            model_costs = []
            model_times = []
            success_count = 0
            total_count = 0

            for photo_data in results:
                model_result = photo_data["model_results"].get(model_key, {})
                total_count += 1

                if model_result.get("success", False):
                    success_count += 1
                    model_costs.append(model_result.get("cost_usd", 0))
                    model_times.append(model_result.get("processing_time", 0))

            cost_summary[model_key] = {
                "model_name": self.MODELS[model_key]["name"],
                "description": self.MODELS[model_key]["description"],
                "total_photos": total_count,
                "successful_tests": success_count,
                "success_rate": success_count / total_count if total_count > 0 else 0,
                "total_cost_usd": sum(model_costs),
                "avg_cost_per_photo": sum(model_costs) / len(model_costs) if model_costs else 0,
                "cost_per_1000_photos": (sum(model_costs) / len(model_costs) * 1000) if model_costs else 0,
                "avg_processing_time": sum(model_times) / len(model_times) if model_times else 0,
                "total_processing_time": sum(model_times)
            }

        # Save cost analysis
        cost_file = os.path.join(self.results_dir, "cost_analysis.json")
        save_json(cost_summary, cost_file, indent=2)

    def export_results_to_csv(self, json_file: str, csv_file: Optional[str] = None) -> bool:
        """
        Export JSON test results to CSV format for pandas analysis.

        Converts nested JSON results into a flattened CSV structure that's optimal
        for pandas operations, filtering, and analysis. Includes full response text
        and all metadata for comprehensive analysis.

        Args:
            json_file: Path to JSON results file to convert
            csv_file: Optional path for CSV output (auto-generated if not provided)

        Returns:
            True if export successful, False otherwise
        """
        if csv_file is None:
            # Auto-generate CSV filename from JSON filename
            json_path = Path(json_file)
            csv_file = str(json_path.with_suffix('.csv'))

        success = convert_json_results_to_csv(json_file, csv_file)

        if success:
            self.logger.info(f"Successfully exported {json_file} to {csv_file}")
        else:
            self.logger.error(f"Failed to export {json_file} to CSV")

        return success

    def export_all_json_to_csv(self) -> None:
        """
        Convert all existing JSON result files in results directory to CSV format.

        Scans the results directory for JSON files and converts each to CSV format.
        Useful for batch conversion of historical test results.
        """
        json_files = list(Path(self.results_dir).glob("*.json"))

        if not json_files:
            self.logger.info("No JSON files found to convert")
            return

        converted_count = 0
        for json_file in json_files:
            if self.export_results_to_csv(str(json_file)):
                converted_count += 1

        self.logger.info(f"Converted {converted_count}/{len(json_files)} JSON files to CSV")

    def test_random_photo_all_models(self, photos_dir: str, metadata_file: str) -> None:
        """
        Test a single randomly selected photo with all configured models.

        This method implements blind testing by selecting a random photo and testing
        it with all models without providing any contextual metadata. Results are
        saved with unique timestamps to preserve test history.

        Perfect for:
        - Initial model evaluation and comparison
        - Quick quality checks before full batch runs
        - Demonstrating model capabilities on specific examples

        Args:
            photos_dir: Directory containing downloaded photos
            metadata_file: Path to metadata JSON file from download phase

        Outputs:
            - Timestamped JSON results file
            - Formatted Markdown report for easy reading
            - Console summary with key metrics
        """
        import random

        # Load metadata
        metadata = load_json(metadata_file)

        if not metadata:
            self.logger.error("No metadata found. Please download photos first.")
            return

        # Select random photo
        photo_meta = random.choice(metadata)
        image_path = os.path.join(photos_dir, photo_meta["local_filename"])

        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return

        self.logger.info(f"Testing random photo: {photo_meta['local_filename']}")
        self.logger.info(f"Photo metadata (not shared with models):")
        self.logger.info(f"  - Decade: {photo_meta.get('decade', 'unknown')}")
        self.logger.info(f"  - Type: {photo_meta.get('photo_type', 'unknown')}")

        # Test with all models
        results = {
            "photo_id": photo_meta["local_filename"],
            "test_type": "random_single",
            "timestamp": datetime.now().isoformat(),
            "model_results": {}
        }

        for model_key in self.MODELS.keys():
            self.logger.info(f"Testing with {model_key}...")
            result = self.test_single_photo(image_path, model_key)
            results["model_results"][model_key] = result

            if result["success"]:
                self.logger.info(f"  ✓ {model_key} completed in {result['processing_time']:.2f}s")
                self.logger.info(f"    Cost: ${result.get('cost_usd', 0):.6f}")
            else:
                self.logger.error(f"  ✗ {model_key} failed: {result.get('error', 'Unknown error')}")

            # Rate limiting
            time.sleep(1)

        # Save results with unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        photo_base = os.path.splitext(photo_meta["local_filename"])[0]  # Remove extension

        output_file = os.path.join(self.results_dir, f"random_test_{timestamp}_{photo_base}.json")
        save_json(results, output_file, indent=2)
        self.logger.info(f"Results saved to {output_file}")

        # Export to CSV format
        csv_file = os.path.join(self.results_dir, f"random_test_{timestamp}_{photo_base}.csv")
        if self.export_results_to_csv(output_file, csv_file):
            self.logger.info(f"CSV export saved to {csv_file}")

        # Generate markdown report with unique filename
        markdown_file = os.path.join(self.results_dir, f"random_test_{timestamp}_{photo_base}.md")
        self._create_markdown_report(results, photo_meta, markdown_file)
        self.logger.info(f"Markdown report saved to {markdown_file}")

        # Print summary
        print("\n" + "="*60)
        print("RANDOM PHOTO TEST SUMMARY")
        print("="*60)
        print(f"Photo: {photo_meta['local_filename']}")
        print(f"Actual decade: {photo_meta.get('decade', 'unknown')}")
        print(f"Actual type: {photo_meta.get('photo_type', 'unknown')}")
        print("\nModel Results:")

        for model_key, result in results["model_results"].items():
            if result["success"]:
                print(f"\n{model_key}:")
                print(f"  Time: {result['processing_time']:.2f}s")
                print(f"  Cost: ${result.get('cost_usd', 0):.6f}")
                print(f"  Tokens: {result.get('total_tokens', 0)}")
                print(f"  Response preview: {result['response'][:200]}...")
            else:
                print(f"\n{model_key}: FAILED - {result.get('error', 'Unknown error')}")

    def _create_markdown_report(self, results: Dict[str, Any], photo_meta: Dict[str, Any], output_file: str) -> None:
        """
        Generate a formatted Markdown report for human-readable analysis.

        Creates a comprehensive report including:
        - Photo metadata and test information
        - Performance comparison table across all models
        - Detailed responses from each model with proper formatting
        - Cost and token usage metrics
        - Test methodology notes

        Args:
            results: Test results from all models for single photo
            photo_meta: Original photo metadata (not shared with models)
            output_file: Path where Markdown report should be saved
        """
        def format_response_text(text: str) -> str:
            """Format response text with proper line breaks."""
            # Replace escaped newlines with actual newlines
            formatted = text.replace('\\n', '\n')
            # Ensure proper spacing for sections
            formatted = formatted.replace('**', '\n**')
            formatted = formatted.replace('- ', '\n- ')
            # Clean up extra newlines
            lines = [line.strip() for line in formatted.split('\n') if line.strip()]
            return '\n'.join(lines)

        photo_id = results.get('photo_id', 'unknown')
        timestamp = results.get('timestamp', datetime.now().isoformat())

        markdown_lines = [
            f"# Vision Model Analysis: {photo_id}",
            f"",
            f"**Test Date:** {timestamp}",
            f"**Photo ID:** {photo_id}",
            f"**Actual Decade:** {photo_meta.get('decade', 'unknown')}",
            f"**Actual Type:** {photo_meta.get('photo_type', 'unknown')}",
            f"**Source:** {photo_meta.get('wikimedia_title', 'unknown')}",
            f"",
            f"## Model Performance Summary",
            f""
        ]

        # Create summary table
        markdown_lines.extend([
            "| Model | Status | Cost (USD) | Time (s) | Input Tokens | Output Tokens | Total Tokens |",
            "|-------|--------|------------|----------|--------------|---------------|--------------|"
        ])

        for model_key, result in results.get('model_results', {}).items():
            if result.get('success', False):
                cost = f"${result.get('cost_usd', 0):.6f}"
                time_val = f"{result.get('processing_time', 0):.2f}"
                input_tokens = str(result.get('input_tokens', 0))
                output_tokens = str(result.get('output_tokens', 0))
                total_tokens = str(result.get('total_tokens', 0))
                status = "✅ Success"
            else:
                cost = "N/A"
                time_val = "N/A"
                input_tokens = "N/A"
                output_tokens = "N/A"
                total_tokens = "N/A"
                status = "❌ Failed"

            markdown_lines.append(
                f"| {model_key} | {status} | {cost} | {time_val} | {input_tokens} | {output_tokens} | {total_tokens} |"
            )

        markdown_lines.extend(["", "## Detailed Model Responses", ""])

        # Add detailed responses
        for model_key, result in results.get('model_results', {}).items():
            model_config = self.MODELS.get(model_key, {})
            markdown_lines.extend([
                f"### {model_key}",
                f"",
                f"**Model:** {model_config.get('name', 'unknown')}",
                f"**Description:** {model_config.get('description', 'No description')}",
                ""
            ])

            if result.get('success', False):
                # Add performance metrics
                markdown_lines.extend([
                    f"**Performance Metrics:**",
                    f"- Cost: ${result.get('cost_usd', 0):.6f}",
                    f"- Processing Time: {result.get('processing_time', 0):.2f} seconds",
                    f"- Input Tokens: {result.get('input_tokens', 0):,}",
                    f"- Output Tokens: {result.get('output_tokens', 0):,}",
                    f"- Total Tokens: {result.get('total_tokens', 0):,}",
                    "",
                    "**Response:**",
                    ""
                ])

                # Format and add response text
                response_text = format_response_text(result.get('response', ''))
                markdown_lines.append(response_text)
            else:
                markdown_lines.extend([
                    f"**Status:** ❌ Failed",
                    f"**Error:** {result.get('error', 'Unknown error')}",
                    f"**Processing Time:** {result.get('processing_time', 0):.2f} seconds"
                ])

            markdown_lines.extend(["", "---", ""])

        # Add footer
        markdown_lines.extend([
            "",
            f"*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*",
            "",
            "## Notes",
            "",
            "- Models received only the image and standardized archival prompt",
            "- No contextual metadata was provided to ensure blind evaluation",
            "- Costs calculated based on token usage and current pricing"
        ])

        # Write markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))

def main():
    """Main function to run vision model tests."""
    # Load environment variables
    load_dotenv("config/.env")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please create config/.env file with your OpenRouter API key.")
        return

    # Initialize tester
    tester = VisionModelTester(api_key)

    # Run tests
    tester.test_all_models(
        photos_dir="data/photos",
        metadata_file="data/metadata.json"
    )

if __name__ == "__main__":
    main()