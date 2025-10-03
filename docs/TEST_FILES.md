# 테스트 파일 생성 방법 및 현황

AI Benchmark 프로젝트의 테스트 파일 생성 가이드와 현재 상태를 문서화합니다.

## 📊 현재 테스트 파일 현황

### 전체 통계
- **총 테스트 파일**: 183개
- **Ground Truth 파일**: 183개 (각 테스트 파일당 1개)

### 에이전트별 분류

| 에이전트 | 테스트 파일 수 | 디렉토리 | Ground Truth 위치 |
|---------|--------------|----------|------------------|
| Source Code | 80 | `data/test_files/source_code/` | `data/ground_truth/source_code/` |
| Assembly Binary | 80 | `data/test_files/assembly_binary/` | `data/ground_truth/assembly_binary/` |
| Dynamic Analysis | 6 | `data/test_files/dynamic_analysis/` | `data/ground_truth/dynamic_analysis/` |
| Logs Config | 17 | `data/test_files/logs_config/` | `data/ground_truth/logs_config/` |

## 🎯 테스트 파일 생성 원칙

### 1. 핵심 원칙: 패턴 회피 (Pattern Evasion)

테스트 파일은 단순한 문자열 매칭이나 정규식으로 탐지할 수 없도록 설계되어야 합니다.

**금지 사항:**
```python
# ❌ 나쁜 예 - 직접적인 알고리즘명 사용
import rsa
from Crypto.Cipher import AES
cipher = RSA.new(key)
seed_encrypt = SEED_Cipher()
```

**권장 사항:**
```python
# ✅ 좋은 예 - 우회적 구현
class SecureProcessor:
    def __init__(self):
        self.modulus = 2048  # RSA 키 사이즈를 계산으로 표현
        self.rounds = 16     # SEED 라운드 수를 숫자로만 표현

    def process_data(self, input_block):
        # 알고리즘 로직 구현 (명시적 이름 없이)
        return self._transform(input_block)
```

### 2. 네이밍 컨벤션

#### 파일명 규칙
- **Source Code**: `{알고리즘_설명}_{용도}.{확장자}`
  - 예: `elliptic_curve_key_exchange.java`, `symmetric_block_cipher.py`
- **Assembly**: `{기능_설명}_operations.s`
  - 예: `modular_exponentiation_operations.s`, `polynomial_operations.s`
- **Dynamic Analysis**: `{시스템_타입}_trace.json`
  - 예: `crypto_api_trace.json`, `ssl_handshake_trace.json`
- **Logs Config**: `{서비스_타입}_{파일_타입}.{확장자}`
  - 예: `web_server_ssl.conf`, `vpn_connection.log`

#### 함수/변수명 규칙
- 우회적 비즈니스 로직 네이밍 사용
- 암호화 관련 직접적 키워드 금지
- 예시:
  ```
  ✅ processBlock, transformData, calculateSignature
  ❌ encryptRSA, seedCipher, aesEncrypt
  ```

### 3. 양자 취약 알고리즘 포함 필수

각 테스트 파일은 최소 1개 이상의 양자 취약 알고리즘을 포함해야 합니다.

#### Shor's Algorithm 취약 (공개키 암호)
```
- RSA (모든 키 길이)
- ECC, ECDSA, ECDH (모든 곡선)
- DSA, DH, ElGamal
- Korean: KCDSA, EC-KCDSA
```

#### Grover's Algorithm 취약 (대칭키/해시)
```
- 대칭키: 3DES, DES, RC4, AES-128
- 해시: MD5, SHA-1, SHA-256
- Korean: SEED, ARIA, HIGHT, LEA, HAS-160, LSH
```

#### 고전 공격 취약
```
- RC2, DES, MD4, MD2
```

### 4. 한국 암호화 알고리즘 통합

최소 20%의 테스트 파일은 한국 표준 암호를 포함해야 합니다.

**한국 표준 암호 목록:**
- **블록 암호**: SEED, ARIA, HIGHT, LEA
- **해시 함수**: HAS-160, LSH
- **전자서명**: KCDSA, EC-KCDSA

