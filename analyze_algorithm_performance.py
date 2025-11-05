#!/usr/bin/env python3
"""
알고리즘별 모델 성능 분석 스크립트

각 모델이 어떤 알고리즘을 잘 찾았는지 분석하고
한국 알고리즘의 정확도를 비교합니다.
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
                        # 직접 expected_findings 형식
                        ground_truth[test_id] = data
            except Exception as e:
                print(f"Warning: Failed to load {gt_file.name}: {e}")
                continue

    return ground_truth


def calculate_metrics(tp, fp, fn):
    """메트릭 계산"""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }


def analyze_by_algorithm(results, ground_truth, with_rag=True):
    """알고리즘별 성능 분석"""
    # 각 알고리즘별 TP, FP, FN 계산
    algo_stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'count': 0, 'test_cases': []})

    for result in results:
        if result.get('with_rag') != with_rag:
            continue
        if 'error' in result:
            continue

        test_id = result.get('test_id')
        if test_id not in ground_truth:
            continue

        gt = ground_truth[test_id]
        expected_algos = set(gt.get('vulnerable_algorithms_detected', []))
        detected_algos = set(result.get('raw_response', {}).get('detected_algorithms', []))

        # 각 알고리즘에 대해 개별적으로 평가
        for algo in expected_algos:
            algo_stats[algo]['count'] += 1
            algo_stats[algo]['test_cases'].append(test_id)

            if algo in detected_algos:
                algo_stats[algo]['tp'] += 1
            else:
                algo_stats[algo]['fn'] += 1

        # FP: 탐지했지만 실제로 없는 알고리즘
        for algo in detected_algos - expected_algos:
            algo_stats[algo]['fp'] += 1

    # 메트릭 계산
    algo_metrics = {}
    for algo, stats in algo_stats.items():
        metrics = calculate_metrics(stats['tp'], stats['fp'], stats['fn'])
        metrics['test_count'] = stats['count']
        algo_metrics[algo] = metrics

    return algo_metrics


def is_korean_algorithm(algo_name):
    """한국 알고리즘인지 확인"""
    korean_algos = ['ARIA', 'LEA', 'HIGHT', 'SEED']
    return any(korean in algo_name.upper() for korean in korean_algos)


def analyze_model_file(file_path, ground_truth):
    """모델 파일 분석"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    model_name = data['benchmark_info']['test_models'][0]
    results = data['results']

    # With RAG 분석
    rag_algo_metrics = analyze_by_algorithm(results, ground_truth, with_rag=True)

    # Without RAG 분석
    no_rag_algo_metrics = analyze_by_algorithm(results, ground_truth, with_rag=False)

    return {
        'model_name': model_name,
        'with_rag': rag_algo_metrics,
        'without_rag': no_rag_algo_metrics
    }


def print_algorithm_comparison(all_models_analysis):
    """알고리즘별 모델 성능 비교 출력"""

    print("\n" + "="*100)
    print("🔍 알고리즘별 모델 성능 비교 (With RAG)")
    print("="*100)

    # 모든 알고리즘 수집
    all_algorithms = set()
    for analysis in all_models_analysis:
        all_algorithms.update(analysis['with_rag'].keys())

    all_algorithms = sorted(list(all_algorithms))

    # 알고리즘별로 비교
    for algo in all_algorithms:
        korean_marker = " 🇰🇷" if is_korean_algorithm(algo) else ""
        print(f"\n📊 {algo}{korean_marker}")
        print("-" * 100)

        model_scores = []
        for analysis in all_models_analysis:
            model_name = analysis['model_name']
            if algo in analysis['with_rag']:
                metrics = analysis['with_rag'][algo]
                model_scores.append((model_name, metrics['f1_score'], metrics))
            else:
                model_scores.append((model_name, 0.0, None))

        # F1 스코어로 정렬
        model_scores.sort(key=lambda x: x[1], reverse=True)

        for rank, (model_name, f1_score, metrics) in enumerate(model_scores, 1):
            if metrics:
                print(f"  {rank}. {model_name:20s} | F1: {f1_score:.4f} | "
                      f"Precision: {metrics['precision']:.4f} | "
                      f"Recall: {metrics['recall']:.4f} | "
                      f"TP: {metrics['tp']:3d} | FP: {metrics['fp']:3d} | FN: {metrics['fn']:3d}")
            else:
                print(f"  {rank}. {model_name:20s} | No data")


