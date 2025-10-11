# 📊 벤치마크 결과 분석 및 시각화 가이드

벤치마크 실행 후 결과를 분석하고 시각화하는 모든 명령어 모음

## 📁 결과 파일 위치

벤치마크 실행 후 생성되는 파일들:
```
benchmark_results_YYYYMMDD_HHMMSS.json  # 상세 결과 (JSON)
benchmark_results_YYYYMMDD_HHMMSS.csv   # 요약 결과 (CSV)
```

---

## 🔍 1. 알고리즘 탐지 분석

### 전체 분석 (모델별 + 통합)
```bash
python3 analyze_algorithm_detection.py
```

### 모델별 분석만
```bash
python3 analyze_algorithm_detection.py --by-model
```

### 전체 통합 분석만
```bash
python3 analyze_algorithm_detection.py --overall
```

### 특정 결과 파일 지정
```bash
python3 analyze_algorithm_detection.py --file benchmark_results_20250111_143022.json
```

**출력 예시:**
```
📊 모델별 알고리즘 탐지 분석
=================================

🤖 모델: gemini-2.5-flash
   총 테스트: 50개
   총 예상 알고리즘: 75개
   총 탐지 성공: 65개 (86.7%)
   총 탐지 실패: 10개 (13.3%)

   📈 알고리즘별 탐지율:
      ✅ RSA            :  25/ 25 (100.0%)
      ✅ AES            :  15/ 15 (100.0%)
      ⚠️  SEED          :   8/ 12 ( 66.7%)
      ❌ ARIA          :   5/ 10 ( 50.0%)
```

---

## 📈 2. 그래프 생성

### 2.1 알고리즘 탐지율 시각화 (신규! 🆕)
```bash
python3 visualize_algorithm_detection.py
```

생성되는 그래프:
- `algorithm_detection_overall.png` - 전체 알고리즘 탐지율 막대 그래프
- `algorithm_detection_by_model.png` - 모델별 알고리즘 탐지율 히트맵
- `algorithm_success_failure.png` - 알고리즘별 성공/실패 스택 바 차트
- `algorithm_top_bottom.png` - 상위/하위 알고리즘 비교

### 2.2 전체 성능 그래프 생성
```bash
# 에이전트 성능
python3 visualize_agent_performance.py

# 응답 시간 분석
python3 visualize_response_time.py
```

생성되는 그래프:
- `agent_model_heatmap_f1_score.png` - 에이전트×모델 F1 점수 히트맵
- `agent_response_time_heatmap.png` - 응답 시간 히트맵
- `agent_response_time_comparison.png` - 응답 시간 비교 바 차트
- `agent_response_time_boxplot.png` - 응답 시간 박스플롯
- `agent_model_rankings.png` - 모델별 순위
- `agent_best_models.png` - 에이전트별 최적 모델

### 2.3 특정 결과 파일로 그래프 생성
```bash
# 알고리즘 탐지율
python3 visualize_algorithm_detection.py --file benchmark_results_20250111_143022.json

# 에이전트 성능
python3 visualize_agent_performance.py --file benchmark_results_20250111_143022.json
```

### 2.4 출력 디렉토리 지정
```bash
python3 visualize_algorithm_detection.py --output-dir ./visualizations
```

---

## 📊 3. 상세 통계 분석

### 3.1 기본 통계 출력
```bash
python3 -c "
import json
with open('benchmark_results_*.json', 'r') as f:
    data = json.load(f)
    print(f\"총 테스트: {data['summary']['total_tests']}\")
    print(f\"성공: {data['summary']['successful_tests']}\")
    print(f\"성공률: {data['summary']['success_rate']:.1%}\")
"
```

### 3.2 모델별 평균 성능
```bash
python3 -c "
import json
from collections import defaultdict

with open('benchmark_results_*.json', 'r') as f:
    data = json.load(f)

model_stats = defaultdict(lambda: {'f1': [], 'time': []})

for result in data['results']:
    model = result['model_name']
    model_stats[model]['f1'].append(result.get('f1_score', 0))
    model_stats[model]['time'].append(result.get('response_time', 0))

for model, stats in model_stats.items():
    avg_f1 = sum(stats['f1']) / len(stats['f1'])
    avg_time = sum(stats['time']) / len(stats['time'])
    print(f\"{model}: F1={avg_f1:.3f}, Time={avg_time:.2f}s\")
"
```

### 3.3 에이전트별 평균 성능
```bash
python3 -c "
import json
from collections import defaultdict

with open('benchmark_results_*.json', 'r') as f:
    data = json.load(f)

agent_stats = defaultdict(lambda: {'f1': [], 'accuracy': []})

for result in data['results']:
    agent = result['agent_type']
    agent_stats[agent]['f1'].append(result.get('f1_score', 0))
    agent_stats[agent]['accuracy'].append(result.get('accuracy', 0))

for agent, stats in agent_stats.items():
    avg_f1 = sum(stats['f1']) / len(stats['f1'])
    avg_acc = sum(stats['accuracy']) / len(stats['accuracy'])
    print(f\"{agent}: F1={avg_f1:.3f}, Accuracy={avg_acc:.3f}\")
"
```

---

## 🎯 4. 종합 분석 워크플로우

### 벤치마크 실행부터 시각화까지 전체 과정:

```bash
# 1. 벤치마크 실행
python3 benchmark_runner.py

# 2. 텍스트 분석 (콘솔 출력)
python3 analyze_algorithm_detection.py > algorithm_analysis.txt

# 3. 그래프 생성
python3 visualize_algorithm_detection.py    # 알고리즘 탐지율 그래프
python3 visualize_agent_performance.py      # 에이전트 성능 그래프
python3 visualize_response_time.py          # 응답 시간 그래프

# 4. 결과 확인
cat algorithm_analysis.txt
ls *.png
```

### 한 줄 명령어로 모든 분석 실행:
```bash
python3 benchmark_runner.py && \
python3 analyze_algorithm_detection.py > algorithm_analysis.txt && \
python3 visualize_algorithm_detection.py && \
python3 visualize_agent_performance.py && \
python3 visualize_response_time.py && \
echo "✅ 분석 완료! 결과를 확인하세요."
```

---

## 📂 5. Google Drive 백업 (Colab 용)

### 자동 백업 (벤치마크 실행 중)
```python
import os
os.environ['GDRIVE_RESULTS_DIR'] = '/content/drive/MyDrive/AI_Benchmark_Results'
```

### 수동 백업
```bash
python3 utils/backup_to_gdrive.py
```

---

## 💾 6. CSV로 결과 내보내기

### JSON → CSV 변환
```bash
python3 -c "
import json
import csv

with open('benchmark_results_*.json', 'r') as f:
    data = json.load(f)

with open('detailed_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Model', 'Agent', 'File', 'F1 Score', 'Accuracy', 'Precision', 'Recall', 'Response Time'])

    for result in data['results']:
        writer.writerow([
            result['model_name'],
            result['agent_type'],
            result['file_name'],
            result.get('f1_score', 0),
            result.get('accuracy', 0),
            result.get('precision', 0),
            result.get('recall', 0),
            result.get('response_time', 0)
        ])
"
```

---

## 🔄 7. 결과 비교 (여러 벤치마크)

### 두 벤치마크 결과 비교
```bash
python3 compare_benchmarks.py \
    --file1 benchmark_results_20250110_120000.json \
    --file2 benchmark_results_20250111_143022.json
```

### 시계열 성능 추이
```bash
python3 plot_performance_trend.py --pattern "benchmark_results_*.json"
```

---

## 📋 8. 빠른 명령어 체크리스트

```bash
# ✅ 알고리즘 탐지 분석 (텍스트)
python3 analyze_algorithm_detection.py

# ✅ 알고리즘 탐지 그래프 생성 ⭐
python3 visualize_algorithm_detection.py

# ✅ 전체 성능 그래프 생성
python3 visualize_agent_performance.py
python3 visualize_response_time.py

# ✅ 결과 백업 (Colab)
python3 utils/backup_to_gdrive.py

# ✅ 최신 결과 확인
ls -lht benchmark_results_*.json | head -1

# ✅ 요약 통계
python3 -c "import json; data=json.load(open('benchmark_results_*.json')); print(data['summary'])"
```

---

## 🎨 9. 시각화 커스터마이징

### 그래프 스타일 변경
```bash
# 다크 테마
python3 visualize_results.py --style dark

# 컬러 팔레트 변경
python3 visualize_results.py --palette viridis

# 해상도 조정 (DPI)
python3 visualize_results.py --dpi 300
```

### 폰트 크기 조정
```bash
python3 visualize_results.py --fontsize 14
```

---

## 🚀 10. Colab에서 한번에 실행

```python
# Colab 노트북에서 실행
!cd /content/AI--Benchmark

# 벤치마크 실행
!python3 benchmark_runner.py

# 분석 및 시각화
!python3 analyze_algorithm_detection.py > algorithm_analysis.txt
!python3 visualize_results.py

# 결과 확인
!cat algorithm_analysis.txt
from IPython.display import Image, display
for img in ['agent_model_heatmap_f1_score.png', 'agent_response_time_comparison.png']:
    display(Image(img))

# Google Drive 백업
!python3 utils/backup_to_gdrive.py
```

---

## 📌 유용한 팁

### 1. 최신 결과 파일 자동 선택
```bash
LATEST=$(ls -t benchmark_results_*.json | head -1)
python3 analyze_algorithm_detection.py --file $LATEST
python3 visualize_results.py --file $LATEST
```

### 2. 결과 압축 및 다운로드
```bash
# 모든 결과 압축
tar -czf benchmark_results.tar.gz benchmark_results_* *.png algorithm_analysis.txt

# Colab에서 다운로드
from google.colab import files
files.download('benchmark_results.tar.gz')
```

### 3. 실시간 로그 모니터링
```bash
# 벤치마크 실행 중 로그 확인
tail -f benchmark.log
```

---

## 🎯 권장 분석 순서

1. **알고리즘 탐지 분석** 먼저 실행
   ```bash
   python3 analyze_algorithm_detection.py
   ```

2. **그래프 생성**으로 시각화
   ```bash
   python3 visualize_results.py
   ```

3. **결과 백업** (선택)
   ```bash
   python3 utils/backup_to_gdrive.py
   ```

4. **상세 분석** (필요시)
   - CSV 변환
   - 커스텀 통계 추출

---

이 가이드를 따라하면 벤치마크 결과를 완벽하게 분석하고 시각화할 수 있습니다! 🎉
