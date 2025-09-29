# AI Benchmark for Quantum-Vulnerable Cryptography Detection

양자 취약 암호 알고리즘 탐지를 위한 AI 모델 성능 평가 벤치마크 시스템

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)]()

## 🎯 프로젝트 개요

포스트 양자 암호(Post-Quantum Cryptography) 전환을 대비하여 기존 시스템의 양자 취약 암호 알고리즘을 탐지하는 AI 모델들의 성능을 종합적으로 평가하는 벤치마크 시스템입니다.

### 주요 특징

- **다중 AI 모델 지원**: 상용 API 3개 + 로컬 Ollama 모델 3개
- **4가지 분석 도메인**: 소스코드, 어셈블리/바이너리, 동적분석, 로그/설정
- **한국 국산 암호**: SEED, ARIA, HIGHT, LEA, KCDSA 등 특화 탐지
- **종합 성능 분석**: 정확도, 속도, 토큰 효율성 등 다각도 평가

## 🧪 지원 모델

### 상용 API 모델
| 프로바이더 | 모델 | 특징 |
|-----------|------|------|
| **Google** | `gemini-2.0-flash-exp` | 높은 정확도, 상세한 분석 |
| **OpenAI** | `gpt-4.1` | 균형잡힌 성능 |
| **xAI** | `grok-3-mini` | 빠른 응답, 경량화 |

### 로컬 Ollama 모델
| 모델 | 크기 | 특징 |
|------|------|------|
| **LLaMA 3** | `llama3:8b` | 범용 성능, 로컬 실행 |
| **Qwen 3** | `qwen3:8b` | 멀티모달 특화 |
| **Code Llama** | `codellama:7b` | 코드 분석 최적화 |

## 📊 분석 에이전트

### 🔍 Source Code Agent
- **대상**: Python, Java, C/C++, JavaScript 소스 코드
- **탐지**: RSA, ECC, DH, DSA, 한국 암호 알고리즘
- **특화**: 코드 패턴 분석, 라이브러리 사용 탐지

### ⚙️ Assembly Binary Agent
- **대상**: 어셈블리 코드, 바이너리 덤프
- **탐지**: 모듈러 지수 연산, 타원곡선 연산, 큰 정수 연산
- **특화**: 컴파일된 코드의 암호 연산 시그니처 분석

### 📈 Dynamic Analysis Agent
- **대상**: 런타임 데이터, API 호출 로그
- **탐지**: 암호화 API 사용 패턴, 메모리 할당
- **특화**: 실행 시 행동 분석, 성능 특성 기반 탐지

### 📋 Logs Config Agent
- **대상**: 설정 파일, 시스템 로그
- **탐지**: SSL/TLS 설정, 인증서 구성
- **특화**: 간접적 암호 사용 증거 수집

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/AI--Benchmark.git
cd AI--Benchmark

# 의존성 설치
pip install -r requirements.txt

# Ollama 설치 (macOS)
brew install ollama

# Ollama 모델 다운로드
ollama pull llama3:8b
ollama pull qwen3:8b
ollama pull codellama:7b

# Ollama 서버 실행
ollama serve
```

### 2. API 키 설정

`config/config.yaml` 파일에 API 키를 설정하세요:

```yaml
llm_providers:
  google:
    api_key: "your_google_api_key_here"
    model: "gemini-2.0-flash-exp"

  openai:
    api_key: "your_openai_api_key_here"
    model: "gpt-4.1"

  xai:
    api_key: "your_xai_api_key_here"
    model: "grok-3-mini"
```

### 3. 시스템 테스트

```bash
# 전체 시스템 테스트
python test_benchmark_system.py

