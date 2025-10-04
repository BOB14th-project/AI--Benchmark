# 응답시간 분석 가이드

## 개요

`visualize_response_time.py`는 각 에이전트별로 모델의 평균 응답시간을 비교 분석하는 전용 도구입니다.

## 핵심 결과 요약

### ⚡ 에이전트별 가장 빠른 모델

| 에이전트 | 가장 빠른 모델 | 평균 응답시간 | 가장 느린 모델 | 속도 차이 |
|---------|---------------|--------------|---------------|----------|
| **assembly_binary** | google/gemini-2.0-flash-exp | 4.04초 | ollama/qwen3:8b (58.66초) | **14.5배** |
| **logs_config** | google/gemini-2.0-flash-exp | 6.48초 | openai/gpt-4.1 (28.30초) | **4.4배** |
| **source_code** | google/gemini-2.0-flash-exp | 3.85초 | ollama/qwen3:8b (57.67초) | **15.0배** |

### 🏆 전체 모델 응답시간 순위 (모든 에이전트 통합)

1. **google/gemini-2.0-flash-exp**: 4.53초 (±1.55) ✨ 압도적 1위
2. **xai/grok-3-mini**: 12.28초 (±3.59)
3. **openai/gpt-4.1**: 14.26초 (±9.71)
4. **ollama/llama3:8b**: 23.99초 (±3.22)
5. **ollama/qwen3:8b**: 61.54초 (±11.96)

**핵심 인사이트:**
- **Gemini**는 모든 에이전트에서 **압도적으로 가장 빠름** (2~3배 차이)
- **Qwen3**는 가장 느림 (Gemini 대비 약 13~15배 느림)
- **GPT-4.1**은 성능은 최고지만 속도는 중간 수준
- **LLaMA3**는 로컬 모델 중 준수한 속도

## 사용 방법

### 1. 요약 정보만 보기 (권장)

```bash
python visualize_response_time.py benchmark_results.json --summary
```

**출력 예시:**
```
⚡ 에이전트별 모델 응답시간 요약

🎯 assembly_binary
  ⚡ 가장 빠른 모델: google/gemini-2.0-flash-exp
     - 평균: 4.04초 (±0.61)
     - 중앙값: 3.89초
     - 범위: 3.16~6.07초

  전체 모델 순위 (평균 응답시간 기준):
    1. google/gemini-2.0-flash-exp: 4.04s (±0.61)
    2. openai/gpt-4.1: 10.36s (±4.48)
    ...
```

### 2. 모든 응답시간 그래프 생성

```bash
python visualize_response_time.py benchmark_results.json --all
```

생성되는 파일:
- `agent_response_time_comparison.png` - 평균 응답시간 비교 (막대 그래프)
- `agent_response_time_heatmap.png` - 응답시간 히트맵
- `agent_response_time_boxplot.png` - 응답시간 분포 (박스플롯)

### 3. 특정 그래프만 생성

```bash
# 비교 막대 그래프만
python visualize_response_time.py benchmark_results.json --comparison

# 히트맵만
python visualize_response_time.py benchmark_results.json --heatmap

# 박스플롯만
python visualize_response_time.py benchmark_results.json --boxplot
```

### 4. 최소 테스트 수 조정

```bash
# 최소 30개 테스트 이상인 모델만
python visualize_response_time.py benchmark_results.json --all --min-tests 30
```

## 생성되는 그래프 설명

### 1. 응답시간 비교 막대 그래프
- **파일명**: `agent_response_time_comparison.png`
- **내용**: 에이전트별 모델 평균 응답시간을 막대로 표시
- **특징**:
  - 에러바(표준편차) 포함
  - 색상 그라데이션 (녹색=빠름, 빨간색=느림)
  - 막대 안에 테스트 수 표시
  - 막대 위에 평균 시간 표시
- **용도**: 에이전트별 모델 속도 비교

