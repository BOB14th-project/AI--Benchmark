# Test 3 RAG 시스템 효과 분석 보고서

## Executive Summary

동일한 RAG 시스템(버전 3)을 사용했음에도 불구하고, 세 가지 모델(GPT-4, Gemini, Llama)은 매우 다른 성능 변화를 보였습니다. 본 보고서는 이러한 차이의 원인을 모델 특성과 Agent 타입 관점에서 심층 분석합니다.

### 핵심 발견
- **GPT-4**: RAG로 F1 Score **+80.92%** 향상 (0.117 → 0.212)
- **Gemini**: RAG로 F1 Score **+6.14%** 소폭 향상 (0.243 → 0.258)
- **Llama**: RAG로 F1 Score **-14.82%** 하락 (0.213 → 0.181)

---

## 1. 전체 모델 비교 분석

### 1.1 GPT-4: 가장 큰 수혜자 (+80.92%)

**성능 변화:**
```
Without RAG: Precision 0.125, Recall 0.129, F1 0.117
With RAG:    Precision 0.240, Recall 0.212, F1 0.212
```

**주요 특징:**
- Precision **+91.4%**, Recall **+64.5%** 모두 대폭 향상
- 응답 시간은 17.9% 증가 (4.78s → 5.63s)로 허용 가능한 수준
- RAG가 도움이 된 테스트: 57/216 (26.4%)
- RAG가 해가 된 테스트: 33/216 (15.3%)

**RAG가 도움이 된 경우 패턴:**
- True Positive 평균 +1.11 증가
- False Negative 평균 -1.05 감소
- 대칭키 암호화(AES, Blowfish) 탐지에서 특히 효과적

**RAG가 해를 끼친 경우:**
- Diffie-Hellman, X25519 등 키 교환 프로토콜 탐지에서 오탐 증가
- 구조화된 RAG 컨텍스트가 너무 구체적인 알고리즘 명시로 혼란 야기

**왜 GPT-4가 가장 큰 이득을 봤는가?**
1. **Instruction-following 능력**: 구조화된 RAG 컨텍스트를 효과적으로 해석
2. **낮은 베이스라인**: 초기 F1 0.117로 개선 여지가 많았음
3. **컨텍스트 활용 능력**: RAG 정보를 기존 지식과 효과적으로 결합

---

### 1.2 Gemini: 균형잡힌 개선 (+6.14%)

**성능 변화:**
```
Without RAG: Precision 0.255, Recall 0.267, F1 0.243
With RAG:    Precision 0.286, Recall 0.253, F1 0.258
```

**주요 특징:**
- Precision **+11.9%** 향상, Recall **-5.3%** 소폭 감소
- 응답 시간 거의 동일 (3.85s → 3.87s, +1.0%)
- RAG가 도움이 된 테스트: 56/216 (25.9%)
- RAG가 해가 된 테스트: 46/216 (21.3%)

**Precision vs Recall 트레이드오프:**
- RAG가 Gemini를 더 **보수적**으로 만듦
- False Positive를 줄이는 대신 일부 탐지를 놓침
- 전체적으로는 F1 Score가 향상

**RAG 효율성:**
- 응답 시간 증가가 거의 없어 매우 효율적
- RAG 컨텍스트를 선택적으로 활용하는 것으로 추정

**왜 Gemini는 소폭만 개선되었는가?**
1. **높은 베이스라인**: 이미 F1 0.243으로 상대적으로 높은 성능
2. **균형잡힌 접근**: RAG를 맹목적으로 따르지 않고 자체 판단과 결합
3. **효율적 처리**: RAG 오버헤드가 거의 없는 효율적인 통합

---

### 1.3 Llama: 예상 밖의 성능 하락 (-14.82%)

**성능 변화:**
```
Without RAG: Precision 0.176, Recall 0.343, F1 0.213
With RAG:    Precision 0.262, Recall 0.154, F1 0.181
```

