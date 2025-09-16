# Archival Photo Vision Model Testing

A comprehensive testing framework for evaluating vision AI models on historical and archival photographs, designed to help community libraries choose the best model for digitization cataloging.

## Overview

This project tests 4 vision models on 50 historical photos from Wikimedia Commons (1920s-1980s) to evaluate their effectiveness for archival cataloging. The models tested are:

- **GPT-4o** (OpenAI) - Latest vision model
- **GPT-4o Mini** (OpenAI) - Cost-optimized version
- **Claude 3.5 Sonnet** (Anthropic) - Latest Claude vision
- **Gemini 1.5 Flash** (Google) - Fast processing model

## Features

- 🖼️ **Automated Photo Collection**: Downloads diverse historical photos from Wikimedia Commons
- 🔍 **Blind Multi-Model Testing**: Tests all models without metadata context for unbiased evaluation
- 💰 **Real-time Cost Analysis**: Tracks API costs and projects expenses for larger collections
- 📊 **Comprehensive Evaluation**: Generates detailed reports and statistical comparisons
- 📈 **Manual Scoring Tools**: Excel templates for human evaluation and quality assessment
- 🛠️ **Utility Tools**: Quick testing, pretty response viewing, and API verification tools
- 📚 **Complete Documentation**: Function docs, examples, and usage workflows

## Quick Start

### 1. Setup

```bash
# Clone or download the project
cd archival-photo-test

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and add your OpenRouter API key:

```bash
cp config/.env.example config/.env
# Edit config/.env and add your OPENROUTER_API_KEY
```

Get your OpenRouter API key at: https://openrouter.ai/

### 3. Run Complete Pipeline

```bash
python run_full_test.py
```

This will:
1. Download 50 historical photos from Wikimedia Commons
2. Test all 4 vision models on each photo
3. Generate comprehensive evaluation reports

### 4. Quick Testing (Recommended First)

Before running the full pipeline, test a single random photo to verify setup:

```bash
# Download some photos first
python src/download_photos.py

# Test one random photo with all models
python tools/test_single_photo.py

# View the results in a pretty format
python tools/view_responses.py
```

### 5. Individual Phases

Run individual phases if needed:

```bash
# Download photos only
python src/download_photos.py

# Test models only (requires photos)
python src/test_models.py

# Generate reports only (requires test results)
python src/evaluate_results.py
```

## Project Structure

```
archival-photo-test/
├── README.md                    # This file
├── CLAUDE.md                    # Detailed project specification
├── requirements.txt             # Python dependencies
├── run_full_test.py            # Main pipeline script
├── config/
│   ├── .env.example            # API key template
│   └── .env                    # Your API keys (not in git)
├── src/
│   ├── download_photos.py      # Wikimedia photo downloader
│   ├── test_models.py          # Vision model testing
│   ├── evaluate_results.py     # Analysis and reporting
│   └── utils.py                # Utility functions
├── tools/
│   ├── test_single_photo.py    # Quick single photo testing
│   ├── view_responses.py       # Pretty response viewer
│   └── test_openrouter.py      # API connection test
├── docs/
│   ├── functions.md            # Detailed function documentation
│   └── examples.md             # Usage examples and workflows
├── data/
│   ├── photos/                 # Downloaded images
│   ├── metadata.json           # Photo metadata
│   └── results/                # Model test results
└── reports/
    ├── evaluation_report.md     # Main findings report
    ├── manual_evaluation_template.xlsx  # For human scoring
    ├── detailed_analysis.json   # Raw analysis data
    └── cost_analysis.json       # Cost projections