### 2. 응답시간 히트맵
- **파일명**: `agent_response_time_heatmap.png`
- **내용**: 에이전트(행) × 모델(열) 응답시간을 색상으로 표시
- **색상**: 녹색(빠름) → 노란색(보통) → 빨간색(느림)
- **용도**: 한눈에 가장 빠른 조합 파악

### 3. 응답시간 박스플롯
- **파일명**: `agent_response_time_boxplot.png`
- **내용**: 에이전트별 모델 응답시간 분포
- **구성**:
  - 박스: 25~75 백분위수
  - 선: 중앙값
  - 점선: 평균값
  - 수염: 최소~최대 범위
- **용도**: 응답시간 안정성 및 이상치 파악

## 실전 활용 예시

### 시나리오 1: 실시간 처리 시스템
**요구사항**: 응답시간 5초 이내

**추천**:
- 모든 에이전트: **google/gemini-2.0-flash-exp**
  - assembly_binary: 4.04초 ✅
  - logs_config: 6.48초 ⚠️ (약간 초과, 허용 가능)
  - source_code: 3.85초 ✅

### 시나리오 2: 배치 처리 시스템
**요구사항**: 대량 파일 처리, 시간 제약 없음

**추천**:
- 성능 우선: **openai/gpt-4.1** (14.26초)
- 비용 절감: **ollama/llama3:8b** (23.99초, 무료)

### 시나리오 3: 하이브리드 전략
**요구사항**: 에이전트별 특성에 맞는 선택

**추천 조합**:
```
source_code (쉬운 작업):
  → gemini (3.85초, F1 0.874) ✨ 빠르고 성능도 좋음

logs_config (중간 난이도):
  → gemini (6.48초, F1 0.956) ✨ 빠르고 성능 우수

assembly_binary (어려운 작업):
  → 옵션 1: gemini (4.04초, F1 0.744) - 속도 우선
  → 옵션 2: gpt-4.1 (10.36초, F1 0.980) - 성능 우선
```

## 성능 vs 속도 트레이드오프

### 모델별 비교 (전체 평균)

| 모델 | 평균 응답시간 | 평균 F1 점수 | 평가 |
|------|--------------|--------------|------|
| **gemini** | 4.53초 | 0.489 | ✨ 가성비 최고 (빠르고 성능 준수) |
| **gpt-4.1** | 14.26초 | 0.470 | 🎯 성능 우선 (느리지만 정확) |
| **grok-3-mini** | 12.28초 | 0.335 | ⚖️ 중간 (속도/성능 모두 중간) |
| **llama3:8b** | 23.99초 | 0.373 | 💰 무료 (느리지만 로컬) |
| **qwen3:8b** | 61.54초 | 0.320 | ❌ 비추천 (느리고 성능도 낮음) |

### 의사결정 기준

**속도가 최우선이면**: `google/gemini-2.0-flash-exp`
- 모든 에이전트에서 가장 빠름
- 성능도 상위권 (특히 logs_config에서 우수)

**성능이 최우선이면**: `openai/gpt-4.1`
- 모든 에이전트에서 F1 0.97~0.98
- 속도는 중간 수준 (14.26초)

**균형을 원하면**: `google/gemini-2.0-flash-exp`
- Gemini: 빠름(4.53초) + 준수한 성능(F1 0.489)
- GPT-4.1 대비: 3배 빠름, 성능은 약간 낮음

**무료가 필요하면**: `ollama/llama3:8b`
- 로컬 실행 가능
- 속도는 느림(23.99초), 성능은 준수(F1 0.373)

## 응답시간 안정성 분석

### 표준편차가 작은 모델 (안정적)

1. **google/gemini-2.0-flash-exp**: ±1.55초 ✨
2. **ollama/llama3:8b**: ±3.22초
3. **xai/grok-3-mini**: ±3.59초

### 표준편차가 큰 모델 (변동성 큼)