**구현 예시:**
```python
# SEED 128비트 블록 암호 (16라운드)
class DataTransformer:
    def __init__(self):
        self.block_size = 128 // 8  # 16 bytes
        self.rounds = 16

    def transform(self, block, keys):
        for i in range(self.rounds):
            block = self._round_function(block, keys[i])
        return block
```

## 📁 에이전트별 테스트 파일 형식

### 1. Source Code Agent

**목적**: 소스 코드에서 양자 취약 암호 알고리즘 탐지

**지원 언어**:
- Python (.py)
- Java (.java)
- C/C++ (.c, .cpp)
- JavaScript/TypeScript (.js, .ts)

**파일 구조**:
```python
# 1. Import 구문 (우회적)
import hashlib
import os

# 2. 클래스/함수 정의 (비즈니스 로직으로 위장)
class SecureDataProcessor:
    def __init__(self, key_size=2048):
        self.key_size = key_size

    # 3. 암호 알고리즘 구현 (명시적 이름 없이)
    def generate_keypair(self):
        # RSA 키 생성 로직 (RSA란 단어 없이)
        p = self._generate_prime(self.key_size // 2)
        q = self._generate_prime(self.key_size // 2)
        n = p * q
        return (e, n), (d, n)

    # 4. 실제 사용 예시
    def encrypt_message(self, message, public_key):
        e, n = public_key
        return pow(message, e, n)
```

**Ground Truth 형식**:
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA"],
    "algorithm_categories": ["shor_vulnerable", "public_key"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.85, 0.95]
}
```

**실제 예시 파일**:
- `rsa_public_key_system.java` - RSA 공개키 암호 시스템
- `elliptic_curve_key_exchange.c` - ECDH 키 교환
- `symmetric_block_cipher.py` - SEED 대칭키 암호

### 2. Assembly Binary Agent

**목적**: 어셈블리/바이너리 코드에서 암호 연산 패턴 탐지

**지원 형식**:
- Assembly (.s, .asm)
- Disassembly output
- Binary dumps

**파일 구조**:
```assembly
# 1. 섹션 정의
.section .text
.global crypto_operation

# 2. 함수 프롤로그
crypto_operation:
    push    %rbp
    mov     %rsp, %rbp

# 3. 암호 연산 (예: 모듈러 지수 - RSA 특징)
modular_exp:
    mov     $0x10001, %rcx          # 지수 (RSA 일반적 e 값)
    mov     (%rdi), %rax            # 밑
    mov     8(%rdi), %rbx           # 모듈러스

exp_loop:
    test    %rcx, %rcx
    jz      exp_done

    # 제곱-곱셈 알고리즘 (RSA 핵심 연산)
    mul     %rax                     # rax = rax * rax
    div     %rbx                     # rax = rax % modulus
    shr     $1, %rcx
    jmp     exp_loop

exp_done:
    pop     %rbp
    ret
```

**Ground Truth 형식**:
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA"],
    "algorithm_categories": ["shor_vulnerable", "public_key"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.75, 0.90]
}
```

**탐지 패턴**:
- **RSA**: 큰 정수 곱셈, 모듈러 지수 연산, 제곱-곱셈 알고리즘
- **ECC**: 타원곡선 점 덧셈/배가, Montgomery ladder, 필드 연산
- **SEED/ARIA**: 16라운드 블록 치환, S-box 룩업, XOR 연산 패턴
- **AES**: SubBytes, ShiftRows, MixColumns 패턴
- **Hash**: Compression function, Merkle-Damgård 구조

**실제 예시 파일**:
- `modular_exponentiation_operations.s` - RSA 모듈러 지수
- `elliptic_curve_point_operations.s` - ECC 점 연산
- `chacha20_stream_processor.s` - ChaCha20 스트림 암호

### 3. Dynamic Analysis Agent

**목적**: 런타임 실행 추적에서 암호 API 호출 패턴 탐지

**지원 형식**:
- JSON trace files
- API call logs
- Memory/Performance profiling data

