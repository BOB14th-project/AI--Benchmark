# 평가 메트릭 및 점수 계산

AI 벤치마크 시스템의 성능 평가 메트릭과 점수 계산 방법에 대한 상세 문서입니다.

## 목차
- [개요](#개요)
- [핵심 메트릭](#핵심-메트릭)
- [점수 계산 상세](#점수-계산-상세)
- [집계 메트릭](#집계-메트릭)
- [계산 예시](#계산-예시)

---

## 개요

본 벤치마크 시스템은 양자 취약 암호 알고리즘 탐지 성능을 다각도로 평가하기 위해 여러 메트릭을 사용합니다. 모든 메트릭은 `utils/metrics_calculator.py`에 구현되어 있습니다.

### 평가 철학

1. **탐지 정확도 우선**: 양자 취약 알고리즘을 얼마나 정확히 탐지하는가
2. **거짓 양성/음성 최소화**: 잘못된 탐지를 최소화
3. **한국 암호 알고리즘 특별 평가**: SEED, ARIA 등 국산 암호 탐지 보너스
4. **실용성 고려**: 응답 시간, 토큰 효율성 등 실무 적용 가능성

---

## 핵심 메트릭

### 1. 탐지 정확도 (Detection Accuracy)

양자 취약 알고리즘을 정확히 탐지한 비율입니다.

**계산 공식:**
```python
accuracy = found_algorithms / total_expected_algorithms
```

**구현 위치:** `_calculate_vulnerable_algorithm_accuracy()` (라인 62-195)

**특징:**
- 알고리즘 이름의 다양한 변형을 인식 (예: `rsa`, `RSA-2048`, `rsa_2048`)
- 83개 이상의 암호 알고리즘 지원
- 대소문자 무시, 하이픈/언더스코어 무시

**예시:**
```json
{
  "expected": ["RSA", "ECDSA", "SHA-256"],
  "detected": ["rsa", "ecdsa", "sha256"],
  "accuracy": 1.0  // 3/3 = 100%
}
```

---

### 2. 정밀도 (Precision)

탐지된 것 중에서 실제로 양자 취약 알고리즘인 비율입니다.

**계산 공식:**
```
Precision = TP / (TP + FP)
```

여기서:
- **TP (True Positive)**: 정확히 탐지된 양자 취약 알고리즘
- **FP (False Positive)**: 잘못 탐지된 알고리즘 (양자 안전한데 취약하다고 판단)

**의미:**
- 높은 Precision = 탐지한 것은 대부분 맞음 (신뢰도 높음)
- 낮은 Precision = 오탐이 많음 (신뢰할 수 없음)

**실무 영향:**
- **높은 FP**: 불필요한 마이그레이션 작업, 비용 낭비
- **낮은 FP**: 신뢰할 수 있는 탐지, 효율적인 리소스 사용

---

### 3. 재현율 (Recall)

실제 양자 취약 알고리즘 중에서 탐지된 비율입니다.

**계산 공식:**
```
Recall = TP / (TP + FN)
```

여기서:
- **FN (False Negative)**: 놓친 양자 취약 알고리즘 (취약한데 안전하다고 판단)

**의미:**
- 높은 Recall = 대부분의 취약점을 찾아냄 (포괄적)
- 낮은 Recall = 많은 취약점을 놓침 (위험함)

**실무 영향:**
- **높은 FN**: 보안 위험! 양자 공격에 취약한 알고리즘이 남아있음
- **낮은 FN**: 안전한 마이그레이션, 대부분의 취약점 해결

---

### 4. F1 점수 (F1 Score)

Precision과 Recall의 조화평균으로, 균형잡힌 성능을 나타냅니다.

**계산 공식:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**특징:**
- 0.0 (최악) ~ 1.0 (최고)
- Precision과 Recall 둘 다 높아야 높은 F1 달성
- 한쪽만 높으면 F1은 낮게 나옴

**예시:**
```
Case 1: Precision=0.9, Recall=0.9 → F1=0.90 (매우 좋음)
Case 2: Precision=1.0, Recall=0.5 → F1=0.67 (Recall 낮음)
Case 3: Precision=0.5, Recall=1.0 → F1=0.67 (Precision 낮음)
Case 4: Precision=0.6, Recall=0.6 → F1=0.60 (둘 다 보통)
```

**우리 벤치마크의 F1 해석:**
- **F1 ≥ 0.85**: 실무 적용 가능, 높은 신뢰도
- **F1 0.70-0.85**: 보조 도구로 사용 가능, 수동 검증 필요
- **F1 0.50-0.70**: 참고용, 많은 검증 필요
- **F1 < 0.50**: 실용성 낮음

---

### 5. 거짓 양성률 (False Positive Rate)

**계산 위치:** `calculate_false_positive_rate()` (라인 339-363)

```
FPR = FP / (FP + TN)
```

**구현 특징:**
- 양자 내성 알고리즘(Kyber, SPHINCS 등)을 취약하다고 잘못 판단하는 비율
- 83개 알고리즘 키워드로 검사
- 낮을수록 좋음 (0에 가까울수록)

---

### 6. 거짓 음성률 (False Negative Rate)

**계산 위치:** `calculate_false_negative_rate()` (라인 366-475)

```
FNR = FN / (FN + TP)
```

**구현 특징:**
- 실제 양자 취약 알고리즘을 놓치는 비율
- 알고리즘별 변형(variations) 체크
- 낮을수록 좋음 (0에 가까울수록)

---

### 7. 응답 시간 점수 (Response Time Score)

**계산 위치:** `calculate_response_time_score()` (라인 289-295)

**계산 로직:**
```python
if response_time <= baseline:         # 기준(10초) 이내
    score = 1.0
elif response_time <= baseline * 2:   # 기준의 2배 이내 (20초)
    score = 1.0 - (response_time - baseline) / baseline
else:                                  # 20초 초과
    score = 0.1
```

**예시:**
- 5초: 1.0 (최고)
- 10초: 1.0 (기준)
- 15초: 0.5 (기준의 1.5배)
- 20초: 0.0 (기준의 2배)
- 30초: 0.1 (매우 느림)

---

### 8. JSON 안정성 점수 (JSON Stability Score)

**계산 위치:** `calculate_json_stability_score()` (라인 298-310)

**계산 로직:**
```python
score = 0.0
if has_analysis_results: score += 0.6
if has_confidence:       score += 0.2
if has_summary:          score += 0.2
```

**요구사항:**
- `analysis_results`: 분석 결과 (60%)
- `confidence_score`: 신뢰도 점수 (20%)
- `summary`: 요약 정보 (20%)

---

## 점수 계산 상세

### 종합 정확도 점수 계산

**계산 위치:** `calculate_accuracy()` (라인 8-59)

**가중치 구조:**
```python
total_score = 0.0

# 1. 양자 취약 알고리즘 탐지 (70% 가중치)
vulnerable_accuracy = _calculate_vulnerable_algorithm_accuracy(...)
total_score += vulnerable_accuracy * 0.7

# 2. 알고리즘 카테고리 탐지 (20% 가중치)
category_accuracy = _calculate_category_accuracy(...)
total_score += category_accuracy * 0.2

# 3. 신뢰도 점수 검증 (10% 가중치)
if expected_min <= confidence <= expected_max:
    confidence_validity = 1.0
else:
    confidence_validity = max(0.0, 1.0 - min_diff)
total_score += confidence_validity * 0.1

# 4. 한국 알고리즘 보너스 (최대 5% 추가)
korean_accuracy = _calculate_korean_algorithm_accuracy(...)
total_score += korean_accuracy * 0.05  # 보너스

final_accuracy = total_score / 1.0  # 최대 1.05까지 가능
```

**왜 이런 가중치?**
- **70% (양자 취약 알고리즘)**: 핵심 목표, 가장 중요
- **20% (카테고리)**: 알고리즘 유형 이해도 평가
- **10% (신뢰도)**: 모델의 자신감 평가
- **5% (한국 알고리즘)**: 국산 암호 탐지 장려

---

### 카테고리 정확도 계산

**계산 위치:** `_calculate_category_accuracy()` (라인 198-233)

**지원 카테고리:**
```python
category_keywords = {
    'shor_vulnerable': [
        'rsa', 'ecc', 'dh', 'dsa', 'ecdsa', 'kcdsa', 'bls',
        'paillier', 'bgn', 'x25519', 'ed25519', 'secp256k1',
        'ecdh', 'feldman'
    ],
    'grover_vulnerable': [
        'aes', 'des', 'md5', 'sha', 'sha256', '3des', 'tea',
        'salsa20', 'chacha20', 'poly1305', 'hmac', 'crc32',
        'seed', 'aria', 'hight', 'lea', 'blake2', 'ghash',
        'siphash', 'pbkdf2', 'gcm', 'ripemd', 'scrypt',
        'keccak', 'shake', 'shamir'
    ],
    'classical_vulnerable': [
        'a5', 'trivium', 'rc4', 'rc2', 'crc32', 'md5', 'sha1'
    ],
    'public_key': [
        'rsa', 'ecc', 'dh', 'dsa', 'ecdsa', 'kcdsa', 'bls',
        'pss', 'paillier', 'bgn', 'x25519', 'ed25519',
        'secp256k1', 'ecdh'
    ],
    'symmetric_key': [
        'aes', 'des', '3des', 'tea', 'salsa20', 'chacha20',
        'seed', 'aria', 'hight', 'lea', 'xchacha20', 'rc2', 'rc4'
    ],
    'hash_function': [
        'md5', 'sha', 'sha256', 'sha1', 'hmac', 'crc32',
        'has-160', 'blake2', 'blake2b', 'ghash', 'ripemd',
        'keccak', 'shake', 'siphash'
    ],
    'mac': ['hmac', 'poly1305', 'ghash', 'siphash'],
    'korean_algorithms': [
        'seed', 'aria', 'hight', 'lea', 'kcdsa',
        'has-160', 'lsh', 'ec-kcdsa'
    ],
    'post_quantum': ['kyber', 'dilithium', 'sphincs', 'ntru']
}
```

---

### 한국 알고리즘 정확도 계산

**계산 위치:** `_calculate_korean_algorithm_accuracy()` (라인 236-264)

**지원 한국 알고리즘:**
```python
korean_variations = {
    'seed': ['seed'],
    'aria': ['aria'],
    'hight': ['hight'],
    'lea': ['lea'],
    'kcdsa': ['kcdsa', 'ec-kcdsa'],
    'has-160': ['has-160', 'has160'],
    'lsh': ['lsh'],
    'ec-kcdsa': ['ec-kcdsa', 'eckcdsa']
}
```

---

## 집계 메트릭

### 전체 벤치마크 결과 집계

**계산 위치:** `aggregate_metrics()` (라인 478-507)

**집계 항목:**
```python
{
    'total_tests': 총 테스트 수,
    'successful_tests': 성공한 테스트 수,
    'success_rate': 성공률,

    # 평균 메트릭
    'average_vulnerable_crypto_detection_accuracy': 평균 탐지 정확도,
    'average_response_time': 평균 응답 시간,
    'average_json_stability': 평균 JSON 안정성,
    'average_completeness': 평균 완전성,
    'average_false_positive_rate': 평균 거짓양성률,
    'average_false_negative_rate': 평균 거짓음성률,

    # 최소/최대
    'min_response_time': 최소 응답 시간,
    'max_response_time': 최대 응답 시간,

    # 유도 메트릭
    'vulnerable_crypto_detection_precision': 1.0 - 평균FPR,
    'vulnerable_crypto_detection_recall': 1.0 - 평균FNR,

    'timestamp': 타임스탬프
}
```

---

## 계산 예시

### 예시 1: 완벽한 탐지

**Ground Truth:**
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "ECDSA", "SHA-256"],
    "algorithm_categories": ["shor_vulnerable", "hash_function"],
    "korean_algorithms_detected": []
  },
  "expected_confidence_range": [0.8, 0.95]
}
```

**모델 응답:**
```json
{
  "valid_json": true,
  "confidence_score": 0.9,
  "analysis_results": {
    "detected_algorithms": ["RSA-2048", "ECDSA-P256", "SHA-256"],
    "categories": ["shor_vulnerable", "hash_function"]
  }
}
```

**계산:**
```
1. 양자 취약 알고리즘 탐지: 3/3 = 1.0
   → 0.7 점 (70% 가중치)

2. 카테고리 탐지: 2/2 = 1.0
   → 0.2 점 (20% 가중치)

3. 신뢰도: 0.9 ∈ [0.8, 0.95] → 1.0
   → 0.1 점 (10% 가중치)

4. 한국 알고리즘: 0/0 = 1.0 (해당없음)
   → 0.0 점 (보너스)

총점: 0.7 + 0.2 + 0.1 = 1.0 (100%)

Precision: 3/(3+0) = 1.0
Recall: 3/(3+0) = 1.0
F1 Score: 2×(1.0×1.0)/(1.0+1.0) = 1.0
```

---

### 예시 2: 부분 탐지

**Ground Truth:**
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["RSA", "ECDSA", "DH", "SHA-1"],
    "algorithm_categories": ["shor_vulnerable", "public_key"],
    "korean_algorithms_detected": []
  }
}
```

**모델 응답:**
```json
{
  "analysis_results": {
    "detected_algorithms": ["RSA", "ECDSA"],
    "categories": ["shor_vulnerable"]
  }
}
```

**계산:**
```
1. 양자 취약 알고리즘: 2/4 = 0.5
   → 0.35 점

2. 카테고리: 1/2 = 0.5
   → 0.1 점

3. 신뢰도: (검사 안됨)
   → 0.05 점 (부분 점수)

총점: 0.35 + 0.1 + 0.05 = 0.5 (50%)

True Positive: 2 (RSA, ECDSA)
False Negative: 2 (DH, SHA-1 놓침)
False Positive: 0

Precision: 2/(2+0) = 1.0 (탐지한 건 다 맞음)
Recall: 2/(2+2) = 0.5 (절반만 찾음)
F1 Score: 2×(1.0×0.5)/(1.0+0.5) = 0.67
```

---

### 예시 3: 한국 알고리즘 보너스

**Ground Truth:**
```json
{
  "expected_findings": {
    "vulnerable_algorithms_detected": ["SEED", "ARIA", "KCDSA"],
    "korean_algorithms_detected": ["SEED", "ARIA", "KCDSA"]
  }
}
```

**모델 응답:**
```json
{
  "analysis_results": {
    "detected": ["SEED-128-CBC", "ARIA-256-CTR", "KCDSA"]
  }
}
```

**계산:**
```
1. 양자 취약 알고리즘: 3/3 = 1.0
   → 0.7 점

2. 카테고리: (검사 안됨)
   → 0.1 점 (부분)

3. 한국 알고리즘: 3/3 = 1.0
   → 0.05 점 (보너스!)

총점: 0.7 + 0.1 + 0.05 = 0.85 (85%)
```

---

## 구현 코드 예시

### 1. 기본 정확도 계산

```python
from utils.metrics_calculator import MetricsCalculator

ground_truth = {
    "expected_findings": {
        "vulnerable_algorithms_detected": ["RSA", "ECDSA"],
        "algorithm_categories": ["shor_vulnerable"],
        "korean_algorithms_detected": []
    },
    "expected_confidence_range": [0.8, 0.95]
}

actual_response = {
    "valid_json": True,
    "confidence_score": 0.85,
    "analysis_results": {
        "algorithms": ["RSA-2048", "ECDSA-P256"],
        "category": "public_key_crypto"
    }
}

accuracy = MetricsCalculator.calculate_accuracy(
    actual_response,
    ground_truth
)
print(f"Accuracy: {accuracy:.2%}")  # 예: Accuracy: 87.50%
```

### 2. F1 점수 계산

```python
# FPR과 FNR로부터 계산
fpr = MetricsCalculator.calculate_false_positive_rate(
    actual_response, ground_truth
)
fnr = MetricsCalculator.calculate_false_negative_rate(
    actual_response, ground_truth
)

precision = 1.0 - fpr
recall = 1.0 - fnr

if precision + recall > 0:
    f1_score = 2 * (precision * recall) / (precision + recall)
else:
    f1_score = 0.0

print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1_score:.2%}")
```

### 3. 집계 메트릭

```python
results = [
    {"success": True, "accuracy_score": 0.85, "response_time": 10.5},
    {"success": True, "accuracy_score": 0.90, "response_time": 8.2},
    {"success": False, "accuracy_score": 0.0, "response_time": 30.0},
]

aggregated = MetricsCalculator.aggregate_metrics(results)
print(f"Success Rate: {aggregated['success_rate']:.2%}")
print(f"Avg Accuracy: {aggregated['average_vulnerable_crypto_detection_accuracy']:.2%}")
print(f"Avg Response Time: {aggregated['average_response_time']:.1f}s")
```

---

## 메트릭 해석 가이드

### F1 점수별 해석

| F1 범위 | 등급 | 해석 | 권장 사항 |
|---------|------|------|-----------|
| 0.90-1.00 | S | 탁월함 | 실무 적용 적극 권장 |
| 0.85-0.90 | A | 우수함 | 실무 적용 가능 |
| 0.75-0.85 | B | 양호함 | 보조 도구로 활용 |
| 0.65-0.75 | C | 보통 | 참고용, 검증 필수 |
| 0.50-0.65 | D | 미흡함 | 개선 필요 |
| <0.50 | F | 불합격 | 실용성 없음 |

### Precision vs Recall 트레이드오프

| 상황 | Precision | Recall | 의미 | 대응 |
|------|-----------|--------|------|------|
| 보수적 탐지 | 높음 | 낮음 | 확실한 것만 탐지 | Recall 개선 필요 |
| 공격적 탐지 | 낮음 | 높음 | 의심되면 모두 탐지 | Precision 개선 필요 |
| 이상적 | 높음 | 높음 | 균형잡힌 탐지 | 유지 |
| 문제 있음 | 낮음 | 낮음 | 제대로 못 찾음 | 전면 재검토 |

---

## 참고사항

### 알고리즘 매칭 로직

모든 알고리즘 탐지는 대소문자 무시, 하이픈/언더스코어 무시로 매칭됩니다:

```
"RSA" = "rsa" = "RSA-2048" = "rsa_2048" = "RSA2048"
"ECDSA" = "ecdsa" = "EC-DSA" = "ec_dsa"
"SEED" = "seed" = "SEED-128" = "seed_cbc"
```

### Ground Truth 작성 시 주의사항

1. **알고리즘 이름은 간단히**: `"RSA-2048"` 대신 `"RSA"`
2. **카테고리는 정확히**: `"shor_vulnerable"` (지원 카테고리 확인)
3. **신뢰도 범위는 현실적으로**: 대부분 `[0.7, 0.95]`
4. **한국 알고리즘은 명시적으로**: 있으면 반드시 포함

---

**문서 업데이트**: 2025-01-01
**구현 파일**: `utils/metrics_calculator.py`
**관련 문서**: [TEST_FILES.md](TEST_FILES.md), [README.md](../README.md)
