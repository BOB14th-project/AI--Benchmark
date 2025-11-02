import json
import os
from collections import defaultdict

# 분석할 파일들
files = {
    'GPT': 'results/gpt_test_3.json',
    'Gemini': 'results/gemini_test_3.json',
    'Llama': 'results/llama_test_3.json'
}

# ground truth 폴더 경로
ground_truth_base = 'data/ground_truth'

# 모델별 암호화 알고리즘 정확도 저장
model_algorithm_stats = defaultdict(lambda: defaultdict(lambda: {'detected': 0, 'total': 0}))

# ground truth 데이터 로드 함수
def load_ground_truth(agent_type, test_id):
    """주어진 agent_type과 test_id에 대한 ground truth 로드"""
    ground_truth_path = os.path.join(ground_truth_base, agent_type, f"{test_id}.json")
    if os.path.exists(ground_truth_path):
        with open(ground_truth_path, 'r') as f:
            return json.load(f)
    return None

for model_name, file_path in files.items():
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # 각 테스트 결과 분석
        for result in data.get('results', []):
            test_id = result.get('test_id')
            agent_type = result.get('agent_type')

            # ground truth 로드
            gt = load_ground_truth(agent_type, test_id)
            if not gt or 'expected_findings' not in gt:
                continue

            expected_algorithms = gt['expected_findings'].get('vulnerable_algorithms_detected', [])
            detected_algorithms = []

            # 탐지된 알고리즘 추출
            raw_response = result.get('raw_response', {})
            if isinstance(raw_response, dict):
                detected_algorithms = raw_response.get('detected_algorithms', [])

            # 각 예상 알고리즘에 대해 탐지 여부 확인
            for algo in expected_algorithms:
                model_algorithm_stats[model_name][algo]['total'] += 1
                if algo in detected_algorithms:
                    model_algorithm_stats[model_name][algo]['detected'] += 1

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        import traceback
        traceback.print_exc()

# 결과 출력
print("=" * 80)
print("모델별 암호화 알고리즘 탐지 성능 분석 (test_3 결과)")
print("=" * 80)

for model_name in ['GPT', 'Gemini', 'Llama']:
    print(f"\n{'='*80}")
    print(f"{model_name} 모델")
    print(f"{'='*80}")

    if model_name not in model_algorithm_stats:
        print("데이터 없음")
        continue

    # 알고리즘별 탐지율 계산 및 정렬
    algorithm_accuracy = []
    for algorithm, stats in model_algorithm_stats[model_name].items():
        detection_rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0
        algorithm_accuracy.append({
            'algorithm': algorithm,
            'detection_rate': detection_rate,
            'detected': stats['detected'],
            'total': stats['total']
        })

    # 탐지율 순으로 정렬
    algorithm_accuracy.sort(key=lambda x: x['detection_rate'], reverse=True)

    # 출력
    print(f"\n{'알고리즘':<20} {'탐지율':<10} {'탐지수/전체':<15}")
    print("-" * 50)
    for item in algorithm_accuracy:
        print(f"{item['algorithm']:<20} {item['detection_rate']:>6.2f}%  {item['detected']:>3}/{item['total']:<3}")

# 각 알고리즘별로 어떤 모델이 가장 잘하는지 찾기
print(f"\n\n{'='*80}")
print("알고리즘별 최고 성능 모델")
print(f"{'='*80}\n")

all_algorithms = set()
for model_stats in model_algorithm_stats.values():
    all_algorithms.update(model_stats.keys())

algorithm_best_model = []
for algorithm in sorted(all_algorithms):
    best_model = None
    best_detection_rate = 0

    for model_name in ['GPT', 'Gemini', 'Llama']:
        if algorithm in model_algorithm_stats[model_name]:
            stats = model_algorithm_stats[model_name][algorithm]
            detection_rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0

            if detection_rate > best_detection_rate:
                best_detection_rate = detection_rate
                best_model = model_name

    if best_model:
        algorithm_best_model.append({
            'algorithm': algorithm,
            'best_model': best_model,
            'detection_rate': best_detection_rate
        })

print(f"{'알고리즘':<20} {'최고 성능 모델':<15} {'탐지율':<10}")
print("-" * 50)
for item in sorted(algorithm_best_model, key=lambda x: x['algorithm']):
    print(f"{item['algorithm']:<20} {item['best_model']:<15} {item['detection_rate']:>6.2f}%")

# 모델별로 가장 잘 찾는 알고리즘 Top 5
print(f"\n\n{'='*80}")
print("모델별 가장 잘 탐지하는 알고리즘 Top 5")
print(f"{'='*80}")

for model_name in ['GPT', 'Gemini', 'Llama']:
    if model_name not in model_algorithm_stats:
        continue

    print(f"\n{model_name}:")
    print("-" * 40)

    algorithm_accuracy = []
    for algorithm, stats in model_algorithm_stats[model_name].items():
        detection_rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0
        algorithm_accuracy.append({
            'algorithm': algorithm,
            'detection_rate': detection_rate,
            'detected': stats['detected'],
            'total': stats['total']
        })

    algorithm_accuracy.sort(key=lambda x: x['detection_rate'], reverse=True)

    for i, item in enumerate(algorithm_accuracy[:5], 1):
        print(f"{i}. {item['algorithm']:<20} {item['detection_rate']:>6.2f}% ({item['detected']}/{item['total']})")