**파일 구조**:
```json
{
  "trace_metadata": {
    "process": "secure_app",
    "pid": 12345,
    "timestamp": "2024-01-15T10:30:00Z",
    "duration_ms": 1250
  },
  "api_calls": [
    {
      "timestamp": "2024-01-15T10:30:00.100Z",
      "function": "CryptGenKey",
      "parameters": {
        "algorithm_id": "0x0000a400",  # CALG_RSA_KEYX (우회적)
        "key_length": 2048,
        "flags": "CRYPT_EXPORTABLE"
      },
      "return_value": "0x00000001",
      "duration_ms": 450
    },
    {
      "timestamp": "2024-01-15T10:30:00.550Z",
      "function": "CryptEncrypt",
      "parameters": {
        "algorithm_id": "0x0000660e",  # CALG_AES_128
        "data_size": 1024
      },
      "duration_ms": 12
    }
  ],
  "memory_operations": [
    {
      "address": "0x7ffee4b2c000",
      "operation": "allocate",
      "size": 256,
      "pattern": "modular_arithmetic_workspace"
    }
  ],
  "performance_metrics": {
    "cpu_intensive_operations": [
      {
        "function": "modular_exponentiation",
        "cpu_cycles": 1250000,
        "characteristic": "public_key_operation"
      }
    ]
  }
}
```

**Ground Truth 형식**:
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "AES-128"],
    "algorithm_categories": ["shor_vulnerable", "public_key", "grover_vulnerable", "symmetric_key"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.80, 0.92]
}
```

**탐지 신호**:
- **API 호출**: CryptGenKey, EVP_PKEY_keygen, crypto.createCipher
- **메모리 패턴**: 큰 정수 버퍼, 타원곡선 점 구조체
- **성능 특성**: 높은 CPU 사용률 (공개키), 빠른 블록 연산 (대칭키)
- **라이브러리**: OpenSSL, CryptoAPI, Bouncy Castle

**실제 예시 파일**:
- `crypto_api_trace.json` - Windows CryptoAPI 추적
- `ssl_handshake_trace.json` - TLS 핸드셰이크 분석

### 4. Logs Config Agent

**목적**: 설정 파일과 로그에서 암호 설정 및 사용 탐지

**지원 형식**:
- Configuration files (.conf, .yaml, .ini, .xml)
- System logs (.log)
- Application logs

**파일 구조 - 설정 파일 (YAML)**:
```yaml
# SSL/TLS 설정 (Apache/Nginx 스타일)
ssl_configuration:
  certificate: /path/to/cert.pem
  private_key: /path/to/key.pem

  # 암호 스위트 (우회적 표현)
  cipher_suites:
    - "ECDHE-RSA-AES256-GCM-SHA384"      # ECDHE, RSA 포함
    - "DHE-RSA-AES128-SHA256"            # DH, RSA 포함
    - "ECDHE-ECDSA-CHACHA20-POLY1305"   # ECDSA 포함

  # 프로토콜 버전
  protocols:
    - TLSv1.2
    - TLSv1.3

  # 키 교환 파라미터
  dh_param_size: 2048                    # DH 그룹 크기
  ecdh_curve: "prime256v1"              # NIST P-256 (ECC)
```

**파일 구조 - 로그 파일**:
```log
2024-01-15 10:30:15 [INFO] Initializing cryptographic module
2024-01-15 10:30:15 [INFO] Loading key pair from keystore
2024-01-15 10:30:16 [DEBUG] Key generation: algorithm=EC, curve=secp256r1, size=256
2024-01-15 10:30:16 [INFO] Certificate: CN=example.com, Signature=ECDSA-SHA256
2024-01-15 10:30:17 [INFO] TLS handshake: cipher=ECDHE-RSA-AES256-GCM-SHA384
2024-01-15 10:30:17 [DEBUG] Key exchange: method=ECDH, curve=prime256v1
2024-01-15 10:30:18 [WARN] Weak cipher detected in legacy mode: 3DES-EDE-CBC
2024-01-15 10:30:19 [INFO] Session established: protocol=TLSv1.2
```

**Ground Truth 형식**:
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "ECDSA", "ECDH", "ECC", "DH", "3DES"],
    "algorithm_categories": ["shor_vulnerable", "public_key", "grover_vulnerable", "symmetric_key"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.88, 0.96]
}
```

