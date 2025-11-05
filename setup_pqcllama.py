"""
Setup script to download and test PQCllama model from HuggingFace
"""
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("="*80)
print("PQCllama Model Setup")
print("="*80)

model_name = "sangwoohahn/PQCllama"
cache_dir = "./models/pqcllama"

print(f"\n📦 Downloading model: {model_name}")
print(f"📁 Cache directory: {cache_dir}")

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🖥️  Device: {device}")
if device == "cuda":
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

try:
    print("\n⏳ Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        trust_remote_code=True
    )
    print("✅ Tokenizer loaded successfully")

    print("\n⏳ Loading model (this may take a while)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        trust_remote_code=True,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        low_cpu_mem_usage=True
    )
    print("✅ Model loaded successfully")

    # Test inference
    print("\n🧪 Testing inference...")
    test_prompt = """Analyze the following code for quantum-vulnerable cryptography:

```python
from Crypto.PublicKey import RSA
key = RSA.generate(2048)
```

Is this code vulnerable to quantum attacks?"""

    inputs = tokenizer(test_prompt, return_tensors="pt")
    if device == "cuda":
        inputs = {k: v.to(device) for k, v in inputs.items()}

    print("⏳ Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n" + "="*80)
    print("Test Response:")
    print("="*80)
    print(response)
    print("="*80)

    print("\n✅ Setup complete! Model is ready for benchmarking.")
    print(f"\n📊 Model info:")
    print(f"   Parameters: {model.num_parameters() / 1e9:.2f}B")
    print(f"   Device: {device}")
    print(f"   Cache: {cache_dir}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify HuggingFace model name: sangwoohahn/PQCllama")
    print("3. Check disk space for model download (~8-16GB)")
    print("4. Try: pip install --upgrade transformers torch")
    raise