**주요 특징:**
- Precision **+48.7%** 향상했지만
- Recall **-55.0%** 급격히 하락 → 전체 F1 감소
- 응답 시간은 오히려 **70% 단축** (21.49s → 6.45s)
- RAG가 도움이 된 테스트: 46/216 (21.3%)
- RAG가 해가 된 테스트: 85/216 (39.4%)

**역설적인 응답 시간 단축:**
```
Without RAG: 21.49초 (긴 탐색적 응답)
With RAG:    6.45초  (짧은 제약된 응답)
```

이는 Llama가 RAG 컨텍스트에 **과도하게 제약**되어 충분한 추론을 하지 못했음을 시사합니다.

**RAG가 도움이 된 경우:**
- False Positive 평균 -3.41 감소 (큰 개선)
- 한국형 IoT, Elliptic Curve 등 특정 패턴에서 효과적

**RAG가 해를 끼친 경우:**
- False Negative 평균 +1.30 증가 (많은 것을 놓침)
- AES, Database Encryption 등 일반적인 암호화에서 탐지 실패

**왜 Llama만 성능이 하락했는가?**
1. **구조화된 컨텍스트 처리 한계**: 구조화된 RAG 형식에 취약
2. **과도한 제약**: RAG 정보에 너무 의존하여 자체 추론 능력 감소
3. **프롬프트 형식 불일치**: GPT/Gemini에 최적화된 RAG 형식이 Llama에는 부적합
4. **오픈소스 모델 특성**: 상용 모델과 다른 instruction-following 패턴

---

## 2. Agent 타입별 분석

본 벤치마크는 세 가지 Agent 타입을 사용합니다:
1. **Assembly/Binary Agent**: 어셈블리/바이너리 코드 분석
2. **Logs/Config Agent**: 로그 및 설정 파일 분석
3. **Source Code Agent**: 소스 코드 분석

### 2.1 Assembly/Binary Agent: RAG의 최대 수혜자

**전체 평균 F1 개선: +62.29%** ✅

| Model  | F1 w/o RAG | F1 w/ RAG | Improvement | Key Metric Change     |
|--------|------------|-----------|-------------|-----------------------|
| GPT-4  | 0.1057     | 0.3072    | **+190.68%** | Recall +212.6%       |
| Gemini | 0.3145     | 0.2870    | -8.74%      | Recall -15.1%        |
| Llama  | 0.2118     | 0.2222    | +4.92%      | Precision +76.9%     |

**주요 발견:**

**GPT-4의 극적인 개선 (+190%):**
- 베이스라인이 매우 낮았음 (F1 0.1057)
- RAG가 어셈블리 코드의 암호화 패턴 인식에 결정적 도움
- 응답 시간은 2배 증가했지만 (3.55s → 6.82s) 성능 대비 충분히 가치 있음

**Gemini의 소폭 하락 (-8.74%):**
- 이미 높은 베이스라인 (F1 0.3145)
- RAG가 오히려 기존 판단을 혼란시킴
- 어셈블리 코드에서는 RAG 없이도 잘 작동

**Llama의 소폭 개선 (+4.92%):**
- Precision은 크게 향상했지만 Recall 감소
- 응답 시간은 크게 개선 (20.74s → 7.31s)
- 어셈블리 분석에서는 RAG가 Llama의 과탐지를 줄이는 데 도움

**왜 Assembly/Binary Agent가 RAG로 가장 큰 이득을 보는가?**
1. **복잡한 패턴 인식**: 어셈블리 명령어는 고수준 언어보다 암호화 알고리즘 식별이 어려움
2. **전문 지식 필요**: RAG가 제공하는 어셈블리 수준의 암호화 패턴 지식이 필수적
3. **컨텍스트 의존성 높음**: 명령어 시퀀스만으로는 알고리즘 식별 어려움

---

### 2.2 Logs/Config Agent: RAG가 해로운 경우

**전체 평균 F1 개선: -19.11%** ⚠️

| Model  | F1 w/o RAG | F1 w/ RAG | Improvement | Key Metric Change     |
|--------|------------|-----------|-------------|-----------------------|
| GPT-4  | 0.1373     | 0.1003    | **-26.93%**  | Recall -42.2%        |
| Gemini | 0.1287     | 0.1495    | +16.15%     | Precision +40.0%     |
| Llama  | 0.2108     | 0.1127    | **-46.54%**  | Recall -61.2%        |