**탐지 패턴**:
- **Cipher Suite 문자열**: "ECDHE-RSA", "DHE-DSS", "RC4-SHA"
- **설정 키워드**: ssl_certificate, private_key, cipher_suites
- **알고리즘 파라미터**: key_size, curve_name, dh_param
- **인증서 정보**: Signature Algorithm, Public Key Algorithm
- **한국 알고리즘**: SEED-*, ARIA-*, KCDSA

**실제 예시 파일**:
- `web_server_ssl.conf` - Apache/Nginx SSL 설정
- `vpn_server_runtime.log` - VPN 서버 실행 로그
- `korean_crypto_library_config.ini` - 한국 암호 라이브러리 설정

## 🔧 Ground Truth 작성 가이드

### 기본 구조

모든 ground truth 파일은 동일한 JSON 구조를 따릅니다:

```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["algorithm1", "algorithm2"],
    "algorithm_categories": ["category1", "category2"],
    "korean_algorithms_detected": ["korean_algo1"]
  },
  "expected_confidence_range": [min_confidence, max_confidence]
}
```

### 필드 설명

#### 1. `vulnerable_algorithms_detected` (배열)
- **목적**: 파일에서 탐지되어야 할 양자 취약 알고리즘 목록
- **규칙**:
  - 대소문자 구분 없음 (metrics_calculator에서 소문자 변환)
  - 정확한 알고리즘명 또는 표준 약어 사용
  - 여러 변형을 나열할 필요 없음 (예: "RSA"만 쓰면 "RSA-2048", "RSA_OAEP" 등도 매칭)

**예시**:
```json
"vulnerable_algorithms_detected": ["RSA", "ECDSA", "SEED", "SHA-1"]
```

#### 2. `algorithm_categories` (배열)
- **목적**: 알고리즘이 속한 카테고리 분류
- **가능한 값**:
  - `"shor_vulnerable"`: Shor's Algorithm에 취약 (RSA, ECC, DH, DSA)
  - `"grover_vulnerable"`: Grover's Algorithm에 취약 (AES-128, 해시)
  - `"classical_vulnerable"`: 고전 공격에 취약 (RC4, DES, MD5)
  - `"public_key"`: 공개키 암호
  - `"symmetric_key"`: 대칭키 암호
  - `"hash_function"`: 해시 함수
  - `"mac"`: 메시지 인증 코드
  - `"stream_cipher"`: 스트림 암호

**예시**:
```json
"algorithm_categories": ["shor_vulnerable", "public_key", "grover_vulnerable", "hash_function"]
```

#### 3. `korean_algorithms_detected` (배열)
- **목적**: 한국 표준 암호 알고리즘 별도 추적
- **가능한 값**: SEED, ARIA, HIGHT, LEA, KCDSA, EC-KCDSA, HAS-160, LSH

**예시**:
```json
"korean_algorithms_detected": ["SEED", "ARIA", "KCDSA"]
```

#### 4. `expected_confidence_range` (배열 [min, max])
- **목적**: LLM 응답에서 기대되는 신뢰도 점수 범위
- **범위**: 0.0 ~ 1.0
- **가이드라인**:
  - 명확한 구현 (Source Code): [0.85, 0.95]
  - 중간 난이도 (Assembly): [0.75, 0.90]
  - 복잡한 패턴 (Dynamic Analysis): [0.70, 0.88]
  - 간접적 증거 (Logs Config): [0.80, 0.92]

### 작성 예시

#### 예시 1: RSA + ECC 조합 (Source Code)
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "ECDSA", "ECDH"],
    "algorithm_categories": ["shor_vulnerable", "public_key"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.88, 0.96]
}
```

#### 예시 2: 한국 알고리즘 포함 (Assembly)
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["SEED", "ARIA", "KCDSA"],
    "algorithm_categories": ["grover_vulnerable", "symmetric_key", "shor_vulnerable", "public_key"],
    "korean_algorithms_detected": ["SEED", "ARIA", "KCDSA"]
  },
  "expected_confidence_range": [0.75, 0.88]
}
```

