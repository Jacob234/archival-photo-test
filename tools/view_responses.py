#!/usr/bin/env python3
"""
Pretty viewer for vision model responses.
Formats JSON results into readable terminal and markdown output.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

def load_results(file_path: str) -> Dict[str, Any]:
    """Load results from JSON file."""
    if not os.path.exists(file_path):
        print(f"❌ Results file not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r') as f:
        return json.load(f)

def format_response_text(text: str, max_width: int = 80) -> str:
    """Format response text with proper line breaks."""
    # Replace \n with actual newlines
    formatted = text.replace('\\n', '\n')

    # Ensure proper spacing for sections
    formatted = formatted.replace('**', '\n**')
    formatted = formatted.replace('- ', '\n- ')

    # Clean up extra newlines
    lines = [line.strip() for line in formatted.split('\n') if line.strip()]
    return '\n'.join(lines)

def print_model_response(model_key: str, result: Dict[str, Any], photo_id: str):
    """Print a single model's response with formatting."""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{model_key.upper()}")
    print(f"{Fore.CYAN}{'='*80}")

    if not result.get("success", False):
        print(f"{Fore.RED}❌ FAILED: {result.get('error', 'Unknown error')}")
        return

    # Print metadata
    print(f"{Fore.GREEN}✓ Success")
    print(f"{Fore.YELLOW}Cost: ${result.get('cost_usd', 0):.6f}")
    print(f"{Fore.YELLOW}Time: {result.get('processing_time', 0):.2f}s")
    print(f"{Fore.YELLOW}Tokens: {result.get('total_tokens', 0)} (in: {result.get('input_tokens', 0)}, out: {result.get('output_tokens', 0)})")

    # Print response
    print(f"\n{Fore.WHITE}{Style.BRIGHT}RESPONSE:")
    print(f"{Fore.WHITE}{'-'*40}")

    response_text = format_response_text(result.get('response', ''))
    print(f"{Fore.WHITE}{response_text}")

def create_markdown_report(results: Dict[str, Any], output_file: str):
    """Create a markdown report of the results."""
    photo_id = results.get('photo_id', 'unknown')
    timestamp = results.get('timestamp', datetime.now().isoformat())

    markdown_lines = [
        f"# Vision Model Test Results",
        f"",
        f"**Photo:** {photo_id}",
        f"**Test Date:** {timestamp}",
        f"**Test Type:** {results.get('test_type', 'unknown')}",
        f"",
        f"## Model Comparison Summary",
        f""
    ]

    # Create summary table
    markdown_lines.extend([
        "| Model | Status | Cost | Time | Tokens |",
        "|-------|--------|------|------|--------|"
    ])

    for model_key, result in results.get('model_results', {}).items():
        if result.get('success', False):
            cost = f"${result.get('cost_usd', 0):.6f}"
            time_val = f"{result.get('processing_time', 0):.2f}s"
            tokens = str(result.get('total_tokens', 0))
            status = "✅ Success"
        else:
            cost = "N/A"
            time_val = "N/A"
            tokens = "N/A"
            status = "❌ Failed"

        markdown_lines.append(f"| {model_key} | {status} | {cost} | {time_val} | {tokens} |")

    markdown_lines.extend(["", "## Detailed Responses", ""])

    # Add detailed responses
    for model_key, result in results.get('model_results', {}).items():
        markdown_lines.extend([
            f"### {model_key}",
            ""
        ])

        if result.get('success', False):
            # Add metadata
            markdown_lines.extend([
                f"**Cost:** ${result.get('cost_usd', 0):.6f}",
                f"**Processing Time:** {result.get('processing_time', 0):.2f} seconds",
                f"**Tokens:** {result.get('total_tokens', 0)} (Input: {result.get('input_tokens', 0)}, Output: {result.get('output_tokens', 0)})",
                "",
                "**Response:**",
                ""
            ])

            # Format response text
            response_text = format_response_text(result.get('response', ''))
            markdown_lines.append(response_text)
        else:
            markdown_lines.append(f"**Error:** {result.get('error', 'Unknown error')}")

        markdown_lines.extend(["", "---", ""])

    # Write markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))

