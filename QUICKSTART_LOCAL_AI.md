# 🚀 로컬 AI 서버 벤치마크 빠른 시작 가이드

## ⚡ 빠른 설정 (5분 이내)

### 1단계: 로컬 AI 서버 정보 확인

먼저 로컬 AI 서버의 다음 정보를 확인하세요:

- **서버 주소**: 예) `http://localhost:8000`
- **API 엔드포인트**: 예) `/v1/chat/completions` (OpenAI 호환) 또는 `/generate` (커스텀)
- **모델 이름**: 예) `llama3-rag`, `custom-model`
- **API 키**: 필요한 경우

### 2단계: 환경 설정

`.env` 파일을 열고 다음 설정을 추가하세요:

```bash
# Local AI Server Configuration
LOCAL_AI_API_KEY=not_required
LOCAL_AI_MODEL=your-model-name
LOCAL_AI_BASE_URL=http://localhost:8000/v1
```

**⚠️ 중요**:
- OpenAI 호환 API를 사용하는 경우 BASE_URL 끝에 `/v1`을 추가하세요
- 커스텀 API를 사용하는 경우 `/v1` 없이 루트 URL만 입력하세요

### 3단계: 연결 테스트

```bash
python test_local_connection.py
```

다음과 같은 출력이 나오면 성공입니다:

```
✅ 서버가 실행 중입니다!
✅ 요청 성공!
✅ 모든 테스트 완료!
```

### 4단계: 벤치마크 실행

```bash
# 방법 1: 로컬 AI만 테스트
python test_model.py --provider local_ai

# 방법 2: 특정 에이전트 테스트
python test_agent.py --agent source_code --provider local_ai

# 방법 3: 전체 벤치마크 (모든 모델 포함)
python run_benchmark.py
```

### 5단계: 결과 분석

```bash
python analyze_and_visualize.py benchmark_results.json
```

생성된 파일:
- `COMPREHENSIVE_REPORT.txt`: 종합 보고서
- `model_f1_comparison.png`: F1 Score 비교
- `model_response_time.png`: 응답 시간 비교

---

## 🔧 커스텀 API 사용 시 추가 설정

OpenAI 호환이 아닌 커스텀 API를 사용하는 경우, `clients/local_ai_client.py` 파일을 수정해야 합니다:

### 수정 위치 1: 요청 엔드포인트 (96번째 줄 근처)

```python
# 예시: 커스텀 엔드포인트로 변경
endpoint = f"{self.base_url}/api/inference"  # 또는 /generate, /predict 등
```

### 수정 위치 2: 요청 데이터 형식 (88-93번째 줄)

```python
# 예시: 로컬 서버의 요청 형식에 맞게 변경
data = {
    "query": prompt,          # 또는 "text", "input" 등
    "max_length": max_tokens, # 또는 "max_tokens", "length" 등
    "temperature": 0.1,
    "model": self.model
}
```

### 수정 위치 3: 응답 파싱 (116-125번째 줄)

```python
# 예시: 로컬 서버의 응답 형식에 맞게 변경
content = response_json.get('generated_text', '')
# 또는
# content = response_json.get('response', '')
# 또는
# content = response_json.get('output', {}).get('text', '')
```

---

## 📊 RAG 시스템 통합 팁

RAG 시스템을 갖춘 로컬 AI 서버를 테스트하는 경우:

### 1. RAG 지식 베이스 준비

벤치마크 실행 전에 다음 파일들을 로컬 AI 서버에 로드하세요:

```bash
data/rag_knowledge/source_code_agent_reference.json
data/rag_knowledge/assembly_binary_agent_reference.json
data/rag_knowledge/logs_config_agent_reference.json
```

### 2. RAG 성능 측정

RAG가 있는 모델과 없는 모델을 비교:

```bash
# RAG 없는 모델 (기본 Ollama)
python test_model.py --provider ollama --model llama3:8b

# RAG 있는 모델 (로컬 AI)
python test_model.py --provider local_ai

# 결과 비교
python analyze_and_visualize.py benchmark_results.json
```

### 3. 타임아웃 조정

RAG 처리 시간을 고려하여 `config/config.yaml`의 타임아웃을 늘리세요:

```yaml
benchmark:
  timeout_seconds: 90  # RAG 시스템용으로 증가
```

---

## 🐛 문제 해결

### 연결 오류

```
Error: Connection refused
```

**해결**:
1. 로컬 AI 서버가 실행 중인지 확인
2. 포트 번호 확인
   ```bash
   curl http://localhost:8000/health
   ```

### 모델을 찾을 수 없음

```
Error: Model 'your-model' not found
```

**해결**:
1. 사용 가능한 모델 확인
   ```bash
   curl http://localhost:8000/v1/models
   ```
2. `.env` 파일의 `LOCAL_AI_MODEL` 수정

### 타임아웃

```
Error: Request timeout
```

**해결**:
1. `config/config.yaml`의 `timeout_seconds` 증가
2. 로컬 서버 리소스 확인 (GPU 메모리, CPU)

### JSON 파싱 오류

```
Error: Invalid JSON response
```

**해결**:
1. 로컬 AI 서버가 JSON 형식으로 응답하는지 확인
2. `clients/local_ai_client.py`의 응답 파싱 로직 수정
3. 프롬프트에 JSON 형식 명시적 요청:
   ```python
   prompt = "... Please respond in JSON format: {...}"
   ```

---

## 📈 예상 결과

벤치마크 실행 후 다음 항목들이 평가됩니다:

1. **F1 Score**: 양자 취약 알고리즘 탐지 정확도
2. **Precision**: 탐지된 것 중 실제 취약 알고리즘 비율
3. **Recall**: 실제 취약 알고리즘 중 탐지된 비율
4. **Response Time**: 평균 응답 시간
5. **Algorithm Detection Rate**: 알고리즘별 탐지율

### RAG 시스템의 기대 효과

- ✅ **Recall 증가**: 누락된 알고리즘 탐지 개선
- ✅ **한국 알고리즘 탐지**: SEED, ARIA, KCDSA 등 탐지율 향상
- ✅ **Precision 유지/증가**: 오탐 감소
- ⚠️ **Response Time 증가**: RAG 검색으로 인한 약간의 속도 저하 (허용 범위)

---

## 📚 추가 리소스

### 상세 가이드
- [LOCAL_AI_SERVER_INTEGRATION.md](docs/LOCAL_AI_SERVER_INTEGRATION.md)

### 생성된 파일들
- `clients/local_ai_client.py`: 로컬 AI 클라이언트
- `test_local_connection.py`: 연결 테스트 스크립트
- `setup_local_ai.py`: 자동 설정 스크립트

### 벤치마크 커스터마이징
- `config/config.yaml`: 벤치마크 설정
- `agents/`: 에이전트 프롬프트 수정
- `utils/metrics_calculator.py`: 평가 지표 추가

---

## 💡 자동 설정 도구

수동 설정이 번거로운 경우, 자동 설정 스크립트를 사용하세요:

```bash
python setup_local_ai.py --interactive
```

대화형 모드로 모든 설정을 자동으로 완료합니다.

---

## 🎯 다음 단계

1. ✅ 로컬 AI 서버 연결 테스트
2. ✅ 단일 파일로 기본 탐지 테스트
3. ✅ 에이전트별 성능 평가
4. ✅ 전체 벤치마크 실행
5. ✅ RAG vs Non-RAG 성능 비교
6. ✅ 결과 분석 및 모델 개선

---

궁금한 점이 있으면 언제든 질문하세요!

**참고**: 이 벤치마크는 양자 컴퓨팅 시대를 대비한 암호 시스템의 **양자 취약 알고리즘**을 탐지하는 AI 모델의 성능을 평가합니다.
