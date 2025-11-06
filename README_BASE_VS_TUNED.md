# Base vs PQC-Tuned Llama 벤치마크 가이드

## 📋 개요

**Base Llama 3.1-8B-Instruct**와 **PQC-tuned Llama** (LoRA fine-tuned)를
기존 벤치마킹 시스템으로 비교합니다.

- **테스트 대상**: Assembly/Binary 파일만
- **비교 모델**:
  - Base: `meta-llama/Meta-Llama-3.1-8B-Instruct` (일반 모델)
  - Tuned: `sangwoohahn/PQCllama` (PQC 특화 파인튜닝)

---

## 🚀 빠른 시작

### 1️⃣ HuggingFace 로그인 (필수)

```bash
# HuggingFace CLI 로그인
huggingface-cli login
# 토큰 입력: hf_xxxxx...

# Llama 3.1 접근 권한 요청
# https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
# "Request Access" 클릭
```

### 2️⃣ 패키지 설치

```bash
pip install peft accelerate
```

### 3️⃣ 벤치마크 실행

```bash
python benchmark_base_vs_tuned_binary.py
```

---

## 📊 어떤 것을 측정하나?

### 테스트 데이터
- **위치**: `data/test_files/assembly_binary/`
- **파일 형식**: Assembly 코드 (`.s` 파일)
- **예시**:
  - `aes_key_expansion_module.s`
  - `rsa_signature_verification.s`
  - `aria_encryption_engine.s`

### 평가 지표

1. **Precision** (정밀도)
   - 탐지한 알고리즘 중 맞춘 비율
   - `TP / (TP + FP)`

2. **Recall** (재현율)
   - 실제 알고리즘 중 찾은 비율
   - `TP / (TP + FN)`

3. **F1-Score** (조화 평균)
   - Precision과 Recall의 균형
   - `2 * (Precision * Recall) / (Precision + Recall)`

4. **Response Time** (응답 시간)
   - 모델이 답변을 생성하는 데 걸린 시간

---

## 🎯 예상 결과

### Base Model (일반 Llama 3.1)
```
Precision: 20-30%
Recall: 20-30%
F1-Score: ~25%
Response Time: ~15-20초
```

### PQC-Tuned Model (파인튜닝)
```
Precision: 60-80% (예상)
Recall: 60-80% (예상)
F1-Score: ~70% (예상)
Response Time: ~15-20초
```

### 개선율
```
예상 개선: +180% (약 2.8배)
```

---

## ⚙️ 설정 옵션

### 테스트 수 제한

```python
# benchmark_base_vs_tuned_binary.py 수정

# 전체 테스트
TEST_LIMIT = None

# 10개만 테스트 (빠른 테스트)
TEST_LIMIT = 10

# 50개 테스트
TEST_LIMIT = 50
```

### 메모리 최적화

Apple M2 24GB에서는 기본 설정으로 충분하지만,
메모리 부족 시:

```python
# benchmark_base_vs_tuned_binary.py에서
torch_dtype=torch.float16  # 이미 설정됨

# 또는 INT8 양자화 (메모리 절약)
load_in_8bit=True
```

---

## 📁 결과 파일

결과는 `results/` 디렉토리에 저장됩니다:

```
results/base_vs_tuned_binary_20250106_123456.json
```

### 결과 구조

```json
{
  "benchmark_info": {
    "timestamp": "2025-01-06T12:34:56",
    "base_model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "tuned_model": "sangwoohahn/PQCllama",
    "test_type": "assembly_binary",
    "total_tests": 152
  },
  "base_results": [
    {
      "test_id": "aes_key_expansion",
      "true_positives": 1,
      "false_positives": 2,
      "false_negatives": 1,
      "response_time": 15.3,
      "detected_algorithms": ["AES", "RSA", "DES"]
    }
  ],
  "tuned_results": [...]
}
```

---

## 📈 결과 시각화

결과를 시각화하려면:

```bash
python visualize_base_vs_tuned.py results/base_vs_tuned_binary_*.json
```

생성되는 그래프:
1. **F1-Score 비교** (막대 그래프)
2. **Precision/Recall 비교** (산점도)
3. **응답 시간 비교** (박스 플롯)
4. **알고리즘별 성능** (히트맵)

---

## ⏱️ 예상 소요 시간

### Apple M2 24GB 기준

| 테스트 수 | 예상 시간 | 권장 |
|----------|----------|------|
| 10개 | ~6분 | 빠른 테스트 ✅ |
| 50개 | ~30분 | 샘플 테스트 ✅ |
| 전체 (~150개) | ~1.5시간 | 전체 벤치마크 |

