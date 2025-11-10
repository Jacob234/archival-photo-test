# Vision Model Comparison Guide

## Overview

This project now tests **15 vision models** across 5 pricing tiers, from **completely free** to premium. Many models can also run locally for zero ongoing costs.

## Model Tiers & Pricing

### 🆓 FREE TIER - $0 per 1,000 photos

Perfect for unlimited testing without any API costs!

| Model | ID | Local? | Context | Best For |
|-------|----|----|---------|----------|
| **Gemini 2.0 Flash Free** | `google/gemini-2.0-flash-exp:free` | ❌ | 1M | General vision, Google quality |
| **Qwen2.5-VL 32B Free** | `qwen/qwen2.5-vl-32b-instruct:free` | ✅ | 16K | Documents, diagrams |
| **Llama 4 Scout Free** | `meta-llama/llama-4-scout:free` | ✅ | 328K | Meta's latest vision |

**💡 Recommendation:** Start here! Test quality before paying anything.

---

### 💰 ULTRA-BUDGET TIER - $0.05-$0.10 per 1,000 photos

Better than free tier, still incredibly cheap.

| Model | Cost per 1K photos | Local? | Context | Best For |
|-------|-------------------|--------|---------|----------|
| **Llama 3.2 11B Vision** | **$0.049** | ✅ | 131K | Best price/quality ratio |
| **Qwen2.5-VL 32B** | $0.27 | ✅ | 16K | Document understanding |
| **Gemini 2.0 Flash Lite** | $0.38 | ❌ | 1M | Google efficiency |
| **Qwen2.5-VL 72B** | $0.41 | ✅ | 32K | Higher quality Qwen |
| **Pixtral 12B** | $0.10 | ✅ | 32K | Mistral vision model |

**💡 Recommendation:** Llama 3.2 11B Vision offers exceptional value at < 5¢ per 1000 photos!

---

### 💵 BUDGET TIER - $0.10-$1.00 per 1,000 photos

Production-ready quality at low cost.

| Model | Cost per 1K photos | Local? | Context | Best For |
|-------|-------------------|--------|---------|----------|
| **Gemini 2.0 Flash** | $0.50 | ❌ | 1M | Latest Google model |
| **GPT-4o Mini** | $0.75 | ❌ | 128K | OpenAI quality |
| **Claude 3.5 Haiku** | $4.80 | ❌ | 200K | Anthropic speed |

---

### 💎 MID TIER - $1-$5 per 1,000 photos

High-quality descriptions for important collections.

| Model | Cost per 1K photos | Local? | Context | Best For |
|-------|-------------------|--------|---------|----------|
| **Claude 3.5 Sonnet** | $18 | ❌ | 200K | Excellent descriptions |

---

### 🏆 PREMIUM TIER - $5+ per 1,000 photos

Top-tier quality for critical archival work.

| Model | Cost per 1K photos | Local? | Context | Best For |
|-------|-------------------|--------|---------|----------|
| **GPT-4o** | $13 | ❌ | 128K | OpenAI flagship |
| **Claude 3 Opus** | $90 | ❌ | 200K | Maximum quality |

---

## Local Model Capabilities

Models marked ✅ can be downloaded and run locally using:

### Option 1: Ollama (Easiest)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models (examples)
ollama pull llama3.2-vision:11b
ollama pull qwen2-vl:7b

# Run
ollama run llama3.2-vision "Describe this archival photo" photo.jpg
```

### Option 2: Hugging Face

```bash
pip install transformers torch accelerate