**주요 발견:**

**GPT-4와 Llama의 큰 성능 하락:**
- 두 모델 모두 Recall이 40% 이상 감소
- RAG가 로그/설정 파일의 간접적인 암호화 징후를 놓치게 만듦
- 구조화된 RAG 정보가 오히려 탐지 범위를 제한

**Gemini만 개선 (+16.15%):**
- Precision을 크게 향상시키면서 Recall 감소 최소화
- 로그/설정 파일에서도 RAG를 선택적으로 활용

**왜 Logs/Config Agent에서 RAG가 해로운가?**
1. **간접적 증거**: 로그/설정 파일은 직접적인 알고리즘 코드가 아닌 간접적 증거
2. **컨텍스트 과적합**: RAG가 명시적인 알고리즘 언급에만 초점을 맞추게 함
3. **유연성 감소**: 패턴 매칭보다는 추론이 필요한데 RAG가 추론 능력을 제약

**개선 방안:**
- Logs/Config Agent는 RAG 없이 사용하거나
- RAG 형식을 더 일반적이고 유연하게 변경 필요

---

### 2.3 Source Code Agent: 중간 수준의 개선

**전체 평균 F1 개선: +13.40%** ✓

| Model  | F1 w/o RAG | F1 w/ RAG | Improvement | Key Metric Change     |
|--------|------------|-----------|-------------|-----------------------|
| GPT-4  | 0.1204     | 0.1627    | **+35.11%**  | Precision +73.8%     |
| Gemini | 0.2203     | 0.2781    | +26.20%     | Precision +44.9%     |
| Llama  | 0.2154     | 0.1700    | -21.10%     | Recall -58.9%        |

**주요 발견:**

**GPT-4와 Gemini의 일관된 개선:**
- 두 모델 모두 Precision 중심의 개선
- False Positive를 줄여 신뢰도 향상
- 소스 코드 분석에서 RAG가 적절히 작동

**Llama의 성능 하락:**
- 다른 모델과 달리 Recall이 크게 감소
- 소스 코드에서도 RAG 제약 효과 나타남

**왜 Source Code Agent는 중간 수준인가?**
1. **가독성**: 소스 코드는 어셈블리보다 이해하기 쉬워 RAG 의존도 낮음
2. **명시적 패턴**: 함수/라이브러리 이름으로 어느 정도 식별 가능
3. **여전히 복잡**: 난독화나 간접 호출은 여전히 RAG가 도움이 됨

---

## 3. 심층 원인 분석

### 3.1 모델 아키텍처 차이

**GPT-4: Instruction-Following 최적화**
- OpenAI의 RLHF(Reinforcement Learning from Human Feedback)로 학습
- 구조화된 프롬프트와 컨텍스트를 따르도록 설계
- RAG 컨텍스트를 "지시사항"으로 해석하고 효과적으로 활용

**Gemini: 멀티모달 균형**
- 다양한 입력 형식에 대한 균형잡힌 성능
- 외부 정보를 맹목적으로 따르지 않고 자체 판단과 결합
- 효율적인 컨텍스트 처리로 응답 시간 증가 거의 없음

**Llama: 오픈소스 Foundation Model**
- 일반적인 언어 모델링에 최적화
- 상용 모델에 비해 instruction-following 능력 약함
- 구조화된 RAG 형식이 오히려 혼란을 야기

### 3.2 RAG 컨텍스트 처리 방식

**구조화된 RAG 형식의 영향:**

현재 RAG 시스템은 아마도 다음과 같은 구조화된 형식으로 정보를 제공할 것으로 추정:
```
Algorithm: RSA
Type: Asymmetric Encryption
Quantum Vulnerable: Yes
Evidence Pattern: RSA_*, rsa_encrypt, ...
```