**참고**: 각 모델이 순차적으로 실행됩니다.
- Base model: 각 테스트 ~15-20초
- Tuned model: 각 테스트 ~15-20초
- 총: ~30-40초 per test

---

## 🔍 상세 분석

### 1. TP/FP/FN 분석

```python
# 결과 파일 로드
import json
with open('results/base_vs_tuned_binary_xxx.json') as f:
    data = json.load(f)

# Base model 분석
base_tp = sum(r['true_positives'] for r in data['base_results'])
base_fp = sum(r['false_positives'] for r in data['base_results'])
base_fn = sum(r['false_negatives'] for r in data['base_results'])

print(f"Base - TP: {base_tp}, FP: {base_fp}, FN: {base_fn}")

# Tuned model 분석
tuned_tp = sum(r['true_positives'] for r in data['tuned_results'])
tuned_fp = sum(r['false_positives'] for r in data['tuned_results'])
tuned_fn = sum(r['false_negatives'] for r in data['tuned_results'])

print(f"Tuned - TP: {tuned_tp}, FP: {tuned_fp}, FN: {tuned_fn}")
```

### 2. 알고리즘별 비교

```python
from collections import defaultdict

# 알고리즘별 성공률
base_alg_success = defaultdict(lambda: {'correct': 0, 'total': 0})

for result in data['base_results']:
    expected = set(result['expected_algorithms'])
    detected = set(result['detected_algorithms'])

    for alg in expected:
        base_alg_success[alg]['total'] += 1
        if alg in detected:
            base_alg_success[alg]['correct'] += 1

# 출력
for alg, stats in sorted(base_alg_success.items()):
    acc = stats['correct'] / stats['total'] * 100
    print(f"{alg}: {acc:.1f}% ({stats['correct']}/{stats['total']})")
```

---

## 🐛 문제 해결

### 1. "401 Unauthorized" 오류

```bash
# HuggingFace 로그인 확인
huggingface-cli whoami

# 재로그인
huggingface-cli login

# Llama 3.1 접근 권한 확인
# https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
```

### 2. "Out of Memory" 오류

```python
# TEST_LIMIT 줄이기
TEST_LIMIT = 10

# 또는 모델을 순차적으로 실행
# (이미 순차 실행이지만, 한 번에 하나씩만)
```

### 3. "PEFT module not found"

```bash
pip install peft
```

### 4. 느린 실행 속도

```python
# 프롬프트 길이 줄이기 (이미 3000자로 제한됨)
# 또는 max_new_tokens 줄이기
max_new_tokens=1000  # 기본 2000
```

---

## 📝 체크리스트

실행 전 확인:

- [ ] HuggingFace 로그인 완료
- [ ] Llama 3.1 접근 권한 승인됨
- [ ] `peft`, `accelerate` 설치됨
- [ ] 디스크 여유 공간 20GB 이상
- [ ] RAM 24GB 이상 (또는 양자화 설정)
- [ ] `data/test_files/assembly_binary/` 존재

---

## 🎓 예상 발견사항

### Base Model 약점
- RSA, DSA, DH 같은 일반 알고리즘은 탐지
- **PQC 특화 알고리즘** (CRYSTALS, NTRU 등) 탐지 실패
- 한국 표준 (SEED, ARIA, HIGHT) 탐지 낮음
- 양자 위협에 대한 이해 부족

### Tuned Model 강점
- PQC 취약 알고리즘 정확히 식별
- 양자 컴퓨팅 위협을 정확히 설명
- CRYSTALS-Kyber, Dilithium 같은 대안 제시
- 한국 표준 알고리즘도 더 잘 인식

---

## 🚀 다음 단계

벤치마크 완료 후:

1. **결과 분석**
   ```bash
   python analyze_results.py results/base_vs_tuned_binary_*.json
   ```

2. **시각화**
   ```bash
   python visualize_base_vs_tuned.py results/base_vs_tuned_binary_*.json
   ```

3. **보고서 생성**
   ```bash
   python generate_report.py results/base_vs_tuned_binary_*.json
   ```

---

## 📞 참고

- **스크립트**: `benchmark_base_vs_tuned_binary.py`
- **데이터**: `data/test_files/assembly_binary/`
- **결과**: `results/base_vs_tuned_binary_*.json`
- **로그인 가이드**: `HUGGINGFACE_LOGIN_GUIDE.md`
