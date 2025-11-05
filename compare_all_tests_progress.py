#!/usr/bin/env python3
"""
전체 테스트 진행 상황 비교 (Test 1, 2, 3, Final)

각 테스트의 개선 추이를 분석합니다.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

sns.set_style("whitegrid")


def calculate_metrics_from_sum(results):
    """전체 TP, FP, FN 합산 후 메트릭 계산 (에러 케이스 제외)"""
    valid_results = [r for r in results if 'error' not in r]

    total_tp = sum(r.get('true_positives', 0) for r in valid_results)
    total_fp = sum(r.get('false_positives', 0) for r in valid_results)
    total_fn = sum(r.get('false_negatives', 0) for r in valid_results)

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'tp': total_tp,
        'fp': total_fp,
        'fn': total_fn,
        'valid_count': len(valid_results),
        'error_count': len(results) - len(valid_results)
    }


def analyze_file(file_path):
    """파일 분석"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    model_name = data['benchmark_info']['test_models'][0]
    results = data['results']

    # RAG 포함/제외 분리
    rag_results = [r for r in results if r.get('with_rag', False)]
    no_rag_results = [r for r in results if not r.get('with_rag', False)]

    # 에이전트 타입별 분석
    agent_types = sorted(list(set(r.get('agent_type', 'unknown') for r in results)))

    rag_metrics_by_agent = {}
    no_rag_metrics_by_agent = {}

    for agent_type in agent_types:
        rag_agent = [r for r in rag_results if r.get('agent_type') == agent_type]
        no_rag_agent = [r for r in no_rag_results if r.get('agent_type') == agent_type]

        rag_metrics_by_agent[agent_type] = calculate_metrics_from_sum(rag_agent)
        no_rag_metrics_by_agent[agent_type] = calculate_metrics_from_sum(no_rag_agent)

    # 전체 메트릭
    overall_rag = calculate_metrics_from_sum(rag_results)
    overall_no_rag = calculate_metrics_from_sum(no_rag_results)

    return {
        'model_name': model_name,
        'agent_types': agent_types,
        'rag_by_agent': rag_metrics_by_agent,
        'no_rag_by_agent': no_rag_metrics_by_agent,
        'overall_rag': overall_rag,
        'overall_no_rag': overall_no_rag
    }


def collect_model_progress(model_files):
    """모델의 전체 진행 상황 수집"""
    progress = []

    for test_name, file_path in sorted(model_files.items()):
        if file_path and file_path.exists():
            data = analyze_file(file_path)
            progress.append({
                'test': test_name,
                'data': data
            })

    return progress


def print_model_progress(model_name, progress):
    """모델별 진행 상황 출력"""
    print(f"\n{'='*100}")
    print(f"📊 {model_name} - 전체 테스트 진행 상황")
    print(f"{'='*100}")

    print(f"\n🎯 With RAG 성능 추이:")
    print(f"{'-'*100}")
    print(f"{'Test':<10} {'F1 Score':<12} {'Precision':<12} {'Recall':<12} {'TP':<8} {'FP':<8} {'FN':<8}")
    print(f"{'-'*100}")

    for p in progress:
        test_name = p['test']
        metrics = p['data']['overall_rag']
        print(f"{test_name:<10} {metrics['f1_score']:<12.4f} {metrics['precision']:<12.4f} "
              f"{metrics['recall']:<12.4f} {metrics['tp']:<8d} {metrics['fp']:<8d} {metrics['fn']:<8d}")

    # 개선율 계산
    if len(progress) >= 2:
        first = progress[0]['data']['overall_rag']
        last = progress[-1]['data']['overall_rag']

        f1_improvement = (last['f1_score'] - first['f1_score']) / first['f1_score'] * 100 if first['f1_score'] > 0 else 0
        precision_improvement = (last['precision'] - first['precision']) / first['precision'] * 100 if first['precision'] > 0 else 0
        recall_improvement = (last['recall'] - first['recall']) / first['recall'] * 100 if first['recall'] > 0 else 0

        print(f"\n📈 전체 개선율 ({progress[0]['test']} → {progress[-1]['test']}):")
        print(f"  F1 Score:  {f1_improvement:+.1f}%")
        print(f"  Precision: {precision_improvement:+.1f}%")
        print(f"  Recall:    {recall_improvement:+.1f}%")

    print(f"\n🎯 Without RAG 성능 추이:")
    print(f"{'-'*100}")
    print(f"{'Test':<10} {'F1 Score':<12} {'Precision':<12} {'Recall':<12} {'TP':<8} {'FP':<8} {'FN':<8}")
    print(f"{'-'*100}")

    for p in progress:
        test_name = p['test']
        metrics = p['data']['overall_no_rag']
        print(f"{test_name:<10} {metrics['f1_score']:<12.4f} {metrics['precision']:<12.4f} "
              f"{metrics['recall']:<12.4f} {metrics['tp']:<8d} {metrics['fp']:<8d} {metrics['fn']:<8d}")

    # 개선율 계산
    if len(progress) >= 2:
        first = progress[0]['data']['overall_no_rag']
        last = progress[-1]['data']['overall_no_rag']

        f1_improvement = (last['f1_score'] - first['f1_score']) / first['f1_score'] * 100 if first['f1_score'] > 0 else 0
        precision_improvement = (last['precision'] - first['precision']) / first['precision'] * 100 if first['precision'] > 0 else 0
        recall_improvement = (last['recall'] - first['recall']) / first['recall'] * 100 if first['recall'] > 0 else 0

        print(f"\n📈 전체 개선율 ({progress[0]['test']} → {progress[-1]['test']}):")
        print(f"  F1 Score:  {f1_improvement:+.1f}%")
        print(f"  Precision: {precision_improvement:+.1f}%")
        print(f"  Recall:    {recall_improvement:+.1f}%")