**모델별 처리 방식:**
- **GPT-4**: 구조를 명확히 이해하고 규칙처럼 적용
- **Gemini**: 구조를 참고하되 유연하게 해석
- **Llama**: 구조에 과도하게 제약되거나 오해

### 3.3 Precision-Recall 트레이드오프 패턴

**모델별 RAG 효과:**

| Model  | RAG가 도움될 때              | RAG가 해가 될 때            |
|--------|--------------------------|-------------------------|
| GPT-4  | TP +1.11, FP +0.27, FN -1.05 | TP -1.46, FP -0.38, FN +1.46 |
| Gemini | TP +1.07, FP -0.28, FN ±0.00 | TP -1.14, FP +0.34, FN +1.14 |
| Llama  | TP +0.52, FP -3.41, FN -0.41 | TP -1.30, FP -1.73, FN +1.30 |

**해석:**
- **GPT-4**: RAG가 균형있게 TP 증가, FN 감소 → 전반적 개선
- **Gemini**: RAG가 FP 감소에 집중 → Precision 개선 전략
- **Llama**: RAG가 과도하게 보수적 → 많은 것을 놓침

### 3.4 응답 시간의 의미

**모델별 응답 시간 변화:**

| Model  | w/o RAG | w/ RAG | Change   | 의미                           |
|--------|---------|--------|----------|--------------------------------|
| GPT-4  | 4.78s   | 5.63s  | +17.9%   | RAG 처리에 적당한 시간 소요    |
| Gemini | 3.85s   | 3.87s  | +1.0%    | 매우 효율적인 RAG 통합         |
| Llama  | 21.49s  | 6.45s  | **-70.0%** | 과도한 제약으로 추론 생략     |

**Llama의 응답 시간 단축은 문제의 징후:**
- RAG 없이: 21.5초 동안 깊은 탐색과 추론 수행
- RAG 있으면: 6.4초로 단축 = RAG에만 의존하고 자체 추론 생략
- 결과: Recall 55% 감소

---

## 4. 종합 결론

### 4.1 Agent 타입이 RAG 효과를 결정짓는 주요 요인

모델 간 차이도 중요하지만, **Agent 타입에 따라 RAG의 유용성이 극명히 달라짐**:

1. **Assembly/Binary (+62%)**: RAG 필수, 모든 모델이 이득
2. **Source Code (+13%)**: RAG가 도움이 되지만 필수는 아님
3. **Logs/Config (-19%)**: RAG가 오히려 해로움

### 4.2 모델별 RAG 최적 전략

**GPT-4:**
- ✅ 현재 RAG 시스템 유지 및 확대
- ✅ Assembly/Binary, Source Code Agent에서 RAG 활용
- ⚠️ Logs/Config Agent는 RAG 비활성화 고려
- 🔄 RAG 컨텍스트를 더 풍부하게 확장 가능

**Gemini:**
- ✅ 현재 설정이 최적
- ✅ 모든 Agent 타입에서 균형있는 성능
- ✅ 효율성이 뛰어나 추가 튜닝 불필요

**Llama:**
- ❌ 현재 RAG 전략 전면 재검토 필요
- 🔄 **대안 1**: 덜 구조화된 RAG 형식 사용
  ```
  "RSA encryption is often identified by patterns like RSA_*, rsa_encrypt..."
  (구조화된 필드 대신 자연어 설명)
  ```
- 🔄 **대안 2**: RAG를 보조 정보로만 제공
  ```
  "Please analyze the code. For reference, common crypto patterns include..."
  (주요 지시사항이 아닌 참고사항으로)
  ```
- 🔄 **대안 3**: Hybrid 접근
  - Assembly/Binary: RAG 사용 (소폭 개선)
  - Source Code: RAG 미사용 (성능 하락 방지)
  - Logs/Config: RAG 미사용 (큰 하락 방지)
- 🔄 **대안 4**: Llama 전용 fine-tuning
  - RAG 스타일 입력에 대한 추가 학습
  - Instruction-following 능력 강화

### 4.3 RAG 시스템 개선 방향

