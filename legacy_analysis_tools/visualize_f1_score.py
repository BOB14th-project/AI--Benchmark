#!/usr/bin/env python3
"""
F1 Score 시각화 도구
- 모델별 F1 Score 비교
- Precision, Recall, F1 Score 함께 시각화
"""

import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_ground_truth(test_id, agent_type):
    """
    테스트 케이스의 ground truth 로드
    """
    ground_truth_base = Path('data/ground_truth')

    # agent_type에 맞는 서브디렉토리 선택
    agent_dir = ground_truth_base / agent_type

    if not agent_dir.exists():
        return set()

    # Try to find the ground truth file
    file_path = agent_dir / f"{test_id}.json"

    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract quantum vulnerable algorithms from expected_findings
                expected_findings = data.get('expected_findings', {})
                vulnerable_algorithms = expected_findings.get('vulnerable_algorithms_detected', [])
                korean_algorithms = expected_findings.get('korean_algorithms_detected', [])

                # Combine all algorithms
                all_algorithms = vulnerable_algorithms + korean_algorithms
                return set([alg.lower().strip() for alg in all_algorithms])
        except Exception as e:
            print(f"Warning: Error loading ground truth for {test_id}: {e}")
            return set()

    return set()


def extract_algorithm_names(detected_algorithms):
    """
    detected_algorithms에서 알고리즘명만 추출
    예: "RSA (EVIDENCE: ...)" -> "rsa"
    """
    import re

    algorithm_names = set()

    for alg_str in detected_algorithms:
        # 괄호와 그 안의 내용 제거
        alg_clean = re.sub(r'\s*\(.*?\)', '', alg_str, flags=re.IGNORECASE)

        # 쉼표로 구분된 알고리즘들 분리
        for alg in alg_clean.split(','):
            alg = alg.strip().lower()
            if alg:
                # 주요 알고리즘 키워드 추출
                keywords = ['rsa', 'ecc', 'ecdsa', 'ecdh', 'dsa', 'dh', 'elgamal',
                           'aes', 'aes-128', 'aes-256', '3des', 'des', 'rc4',
                           'md5', 'sha-1', 'sha-256', 'sha1', 'sha256',
                           'seed', 'aria', 'hight', 'lea', 'kcdsa', 'ec-kcdsa',
                           'has-160', 'lsh']

                for keyword in keywords:
                    if keyword in alg:
                        algorithm_names.add(keyword)

    return algorithm_names


