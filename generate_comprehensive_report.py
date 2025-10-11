#!/usr/bin/env python3
"""
종합 분석 보고서 생성 도구
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


def load_results(file_path):
    """결과 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_report(results_file, output_file):
    """종합 보고서 생성"""
    results = load_results(results_file)
    summary = results.get('summary', {})
    metadata = results.get('metadata', {})

    report = []
    report.append("=" * 100)
    report.append("📊 AI 벤치마크 종합 분석 보고서")
    report.append("   양자 취약 암호 알고리즘 탐지 성능 평가")
    report.append("=" * 100)
    report.append("")

    # 1. 실행 정보
    report.append("## 1️⃣ 실행 정보")
    report.append("-" * 100)
    report.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"결과 파일: {results_file}")
    report.append(f"총 테스트: {summary.get('total_tests', 0)}개")
    report.append(f"성공 테스트: {summary.get('successful_tests', 0)}개")
    report.append(f"성공률: {summary.get('success_rate', 0) * 100:.1f}%")
    report.append(f"테스트 제한: {metadata.get('test_limit', 'N/A')}")
    report.append("")

    # 2. 프로바이더별 성능
    report.append("## 2️⃣ 프로바이더별 성능")
    report.append("-" * 100)
    report.append(f"{'프로바이더':<15} {'성공/전체':<15} {'성공률':<10} {'평균 응답시간':<15} {'평균 신뢰도':<12}")
    report.append("-" * 100)

    for provider, stats in summary.get('by_provider', {}).items():
        if provider == 'unknown':
            continue
        total = stats.get('total', 0)
        successful = stats.get('successful', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_time = stats.get('avg_response_time', 0)
        avg_conf = stats.get('avg_confidence', 0)

        report.append(f"{provider.upper():<15} {f'{successful}/{total}':<15} {success_rate:<10.1f}% {avg_time:<15.2f}s {avg_conf:<12.3f}")

    report.append("")

    # 3. 모델별 성능
    report.append("## 3️⃣ 모델별 성능")
    report.append("-" * 100)
    report.append(f"{'모델':<30} {'성공/전체':<15} {'성공률':<10}")
    report.append("-" * 100)

    model_performance = []
    for model, stats in summary.get('by_model', {}).items():
        if 'unknown' in model:
            continue
        total = stats.get('total', 0)
        successful = stats.get('successful', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        model_performance.append((model, successful, total, success_rate))

    # Sort by success rate
    model_performance.sort(key=lambda x: x[3], reverse=True)

    for i, (model, successful, total, success_rate) in enumerate(model_performance, 1):
        medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '  '
        report.append(f"{medal} {model:<28} {f'{successful}/{total}':<15} {success_rate:<10.1f}%")

    report.append("")

    # 4. 에이전트별 분포
    report.append("## 4️⃣ 에이전트별 테스트 분포")
    report.append("-" * 100)
    report.append(f"{'에이전트':<30} {'전체 테스트':<15} {'성공 테스트':<15} {'성공률':<10}")
    report.append("-" * 100)

    for agent, stats in summary.get('by_agent', {}).items():
        total = stats.get('total', 0)
        successful = stats.get('successful', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        report.append(f"{agent.replace('_', ' ').title():<30} {total:<15} {successful:<15} {success_rate:<10.1f}%")

    report.append("")

    # 5. 주요 발견사항
    report.append("## 5️⃣ 주요 발견사항")
    report.append("-" * 100)

    # Best model
    if model_performance:
        best_model = model_performance[0]
        report.append(f"✅ 최고 성능 모델: {best_model[0]}")
        report.append(f"   - 성공률: {best_model[3]:.1f}% ({best_model[1]}/{best_model[2]})")
        report.append("")

    # Provider comparison
    provider_perf = []
    for provider, stats in summary.get('by_provider', {}).items():
        if provider != 'unknown':
            total = stats.get('total', 0)
            successful = stats.get('successful', 0)
            success_rate = (successful / total * 100) if total > 0 else 0
            provider_perf.append((provider, success_rate, stats.get('avg_response_time', 0)))

    provider_perf.sort(key=lambda x: x[1], reverse=True)

    if provider_perf:
        report.append("📊 프로바이더 순위 (성공률 기준):")
        for i, (provider, rate, time) in enumerate(provider_perf, 1):
            report.append(f"   {i}. {provider.upper()}: {rate:.1f}% (평균 {time:.2f}s)")
        report.append("")

    # Fastest model
    fastest_provider = min(provider_perf, key=lambda x: x[2]) if provider_perf else None
    if fastest_provider:
        report.append(f"⚡ 가장 빠른 프로바이더: {fastest_provider[0].upper()} ({fastest_provider[2]:.2f}s)")
        report.append("")

    # 6. 생성된 파일
    report.append("## 6️⃣ 생성된 파일")
    report.append("-" * 100)
    report.append("분석 결과:")
    report.append("  - algorithm_detection_overall.txt    : 전체 알고리즘 탐지 분석")
    report.append("  - algorithm_detection_by_model.txt   : 모델별 알고리즘 탐지 분석")
    report.append("  - precision_recall_summary.txt       : Precision/Recall/F1 분석")
    report.append("")
    report.append("시각화 그래프:")
    report.append("  - algorithm_detection_overall.png    : 전체 알고리즘 탐지율")
    report.append("  - algorithm_detection_by_model.png   : 모델별 알고리즘 비교")
    report.append("  - algorithm_success_failure.png      : 성공/실패 분석")
    report.append("  - algorithm_top_bottom.png           : 상위/하위 알고리즘")
    report.append("  - model_success_rate.png             : 모델별 성공률")
    report.append("  - model_response_time.png            : 모델별 응답시간")
    report.append("  - provider_comparison.png            : 프로바이더 비교")
    report.append("  - agent_distribution.png             : 에이전트별 분포")
    report.append("")

    report.append("=" * 100)
    report.append("보고서 종료")
    report.append("=" * 100)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f'✅ 종합 보고서 생성: {output_file}')


def main():
    parser = argparse.ArgumentParser(description='종합 분석 보고서 생성')
    parser.add_argument('--file', type=str, required=True, help='벤치마크 결과 JSON 파일')
    parser.add_argument('--output', type=str, required=True, help='출력 파일')

    args = parser.parse_args()

    generate_report(args.file, args.output)


if __name__ == '__main__':
    main()
