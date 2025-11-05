#!/usr/bin/env python3
"""
Final Results 시각화 스크립트

_final.json 파일들에서 F1 Score를 추출하여 시각화합니다.
- 각 모델별 RAG vs No RAG 비교 (3개)
- 3개 모델 With RAG 비교 (1개)
- 3개 모델 Without RAG 비교 (1개)
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def calculate_metrics_from_sum(results):
    """전체 TP, FP, FN 합산 후 메트릭 계산 (에러 케이스 제외)"""
    # 'error' 플래그가 없는 케이스만 필터링
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


def load_and_process_file(file_path):
    """JSON 파일 로드 및 처리"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    model_name = data['benchmark_info']['test_models'][0]

    # RAG 포함/제외 분리
    rag_results = [r for r in results if r.get('with_rag', False)]
    no_rag_results = [r for r in results if not r.get('with_rag', False)]

    # 에이전트 타입 추출
    agent_types = sorted(list(set(r.get('agent_type', 'unknown') for r in results)))

    # 에이전트별 F1 Score 계산
    rag_f1_by_agent = []
    no_rag_f1_by_agent = []

    for agent_type in agent_types:
        rag_agent = [r for r in rag_results if r.get('agent_type') == agent_type]
        no_rag_agent = [r for r in no_rag_results if r.get('agent_type') == agent_type]

        rag_metrics = calculate_metrics_from_sum(rag_agent)
        no_rag_metrics = calculate_metrics_from_sum(no_rag_agent)

        rag_f1_by_agent.append(rag_metrics['f1_score'])
        no_rag_f1_by_agent.append(no_rag_metrics['f1_score'])

    return {
        'model_name': model_name,
        'agent_types': agent_types,
        'rag_f1': rag_f1_by_agent,
        'no_rag_f1': no_rag_f1_by_agent
    }


def visualize_individual_model(model_data, output_file):
    """개별 모델의 RAG vs No RAG 비교"""
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle(f'F1 Score by Agent Type - {model_data["model_name"]}',
                 fontsize=15, fontweight='bold')

    agent_types = model_data['agent_types']
    x = np.arange(len(agent_types))
    width = 0.35

    bars1 = ax.bar(x - width/2, model_data['rag_f1'], width,
                   label='With RAG', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, model_data['no_rag_f1'], width,
                   label='Without RAG', color='#e74c3c', alpha=0.8)

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_xlabel('Agent Type', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agent_types, fontsize=11)
    ax.legend(fontsize=12)
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # 막대 위에 값 표시
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def visualize_multi_model_comparison(all_models_data, with_rag, output_file):
    """여러 모델의 비교 (With RAG 또는 Without RAG)"""
    rag_label = "With RAG" if with_rag else "Without RAG"

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle(f'F1 Score Comparison - {rag_label}',
                 fontsize=15, fontweight='bold')

    # 모든 에이전트 타입 통합
    all_agent_types = sorted(list(set(
        agent_type
        for model_data in all_models_data
        for agent_type in model_data['agent_types']
    )))

    x = np.arange(len(all_agent_types))
    width = 0.25

    colors = {
        'llama3:8b': '#e74c3c',
        'gemini-2.0-flash': '#3498db',
        'gpt-4.1': '#2ecc71'
    }

    # 각 모델별로 막대 그리기
    for i, model_data in enumerate(all_models_data):
        model_name = model_data['model_name']

        # 해당 모델의 F1 스코어를 에이전트 타입에 맞게 정렬
        f1_scores = []
        for agent_type in all_agent_types:
            if agent_type in model_data['agent_types']:
                idx = model_data['agent_types'].index(agent_type)
                score = model_data['rag_f1'][idx] if with_rag else model_data['no_rag_f1'][idx]
                f1_scores.append(score)
            else:
                f1_scores.append(0)

        offset = (i - 1) * width
        color = colors.get(model_name, f'C{i}')
        bars = ax.bar(x + offset, f1_scores, width,
                     label=model_name, color=color, alpha=0.8)

        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_xlabel('Agent Type', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(all_agent_types, fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def main():
    results_dir = Path('results')

    # _final.json 파일들
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

    print(f"\n{'='*80}")
    print(f"Final Results Visualization")
    print(f"{'='*80}\n")

    # 모든 모델 데이터 로드
    all_models_data = []

    for name, file_path in files.items():
        print(f"Loading: {file_path.name}")
        model_data = load_and_process_file(file_path)
        all_models_data.append(model_data)

        # 1. 개별 모델 시각화
        output_file = results_dir / f'{name}_final_f1_comparison.png'
        visualize_individual_model(model_data, output_file)

    # 2. With RAG 비교
    print(f"\nGenerating combined with RAG comparison...")
    output_file = results_dir / 'all_models_with_rag_comparison.png'
    visualize_multi_model_comparison(all_models_data, with_rag=True, output_file=output_file)

    # 3. Without RAG 비교
    print(f"Generating combined without RAG comparison...")
    output_file = results_dir / 'all_models_without_rag_comparison.png'
    visualize_multi_model_comparison(all_models_data, with_rag=False, output_file=output_file)

    print(f"\n{'='*80}")
    print(f"Visualization Complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
