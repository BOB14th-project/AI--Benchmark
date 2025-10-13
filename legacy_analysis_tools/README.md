# 레거시 분석 도구들

이 디렉토리에는 이전 버전의 개별 분석 및 시각화 도구들이 포함되어 있습니다.

## ⚠️ 중요 안내

**새로운 통합 도구 사용을 권장합니다:**
```bash
python analyze_and_visualize.py benchmark_results.json
```

통합 도구는 다음과 같은 장점을 제공합니다:
- 모든 분석 기능 통합
- 일관된 결과 형식
- 더 나은 성능
- 간편한 사용법
- 통일된 Ground Truth 처리

## 레거시 도구 목록

### 분석 도구
- `analyze_algorithm_detection.py` - 알고리즘별 탐지 성공/실패 분석
- `analyze_precision_recall.py` - Precision, Recall, F1 Score 상세 분석
- `generate_comprehensive_report.py` - 종합 텍스트 보고서 생성
- `check_f1_data.py` - F1 점수 데이터 확인 스크립트

### 시각화 도구
- `visualize_agent_performance.py` - 에이전트별 모델 성능 시각화
- `visualize_response_time.py` - 응답시간 시각화
- `visualize_algorithm_detection.py` - 알고리즘 탐지율 시각화
- `visualize_model_performance.py` - 모델 성능 비교 시각화
- `visualize_f1_score.py` - F1 Score 시각화

## 레거시 도구 사용법 (참고용)

### 알고리즘 탐지 분석
```bash
cd legacy_analysis_tools
python analyze_algorithm_detection.py --file ../benchmark_results.json --by-model
```

### Precision/Recall 분석
```bash
python analyze_precision_recall.py --file ../benchmark_results.json
```

### 에이전트별 성능 시각화
```bash
python visualize_agent_performance.py ../benchmark_results.json --all
```

### 응답시간 시각화
```bash
python visualize_response_time.py ../benchmark_results.json --all
```

### F1 Score 시각화
```bash
python visualize_f1_score.py --file ../benchmark_results.json
```

### 알고리즘 탐지 시각화
```bash
python visualize_algorithm_detection.py --file ../benchmark_results.json
```

### 모델 성능 시각화
```bash
python visualize_model_performance.py --file ../benchmark_results.json
```

### 종합 보고서 생성
```bash
python generate_comprehensive_report.py --file ../benchmark_results.json --output report.txt
```

## 마이그레이션 가이드

기존 레거시 도구 사용자는 다음과 같이 새 도구로 전환할 수 있습니다:

| 기존 도구 | 새 도구 | 비고 |
|----------|---------|------|
| `analyze_*.py` | `analyze_and_visualize.py` | 모든 분석 기능 통합 |
| `visualize_*.py` | `analyze_and_visualize.py` | 모든 시각화 기능 통합 |
| 개별 실행 | 한 번의 실행 | 훨씬 간편함 |

## 유지보수 상태

이 레거시 도구들은 **유지보수 모드**입니다:
- 버그 수정만 제공
- 새로운 기능 추가 없음
- 향후 버전에서 제거될 수 있음

## 문의

레거시 도구 관련 문의나 새 도구로의 전환 문의는 GitHub Issues에 남겨주세요.
