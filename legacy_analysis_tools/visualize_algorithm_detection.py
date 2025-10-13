#!/usr/bin/env python3
"""
알고리즘별 탐지 성공/실패 시각화 도구
"""

import json
import os
import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import numpy as np
from collections import defaultdict
import argparse

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class AlgorithmDetectionVisualizer:
    def __init__(self, results_file: str = None):
        self.results_file = results_file
        self.results_data = None
        self.ground_truth_cache = {}

    def load_results(self):
        """벤치마크 결과 파일 로드"""
        if not self.results_file:
            result_files = sorted(glob.glob("benchmark_results_*.json"), reverse=True)
            if not result_files:
                print("❌ 벤치마크 결과 파일이 없습니다.")
                return False
            self.results_file = result_files[0]

        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 새 형식 지원: detailed_results를 results로 변환
            if 'detailed_results' in data and 'results' not in data:
                data['results'] = data['detailed_results']

            self.results_data = data
            print(f"✅ 결과 파일 로드: {self.results_file}\n")
            return True
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            return False

    def load_ground_truth(self, file_name: str, agent_type: str):
        """Ground truth 파일 로드"""
        cache_key = f"{agent_type}/{file_name}"
        if cache_key in self.ground_truth_cache:
            return self.ground_truth_cache[cache_key]

        base_name = os.path.splitext(file_name)[0]
        gt_path = f"data/ground_truth/{agent_type}/{base_name}.json"

        if not os.path.exists(gt_path):
            return {}

        try:
            with open(gt_path, 'r', encoding='utf-8') as f:
                gt_data = json.load(f)
                self.ground_truth_cache[cache_key] = gt_data
                return gt_data
        except:
            return {}

    def extract_expected_algorithms(self, ground_truth):
        """Ground truth에서 예상 알고리즘 추출"""
        algorithms = []

        # 새 형식: expected_findings.vulnerable_algorithms_detected
        if 'expected_findings' in ground_truth:
            findings = ground_truth['expected_findings']
            if 'vulnerable_algorithms_detected' in findings:
                algos = findings['vulnerable_algorithms_detected']
                if isinstance(algos, list):
                    algorithms.extend([a.upper() for a in algos if isinstance(a, str)])

            # Korean algorithms도 추가
            if 'korean_algorithms_detected' in findings:
                algos = findings['korean_algorithms_detected']
                if isinstance(algos, list):
                    algorithms.extend([a.upper() for a in algos if isinstance(a, str)])

        # 기존 형식: algorithms 필드
        elif 'algorithms' in ground_truth:
            for algo in ground_truth['algorithms']:
                if isinstance(algo, dict) and 'name' in algo:
                    algorithms.append(algo['name'].upper())

        return algorithms

    def extract_detected_algorithms(self, actual_response):
        """실제 응답에서 탐지된 알고리즘 추출"""
        detected = []
        if not actual_response.get('valid_json', False) and not actual_response.get('json_valid', False):
            return detected

        analysis = actual_response.get('analysis_results', {})

        # algorithms_detected 필드
        if 'algorithms_detected' in analysis:
            algos = analysis['algorithms_detected']
            if isinstance(algos, list):
                detected.extend([a.upper() for a in algos if isinstance(a, str)])

        # vulnerable_algorithms 필드
        if 'vulnerable_algorithms' in analysis:
            algos = analysis['vulnerable_algorithms']
            if isinstance(algos, list):
                for algo in algos:
                    if isinstance(algo, str):
                        detected.append(algo.upper())
                    elif isinstance(algo, dict) and 'name' in algo:
                        detected.append(algo['name'].upper())

        # quantum_vulnerable_algorithms 필드
        if 'quantum_vulnerable_algorithms' in analysis:
            algos = analysis['quantum_vulnerable_algorithms']
            if isinstance(algos, list):
                for algo in algos:
                    if isinstance(algo, str):
                        detected.append(algo.upper())
                    elif isinstance(algo, dict) and 'algorithm' in algo:
                        detected.append(algo['algorithm'].upper())

        # detected_algorithms 필드 (새 형식)
        if 'detected_algorithms' in actual_response:
            algos = actual_response['detected_algorithms']
            if isinstance(algos, list):
                detected.extend([a.upper() for a in algos if isinstance(a, str)])

        # analysis_results 값에서 DETECTED 패턴 찾기
        import re
        for key, value in analysis.items():
            if isinstance(value, str) and 'DETECTED:' in value.upper():
                matches = re.findall(r'DETECTED:\s*([A-Z0-9\-/]+)', value.upper())
                detected.extend(matches)

        return list(set(detected))

    def normalize_algorithm_name(self, name: str) -> str:
        """알고리즘 이름 정규화"""
        name = name.upper().strip()
        mappings = {
            'TRIPLE DES': '3DES', 'TRIPLE-DES': '3DES', 'TDES': '3DES',
            'EC-KCDSA': 'KCDSA', 'ECKCDSA': 'KCDSA',
            'DIFFIE-HELLMAN': 'DH', 'DIFFIE HELLMAN': 'DH',
            'SHA1': 'SHA-1', 'SHA256': 'SHA-256', 'SHA512': 'SHA-512',
        }
        for pattern, replacement in mappings.items():
            if pattern in name:
                return replacement
        return name

    def check_algorithm_match(self, expected: str, detected_list: list) -> bool:
        """알고리즘 매칭 확인"""
        expected_norm = self.normalize_algorithm_name(expected)
        detected_norm = [self.normalize_algorithm_name(d) for d in detected_list]

        if expected_norm in detected_norm:
            return True

        for detected in detected_norm:
            if expected_norm in detected or detected in expected_norm:
                return True
        return False

    def collect_algorithm_stats(self):
        """모든 알고리즘 통계 수집"""
        overall_stats = defaultdict(lambda: {'expected': 0, 'detected': 0, 'missed': 0})
        model_stats = defaultdict(lambda: defaultdict(lambda: {'expected': 0, 'detected': 0, 'missed': 0}))

        for result in self.results_data.get('results', []):
            # 필드명 매핑: model 또는 model_name
            model_name = result.get('model', result.get('model_name', 'unknown'))
            # 파일 경로에서 파일명 추출
            file_path = result.get('file_path', result.get('file_name', ''))
            file_name = os.path.basename(file_path) if file_path else ''
            agent_type = result.get('agent_type', '')

            gt = self.load_ground_truth(file_name, agent_type)
            if not gt:
                continue

            expected_algos = self.extract_expected_algorithms(gt)
            if not expected_algos:
                continue

            detected_algos = self.extract_detected_algorithms(result)

            for expected in expected_algos:
                expected_norm = self.normalize_algorithm_name(expected)

                overall_stats[expected_norm]['expected'] += 1
                model_stats[model_name][expected_norm]['expected'] += 1

                if self.check_algorithm_match(expected, detected_algos):
                    overall_stats[expected_norm]['detected'] += 1
                    model_stats[model_name][expected_norm]['detected'] += 1
                else:
                    overall_stats[expected_norm]['missed'] += 1
                    model_stats[model_name][expected_norm]['missed'] += 1

        return overall_stats, model_stats

    def plot_overall_detection_rate(self, overall_stats, output_file='algorithm_detection_overall.png'):
        """전체 알고리즘 탐지율 막대 그래프"""
        algorithms = sorted(overall_stats.keys(),
                          key=lambda x: overall_stats[x]['detected'] / max(overall_stats[x]['expected'], 1),
                          reverse=True)

        detection_rates = []
        expected_counts = []

        for algo in algorithms:
            stats = overall_stats[algo]
            rate = stats['detected'] / max(stats['expected'], 1) * 100
            detection_rates.append(rate)
            expected_counts.append(stats['expected'])

        fig, ax = plt.subplots(figsize=(14, 8))

        colors = ['#2ecc71' if r >= 80 else '#f39c12' if r >= 50 else '#e74c3c' for r in detection_rates]
        bars = ax.barh(algorithms, detection_rates, color=colors, alpha=0.8)

        # 값 표시
        for i, (bar, rate, count) in enumerate(zip(bars, detection_rates, expected_counts)):
            ax.text(rate + 2, i, f'{rate:.1f}% ({count} tests)',
                   va='center', fontsize=10)

        ax.set_xlabel('Detection Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Algorithm Detection Rate (All Models Combined)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # 범례
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='Excellent (≥80%)'),
            Patch(facecolor='#f39c12', label='Moderate (50-80%)'),
            Patch(facecolor='#e74c3c', label='Poor (<50%)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 저장: {output_file}")
        plt.close()

    def plot_model_comparison_heatmap(self, model_stats, output_file='algorithm_detection_by_model.png'):
        """모델별 알고리즘 탐지율 히트맵"""
        # 모든 알고리즘 수집
        all_algorithms = set()
        for model_data in model_stats.values():
            all_algorithms.update(model_data.keys())

        algorithms = sorted(all_algorithms)
        models = sorted(model_stats.keys())

        # 데이터 매트릭스 생성
        data = np.zeros((len(algorithms), len(models)))

        for i, algo in enumerate(algorithms):
            for j, model in enumerate(models):
                stats = model_stats[model].get(algo, {'expected': 0, 'detected': 0})
                if stats['expected'] > 0:
                    data[i, j] = stats['detected'] / stats['expected'] * 100
                else:
                    data[i, j] = np.nan

        fig, ax = plt.subplots(figsize=(12, max(8, len(algorithms) * 0.4)))

        sns.heatmap(data, annot=True, fmt='.1f', cmap='RdYlGn',
                   xticklabels=models, yticklabels=algorithms,
                   vmin=0, vmax=100, cbar_kws={'label': 'Detection Rate (%)'},
                   linewidths=0.5, ax=ax)

        ax.set_title('Algorithm Detection Rate by Model (%)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_ylabel('Algorithm', fontsize=12, fontweight='bold')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 저장: {output_file}")
        plt.close()

    def plot_success_failure_stacked(self, overall_stats, output_file='algorithm_success_failure.png'):
        """알고리즘별 성공/실패 스택 바 차트"""
        algorithms = sorted(overall_stats.keys(),
                          key=lambda x: overall_stats[x]['detected'] / max(overall_stats[x]['expected'], 1),
                          reverse=True)

        detected = [overall_stats[a]['detected'] for a in algorithms]
        missed = [overall_stats[a]['missed'] for a in algorithms]

        fig, ax = plt.subplots(figsize=(14, 8))

        x = np.arange(len(algorithms))
        width = 0.7

        p1 = ax.bar(x, detected, width, label='Detected', color='#2ecc71', alpha=0.8)
        p2 = ax.bar(x, missed, width, bottom=detected, label='Missed', color='#e74c3c', alpha=0.8)

        ax.set_ylabel('Number of Tests', fontsize=12, fontweight='bold')
        ax.set_title('Algorithm Detection Success vs Failure',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # 퍼센트 표시
        for i, (d, m) in enumerate(zip(detected, missed)):
            total = d + m
            if total > 0:
                percentage = d / total * 100
                ax.text(i, total + 1, f'{percentage:.0f}%',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 저장: {output_file}")
        plt.close()

    def plot_top_bottom_algorithms(self, overall_stats, output_file='algorithm_top_bottom.png'):
        """상위/하위 알고리즘 비교"""
        algo_rates = []
        for algo, stats in overall_stats.items():
            if stats['expected'] >= 5:  # 최소 5개 테스트 이상
                rate = stats['detected'] / stats['expected'] * 100
                algo_rates.append((algo, rate, stats['expected']))

        algo_rates.sort(key=lambda x: x[1], reverse=True)

        top_5 = algo_rates[:5]
        bottom_5 = algo_rates[-5:]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Top 5
        algos_top = [a[0] for a in top_5]
        rates_top = [a[1] for a in top_5]
        counts_top = [a[2] for a in top_5]

        bars1 = ax1.barh(algos_top, rates_top, color='#2ecc71', alpha=0.8)
        for i, (bar, rate, count) in enumerate(zip(bars1, rates_top, counts_top)):
            ax1.text(rate + 2, i, f'{rate:.1f}% ({count})', va='center')

        ax1.set_xlabel('Detection Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Top 5 Best Detected Algorithms', fontsize=13, fontweight='bold')
        ax1.set_xlim(0, 110)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')

        # Bottom 5
        algos_bottom = [a[0] for a in bottom_5]
        rates_bottom = [a[1] for a in bottom_5]
        counts_bottom = [a[2] for a in bottom_5]

        bars2 = ax2.barh(algos_bottom, rates_bottom, color='#e74c3c', alpha=0.8)
        for i, (bar, rate, count) in enumerate(zip(bars2, rates_bottom, counts_bottom)):
            ax2.text(rate + 2, i, f'{rate:.1f}% ({count})', va='center')

        ax2.set_xlabel('Detection Rate (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Bottom 5 Worst Detected Algorithms', fontsize=13, fontweight='bold')
        ax2.set_xlim(0, 110)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 저장: {output_file}")
        plt.close()

    def generate_all_plots(self, output_dir='.'):
        """모든 그래프 생성"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        overall_stats, model_stats = self.collect_algorithm_stats()

        if not overall_stats:
            print("⚠️  알고리즘 통계 데이터가 없습니다.")
            return

        print("\n📊 알고리즘 탐지 그래프 생성 중...\n")

        self.plot_overall_detection_rate(
            overall_stats,
            os.path.join(output_dir, 'algorithm_detection_overall.png')
        )

        self.plot_model_comparison_heatmap(
            model_stats,
            os.path.join(output_dir, 'algorithm_detection_by_model.png')
        )

        self.plot_success_failure_stacked(
            overall_stats,
            os.path.join(output_dir, 'algorithm_success_failure.png')
        )

        self.plot_top_bottom_algorithms(
            overall_stats,
            os.path.join(output_dir, 'algorithm_top_bottom.png')
        )

        print("\n✅ 모든 알고리즘 탐지 그래프 생성 완료!")


def main():
    parser = argparse.ArgumentParser(description='알고리즘 탐지율 시각화')
    parser.add_argument('--file', '-f', help='벤치마크 결과 JSON 파일')
    parser.add_argument('--output-dir', '-o', default='.', help='출력 디렉토리')

    args = parser.parse_args()

    visualizer = AlgorithmDetectionVisualizer(args.file)

    if not visualizer.load_results():
        return

    visualizer.generate_all_plots(args.output_dir)


if __name__ == "__main__":
    main()
