"""
Benchmark comparison: PQCllama (fine-tuned) vs Llama3.1 8B (base)
"""
import json
import time
import os
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests
from tqdm import tqdm

# Configuration
PQCLLAMA_MODEL = "sangwoohahn/PQCllama"
LLAMA3_OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"
CACHE_DIR = "./models/pqcllama"

# Test configuration
TEST_LIMIT = 50  # Number of tests to run (set None for all)
WITH_RAG = False  # Set to True if you want to test with RAG

class PQCLlamaWrapper:
    """Wrapper for HuggingFace PQCllama model"""

    def __init__(self, model_name, cache_dir):
        print(f"Loading PQCllama from HuggingFace: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True
        )

        print(f"✅ PQCllama loaded ({self.model.num_parameters() / 1e9:.2f}B parameters)")

    def generate(self, prompt, max_tokens=2000):
        """Generate response from PQCllama"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

        if self.device == "cuda":
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

        # Remove the prompt from response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()

        return response, response_time

class Llama3OllamaWrapper:
    """Wrapper for Ollama Llama3.1 model"""

    def __init__(self, model_name, base_url):
        self.model_name = model_name
        self.base_url = base_url
        print(f"Using Ollama Llama3.1: {model_name}")

        # Test connection
        try:
            response = requests.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                print(f"✅ Connected to Ollama at {base_url}")
            else:
                raise Exception(f"Ollama returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            raise

    def generate(self, prompt, max_tokens=2000):
        """Generate response from Llama3.1 via Ollama"""
        start_time = time.time()

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            }
        )

        response_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            return result.get("response", ""), response_time
        else:
            raise Exception(f"Ollama API error: {response.status_code}")

def load_test_cases(limit=None):
    """Load test cases from test_cases directory"""
    test_cases_dir = "test_cases"
    test_cases = []

    if not os.path.exists(test_cases_dir):
        print(f"❌ Test cases directory not found: {test_cases_dir}")
        return []

    for file_name in os.listdir(test_cases_dir):
        if file_name.endswith('.json'):
            file_path = os.path.join(test_cases_dir, file_name)
            with open(file_path, 'r') as f:
                test_case = json.load(f)
                test_cases.append(test_case)
                if limit and len(test_cases) >= limit:
                    break

    print(f"✅ Loaded {len(test_cases)} test cases")
    return test_cases

def create_prompt(test_case, with_rag=False):
    """Create prompt for the model"""
    file_content = test_case.get('file_content', '')

    prompt = f"""You are a cybersecurity expert analyzing code for post-quantum cryptography vulnerabilities.

Analyze the following code and identify any cryptographic algorithms that are vulnerable to quantum computing attacks.

Code to analyze:
```
{file_content}
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
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            return json.loads(json_str)
        else:
            return None
    except:
        return None

def evaluate_response(response_json, expected_algorithms):
    """Evaluate model response against ground truth"""
    if not response_json:
        return {
            'json_valid': False,
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': len(expected_algorithms)
        }

    detected = set([alg.upper() for alg in response_json.get('detected_algorithms', [])])
    expected = set([alg.upper() for alg in expected_algorithms])

    tp = len(detected & expected)
    fp = len(detected - expected)
    fn = len(expected - detected)

    return {
        'json_valid': True,
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn
    }

def run_benchmark():
    """Run benchmark comparing PQCllama vs Llama3.1"""

    print("="*80)
    print("PQCllama vs Llama3.1 8B Benchmark")
    print("="*80)

    # Initialize models
    print("\n🔧 Initializing models...")
    pqcllama = PQCLlamaWrapper(PQCLLAMA_MODEL, CACHE_DIR)
    llama3 = Llama3OllamaWrapper(LLAMA3_OLLAMA_MODEL, OLLAMA_BASE_URL)

    # Load test cases
    print("\n📂 Loading test cases...")
    test_cases = load_test_cases(limit=TEST_LIMIT)

    if not test_cases:
        print("❌ No test cases found!")
        return

    # Results storage
    results = {
        "benchmark_info": {
            "timestamp": datetime.now().isoformat(),
            "pqcllama_model": PQCLLAMA_MODEL,
            "llama3_model": LLAMA3_OLLAMA_MODEL,
            "total_tests": len(test_cases),
            "with_rag": WITH_RAG
        },
        "pqcllama_results": [],
        "llama3_results": []
    }

    print(f"\n🚀 Running benchmark on {len(test_cases)} test cases...")
    print("="*80)

    for idx, test_case in enumerate(tqdm(test_cases, desc="Testing")):
        test_id = test_case.get('test_id', f'test_{idx}')
        expected_algorithms = test_case.get('expected_algorithms', [])

        prompt = create_prompt(test_case, WITH_RAG)

        # Test PQCllama
        try:
            pqc_response, pqc_time = pqcllama.generate(prompt)
            pqc_json = parse_json_response(pqc_response)
            pqc_eval = evaluate_response(pqc_json, expected_algorithms)

            results["pqcllama_results"].append({
                "test_id": test_id,
                "response_time": pqc_time,
                "json_valid": pqc_eval['json_valid'],
                "true_positives": pqc_eval['true_positives'],
                "false_positives": pqc_eval['false_positives'],
                "false_negatives": pqc_eval['false_negatives'],
                "raw_response": pqc_json
            })
        except Exception as e:
            print(f"\n❌ PQCllama error on {test_id}: {e}")
            results["pqcllama_results"].append({
                "test_id": test_id,
                "error": str(e)
            })

        # Test Llama3.1
        try:
            llama_response, llama_time = llama3.generate(prompt)
            llama_json = parse_json_response(llama_response)
            llama_eval = evaluate_response(llama_json, expected_algorithms)

            results["llama3_results"].append({
                "test_id": test_id,
                "response_time": llama_time,
                "json_valid": llama_eval['json_valid'],
                "true_positives": llama_eval['true_positives'],
                "false_positives": llama_eval['false_positives'],
                "false_negatives": llama_eval['false_negatives'],
                "raw_response": llama_json
            })
        except Exception as e:
            print(f"\n❌ Llama3.1 error on {test_id}: {e}")
            results["llama3_results"].append({
                "test_id": test_id,
                "error": str(e)
            })

    # Save results
    output_file = f"results/pqcllama_vs_llama3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("results", exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Benchmark complete! Results saved to: {output_file}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for model_name, model_results in [("PQCllama", results["pqcllama_results"]),
                                       ("Llama3.1", results["llama3_results"])]:
        valid_results = [r for r in model_results if 'error' not in r]

        if valid_results:
            avg_time = sum(r['response_time'] for r in valid_results) / len(valid_results)
            total_tp = sum(r['true_positives'] for r in valid_results)
            total_fp = sum(r['false_positives'] for r in valid_results)
            total_fn = sum(r['false_negatives'] for r in valid_results)

            precision = total_tp / (total_tp + total_fp) * 100 if (total_tp + total_fp) > 0 else 0
            recall = total_tp / (total_tp + total_fn) * 100 if (total_tp + total_fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            print(f"\n{model_name}:")
            print(f"  Avg Response Time: {avg_time:.2f}s")
            print(f"  Precision: {precision:.2f}%")
            print(f"  Recall: {recall:.2f}%")
            print(f"  F1-Score: {f1:.2f}%")
            print(f"  TP: {total_tp}, FP: {total_fp}, FN: {total_fn}")

if __name__ == "__main__":
    run_benchmark()
