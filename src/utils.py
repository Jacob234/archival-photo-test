"""
Utility functions for the archival photo testing project.

This module provides core utility functions used throughout the project:
- File operations (save/load JSON, directory management)
- Text processing (filename sanitization, date extraction)
- Logging setup
- Cost calculations for API usage
- Photo ID generation

Example:
    Basic usage of utilities:

    >>> from src.utils import save_json, load_json, setup_logging
    >>> logger = setup_logging()
    >>> data = {"test": "data"}
    >>> save_json(data, "output.json")
    >>> loaded = load_json("output.json")
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import pandas as pd

def setup_logging(log_file: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level),
        format=log_format,
        handlers=handlers
    )

    return logging.getLogger(__name__)

def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data to JSON file.

    Args:
        data: Dictionary to save
        filepath: Path to save file
        indent: JSON indentation level
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_photo_id(url: str) -> str:
    """
    Generate unique photo ID from URL.

    Args:
        url: Photo URL

    Returns:
        Unique photo ID
    """
    return hashlib.md5(url.encode()).hexdigest()[:8]

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename for safe filesystem storage.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length while preserving extension
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext

    return filename

def format_filesize(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_decade_from_year(year: str) -> str:
    """
    Extract decade from year string.

    Args:
        year: Year string (e.g., "1925", "circa 1920s")

    Returns:
        Decade string (e.g., "1920s")
    """
    import re

    # Try to extract 4-digit year
    match = re.search(r'\b(19\d{2}|20\d{2})\b', year)
    if match:
        year_num = int(match.group(1))
        decade = (year_num // 10) * 10
        return f"{decade}s"

    # Try to extract decade directly
    match = re.search(r'\b(19\d0s|20\d0s)\b', year)
    if match:
        return match.group(1)

    return "unknown"

def calculate_cost(tokens: Dict[str, int], model_pricing: Dict[str, float]) -> float:
    """
    Calculate API cost based on token usage.

    Args:
        tokens: Dictionary with 'input' and 'output' token counts
        model_pricing: Dictionary with 'input_per_1k' and 'output_per_1k' prices

    Returns:
        Total cost in USD
    """
    input_cost = (tokens.get('input', 0) / 1000) * model_pricing.get('input_per_1k', 0)
    output_cost = (tokens.get('output', 0) / 1000) * model_pricing.get('output_per_1k', 0)
    return input_cost + output_cost

def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if necessary.

    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def flatten_photo_test_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten nested photo test results into a list suitable for CSV conversion.

    Args:
        results: List of photo test results with nested model_results

    Returns:
        List of flattened dictionaries, one row per photo-model combination
    """
    flattened = []

    for photo_data in results:
        base_row = {
            "photo_id": photo_data.get("photo_id", ""),
            "test_timestamp": photo_data.get("timestamp", ""),
            "test_type": photo_data.get("test_type", ""),
            "wikimedia_title": photo_data.get("wikimedia_title", ""),
            "decade": photo_data.get("decade", ""),
            "photo_type": photo_data.get("photo_type", ""),
            "description": photo_data.get("description", "")
        }

        # Add results for each model
        model_results = photo_data.get("model_results", {})
        for model_key, model_result in model_results.items():
            row = base_row.copy()
            row.update({
                "model": model_key,
                "model_name": model_result.get("model_name", ""),
                "success": model_result.get("success", False),
                "error_message": model_result.get("error", ""),
                "processing_time": model_result.get("processing_time", 0),
                "input_tokens": model_result.get("input_tokens", 0),
                "output_tokens": model_result.get("output_tokens", 0),
                "total_tokens": model_result.get("total_tokens", 0),
                "cost_usd": model_result.get("cost_usd", 0),
                "response_length": len(model_result.get("response", "")),
                "full_response": model_result.get("response", ""),
                "model_timestamp": model_result.get("timestamp", "")
            })
            flattened.append(row)

    return flattened

def convert_json_results_to_csv(json_file: str, csv_file: str) -> bool:
    """
    Convert JSON test results to CSV format for pandas analysis.

    Args:
        json_file: Path to JSON results file
        csv_file: Path to output CSV file

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            # Batch test results format
            flattened_data = flatten_photo_test_results(data)
        elif isinstance(data, dict) and "model_results" in data:
            # Single photo test format
            flattened_data = flatten_photo_test_results([data])
        else:
            raise ValueError("Unrecognized JSON structure")

        # Convert to DataFrame and save
        df = pd.DataFrame(flattened_data)

        # Ensure directory exists
        ensure_directory(str(Path(csv_file).parent))

        # Save to CSV
        df.to_csv(csv_file, index=False, encoding='utf-8')

        return True

    except Exception as e:
        logger = setup_logging()
        logger.error(f"Error converting {json_file} to CSV: {e}")
        return False

def load_test_results_csv(csv_file: str) -> Optional[pd.DataFrame]:
    """
    Load test results from CSV file with proper data types.

    Args:
        csv_file: Path to CSV results file

    Returns:
        DataFrame with test results or None if file doesn't exist
    """
    try:
        if not os.path.exists(csv_file):
            return None

        df = pd.read_csv(csv_file, encoding='utf-8')

        # Convert data types for better analysis
        df['success'] = df['success'].astype(bool)
        df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
        df['cost_usd'] = pd.to_numeric(df['cost_usd'], errors='coerce')
        df['input_tokens'] = pd.to_numeric(df['input_tokens'], errors='coerce')
        df['output_tokens'] = pd.to_numeric(df['output_tokens'], errors='coerce')
        df['total_tokens'] = pd.to_numeric(df['total_tokens'], errors='coerce')
        df['response_length'] = pd.to_numeric(df['response_length'], errors='coerce')

        # Convert timestamp columns
        for col in ['test_timestamp', 'model_timestamp']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    except Exception as e:
        logger = setup_logging()
        logger.error(f"Error loading CSV {csv_file}: {e}")
        return None