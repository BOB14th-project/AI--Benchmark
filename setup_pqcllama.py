"""
Setup script to download and test PQCllama model from HuggingFace
PQCllama is a LoRA adapter on top of Llama 3.1 8B Instruct
"""
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

print("="*80)
print("PQCllama Model Setup (LoRA Adapter)")
print("="*80)

adapter_name = "sangwoohahn/PQCllama"
cache_dir = "./models/pqcllama"

print(f"\n📦 Downloading PQCllama adapter: {adapter_name}")
print(f"📁 Cache directory: {cache_dir}")

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"\n🖥️  Device: {device}")
if device == "cuda":
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
elif device == "mps":
    print(f"   Apple Silicon GPU (Metal)")

try:
    # Load PEFT config to get base model
    print("\n⏳ Loading PEFT config...")
    peft_config = PeftConfig.from_pretrained(adapter_name, cache_dir=cache_dir)
    base_model_name = peft_config.base_model_name_or_path

    print(f"✅ Base model: {base_model_name}")
    print(f"   LoRA rank: {peft_config.r}")
    print(f"   LoRA alpha: {peft_config.lora_alpha}")

    print(f"\n⏳ Loading tokenizer from base model...")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_name,
        cache_dir=cache_dir,
        trust_remote_code=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("✅ Tokenizer loaded successfully")

    print(f"\n⏳ Loading base model: {base_model_name}")
    print("   (This may take a while, downloading ~16GB...)")

    # Load base model with appropriate settings
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        cache_dir=cache_dir,
        trust_remote_code=True,
        dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map="auto" if device != "cpu" else None,
        low_cpu_mem_usage=True
    )
    print("✅ Base model loaded successfully")

    print(f"\n⏳ Loading LoRA adapter: {adapter_name}")
    model = PeftModel.from_pretrained(
        base_model,
        adapter_name,
        cache_dir=cache_dir
    )
    print("✅ LoRA adapter loaded successfully")

    # Merge adapter for faster inference (optional)
    print("\n⏳ Merging LoRA adapter with base model...")
    model = model.merge_and_unload()
    print("✅ Adapter merged successfully")

    # Move to device
    if device != "auto":
        model = model.to(device)

    # Test inference
    print("\n🧪 Testing inference...")
    test_prompt = """Analyze the following code for quantum-vulnerable cryptography:

```python
from Crypto.PublicKey import RSA
key = RSA.generate(2048)
```

Is this code vulnerable to quantum attacks? Respond in JSON format with detected_algorithms."""

    inputs = tokenizer(test_prompt, return_tensors="pt", truncation=True, max_length=512)
    if device == "cuda" or device == "mps":
        inputs = {k: v.to(device) for k, v in inputs.items()}

    print("⏳ Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n" + "="*80)
    print("Test Response:")
    print("="*80)
    # Only show the response part (not the prompt)
    if test_prompt in response:
        response = response[len(test_prompt):].strip()
    print(response[:500] + "..." if len(response) > 500 else response)
    print("="*80)

    print("\n✅ Setup complete! PQCllama is ready for benchmarking.")
    print(f"\n📊 Model info:")
    print(f"   Base model: {base_model_name}")
    print(f"   Adapter: {adapter_name}")
    print(f"   Parameters: ~8B (base) + LoRA adapter")
    print(f"   Device: {device}")
    print(f"   Cache: {cache_dir}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Install required packages:")
    print("   pip install peft accelerate bitsandbytes")
    print("2. Check internet connection")
    print("3. You may need HuggingFace access token for Llama models:")
    print("   huggingface-cli login")
    print("   or get token from: https://huggingface.co/settings/tokens")
    print("4. Check disk space for model download (~16GB)")
    raise
