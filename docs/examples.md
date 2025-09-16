# Usage Examples

This document provides practical examples for using the archival photo testing project.

## Quick Start

### 1. Download Historical Photos
```python
from src.download_photos import WikimediaDownloader

# Download 50 historical photos
downloader = WikimediaDownloader()
downloader.download_from_categories(target_count=50)
```

### 2. Test Single Random Photo
```python
from src.test_models import VisionModelTester
import os

# Initialize tester
api_key = os.getenv("OPENROUTER_API_KEY")
tester = VisionModelTester(api_key)

# Test random photo with all models
tester.test_random_photo_all_models("data/photos", "data/metadata.json")
```

### 3. Generate Evaluation Reports
```python
from src.evaluate_results import ResultsEvaluator

# Generate comprehensive reports
evaluator = ResultsEvaluator()
evaluator.generate_all_reports()
```

## Detailed Examples

### Custom Photo Download

```python
from src.download_photos import WikimediaDownloader

# Custom configuration
downloader = WikimediaDownloader(
    output_dir="custom/photos",
    metadata_file="custom/metadata.json"
)

# Download more photos
downloader.download_from_categories(target_count=100)
```

### Testing Specific Models

```python
from src.test_models import VisionModelTester

tester = VisionModelTester(api_key="your_key")

# Test single photo with specific model
result = tester.test_single_photo(
    "data/photos/photo_abc123.jpg",
    "gpt-4o"
)

print(f"Response: {result['response']}")
print(f"Cost: ${result['cost_usd']:.6f}")
```

### Custom Analysis

```python
from src.evaluate_results import ResultsEvaluator

evaluator = ResultsEvaluator()

# Load results
data = evaluator.load_results()

# Custom analysis
performance = evaluator.analyze_performance_metrics(data["test_results"])
photo_types = evaluator.analyze_by_photo_type(data["test_results"])

# Print summary
for model, metrics in performance.items():
    print(f"{model}: {metrics['success_rate']:.1%} success rate")
```

## Utility Scripts

### View Test Results (tools/view_responses.py)
```bash
# View latest test results with formatting
python tools/view_responses.py

# View specific file
python tools/view_responses.py --file data/results/random_test_20240315_143022_photo_abc123.json
```

### Single Photo Testing (tools/test_single_photo.py)
```bash
# Test one random photo quickly
python tools/test_single_photo.py
```

### Test API Connection (tools/test_openrouter.py)
```bash
# Verify OpenRouter API setup
python tools/test_openrouter.py
```

## Configuration Examples

### Environment Setup (.env file)
```bash
# OpenRouter API key
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional: Custom model configurations
DEFAULT_MODEL=gpt-4o
```

### Custom Model Configuration

```python
from src.test_models import VisionModelTester

# Extend supported models
tester = VisionModelTester(api_key)
tester.MODELS["custom-model"] = {
    "name": "provider/model-name",
    "description": "Custom model description",
    "pricing": {"input_per_1k": 0.001, "output_per_1k": 0.002}
}
```

## Workflow Examples

### Complete Research Workflow

```python
# 1. Download photos
from src.download_photos import WikimediaDownloader
downloader = WikimediaDownloader()
downloader.download_from_categories(target_count=50)

# 2. Test all models
from src.test_models import VisionModelTester
tester = VisionModelTester(api_key="your_key")
tester.test_all_models("data/photos", "data/metadata.json")

# 3. Generate reports
from src.evaluate_results import ResultsEvaluator
evaluator = ResultsEvaluator()
evaluator.generate_all_reports()
```

### Budget-Conscious Testing

```python
# Test just a few photos first
tester = VisionModelTester(api_key)

# Test 3 random photos to estimate costs
for i in range(3):
    tester.test_random_photo_all_models("data/photos", "data/metadata.json")

# Check cost analysis before proceeding
evaluator = ResultsEvaluator()
data = evaluator.load_results()
print("Estimated costs per 1000 photos:")
for model, cost_info in data["cost_analysis"].items():
    print(f"{model}: ${cost_info['cost_per_1000_photos']:.2f}")
```

### Quality Control Testing

```python
# Test specific photo types
from src.utils import load_json

metadata = load_json("data/metadata.json")
portraits = [p for p in metadata if p["photo_type"] == "portrait"]

# Test only portrait photos
for photo_meta in portraits[:5]:  # Test first 5 portraits
    image_path = f"data/photos/{photo_meta['local_filename']}"
    for model_key in ["gpt-4o", "claude-3.5-sonnet"]:
        result = tester.test_single_photo(image_path, model_key)
        print(f"{model_key} on {photo_meta['local_filename']}: {result['success']}")
```

## Error Handling Examples

### Robust Testing with Error Handling

```python
import logging
from src.test_models import VisionModelTester

logger = logging.getLogger(__name__)
tester = VisionModelTester(api_key)

try:
    tester.test_random_photo_all_models("data/photos", "data/metadata.json")
except FileNotFoundError:
    logger.error("Photos not found. Run download first.")
except Exception as e:
    logger.error(f"Testing failed: {e}")
```

### Handling Missing Dependencies

```python
try:
    from src.evaluate_results import ResultsEvaluator
    evaluator = ResultsEvaluator()
    evaluator.generate_all_reports()
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
```

## Performance Optimization

### Batch Processing with Delays

```python
import time
from src.test_models import VisionModelTester

tester = VisionModelTester(api_key)

# Process with custom delays to avoid rate limits
for photo_meta in metadata[:10]:
    image_path = f"data/photos/{photo_meta['local_filename']}"

    for model_key in tester.MODELS.keys():
        result = tester.test_single_photo(image_path, model_key)
        print(f"Tested {model_key}: {'✓' if result['success'] else '✗'}")

        # Custom delay between requests
        time.sleep(2)
```

### Memory Management for Large Datasets

```python
from src.test_models import VisionModelTester
from src.utils import load_json

# Process in chunks to manage memory
def process_photos_in_chunks(photos_dir, metadata_file, chunk_size=5):
    metadata = load_json(metadata_file)
    tester = VisionModelTester(api_key)

    for i in range(0, len(metadata), chunk_size):
        chunk = metadata[i:i+chunk_size]
        print(f"Processing chunk {i//chunk_size + 1}")

        for photo_meta in chunk:
            # Process each photo
            pass
```