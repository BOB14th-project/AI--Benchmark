# 에이전트별 모델 성능 시각화 가이드

## 개요

`visualize_agent_performance.py`는 각 에이전트(source_code, assembly_binary, logs_config)에서 어떤 모델이 가장 뛰어난지 시각적으로 비교 분석하는 도구입니다.

## 핵심 결과 요약

### 🏆 에이전트별 최고 성능 모델

| 에이전트 | 최고 F1 모델 | F1 점수 | Precision | Recall | 가장 빠른 모델 |
|---------|-------------|---------|-----------|--------|--------------|
| **assembly_binary** | openai/gpt-4.1 | 0.980 | 0.980 | 0.980 | google/gemini-2.0-flash-exp (4.04초) |
| **logs_config** | openai/gpt-4.1 | 0.988 | 0.988 | 0.988 | google/gemini-2.0-flash-exp (6.48초) |
| **source_code** | openai/gpt-4.1 | 0.974 | 0.974 | 0.974 | google/gemini-2.0-flash-exp (3.85초) |

**결론**:
- **성능 최우선**: `openai/gpt-4.1` - 모든 에이전트에서 최고 F1 점수
- **속도 최우선**: `google/gemini-2.0-flash-exp` - 모든 에이전트에서 가장 빠름
- **균형 잡힌 선택**: `google/gemini-2.0-flash-exp` - 높은 F1 + 빠른 속도

## 사용 방법

### 1. 요약 정보만 보기 (권장)

```bash
python visualize_agent_performance.py benchmark_results.json --summary
```

**출력 예시:**
```
🏆 에이전트별 최고 성능 모델 요약

🎯 assembly_binary
  🥇 최고 F1 점수: openai/gpt-4.1
     - F1: 0.980, Precision: 0.980, Recall: 0.980
     - 테스트 수: 60개, 응답시간: 10.36초

  전체 모델 순위 (F1 기준):
    1. openai/gpt-4.1: F1 0.980 (60개 테스트)
    2. ollama/llama3:8b: F1 0.802 (61개 테스트)
    3. google/gemini-2.0-flash-exp: F1 0.744 (43개 테스트)
```

### 2. 모든 그래프 생성

```bash
python visualize_agent_performance.py benchmark_results.json --all
```

생성되는 파일:
- `agent_model_heatmap_f1_score.png` - 히트맵
- `agent_best_models.png` - 에이전트별 최고 모델 비교
- `agent_model_rankings.png` - 에이전트별 모델 순위
- `comprehensive_agent_model_comparison.png` - 종합 비교

### 3. 특정 그래프만 생성

```bash
# 히트맵만
python visualize_agent_performance.py benchmark_results.json --heatmap

# 막대 그래프만
python visualize_agent_performance.py benchmark_results.json --bar

# 순위 차트만
python visualize_agent_performance.py benchmark_results.json --ranking

# 종합 비교만
python visualize_agent_performance.py benchmark_results.json --comprehensive
```

### 4. 최소 테스트 수 필터링

```bash
# 최소 30개 테스트 이상인 모델만 분석
python visualize_agent_performance.py benchmark_results.json --all --min-tests 30
```

## 생성되는 그래프 설명

### 1. 히트맵 (Heatmap)
- **파일명**: `agent_model_heatmap_f1_score.png`
- **내용**: 에이전트(행) × 모델(열) 성능을 색상으로 표시
- **색상**: 빨간색이 진할수록 성능 우수
- **용도**: 한눈에 어떤 조합이 좋은지 파악

### 2. 에이전트별 최고 모델 비교
- **파일명**: `agent_best_models.png`
- **내용**: 각 에이전트에서 가장 뛰어난 모델을 F1, Precision, Recall로 비교
- **구성**: 3개 서브플롯 (F1, Precision, Recall)
- **용도**: 에이전트별 최적 모델 선택

### 3. 순위 차트
- **파일명**: `agent_model_rankings.png`
- **내용**: 각 에이전트별로 모든 모델의 F1 순위
- **특징**: 막대 안에 테스트 수(n=) 표시
- **용도**: 에이전트별 모델 간 성능 차이 파악

### 4. 종합 비교
- **파일명**: `comprehensive_agent_model_comparison.png`
- **내용**: F1, Precision, Recall을 한 그래프에 모두 표시
- **구성**: 에이전트별로 구분되어 모든 모델의 3가지 지표 비교
- **용도**: 전체적인 성능 패턴 파악

## 실전 활용 예시

### 시나리오 1: 성능 최우선 프로젝트
**목표**: 최고 정확도로 양자 취약 알고리즘 탐지

```bash
python visualize_agent_performance.py benchmark_results.json --summary
```

**결론**: 모든 에이전트에서 **openai/gpt-4.1** 선택
- assembly_binary: F1 0.980
- logs_config: F1 0.988
- source_code: F1 0.974