# 예상 출력:
# 🧪 AI 벤치마크 시스템 테스트
# ============================================================
# 🔧 설정 로더 테스트...
#   ✅ google 설정 완료
#   ✅ 설정 로더 정상 작동
# 🤖 Ollama 연결 테스트...
#   ✅ Ollama 서버 연결됨
#   📋 사용 가능한 모델: ['llama3:8b', 'codellama:7b', 'qwen3:8b']
```

## 📋 사용법

### 전체 벤치마크 실행

```bash
# 모든 모델로 소규모 테스트 (에이전트당 3개 파일)
python benchmark_runner.py --limit 3

# 특정 프로바이더만 테스트
python benchmark_runner.py --providers google ollama --limit 5

# 특정 에이전트만 테스트
python benchmark_runner.py --agents source_code assembly_binary --limit 2

# 병렬 실행 (빠른 처리)
python benchmark_runner.py --parallel --limit 3
```

### 결과 분석

```bash
# 모든 분석 실행
python analyze_results.py results/benchmark_results_*.json --all

# 모델별 성능 비교
python analyze_results.py results/benchmark_results_*.json --compare-models

# 시각화 생성
python analyze_results.py results/benchmark_results_*.json --visualize
```

### 단일 파일 테스트

```bash
# 특정 파일로 빠른 테스트
python test_single_file.py
```

## 📈 성능 지표

### 평가 메트릭
- **탐지 정확도**: 실제 취약점 대비 정확 탐지율
- **정밀도/재현율**: 거짓양성/거짓음성 최소화
- **F1 점수**: 정밀도와 재현율의 조화평균
- **응답 시간**: API 호출 속도
- **토큰 효율성**: 비용 대비 성능
- **JSON 유효성**: 구조화된 출력 생성 능력

### 예상 성능 (F1 점수 기준)

| 모델 | 예상 성능 | 응답 시간 | 특징 |
|------|-----------|-----------|------|
| gemini-2.0-flash-exp | 0.85-0.90 | 10-15초 | 최고 정확도 |
| gpt-4.1 | 0.80-0.85 | 8-12초 | 균형잡힌 성능 |
| grok-3-mini | 0.75-0.80 | 5-8초 | 빠른 응답 |
| llama3:8b | 0.70-0.75 | 3-5초 | 로컬 실행, 빠름 |
| qwen3:8b | 0.65-0.70 | 4-6초 | 멀티모달 특화 |
| codellama:7b | 0.60-0.65 | 2-4초 | 코드 분석 최적화 |

## 📁 프로젝트 구조

```
AI--Benchmark/
├── 📋 README.md                 # 이 파일
├── ⚙️ benchmark_runner.py       # 메인 벤치마크 실행기
├── 📊 analyze_results.py        # 결과 분석 도구
├── 🧪 test_benchmark_system.py  # 시스템 테스트
├── 📄 requirements.txt          # 의존성 목록
├── 📁 docs/                     # 문서들
│   └── CLAUDE.md               # 상세 문서
├── 🔧 config/                   # 설정 파일들
│   ├── config.yaml             # 메인 설정 파일
│   └── config_loader.py        # 설정 로더
├── 🤖 agents/                   # 분석 에이전트들
│   ├── base_agent.py           # 기본 에이전트
│   ├── source_code_agent.py    # 소스코드 분석
│   ├── assembly_agent.py       # 어셈블리 분석
│   ├── dynamic_analysis_agent.py # 동적 분석
│   ├── logs_config_agent.py    # 로그/설정 분석
│   └── agent_factory.py        # 에이전트 팩토리
├── 🌐 clients/                  # LLM API 클라이언트들
│   ├── base_client.py          # 기본 클라이언트
│   ├── google_client.py        # Google Gemini
│   ├── openai_client.py        # OpenAI GPT
│   ├── xai_client.py           # xAI Grok
│   ├── ollama_client.py        # Ollama 로컬
│   └── client_factory.py       # 클라이언트 팩토리
├── 📂 data/                     # 테스트 데이터
│   ├── test_files/             # 실제 테스트 파일들
│   │   ├── source_code/        # 소스코드 샘플 (28개)
│   │   ├── assembly_binary/    # 어셈블리 샘플 (17개)
│   │   ├── dynamic_analysis/   # 동적분석 데이터 (1개)
│   │   └── logs_config/        # 로그/설정 (5개)
│   └── ground_truth/           # 정답 데이터
├── 🛠️ utils/                    # 유틸리티
│   └── test_case_manager.py    # 테스트 케이스 관리
├── 📜 scripts/                  # 추가 스크립트들
│   ├── test_single_file.py     # 단일 파일 테스트
│   ├── test_available_models.py # 모델 가용성 확인
│   └── (기타 개발/테스트 스크립트)
├── 📊 results/                  # 결과 파일들 (JSON + CSV)
└── 📋 reports/                  # 분석 리포트들
```

## 🔍 탐지 대상 암호 알고리즘

### 양자 취약 공개키 암호
- **RSA**: 1024, 2048, 3072, 4096비트
- **ECC**: secp256r1, secp384r1, secp521r1
- **DH/DSA**: 1024, 2048, 3072비트
- **ElGamal**: 이산로그 기반

### 한국 국산 암호 알고리즘
- **대칭키**: SEED, ARIA, HIGHT, LEA
- **공개키**: KCDSA, EC-KCDSA
- **해시**: HAS-160, LSH

### Grover 알고리즘 취약 대칭키
- **블록암호**: AES-128, 3DES, DES, RC4
- **해시함수**: MD5, SHA-1, SHA-256

## 📊 예제 결과

```bash
$ python benchmark_runner.py --limit 2

