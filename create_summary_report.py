#!/usr/bin/env python3
"""
주요 알고리즘별 성능 요약 리포트
"""

import json
from pathlib import Path
from collections import defaultdict


def load_ground_truth():
    """Ground truth 데이터 로드"""
    ground_truth_dir = Path('data/ground_truth')
    ground_truth = {}

    for category_dir in ground_truth_dir.iterdir():
        if not category_dir.is_dir():
            continue

        for gt_file in category_dir.glob('*.json'):
            test_id = gt_file.stem
            try:
                with open(gt_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'expected_findings' in data:
                        ground_truth[test_id] = data['expected_findings']
                    elif 'vulnerable_algorithms_detected' in data:
                        ground_truth[test_id] = data
            except Exception:
                continue

    return ground_truth


def analyze_algorithm_detection(file_path, ground_truth):
    """알고리즘별 탐지 성능 분석"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    model_name = data['benchmark_info']['test_models'][0]
    results = [r for r in data['results'] if r.get('with_rag', False) and 'error' not in r]

    algo_stats = defaultdict(lambda: {'tp': 0, 'fn': 0, 'test_cases': 0})

    for result in results:
        test_id = result.get('test_id')
        if test_id not in ground_truth:
            continue

        gt = ground_truth[test_id]
        expected_algos = set(gt.get('vulnerable_algorithms_detected', []))
        detected_algos = set(result.get('raw_response', {}).get('detected_algorithms', []))

        for algo in expected_algos:
            algo_stats[algo]['test_cases'] += 1
            if algo in detected_algos:
                algo_stats[algo]['tp'] += 1
            else:
                algo_stats[algo]['fn'] += 1

    # F1 스코어 계산
    algo_f1 = {}
    for algo, stats in algo_stats.items():
        tp = stats['tp']
        fn = stats['fn']
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        # Precision은 FP가 필요하지만 여기서는 간단히 recall만 사용
        algo_f1[algo] = {
            'recall': recall,
            'tp': tp,
            'fn': fn,
            'test_cases': stats['test_cases']
        }

    return model_name, algo_f1


def is_korean_algorithm(algo_name):
    """한국 알고리즘인지 확인"""
    korean_algos = ['ARIA', 'LEA', 'HIGHT', 'SEED']
    return any(korean in algo_name.upper() for korean in korean_algos)


def main():
    results_dir = Path('results')
    files = [
        results_dir / 'llama_final.json',
        results_dir / 'gemini_final.json',
        results_dir / 'gpt_final.json'
    ]

    print("\n" + "="*100)
    print("📊 알고리즘별 모델 탐지 성능 요약")
    print("="*100)

    ground_truth = load_ground_truth()
    print(f"Loaded {len(ground_truth)} test cases\n")

    # 모델별 분석
    all_models = {}
    for file_path in files:
        model_name, algo_f1 = analyze_algorithm_detection(file_path, ground_truth)
        all_models[model_name] = algo_f1

    # 주요 알고리즘만 필터링
    major_algos = ['RSA', 'ECC', 'ECDSA', 'AES', 'DES', '3DES', 'SHA-1', 'SHA-256',
                   'MD5', 'DSA', 'DH', 'ChaCha20', 'BLAKE2b', 'Blowfish']

    # 한국 알고리즘
    korean_algos = ['ARIA', 'LEA', 'HIGHT', 'SEED']

    # 1. 주요 국제 알고리즘 성능
    print("="*100)
    print("🌍 주요 국제 암호 알고리즘 탐지 성능")
    print("="*100)

    for algo in major_algos:
        # 각 모델의 성능 수집
        model_scores = []
        for model_name, algo_data in all_models.items():
            if algo in algo_data:
                model_scores.append((model_name, algo_data[algo]))
            else:
                model_scores.append((model_name, None))

        # 결과 출력
        has_data = any(score is not None for _, score in model_scores)
        if has_data:
            print(f"\n📌 {algo}")
            print("-" * 100)

            # Recall로 정렬
            model_scores.sort(key=lambda x: x[1]['recall'] if x[1] else 0, reverse=True)

            for rank, (model_name, data) in enumerate(model_scores, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                if data:
                    recall_pct = data['recall'] * 100
                    print(f"  {medal} {model_name:25s} | Recall: {recall_pct:5.1f}% | "
                          f"Detected: {data['tp']:3d}/{data['test_cases']:3d}")
                else:
                    print(f"  {rank}. {model_name:25s} | No data")

    # 2. 한국 알고리즘 성능
    print("\n" + "="*100)
    print("🇰🇷 한국 암호 알고리즘 탐지 성능")
    print("="*100)

    for algo in korean_algos:
        # 각 모델의 성능 수집
        model_scores = []
        for model_name, algo_data in all_models.items():
            if algo in algo_data:
                model_scores.append((model_name, algo_data[algo]))
            else:
                model_scores.append((model_name, None))

        # 결과 출력
        has_data = any(score is not None for _, score in model_scores)
        if has_data:
            print(f"\n📌 {algo}")
            print("-" * 100)

            # Recall로 정렬
            model_scores.sort(key=lambda x: x[1]['recall'] if x[1] else 0, reverse=True)

            for rank, (model_name, data) in enumerate(model_scores, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                if data:
                    recall_pct = data['recall'] * 100
                    print(f"  {medal} {model_name:25s} | Recall: {recall_pct:5.1f}% | "
                          f"Detected: {data['tp']:3d}/{data['test_cases']:3d}")
                else:
                    print(f"  {rank}. {model_name:25s} | No data")

    # 3. 종합 요약
    print("\n" + "="*100)
    print("📈 모델별 종합 성능 요약")
    print("="*100)

    for model_name, algo_data in all_models.items():
        print(f"\n{model_name}:")

        # 전체 알고리즘 통계
        total_tp = sum(d['tp'] for d in algo_data.values())
        total_test_cases = sum(d['test_cases'] for d in algo_data.values())
        overall_recall = total_tp / total_test_cases if total_test_cases > 0 else 0

        # 한국 알고리즘만 통계
        korean_tp = sum(d['tp'] for algo, d in algo_data.items() if is_korean_algorithm(algo))
        korean_test_cases = sum(d['test_cases'] for algo, d in algo_data.items() if is_korean_algorithm(algo))
        korean_recall = korean_tp / korean_test_cases if korean_test_cases > 0 else 0

        print(f"  전체 알고리즘: {overall_recall*100:5.1f}% recall ({total_tp}/{total_test_cases})")
        print(f"  한국 알고리즘: {korean_recall*100:5.1f}% recall ({korean_tp}/{korean_test_cases})")

        # 가장 잘 찾은 알고리즘 Top 5
        top_algos = sorted(algo_data.items(), key=lambda x: x[1]['recall'], reverse=True)[:5]
        print(f"  가장 잘 탐지한 알고리즘:")
        for algo, data in top_algos:
            if data['recall'] > 0:
                print(f"    - {algo:20s}: {data['recall']*100:5.1f}% ({data['tp']}/{data['test_cases']})")

    print("\n" + "="*100)
    print("✅ 요약 완료!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