def calculate_precision_recall_f1(detected, ground_truth):
    """
    Precision, Recall, F1 계산
    """
    if not ground_truth:
        return 0.0, 0.0, 0.0

    # detected_algorithms에서 알고리즘명 추출
    detected_set = extract_algorithm_names(detected)
    ground_truth_set = set([alg.lower().strip() for alg in ground_truth])

    # True Positives: 정확히 탐지된 것
    true_positives = len(detected_set & ground_truth_set)

    # False Positives: 잘못 탐지된 것
    false_positives = len(detected_set - ground_truth_set)

    # False Negatives: 놓친 것
    false_negatives = len(ground_truth_set - detected_set)

    # Precision
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0

    # Recall
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0

    # F1 Score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def load_results(file_path):
    """결과 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_model_metrics(results):
    """
    모델별 Precision, Recall, F1 Score 계산
    """
    model_metrics = defaultdict(lambda: {'precision': [], 'recall': [], 'f1': []})

    for result in results.get('detailed_results', []):
        model = result.get('model', 'unknown')
        agent_type = result.get('agent_type', 'unknown')

        if model == 'unknown' or agent_type == 'unknown' or not result.get('success'):
            continue

        test_id = result.get('test_id')
        detected_algorithms = result.get('detected_algorithms', [])

        # Load ground truth
        ground_truth = load_ground_truth(test_id, agent_type)

        if ground_truth:
            precision, recall, f1 = calculate_precision_recall_f1(detected_algorithms, ground_truth)

            model_metrics[model]['precision'].append(precision)
            model_metrics[model]['recall'].append(recall)
            model_metrics[model]['f1'].append(f1)

    # 평균 계산
    model_avg_metrics = {}
    for model, metrics in model_metrics.items():
        model_avg_metrics[model] = {
            'precision': np.mean(metrics['precision']) if metrics['precision'] else 0.0,
            'recall': np.mean(metrics['recall']) if metrics['recall'] else 0.0,
            'f1': np.mean(metrics['f1']) if metrics['f1'] else 0.0,
            'count': len(metrics['f1'])
        }

    return model_avg_metrics


def plot_f1_score_comparison(model_metrics, output_dir):
    """
    모델별 F1 Score 비교 그래프
    """
    # 모델명 정리
    models = []
    f1_scores = []
    counts = []

    for model, metrics in sorted(model_metrics.items(), key=lambda x: x[1]['f1'], reverse=True):
        # 모델명 간소화
        model_name = model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', '')
        models.append(model_name)
        f1_scores.append(metrics['f1'] * 100)  # 퍼센트로 변환
        counts.append(metrics['count'])

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(12, 7))

    # 색상 설정
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(models)))
    bars = ax.barh(models, f1_scores, color=colors, edgecolor='black', linewidth=1.2)

    # 값 표시
    for i, (bar, score, count) in enumerate(zip(bars, f1_scores, counts)):
        ax.text(score + 1, i, f'{score:.2f}% (n={count})',
                va='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('F1 Score (%)', fontsize=13, fontweight='bold')
    ax.set_title('Model F1 Score Comparison\n(Quantum-Vulnerable Algorithm Detection)',
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlim(0, max(f1_scores) * 1.15 if f1_scores else 100)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    output_path = f'{output_dir}/model_f1_score.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_path}')


def plot_precision_recall_f1(model_metrics, output_dir):
    """
    Precision, Recall, F1 Score 함께 비교
    """
    # 데이터 준비
    models = []
    precisions = []
    recalls = []
    f1_scores = []

    for model, metrics in sorted(model_metrics.items(), key=lambda x: x[1]['f1'], reverse=True):
        model_name = model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', '')
        models.append(model_name)
        precisions.append(metrics['precision'] * 100)
        recalls.append(metrics['recall'] * 100)
        f1_scores.append(metrics['f1'] * 100)

    # 그래프 생성
    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 7))

    bars1 = ax.bar(x - width, precisions, width, label='Precision',
                   color='skyblue', edgecolor='navy', linewidth=1.2)
    bars2 = ax.bar(x, recalls, width, label='Recall',
                   color='lightcoral', edgecolor='darkred', linewidth=1.2)
    bars3 = ax.bar(x + width, f1_scores, width, label='F1 Score',
                   color='lightgreen', edgecolor='darkgreen', linewidth=1.2)

    # 값 표시
    def add_values(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=8)

    add_values(bars1)
    add_values(bars2)
    add_values(bars3)

    ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Precision, Recall, and F1 Score by Model\n(Quantum-Vulnerable Algorithm Detection)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, max(max(precisions), max(recalls), max(f1_scores)) * 1.15 if f1_scores else 100)

    plt.tight_layout()
    output_path = f'{output_dir}/model_precision_recall_f1.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_path}')


def plot_f1_radar_chart(model_metrics, output_dir):
    """
    레이더 차트로 Precision, Recall, F1 비교
    """
    # 상위 6개 모델만 선택
    top_models = sorted(model_metrics.items(), key=lambda x: x[1]['f1'], reverse=True)[:6]

    # 각도 설정
    categories = ['Precision', 'Recall', 'F1 Score']
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 닫힌 도형을 만들기 위해

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    colors = plt.cm.Set3(np.linspace(0, 1, len(top_models)))

    for idx, (model, metrics) in enumerate(top_models):
        model_name = model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', '')

        values = [
            metrics['precision'] * 100,
            metrics['recall'] * 100,
            metrics['f1'] * 100
        ]
        values += values[:1]  # 닫힌 도형

        ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.set_title('Top 6 Models: Precision, Recall, F1 Score Comparison\n(Radar Chart)',
                 fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    output_path = f'{output_dir}/model_f1_radar.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_path}')


def print_summary(model_metrics):
    """
    모델별 메트릭 요약 출력
    """
    print('\n' + '='*80)
    print('📊 Model F1 Score Summary (Quantum-Vulnerable Algorithm Detection)')
    print('='*80)
    print(f"{'Model':<25} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Tests':<8}")
    print('-'*80)

    for model, metrics in sorted(model_metrics.items(), key=lambda x: x[1]['f1'], reverse=True):
        model_name = model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', '')
        print(f"{model_name:<25} {metrics['precision']*100:>10.2f}% {metrics['recall']*100:>10.2f}% "
              f"{metrics['f1']*100:>10.2f}% {metrics['count']:>8}")

    print('='*80 + '\n')


def main():
    parser = argparse.ArgumentParser(description='F1 Score 시각화')
    parser.add_argument('--file', type=str, default='benchmark_results_2.json',
                        help='벤치마크 결과 JSON 파일')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='출력 디렉토리')

    args = parser.parse_args()

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load results
    print(f'✅ 결과 파일 로드: {args.file}\n')
    results = load_results(args.file)

    # Calculate metrics
    print('📊 모델별 F1 Score 계산 중...\n')
    model_metrics = calculate_model_metrics(results)

    if not model_metrics:
        print('❌ F1 Score를 계산할 수 있는 데이터가 없습니다.')
        print('   Ground truth 파일이 data/ground_truth/ 디렉토리에 있는지 확인하세요.')
        return

    # Print summary
    print_summary(model_metrics)

    # Generate plots
    print('📊 F1 Score 그래프 생성 중...\n')
    plot_f1_score_comparison(model_metrics, args.output_dir)
    plot_precision_recall_f1(model_metrics, args.output_dir)
    plot_f1_radar_chart(model_metrics, args.output_dir)

    print('\n✅ 모든 F1 Score 그래프 생성 완료!')


if __name__ == '__main__':
    main()
