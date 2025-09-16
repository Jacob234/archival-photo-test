# Function Documentation

This document provides detailed documentation for all functions in the archival photo testing project.

## src/utils.py

### setup_logging(log_file: Optional[str] = None, level: str = "INFO") -> logging.Logger
Set up logging configuration for the project.

**Parameters:**
- `log_file`: Optional path to log file for persistent logging
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR)

**Returns:** Configured logger instance

**Usage:**
```python
logger = setup_logging("logs/app.log", "DEBUG")
```

### save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None
Save data to JSON file with automatic directory creation.

**Parameters:**
- `data`: Dictionary to save
- `filepath`: Path where JSON file should be saved
- `indent`: JSON indentation level for readability

**Usage:**
```python
save_json({"test": "data"}, "output/results.json")
```

### load_json(filepath: str) -> Dict[str, Any]
Load data from JSON file.

**Parameters:**
- `filepath`: Path to JSON file

**Returns:** Loaded dictionary

**Usage:**
```python
data = load_json("input/config.json")
```

### generate_photo_id(url: str) -> str
Generate unique 8-character photo ID from URL using MD5 hash.

**Parameters:**
- `url`: Photo URL

**Returns:** Unique 8-character photo ID

**Usage:**
```python
photo_id = generate_photo_id("https://example.com/photo.jpg")
# Returns: "a1b2c3d4"
```

### sanitize_filename(filename: str, max_length: int = 100) -> str
Sanitize filename for safe filesystem storage.

**Parameters:**
- `filename`: Original filename
- `max_length`: Maximum filename length

**Returns:** Sanitized filename safe for all filesystems

**Usage:**
```python
safe_name = sanitize_filename("photo<with>bad:chars.jpg")
# Returns: "photo_with_bad_chars.jpg"
```

### format_filesize(size_bytes: int) -> str
Format file size in human-readable format.

**Parameters:**
- `size_bytes`: File size in bytes

**Returns:** Formatted string (e.g., "1.5 MB")

**Usage:**
```python
readable_size = format_filesize(1536000)
# Returns: "1.5 MB"
```

### get_decade_from_year(year: str) -> str
Extract decade from year string using regex patterns.

**Parameters:**
- `year`: Year string (e.g., "1925", "circa 1920s")

**Returns:** Decade string (e.g., "1920s") or "unknown"

**Usage:**
```python
decade = get_decade_from_year("1925")
# Returns: "1920s"
decade = get_decade_from_year("circa 1930s")
# Returns: "1930s"
```

### calculate_cost(tokens: Dict[str, int], model_pricing: Dict[str, float]) -> float
Calculate API cost based on token usage and model pricing.

**Parameters:**
- `tokens`: Dictionary with 'input' and 'output' token counts
- `model_pricing`: Dictionary with 'input_per_1k' and 'output_per_1k' prices

**Returns:** Total cost in USD

**Usage:**
```python
cost = calculate_cost(
    {"input": 1000, "output": 500},
    {"input_per_1k": 0.003, "output_per_1k": 0.015}
)
# Returns: 0.0105
```

### ensure_directory(path: str) -> None
Ensure directory exists, creating parent directories as needed.

**Parameters:**
- `path`: Directory path to create

**Usage:**
```python
ensure_directory("data/photos/downloads")
```

## src/download_photos.py

### WikimediaDownloader Class

#### __init__(output_dir: str = "data/photos", metadata_file: str = "data/metadata.json")
Initialize downloader with output directories and API session.

**Parameters:**
- `output_dir`: Directory to save downloaded photos
- `metadata_file`: Path to metadata JSON file

#### get_category_members(category: str, limit: int = 50) -> List[str]
Get file members from a Wikimedia category using the API.

**Parameters:**
- `category`: Category name (e.g., "Category:1920s photographs")
- `limit`: Maximum number of files to retrieve

**Returns:** List of file titles

#### get_image_info(file_title: str) -> Optional[Dict[str, Any]]
Get detailed information about an image file from Wikimedia.

**Parameters:**
- `file_title`: Wikimedia file title (e.g., "File:Example.jpg")

**Returns:** Dictionary with image metadata or None if failed

#### classify_photo_type(title: str, description: str = "") -> str
Classify photo type based on title and description keywords.

