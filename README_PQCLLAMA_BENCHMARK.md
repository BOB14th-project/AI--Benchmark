# PQCllama vs Llama3.1 Benchmark Guide

## 📋 개요

이 벤치마크는 **PQC 특화 파인튜닝 모델**과 **일반 Llama 모델**의 성능을 비교합니다:

- **PQCllama**: HuggingFace의 `sangwoohahn/PQCllama` (PQC 취약점 탐지에 특화)
- **Llama3.1 8B**: Ollama를 통한 일반 Llama 모델

## 🚀 설치 및 설정

### 1. 필수 패키지 설치

```bash
pip install transformers torch accelerate sentencepiece
```

### 2. Ollama 설치 및 Llama3.1 다운로드

```bash
# Ollama가 설치되어 있지 않다면
brew install ollama  # macOS

# Llama3.1 8B 모델 다운로드
ollama pull llama3.1:8b

# Ollama 서버 실행 (다른 터미널에서)
ollama serve
```

### 3. PQCllama 모델 다운로드 및 테스트

```bash
python setup_pqcllama.py
```

이 스크립트는:
- HuggingFace에서 PQCllama 모델 다운로드 (~8-16GB)
- 모델을 `./models/pqcllama` 디렉토리에 캐시
- 간단한 테스트로 모델이 정상 작동하는지 확인

## 🧪 벤치마크 실행

### 기본 실행 (50개 테스트)

```bash
python benchmark_pqcllama_vs_llama3.py
```

### 전체 테스트 실행

벤치마크 스크립트를 수정하여 `TEST_LIMIT = None`으로 설정:

```python
# benchmark_pqcllama_vs_llama3.py 파일 수정
TEST_LIMIT = None  # 모든 테스트 실행
```

### RAG 포함 테스트

```python
# benchmark_pqcllama_vs_llama3.py 파일 수정
WITH_RAG = True
```

## 📊 결과 분석

결과는 `results/pqcllama_vs_llama3_[timestamp].json`에 저장됩니다.

### 결과 시각화

```bash
python visualize_pqcllama_comparison.py results/pqcllama_vs_llama3_*.json
```

## 📁 파일 구조

```
AI--Benchmark/
├── setup_pqcllama.py                    # PQCllama 다운로드 및 테스트
├── benchmark_pqcllama_vs_llama3.py      # 벤치마크 실행
├── visualize_pqcllama_comparison.py     # 결과 시각화
├── models/
│   └── pqcllama/                        # PQCllama 모델 캐시
├── test_cases/                          # 테스트 케이스
└── results/
    └── pqcllama_vs_llama3_*.json        # 벤치마크 결과
```

## 🎯 비교 지표

### 1. 정확도 지표
- **Precision**: 탐지된 알고리즘 중 정확한 비율
- **Recall**: 실제 알고리즘 중 탐지된 비율
- **F1-Score**: Precision과 Recall의 조화 평균

### 2. 성능 지표
- **Response Time**: 응답 생성 시간
- **JSON Validity**: 올바른 JSON 형식 출력 비율

### 3. 탐지 품질
- **True Positives (TP)**: 정확히 탐지한 알고리즘
- **False Positives (FP)**: 잘못 탐지한 알고리즘
- **False Negatives (FN)**: 놓친 알고리즘

## 🔍 예상 결과

### PQCllama (파인튜닝 모델)
- ✅ **PQC 취약점 탐지**: 높은 정확도 예상
- ✅ **전문 용어**: PQC 관련 용어를 정확히 이해
- ✅ **권장사항**: PQC 표준(CRYSTALS-Kyber, Dilithium 등)을 제시
- ⚠️ **일반 암호**: 전통적 암호 알고리즘 탐지는 베이스 모델과 비슷할 수 있음

### Llama3.1 8B (베이스 모델)
- ⚠️ **일반적 지식**: 기본적인 암호화 알고리즘은 알지만 PQC 특화 지식 부족
- ⚠️ **양자 위협**: 양자 컴퓨팅의 위협을 제대로 이해하지 못할 수 있음
- ⚠️ **권장사항**: 구체적인 PQC 대안을 제시하지 못할 가능성

## ⚙️ 설정 옵션

### GPU vs CPU

GPU가 있으면 자동으로 사용됩니다:
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

CPU만 있는 경우 속도가 느릴 수 있습니다.

### 메모리 최적화

메모리 부족 시:
```python
# benchmark_pqcllama_vs_llama3.py에서
torch_dtype=torch.float16  # 또는 torch.bfloat16
low_cpu_mem_usage=True
```

### 테스트 수 조절

```python
TEST_LIMIT = 10   # 빠른 테스트
TEST_LIMIT = 50   # 기본값
TEST_LIMIT = None # 전체 테스트
```

## 🐛 문제 해결

### 1. PQCllama 다운로드 실패

```bash
# HuggingFace 토큰이 필요한 경우
huggingface-cli login

# 또는 환경 변수로 설정
export HF_TOKEN=your_token_here
```

### 2. Ollama 연결 실패

```bash
# Ollama 서버가 실행 중인지 확인
ps aux | grep ollama

# Ollama 재시작
killall ollama
ollama serve
```

### 3. 메모리 부족 (OOM)

```bash
# 테스트 수 줄이기
TEST_LIMIT = 10

# 또는 배치 크기 조절
# 한 번에 하나씩 처리하도록 이미 설정됨
```

### 4. CUDA Out of Memory

```python
# CPU 사용으로 변경
device = "cpu"

# 또는 더 작은 정밀도 사용
torch_dtype=torch.float16
```

## 📈 결과 해석 예시

```json
{
  "PQCllama": {
    "Precision": 85.3%,
    "Recall": 78.2%,
    "F1-Score": 81.6%,
    "Avg Response Time": 8.5s
  },
  "Llama3.1": {
    "Precision": 22.4%,
    "Recall": 25.1%,
    "F1-Score": 23.7%,
    "Avg Response Time": 13.6s
  }
}
```

**해석**:
- PQCllama가 **3.4배 높은 F1-Score** → 파인튜닝 효과 명확
- PQCllama가 **1.6배 빠름** → 특화 학습으로 더 효율적
- 일반 Llama는 PQC 탐지에 매우 취약

## 🎓 참고사항

- **PQCllama**: Post-Quantum Cryptography에 특화된 파인튜닝 모델
- **기대 효과**: PQC 취약점 탐지에서 일반 모델 대비 **3-5배 성능 향상** 예상
- **한계**: 전통적 암호 알고리즘 탐지는 큰 차이 없을 수 있음

## 📞 문의

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.8 이상 권장)
2. CUDA 버전 (GPU 사용 시)
3. 디스크 공간 (최소 20GB 여유 공간)
4. 메모리 (최소 16GB RAM 권장)
