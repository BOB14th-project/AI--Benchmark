# PQC Inspector vs llama3:8b 벤치마크 가이드

AI-Server의 RAG 강화 전문 에이전트와 llama3:8b를 비교 평가하는 벤치마크 시스템입니다.

## 🎯 개요

이 벤치마크는 다음을 비교합니다:
- **PQC Inspector 에이전트** (RAG + Gemini 2.5 Flash)
  - SourceCodeAgent
  - AssemblyBinaryAgent
  - LogsConfigAgent
- **llama3:8b** (Ollama 로컬 모델)

## 📋 사전 준비

### 1. AI-Server 실행

```bash
cd AI-Server
python main.py
```

서버가 정상적으로 실행되면 `http://localhost:8000`에서 접근 가능합니다.

### 2. Ollama 실행 및 모델 설치

```bash
# Ollama 서버 실행
ollama serve

# llama3:8b 모델 다운로드
ollama pull llama3:8b
```

### 3. 환경 확인

두 서버가 모두 실행 중인지 확인:

```bash
# AI-Server 확인
curl http://localhost:8000/

# Ollama 확인
curl http://localhost:11434/api/tags
```

## 🚀 벤치마크 실행

### 빠른 테스트 (에이전트당 2개 파일)

```bash
cd AI--Benchmark
python benchmark_pqc_inspector.py --limit 2
```

### 특정 에이전트만 테스트

```bash
# 소스코드 에이전트만
python benchmark_pqc_inspector.py --agents source_code --limit 3

# 여러 에이전트
python benchmark_pqc_inspector.py --agents source_code assembly_binary --limit 3
```

### 전체 벤치마크

```bash
python benchmark_pqc_inspector.py
```

### 서버 URL 커스터마이징

```bash
python benchmark_pqc_inspector.py \
  --pqc-url http://localhost:8000 \
  --ollama-url http://localhost:11434 \
  --limit 5
```

## 📊 결과 분석

### 1. 콘솔 출력

벤치마크 실행 중 실시간으로 각 테스트의 결과를 확인할 수 있습니다:

```
--- 테스트 1/2: rsa_example.py ---
✅ PQC Inspector (source_code): F1=0.950, 시간=3.45초
✅ llama3:8b (source_code): F1=0.720, 시간=2.10초
```

### 2. 요약 통계

벤치마크 완료 후 전체 요약이 출력됩니다:

```
📊 벤치마크 결과 요약
============================================================

🤖 PQC Inspector (RAG 강화 에이전트)
   테스트 수: 12
   평균 F1 Score: 0.875
   평균 Precision: 0.892
   평균 Recall: 0.860
   평균 응답시간: 4.23초

🦙 llama3:8b (Ollama)
   테스트 수: 12
   평균 F1 Score: 0.698
   평균 Precision: 0.715
   평균 Recall: 0.683
   평균 응답시간: 2.45초

📋 에이전트별 성능 비교
  source_code:
    PQC Inspector: F1=0.910, 시간=3.89초
    llama3:8b:     F1=0.745, 시간=2.21초

  assembly_binary:
    PQC Inspector: F1=0.845, 시간=4.12초
    llama3:8b:     F1=0.670, 시간=2.55초

  logs_config:
    PQC Inspector: F1=0.870, 시간=4.67초
    llama3:8b:     F1=0.680, 시간=2.60초
```

### 3. JSON 결과 파일

결과는 `results/` 디렉토리에 JSON 형식으로 저장됩니다:

```bash
results/pqc_inspector_vs_llama3_results_20251025_143022.json
```

결과 파일 구조:
```json
{
  "benchmark_info": {
    "timestamp": "2025-10-25T14:30:22",
    "pqc_base_url": "http://localhost:8000",
    "ollama_base_url": "http://localhost:11434",
    "total_tests": 24
  },
  "results": [
    {
      "provider": "pqc_inspector",
      "model": "source_code",
      "agent_type": "source_code",
      "test_id": "source_code_001",
      "file_name": "rsa_example.py",
      "response_time": 3.45,
      "json_valid": true,
      "f1_score": 0.95,
      "precision": 0.96,
      "recall": 0.94,
      "accuracy": 0.93,
      "raw_response": {...}
    },
    ...
  ]
}
```