**Parameters:**
- `title`: File title
- `description`: File description

**Returns:** Photo type category (portrait, street, building, event, work, miscellaneous)

#### download_image(url: str, filename: str, min_width: int = 500) -> bool
Download image from URL with size validation.

**Parameters:**
- `url`: Image URL
- `filename`: Local filename to save
- `min_width`: Minimum width requirement in pixels

**Returns:** True if successful, False otherwise

#### extract_metadata(file_title: str, image_info: Dict[str, Any]) -> Dict[str, Any]
Extract and format metadata from Wikimedia image info.

**Parameters:**
- `file_title`: Wikimedia file title
- `image_info`: Raw image info from API

**Returns:** Formatted metadata dictionary with all photo details

#### download_from_categories(target_count: int = 50) -> None
Download photos from all configured categories with balanced distribution.

**Parameters:**
- `target_count`: Total number of photos to download

**Process:**
1. Collects files from each category
2. Shuffles for diversity
3. Downloads with type balancing
4. Saves metadata and progress

## src/test_models.py

### VisionModelTester Class

#### __init__(api_key: str, results_dir: str = "data/results")
Initialize the vision model tester with OpenRouter API.

**Parameters:**
- `api_key`: OpenRouter API key
- `results_dir`: Directory to save test results

#### encode_image(image_path: str) -> str
Encode image file to base64 for API transmission.

**Parameters:**
- `image_path`: Path to image file

**Returns:** Base64 encoded image string

#### test_single_photo(image_path: str, model_key: str) -> Dict[str, Any]
Test a single photo with a specific model using blind methodology.

**Parameters:**
- `image_path`: Path to image file
- `model_key`: Model key from MODELS dict

**Returns:** Dictionary with test results including response, timing, and cost

#### test_all_models(photos_dir: str, metadata_file: str) -> None
Run comprehensive testing of all photos with all configured models.

**Process:**
1. Loads photo metadata
2. Tests each photo with each model
3. Provides progress tracking
4. Saves intermediate backups
5. Generates final reports

#### test_random_photo_all_models(photos_dir: str, metadata_file: str) -> None
Test a single randomly selected photo with all models for quick evaluation.

**Process:**
1. Selects random photo
2. Tests with all models
3. Saves timestamped results
4. Generates markdown report
5. Prints console summary

#### _create_markdown_report(results: Dict[str, Any], photo_meta: Dict[str, Any], output_file: str) -> None
Generate formatted Markdown report for human-readable analysis.

**Creates:**
- Performance comparison table
- Detailed model responses
- Cost and token usage metrics
- Test methodology notes

## src/evaluate_results.py

### ResultsEvaluator Class

#### __init__(results_dir: str = "data/results", reports_dir: str = "reports")
Initialize evaluator with input and output directories.

**Parameters:**
- `results_dir`: Directory containing test results files
- `reports_dir`: Directory for saving generated reports

#### load_results() -> Optional[Dict[str, Any]]
Load and combine test results and cost analysis data.

**Returns:** Combined data structure or None if files not found

#### analyze_performance_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]
Calculate comprehensive performance metrics for all models.

**Returns:** Performance analysis with success rates, response statistics, and sample responses

#### analyze_by_photo_type(results: List[Dict[str, Any]]) -> Dict[str, Any]
Analyze model performance segmented by photo type categories.

**Returns:** Photo type analysis showing success rates and quality metrics by category

#### analyze_by_decade(results: List[Dict[str, Any]]) -> Dict[str, Any]
Analyze model performance segmented by historical decade.

**Returns:** Decade analysis showing temporal performance trends

#### generate_markdown_report(data: Dict[str, Any]) -> str
Generate comprehensive stakeholder-ready markdown report.

**Returns:** Formatted markdown with executive summary, comparisons, and recommendations

#### create_evaluation_spreadsheet(data: Dict[str, Any]) -> None
Create Excel template for manual qualitative evaluation.

**Outputs:** Excel file with model responses and manual scoring columns

#### generate_all_reports() -> None
Generate complete suite of evaluation reports and analysis files.

**Outputs:**
- evaluation_report.md: Stakeholder report
- manual_evaluation_template.xlsx: Evaluation template
- detailed_analysis.json: Raw analysis data