def find_latest_test_file() -> str:
    """Find the most recent random test file."""
    import glob

    # Look for random test files
    pattern = "data/results/random_test_*.json"
    test_files = glob.glob(pattern)

    if not test_files:
        # Fallback to old naming scheme
        old_file = "data/results/random_photo_test.json"
        if os.path.exists(old_file):
            return old_file
        return None

    # Sort by filename (which includes timestamp) to get most recent
    test_files.sort(reverse=True)
    return test_files[0]

def list_available_tests():
    """List all available test files."""
    import glob

    pattern = "data/results/random_test_*.json"
    test_files = glob.glob(pattern)

    # Also check for old format
    old_file = "data/results/random_photo_test.json"
    if os.path.exists(old_file):
        test_files.append(old_file)

    if not test_files:
        print("❌ No test files found.")
        return

    print("\n📁 Available test files:")
    test_files.sort(reverse=True)
    for i, file in enumerate(test_files, 1):
        # Extract info from filename if possible
        basename = os.path.basename(file)
        if basename.startswith("random_test_"):
            parts = basename.replace("random_test_", "").replace(".json", "").split("_")
            if len(parts) >= 3:
                date_part = parts[0]
                time_part = parts[1]
                photo_part = "_".join(parts[2:])
                formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                print(f"  {i:2d}. {basename}")
                print(f"      Date: {formatted_date} {formatted_time}, Photo: {photo_part}")
            else:
                print(f"  {i:2d}. {basename}")
        else:
            print(f"  {i:2d}. {basename}")

def main():
    """Main function to view responses."""
    # Check for special commands
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--list", "-l"]:
            list_available_tests()
            return
        results_file = sys.argv[1]
    else:
        # Find the most recent test file
        results_file = find_latest_test_file()

        if not results_file:
            print("❌ No test files found.")
            print("\nUsage:")
            print(f"  python {sys.argv[0]} [results_file.json]")
            print(f"  python {sys.argv[0]} --list              # List all available tests")
            print(f"  python {sys.argv[0]}                     # Use most recent test")
            print("\nRun some tests first with: python test_single_photo.py")
            sys.exit(1)

    if not os.path.exists(results_file):
        print(f"❌ File not found: {results_file}")
        print("\nAvailable options:")
        list_available_tests()
        print(f"\nUsage:")
        print(f"  python {sys.argv[0]} [results_file.json]")
        print(f"  python {sys.argv[0]} --list              # List all available tests")
        sys.exit(1)

    # Load results
    results = load_results(results_file)
    photo_id = results.get('photo_id', 'unknown')

    # Print header
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'='*80}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}🖼️  VISION MODEL RESPONSES")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*80}")
    print(f"{Fore.WHITE}Photo: {photo_id}")
    print(f"{Fore.WHITE}Test Date: {results.get('timestamp', 'unknown')}")

    # Print each model's response
    model_results = results.get('model_results', {})
    for model_key, result in model_results.items():
        print_model_response(model_key, result, photo_id)

    # Print summary
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'='*80}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}SUMMARY")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*80}")

    successful_models = [k for k, v in model_results.items() if v.get('success', False)]
    failed_models = [k for k, v in model_results.items() if not v.get('success', False)]

    print(f"{Fore.GREEN}✅ Successful models: {len(successful_models)}")
    for model in successful_models:
        result = model_results[model]
        print(f"   {Fore.GREEN}{model}: ${result.get('cost_usd', 0):.6f}, {result.get('processing_time', 0):.2f}s")

    if failed_models:
        print(f"{Fore.RED}❌ Failed models: {len(failed_models)}")
        for model in failed_models:
            print(f"   {Fore.RED}{model}: {model_results[model].get('error', 'Unknown error')}")

    # Generate markdown report
    base_name = os.path.splitext(results_file)[0]
    markdown_file = f"{base_name}.md"
    create_markdown_report(results, markdown_file)

    print(f"\n{Fore.CYAN}📄 Markdown report saved: {markdown_file}")
    print(f"{Fore.CYAN}📊 Original JSON: {results_file}")

if __name__ == "__main__":
    main()