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
llm_analysis_benchmark/
├── agents/                          # 분석 에이전트
│   ├── source_code_agent.py        # 소스코드 분석
│   ├── assembly_agent.py           # 어셈블리/바이너리 분석
│   ├── dynamic_analysis_agent.py   # 동적 분석 데이터 처리
│   └── logs_config_agent.py        # 로그/설정 파일 분석
├── config/
│   └── config.yaml                 # 설정 파일 (LLM API, 알고리즘 목록)
├── data/
│   └── test_cases/                 # 테스트 케이스
│       ├── source_code/            # 소스코드 테스트 (5개)
│       ├── assembly_binary/        # 어셈블리 테스트 (5개)
│       ├── dynamic_analysis/       # 동적 분석 테스트 (5개)
│       └── logs_config/            # 로그/설정 테스트 (5개)
├── utils/
│   ├── llm_client.py              # LLM API 클라이언트
│   ├── metrics_calculator.py      # 성능 지표 계산
│   └── test_manager.py            # 테스트 케이스 관리
├── results/                        # 벤치마크 결과
│   ├── raw_results/               # 원시 결과 데이터
│   └── summary_reports/           # CSV 요약 보고서
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
python main.py --benchmark
```

### 특정 에이전트만 테스트

```bash
# 소스코드 에이전트만 테스트
python main.py --benchmark --agents source_code

# 여러 에이전트 테스트
python main.py --benchmark --agents source_code,assembly_binary
```

### 특정 LLM만 테스트

```bash
# OpenAI 모델만 테스트
python main.py --benchmark --llms openai

# 여러 LLM 테스트
python main.py --benchmark --llms openai,google
```

### 테스트 케이스 생성

```bash
# 새로운 테스트 케이스 생성
python main.py --generate-tests --count 10

# 특정 에이전트용 테스트 케이스 생성
python main.py --generate-tests --agent-type source_code --count 5
```

### 상세 옵션

```bash
python main.py --help
```

#### 주요 옵션들:

- `--benchmark`: 벤치마크 실행
- `--agents AGENTS`: 테스트할 에이전트 선택 (기본값: 모든 에이전트)
- `--llms LLMS`: 테스트할 LLM 선택 (기본값: 모든 LLM)
- `--output-dir DIR`: 결과 저장 디렉토리
- `--config CONFIG`: 설정 파일 경로
- `--verbose`: 상세 로그 출력
- `--generate-tests`: 테스트 케이스 생성
- `--validate-config`: 설정 파일 검증

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

## 🧪 테스트 케이스

각 에이전트별로 5개씩 총 20개의 테스트 케이스가 포함되어 있습니다:

### 소스코드 테스트
- RSA 취약한 구현 (PKCS#1 v1.5 패딩)
- 한국 SEED 암호 (난독화된 구현)
- ECC 양자 취약 곡선 (secp256r1, secp256k1)
- 한국 ARIA 암호 (위장된 S-box)
- 레거시 암호 혼합 (DES, 3DES, RC4, MD5, SHA-1)

### 어셈블리/바이너리 테스트
- RSA 모듈러 지수 연산
- 타원곡선 점 곱셈 및 ECDSA
- 한국 SEED 암호 어셈블리
- DES/3DES Feistel 구조
- DSA 서명 및 Diffie-Hellman

### 동적 분석 테스트
- RSA API 호출 추적
- 한국 암호 라이브러리 사용
- ECC 키 교환 패턴
- 레거시 해시 함수 사용
- RC4/DES 런타임 행동

### 로그/설정 테스트
- SSL 취약한 설정
- 한국 암호 정책 설정
- OpenSSL 암호 사용 로그
- Nginx TLS 설정
- 암호화 감사 로그

## 🔧 커스터마이제이션

### 새로운 알고리즘 추가

`config/config.yaml`에서 `vulnerable_algorithms` 섹션을 수정:

```yaml
vulnerable_algorithms:
  shor_vulnerable:
    - "NEW_ALGORITHM"
  korean_algorithms:
    - "NEW_KOREAN_ALGORITHM"
```

### 새로운 LLM 추가

`utils/llm_client.py`에서 새 LLM 클라이언트 구현 후 설정 파일에 추가:

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
4. `main.py`에서 에이전트 등록

## 📈 성능 최적화

### 병렬 처리

기본적으로 여러 LLM 요청을 병렬로 처리합니다:

```bash
python main.py --benchmark --parallel-requests 5
```

### 캐싱

동일한 입력에 대한 LLM 응답을 캐싱하여 중복 요청을 방지:

```bash
python main.py --benchmark --enable-cache
```

### 배치 처리

큰 데이터셋에 대해 배치 단위로 처리:

```bash
python main.py --benchmark --batch-size 10
```

## 🐛 문제 해결

### 일반적인 문제들

1. **API 키 오류**: `config/config.yaml`에서 올바른 API 키 설정 확인
2. **네트워크 오류**: 인터넷 연결 및 방화벽 설정 확인
3. **메모리 부족**: `--batch-size` 옵션으로 배치 크기 조정
4. **JSON 파싱 오류**: LLM 응답 형식 문제, `--retry-failed` 옵션 사용

### 로그 확인

```bash
# 상세 로그 출력
python main.py --benchmark --verbose

# 로그 파일 확인
tail -f logs/benchmark.log
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