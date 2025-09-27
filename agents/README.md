# AI Benchmark - Specialized Agents Documentation

이 문서는 AI 벤치마크 시스템에서 사용되는 전용 분석 에이전트들의 상세한 정보를 제공합니다.

## 개요

모든 에이전트는 `BaseAnalysisAgent` 추상 클래스를 상속받아 구현되며, 양자 취약 암호 알고리즘 탐지에 특화되어 있습니다. 각 에이전트는 특정 데이터 타입과 분석 도메인에 최적화된 프롬프트와 검증 로직을 가지고 있습니다.

## 지원되는 에이전트 타입

### 1. Source Code Agent (`source_code`)

**목적**: 소스 코드에서 양자 취약 암호 알고리즘 탐지

**입력 데이터**:
- 다양한 프로그래밍 언어의 소스 코드
- 함수, 클래스, import 문 등을 포함한 코드 텍스트

**출력 형식**:
```json
{
    "agent_type": "Source Code Vulnerable Crypto Detection Agent",
    "analysis_results": {
        "quantum_vulnerable_rsa_implementations_and_usage_patterns": "<분석 결과>",
        "elliptic_curve_cryptography_(ecc/ecdsa/ecdh)_implementations": "<분석 결과>",
        "discrete_logarithm_based_algorithms_(dsa,_dh,_elgamal)": "<분석 결과>",
        "korean_domestic_algorithms_(seed,_aria,_hight,_lea,_kcdsa,_ec_kcdsa,_has_160,_lsh)": "<분석 결과>",
        "symmetric_ciphers_vulnerable_to_grover's_algorithm_(aes_128,_3des,_des,_rc4)": "<분석 결과>",
        "weak_hash_functions_(md5,_sha_1,_sha_256_with_reduced_security)": "<분석 결과>",
        "vulnerable_padding_schemes_(pkcs#1_v1.5,_weak_oaep)": "<분석 결과>",
        "insecure_random_number_generators_and_key_derivation_functions": "<분석 결과>",
        "obfuscated_or_indirect_implementations_of_vulnerable_algorithms": "<분석 결과>",
        "hybrid_systems_mixing_quantum_vulnerable_and_quantum_resistant_algorithms": "<분석 결과>",
        "legacy_cryptographic_libraries_and_deprecated_cipher_suites": "<분석 결과>",
        "implementation_specific_vulnerabilities_in_quantum_vulnerable_algorithms": "<분석 결과>"
    },
    "confidence_score": 0.95,
    "summary": "요약"
}
```

**특화된 프롬프트**:
```
Analyze the following source code and provide insights about: {analysis_points}
```

**검증 로직**:
- 기본 코드 패턴 (함수, 클래스, import 등)
- 양자 취약 암호 패턴 (RSA, ECC, 한국 알고리즘 등)
- 정규식 기반 패턴 매칭

### 2. Assembly Binary Agent (`assembly_binary`)

**목적**: 어셈블리/바이너리 코드에서 양자 취약 암호 연산 탐지

**입력 데이터**:
- 어셈블리 코드 (x86, x64 등)
- 바이너리 파일의 디스어셈블된 내용
- 16진수 덤프

**출력 형식**:
```json
{
    "agent_type": "Assembly Binary Vulnerable Crypto Detection Agent",
    "analysis_results": {
        "rsa_modular_exponentiation_and_large_integer_arithmetic_patterns": "<분석 결과>",
        "elliptic_curve_point_operations_and_scalar_multiplication_patterns": "<분석 결과>",
        "discrete_logarithm_computation_signatures_(dsa,_dh,_elgamal)": "<분석 결과>",
        "korean_algorithm_signatures_(seed_s_boxes,_aria_transformations,_hight_operations,_lea_rotations)": "<분석 결과>",
        "symmetric_cipher_patterns_vulnerable_to_quantum_attacks_(des,_3des,_rc4,_aes_128)": "<분석 결과>",
        "cryptographic_hash_function_implementations_(md5,_sha_1,_vulnerable_sha_variants)": "<분석 결과>",
        "big_integer_libraries_and_modular_arithmetic_operations": "<분석 결과>",
        "cryptographic_library_calls_and_api_signatures": "<분석 결과>",
        "optimization_patterns_specific_to_vulnerable_crypto_algorithms": "<분석 결과>",
        "korean_cryptographic_library_signatures_and_domestic_algorithm_implementations": "<분석 결과>",
        "memory_allocation_patterns_for_cryptographic_key_storage": "<분석 결과>",
        "side_channel_vulnerable_implementation_patterns": "<분석 결과>",
        "assembly_level_obfuscation_of_vulnerable_crypto_operations": "<분석 결과>"
    },
    "confidence_score": 0.88,
    "summary": "요약"
}
```

