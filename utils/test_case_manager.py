import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class TestCaseManager:
    def __init__(self, test_cases_dir: str, ground_truth_dir: str, test_files_dir: str = None):
        self.test_cases_dir = Path(test_cases_dir)
        self.ground_truth_dir = Path(ground_truth_dir)
        self.test_files_dir = Path(test_files_dir) if test_files_dir else self.test_cases_dir.parent / 'test_files'

        self.test_cases_dir.mkdir(parents=True, exist_ok=True)
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)
        self.test_files_dir.mkdir(parents=True, exist_ok=True)

        for agent_type in ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']:
            (self.test_cases_dir / agent_type).mkdir(exist_ok=True)
            (self.ground_truth_dir / agent_type).mkdir(exist_ok=True)
            (self.test_files_dir / agent_type).mkdir(exist_ok=True)

    def load_test_cases(self, agent_type: str) -> List[Dict[str, Any]]:
        """Load test cases - supports both legacy JSON format and new file-based format"""
        test_cases = []

        # Load legacy JSON-based test cases
        test_cases.extend(self._load_legacy_test_cases(agent_type))

        # Load new file-based test cases
        test_cases.extend(self._load_file_based_test_cases(agent_type))

        return sorted(test_cases, key=lambda x: x.get('test_id', ''))

    def _load_legacy_test_cases(self, agent_type: str) -> List[Dict[str, Any]]:
        """Load legacy JSON-based test cases where input_data is embedded in JSON"""
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
                    test_case['format'] = 'legacy_json'
                    test_cases.append(test_case)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading test case {test_file}: {e}")

        return test_cases

    def _load_file_based_test_cases(self, agent_type: str) -> List[Dict[str, Any]]:
        """Load file-based test cases where actual test files exist separately"""
        test_files_dir = self.test_files_dir / agent_type
        test_cases = []

        if not test_files_dir.exists():
            return test_cases

        # Get all test files (various extensions based on agent type)
        file_patterns = self._get_file_patterns(agent_type)

        for pattern in file_patterns:
            for test_file in test_files_dir.glob(pattern):
                try:
                    # Read the actual test file content
                    file_content = self._read_test_file(test_file)

                    # Create test case structure
                    test_case = {
                        'test_id': test_file.stem,
                        'input_data': file_content,
                        'file_path': str(test_file),
                        'file_extension': test_file.suffix,
                        'format': 'file_based'
                    }

                    # Try to load additional metadata from ground truth
                    ground_truth = self.load_ground_truth(agent_type, test_file.stem)
                    if ground_truth:
                        test_case.update({
                            'description': ground_truth.get('description', f'File-based test case: {test_file.name}'),
                            'expected_analysis_points': ground_truth.get('expected_findings', {}).get('analysis_points', []),
                            'difficulty': ground_truth.get('difficulty', 'medium'),
                            'tags': ground_truth.get('tags', [])
                        })

                    test_cases.append(test_case)

                except Exception as e:
                    print(f"Error loading file-based test case {test_file}: {e}")

        return test_cases

    def _get_file_patterns(self, agent_type: str) -> List[str]:
        """Get file patterns to search for based on agent type"""
        patterns = {
            'source_code': ['*.py', '*.c', '*.cpp', '*.java', '*.js', '*.go', '*.rs', '*.rb'],
            'assembly_binary': ['*.s', '*.asm', '*.bin', '*.exe', '*.so', '*.dll'],
            'dynamic_analysis': ['*.json', '*.log', '*.txt', '*.trace'],
            'logs_config': ['*.conf', '*.config', '*.yaml', '*.yml', '*.ini', '*.log', '*.txt']
        }
        return patterns.get(agent_type, ['*'])

    def _read_test_file(self, file_path: Path) -> str:
        """Read test file content with appropriate encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try with latin-1 for binary/mixed content
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                # For binary files, read as bytes and represent as hex
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                    if len(binary_content) > 10000:  # Limit large binary files
                        binary_content = binary_content[:10000]
                        return f"Binary content (first 10KB):\n{binary_content.hex()}\n... (truncated)"
                    return f"Binary content:\n{binary_content.hex()}"

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
        """Save test case - supports both legacy JSON format and new file-based format"""
        test_file = self.test_cases_dir / agent_type / f"{test_id}.json"

        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving test case {test_file}: {e}")
            return False

    def save_test_file(self, agent_type: str, test_id: str, file_content: str, file_extension: str = None) -> bool:
        """Save actual test file content separately from metadata"""
        if not file_extension:
            # Auto-detect extension based on agent type and content
            file_extension = self._detect_file_extension(agent_type, file_content)

        test_file = self.test_files_dir / agent_type / f"{test_id}{file_extension}"

        try:
            if file_extension in ['.bin', '.exe', '.so', '.dll'] or 'Binary content:' in file_content:
                # Handle binary content
                if file_content.startswith('Binary content:'):
                    hex_content = file_content.split('\n', 1)[1].replace('... (truncated)', '').strip()
                    binary_data = bytes.fromhex(hex_content)
                    with open(test_file, 'wb') as f:
                        f.write(binary_data)
                else:
                    # Assume text content, save as text
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(file_content)
            else:
                # Text content
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            return True
        except Exception as e:
            print(f"Error saving test file {test_file}: {e}")
            return False

    def _detect_file_extension(self, agent_type: str, content: str) -> str:
        """Auto-detect file extension based on agent type and content"""
        content_lower = content.lower().strip()

        if agent_type == 'source_code':
            if 'import ' in content or 'def ' in content or 'class ' in content:
                return '.py'
            elif '#include' in content or 'int main(' in content:
                return '.c'
            elif 'class ' in content and '{' in content:
                return '.cpp' if 'std::' in content else '.java'
            elif 'function ' in content or 'const ' in content:
                return '.js'
            elif 'fn ' in content or 'let ' in content:
                return '.rs'
            elif 'func ' in content or 'package ' in content:
                return '.go'

        elif agent_type == 'assembly_binary':
            if content_lower.startswith('binary content:'):
                return '.bin'
            elif any(instr in content_lower for instr in ['.section', '.text', 'mov ', 'push', 'pop']):
                return '.s'

        elif agent_type == 'dynamic_analysis':
            if content.strip().startswith('{') and content.strip().endswith('}'):
                return '.json'
            else:
                return '.log'

        elif agent_type == 'logs_config':
            if '=' in content and '[' in content and ']' in content:
                return '.conf'
            elif content.strip().startswith('{'):
                return '.json'
            elif ':' in content and any(key in content_lower for key in ['server', 'listen', 'location']):
                return '.conf'

        return '.txt'

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

    def migrate_to_file_based(self, agent_type: str = None) -> bool:
        """Migrate legacy JSON-based test cases to file-based structure"""
        agent_types = [agent_type] if agent_type else ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']

        for atype in agent_types:
            legacy_cases = self._load_legacy_test_cases(atype)

            for test_case in legacy_cases:
                if 'input_data' not in test_case or not test_case['input_data'].strip():
                    continue

                test_id = test_case['test_id']
                input_data = test_case['input_data']

                # Save the file content separately
                file_extension = self._detect_file_extension(atype, input_data)
                self.save_test_file(atype, test_id, input_data, file_extension)

                # Create updated ground truth with file-based metadata
                ground_truth = {
                    'description': test_case.get('description', f'Migrated test case: {test_id}'),
                    'file_extension': file_extension,
                    'format': 'file_based',
                    'migrated_from_legacy': True,
                    'expected_findings': {
                        'analysis_points': test_case.get('expected_analysis_points', []),
                        'vulnerable_algorithms_detected': test_case.get('vulnerable_algorithms_present', []),
                        'algorithm_categories': test_case.get('algorithm_categories', []),
                        'korean_algorithms_detected': test_case.get('korean_algorithms', [])
                    },
                    'difficulty': test_case.get('difficulty', 'medium'),
                    'tags': test_case.get('tags', [])
                }

                # Save updated ground truth
                self.save_ground_truth(atype, test_id, ground_truth)

                print(f"Migrated {atype}/{test_id} to file-based structure")

        return True

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