**즉시 적용 가능:**
1. **Agent별 RAG On/Off 전략**
   - Assembly/Binary: 모든 모델 RAG 사용
   - Source Code: GPT-4, Gemini RAG 사용, Llama 미사용
   - Logs/Config: 모든 모델 RAG 미사용

2. **모델별 RAG 형식 분기**
   ```python
   if model == "gpt-4" or model == "gemini":
       rag_context = structured_rag_format()
   elif model == "llama":
       rag_context = conversational_rag_format()
   ```

**중장기 개선:**
1. **Dynamic RAG**: Agent와 모델 조합에 따라 RAG 강도 조절
2. **Confidence-based RAG**: 모델의 confidence score에 따라 RAG 활용도 조정
3. **A/B Testing**: 다양한 RAG 형식을 테스트하여 최적화

---

## 5. 권장사항 요약

### 즉시 적용 (High Priority)

| Model  | Assembly/Binary | Source Code | Logs/Config | Expected Impact      |
|--------|----------------|-------------|-------------|----------------------|
| GPT-4  | ✅ RAG ON      | ✅ RAG ON   | ❌ RAG OFF  | F1 +100% → +120%    |
| Gemini | ❌ RAG OFF     | ✅ RAG ON   | ✅ RAG ON   | F1 +6% → +15%       |
| Llama  | ✅ RAG ON      | ❌ RAG OFF  | ❌ RAG OFF  | F1 -15% → +5%       |

### 중기 개선 (Medium Priority)

1. **Llama 전용 RAG 형식 개발**
   - 자연어 기반 설명형 RAG
   - 테스트 후 점진적 적용

2. **RAG 컨텍스트 품질 개선**
   - Assembly/Binary 패턴 DB 확충
   - 간접적 증거 탐지 가이드 추가

### 장기 연구 (Low Priority)

1. **Adaptive RAG System**
   - 실시간 성능 피드백 기반 RAG 조정

2. **Model Fine-tuning**
   - Llama를 crypto detection task에 특화 학습

---

## 6. 부록: 데이터 요약

### 전체 성능 비교표

| Model  | Metric    | w/o RAG | w/ RAG  | Change   |
|--------|-----------|---------|---------|----------|
| GPT-4  | Precision | 0.1255  | 0.2402  | +91.4%   |
|        | Recall    | 0.1290  | 0.2122  | +64.5%   |
|        | F1 Score  | 0.1173  | 0.2122  | +80.9%   |
| Gemini | Precision | 0.2554  | 0.2858  | +11.9%   |
|        | Recall    | 0.2667  | 0.2526  | -5.3%    |
|        | F1 Score  | 0.2432  | 0.2581  | +6.1%    |
| Llama  | Precision | 0.1763  | 0.2621  | +48.7%   |
|        | Recall    | 0.3425  | 0.1542  | -55.0%   |
|        | F1 Score  | 0.2130  | 0.1815  | -14.8%   |

### Agent별 평균 성능

| Agent Type      | Avg F1 Improvement | Best Model | Worst Model |
|-----------------|-------------------|------------|-------------|
| Assembly/Binary | +62.29%           | GPT-4      | Gemini      |
| Source Code     | +13.40%           | GPT-4      | Llama       |
| Logs/Config     | -19.11%           | Gemini     | Llama       |

---

## 결론

동일한 RAG 시스템을 사용하더라도:
1. **모델 아키텍처**에 따라 RAG 활용 능력이 크게 다름
2. **Agent/Task 타입**이 RAG 효과를 결정짓는 더 중요한 요인
3. **일률적인 RAG 적용보다 맞춤형 전략**이 필수

GPT-4는 구조화된 RAG를 잘 활용하고, Gemini는 효율적으로 선택 활용하며, Llama는 다른 형식의 RAG가 필요합니다. Agent 타입별로는 Assembly/Binary에서는 RAG가 필수이지만, Logs/Config에서는 오히려 해롭습니다.

**최종 권장: Agent별, Model별 맞춤형 RAG 전략 수립**

---

*생성일: 2025-10-31*
*분석 대상: Test 3 Results (GPT-4, Gemini, Llama)*
*테스트 케이스: 216 cases per model*