**특화된 프롬프트**:
```
Analyze the following assembly/binary code and identify: {analysis_points}
```

**검증 로직**:
- 표준 어셈블리 지시어 (mov, push, call 등)
- 레지스터 패턴 (eax, rax 등)
- 암호화 관련 함수 호출 패턴
- 대용량 정수 연산 패턴

### 3. Dynamic Analysis Agent (`dynamic_analysis`)

**목적**: 런타임 동작에서 양자 취약 암호 사용 탐지

**입력 데이터**:
- JSON 형태의 동적 분석 데이터
- API 호출 로그
- 성능 메트릭
- 메모리/네트워크 사용 패턴

**출력 형식**:
```json
{
    "agent_type": "Dynamic Analysis Vulnerable Crypto Detection Agent",
    "analysis_results": {
        "rsa_key_generation_and_modular_exponentiation_api_calls_and_performance_signatures": "<분석 결과>",
        "elliptic_curve_cryptography_operations_and_point_multiplication_behaviors": "<분석 결과>",
        "discrete_logarithm_algorithm_usage_patterns_(dsa,_dh,_elgamal)": "<분석 결과>",
        "korean_algorithm_runtime_signatures_(seed,_aria,_hight,_lea,_kcdsa_operations)": "<분석 결과>",
        "symmetric_cipher_usage_vulnerable_to_quantum_attacks_(des,_3des,_rc4,_aes_128)": "<분석 결과>",
        "cryptographic_hash_function_calls_and_timing_patterns_(md5,_sha_1,_sha_256)": "<분석 결과>",
        "vulnerable_random_number_generation_and_entropy_collection_patterns": "<분석 결과>",
        "cryptographic_library_loading_and_initialization_behaviors": "<분석 결과>",
        "memory_allocation_patterns_for_large_cryptographic_keys_and_operations": "<분석 결과>",
        "network_protocol_usage_with_quantum_vulnerable_cipher_suites": "<분석 결과>",
        "certificate_validation_and_pki_operations_with_vulnerable_algorithms": "<분석 결과>",
        "performance_characteristics_indicating_quantum_vulnerable_crypto_computations": "<분석 결과>",
        "korean_cryptographic_library_usage_and_domestic_algorithm_api_calls": "<분석 결과>",
        "side_channel_information_leakage_in_vulnerable_crypto_implementations": "<분석 결과>"
    },
    "confidence_score": 0.92,
    "summary": "요약"
}
```

**특화된 프롬프트**:
```
Analyze the following dynamic analysis parameters and extract: {analysis_points}
```

**검증 로직**:
- JSON 파싱 시도
- 동적 분석 지표 (PID, 타임스탬프, 메모리 사용량 등)
- 암호화 라이브러리 API 호출 패턴
- 성능 특성 분석

### 4. Logs Config Agent (`logs_config`)

**목적**: 설정 파일과 로그에서 양자 취약 암호 설정 탐지

**입력 데이터**:
- 설정 파일 (INI, YAML, JSON, XML 등)
- 시스템 로그
- 애플리케이션 로그
- SSL/TLS 설정

