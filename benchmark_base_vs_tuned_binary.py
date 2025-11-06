"""
Base Llama 3.1 vs PQC-tuned Llama Benchmark
Binary/Assembly files only
"""
import json
import time
import os
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch
from tqdm import tqdm
import glob

# Configuration
BASE_MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"
PQCLLAMA_ADAPTER = "sangwoohahn/PQCllama"
CACHE_DIR = "./models/pqcllama"
RESULTS_DIR = "./results"

# Test configuration
TEST_LIMIT = 1  # Set to number for testing, None for all
BINARY_FILES_DIR = "data/test_files/assembly_binary"

class LlamaModelWrapper:
    """Wrapper for Llama models (base or tuned)"""

    def __init__(self, model_name, is_pqc_tuned=False, cache_dir="./models"):
        self.model_name = model_name
        self.is_pqc_tuned = is_pqc_tuned
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

        print(f"\n{'='*80}")
        print(f"Loading {'PQC-tuned' if is_pqc_tuned else 'Base'} Llama Model")
        print(f"{'='*80}")
        print(f"Device: {self.device}")

        # Load tokenizer
        print(f"⏳ Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("✅ Tokenizer loaded")

        # Load base model
        print(f"⏳ Loading base model: {model_name}")
        print("   (This may take a while...)")

        # For MPS/Apple Silicon, don't use device_map="auto" (causes issues with PEFT)
        # Load everything on MPS directly
        if self.device == "mps":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            self.model = self.model.to("mps")
        elif self.device == "cuda":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
        else:  # CPU
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
        print("✅ Base model loaded")

        # Load PQC adapter if needed
        if is_pqc_tuned:
            print(f"⏳ Loading PQC adapter: {PQCLLAMA_ADAPTER}")

            # For CUDA with device_map, we can't merge easily
            # For MPS/CPU, we can merge
            if self.device == "cuda":
                # Don't merge on CUDA with device_map
                self.model = PeftModel.from_pretrained(
                    self.model,
                    PQCLLAMA_ADAPTER,
                    cache_dir=cache_dir
                )
                print("✅ PQC adapter loaded (not merged on CUDA)")
            else:
                # Merge on MPS/CPU
                self.model = PeftModel.from_pretrained(
                    self.model,
                    PQCLLAMA_ADAPTER,
                    cache_dir=cache_dir
                )
                print("✅ PQC adapter loaded")

                print("⏳ Merging adapter...")
                self.model = self.model.merge_and_unload()
                print("✅ Adapter merged")

        # Don't call .to() when using device_map="auto"!
        # The model is already placed on the correct device by accelerate

        self.model.eval()
        print(f"✅ Model ready for inference")

    def generate(self, prompt, max_tokens=2000):
        """Generate response"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

        if self.device == "cuda" or self.device == "mps":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        start_time = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

        response_time = time.time() - start_time
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove prompt from response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()

        return response, response_time

def load_binary_tests(limit=None):
    """Load binary/assembly test files with ground truth"""
    test_files = []
    ground_truth_dir = "data/ground_truth/assembly_binary"

    if not os.path.exists(BINARY_FILES_DIR):
        print(f"❌ Binary files directory not found: {BINARY_FILES_DIR}")
        return []

    if not os.path.exists(ground_truth_dir):
        print(f"❌ Ground truth directory not found: {ground_truth_dir}")
        return []

    # Get all .s files (assembly)
    assembly_files = glob.glob(os.path.join(BINARY_FILES_DIR, "*.s"))

    for file_path in assembly_files:
        test_id = os.path.splitext(os.path.basename(file_path))[0]

        # Load ground truth
        ground_truth_path = os.path.join(ground_truth_dir, f"{test_id}.json")
        if not os.path.exists(ground_truth_path):
            print(f"⚠️  No ground truth for: {test_id}, skipping...")
            continue

        with open(ground_truth_path, 'r') as gt_file:
            ground_truth = json.load(gt_file)

        # Load test file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract expected algorithms from ground truth
        expected_algorithms = ground_truth.get('expected_findings', {}).get('vulnerable_algorithms_detected', [])

        test_files.append({
            'test_id': test_id,
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'content': content,
            'expected_algorithms': expected_algorithms,
            'ground_truth': ground_truth
        })

        if limit and len(test_files) >= limit:
            break

    print(f"✅ Loaded {len(test_files)} binary test files with ground truth")
    return test_files

def create_prompt(test_case):
    """Create prompt for binary analysis"""
    content = test_case['content']

    # Truncate if too long
    if len(content) > 3000:
        content = content[:3000] + "\n... (truncated)"

    prompt = f"""You are a cybersecurity expert analyzing assembly code for post-quantum cryptography vulnerabilities.

Analyze the following assembly code and identify any cryptographic algorithms that are vulnerable to quantum computing attacks.

Assembly code:
```
{content}
```

Respond ONLY with a valid JSON object in this exact format:
{{
    "is_pqc_vulnerable": true or false,
    "detected_algorithms": ["algorithm1", "algorithm2"],
    "vulnerability_details": "detailed explanation",
    "recommendations": "security recommendations",
    "confidence_score": 0.0 to 1.0
}}"""

    return prompt

def parse_json_response(response_text):
    """Extract and parse JSON from response"""
    try:
        # Find JSON in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            return json.loads(json_str)
        else:
            return None
    except Exception as e:
        return None

def evaluate_response(response_json, expected_algorithms):
    """Evaluate model response"""
    if not response_json:
        return {
            'json_valid': False,
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': len(expected_algorithms)
        }

    detected = set([alg.upper().strip() for alg in response_json.get('detected_algorithms', [])])
    expected = set([alg.upper().strip() for alg in expected_algorithms])

    # Fuzzy matching for common variants
    matched = set()
    for det in detected:
        for exp in expected:
            if det in exp or exp in det or det.replace('-', '') == exp.replace('-', ''):
                matched.add(exp)

    tp = len(matched)
    fp = len(detected - expected)
    fn = len(expected - matched)

    return {
        'json_valid': True,
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn
    }

def run_benchmark():
    """Run benchmark comparing base vs tuned models"""

    print("="*80)
    print("Base Llama 3.1 vs PQC-tuned Llama Benchmark")
    print("Binary/Assembly Files Only")
    print("="*80)

    # Load test files
    print(f"\n📂 Loading binary test files from: {BINARY_FILES_DIR}")
    test_files = load_binary_tests(limit=TEST_LIMIT)

    if not test_files:
        print("❌ No test files found!")
        return

    print(f"\n📊 Total tests: {len(test_files)}")

    # Results storage
    results = {
        "benchmark_info": {
            "timestamp": datetime.now().isoformat(),
            "base_model": BASE_MODEL_NAME,
            "tuned_model": PQCLLAMA_ADAPTER,
            "test_type": "assembly_binary",
            "total_tests": len(test_files)
        },
        "base_results": [],
        "tuned_results": []
    }

    print(f"\n{'='*80}")
    print("Running Benchmark - BASE MODEL")
    print(f"{'='*80}\n")

    # Run BASE model tests first
    print(f"\n🔧 Initializing Base Model...")
    base_model = LlamaModelWrapper(BASE_MODEL_NAME, is_pqc_tuned=False, cache_dir=CACHE_DIR)

    for idx, test_case in enumerate(tqdm(test_files, desc="Testing Base Model")):
        test_id = test_case['test_id']
        expected_algorithms = test_case['expected_algorithms']
        prompt = create_prompt(test_case)

        try:
            print(f"\n[{idx+1}/{len(test_files)}] Testing Base Model: {test_id}")
            base_response, base_time = base_model.generate(prompt)
            base_json = parse_json_response(base_response)
            base_eval = evaluate_response(base_json, expected_algorithms)

            results["base_results"].append({
                "test_id": test_id,
                "file_name": test_case['file_name'],
                "response_time": base_time,
                "json_valid": base_eval['json_valid'],
                "true_positives": base_eval['true_positives'],
                "false_positives": base_eval['false_positives'],
                "false_negatives": base_eval['false_negatives'],
                "expected_algorithms": expected_algorithms,
                "detected_algorithms": base_json.get('detected_algorithms', []) if base_json else []
            })

            print(f"  Base: TP={base_eval['true_positives']}, FP={base_eval['false_positives']}, FN={base_eval['false_negatives']}, Time={base_time:.2f}s")

        except Exception as e:
            print(f"  ❌ Base model error: {e}")
            results["base_results"].append({
                "test_id": test_id,
                "error": str(e)
            })

    # Unload base model to free memory
    print(f"\n🗑️  Unloading base model to free memory...")
    del base_model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    print(f"\n{'='*80}")
    print("Running Benchmark - TUNED MODEL")
    print(f"{'='*80}\n")

    # Run TUNED model tests second
    print(f"\n🔧 Initializing Tuned Model...")
    tuned_model = LlamaModelWrapper(BASE_MODEL_NAME, is_pqc_tuned=True, cache_dir=CACHE_DIR)

    for idx, test_case in enumerate(tqdm(test_files, desc="Testing Tuned Model")):
        test_id = test_case['test_id']
        expected_algorithms = test_case['expected_algorithms']
        prompt = create_prompt(test_case)

        try:
            print(f"\n[{idx+1}/{len(test_files)}] Testing Tuned Model: {test_id}")
            tuned_response, tuned_time = tuned_model.generate(prompt)
            tuned_json = parse_json_response(tuned_response)
            tuned_eval = evaluate_response(tuned_json, expected_algorithms)

            results["tuned_results"].append({
                "test_id": test_id,
                "file_name": test_case['file_name'],
                "response_time": tuned_time,
                "json_valid": tuned_eval['json_valid'],
                "true_positives": tuned_eval['true_positives'],
                "false_positives": tuned_eval['false_positives'],
                "false_negatives": tuned_eval['false_negatives'],
                "expected_algorithms": expected_algorithms,
                "detected_algorithms": tuned_json.get('detected_algorithms', []) if tuned_json else []
            })

            print(f"  Tuned: TP={tuned_eval['true_positives']}, FP={tuned_eval['false_positives']}, FN={tuned_eval['false_negatives']}, Time={tuned_time:.2f}s")

        except Exception as e:
            print(f"  ❌ Tuned model error: {e}")
            results["tuned_results"].append({
                "test_id": test_id,
                "error": str(e)
            })

    # Unload tuned model
    print(f"\n🗑️  Unloading tuned model...")
    del tuned_model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_file = os.path.join(RESULTS_DIR, f"base_vs_tuned_binary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Benchmark complete! Results saved to: {output_file}")

    # Print summary
    print_summary(results)

def print_summary(results):
    """Print benchmark summary"""
    print(f"\n{'='*80}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*80}")

    for model_name, model_results in [("Base Llama 3.1", results["base_results"]),
                                       ("PQC-tuned Llama", results["tuned_results"])]:
        valid_results = [r for r in model_results if 'error' not in r]

        if valid_results:
            total_tp = sum(r['true_positives'] for r in valid_results)
            total_fp = sum(r['false_positives'] for r in valid_results)
            total_fn = sum(r['false_negatives'] for r in valid_results)
            avg_time = sum(r['response_time'] for r in valid_results) / len(valid_results)

            precision = total_tp / (total_tp + total_fp) * 100 if (total_tp + total_fp) > 0 else 0
            recall = total_tp / (total_tp + total_fn) * 100 if (total_tp + total_fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            print(f"\n{model_name}:")
            print(f"  Tests: {len(valid_results)}")
            print(f"  Avg Response Time: {avg_time:.2f}s")
            print(f"  Precision: {precision:.2f}%")
            print(f"  Recall: {recall:.2f}%")
            print(f"  F1-Score: {f1:.2f}%")
            print(f"  TP: {total_tp}, FP: {total_fp}, FN: {total_fn}")

    # Comparison
    base_valid = [r for r in results["base_results"] if 'error' not in r]
    tuned_valid = [r for r in results["tuned_results"] if 'error' not in r]

    if base_valid and tuned_valid:
        base_f1 = calculate_f1(base_valid)
        tuned_f1 = calculate_f1(tuned_valid)
        improvement = ((tuned_f1 - base_f1) / base_f1 * 100) if base_f1 > 0 else 0

        print(f"\n{'='*80}")
        print("IMPROVEMENT")
        print(f"{'='*80}")
        print(f"Base F1-Score: {base_f1:.2f}%")
        print(f"Tuned F1-Score: {tuned_f1:.2f}%")
        print(f"Improvement: {improvement:+.2f}%")

def calculate_f1(results):
    """Calculate F1 score"""
    total_tp = sum(r['true_positives'] for r in results)
    total_fp = sum(r['false_positives'] for r in results)
    total_fn = sum(r['false_negatives'] for r in results)

    precision = total_tp / (total_tp + total_fp) * 100 if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) * 100 if (total_tp + total_fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return f1

if __name__ == "__main__":
    run_benchmark()