🚀 벤치마크 시작
============================================================
✅ Ollama 사용 가능한 모델: ['llama3:8b', 'codellama:7b']
📁 source_code: 2개 테스트 파일 로드됨
📁 assembly_binary: 2개 테스트 파일 로드됨
📊 총 12개 테스트 조합

📋 테스트 1/12: google/gemini-2.0-flash-exp/source_code
    파일: rsa_public_key_system
    ✅ 완료 (13.2초)
    🎯 신뢰도: 0.850
    🔍 취약점: 8개

📋 테스트 2/12: ollama/llama3:8b/source_code
    파일: rsa_public_key_system
    ✅ 완료 (4.1초)
    🎯 신뢰도: 0.720
    🔍 취약점: 6개

============================================================
📊 벤치마크 결과 요약
============================================================
전체 테스트: 12
성공: 11
성공률: 91.7%

🏆 프로바이더별 성능:
  google:
    성공률: 100.0%
    평균 응답시간: 12.34초
    평균 신뢰도: 0.863
    평균 취약점 탐지: 7.8개

  ollama:
    성공률: 87.5%
    평균 응답시간: 3.91초
    평균 신뢰도: 0.701
    평균 취약점 탐지: 5.2개
```

## 🛠️ 문제 해결

### API 연결 문제
```bash
# Google API 키 확인
python -c "from config.config_loader import ConfigLoader; print(ConfigLoader().get_llm_config('google'))"

# Ollama 서버 상태 확인
curl http://localhost:11434/api/tags
```

### Ollama 설정
```bash
# Ollama 서버 시작
ollama serve

# 모델 다운로드 확인
ollama list

# 필요시 모델 재다운로드
ollama pull llama3:8b
```

### 메모리 부족 시
```bash
# 배치 크기 줄이기
python benchmark_runner.py --limit 1

# 특정 에이전트만 테스트
python benchmark_runner.py --agents source_code --limit 3
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **프로젝트 링크**: [https://github.com/your-username/AI--Benchmark](https://github.com/your-username/AI--Benchmark)
- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/AI--Benchmark/issues)

## 🙏 감사의 말

- OpenAI, Google, xAI의 API 제공
- Ollama 팀의 로컬 LLM 실행 환경
- 오픈소스 암호화 라이브러리 커뮤니티

---

**⚠️ 주의사항**: 이 도구는 연구 및 교육 목적으로 설계되었습니다. 실제 보안 감사에 사용하기 전에 충분한 검증이 필요합니다.