**출력 형식**:
```json
{
    "agent_type": "Configuration and Logs Vulnerable Crypto Analysis Agent",
    "analysis_results": {
        "rsa_certificate_configurations_and_key_specifications_in_config_files": "<분석 결과>",
        "elliptic_curve_cipher_suite_configurations_and_ecc_parameter_settings": "<분석 결과>",
        "discrete_logarithm_based_algorithm_configurations_(dsa,_dh,_elgamal)": "<분석 결과>",
        "korean_algorithm_configuration_parameters_(seed,_aria,_hight,_lea,_kcdsa,_has_160,_lsh)": "<분석 결과>",
        "symmetric_cipher_configurations_vulnerable_to_quantum_attacks": "<분석 결과>",
        "ssl/tls_configuration_with_quantum_vulnerable_cipher_suites_and_protocols": "<분석 결과>",
        "cryptographic_library_configuration_and_algorithm_selection_settings": "<분석 결과>",
        "certificate_authority_and_pki_configurations_using_vulnerable_algorithms": "<분석 결과>",
        "log_entries_indicating_quantum_vulnerable_cryptographic_operations": "<분석 결과>",
        "authentication_and_key_management_system_configurations": "<분석 결과>",
        "legacy_cryptographic_protocol_configurations_and_deprecated_settings": "<분석 결과>",
        "korean_domestic_cryptographic_standard_compliance_configurations": "<분석 결과>",
        "error_patterns_and_warnings_related_to_vulnerable_crypto_implementations": "<분석 결과>",
        "migration_logs_showing_use_of_quantum_vulnerable_to_quantum_resistant_transitions": "<분석 결과>"
    },
    "confidence_score": 0.87,
    "summary": "요약"
}
```

**특화된 프롬프트**:
```
Analyze the following logs/configuration and determine: {analysis_points}
```

**검증 로직**:
- 표준 로그 형식 (타임스탬프, 로그 레벨 등)
- 설정 파일 패턴 (키-값 쌍, 섹션 등)
- SSL/TLS 설정 패턴
- 취약한 암호화 설정 패턴

## 공통 기능

### BaseAnalysisAgent 메서드

1. **`get_analysis_points()`**: 각 에이전트의 분석 포인트 목록 반환
2. **`validate_input(input_data)`**: 입력 데이터 유효성 검증
3. **`create_prompt(input_data, analysis_points)`**: 분석용 프롬프트 생성
4. **`extract_key_findings(response)`**: JSON 응답 파싱 및 검증

### AgentFactory 사용법

```python
from agents.agent_factory import AgentFactory

# 지원되는 에이전트 타입 확인
supported_agents = AgentFactory.get_supported_agents()
# ['source_code', 'assembly_binary', 'dynamic_analysis', 'logs_config']

# 에이전트 생성
agent = AgentFactory.create_agent('source_code')

# 에이전트 정보 확인
info = AgentFactory.get_agent_info('source_code')
```

## 특화된 탐지 패턴

### 한국 국산 알고리즘
- **SEED**: 128비트 블록 암호
- **ARIA**: 128/192/256비트 블록 암호
- **HIGHT**: 64비트 블록 암호
- **LEA**: 128비트 블록 암호
- **KCDSA**: 한국형 DSA
- **HAS-160**: 한국형 해시 함수
- **LSH**: 한국형 해시 함수

### 양자 취약 알고리즘
- **RSA**: 소인수분해 문제 기반
- **ECC/ECDSA**: 타원곡선 이산로그 문제 기반
- **DH/DSA**: 이산로그 문제 기반
- **대칭키 암호**: Grover 알고리즘에 취약 (키 길이 절반 감소)

## 신뢰도 점수

각 에이전트는 0.0에서 1.0 사이의 신뢰도 점수를 제공합니다:
- **0.9-1.0**: 매우 높은 확신
- **0.7-0.9**: 높은 확신
- **0.5-0.7**: 보통 확신
- **0.3-0.5**: 낮은 확신
- **0.0-0.3**: 매우 낮은 확신

## 사용 예시

```python
# 소스 코드 분석
agent = AgentFactory.create_agent('source_code')
prompt = agent.create_prompt(source_code_content)
# LLM에 프롬프트 전송 후 응답 받기
results = agent.extract_key_findings(llm_response)

# 동적 분석
agent = AgentFactory.create_agent('dynamic_analysis')
if agent.validate_input(dynamic_data):
    prompt = agent.create_prompt(dynamic_data)
    # 분석 진행
```

이 시스템은 포스트 양자 암호(Post-Quantum Cryptography) 전환을 위한 기존 시스템의 취약점 식별에 특화되어 있습니다.