#!/usr/bin/env python3
"""
모델 성능 비교 시각화 도구
- 성공률, 응답시간, Precision/Recall/F1 비교
"""

import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_results(file_path):
    """결과 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_success_rate(summary, output_dir):
    """모델별 성공률 시각화"""
    models = []
    success_rates = []
    total_tests = []

    for model, stats in summary.get('by_model', {}).items():
        if 'unknown' in model:
            continue
        models.append(model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', ''))
        success_rate = stats.get('successful', 0) / stats.get('total', 1) if stats.get('total', 0) > 0 else 0
        success_rates.append(success_rate * 100)
        total_tests.append(stats.get('total', 0))

    # Sort by success rate
    sorted_data = sorted(zip(models, success_rates, total_tests), key=lambda x: x[1], reverse=True)
    models, success_rates, total_tests = zip(*sorted_data)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(models, success_rates, color='skyblue', edgecolor='navy')

    # Add values on bars
    for i, (bar, rate, total) in enumerate(zip(bars, success_rates, total_tests)):
        ax.text(rate + 1, i, f'{rate:.1f}% ({int(rate * total / 100)}/{total})',
                va='center', fontsize=9)

    ax.set_xlabel('Success Rate (%)', fontsize=12)
    ax.set_title('Model Success Rate Comparison', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/model_success_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_dir}/model_success_rate.png')


def plot_response_time(summary, output_dir):
    """모델별 응답 시간 시각화"""
    models = []
    response_times = []

    for model, stats in summary.get('by_model', {}).items():
        if 'unknown' in model:
            continue
        # Get provider stats for avg response time
        provider = model.split('/')[0] if '/' in model else 'unknown'
        avg_time = summary.get('by_provider', {}).get(provider, {}).get('avg_response_time', 0)

        models.append(model.replace('ollama/', '').replace('google/', '').replace('openai/', '').replace('xai/', ''))
        response_times.append(avg_time)

    # Sort by response time
    sorted_data = sorted(zip(models, response_times), key=lambda x: x[1])
    models, response_times = zip(*sorted_data)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(models, response_times, color='lightcoral', edgecolor='darkred')

    # Add values on bars
    for i, (bar, time) in enumerate(zip(bars, response_times)):
        ax.text(time + 0.5, i, f'{time:.2f}s', va='center', fontsize=9)

    ax.set_xlabel('Average Response Time (seconds)', fontsize=12)
    ax.set_title('Model Response Time Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/model_response_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_dir}/model_response_time.png')


def plot_provider_comparison(summary, output_dir):
    """프로바이더별 종합 비교"""
    providers = []
    success_rates = []
    avg_times = []
    total_tests = []

    for provider, stats in summary.get('by_provider', {}).items():
        if provider == 'unknown':
            continue
        providers.append(provider.upper())
        success_rate = stats.get('successful', 0) / stats.get('total', 1) if stats.get('total', 0) > 0 else 0
        success_rates.append(success_rate * 100)
        avg_times.append(stats.get('avg_response_time', 0))
        total_tests.append(stats.get('total', 0))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Success rate
    bars1 = ax1.bar(providers, success_rates, color='lightgreen', edgecolor='darkgreen')
    for bar, rate, total in zip(bars1, success_rates, total_tests):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%\n({int(rate * total / 100)}/{total})',
                ha='center', va='bottom', fontsize=9)

    ax1.set_ylabel('Success Rate (%)', fontsize=11)
    ax1.set_title('Success Rate by Provider', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, max(success_rates) * 1.15)
    ax1.grid(axis='y', alpha=0.3)

    # Response time
    bars2 = ax2.bar(providers, avg_times, color='lightyellow', edgecolor='orange')
    for bar, time in zip(bars2, avg_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{time:.2f}s',
                ha='center', va='bottom', fontsize=9)

    ax2.set_ylabel('Avg Response Time (s)', fontsize=11)
    ax2.set_title('Response Time by Provider', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, max(avg_times) * 1.15)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/provider_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_dir}/provider_comparison.png')


def plot_agent_distribution(summary, output_dir):
    """에이전트별 테스트 분포"""
    agents = []
    totals = []
    successful = []

    for agent, stats in summary.get('by_agent', {}).items():
        agents.append(agent.replace('_', ' ').title())
        totals.append(stats.get('total', 0))
        successful.append(stats.get('successful', 0))

    if not agents:
        return

    x = np.arange(len(agents))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, totals, width, label='Total Tests', color='lightblue', edgecolor='navy')
    bars2 = ax.bar(x + width/2, successful, width, label='Successful', color='lightgreen', edgecolor='darkgreen')

    # Add values on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Number of Tests', fontsize=11)
    ax.set_title('Test Distribution by Agent Type', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agents)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/agent_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ 저장: {output_dir}/agent_distribution.png')


def main():
    parser = argparse.ArgumentParser(description='모델 성능 비교 시각화')
    parser.add_argument('--file', type=str, required=True, help='벤치마크 결과 JSON 파일')
    parser.add_argument('--output-dir', type=str, default='.', help='출력 디렉토리')

    args = parser.parse_args()

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load results
    print(f'✅ 결과 파일 로드: {args.file}\n')
    results = load_results(args.file)
    summary = results.get('summary', {})

    print('📊 모델 성능 그래프 생성 중...\n')

    # Generate plots
    plot_success_rate(summary, args.output_dir)
    plot_response_time(summary, args.output_dir)
    plot_provider_comparison(summary, args.output_dir)
    plot_agent_distribution(summary, args.output_dir)

    print('\n✅ 모든 성능 그래프 생성 완료!')


if __name__ == '__main__':
    main()