1. **openai/gpt-4.1**: ±9.71초 ⚠️
2. **ollama/qwen3:8b**: ±11.96초 ⚠️

**해석**:
- **Gemini**: 가장 안정적 (예측 가능한 응답시간)
- **GPT-4.1**: 변동성 높음 (때로는 매우 빠르거나 느림)
- **Qwen3**: 변동성 매우 높음 (신뢰하기 어려움)

## 에이전트별 속도 특성

### assembly_binary
- **가장 빠른**: gemini (4.04초)
- **가장 느린**: qwen3 (58.66초)
- **속도 차이**: 14.5배
- **특징**: 어려운 작업이지만 Gemini는 빠르게 처리

### logs_config
- **가장 빠른**: gemini (6.48초)
- **가장 느린**: gpt-4.1 (28.30초)
- **속도 차이**: 4.4배
- **특징**: GPT-4.1이 가장 느린 에이전트 (표준편차도 큼)

### source_code
- **가장 빠른**: gemini (3.85초)
- **가장 느린**: qwen3 (57.67초)
- **속도 차이**: 15.0배
- **특징**: 가장 빠르게 처리되는 에이전트

## 옵션 설명

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--summary` | 응답시간 요약 출력 | `--summary` |
| `--comparison` | 평균 응답시간 비교 막대 그래프 | `--comparison` |
| `--heatmap` | 응답시간 히트맵 | `--heatmap` |
| `--boxplot` | 응답시간 분포 박스플롯 | `--boxplot` |
| `--all` | 모든 그래프 및 요약 생성 | `--all` |
| `--min-tests N` | 최소 테스트 수 (기본값: 10) | `--min-tests 30` |

## 빠른 의사결정 가이드

### Q: 가장 빠른 모델은?
**A**: `google/gemini-2.0-flash-exp` (4.53초)
- 모든 에이전트에서 압도적 1위
- GPT-4.1 대비 3배 빠름

### Q: 성능을 포기하지 않으면서 빠른 모델은?
**A**: `google/gemini-2.0-flash-exp`
- 빠름: 4.53초 (1위)
- 성능: F1 0.489 (2위)
- logs_config에서 F1 0.956 (거의 GPT-4.1 수준)

### Q: 응답시간이 가장 안정적인 모델은?
**A**: `google/gemini-2.0-flash-exp` (±1.55초)
- 표준편차 가장 작음
- 예측 가능한 성능

### Q: 무료 모델 중 가장 빠른 것은?
**A**: `ollama/llama3:8b` (23.99초)
- Qwen3 대비 2.5배 빠름
- 성능도 더 좋음

## 문제 해결

### 그래프에 모델이 안 보이는 경우
```bash
# 최소 테스트 수를 낮추기
python visualize_response_time.py benchmark_results.json --all --min-tests 5
```

### 특정 에이전트만 분석하고 싶은 경우
현재는 모든 에이전트를 함께 분석합니다.
필요시 코드 수정으로 필터링 가능합니다.

## 마무리

### 권장 사항

**대부분의 경우**: `google/gemini-2.0-flash-exp`를 사용하세요
- ✅ 가장 빠름 (4.53초)
- ✅ 안정적 (±1.55초)
- ✅ 성능도 우수 (F1 0.489, logs에서 0.956)
- ✅ 가성비 최고

**초고성능이 필요한 경우**: `openai/gpt-4.1`
- ✅ 최고 F1 점수 (0.47~0.98)
- ⚠️ 속도는 중간 (14.26초)
- ⚠️ 변동성 높음 (±9.71초)

**무료 솔루션**: `ollama/llama3:8b`
- ✅ 로컬 실행
- ✅ 준수한 성능 (F1 0.373)
- ⚠️ 느림 (23.99초)

### 빠른 시작

```bash
# 요약만 보기
python visualize_response_time.py benchmark_results.json --summary --min-tests 20

# 모든 그래프 생성
python visualize_response_time.py benchmark_results.json --all --min-tests 20
```
