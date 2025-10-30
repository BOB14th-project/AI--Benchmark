#!/usr/bin/env python3
"""
RAG 효과 측정 결과 시각화 스크립트

각 결과 JSON 파일을 읽어서 시각화 이미지를 생성합니다.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import argparse


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


def visualize_rag_effect(result_file: Path, output_dir: Path):
    """RAG 효과 시각화 - F1 Score by Agent Type만"""

    # 결과 파일 로드
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    benchmark_info = data['benchmark_info']
    test_models = benchmark_info.get('test_models', [])

    # 모델명 추출 (리스트의 첫 번째 모델 사용)
    model_name = test_models[0] if test_models else "Unknown Model"

    # RAG 포함/제외 분리
    rag_results = [r for r in results if r.get('with_rag', False)]
    no_rag_results = [r for r in results if not r.get('with_rag', False)]

    # Figure 생성 (단일 차트)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle(f'F1 Score by Agent Type - {model_name}', fontsize=14, fontweight='bold')

    # 에이전트별 F1 Score 계산
    agent_types = list(set(r.get('agent_type', 'unknown') for r in results))
    agent_types.sort()

    rag_f1_by_agent = []
    no_rag_f1_by_agent = []

    for agent_type in agent_types:
        rag_agent = [r for r in rag_results if r.get('agent_type') == agent_type]
        no_rag_agent = [r for r in no_rag_results if r.get('agent_type') == agent_type]

        rag_agent_metrics = calculate_metrics_from_sum(rag_agent)
        no_rag_agent_metrics = calculate_metrics_from_sum(no_rag_agent)

        rag_f1_by_agent.append(rag_agent_metrics['f1_score'])
        no_rag_f1_by_agent.append(no_rag_agent_metrics['f1_score'])

    # 막대 그래프 그리기
    x = np.arange(len(agent_types))
    width = 0.35

    bars1 = ax.bar(x - width/2, rag_f1_by_agent, width, label='With RAG', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, no_rag_f1_by_agent, width, label='Without RAG', color='#e74c3c', alpha=0.8)

    ax.set_ylabel('F1 Score', fontsize=12, fontweight='bold')
    ax.set_xlabel('Agent Type', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agent_types, rotation=15, ha='right')
    ax.legend(fontsize=11)
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # 막대 위에 값 표시
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 레이아웃 조정
    plt.tight_layout()

    # 저장
    output_file = output_dir / f"{result_file.stem}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")

    plt.close()


def main():
    parser = argparse.ArgumentParser(description="RAG 효과 측정 결과 시각화")
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('results'),
        help='결과 JSON 파일이 있는 디렉토리'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('results'),
        help='시각화 이미지를 저장할 디렉토리'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='특정 파일만 시각화 (파일명 지정)'
    )

    args = parser.parse_args()

    # 출력 디렉토리 생성
    args.output_dir.mkdir(exist_ok=True)

    # 처리할 파일 목록
    if args.files:
        json_files = [args.input_dir / f for f in args.files]
    else:
        json_files = list(args.input_dir.glob('*.json'))

    print(f"\n{'='*80}")
    print(f"🎨 RAG 효과 시각화 시작")
    print(f"{'='*80}")
    print(f"입력 디렉토리: {args.input_dir}")
    print(f"출력 디렉토리: {args.output_dir}")
    print(f"처리할 파일 수: {len(json_files)}")
    print(f"{'='*80}\n")

    # 각 파일 처리
    for json_file in json_files:
        if not json_file.exists():
            print(f"⚠️  파일 없음: {json_file}")
            continue

        print(f"📊 Processing: {json_file.name}")

        try:
            visualize_rag_effect(json_file, args.output_dir)
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}")
    print(f"✅ 시각화 완료!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