def visualize_progress(all_model_progress, output_dir):
    """전체 진행 상황 시각화"""

    # 1. With RAG F1 Score 추이
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    fig.suptitle('Performance Progression: Test 1 → Test 2 → Test 3 → Final',
                 fontsize=16, fontweight='bold')

    # With RAG
    ax = axes[0]
    colors = {'llama3:8b': '#e74c3c', 'gemini-2.0-flash-exp': '#3498db', 'gpt-4.1': '#2ecc71'}
    markers = {'llama3:8b': 'o', 'gemini-2.0-flash-exp': 's', 'gpt-4.1': '^'}

    for model_name, progress in all_model_progress.items():
        test_names = [p['test'] for p in progress]
        f1_scores = [p['data']['overall_rag']['f1_score'] for p in progress]

        color = colors.get(model_name, 'gray')
        marker = markers.get(model_name, 'o')

        ax.plot(test_names, f1_scores, marker=marker, markersize=10, linewidth=2.5,
                label=model_name, color=color, alpha=0.8)

        # 값 표시
        for i, (test, f1) in enumerate(zip(test_names, f1_scores)):
            ax.text(i, f1 + 0.005, f'{f1:.4f}', ha='center', va='bottom',
                   fontsize=9, fontweight='bold')

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_title('With RAG Performance', fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim([0, 0.35])

    # Without RAG
    ax = axes[1]
    for model_name, progress in all_model_progress.items():
        test_names = [p['test'] for p in progress]
        f1_scores = [p['data']['overall_no_rag']['f1_score'] for p in progress]

        color = colors.get(model_name, 'gray')
        marker = markers.get(model_name, 'o')

        ax.plot(test_names, f1_scores, marker=marker, markersize=10, linewidth=2.5,
                label=model_name, color=color, alpha=0.8)

        # 값 표시
        for i, (test, f1) in enumerate(zip(test_names, f1_scores)):
            ax.text(i, f1 + 0.005, f'{f1:.4f}', ha='center', va='bottom',
                   fontsize=9, fontweight='bold')

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_title('Without RAG Performance', fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim([0, 0.35])

    plt.tight_layout()
    output_file = output_dir / 'all_tests_progression.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Saved: {output_file}")
    plt.close()

    # 2. Precision vs Recall 추이
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Precision vs Recall Progression', fontsize=16, fontweight='bold')

    # With RAG
    ax = axes[0]
    for model_name, progress in all_model_progress.items():
        precisions = [p['data']['overall_rag']['precision'] for p in progress]
        recalls = [p['data']['overall_rag']['recall'] for p in progress]
        test_names = [p['test'] for p in progress]

        color = colors.get(model_name, 'gray')
        marker = markers.get(model_name, 'o')

        ax.plot(recalls, precisions, marker=marker, markersize=10, linewidth=2.5,
                label=model_name, color=color, alpha=0.8)

        # 시작점과 끝점 표시
        ax.scatter([recalls[0]], [precisions[0]], s=200, color=color,
                  marker='o', edgecolor='black', linewidth=2, alpha=0.5, zorder=5)
        ax.scatter([recalls[-1]], [precisions[-1]], s=200, color=color,
                  marker='*', edgecolor='black', linewidth=2, zorder=5)

        # 레이블
        ax.text(recalls[0], precisions[0] - 0.02, 'Start', ha='center',
               fontsize=9, fontweight='bold')
        ax.text(recalls[-1], precisions[-1] + 0.02, 'Final', ha='center',
               fontsize=9, fontweight='bold')

    ax.set_xlabel('Recall', fontsize=13, fontweight='bold')
    ax.set_ylabel('Precision', fontsize=13, fontweight='bold')
    ax.set_title('With RAG', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 0.4])
    ax.set_ylim([0, 0.4])

    # Without RAG
    ax = axes[1]
    for model_name, progress in all_model_progress.items():
        precisions = [p['data']['overall_no_rag']['precision'] for p in progress]
        recalls = [p['data']['overall_no_rag']['recall'] for p in progress]

        color = colors.get(model_name, 'gray')
        marker = markers.get(model_name, 'o')

        ax.plot(recalls, precisions, marker=marker, markersize=10, linewidth=2.5,
                label=model_name, color=color, alpha=0.8)

        # 시작점과 끝점 표시
        ax.scatter([recalls[0]], [precisions[0]], s=200, color=color,
                  marker='o', edgecolor='black', linewidth=2, alpha=0.5, zorder=5)
        ax.scatter([recalls[-1]], [precisions[-1]], s=200, color=color,
                  marker='*', edgecolor='black', linewidth=2, zorder=5)

        # 레이블
        ax.text(recalls[0], precisions[0] - 0.02, 'Start', ha='center',
               fontsize=9, fontweight='bold')
        ax.text(recalls[-1], precisions[-1] + 0.02, 'Final', ha='center',
               fontsize=9, fontweight='bold')

    ax.set_xlabel('Recall', fontsize=13, fontweight='bold')
    ax.set_ylabel('Precision', fontsize=13, fontweight='bold')
    ax.set_title('Without RAG', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 0.4])
    ax.set_ylim([0, 0.4])

    plt.tight_layout()
    output_file = output_dir / 'precision_recall_progression.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()

    # 3. 개선율 히트맵
    fig, ax = plt.subplots(figsize=(12, 8))

    improvement_data = []
    model_labels = []

    for model_name, progress in all_model_progress.items():
        if len(progress) >= 2:
            first_rag = progress[0]['data']['overall_rag']
            last_rag = progress[-1]['data']['overall_rag']

            f1_imp = ((last_rag['f1_score'] - first_rag['f1_score']) / first_rag['f1_score'] * 100) if first_rag['f1_score'] > 0 else 0
            prec_imp = ((last_rag['precision'] - first_rag['precision']) / first_rag['precision'] * 100) if first_rag['precision'] > 0 else 0
            rec_imp = ((last_rag['recall'] - first_rag['recall']) / first_rag['recall'] * 100) if first_rag['recall'] > 0 else 0

            improvement_data.append([f1_imp, prec_imp, rec_imp])
            model_labels.append(model_name)

    improvement_array = np.array(improvement_data)

    im = ax.imshow(improvement_array, cmap='RdYlGn', aspect='auto', vmin=-20, vmax=20)

    ax.set_xticks(np.arange(3))
    ax.set_yticks(np.arange(len(model_labels)))
    ax.set_xticklabels(['F1 Score', 'Precision', 'Recall'], fontsize=12, fontweight='bold')
    ax.set_yticklabels(model_labels, fontsize=12)

    # 값 표시
    for i in range(len(model_labels)):
        for j in range(3):
            text = ax.text(j, i, f'{improvement_array[i, j]:+.1f}%',
                          ha="center", va="center", color="black",
                          fontsize=13, fontweight='bold')

    ax.set_title('Improvement Rate: First Test → Final (With RAG)',
                fontsize=14, fontweight='bold', pad=20)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Improvement (%)', rotation=270, labelpad=20, fontsize=12, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / 'improvement_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def main():
    results_dir = Path('results')
    backup_dir = results_dir / 'backup'

    # 각 모델별 테스트 파일 정의
    models = {
        'llama3:8b': {
            'test_1': backup_dir / 'llama_test_1.json',
            'test_2': backup_dir / 'llama_test_2.json',
            'test_3': backup_dir / 'llama_test_3.json',
            'final': results_dir / 'llama_final.json'
        },
        'gemini-2.0-flash-exp': {
            'test_1': backup_dir / 'gemini_test_1.json',
            'test_2': backup_dir / 'gemini_test_2.json',
            'test_3': backup_dir / 'gemini_test_3.json',
            'final': results_dir / 'gemini_final.json'
        },
        'gpt-4.1': {
            'test_3': backup_dir / 'gpt_test_3.json',
            'final': results_dir / 'gpt_final.json'
        }
    }

    print(f"\n{'='*100}")
    print(f"🔬 전체 테스트 진행 상황 분석 (Test 1 → Test 2 → Test 3 → Final)")
    print(f"{'='*100}")

    all_model_progress = {}

    for model_name, test_files in models.items():
        print(f"\n처리 중: {model_name}")
        progress = collect_model_progress(test_files)
        all_model_progress[model_name] = progress
        print_model_progress(model_name, progress)

    # 시각화
    print(f"\n{'='*100}")
    print(f"📊 시각화 생성 중...")
    print(f"{'='*100}")

    visualize_progress(all_model_progress, results_dir)

    print(f"\n{'='*100}")
    print(f"✅ 분석 완료!")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()