def print_korean_algorithm_summary(all_models_analysis):
    """한국 알고리즘 성능 요약"""

    print("\n" + "="*100)
    print("🇰🇷 한국 알고리즘 탐지 정확도 비교")
    print("="*100)

    korean_algos_found = set()
    for analysis in all_models_analysis:
        for algo in analysis['with_rag'].keys():
            if is_korean_algorithm(algo):
                korean_algos_found.add(algo)

    if not korean_algos_found:
        print("\n⚠️  한국 알고리즘 데이터가 없습니다.")
        return

    korean_algos_found = sorted(list(korean_algos_found))

    print("\n📌 With RAG 성능:")
    print("-" * 100)

    for algo in korean_algos_found:
        print(f"\n{algo}:")

        model_results = []
        for analysis in all_models_analysis:
            model_name = analysis['model_name']
            if algo in analysis['with_rag']:
                metrics = analysis['with_rag'][algo]
                model_results.append((model_name, metrics))

        # F1 스코어로 정렬
        model_results.sort(key=lambda x: x[1]['f1_score'], reverse=True)

        for rank, (model_name, metrics) in enumerate(model_results, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
            print(f"  {medal} {model_name:20s} | "
                  f"F1: {metrics['f1_score']:.4f} | "
                  f"Precision: {metrics['precision']:.4f} | "
                  f"Recall: {metrics['recall']:.4f}")

    # RAG vs No RAG 비교
    print("\n" + "-" * 100)
    print("📌 RAG 효과 비교 (한국 알고리즘):")
    print("-" * 100)

    for model_analysis in all_models_analysis:
        model_name = model_analysis['model_name']
        print(f"\n{model_name}:")

        for algo in korean_algos_found:
            rag_f1 = 0.0
            no_rag_f1 = 0.0

            if algo in model_analysis['with_rag']:
                rag_f1 = model_analysis['with_rag'][algo]['f1_score']
            if algo in model_analysis['without_rag']:
                no_rag_f1 = model_analysis['without_rag'][algo]['f1_score']

            improvement = ((rag_f1 - no_rag_f1) / no_rag_f1 * 100) if no_rag_f1 > 0 else 0
            arrow = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"

            print(f"  {algo:15s} | With RAG: {rag_f1:.4f} | Without RAG: {no_rag_f1:.4f} | "
                  f"{arrow} {improvement:+6.1f}%")


def print_model_summary(all_models_analysis):
    """모델별 전체 성능 요약"""

    print("\n" + "="*100)
    print("📈 모델별 전체 성능 요약 (With RAG)")
    print("="*100)

    model_summaries = []

    for analysis in all_models_analysis:
        model_name = analysis['model_name']
        algo_metrics = analysis['with_rag']

        # 전체 TP, FP, FN 합산
        total_tp = sum(m['tp'] for m in algo_metrics.values())
        total_fp = sum(m['fp'] for m in algo_metrics.values())
        total_fn = sum(m['fn'] for m in algo_metrics.values())

        overall_metrics = calculate_metrics(total_tp, total_fp, total_fn)

        # 한국 알고리즘만 따로 계산
        korean_tp = sum(m['tp'] for algo, m in algo_metrics.items() if is_korean_algorithm(algo))
        korean_fp = sum(m['fp'] for algo, m in algo_metrics.items() if is_korean_algorithm(algo))
        korean_fn = sum(m['fn'] for algo, m in algo_metrics.items() if is_korean_algorithm(algo))
        korean_metrics = calculate_metrics(korean_tp, korean_fp, korean_fn)

        model_summaries.append({
            'name': model_name,
            'overall': overall_metrics,
            'korean': korean_metrics
        })

    # F1 스코어로 정렬
    model_summaries.sort(key=lambda x: x['overall']['f1_score'], reverse=True)

    print("\n전체 알고리즘:")
    for rank, summary in enumerate(model_summaries, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        metrics = summary['overall']
        print(f"{medal} {rank}. {summary['name']:20s} | "
              f"F1: {metrics['f1_score']:.4f} | "
              f"Precision: {metrics['precision']:.4f} | "
              f"Recall: {metrics['recall']:.4f}")

    # 한국 알고리즘 순위
    model_summaries.sort(key=lambda x: x['korean']['f1_score'], reverse=True)

    print("\n한국 알고리즘만:")
    for rank, summary in enumerate(model_summaries, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        metrics = summary['korean']
        print(f"{medal} {rank}. {summary['name']:20s} | "
              f"F1: {metrics['f1_score']:.4f} | "
              f"Precision: {metrics['precision']:.4f} | "
              f"Recall: {metrics['recall']:.4f}")


def main():
    results_dir = Path('results')

    files = {
        'llama': results_dir / 'llama_final.json',
        'gemini': results_dir / 'gemini_final.json',
        'gpt': results_dir / 'gpt_final.json'
    }

    # 파일 존재 확인
    for name, file_path in files.items():
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return

    print("\n" + "="*100)
    print("🔬 알고리즘별 모델 성능 분석")
    print("="*100)

    # Ground truth 로드
    print("Loading ground truth data...")
    ground_truth = load_ground_truth()
    print(f"Loaded {len(ground_truth)} test cases")

    # 모든 모델 분석
    all_models_analysis = []
    for name, file_path in files.items():
        print(f"Loading: {file_path.name}")
        analysis = analyze_model_file(file_path, ground_truth)
        all_models_analysis.append(analysis)

    # 1. 모델별 전체 성능 요약
    print_model_summary(all_models_analysis)

    # 2. 알고리즘별 비교
    print_algorithm_comparison(all_models_analysis)

    # 3. 한국 알고리즘 요약
    print_korean_algorithm_summary(all_models_analysis)

    print("\n" + "="*100)
    print("✅ 분석 완료!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