### 시나리오 2: 속도 최우선 프로젝트
**목표**: 빠른 응답 시간으로 대량 파일 처리

**결론**: 모든 에이전트에서 **google/gemini-2.0-flash-exp** 선택
- assembly_binary: 4.04초 (F1 0.744)
- logs_config: 6.48초 (F1 0.956)
- source_code: 3.85초 (F1 0.874)

### 시나리오 3: 균형 잡힌 선택
**목표**: 성능과 속도 모두 고려

**추천 조합**:
- **logs_config**: `google/gemini-2.0-flash-exp` (F1 0.956, 6.48초) - 성능도 우수하고 빠름
- **source_code**: `google/gemini-2.0-flash-exp` (F1 0.874, 3.85초) - 적절한 성능과 빠른 속도
- **assembly_binary**: `openai/gpt-4.1` (F1 0.980, 10.36초) - 어려운 작업이므로 성능 우선

### 시나리오 4: 비용 최소화 (오픈소스 모델)
**목표**: 무료 로컬 모델 사용

**추천**: **ollama/llama3:8b**
- assembly_binary: F1 0.802 (2위)
- logs_config: F1 0.804 (4위)
- source_code: F1 0.802 (3위)
- 특징: 유료 모델 대비 성능은 낮지만, 로컬 실행 가능

## 통계적 신뢰도

기본적으로 **최소 20개 테스트** 이상인 모델만 분석에 포함됩니다.
이는 통계적으로 의미 있는 결과를 보장하기 위함입니다.

**테스트 수가 부족한 경우 제외되는 모델**:
- `ollama/codellama:7b`: 3개 테스트 (부족)
- 일부 에이전트에서 테스트되지 않은 모델 조합

## 옵션 설명

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--summary` | 에이전트별 최고 모델 요약 출력 | `--summary` |
| `--heatmap` | 히트맵 생성 | `--heatmap` |
| `--bar` | 막대 그래프 생성 | `--bar` |
| `--ranking` | 순위 차트 생성 | `--ranking` |
| `--comprehensive` | 종합 비교 그래프 생성 | `--comprehensive` |
| `--all` | 모든 그래프 및 요약 생성 | `--all` |
| `--min-tests N` | 최소 테스트 수 설정 (기본값: 10) | `--min-tests 30` |

## 빠른 의사결정 가이드

### Q: 어떤 모델을 선택해야 하나요?

**A: 우선순위에 따라 선택하세요:**

1. **최고 정확도**: `openai/gpt-4.1` (모든 에이전트에서 1위)
2. **최고 속도**: `google/gemini-2.0-flash-exp` (모든 에이전트에서 가장 빠름)
3. **가성비 최고**: `google/gemini-2.0-flash-exp` (높은 성능 + 빠른 속도)
4. **무료 오픈소스**: `ollama/llama3:8b` (로컬 실행, 준수한 성능)

### Q: 에이전트마다 다른 모델을 써도 되나요?

**A: 네, 추천합니다!**

각 에이전트의 특성에 맞는 모델 선택:
- **logs_config**: 상대적으로 쉬운 작업 → 빠른 모델(`gemini`)로도 충분
- **assembly_binary**: 어려운 작업 → 정확한 모델(`gpt-4.1`) 필요
- **source_code**: 중간 난이도 → 균형 잡힌 모델 선택

### Q: 그래프를 볼 필요가 있나요?

**A: 상황에 따라 다릅니다:**

- **빠른 의사결정**: `--summary`만 사용 (텍스트 출력)
- **보고서/발표**: `--all` 사용 (모든 그래프 생성)
- **특정 지표 분석**: 필요한 그래프만 선택적으로 생성

## 문제 해결

### 그래프가 생성되지 않는 경우

```bash
# matplotlib 설치 확인
pip install matplotlib seaborn numpy pandas

# 폰트 경고 무시하려면
python visualize_agent_performance.py benchmark_results.json --all 2>/dev/null
```

### 데이터가 없다는 오류

```bash
# 최소 테스트 수를 낮추기
python visualize_agent_performance.py benchmark_results.json --all --min-tests 5
```

### 특정 에이전트만 분석하고 싶은 경우

현재는 모든 에이전트를 함께 분석합니다.
필요시 코드 수정으로 특정 에이전트만 필터링 가능합니다.

## 마무리

이 도구를 사용하여:
1. ✅ 각 에이전트에 최적화된 모델 선택
2. ✅ 성능과 속도 트레이드오프 파악
3. ✅ 비용 효율적인 모델 조합 구성
4. ✅ 데이터 기반 의사결정

**권장 첫 단계**:
```bash
python visualize_agent_performance.py benchmark_results.json --summary --min-tests 20
```