# Download and run Qwen2.5-VL
# See docs/local_models_guide.md for full examples
```

**Local-Capable Models in This Project:**
- ✅ Qwen2.5-VL 32B Free
- ✅ Llama 4 Scout Free
- ✅ Llama 3.2 11B Vision ($0.049 or local)
- ✅ Qwen2.5-VL 32B ($0.27 or local)
- ✅ Qwen2.5-VL 72B ($0.41 or local)
- ✅ Pixtral 12B ($0.10 or local)

---

## Cost Comparison for 10,000 Photos

| Tier | Example Model | API Cost | Local Cost | Break-even |
|------|---------------|----------|------------|------------|
| Free | Gemini 2.0 Free | **$0** | $0 | N/A |
| Ultra-Budget | Llama 3.2 11B | **$0.49** | $1,600 GPU | 3.3M photos |
| Budget | GPT-4o Mini | $7.50 | - | - |
| Mid | Claude Sonnet | $180 | - | - |
| Premium | GPT-4o | $130 | - | - |
| Premium | Claude Opus | $900 | - | - |

**Key Insight:** For most library projects, **free or ultra-budget tiers are sufficient**!

---

## Quality Comparison (Estimated)

Based on benchmarks and community feedback:

| Model | Quality Score | Speed | Local? |
|-------|--------------|-------|--------|
| Claude 3 Opus | ⭐⭐⭐⭐⭐ 95% | 🐌 Slow | ❌ |
| GPT-4o | ⭐⭐⭐⭐⭐ 94% | 🚀 Fast | ❌ |
| Claude 3.5 Sonnet | ⭐⭐⭐⭐⭐ 93% | 🐌 Slow | ❌ |
| Qwen2.5-VL 72B | ⭐⭐⭐⭐ 88% | ⚡ Med | ✅ |
| Llama 3.2 11B Vision | ⭐⭐⭐⭐ 85% | ⚡ Med | ✅ |
| Gemini 2.0 Flash | ⭐⭐⭐⭐ 85% | 🚀 Fast | ❌ |
| GPT-4o Mini | ⭐⭐⭐⭐ 82% | 🚀 Fast | ❌ |
| Qwen2.5-VL 32B | ⭐⭐⭐ 78% | ⚡ Med | ✅ |
| Pixtral 12B | ⭐⭐⭐ 75% | ⚡ Med | ✅ |
| Claude 3.5 Haiku | ⭐⭐⭐ 75% | 🚀 Fast | ❌ |

---

## Recommended Testing Strategy

### Phase 1: Free Tier Baseline (Cost: $0)

Test all 3 free models to establish baseline quality:

```bash
python tools/test_single_photo.py
# Tests: gemini-2.0-flash-free, qwen2.5-vl-32b-free, llama-4-scout-free
```

**Goal:** Determine if free tier meets your needs (it might!)

### Phase 2: Ultra-Budget Comparison (Cost: ~$0.50 for 1,000 photos)

Compare the best value models:

```bash
# Focus on these models:
# - llama-3.2-11b-vision ($0.049/1K)
# - qwen2.5-vl-32b ($0.27/1K)
# - pixtral-12b ($0.10/1K)
```

**Goal:** Find the sweet spot between cost and quality.

### Phase 3: Premium Spot Check (Cost: ~$5-10 for 50 photos)

Test premium models on a small sample:

```bash
# Test 50 photos with:
# - claude-3.5-sonnet
# - gpt-4o
```

**Goal:** Understand quality ceiling vs budget options.

### Phase 4: Production Decision

Choose based on your collection size and budget:

- **< 10K photos:** Use free tier or ultra-budget
- **10K-100K photos:** Ultra-budget tier (Llama 3.2 11B)
- **100K+ photos:** Consider local deployment
- **Critical collections:** Premium tier for subset, budget for bulk

---

## Special Use Cases

### 📄 **Best for Documents/Diagrams**
1. Qwen2.5-VL 72B ($0.41/1K) ⭐ Best
2. Qwen2.5-VL 32B ($0.27/1K or FREE)
3. Gemini 2.0 Flash ($0.50/1K)

### 🖼️ **Best for Historical Photos**
1. Claude 3.5 Sonnet ($18/1K) - Rich historical context
2. GPT-4o ($13/1K) - Detailed descriptions
3. Llama 3.2 11B ($0.049/1K) - Budget option

### 💰 **Best Value Overall**
1. **Llama 3.2 11B Vision** - $0.049/1K, can run locally
2. Gemini 2.0 Flash Free - $0, good quality
3. Pixtral 12B - $0.10/1K, local-capable

### 🏃 **Fastest Processing**
1. Gemini 2.0 Flash (Free or $0.50)
2. GPT-4o Mini ($0.75/1K)
3. Claude 3.5 Haiku ($4.80/1K)

### 🏠 **Best for Local Deployment**
1. **Qwen2.5-VL 72B** - Best quality local model
2. Llama 3.2 11B Vision - Most efficient
3. Pixtral 12B - Good balance

---

## Sample Test Results

Once you have photos, you can expect results like:

```bash
$ python tools/test_single_photo.py

