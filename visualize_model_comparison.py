#!/usr/bin/env python3
"""
모델별 RAG 성능 비교 시각화 스크립트

llama, gemini, gpt test_3 파일에서 With RAG 성능만 비교합니다.
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


def visualize_model_comparison(result_files: list, output_file: Path):
    """3개 모델의 With RAG 성능 비교"""

    # 각 모델의 데이터 로드
    models_data = {}

    for file_path in result_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 모델명 추출
        model_name = data['benchmark_info']['test_models'][0]

        # With RAG 결과만 필터링
        rag_results = [r for r in data['results'] if r.get('with_rag', False)]

        models_data[model_name] = rag_results

    # 모든 에이전트 타입 추출
    all_agent_types = set()
    for results in models_data.values():
        for r in results:
            all_agent_types.add(r.get('agent_type', 'unknown'))

    agent_types = sorted(list(all_agent_types))

    # 각 모델별, 에이전트별 F1 Score 계산
    model_names = list(models_data.keys())
    f1_scores = {model: [] for model in model_names}

    for agent_type in agent_types:
        for model_name, results in models_data.items():
            agent_results = [r for r in results if r.get('agent_type') == agent_type]
            metrics = calculate_metrics_from_sum(agent_results)
            f1_scores[model_name].append(metrics['f1_score'])

    # Figure 생성
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Model Comparison - F1 Score by Agent Type (With RAG Only)',
                 fontsize=15, fontweight='bold')

    # 막대 그래프 그리기
    x = np.arange(len(agent_types))
    width = 0.25  # 3개 모델이므로 좁게

    colors = {
        'llama3:8b': '#e74c3c',
        'gemini-2.0-flash': '#3498db',
        'gpt-4.1': '#2ecc71'
    }

    # 각 모델별로 막대 그리기
    bars_list = []
    for i, model_name in enumerate(model_names):
        offset = (i - 1) * width  # -1, 0, 1
        color = colors.get(model_name, f'C{i}')
        bars = ax.bar(x + offset, f1_scores[model_name], width,
                     label=model_name, color=color, alpha=0.8)
        bars_list.append(bars)

    # 축 설정
    ax.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
    ax.set_xlabel('Agent Type', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agent_types, fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # 막대 위에 값 표시
    for bars in bars_list:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 레이아웃 조정
    plt.tight_layout()

    # 저장
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")

    plt.close()


def main():
    # 입력 파일들
    results_dir = Path('results')
    result_files = [
        results_dir / 'llama_test_3.json',
        results_dir / 'gemini_test_3.json',
        results_dir / 'gpt_test_3.json'
    ]

    # 모든 파일이 존재하는지 확인
    for file_path in result_files:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return

    print(f"\n{'='*80}")
    print(f"🎨 모델 비교 시각화 시작")
    print(f"{'='*80}")
    print(f"비교 모델:")
    for file_path in result_files:
        print(f"  - {file_path.name}")
    print(f"{'='*80}\n")

    # 출력 파일
    output_file = results_dir / 'model_comparison_test3.png'

    # 시각화 생성
    visualize_model_comparison(result_files, output_file)

    print(f"\n{'='*80}")
    print(f"✅ 시각화 완료!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