## 📈 기대 성능

| 메트릭 | PQC Inspector | llama3:8b | 차이 |
|--------|---------------|-----------|------|
| F1 Score | 0.85-0.90 | 0.65-0.75 | +20-25% |
| Precision | 0.87-0.92 | 0.68-0.78 | +19-21% |
| Recall | 0.83-0.88 | 0.62-0.72 | +21-23% |
| 응답 시간 | 3-5초 | 2-3초 | PQC가 약간 느림 |
| JSON 유효성 | 95-100% | 70-85% | RAG로 구조화된 응답 |

### PQC Inspector의 장점:
1. **높은 정확도**: RAG 시스템이 전문 지식 제공
2. **낮은 오탐율**: 전문화된 프롬프트와 검증
3. **안정적인 JSON**: 구조화된 응답 생성

### llama3:8b의 장점:
1. **빠른 응답**: 로컬 실행으로 낮은 지연시간
2. **비용 효율**: API 비용 없음
3. **오프라인 가능**: 인터넷 연결 불필요

## 🔍 상세 분석

### 기존 분석 도구 활용

벤치마크 결과를 기존 분석 도구로 시각화:

```bash
# 통합 분석 및 시각화
python analyze_and_visualize.py results/pqc_inspector_vs_llama3_results_*.json

# 모델별 F1 비교 차트
python visualize_f1_scores.py results/pqc_inspector_vs_llama3_results_*.json

# 에이전트별 성능 분석
python analyze_agent_performance.py results/pqc_inspector_vs_llama3_results_*.json
```

## 🛠️ 문제 해결

### AI-Server 접속 불가

```bash
❌ PQC Inspector 서버 접속 불가: http://localhost:8000
```

**해결책:**
```bash
cd AI-Server
python main.py
```

### llama3:8b 모델 없음

```bash
⚠️  llama3:8b 모델이 없습니다.
```

**해결책:**
```bash
ollama pull llama3:8b
```

### API 키 오류

AI-Server의 `.env` 파일에 API 키가 설정되어 있는지 확인:

```bash
# AI-Server/.env
GOOGLE_API_KEY="your-google-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

### 테스트 파일 없음

```bash
⚠️  파일 없음: data/test_files/source_code/example.py
```

**해결책:**
테스트 파일이 `AI--Benchmark/data/test_files/` 디렉토리에 있는지 확인

## 📝 벤치마크 커스터마이징

### 새로운 테스트 케이스 추가

1. 테스트 파일 추가:
```bash
AI--Benchmark/data/test_files/source_code/my_test.py
```

2. Ground truth 생성:
```bash
AI--Benchmark/data/ground_truth/source_code/my_test.json
```

3. 벤치마크 실행:
```bash
python benchmark_pqc_inspector.py --agents source_code
```

### 다른 Ollama 모델과 비교

벤치마크 스크립트의 `test_llama3()` 메서드를 수정하여 다른 모델 사용:

```python
# llama3:8b 대신 qwen3:8b 사용
client = OllamaClient(
    model='qwen3:8b',  # 변경
    base_url=self.ollama_base_url
)
```

## 🎯 다음 단계

1. **결과 분석**: JSON 결과 파일을 확인하여 세부 성능 분석
2. **시각화**: `analyze_and_visualize.py`로 차트 생성
3. **튜닝**: 성능이 낮은 에이전트의 RAG 지식 베이스 개선
4. **확장**: 더 많은 테스트 케이스로 벤치마크 확장

## 📚 참고 문서

- [AI-Server README](../AI-Server/README.md) - PQC Inspector 상세 문서
- [AI--Benchmark README](./README.md) - 벤치마크 시스템 전체 가이드
- [METRICS.md](./docs/METRICS.md) - 평가 메트릭 상세 설명
