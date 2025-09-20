# LLM Analysis Benchmark: Quantum-Vulnerable Cryptography Detection

양자 내성이 없는 암호화 알고리즘 탐지를 위한 LLM 성능 벤치마킹 시스템입니다. 이 프로젝트는 다양한 LLM(ChatGPT, Gemini, Grok 등)이 소스코드, 어셈블리/바이너리, 동적 분석 데이터, 로그/설정 파일에서 취약한 암호화 알고리즘을 얼마나 잘 탐지하는지 평가합니다.

## 🎯 프로젝트 목표

- **4가지 분석 에이전트**의 성능 비교 (소스코드, 어셈블리/바이너리, 동적분석, 로그/설정)
- **다양한 LLM API** 테스트 (ChatGPT, Gemini, Grok 등)
- **정확도, 속도, JSON 응답 안정성** 자동 측정
- **한국 국산 알고리즘** 포함 (SEED, ARIA, HIGHT, LEA, KCDSA 등)
- **양자 컴퓨터 취약성** 분석 (Shor's, Grover's 알고리즘)

## 🔍 탐지 대상 알고리즘

### Shor's 알고리즘에 취약한 암호화
- **RSA** (1024, 2048, 4096-bit)
- **ECC/ECDSA/ECDH** (secp256r1, secp384r1, secp256k1 등)
- **DSA/DH** (Digital Signature Algorithm, Diffie-Hellman)
- **한국 공개키 알고리즘**: KCDSA, EC-KCDSA

### Grover's 알고리즘에 취약한 암호화
- **대칭키 암호**: AES-128, DES, 3DES, RC4
- **한국 대칭키 암호**: SEED-128, ARIA-128/256, HIGHT-128, LEA
- **해시 함수**: SHA-256 (보안 강도 감소)
- **한국 해시 함수**: HAS-160, LSH-256/512

### 기타 취약한 알고리즘
- **해시 함수**: MD5, SHA-1 (충돌 공격)
- **스트림 암호**: RC4 (편향된 키스트림)
- **패딩 방식**: PKCS#1 v1.5 (패딩 오라클 공격)

## 📁 프로젝트 구조

```
AI--Benchmark/
├── agents/                          # 분석 에이전트
│   ├── source_code_agent.py        # 소스코드 분석
│   ├── assembly_agent.py           # 어셈블리/바이너리 분석
│   ├── dynamic_analysis_agent.py   # 동적 분석 데이터 처리
│   └── logs_config_agent.py        # 로그/설정 파일 분석
├── clients/                         # LLM API 클라이언트
│   ├── openai_client.py            # OpenAI/ChatGPT
│   ├── google_client.py            # Google Gemini
│   ├── anthropic_client.py         # Anthropic Claude
│   └── xai_client.py               # xAI Grok
├── config/
│   └── config.yaml                 # 설정 파일 (LLM API, 알고리즘 목록)
├── data/
│   ├── test_files/                 # 실제 테스트 파일들 (새로운 구조!)
│   │   ├── source_code/            # .py, .c, .cpp, .java 등
│   │   ├── assembly_binary/        # .s, .asm, .bin 등
│   │   ├── dynamic_analysis/       # .json, .log, .trace 등
│   │   └── logs_config/            # .conf, .yaml, .log 등
│   └── ground_truth/               # 테스트 메타데이터 및 정답
│       ├── source_code/            # 소스코드 테스트 정답
│       ├── assembly_binary/        # 어셈블리 테스트 정답
│       ├── dynamic_analysis/       # 동적 분석 테스트 정답
│       └── logs_config/            # 로그/설정 테스트 정답
├── utils/
│   ├── test_case_manager.py        # 테스트 케이스 관리 (파일 기반)
│   └── metrics_calculator.py      # 성능 지표 계산
├── reports/                        # 결과 보고서 생성
│   └── csv_generator.py           # CSV 보고서
├── results/                        # 벤치마크 결과
├── benchmark.py                    # 벤치마크 엔진
├── main.py                        # 메인 실행 스크립트
└── README.md                      # 프로젝트 문서
```

## ⚙️ 설치 및 설정

### 1. 필요한 패키지 설치

```bash
pip install openai google-generativeai anthropic requests pyyaml pandas numpy
```

### 2. API 키 설정

`config/config.yaml` 파일에서 사용할 LLM의 API 키를 설정하세요:

```yaml
llm_providers:
  openai:
    api_key: "your-openai-api-key"
    models: ["gpt-4", "gpt-3.5-turbo"]

  google:
    api_key: "your-google-api-key"
    models: ["gemini-pro", "gemini-pro-vision"]

  anthropic:
    api_key: "your-anthropic-api-key"
    models: ["claude-3-sonnet", "claude-3-haiku"]
```

### 3. 환경 변수 설정 (선택사항)

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 🚀 실행 방법

### 기본 벤치마크 실행

```bash
python main.py
```

### 특정 LLM Provider만 테스트

```bash
# OpenAI만 테스트
python main.py --providers openai

# 여러 Provider 테스트
python main.py --providers openai google anthropic
```

### 특정 에이전트만 테스트

