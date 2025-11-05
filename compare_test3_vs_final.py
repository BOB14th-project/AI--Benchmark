#!/usr/bin/env python3
"""
Test 3 vs Final 결과 비교 스크립트

3차 테스트와 최종 결과를 비교하여 개선 정도를 분석합니다.
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


def compare_versions(test3_data, final_data):
    """버전 간 비교"""
    comparison = {
        'model_name': test3_data['model_name'],
        'improvements': {}
    }

    # 전체 성능 비교
    for metric in ['f1_score', 'precision', 'recall']:
        test3_rag = test3_data['overall_rag'][metric]
        final_rag = final_data['overall_rag'][metric]
        test3_no_rag = test3_data['overall_no_rag'][metric]
        final_no_rag = final_data['overall_no_rag'][metric]

        improvement_rag = final_rag - test3_rag
        improvement_no_rag = final_no_rag - test3_no_rag
        improvement_pct_rag = (improvement_rag / test3_rag * 100) if test3_rag > 0 else 0
        improvement_pct_no_rag = (improvement_no_rag / test3_no_rag * 100) if test3_no_rag > 0 else 0

        comparison['improvements'][metric] = {
            'test3_rag': test3_rag,
            'final_rag': final_rag,
            'improvement_rag': improvement_rag,
            'improvement_pct_rag': improvement_pct_rag,
            'test3_no_rag': test3_no_rag,
            'final_no_rag': final_no_rag,
            'improvement_no_rag': improvement_no_rag,
            'improvement_pct_no_rag': improvement_pct_no_rag
        }

    # 에이전트별 비교
    agent_comparison = {}
    for agent_type in test3_data['agent_types']:
        if agent_type in final_data['agent_types']:
            test3_f1 = test3_data['rag_by_agent'][agent_type]['f1_score']
            final_f1 = final_data['rag_by_agent'][agent_type]['f1_score']
            improvement = final_f1 - test3_f1
            improvement_pct = (improvement / test3_f1 * 100) if test3_f1 > 0 else 0

            agent_comparison[agent_type] = {
                'test3': test3_f1,
                'final': final_f1,
                'improvement': improvement,
                'improvement_pct': improvement_pct
            }

    comparison['agent_comparison'] = agent_comparison

    return comparison


def print_comparison(comparison):
    """비교 결과 출력"""
    model_name = comparison['model_name']

    print(f"\n{'='*100}")
    print(f"📊 {model_name} - Test 3 vs Final 비교")
    print(f"{'='*100}")

    # 전체 성능 비교
    print(f"\n🎯 전체 성능 비교 (With RAG):")
    print(f"{'-'*100}")

    for metric in ['f1_score', 'precision', 'recall']:
        data = comparison['improvements'][metric]
        metric_name = metric.replace('_', ' ').title()

        print(f"\n{metric_name}:")
        print(f"  Test 3: {data['test3_rag']:.4f}")
        print(f"  Final:  {data['final_rag']:.4f}")

        arrow = "📈" if data['improvement_rag'] > 0 else "📉" if data['improvement_rag'] < 0 else "➡️"
        print(f"  {arrow} 변화: {data['improvement_rag']:+.4f} ({data['improvement_pct_rag']:+.1f}%)")

    print(f"\n🎯 전체 성능 비교 (Without RAG):")
    print(f"{'-'*100}")

    for metric in ['f1_score', 'precision', 'recall']:
        data = comparison['improvements'][metric]
        metric_name = metric.replace('_', ' ').title()

        print(f"\n{metric_name}:")
        print(f"  Test 3: {data['test3_no_rag']:.4f}")
        print(f"  Final:  {data['final_no_rag']:.4f}")

        arrow = "📈" if data['improvement_no_rag'] > 0 else "📉" if data['improvement_no_rag'] < 0 else "➡️"
        print(f"  {arrow} 변화: {data['improvement_no_rag']:+.4f} ({data['improvement_pct_no_rag']:+.1f}%)")

    # 에이전트별 비교
    print(f"\n📌 에이전트별 F1 Score 변화 (With RAG):")
    print(f"{'-'*100}")

    agent_comp = comparison['agent_comparison']
    for agent_type in sorted(agent_comp.keys()):
        data = agent_comp[agent_type]
        arrow = "📈" if data['improvement'] > 0 else "📉" if data['improvement'] < 0 else "➡️"

        print(f"{agent_type:20s} | Test 3: {data['test3']:.4f} | Final: {data['final']:.4f} | "
              f"{arrow} {data['improvement']:+.4f} ({data['improvement_pct']:+.1f}%)")


def visualize_comparison(all_comparisons, output_dir):
    """비교 결과 시각화"""

    # 1. 전체 F1 Score 비교
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    fig.suptitle('Test 3 vs Final - F1 Score Comparison', fontsize=16, fontweight='bold')

    # With RAG
    ax = axes[0]
    models = [comp['model_name'] for comp in all_comparisons]
    test3_rag = [comp['improvements']['f1_score']['test3_rag'] for comp in all_comparisons]
    final_rag = [comp['improvements']['f1_score']['final_rag'] for comp in all_comparisons]

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax.bar(x - width/2, test3_rag, width, label='Test 3', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, final_rag, width, label='Final', color='#2ecc71', alpha=0.8)

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_title('With RAG', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend(fontsize=12)
    ax.set_ylim([0, 0.5])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # 막대 위에 값 표시
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 개선 퍼센트 표시
    for i, comp in enumerate(all_comparisons):
        improvement_pct = comp['improvements']['f1_score']['improvement_pct_rag']
        y_pos = max(test3_rag[i], final_rag[i]) + 0.02
        arrow = "↑" if improvement_pct > 0 else "↓" if improvement_pct < 0 else "→"
        color = 'green' if improvement_pct > 0 else 'red' if improvement_pct < 0 else 'gray'
        ax.text(i, y_pos, f'{arrow}{abs(improvement_pct):.1f}%',
                ha='center', fontsize=10, fontweight='bold', color=color)

    # Without RAG
    ax = axes[1]
    test3_no_rag = [comp['improvements']['f1_score']['test3_no_rag'] for comp in all_comparisons]
    final_no_rag = [comp['improvements']['f1_score']['final_no_rag'] for comp in all_comparisons]

    bars1 = ax.bar(x - width/2, test3_no_rag, width, label='Test 3', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, final_no_rag, width, label='Final', color='#2ecc71', alpha=0.8)

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_title('Without RAG', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend(fontsize=12)
    ax.set_ylim([0, 0.5])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    for i, comp in enumerate(all_comparisons):
        improvement_pct = comp['improvements']['f1_score']['improvement_pct_no_rag']
        y_pos = max(test3_no_rag[i], final_no_rag[i]) + 0.02
        arrow = "↑" if improvement_pct > 0 else "↓" if improvement_pct < 0 else "→"
        color = 'green' if improvement_pct > 0 else 'red' if improvement_pct < 0 else 'gray'
        ax.text(i, y_pos, f'{arrow}{abs(improvement_pct):.1f}%',
                ha='center', fontsize=10, fontweight='bold', color=color)

    plt.tight_layout()
    output_file = output_dir / 'test3_vs_final_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Saved: {output_file}")
    plt.close()

    # 2. 개선율 비교
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Improvement Rate: Final vs Test 3', fontsize=16, fontweight='bold')

    improvement_rag = [comp['improvements']['f1_score']['improvement_pct_rag'] for comp in all_comparisons]
    improvement_no_rag = [comp['improvements']['f1_score']['improvement_pct_no_rag'] for comp in all_comparisons]

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax.bar(x - width/2, improvement_rag, width, label='With RAG', alpha=0.8)
    bars2 = ax.bar(x + width/2, improvement_no_rag, width, label='Without RAG', alpha=0.8)

    # 색상 설정
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            bar.set_color('#2ecc71' if height > 0 else '#e74c3c' if height < 0 else '#95a5a6')

    ax.set_ylabel('Improvement (%)', fontsize=13, fontweight='bold')
    ax.set_title('F1 Score Improvement Rate', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend(fontsize=12)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:+.1f}%',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=11, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / 'test3_vs_final_improvement_rate.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def main():
    results_dir = Path('results')
    backup_dir = results_dir / 'backup'

    models = {
        'llama': {
            'test3': backup_dir / 'llama_test_3.json',
            'final': results_dir / 'llama_final.json'
        },
        'gemini': {
            'test3': backup_dir / 'gemini_test_3.json',
            'final': results_dir / 'gemini_final.json'
        },
        'gpt': {
            'test3': backup_dir / 'gpt_test_3.json',
            'final': results_dir / 'gpt_final.json'
        }
    }

    print(f"\n{'='*100}")
    print(f"🔬 Test 3 vs Final 결과 비교 분석")
    print(f"{'='*100}")

    all_comparisons = []

    for name, files in models.items():
        if not files['test3'].exists() or not files['final'].exists():
            print(f"⚠️  Missing files for {name}")
            continue

        print(f"\n처리 중: {name}")

        test3_data = analyze_file(files['test3'])
        final_data = analyze_file(files['final'])

        comparison = compare_versions(test3_data, final_data)
        all_comparisons.append(comparison)

        print_comparison(comparison)

    # 시각화
    print(f"\n{'='*100}")
    print(f"📊 시각화 생성 중...")
    print(f"{'='*100}")

    visualize_comparison(all_comparisons, results_dir)

    print(f"\n{'='*100}")
    print(f"✅ 분석 완료!")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()
