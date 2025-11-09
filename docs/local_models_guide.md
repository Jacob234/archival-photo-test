# Local Vision Models Setup Guide

## Overview

This guide explains how to run vision models locally for archival photo analysis, eliminating API costs and maintaining complete data privacy.

## Why Local Models?

**Pros:**
- ✅ **Zero API costs** - Pay only for hardware (one-time)
- ✅ **Complete data privacy** - Photos never leave your infrastructure
- ✅ **No rate limits** - Process unlimited photos
- ✅ **Offline capability** - Works without internet
- ✅ **Customizable** - Fine-tune models for your specific photo types

**Cons:**
- ❌ **Hardware requirements** - Needs GPU with 8GB+ VRAM
- ❌ **Setup complexity** - More technical than API calls
- ❌ **Slower processing** - Usually 2-10x slower than cloud APIs
- ❌ **Model management** - Must download and update models yourself
- ❌ **Quality variance** - May not match GPT-4o/Claude quality

## Recommended Local Vision Models (2025)

### Top Choices for Archival Photos

1. **Qwen2.5-VL-7B** ⭐ Best Overall
   - Excellent document and diagram understanding
   - Strong historical context recognition
   - Sizes: 3B, 7B, 72B parameters
   - VRAM: 8GB (7B model with quantization)
   - Best for: Detailed archival descriptions

2. **Llama-3.2-11B-Vision** ⭐ Good Balance
   - Strong general vision capabilities
   - Good multimodal reasoning
   - VRAM: 12GB (with 4-bit quantization)
   - Best for: Balanced performance/quality

3. **LLaVA-NeXT (LLaVA-1.6)**
   - Excellent instruction following
   - Strong open-source community
   - Multiple sizes: 7B, 13B, 34B
   - VRAM: 8GB+ (depending on size)
   - Best for: Custom fine-tuning

4. **Pixtral-12B**
   - Strong instruction following
   - Good benchmark performance
   - VRAM: 14GB
   - Best for: High-quality descriptions

## Setup Methods

### Method 1: Ollama (Easiest) ⭐ Recommended

Ollama provides the simplest way to run local vision models.

**Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a vision model
ollama pull llama3.2-vision:11b
# or
ollama pull llava:7b
```

**Usage in Python:**
```python
import ollama

response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content': 'Describe this historical photograph for archival cataloging.',
        'images': ['path/to/photo.jpg']
    }]
)

print(response['message']['content'])
```

**Available Ollama Vision Models:**
- `llama3.2-vision:11b` - Llama 3.2 11B Vision
- `llama3.2-vision:90b` - Llama 3.2 90B Vision (requires 64GB+ VRAM)
- `llava:7b` - LLaVA 7B
- `llava:13b` - LLaVA 13B
- `llava:34b` - LLaVA 34B
- `bakllava:7b` - BakLLaVA 7B

### Method 2: Hugging Face Transformers

More control but requires more setup.

**Installation:**
```bash
pip install transformers torch pillow accelerate
```

**Example - Qwen2-VL:**
```python
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import Image
import torch

# Load model
model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

# Prepare input
image = Image.open("photo.jpg")
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Describe this historical photograph for archival cataloging."}
        ]
    }
]

# Process
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=[text], images=[image], return_tensors="pt").to("cuda")

# Generate
output = model.generate(**inputs, max_new_tokens=500)
response = processor.batch_decode(output, skip_special_tokens=True)[0]
print(response)
```

### Method 3: vLLM (Production)

Best for high-throughput batch processing.

**Installation:**
```bash
pip install vllm
```

**Usage:**
```python
from vllm import LLM, SamplingParams
from vllm.multimodal.image import ImageFeaturePlugin

llm = LLM(
    model="llava-hf/llava-1.5-7b-hf",
    gpu_memory_utilization=0.9
)

sampling_params = SamplingParams(temperature=0.3, max_tokens=500)

# Batch process multiple photos
outputs = llm.generate([
    {"prompt": "Describe this photo", "image": "photo1.jpg"},
    {"prompt": "Describe this photo", "image": "photo2.jpg"},
], sampling_params=sampling_params)
```

## Hardware Requirements

### Minimum Requirements
- **GPU:** NVIDIA GPU with 8GB VRAM (RTX 3060, RTX 4060)
- **RAM:** 16GB system RAM
- **Storage:** 50GB for models
- **Models:** 7B parameter models with 4-bit quantization

### Recommended Setup
- **GPU:** NVIDIA RTX 4090 (24GB VRAM) or A100
- **RAM:** 32GB+ system RAM
- **Storage:** 200GB NVMe SSD
- **Models:** 13B-34B parameter models with 8-bit quantization

### Budget Setup
- **Option 1:** Use cloud GPU (RunPod, Vast.ai) - ~$0.30/hour
- **Option 2:** Rent GPU instance only for batch processing
- **Option 3:** Use quantized models (4-bit) on 8GB consumer GPU

## Integration with This Project

### Step 1: Create Local Model Client

Create `src/local_model_client.py`:

```python
import ollama
from typing import Dict, Any
import base64
from pathlib import Path