#### 예시 3: 복합 암호 시스템 (Logs Config)
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "ECDSA", "3DES", "SHA-1", "MD5"],
    "algorithm_categories": ["shor_vulnerable", "public_key", "grover_vulnerable", "classical_vulnerable", "symmetric_key", "hash_function"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.85, 0.94]
}
```

#### 예시 4: 포스트 양자 알고리즘 (탐지 안됨)
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": [],
    "algorithm_categories": [],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.90, 0.98]
}
```

## ✅ 테스트 파일 검증 체크리스트

새로운 테스트 파일을 추가할 때 다음 체크리스트를 확인하세요:

### 파일 구조 검증
- [ ] 파일이 해당 에이전트 디렉토리에 올바르게 위치
- [ ] 파일명이 네이밍 컨벤션을 따름
- [ ] 파일 형식이 에이전트 타입에 적합 (언어, 형식 등)

### 내용 검증
- [ ] 암호 알고리즘명을 직접 사용하지 않음
- [ ] 우회적 네이밍과 구현 패턴 사용
- [ ] 최소 1개 이상의 양자 취약 알고리즘 포함
- [ ] 실제 컴파일/실행 가능한 수준의 코드 품질
- [ ] 현실적인 비즈니스 로직 컨텍스트

### Ground Truth 검증
- [ ] 대응하는 ground_truth JSON 파일 존재
- [ ] `vulnerable_algorithms_detected` 정확히 작성
- [ ] `algorithm_categories` 적절히 분류
- [ ] `korean_algorithms_detected` (해당 시) 포함
- [ ] `expected_confidence_range` 적절히 설정

### 알고리즘 지원 검증
- [ ] **중요**: `utils/metrics_calculator.py`에 사용된 알고리즘이 등록되어 있는지 확인
- [ ] 새로운 알고리즘 사용 시 metrics_calculator.py 업데이트
  - Line 61-108: `algorithm_variations` 추가
  - Line 122-130: `category_keywords` 추가
  - Line 146-154: `korean_variations` 추가 (한국 알고리즘인 경우)
  - Line 189-218: 필요 시 추가 매칭 로직

### 실행 검증
- [ ] 벤치마크 실행 시 JSON 파싱 오류 없음
- [ ] Ground truth와 실제 파일 내용이 일치
- [ ] LLM이 예상한 알고리즘을 탐지할 수 있을 만한 충분한 힌트 포함

## 🚀 새 테스트 파일 생성 프로세스

### Step 1: 요구사항 정의
```bash
# 어떤 알고리즘을 테스트할 것인가?
ALGORITHM="RSA + ECDSA 하이브리드"

# 어떤 에이전트에서 테스트할 것인가?
AGENT_TYPE="source_code"

# 어떤 언어/형식을 사용할 것인가?
FORMAT="Python"

# 난이도는?
DIFFICULTY="중간 - 비즈니스 로직으로 위장"
```

### Step 2: 파일 작성
```bash
# 1. 테스트 파일 생성
vim data/test_files/source_code/secure_messaging_system.py

# 2. Ground truth 파일 생성
vim data/ground_truth/source_code/secure_messaging_system.json
```

### Step 3: 알고리즘 지원 확인
```bash
# metrics_calculator.py에서 알고리즘 검색
grep -i "rsa" utils/metrics_calculator.py
grep -i "ecdsa" utils/metrics_calculator.py

# 없으면 추가 필요
```

### Step 4: 테스트 실행
```bash
# 단일 파일 테스트
python test_single_file.py \
  --file data/test_files/source_code/secure_messaging_system.py \
  --model gemini-2.0-flash-exp

# 결과 확인
cat results/source_code/secure_messaging_system_gemini-2.0-flash-exp.json
```

### Step 5: 검증
```bash
# Ground truth와 비교
python utils/result_analyzer.py \
  --result results/source_code/secure_messaging_system_gemini-2.0-flash-exp.json \
  --ground-truth data/ground_truth/source_code/secure_messaging_system.json
```

## 📚 참고 자료

### 알고리즘 분류 기준

