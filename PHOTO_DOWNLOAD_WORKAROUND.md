# Photo Download Workaround

## Issue
This environment has strict network restrictions that block downloads from:
- Wikimedia Commons (403 Forbidden)
- Library of Congress API (403 Forbidden)
- Unsplash, Pexels, and other image services (403 Forbidden)
- Lorem Picsum and other placeholder services (blocked)

## Solution: Synthetic Test Images

Since real historical photos cannot be downloaded in this environment, we've created **synthetic test images** using Python's PIL library.

### What We Have

✅ **15 synthetic test images** in `data/photos/`:
- 3 landscape scenes (trees, buildings, sky)
- 3 portrait images (simple faces)
- 3 building/architecture images
- 3 street scenes (urban settings)
- 3 group scenes (multiple people)

### Metadata
- All images: 800x600 pixels, JPEG format
- Metadata saved in: `data/metadata_synthetic.json`
- Total size: ~359 KB

### How to Use

**Test Vision Models Immediately:**
```bash
# The test_models.py script will work with these synthetic images
python src/test_models.py

# Or test specific models
python src/test_models.py --model gemini-2.0-flash-free
```

### Benefits of This Approach

✅ **Works without network access** - No download failures
✅ **Consistent testing** - Same images for all model comparisons
✅ **Verifies entire pipeline** - Tests API connections, image processing, output formatting
✅ **Model comparison** - See how each model describes simple vs complex scenes
✅ **Fast iteration** - No waiting for downloads or dealing with rate limits

### Using Real Photos Later

When you have access to real historical photos:

1. **Option 1: Manual Download**
   ```bash
   # Download photos to data/photos/ manually
   # Run the test script - it will process all images in that directory
   python src/test_models.py
   ```

2. **Option 2: Use Download Scripts from Different Network**
   ```bash
   # From a network without restrictions:
   python src/download_photos.py          # Wikimedia Commons
   python src/download_loc_photos.py      # Library of Congress
   python src/download_test_photos.py     # Multiple sources
   ```

3. **Option 3: Use Your Own Photos**
   ```bash
   # Copy your historical photo collection to data/photos/
   cp /path/to/your/photos/*.jpg data/photos/

   # Run tests
   python src/test_models.py
   ```

### What the Synthetic Images Test

Even though these are not real historical photos, they allow you to:

1. **Verify API Credentials** - Confirm all 15 models are accessible
2. **Compare Response Styles** - See verbose vs concise descriptions
3. **Evaluate Detail Levels** - Which models notice small elements
4. **Test Edge Cases** - How models handle simple shapes vs complex scenes
5. **Benchmark Speed** - Processing time per image for each model
6. **Calculate Costs** - Actual token usage and pricing

### Next Steps

1. **Run Initial Tests:**
   ```bash
   python src/test_models.py
   ```

2. **Review Model Outputs:**
   ```bash
   # Results will be in results/ directory
   cat results/model_comparison.csv
   ```

3. **Compare Models:**
   - Check which models provide most detail for simple images
   - Evaluate response quality vs. cost
   - Identify best performers for your use case

4. **When Ready for Real Photos:**
   - Replace synthetic images in `data/photos/`
   - Run tests again with same methodology
   - Compare results with historical photo complexity

### Scripts Available

- `src/generate_test_images.py` - Creates synthetic test images (already run)
- `src/test_models.py` - Tests all 15 vision models on available images
- `src/evaluate_results.py` - Analyzes and compares model outputs
- `src/download_photos.py` - Downloads from Wikimedia (blocked in this env)
- `src/download_loc_photos.py` - Downloads from LOC (blocked in this env)
- `src/download_test_photos.py` - Multi-source download (blocked in this env)

### Important Notes

⚠️ **Network Restrictions**: All external image downloads are blocked in this environment due to IP-based filtering

✅ **Workaround Success**: Synthetic images allow complete testing of the vision model pipeline

🔄 **Drop-in Replacement**: When real photos are available, simply replace files in `data/photos/` - no code changes needed

💰 **Cost Savings**: Test with FREE models first (Gemini 2.0, Qwen 2.5-VL, Llama 4) before using paid APIs