```bash
# 소스코드 에이전트만 테스트
python main.py --agents source_code

# 여러 에이전트 테스트
python main.py --agents source_code assembly_binary
```

### 테스트 케이스 관리

```bash
# 취약한 암호화 테스트 케이스 생성
python main.py --generate-vulnerable-test-cases

# 레거시 JSON 테스트를 파일 기반으로 마이그레이션
python main.py --migrate-to-file-based

# 테스트 케이스 통계 확인
python main.py --test-cases-stats
```

### 정보 확인

```bash
# 사용 가능한 LLM Provider 목록
python main.py --list-providers

# 사용 가능한 분석 에이전트 목록
python main.py --list-agents

# 취약한 알고리즘 목록
python main.py --vulnerable-algorithms

# 한국 국산 알고리즘 목록
python main.py --korean-algorithms
```

### 상세 옵션

```bash
python main.py --help
```

#### 주요 옵션들:

- `--providers PROVIDERS`: 테스트할 LLM provider 선택
- `--agents AGENTS`: 테스트할 에이전트 선택 (source_code, assembly_binary, dynamic_analysis, logs_config)
- `--workers N`: 병렬 처리 워커 수 (기본값: 4)
- `--output-dir DIR`: 결과 저장 디렉토리 (기본값: results)
- `--config CONFIG`: 설정 파일 경로 (기본값: config/config.yaml)
- `--csv-only`: CSV 보고서만 생성
- `--generate-vulnerable-test-cases`: 취약한 암호화 테스트 케이스 생성
- `--migrate-to-file-based`: 레거시 JSON을 파일 기반 구조로 마이그레이션
- `--test-cases-stats`: 테스트 케이스 통계 출력

## 📊 결과 분석

### CSV 요약 보고서

벤치마크 실행 후 `results/summary_reports/` 디렉토리에 다음 파일들이 생성됩니다:

- `summary_YYYYMMDD_HHMMSS.csv`: 전체 성능 요약
- `detailed_results_YYYYMMDD_HHMMSS.csv`: 상세 결과
- `korean_algorithms_YYYYMMDD_HHMMSS.csv`: 한국 알고리즘 탐지 성능

### 성능 지표

1. **정확도 (Accuracy)**: 전체 알고리즘 탐지 정확도
2. **한국 알고리즘 정확도**: 한국 국산 알고리즘 탐지 정확도
3. **응답 시간**: LLM 응답 속도
4. **JSON 안정성**: 올바른 JSON 형식 응답 비율
5. **False Positive Rate**: 오탐지율
6. **False Negative Rate**: 미탐지율

### 결과 예시

```csv
LLM,Model,Agent,Accuracy,Korean_Accuracy,Avg_Response_Time,JSON_Stability,FP_Rate,FN_Rate
openai,gpt-4,source_code,0.92,0.88,3.2,0.98,0.05,0.08
google,gemini-pro,assembly_binary,0.85,0.82,2.8,0.95,0.08,0.15
```

## 🧪 테스트 케이스 (파일 기반 구조)

새로운 파일 기반 구조로 각 에이전트별 테스트 케이스를 관리합니다:

### 📁 data/test_files/ 구조

