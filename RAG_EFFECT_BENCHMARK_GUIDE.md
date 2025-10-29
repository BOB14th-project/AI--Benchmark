# RAG 효과 측정 벤치마크 가이드

같은 기본 모델로 RAG 유무에 따른 성능 차이를 측정하는 벤치마크 시스템입니다.

## 🎯 비교 대상

### 1. llama3:8b 기반 비교
- **PQC Inspector (llama3:8b + RAG)** vs **llama3:8b (순수)**
- RAG 시스템이 로컬 모델 성능에 미치는 영향 측정

### 2. gemini-2.0-flash-exp 기반 비교
- **PQC Inspector (gemini-2.0-flash-exp + RAG)** vs **gemini-2.0-flash-exp (순수)**
- RAG 시스템이 상용 API 성능에 미치는 영향 측정

## 📊 측정 메트릭

각 테스트에서 다음을 측정합니다:

| 메트릭 | 설명 |
|--------|------|
| **F1 Score** | 정밀도와 재현율의 조화 평균 |
| **Precision** | 탐지 정확도 (거짓 양성 최소화) |
| **Recall** | 탐지 완전성 (거짓 음성 최소화) |
| **Response Time** | 응답 시간 |
| **JSON Valid** | 구조화된 응답 생성 능력 |

**RAG 효과 = (RAG 포함 F1 - RAG 없음 F1) / RAG 없음 F1 × 100%**

## 📋 사전 준비

### 1. AI-Server 실행

```bash
cd AI-Server
python main.py
```

### 2. Ollama 실행 (llama3:8b 테스트시)

```bash
# Ollama 서버 실행
ollama serve

# llama3:8b 모델 다운로드
ollama pull llama3:8b
```

### 3. API 키 설정 (gemini 테스트시)

`AI--Benchmark/config/config.yaml` 또는 `.env` 파일에 Google API 키 설정:

```yaml
llm_providers:
  google:
    api_key_env: "GOOGLE_API_KEY"
    model_env: "GOOGLE_MODEL"
```

## 🚀 벤치마크 실행

### 기본 실행 (llama3:8b + gemini 모두 테스트)

```bash
cd AI--Benchmark
python benchmark_rag_effect.py --limit 2
```

### llama3:8b만 테스트

```bash
python benchmark_rag_effect.py --models llama3:8b --limit 1
```

### gemini-2.0-flash-exp만 테스트

```bash
python benchmark_rag_effect.py --models gemini-2.0-flash --limit 1
```

### 특정 에이전트만 테스트

```bash
# 소스코드 에이전트만
python benchmark_rag_effect.py --agents source_code --limit 3

# 여러 에이전트
python benchmark_rag_effect.py --agents source_code logs_config --limit 2
```

### 전체 벤치마크

```bash
python benchmark_rag_effect.py --models llama3:8b gemini-2.0-flash-exp
```

## 📊 결과 해석

### 콘솔 출력 예시

```
🔬 모델: llama3:8b
============================================================

📈 전체 평균:
   RAG 포함:  F1=0.875, Precision=0.892, Recall=0.860, 시간=4.23초
   RAG 없음:  F1=0.698, Precision=0.715, Recall=0.683, 시간=2.45초
   🎯 RAG 효과: F1 Score +25.4% 향상

📋 에이전트별 RAG 효과:
   source_code         : RAG=0.910, 순수=0.745, 효과=+22.1%
   assembly_binary     : RAG=0.845, 순수=0.670, 효과=+26.1%
   logs_config         : RAG=0.870, 순수=0.680, 효과=+27.9%


🔬 모델: gemini-2.0-flash-exp
============================================================

📈 전체 평균:
   RAG 포함:  F1=0.920, Precision=0.935, Recall=0.906, 시간=5.12초
   RAG 없음:  F1=0.865, Precision=0.880, Recall=0.851, 시간=4.67초
   🎯 RAG 효과: F1 Score +6.4% 향상

📋 에이전트별 RAG 효과:
   source_code         : RAG=0.945, 순수=0.890, 효과=+6.2%
   assembly_binary     : RAG=0.900, 순수=0.850, 효과=+5.9%
   logs_config         : RAG=0.915, 순수=0.855, 효과=+7.0%
```

### 결과 분석 포인트

1. **RAG 효과가 큰 경우**
   - F1 Score 향상률 > 15%
   - 특히 로컬 모델(llama3:8b)에서 효과가 큼
   - RAG가 전문 지식을 효과적으로 제공

2. **RAG 효과가 작은 경우**
   - F1 Score 향상률 < 10%
   - 상용 API(gemini)는 이미 고성능
   - RAG가 추가 개선 제공하지만 폭이 작음

3. **응답 시간 증가**
   - RAG 검색 오버헤드로 1-2초 증가
   - 성능 향상 대비 허용 가능한 수준

## 🔧 AI-Server 모델 변경

RAG 효과 측정을 위해 AI-Server의 에이전트 모델을 변경해야 합니다.

### 방법 1: .env 파일 수동 편집 (권장)

```bash
# AI-Server/.env 파일 편집
vim AI-Server/.env
```

다음 변수를 원하는 모델로 변경:

```env
# llama3:8b 테스트시
SOURCE_CODE_MODEL=llama3:8b
BINARY_MODEL=llama3:8b
LOG_CONF_MODEL=llama3:8b

# gemini 테스트시
SOURCE_CODE_MODEL=gemini-2.0-flash-exp
BINARY_MODEL=gemini-2.0-flash-exp
LOG_CONF_MODEL=gemini-2.0-flash-exp
```

변경 후 AI-Server 재시작:

```bash
cd AI-Server
python main.py
```

### 방법 2: 자동 변경 (실험적)

```bash
python benchmark_rag_effect.py --models llama3:8b --auto-restart
```

**주의**: 이 방법은 .env 파일을 자동으로 수정하고 재시작을 요청합니다.

## 📁 결과 파일

결과는 `results/` 디렉토리에 저장됩니다:

```
results/rag_effect_comparison_20251025_143022.json
```

### 결과 파일 구조

```json
{
  "benchmark_info": {
    "timestamp": "2025-10-25T14:30:22",
    "test_models": ["llama3:8b", "gemini-2.0-flash-exp"],
    "total_tests": 24
  },
  "results": [
    {
      "base_model": "llama3:8b",
      "with_rag": true,
      "agent_type": "source_code",
      "f1_score": 0.91,
      "precision": 0.93,
      "recall": 0.89,
      "response_time": 4.23,
      ...
    },
    {
      "base_model": "llama3:8b",
      "with_rag": false,
      "agent_type": "source_code",
      "f1_score": 0.75,
      "precision": 0.78,
      "recall": 0.72,
      "response_time": 2.10,
      ...
    },
    ...
  ]
}
```

## 📈 기대 결과

### llama3:8b

| 메트릭 | RAG 포함 | RAG 없음 | 효과 |
|--------|----------|----------|------|
| F1 Score | 0.85-0.90 | 0.65-0.75 | **+20-30%** |
| Precision | 0.87-0.92 | 0.68-0.78 | +19-25% |
| Recall | 0.83-0.88 | 0.62-0.72 | +21-30% |
| 응답 시간 | 4-6초 | 2-3초 | +100% |

**결론**: RAG가 로컬 모델 성능을 **크게 향상**시킴

### gemini-2.0-flash-exp

| 메트릭 | RAG 포함 | RAG 없음 | 효과 |
|--------|----------|----------|------|
| F1 Score | 0.92-0.95 | 0.86-0.90 | **+5-10%** |
| Precision | 0.93-0.96 | 0.88-0.92 | +5-8% |
| Recall | 0.91-0.94 | 0.84-0.88 | +7-12% |
| 응답 시간 | 5-7초 | 4-6초 | +20% |

**결론**: RAG가 고성능 모델도 **추가 개선**

## 🔍 상세 분석

### 기존 분석 도구 활용

```bash
# 통합 분석 및 시각화
python analyze_and_visualize.py results/rag_effect_comparison_*.json

# RAG 효과만 시각화
python visualize_rag_effect.py results/rag_effect_comparison_*.json
```

### Python으로 결과 분석

```python
import json

# 결과 로드
with open('results/rag_effect_comparison_20251025_143022.json') as f:
    data = json.load(f)

# RAG 포함/제외 분리
rag_results = [r for r in data['results'] if r['with_rag']]
no_rag_results = [r for r in data['results'] if not r['with_rag']]

# 평균 F1 계산
avg_rag_f1 = sum(r['f1_score'] for r in rag_results) / len(rag_results)
avg_no_rag_f1 = sum(r['f1_score'] for r in no_rag_results) / len(no_rag_results)

print(f"RAG 포함 평균 F1: {avg_rag_f1:.3f}")
print(f"RAG 없음 평균 F1: {avg_no_rag_f1:.3f}")
print(f"효과: {(avg_rag_f1 - avg_no_rag_f1) / avg_no_rag_f1 * 100:.1f}%")
```

## 🛠️ 문제 해결

### AI-Server가 Ollama 모델을 인식하지 못함

**증상:**
```
❌ AI 모델 'llama3:8b' 호출 중 오류 발생
```

**해결책:**
1. AI-Server의 Ollama 지원이 추가되었는지 확인
2. `pqc_inspector_server/services/ai_service.py`에 `_call_ollama` 메서드 확인
3. AI-Server 재시작

### gemini 모델 API 오류

**증상:**
```
❌ Google API 오류: 401 - Unauthorized
```

**해결책:**
```bash
# AI-Server/.env 파일 확인
cat AI-Server/.env | grep GOOGLE_API_KEY

# 유효한 API 키로 업데이트
vim AI-Server/.env
```

### JSON 파싱 실패

RAG 없는 테스트에서 JSON 파싱 실패율이 높을 수 있습니다. 이는 정상적인 현상으로, RAG의 효과를 보여주는 지표입니다.

## 💡 벤치마크 팁

1. **작은 샘플로 시작**: `--limit 2`로 빠르게 테스트
2. **한 모델씩 테스트**: llama3:8b 먼저, 그 다음 gemini
3. **결과 비교**: 여러 번 실행하여 평균 구하기
4. **에이전트 필터**: 특정 에이전트만 집중 테스트

## 📚 관련 문서

- [AI-Server README](../AI-Server/README.md) - PQC Inspector 상세 문서
- [PQC Inspector Benchmark Guide](./PQC_INSPECTOR_BENCHMARK_GUIDE.md) - 기본 벤치마크 가이드
- [METRICS.md](./docs/METRICS.md) - 평가 메트릭 설명
