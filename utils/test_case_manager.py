import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class TestCaseManager:
    def __init__(self, test_cases_dir: str, ground_truth_dir: str):
        self.test_cases_dir = Path(test_cases_dir)
        self.ground_truth_dir = Path(ground_truth_dir)

        self.test_cases_dir.mkdir(parents=True, exist_ok=True)
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)

        for agent_type in ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']:
            (self.test_cases_dir / agent_type).mkdir(exist_ok=True)
            (self.ground_truth_dir / agent_type).mkdir(exist_ok=True)

    def load_test_cases(self, agent_type: str) -> List[Dict[str, Any]]:
        agent_dir = self.test_cases_dir / agent_type
        test_cases = []

        if not agent_dir.exists():
            return test_cases

        for test_file in agent_dir.glob('*.json'):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_case = json.load(f)
                    test_case['file_path'] = str(test_file)
                    test_case['test_id'] = test_file.stem
                    test_cases.append(test_case)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading test case {test_file}: {e}")

        return sorted(test_cases, key=lambda x: x.get('test_id', ''))

    def load_ground_truth(self, agent_type: str, test_id: str) -> Optional[Dict[str, Any]]:
        truth_file = self.ground_truth_dir / agent_type / f"{test_id}.json"

        if not truth_file.exists():
            return None

        try:
            with open(truth_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading ground truth {truth_file}: {e}")
            return None

    def save_test_case(self, agent_type: str, test_id: str, test_data: Dict[str, Any]) -> bool:
        test_file = self.test_cases_dir / agent_type / f"{test_id}.json"

        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving test case {test_file}: {e}")
            return False

    def save_ground_truth(self, agent_type: str, test_id: str, ground_truth: Dict[str, Any]) -> bool:
        truth_file = self.ground_truth_dir / agent_type / f"{test_id}.json"

        try:
            with open(truth_file, 'w', encoding='utf-8') as f:
                json.dump(ground_truth, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving ground truth {truth_file}: {e}")
            return False

    def get_test_case_stats(self) -> Dict[str, int]:
        stats = {}

        for agent_type in ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']:
            test_cases = self.load_test_cases(agent_type)
            ground_truths = len(list((self.ground_truth_dir / agent_type).glob('*.json')))

            stats[agent_type] = {
                'test_cases': len(test_cases),
                'ground_truths': ground_truths,
                'coverage': ground_truths / len(test_cases) if test_cases else 0
            }

        return stats

    def validate_test_case(self, test_case: Dict[str, Any]) -> List[str]:
        errors = []

        required_fields = ['input_data', 'description', 'expected_analysis_points']
        for field in required_fields:
            if field not in test_case:
                errors.append(f"Missing required field: {field}")

        if 'input_data' in test_case and not test_case['input_data'].strip():
            errors.append("input_data cannot be empty")

        return errors

    def create_test_case_template(self, agent_type: str) -> Dict[str, Any]:
        templates = {
            'source_code': {
                'input_data': '# Sample source code for PQC algorithm detection',
                'description': 'Test case for detecting post-quantum cryptography usage in source code',
                'expected_analysis_points': [
                    'post-quantum cryptography algorithm identification',
                    'PQC implementation patterns',
                    'quantum-resistant key exchange mechanisms'
                ],
                'pqc_algorithms_present': [],
                'pqc_algorithm_families': [],
                'difficulty': 'medium',
                'tags': ['pqc', 'source-code', 'template']
            },
            'assembly_binary': {
                'input_data': '; Sample assembly code with potential PQC operations',
                'description': 'Test case for detecting PQC algorithm signatures in assembly/binary code',
                'expected_analysis_points': [
                    'post-quantum cryptographic operations in assembly',
                    'lattice-based arithmetic patterns',
                    'large integer arithmetic indicative of PQC'
                ],
                'pqc_algorithms_present': [],
                'pqc_algorithm_families': [],
                'difficulty': 'medium',
                'tags': ['pqc', 'assembly', 'template']
            },
            'dynamic_analysis': {
                'input_data': '{"runtime_data": "sample dynamic analysis with PQC indicators"}',
                'description': 'Test case for detecting PQC usage through runtime behavior analysis',
                'expected_analysis_points': [
                    'PQC algorithm usage through API calls',
                    'memory allocation patterns characteristic of PQC',
                    'performance signatures of PQC operations'
                ],
                'pqc_algorithms_present': [],
                'pqc_algorithm_families': [],
                'difficulty': 'medium',
                'tags': ['pqc', 'dynamic', 'template']
            },
            'logs_config': {
                'input_data': '2024-01-01 10:00:00 [INFO] Sample log entry with PQC configuration',
                'description': 'Test case for detecting PQC configuration and usage in logs',
                'expected_analysis_points': [
                    'PQC algorithm configuration parameters',
                    'post-quantum certificate usage',
                    'TLS/SSL configuration with quantum-resistant cipher suites'
                ],
                'pqc_algorithms_present': [],
                'pqc_algorithm_families': [],
                'difficulty': 'medium',
                'tags': ['pqc', 'logs', 'config', 'template']
            }
        }

        return templates.get(agent_type, {})

    def create_ground_truth_template(self, agent_type: str) -> Dict[str, Any]:
        return {
            'expected_findings': {
                'pqc_algorithms_detected': [],
                'pqc_algorithm_families': [],
                'confidence_indicators': [],
                'false_positive_indicators': []
            },
            'expected_confidence_range': [0.7, 1.0],
            'key_metrics': {
                'pqc_detection_accuracy': 0.8,
                'algorithm_identification_precision': 0.75,
                'false_positive_rate_max': 0.1,
                'completeness_threshold': 0.7
            },
            'evaluation_criteria': [
                'accuracy of PQC algorithm identification',
                'precision in distinguishing PQC from classical crypto',
                'completeness of PQC feature detection',
                'ability to detect obfuscated or indirect PQC usage',
                'recognition of hybrid classical-PQC implementations'
            ],
            'pqc_specific_validation': {
                'algorithm_categories': ['lattice_based', 'code_based', 'multivariate', 'hash_based', 'isogeny_based'],
                'detection_difficulty': 'medium',
                'obfuscation_level': 'none'
            }
        }