#### source_code/ - 소스코드 테스트 파일
- `test_rsa_vulnerable.py`: RSA 취약한 구현 (1024-bit, PKCS#1 v1.5 패딩, SHA-1)
- `test_korean_seed.c`: 한국 SEED 암호 (난독화된 C 구현)
- `test_ecc_vulnerable.cpp`: ECC 양자 취약 곡선 (secp256r1, secp256k1)
- `test_korean_aria.py`: 한국 ARIA 암호 (위장된 S-box 구현)
- `test_legacy_crypto_mix.java`: 레거시 암호 혼합 (DES, 3DES, RC4, MD5, SHA-1)

#### assembly_binary/ - 어셈블리/바이너리 테스트 파일
- `test_rsa_modexp.s`: RSA 모듈러 지수 연산 어셈블리
- `test_ecc_point_mul.bin`: 타원곡선 점 곱셈 및 ECDSA 바이너리
- `test_korean_seed.s`: 한국 SEED 암호 어셈블리
- `test_des_3des.asm`: DES/3DES Feistel 구조 어셈블리
- `test_dsa_dh.bin`: DSA 서명 및 Diffie-Hellman 바이너리

#### dynamic_analysis/ - 동적 분석 테스트 파일
- `test_rsa_api_calls.json`: RSA API 호출 추적 데이터
- `test_korean_crypto_libs.log`: 한국 암호 라이브러리 사용 로그
- `test_ecc_key_exchange.json`: ECC 키 교환 패턴 분석
- `test_legacy_hash_usage.trace`: 레거시 해시 함수 사용 추적
- `test_rc4_des_runtime.log`: RC4/DES 런타임 행동 분석

#### logs_config/ - 로그/설정 테스트 파일
- `test_ssl_config_vulnerable.conf`: Apache SSL 취약한 설정
- `test_korean_crypto_config.yml`: 한국 암호 정책 설정
- `test_openssl_cipher_logs.log`: OpenSSL 암호 사용 로그
- `test_nginx_tls_config.conf`: Nginx TLS 설정
- `test_crypto_audit_logs.log`: 암호화 감사 로그

### 📁 data/ground_truth/ 구조

각 테스트 파일에 대응하는 정답 파일이 JSON 형태로 저장:
- 예상 탐지 알고리즘 목록
- 알고리즘 카테고리 (shor_vulnerable, grover_vulnerable 등)
- 한국 알고리즘 정보
- 난이도 및 태그 정보
- 평가 기준 및 성능 지표

## ✨ 새로운 기능 (v2.0)

### 🗂️ 파일 기반 테스트 구조
- **실제 파일 형태**로 테스트 케이스 저장 (.py, .c, .conf, .log 등)
- **자동 파일 타입 감지** 및 적절한 확장자 할당
- **바이너리 파일 지원** (hex 형태로 저장/로드)
- **레거시 JSON 호환성** 유지

### 🔄 마이그레이션 도구
```bash
# 기존 JSON 테스트를 파일 기반으로 자동 변환
python main.py --migrate-to-file-based
```

### 📊 향상된 테스트 관리
```bash
# 테스트 케이스 통계 및 커버리지 확인
python main.py --test-cases-stats

# 다양한 정보 확인 옵션들
python main.py --list-providers
python main.py --list-agents
python main.py --vulnerable-algorithms
python main.py --korean-algorithms
```

## 🔧 커스터마이제이션

### 새로운 테스트 파일 추가

1. **테스트 파일 생성**: `data/test_files/[agent_type]/`에 실제 파일 저장
2. **Ground Truth 생성**: `data/ground_truth/[agent_type]/`에 JSON 메타데이터 저장

```json
{
  "description": "테스트 케이스 설명",
  "file_extension": ".py",
  "format": "file_based",
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA-1024", "SHA-1"],
    "algorithm_categories": ["shor_vulnerable", "grover_vulnerable"],
    "korean_algorithms_detected": []
  },
  "difficulty": "medium",
  "tags": ["rsa", "vulnerable-crypto"]
}
```

### 새로운 알고리즘 추가

`config/config.yaml`에서 `vulnerable_algorithms` 섹션을 수정:

```yaml
vulnerable_algorithms:
  shor_vulnerable:
    - "NEW_ALGORITHM"
  korean_algorithms:
    - "NEW_KOREAN_ALGORITHM"
```

### 새로운 LLM Provider 추가

`clients/` 디렉토리에 새 클라이언트 구현 후 설정 파일에 추가:

```yaml
llm_providers:
  new_provider:
    api_key: "api-key"
    models: ["model-name"]
    base_url: "https://api.example.com"
```

### 새로운 에이전트 추가

1. `agents/` 디렉토리에 새 에이전트 파일 생성
2. `BaseAgent` 클래스 상속
3. `analyze()` 메서드 구현
4. Factory 패턴으로 등록

## 📈 성능 최적화

### 병렬 처리

기본적으로 여러 LLM 요청을 병렬로 처리합니다:

```bash
# 워커 수 조정 (기본값: 4)
python main.py --workers 8
```

### 출력 최적화

```bash
# CSV 보고서만 생성 (JSON 생략으로 속도 향상)
python main.py --csv-only

# 특정 출력 디렉토리 지정
python main.py --output-dir custom_results
```

### 테스트 범위 제한

```bash
# 특정 Provider와 Agent만 테스트하여 시간 단축
python main.py --providers openai --agents source_code
```

## 🐛 문제 해결

### 일반적인 문제들

1. **API 키 오류**: `config/config.yaml`에서 올바른 API 키 설정 확인
2. **네트워크 오류**: 인터넷 연결 및 방화벽 설정 확인
3. **테스트 케이스 오류**: `python main.py --test-cases-stats`로 상태 확인
4. **파일 인코딩 문제**: UTF-8 인코딩 자동 처리, 바이너리 파일은 hex 변환

### 로그 확인

```bash
# 벤치마크 로그 확인
tail -f benchmark.log

# Provider 상태 확인
python main.py --list-providers
```

### 마이그레이션 문제

```bash
# 레거시 JSON에서 파일 기반으로 마이그레이션 재실행
python main.py --migrate-to-file-based

# 마이그레이션 후 통계 확인
python main.py --test-cases-stats
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-algorithm`)
3. Commit your changes (`git commit -am 'Add new quantum-vulnerable algorithm'`)
4. Push to the branch (`git push origin feature/new-algorithm`)
5. Create a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 📞 연락처

- 이슈 리포트: GitHub Issues
- 기능 요청: GitHub Discussions
- 보안 문제: 비공개 이메일로 연락

## 🙏 감사의 말

- KISA (한국인터넷진흥원) - 한국 암호 표준 정보 제공
- NIST - 양자 내성 암호 연구 자료
- OpenAI, Google, Anthropic - LLM API 제공

---

**주의사항**: 이 도구는 교육 및 연구 목적으로만 사용하세요. 실제 보안 시스템에서는 전문가의 검토를 받은 후 사용하시기 바랍니다.