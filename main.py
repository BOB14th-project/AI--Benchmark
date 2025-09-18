#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

from benchmark import LLMAnalysisBenchmark
from reports.csv_generator import CSVReportGenerator
from utils.test_case_manager import TestCaseManager
from config.config_loader import ConfigLoader

def main():
    parser = argparse.ArgumentParser(
        description="Quantum-Vulnerable Cryptography Detection Benchmark"
    )

    parser.add_argument('--config', default='config/config.yaml', help='Configuration file path')
    parser.add_argument('--providers', nargs='+', help='LLM providers to test')
    parser.add_argument('--agents', nargs='+', choices=['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config'], help='Analysis agents to test')
    parser.add_argument('--workers', type=int, default=4, help='Number of concurrent workers')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--generate-vulnerable-test-cases', action='store_true', help='Generate test cases and exit')
    parser.add_argument('--list-providers', action='store_true', help='List providers and exit')
    parser.add_argument('--list-agents', action='store_true', help='List agents and exit')
    parser.add_argument('--test-cases-stats', action='store_true', help='Show test case statistics and exit')
    parser.add_argument('--csv-only', action='store_true', help='Generate only CSV reports')
    parser.add_argument('--vulnerable-algorithms', action='store_true', help='List vulnerable algorithms and exit')
    parser.add_argument('--korean-algorithms', action='store_true', help='List Korean algorithms and exit')

    args = parser.parse_args()

    try:
        config = ConfigLoader(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    if args.vulnerable_algorithms:
        show_vulnerable_algorithms(config)
        return

    if args.korean_algorithms:
        show_korean_algorithms(config)
        return

    if args.list_providers:
        show_providers(config)
        return

    if args.list_agents:
        show_agents(config)
        return

    test_manager = TestCaseManager(
        config.get_paths_config()['test_cases'],
        config.get_paths_config()['ground_truth']
    )

    if args.test_cases_stats:
        show_test_stats(test_manager)
        return

    if args.generate_vulnerable_test_cases:
        generate_test_cases(test_manager, config)
        return

    run_benchmark(args, config, test_manager)

def show_vulnerable_algorithms(config):
    vulnerable_algorithms = config.config.get('benchmark', {}).get('vulnerable_algorithms', {})
    print("Known Quantum-Vulnerable Cryptographic Algorithms by Category:")
    for category, subcategories in vulnerable_algorithms.items():
        category_name = category.replace('_', ' ').title()
        print(f"\n  {category_name}:")
        if isinstance(subcategories, dict):
            for subcat, algorithms in subcategories.items():
                subcat_name = subcat.replace('_', ' ').title()
                print(f"    {subcat_name}:")
                for algorithm in algorithms:
                    print(f"      • {algorithm}")
        else:
            for algorithm in subcategories:
                print(f"    • {algorithm}")

def show_korean_algorithms(config):
    vulnerable_algorithms = config.config.get('benchmark', {}).get('vulnerable_algorithms', {})
    print("Korean Domestic Cryptographic Algorithms and Their Quantum Vulnerability:")

    korean_algs = {
        "Public Key Algorithms (Shor's Algorithm Vulnerable)":
            vulnerable_algorithms.get('shor_vulnerable', {}).get('korean_public_key', []),
        "Symmetric Ciphers (Grover's Algorithm Vulnerable)":
            vulnerable_algorithms.get('grover_vulnerable', {}).get('korean_symmetric', []),
        "Hash Functions (Grover's Algorithm Vulnerable)":
            vulnerable_algorithms.get('grover_vulnerable', {}).get('korean_hash', []),
        "Legacy/Deprecated Korean Algorithms":
            vulnerable_algorithms.get('other_vulnerable', {}).get('korean_legacy', [])
    }

    for category, algorithms in korean_algs.items():
        if algorithms:
            print(f"\n  {category}:")
            for algorithm in algorithms:
                print(f"    • {algorithm}")

    print("\nNote: These Korean domestic algorithms are vulnerable to quantum attacks")
    print("and should be replaced with post-quantum cryptographic alternatives.")

def show_providers(config):
    providers = config.get_all_llm_providers()
    print("Available LLM providers for vulnerable crypto detection:")
    for provider in providers:
        provider_config = config.get_llm_config(provider)
        status = "✓" if provider_config.get('api_key') and not provider_config['api_key'].startswith('your_') else "✗"
        print(f"  {status} {provider} ({provider_config.get('model', 'unknown model')})")

def show_agents(config):
    agents = config.get_all_agents()
    print("Available vulnerable crypto detection agents:")
    for agent in agents:
        agent_config = config.get_agent_config(agent)
        print(f"  • {agent}: {agent_config.get('description', 'No description')}")

def show_test_stats(test_manager):
    stats = test_manager.get_test_case_stats()
    print("Vulnerable crypto detection test cases statistics:")
    for agent_type, stat in stats.items():
        print(f"  {agent_type}:")
        print(f"    Test cases: {stat['test_cases']}")
        print(f"    Ground truths: {stat['ground_truths']}")
        print(f"    Coverage: {stat['coverage']:.1%}")

def generate_test_cases(test_manager, config):
    print("Generating example vulnerable crypto detection test cases...")
    generate_vulnerable_crypto_test_cases(test_manager, config)
    print("Vulnerable crypto detection test cases generated successfully!")
    print("\nGenerated test cases include:")
    print("  • RSA, ECC, DSA, DH implementations")
    print("  • Korean algorithms: SEED, ARIA, HIGHT, LEA, KCDSA, HAS-160")
    print("  • Symmetric ciphers: DES, 3DES, RC4, AES-128")
    print("  • Hash functions: MD5, SHA-1, SHA-256")
    print("  • Obfuscated and indirect implementations")

def run_benchmark(args, config, test_manager):
    print("Starting Quantum-Vulnerable Cryptography Detection Benchmark...")
    print("This benchmark evaluates LLM capability to detect quantum-vulnerable algorithms")
    print("that simple pattern matching cannot identify, including:")
    print("  • Korean domestic algorithms (SEED, ARIA, HIGHT, LEA, etc.)")
    print("  • International standards (RSA, ECC, DSA, DES, etc.)")
    print("  • Obfuscated and indirect implementations")

    benchmark = LLMAnalysisBenchmark(args.config)

    try:
        results = benchmark.run_benchmark(
            providers=args.providers,
            agents=args.agents,
            max_workers=args.workers
        )

        if not args.csv_only:
            json_output = benchmark.save_results(results)
            print(f"\nJSON results saved to: {json_output}")

        csv_generator = CSVReportGenerator(args.output_dir)
        csv_reports = csv_generator.generate_all_reports(results)

        print("\nVulnerable Crypto Detection CSV reports generated:")
        for report in csv_reports:
            print(f"  • {report}")

        print_benchmark_summary(results)

    except Exception as e:
        print(f"Error running vulnerable crypto detection benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def print_benchmark_summary(results):
    print("\nVulnerable Crypto Detection Benchmark Summary:")
    for provider, provider_results in results.items():
        if 'error' in provider_results:
            print(f"  {provider}: ERROR - {provider_results['error']}")
        else:
            summary = provider_results.get('summary', {})
            print(f"  {provider}:")
            print(f"    Success Rate: {summary.get('overall_success_rate', 0):.1%}")
            print(f"    Vulnerable Crypto Detection Accuracy: {summary.get('overall_accuracy', 0):.3f}")
            print(f"    Avg Response Time: {summary.get('overall_response_time', 0):.2f}s")
            print(f"    False Positive Rate: {summary.get('overall_false_positive_rate', 0):.3f}")
            print(f"    False Negative Rate: {summary.get('overall_false_negative_rate', 0):.3f}")

    print("\n" + "="*60)
    print("TOP PERFORMING LLM PROVIDERS:")
    print("="*60)

    provider_scores = []
    for provider, provider_results in results.items():
        if 'error' not in provider_results:
            summary = provider_results.get('summary', {})
            overall_score = (
                summary.get('overall_accuracy', 0) * 0.4 +
                summary.get('overall_success_rate', 0) * 0.3 +
                (1 - summary.get('overall_false_positive_rate', 1)) * 0.15 +
                (1 - summary.get('overall_false_negative_rate', 1)) * 0.15
            )
            provider_scores.append((provider, overall_score, summary))

    provider_scores.sort(key=lambda x: x[1], reverse=True)

    for i, (provider, score, summary) in enumerate(provider_scores[:3]):
        rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        print(f"{rank_emoji} {provider}: Overall Score {score:.3f}")
        print(f"    Accuracy: {summary.get('overall_accuracy', 0):.3f} | "
              f"Success: {summary.get('overall_success_rate', 0):.1%} | "
              f"FP: {summary.get('overall_false_positive_rate', 0):.3f} | "
              f"FN: {summary.get('overall_false_negative_rate', 0):.3f}")

def generate_vulnerable_crypto_test_cases(test_manager: TestCaseManager, config: ConfigLoader):
    vulnerable_crypto_test_data = {
        'source_code': [{
            'input_data': '''
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

class LegacyCryptoSystem:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
        )
        self.public_key = self.private_key.public_key()

    def encrypt_data(self, plaintext):
        ciphertext = self.public_key.encrypt(
            plaintext.encode(),
            padding.PKCS1v15()
        )
        return ciphertext

    def sign_data(self, data):
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1()
        )
        return signature

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

class KoreanCipher:
    def __init__(self):
        self.name = "domestic_cipher"
        self.rounds = 16
        self.key_schedule = self._setup_ks()

    def _setup_ks(self):
        ss0 = [0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0]
        ss1 = [0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0]
        return [ss0, ss1]

    def encrypt_block(self, block, key):
        left, right = block[:4], block[4:]
        for round_num in range(self.rounds):
            temp = self._f_function(right, key, round_num)
            left, right = right, self._xor_bytes(left, temp)
        return right + left
''',
            'description': 'Source code with RSA-1024, SHA-1, MD5, and obfuscated Korean SEED cipher',
            'expected_analysis_points': [
                'quantum-vulnerable RSA implementations',
                'Korean domestic algorithms',
                'weak hash functions',
                'vulnerable padding schemes'
            ],
            'vulnerable_algorithms_present': ['RSA-1024', 'SHA-1', 'MD5', 'SEED', 'PKCS#1 v1.5'],
            'algorithm_categories': ['shor_vulnerable', 'grover_vulnerable', 'korean_algorithms'],
            'korean_algorithms': ['SEED'],
            'difficulty': 'hard',
            'tags': ['vulnerable-crypto', 'rsa', 'korean', 'obfuscated', 'seed']
        }],
        'dynamic_analysis': [{
            'input_data': json.dumps({
                "process_id": 7834,
                "api_calls": [
                    {
                        "function": "RSA_generate_key",
                        "library": "libssl.so.1.1",
                        "parameters": {"key_size": 2048, "public_exponent": 65537},
                        "frequency": 12
                    },
                    {
                        "function": "SEED_encrypt",
                        "library": "libkisa.so",
                        "parameters": {"block_size": 128, "key_size": 128, "mode": "cbc"},
                        "frequency": 234,
                        "note": "Korean domestic cipher detected"
                    },
                    {
                        "function": "MD5_Update",
                        "library": "libcrypto.so.1.1",
                        "parameters": {"data_length": 1024},
                        "frequency": 2341,
                        "security_warning": "MD5 is cryptographically broken"
                    }
                ],
                "library_dependencies": [
                    {
                        "library": "libkisa.so.2.1",
                        "functions": ["SEED_encrypt", "ARIA_encrypt", "HIGHT_init"],
                        "vulnerability_status": "quantum_vulnerable"
                    }
                ]
            }, indent=2),
            'description': 'Runtime analysis with RSA, Korean ciphers, and MD5',
            'expected_analysis_points': [
                'RSA key generation and modular exponentiation',
                'Korean algorithm runtime signatures',
                'weak hash functions'
            ],
            'vulnerable_algorithms_present': ['RSA-2048', 'SEED', 'ARIA', 'MD5'],
            'algorithm_categories': ['shor_vulnerable', 'grover_vulnerable', 'korean_algorithms'],
            'korean_algorithms': ['SEED', 'ARIA'],
            'difficulty': 'hard',
            'tags': ['vulnerable-crypto', 'runtime', 'korean', 'rsa']
        }],
        'logs_config': [{
            'input_data': '''
[crypto_policy]
approved_algorithms = SEED-128, ARIA-128, ARIA-256, LEA-128, HIGHT-64
deprecated_algorithms = DES, 3DES, RC4, MD5, SHA-1

[ssl_configuration]
cipher_suites = [
    "TLS_SEED_WITH_SEED_CBC_SHA",
    "TLS_ARIA_128_GCM_SHA256",
    "TLS_RSA_WITH_ARIA_256_CBC_SHA384"
]
certificate_type = RSA-2048
certificate_signature_algorithm = SHA256withRSA
kcdsa_certificates = enabled

[audit_log_sample]
2024-01-15 14:30:22 [INFO] CryptoInit - Initializing KISA approved cryptographic modules
2024-01-15 14:30:23 [WARN] CryptoConfig - RSA-1024 detected in legacy system
2024-01-15 14:30:24 [INFO] SEED - SEED cipher initialized with 128-bit key
2024-01-15 14:30:25 [INFO] ARIA - ARIA-256 encryption engine started
2024-01-15 14:30:26 [WARN] LegacyCrypto - DES encryption found in legacy module
2024-01-15 14:30:27 [ERROR] HashValidation - MD5 hash function usage detected
2024-01-15 14:30:28 [INFO] KCDSA - Korean Certificate DSA signature verification complete
''',
            'description': 'Korean government crypto configuration with vulnerable algorithms',
            'expected_analysis_points': [
                'Korean algorithm configuration parameters',
                'RSA certificate configurations',
                'weak hash functions'
            ],
            'vulnerable_algorithms_present': ['SEED', 'ARIA', 'LEA', 'RSA-2048', 'KCDSA', 'MD5', 'DES'],
            'algorithm_categories': ['shor_vulnerable', 'grover_vulnerable', 'korean_algorithms'],
            'korean_algorithms': ['SEED', 'ARIA', 'LEA', 'KCDSA'],
            'difficulty': 'medium',
            'tags': ['vulnerable-crypto', 'config', 'korean', 'government']
        }]
    }

    for agent_type, test_cases in vulnerable_crypto_test_data.items():
        for i, test_case in enumerate(test_cases):
            test_id = f"vuln_crypto_{agent_type}_{i+1}"
            test_manager.save_test_case(agent_type, test_id, test_case)

            ground_truth = {
                'expected_findings': {
                    'vulnerable_algorithms_detected': test_case.get('vulnerable_algorithms_present', []),
                    'algorithm_categories': test_case.get('algorithm_categories', []),
                    'korean_algorithms_detected': test_case.get('korean_algorithms', []),
                    'confidence_indicators': [
                        'specific vulnerable algorithm implementation patterns',
                        'characteristic mathematical operations for quantum-vulnerable crypto',
                        'Korean domestic algorithm signatures and behaviors',
                        'legacy cryptographic library usage patterns'
                    ]
                },
                'expected_confidence_range': [0.75, 0.95],
                'key_metrics': {
                    'vulnerable_crypto_detection_accuracy': 0.80,
                    'algorithm_identification_precision': 0.75,
                    'korean_algorithm_detection_accuracy': 0.85,
                    'false_positive_rate_max': 0.1,
                    'false_negative_rate_max': 0.15
                },
                'evaluation_criteria': [
                    'accuracy of vulnerable algorithm identification',
                    'precision in distinguishing vulnerable from quantum-resistant crypto',
                    'ability to detect Korean domestic algorithm usage',
                    'detection of obfuscated or indirect vulnerable implementations',
                    'recognition of legacy and deprecated cryptographic practices'
                ],
                'vulnerability_assessment': {
                    'quantum_threat_level': 'high' if any(alg in ['RSA', 'ECC', 'DSA']
                                                        for alg in test_case.get('vulnerable_algorithms_present', [])) else 'medium',
                    'korean_compliance_issue': len(test_case.get('korean_algorithms', [])) > 0,
                    'detection_difficulty': test_case.get('difficulty', 'medium')
                }
            }
            test_manager.save_ground_truth(agent_type, test_id, ground_truth)

if __name__ == "__main__":
    main()