#### Shor's Algorithm 취약 (공개키 암호)
- **원리**: 정수 인수분해, 이산대수 문제 양자 알고리즘으로 해결
- **대상**: RSA, DSA, DH, ElGamal, ECC (모든 변형), KCDSA
- **취약도**: 완전 파괴 (키 길이 무관)

#### Grover's Algorithm 취약 (대칭키/해시)
- **원리**: 검색 공간을 제곱근으로 축소
- **대상**: AES-128, 3DES, SEED, ARIA, SHA-256
- **취약도**: 보안 강도 절반 (128비트 → 64비트)

#### 고전 공격 취약
- **원리**: 이미 고전 컴퓨터로 취약
- **대상**: DES, RC4, MD5, SHA-1
- **취약도**: 현재도 안전하지 않음

### 포스트 양자 암호 (탐지 안됨)

양자 내성이 있어 탐지 대상이 **아닌** 알고리즘:
- **격자 기반**: Kyber, Dilithium, NTRU
- **해시 기반**: SPHINCS+
- **코드 기반**: Classic McEliece
- **다변수 다항식**: Rainbow, GeMSS

이러한 알고리즘이 포함된 파일은 `vulnerable_algorithms_detected`가 빈 배열이어야 합니다.

### MetricsCalculator 알고리즘 등록

새 알고리즘을 추가할 때는 `utils/metrics_calculator.py`의 다음 위치를 수정:

```python
# Line 61-108: 알고리즘 변형 정의
elif 'new_algorithm' in algorithm_lower:
    algorithm_variations = ['new_algorithm', 'new-algo', 'NEW_ALGO']

# Line 122-130: 카테고리 키워드 (필요시)
'custom_category': ['new_algorithm', 'related_keyword']

# Line 146-154: 한국 알고리즘 (해당시)
korean_variations = {
    'new_korean_algo': ['new_korean_algo', 'variant']
}
```

상세한 메트릭 계산 방법은 [METRICS.md](METRICS.md)를 참조하세요.

## 📊 현재 알고리즘 커버리지

### 지원되는 알고리즘 (metrics_calculator.py 등록됨)

#### 공개키 암호
- RSA (모든 변형)
- ECC, ECDSA, ECDH, Ed25519, X25519, Curve25519
- DSA, DH, ElGamal
- KCDSA, EC-KCDSA

#### 대칭키 암호
- AES (128/192/256)
- DES, 3DES
- RC4, RC2
- ChaCha20, Salsa20
- SEED, ARIA, HIGHT, LEA

#### 해시 함수
- MD5, MD4, MD2
- SHA-1, SHA-256, SHA-384, SHA-512
- HAS-160, LSH
- BLAKE2, SipHash

#### MAC
- HMAC (모든 변형)
- Poly1305

#### 포스트 양자 (탐지 제외)
- Kyber, Dilithium, SPHINCS+, NTRU

### 테스트 파일 분포

#### Source Code (80개)
- RSA 구현: 15개
- ECC/ECDSA: 12개
- 한국 알고리즘: 18개
- 하이브리드 시스템: 20개
- 기타: 15개

#### Assembly Binary (80개)
- 모듈러 연산: 15개
- 타원곡선 연산: 12개
- 블록 암호: 20개
- 해시 함수: 18개
- 기타: 15개

#### Dynamic Analysis (6개)
- Windows CryptoAPI: 2개
- OpenSSL 추적: 2개
- Java Crypto: 1개
- 혼합 시스템: 1개

#### Logs Config (17개)
- SSL/TLS 설정: 5개
- 시스템 로그: 4개
- 한국 암호 설정: 3개
- VPN/네트워크: 3개
- 기타: 2개

## 🔄 업데이트 이력

- **2024-01**: 초기 183개 테스트 파일 생성
- **2024-01**: SipHash, RC2 알고리즘 지원 추가
- **2024-01**: 한국 암호 알고리즘 확장 (KCDSA, LSH 등)
- **2024-01**: Ground truth 형식 표준화

---

더 자세한 평가 지표 및 점수 계산 방법은 [METRICS.md](METRICS.md)를 참조하세요.