class LocalVisionModel:
    def __init__(self, model_name: str = "llama3.2-vision"):
        self.model_name = model_name

    def analyze_photo(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze a photo using local Ollama model."""
        response = ollama.chat(
            model=self.model_name,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )

        return {
            "success": True,
            "response": response['message']['content'],
            "model": self.model_name,
            # Note: Ollama doesn't provide token counts by default
        }
```

### Step 2: Add to test_models.py

Add local models to the MODELS dict:

```python
"llama3.2-vision": {
    "name": "local/llama3.2-vision:11b",
    "description": "Llama 3.2 Vision 11B - Local via Ollama",
    "pricing": {"input_per_1k": 0, "output_per_1k": 0},  # No API cost
    "provider": "ollama"
},
"llava-7b": {
    "name": "local/llava:7b",
    "description": "LLaVA 7B - Local via Ollama",
    "pricing": {"input_per_1k": 0, "output_per_1k": 0},
    "provider": "ollama"
}
```

### Step 3: Modify test_single_photo method

Add provider detection:

```python
def test_single_photo(self, image_path: str, model_key: str) -> Dict[str, Any]:
    model_config = self.MODELS[model_key]

    # Check if local model
    if model_config.get("provider") == "ollama":
        return self._test_local_model(image_path, model_config)
    else:
        return self._test_openrouter_model(image_path, model_config)
```

## Performance Comparison

Based on typical 7B-13B models on consumer hardware:

| Model | Hardware | Speed | Quality | VRAM | Cost/1000 |
|-------|----------|-------|---------|------|-----------|
| Llama 3.2-11B | RTX 4090 | ~15s | ⭐⭐⭐⭐ | 14GB | $0 |
| LLaVA-13B | RTX 4090 | ~12s | ⭐⭐⭐⭐ | 16GB | $0 |
| Qwen2-VL-7B | RTX 4090 | ~10s | ⭐⭐⭐⭐⭐ | 12GB | $0 |
| GPT-4o (API) | Cloud | ~3s | ⭐⭐⭐⭐⭐ | N/A | $12 |
| Claude Sonnet | Cloud | ~4s | ⭐⭐⭐⭐⭐ | N/A | $10 |

## Cost Analysis: Local vs Cloud

For processing **10,000 archival photos**:

### Cloud APIs
- GPT-4o: ~$120
- Claude Sonnet: ~$100
- Gemini Flash: ~$1

### Local Setup
- Initial: RTX 4090 (~$1,600) or rent at $0.30/hr
- Processing time: ~42 hours (15s/photo)
- Rental cost: ~$13 for one-time batch
- **Break-even point: ~13,000 photos**

## Fine-Tuning for Your Collection

Local models can be fine-tuned on your specific photo types:

```bash
# Example using Unsloth for efficient fine-tuning
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Fine-tune LLaVA on your labeled photos
python scripts/finetune_vision_model.py \
  --model llava-1.5-7b \
  --dataset your_labeled_photos/ \
  --output models/llava-archival-finetuned
```

## Troubleshooting

### "CUDA out of memory"
- Reduce batch size
- Use 4-bit quantization
- Try smaller model (7B instead of 13B)
- Close other GPU applications

### "Model too slow"
- Use vLLM instead of transformers
- Enable flash attention
- Batch process multiple photos
- Consider cloud GPU rental

### "Poor quality results"
- Try larger model (13B or 34B)
- Adjust temperature (try 0.1-0.5)
- Refine your prompt
- Consider fine-tuning

## Recommended Workflow

1. **Start with cloud APIs** - Test GPT-4o, Claude, Gemini on 50-100 photos
2. **Benchmark local models** - Compare Llama 3.2, LLaVA quality
3. **Calculate break-even** - Based on your collection size
4. **Hybrid approach** - Use local for bulk, cloud for edge cases
5. **Fine-tune** - Once you have labeled data from cloud APIs

## Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Qwen2-VL GitHub](https://github.com/QwenLM/Qwen2-VL)
- [LLaVA Project](https://llava-vl.github.io/)
- [Unsloth Fine-tuning](https://github.com/unslothai/unsloth)
- [vLLM Documentation](https://docs.vllm.ai/)

## Next Steps

To add local model support to this project:

1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Pull a model: `ollama pull llama3.2-vision:11b`
3. Test it: `ollama run llama3.2-vision "Describe this image" path/to/photo.jpg`
4. Integrate with project using the examples above
5. Compare results with cloud APIs
