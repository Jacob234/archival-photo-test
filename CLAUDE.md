# Archival Photo Vision Model Testing Project

## Project Overview

Test vision models on historical/archival photos for community library digitization. Download sample photos from Wikimedia Commons and evaluate multiple vision models for photo description quality.

## Phase 1: Download Test Dataset

### Requirements

* Python 3.8+
* requests, beautifulsoup4, pillow libraries
* Target: 50-100 diverse historical photos from Wikimedia Commons

### Implementation Steps

1. **Setup Environment**
   ```bash
   pip install requests beautifulsoup4 pillow pandas
   mkdir archival_photos_test
   cd archival_photos_test
   ```
2. **Create Wikimedia Scraper**
   * Target categories: "Historical photographs by decade"
   * Diversify across 1900-1980s
   * Include various photo types: portraits, street scenes, events, buildings
   * Filter for good quality images (>500px width)
   * Save metadata (year, description, source URL)
3. **Photo Selection Criteria**
   * Family/portrait photos (20%)
   * Street scenes and buildings (20%)
   * Events and gatherings (20%)
   * Industrial/work scenes (20%)
   * Misc (20%)
   * Mixed quality levels including some damaged/faded (15%)

## Phase 2: Vision Model Testing

### Models to Test

1. **Claude Sonnet 4** (via Anthropic API)
2. **GPT-4o** (via OpenAI API)
3. **GPT-4o mini** (cost comparison)
4. **Gemini 1.5 Flash** (via Google AI)

### Standardized Prompt

```
"Describe this historical photograph in detail for archival cataloging. Include:
- People: number, apparent age, clothing, activities
- Setting: location type, time period indicators, notable objects
- Photo quality: condition, clarity, any damage
- Historical context: estimated decade, cultural/social elements
- Archival value: what makes this photo historically significant"
```

### Testing Process

1. **Batch Processing Script**
   * Load photos sequentially
   * Apply standardized prompt to each model
   * Save results to structured format (CSV/JSON)
   * Include timing and cost tracking
2. **Error Handling**
   * API rate limiting
   * Image format compatibility
   * Network timeouts
   * Invalid responses

## Phase 3: Evaluation Framework

### Automated Metrics

* Response length consistency
* Processing time per photo
* Cost per photo calculation
* Success rate (valid responses)

### Manual Evaluation Criteria

* **Accuracy** : Correct identification of visible elements
* **Detail Level** : Comprehensiveness of description
* **Historical Context** : Recognition of time period indicators
* **Archival Usefulness** : Practical value for cataloging
* **Edge Case Handling** : Performance on damaged/unclear photos

### Evaluation Process

1. Create evaluation spreadsheet with photos and model responses
2. Score each response 1-5 on criteria above
3. Note specific strengths/weaknesses per model
4. Calculate cost-effectiveness ratios

## Phase 4: Implementation Recommendations

### Output Requirements

* Comparative analysis report
* Cost breakdown per 1000 photos
* Recommended model(s) for library use
* Sample workflow for batch processing
* Quality control procedures

### Success Criteria

* Identify best performing model for archival description
* Establish cost-effective processing workflow
* Create reusable framework for library's photo collection
* Document edge cases and limitations

## File Structure

```
archival_photos_test/
├── claude.md (this file)
├── src/
│   ├── download_photos.py
│   ├── test_models.py
│   ├── evaluate_results.py
│   └── utils.py
├── data/
│   ├── photos/ (downloaded images)
│   ├── metadata.json
│   └── results.csv
├── results/
│   ├── model_comparison.csv
│   ├── evaluation_report.md
│   └── cost_analysis.json
└── config/
    └── api_keys.env
```

## Next Steps

1. Set up project structure
2. Implement Wikimedia photo downloader
3. Configure API access for vision models
4. Create batch testing pipeline
5. Develop evaluation framework
6. Generate final recommendations