Testing: photo_1920s_street.jpg
================================

FREE TIER:
✓ gemini-2.0-flash-free    - 3.2s  - $0.00000
✓ qwen2.5-vl-32b-free      - 4.1s  - $0.00000
✓ llama-4-scout-free       - 3.8s  - $0.00000

ULTRA-BUDGET:
✓ llama-3.2-11b-vision     - 4.5s  - $0.00005
✓ qwen2.5-vl-32b          - 5.2s  - $0.00027
✓ pixtral-12b             - 4.8s  - $0.00010

BUDGET:
✓ gemini-2.0-flash         - 2.9s  - $0.00050
✓ gpt-4o-mini             - 3.1s  - $0.00075

MID:
✓ claude-3.5-sonnet       - 5.4s  - $0.01800

PREMIUM:
✓ gpt-4o                  - 3.5s  - $0.01300
✓ claude-3-opus           - 6.2s  - $0.09000

Total cost: $0.12162 for 12 models
```

---

## Migration Path: Cloud → Local

If you process enough photos, local deployment becomes cost-effective:

**Scenario: 100,000 archival photos**

| Approach | Cost | Setup Time | Processing Time |
|----------|------|------------|-----------------|
| Gemini Free | $0 | 5 min | ~83 hrs |
| Llama 3.2 11B (API) | $4.90 | 5 min | ~125 hrs |
| Llama 3.2 11B (local) | $1,600* | 2 hrs | ~167 hrs |
| Claude Sonnet (API) | $1,800 | 5 min | ~150 hrs |

*One-time GPU cost (RTX 4090) or ~$50 cloud GPU rental

**Break-even point for local:** ~13,000 photos vs Claude, ~327,000 vs Llama API

---

## Quick Start Commands

### Test All Models (with photos):
```bash
python tools/test_single_photo.py
```

### Test Only Free Models:
```bash
# Edit src/test_models.py to comment out paid models
python tools/test_single_photo.py
```

### Test Only Local-Capable Models:
```bash
# Filter for models where local_capable=True
# Models: qwen2.5-vl-*, llama-*, pixtral-12b
```

### Run Full Evaluation (all 15 models):
```bash
python run_full_test.py
# Warning: Will cost ~$0.12 per photo with all models
```

---

## Model Selection Decision Tree

```
Start
  │
  ├─ Need to test first?
  │   └─ YES → Use FREE tier (3 models, $0)
  │
  ├─ Budget < $1 per 1,000 photos?
  │   └─ YES → Llama 3.2 11B ($0.049)
  │
  ├─ Processing > 100K photos?
  │   └─ YES → Deploy locally (Qwen2.5-VL 72B)
  │
  ├─ Need best quality?
  │   └─ YES → Claude 3.5 Sonnet or GPT-4o
  │
  └─ Default → Gemini 2.0 Flash ($0.50)
```

---

## Summary

**🎯 Best Overall Value:** Llama 3.2 11B Vision - $0.049/1K photos, great quality

**🆓 Best Free Option:** Gemini 2.0 Flash Free - No cost, good quality

**🏠 Best Local Model:** Qwen2.5-VL 72B - Excellent quality, runs on consumer GPU

**🏆 Best Quality:** Claude 3 Opus - Maximum accuracy for critical work

**⚡ Best Speed:** Gemini 2.0 Flash - Fastest processing

---

**Updated:** 2025-11-10
**Total Models:** 15 (3 free, 5 ultra-budget, 3 budget, 1 mid, 2 premium)
**Price Range:** $0 - $90 per 1,000 photos
**Local-Capable:** 6 models