```

## Output Files

### Key Reports

- **`reports/evaluation_report.md`** - Main findings and recommendations
- **`reports/manual_evaluation_template.xlsx`** - Spreadsheet for detailed human evaluation
- **`data/results/cost_analysis.json`** - Cost breakdown and projections

### Data Files

- **`data/metadata.json`** - Metadata for all downloaded photos
- **`data/results/model_test_results.json`** - Raw model responses
- **`data/results/model_comparison.csv`** - Results in spreadsheet format

## Evaluation Criteria

Each model is evaluated on:

1. **Accuracy** - Correct identification of visible elements
2. **Detail Level** - Comprehensiveness of description
3. **Historical Context** - Recognition of time period indicators
4. **Archival Usefulness** - Practical value for cataloging
5. **Cost Effectiveness** - Performance vs. API costs

## Usage Workflows

### For Researchers and Librarians

1. **Quick Evaluation**: Test setup and model performance
   ```bash
   python src/download_photos.py  # Get some photos
   python tools/test_single_photo.py  # Test one photo
   python tools/view_responses.py  # Review results
   ```

2. **Budget Planning**: Estimate costs before large-scale testing
   ```bash
   # Test 3-5 photos to get cost estimates
   python tools/test_single_photo.py  # Run multiple times
   # Check cost analysis in generated reports
   ```

3. **Full Analysis**: Complete research workflow
   ```bash
   python run_full_test.py  # Full pipeline
   # Review reports/ directory for findings
   ```

### For Developers

1. **API Testing**: Verify OpenRouter connection
   ```bash
   python tools/test_openrouter.py
   ```

2. **Custom Models**: Add new vision models to test
   - Edit `MODELS` dictionary in `src/test_models.py`
   - Add pricing information for cost analysis

3. **Custom Analysis**: Extend evaluation metrics
   - Modify analysis functions in `src/evaluate_results.py`
   - Add new report sections

## Customization

### Modify Photo Selection

Edit `CATEGORIES` in `src/download_photos.py` to target different photo types:

```python
CATEGORIES = [
    "Category:1920s photographs of the United States",
    "Category:Portrait photographs",
    # Add your categories here
]
```

### Adjust Photo Count

```bash
python run_full_test.py --photos 100  # Download 100 photos instead of 50
```

### Change Evaluation Prompt

Edit `ARCHIVAL_PROMPT` in `src/test_models.py` to customize how models are prompted.

### Blind Testing Methodology

This project implements "blind" testing where models receive only the image without any contextual metadata (title, date, description). This ensures unbiased evaluation of pure visual analysis capabilities.

## API Costs

Approximate costs per photo (as of 2024):

- **GPT-4o Mini**: ~$0.0002
- **Gemini 1.5 Flash**: ~$0.003
- **Claude 3.5 Sonnet**: ~$0.018
- **GPT-4o**: ~$0.020

For 1000 photos, expect costs of $0.20 - $20 depending on model choice.

## Requirements

- Python 3.8+
- OpenRouter API key
- ~500MB disk space for 50 photos
- Internet connection for Wikimedia Commons

## Utility Tools

### tools/test_single_photo.py
Quickly test one random photo with all models. Perfect for:
- Verifying API setup
- Getting cost estimates
- Quick quality checks

### tools/view_responses.py
Pretty-print model responses with color formatting. Features:
- Automatically finds latest test results
- Color-coded model responses
- Performance metrics display
- Markdown report generation

### tools/test_openrouter.py
Test OpenRouter API connection and model access.

## Documentation

- **docs/functions.md**: Detailed documentation for all functions
- **docs/examples.md**: Usage examples and code snippets
- **CLAUDE.md**: Complete project specification and research methodology

## Troubleshooting

### Common Issues

**"No module named 'src'"**
```bash
# Make sure you're in the project root directory
cd archival-photo-test
python run_full_test.py
```

**"OPENROUTER_API_KEY not found"**
```bash
# Check your .env file
cat config/.env
# Should contain: OPENROUTER_API_KEY=your_key_here
```

**OpenAI/httpx compatibility errors**
- Project includes compatibility fixes for OpenRouter
- Uses pinned versions: openai==1.55.3, httpx==0.27.2
- Custom wrapper removes unsupported 'proxies' argument

**Rate limiting errors**
- The project includes built-in rate limiting (1 second between requests)
- If you get rate limit errors, the script will retry automatically

**Download failures**
- Some photos may fail due to network issues or file problems
- The script will continue and download alternative photos

**Results not overwriting**
- Test results use unique timestamps to preserve history
- Format: `random_test_YYYYMMDD_HHMMSS_photo_id.json`
- Use `tools/view_responses.py` to see latest results

## Contributing

This is a research/evaluation project. To contribute:

1. Test with different photo categories
2. Add new evaluation metrics
3. Improve the reporting format
4. Test with additional vision models

## License

This project is for educational and research purposes. Photos downloaded from Wikimedia Commons retain their original licenses (mostly public domain or Creative Commons).

## Key Features

### Blind Testing Methodology
- Models receive only images without metadata context
- Ensures unbiased evaluation of visual analysis capabilities
- Prevents models from relying on textual hints

### Cost Tracking
- Tracks API usage and costs in real-time
- Projects expenses for larger datasets
- Helps budget planning for institutional use

### Comprehensive Reporting
- Markdown reports for stakeholders
- Excel templates for manual evaluation
- Statistical analysis across multiple dimensions
- Performance comparisons and recommendations

### Quality Assurance
- Built-in error handling and retry logic
- Progress tracking with intermediate backups
- Unique filename generation preserves test history
- Extensive logging for debugging

## Support

For questions or issues:
1. Check the detailed error messages and logs
2. Review `docs/functions.md` for function documentation
3. See `docs/examples.md` for usage patterns
4. Examine `CLAUDE.md` for research methodology

This is a self-contained testing framework designed to be understandable and modifiable for research purposes.