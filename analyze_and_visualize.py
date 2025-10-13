#!/usr/bin/env python3
"""
통합 분석 및 시각화 도구
벤치마크 결과를 분석하고 다양한 관점에서 시각화합니다.

사용법:
    python analyze_and_visualize.py <results_file> [options]

옵션:
    --all                모든 분석 및 시각화 수행 (기본값)
    --text-only          텍스트 분석만 수행
    --visualize-only     시각화만 수행
    --output-dir DIR     출력 디렉토리 (기본값: result_analysis)
    --min-tests N        최소 테스트 수 (기본값: 10)
"""

import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ComprehensiveAnalyzer:
    """통합 분석 및 시각화 클래스"""

    ALGORITHM_VARIATIONS = {
        'rsa': ['rsa'],
        'ecc': ['ecc', 'ecdsa', 'ecdh', 'elliptic curve', 'p-256', 'secp256'],
        'aes': ['aes', 'rijndael', 'aes-128', 'aes-256'],
        'md5': ['md5', 'message digest 5'],
        'seed': ['seed'],
        'aria': ['aria'],
        'hight': ['hight'],
        'lea': ['lea'],
        'sha1': ['sha1', 'sha-1'],
        'sha256': ['sha256', 'sha-256'],
        '3des': ['3des', 'triple des', 'triple-des', 'tdes'],
        'des': ['des'],
        'rc4': ['rc4', 'arcfour'],
        'dsa': ['dsa'],
        'dh': ['diffie-hellman', 'dh', 'diffie hellman'],
        'elgamal': ['elgamal'],
        'kcdsa': ['kcdsa', 'ec-kcdsa', 'eckcdsa'],
        'has-160': ['has-160', 'has160'],
        'lsh': ['lsh'],
    }

    def __init__(self, results_file: str, output_dir: str = "result_analysis", min_tests: int = 10):
        self.results_file = results_file
        self.output_dir = output_dir
        self.min_tests = min_tests
        self.results = None
        self.df = None
        self.ground_truth_cache = {}

        # 출력 디렉토리 생성
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def load_results(self):
        """결과 파일 로드"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)

            # 형식 통일
            if 'detailed_results' in self.results and 'results' not in self.results:
                self.results['results'] = self.results['detailed_results']

            print(f"✅ 결과 파일 로드: {self.results_file}")
            print(f"   총 테스트: {self.results.get('metadata', {}).get('total_tests', 0)}개")
            return True
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            return False

    def create_dataframe(self):
        """결과를 DataFrame으로 변환"""
        detailed_results = self.results.get('detailed_results', self.results.get('results', []))
        successful_results = [r for r in detailed_results if r.get('success', False)]

        if not successful_results:
            print("⚠️  성공한 테스트 결과가 없습니다.")
            return False

        self.df = pd.DataFrame(successful_results)
        self.df['provider_model'] = self.df['provider'] + '/' + self.df['model']

        # Precision, Recall, F1 계산
        self._calculate_metrics()

        print(f"✅ DataFrame 생성 완료: {len(self.df)}개 성공 테스트")
        return True

    def _load_ground_truth(self, file_path: str):
        """Ground truth 로드"""
        if file_path in self.ground_truth_cache:
            return self.ground_truth_cache[file_path]

        path = Path(file_path)
        if 'test_files' in path.parts:
            parts = list(path.parts)
            test_files_idx = parts.index('test_files')
            parts[test_files_idx] = 'ground_truth'
            gt_path = Path(*parts).with_suffix('.json')

            try:
                with open(gt_path, 'r', encoding='utf-8') as f:
                    gt_data = json.load(f)
                    self.ground_truth_cache[file_path] = gt_data
                    return gt_data
            except:
                return None
        return None

    def _normalize_algorithm_name(self, name: str) -> str:
        """알고리즘 이름 정규화"""
        name_lower = name.lower().strip()

        for standard_name, variations in self.ALGORITHM_VARIATIONS.items():
            if any(var in name_lower for var in variations):
                return standard_name.upper()

        return name.upper()

    def _calculate_precision_recall(self, detected: list, expected: list) -> tuple:
        """Precision, Recall, F1 계산"""
        if not expected:
            return 1.0, 1.0, 1.0

        if not detected:
            return 0.0, 0.0, 0.0

        # 정규화
        detected_set = set(self._normalize_algorithm_name(alg) for alg in detected)
        expected_set = set(self._normalize_algorithm_name(alg) for alg in expected)

        # True Positives
        true_positives = len(detected_set & expected_set)

        # Precision, Recall, F1
        precision = true_positives / len(detected_set) if detected_set else 0.0
        recall = true_positives / len(expected_set) if expected_set else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return precision, recall, f1

    def _calculate_metrics(self):
        """모든 테스트에 대해 Precision, Recall, F1 계산"""
        precisions = []
        recalls = []
        f1_scores = []

        for idx, row in self.df.iterrows():
            file_path = row.get('file_path', '')
            detected_algos = row.get('detected_algorithms', [])

            gt = self._load_ground_truth(file_path)

            if gt and 'expected_findings' in gt:
                expected_algos = gt['expected_findings'].get('vulnerable_algorithms_detected', [])
                expected_algos += gt['expected_findings'].get('korean_algorithms_detected', [])
                precision, recall, f1 = self._calculate_precision_recall(detected_algos, expected_algos)
            else:
                # Ground truth가 없으면 confidence_score 사용
                precision = recall = f1 = row.get('confidence_score', 0.0)

            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)

        self.df['precision'] = precisions
        self.df['recall'] = recalls
        self.df['f1_score'] = f1_scores

        print(f"✅ 메트릭 계산 완료 (평균 F1: {np.mean(f1_scores):.3f})")

    # ==================== 텍스트 분석 ====================

    def generate_text_report(self):
        """종합 텍스트 리포트 생성"""
        output_file = f"{self.output_dir}/COMPREHENSIVE_REPORT.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            self._write_header(f)
            self._write_summary(f)
            self._write_model_comparison(f)
            self._write_agent_analysis(f)
            self._write_algorithm_analysis(f)
            self._write_performance_analysis(f)

        print(f"✅ 텍스트 리포트 생성: {output_file}")

    def _write_header(self, f):
        """헤더 작성"""
        f.write("=" * 100 + "\n")
        f.write("📊 AI 벤치마크 종합 분석 보고서\n")
        f.write("   양자 취약 암호 알고리즘 탐지 성능 평가\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"결과 파일: {self.results_file}\n")
        f.write(f"출력 디렉토리: {self.output_dir}\n\n")

    def _write_summary(self, f):
        """요약 정보 작성"""
        f.write("## 1️⃣ 실행 요약\n")
        f.write("-" * 100 + "\n")

        summary = self.results.get('summary', {})
        f.write(f"총 테스트: {summary.get('total_tests', 0)}개\n")
        f.write(f"성공 테스트: {summary.get('successful_tests', 0)}개\n")
        f.write(f"성공률: {summary.get('success_rate', 0) * 100:.1f}%\n")
        f.write(f"평균 신뢰도: {summary.get('avg_confidence', 0):.3f}\n")
        f.write(f"평균 응답시간: {summary.get('avg_response_time', 0):.2f}초\n\n")

    def _write_model_comparison(self, f):
        """모델별 성능 비교 작성"""
        f.write("## 2️⃣ 모델별 성능 비교 (F1 Score 기준)\n")
        f.write("=" * 100 + "\n\n")

        model_stats = self.df.groupby('provider_model').agg({
            'f1_score': ['mean', 'std', 'min', 'max', 'count'],
            'precision': ['mean', 'std'],
            'recall': ['mean', 'std'],
            'response_time': ['mean', 'std'],
            'confidence_score': 'mean'
        }).round(3)

        model_stats.columns = ['_'.join(col).strip('_') for col in model_stats.columns]
        model_stats = model_stats.sort_values('f1_score_mean', ascending=False)

        # 신뢰할 수 있는 결과 (min_tests 이상)
        reliable = model_stats[model_stats['f1_score_count'] >= self.min_tests]

        if not reliable.empty:
            f.write(f"🏆 신뢰할 수 있는 결과 (테스트 수 >= {self.min_tests}):\n")
            f.write("-" * 100 + "\n")

            for i, (model, stats) in enumerate(reliable.iterrows(), 1):
                medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '  '
                f.write(f"{medal} {i}. {model}\n")
                f.write(f"   F1 Score: {stats['f1_score_mean']:.3f} (±{stats['f1_score_std']:.3f})\n")
                f.write(f"   Precision: {stats['precision_mean']:.3f} (±{stats['precision_std']:.3f})\n")
                f.write(f"   Recall: {stats['recall_mean']:.3f} (±{stats['recall_std']:.3f})\n")
                f.write(f"   응답시간: {stats['response_time_mean']:.2f}초 (±{stats['response_time_std']:.2f})\n")
                f.write(f"   테스트 수: {int(stats['f1_score_count'])}개\n\n")

        # 전체 결과
        f.write(f"\n전체 모델 순위 (모든 테스트):\n")
        f.write("-" * 100 + "\n")
        for i, (model, stats) in enumerate(model_stats.iterrows(), 1):
            warning = " ⚠️ " if stats['f1_score_count'] < self.min_tests else ""
            f.write(f"  {i}. {model}: F1 {stats['f1_score_mean']:.3f} ({int(stats['f1_score_count'])}개){warning}\n")
        f.write("\n")

    def _write_agent_analysis(self, f):
        """에이전트별 분석 작성"""
        f.write("## 3️⃣ 에이전트별 성능 분석\n")
        f.write("=" * 100 + "\n\n")

        agent_stats = self.df.groupby('agent_type').agg({
            'f1_score': ['mean', 'std', 'count'],
            'precision': 'mean',
            'recall': 'mean',
            'response_time': 'mean',
            'confidence_score': 'mean'
        }).round(3)

        agent_stats.columns = ['_'.join(col).strip('_') for col in agent_stats.columns]

        for agent, stats in agent_stats.iterrows():
            f.write(f"🎯 {agent}\n")
            f.write("-" * 100 + "\n")
            f.write(f"  테스트 수: {int(stats['f1_score_count'])}개\n")
            f.write(f"  F1 Score: {stats['f1_score_mean']:.3f} (±{stats['f1_score_std']:.3f})\n")
            f.write(f"  Precision: {stats['precision_mean']:.3f}\n")
            f.write(f"  Recall: {stats['recall_mean']:.3f}\n")
            f.write(f"  평균 응답시간: {stats['response_time_mean']:.2f}초\n\n")

    def _write_algorithm_analysis(self, f):
        """알고리즘별 탐지 분석 작성"""
        f.write("## 4️⃣ 알고리즘 탐지 분석\n")
        f.write("=" * 100 + "\n\n")

        algorithm_stats = self._collect_algorithm_stats()

        if algorithm_stats:
            f.write("전체 알고리즘 탐지율:\n")
            f.write("-" * 100 + "\n")

            for algo, stats in sorted(algorithm_stats.items(),
                                     key=lambda x: x[1]['detected'] / max(x[1]['expected'], 1),
                                     reverse=True):
                rate = stats['detected'] / max(stats['expected'], 1) * 100
                status = "✅" if rate >= 80 else "⚠️ " if rate >= 50 else "❌"
                f.write(f"  {status} {algo:15s}: {rate:5.1f}% ({stats['detected']}/{stats['expected']})\n")
            f.write("\n")

    def _write_performance_analysis(self, f):
        """성능 분석 작성"""
        f.write("## 5️⃣ 성능 분석\n")
        f.write("=" * 100 + "\n\n")

        # 응답시간
        f.write("⚡ 응답시간 순위:\n")
        f.write("-" * 100 + "\n")
        response_stats = self.df.groupby('provider_model')['response_time'].mean().sort_values()
        for i, (model, time) in enumerate(response_stats.items(), 1):
            f.write(f"  {i}. {model}: {time:.2f}초\n")
        f.write("\n")

        # 상관관계
        if len(self.df) >= 10:
            f.write("🔗 주요 상관관계:\n")
            f.write("-" * 100 + "\n")
            corr = self.df[['f1_score', 'response_time', 'confidence_score']].corr()
            f.write(f"  F1 Score vs 응답시간: {corr.loc['f1_score', 'response_time']:.3f}\n")
            f.write(f"  F1 Score vs 신뢰도: {corr.loc['f1_score', 'confidence_score']:.3f}\n\n")

    def _collect_algorithm_stats(self):
        """알고리즘 통계 수집"""
        stats = defaultdict(lambda: {'expected': 0, 'detected': 0})

        for idx, row in self.df.iterrows():
            file_path = row.get('file_path', '')
            detected_algos = row.get('detected_algorithms', [])

            gt = self._load_ground_truth(file_path)
            if not gt or 'expected_findings' not in gt:
                continue

            expected_algos = gt['expected_findings'].get('vulnerable_algorithms_detected', [])
            expected_algos += gt['expected_findings'].get('korean_algorithms_detected', [])

            for algo in expected_algos:
                norm_algo = self._normalize_algorithm_name(algo)
                stats[norm_algo]['expected'] += 1

                # 탐지 여부 확인
                detected_norm = [self._normalize_algorithm_name(d) for d in detected_algos]
                if norm_algo in detected_norm:
                    stats[norm_algo]['detected'] += 1

        return dict(stats)

    # ==================== 시각화 ====================

    def generate_visualizations(self):
        """모든 시각화 생성"""
        print("\n📊 시각화 생성 중...")

        self._plot_model_f1_comparison()
        self._plot_precision_recall_f1()
        self._plot_agent_performance()
        self._plot_response_time()
        self._plot_algorithm_detection()
        self._plot_model_heatmap()

        print("✅ 모든 시각화 생성 완료")

    def _plot_model_f1_comparison(self):
        """모델별 F1 Score 비교"""
        model_stats = self.df.groupby('provider_model').agg({
            'f1_score': ['mean', 'count']
        })
        model_stats.columns = ['mean', 'count']
        model_stats = model_stats[model_stats['count'] >= self.min_tests].sort_values('mean', ascending=True)

        if model_stats.empty:
            return

        fig, ax = plt.subplots(figsize=(12, max(6, len(model_stats) * 0.4)))

        colors = ['#2ecc71' if x >= 0.8 else '#f39c12' if x >= 0.5 else '#e74c3c'
                 for x in model_stats['mean']]
        bars = ax.barh(range(len(model_stats)), model_stats['mean'], color=colors, alpha=0.8)

        # 값 표시
        for i, (bar, f1, count) in enumerate(zip(bars, model_stats['mean'], model_stats['count'])):
            ax.text(f1 + 0.01, i, f'{f1:.3f} (n={int(count)})',
                   va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(range(len(model_stats)))
        ax.set_yticklabels(model_stats.index, fontsize=10)
        ax.set_xlabel('F1 Score', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison (F1 Score)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, min(1.0, max(model_stats['mean']) * 1.15))
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/model_f1_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ model_f1_comparison.png")

    def _plot_precision_recall_f1(self):
        """Precision, Recall, F1 함께 비교"""
        model_stats = self.df.groupby('provider_model').agg({
            'precision': 'mean',
            'recall': 'mean',
            'f1_score': ['mean', 'count']
        })
        model_stats.columns = ['precision', 'recall', 'f1', 'count']
        model_stats = model_stats[model_stats['count'] >= self.min_tests].sort_values('f1', ascending=False)

        if model_stats.empty:
            return

        x = np.arange(len(model_stats))
        width = 0.25

        fig, ax = plt.subplots(figsize=(14, 7))

        ax.bar(x - width, model_stats['precision'], width, label='Precision',
               color='#3498db', edgecolor='black', alpha=0.8)
        ax.bar(x, model_stats['recall'], width, label='Recall',
               color='#e74c3c', edgecolor='black', alpha=0.8)
        ax.bar(x + width, model_stats['f1'], width, label='F1 Score',
               color='#2ecc71', edgecolor='black', alpha=0.8)

        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Precision, Recall, and F1 Score Comparison',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(model_stats.index, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, 1.1)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/precision_recall_f1.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ precision_recall_f1.png")

    def _plot_agent_performance(self):
        """에이전트별 성능"""
        agent_stats = self.df.groupby('agent_type').agg({
            'f1_score': 'mean',
            'confidence_score': 'count'
        })
        agent_stats.columns = ['f1', 'count']
        agent_stats = agent_stats.sort_values('f1', ascending=True)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(agent_stats)))
        bars = ax.barh(range(len(agent_stats)), agent_stats['f1'], color=colors, alpha=0.8)

        for i, (bar, f1, count) in enumerate(zip(bars, agent_stats['f1'], agent_stats['count'])):
            ax.text(f1 + 0.01, i, f'{f1:.3f} (n={int(count)})',
                   va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(range(len(agent_stats)))
        ax.set_yticklabels(agent_stats.index, fontsize=11)
        ax.set_xlabel('F1 Score', fontsize=12, fontweight='bold')
        ax.set_title('Agent Performance Comparison', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, min(1.0, max(agent_stats['f1']) * 1.15))
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/agent_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ agent_performance.png")

    def _plot_response_time(self):
        """응답시간 비교"""
        response_stats = self.df.groupby('provider_model').agg({
            'response_time': ['mean', 'std', 'count']
        })
        response_stats.columns = ['mean', 'std', 'count']
        response_stats = response_stats[response_stats['count'] >= self.min_tests].sort_values('mean')

        if response_stats.empty:
            return

        fig, ax = plt.subplots(figsize=(12, max(6, len(response_stats) * 0.4)))

        max_time = response_stats['mean'].max()
        colors = plt.cm.RdYlGn_r(response_stats['mean'] / max_time)

        bars = ax.barh(range(len(response_stats)), response_stats['mean'],
                      xerr=response_stats['std'], capsize=5,
                      color=colors, edgecolor='black', alpha=0.8)

        for i, (bar, time, count) in enumerate(zip(bars, response_stats['mean'], response_stats['count'])):
            ax.text(time + response_stats['std'].iloc[i] + 0.5, i,
                   f'{time:.2f}s (n={int(count)})',
                   va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(range(len(response_stats)))
        ax.set_yticklabels(response_stats.index, fontsize=10)
        ax.set_xlabel('Response Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Model Response Time Comparison', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/model_response_time.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ model_response_time.png")

    def _plot_algorithm_detection(self):
        """알고리즘 탐지율"""
        algorithm_stats = self._collect_algorithm_stats()

        if not algorithm_stats:
            return

        # 탐지율 계산 및 정렬
        algo_data = []
        for algo, stats in algorithm_stats.items():
            if stats['expected'] > 0:
                rate = stats['detected'] / stats['expected'] * 100
                algo_data.append((algo, rate, stats['expected']))

        algo_data.sort(key=lambda x: x[1], reverse=True)
        algorithms, rates, counts = zip(*algo_data)

        fig, ax = plt.subplots(figsize=(14, max(8, len(algorithms) * 0.4)))

        colors = ['#2ecc71' if r >= 80 else '#f39c12' if r >= 50 else '#e74c3c' for r in rates]
        bars = ax.barh(range(len(algorithms)), rates, color=colors, alpha=0.8)

        for i, (bar, rate, count) in enumerate(zip(bars, rates, counts)):
            ax.text(rate + 2, i, f'{rate:.1f}% (n={count})',
                   va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(range(len(algorithms)))
        ax.set_yticklabels(algorithms, fontsize=10)
        ax.set_xlabel('Detection Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Algorithm Detection Rate (All Models)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/algorithm_detection_overall.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ algorithm_detection_overall.png")

    def _plot_model_heatmap(self):
        """모델-에이전트 히트맵"""
        pivot_data = self.df.groupby(['agent_type', 'provider_model']).agg({
            'f1_score': 'mean',
            'confidence_score': 'count'
        }).reset_index()

        pivot_data = pivot_data[pivot_data['confidence_score'] >= self.min_tests]

        if pivot_data.empty:
            return

        heatmap_data = pivot_data.pivot(
            index='agent_type',
            columns='provider_model',
            values='f1_score'
        )

        fig, ax = plt.subplots(figsize=(14, 8))

        sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='YlGnBu',
                   cbar_kws={'label': 'F1 Score'}, linewidths=0.5,
                   linecolor='gray', ax=ax)

        ax.set_title('Model-Agent Performance Heatmap (F1 Score)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_ylabel('Agent Type', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/model_agent_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ model_agent_heatmap.png")

    # ==================== 메인 실행 ====================

    def run_all(self):
        """전체 분석 및 시각화 실행"""
        print("\n" + "=" * 80)
        print("🚀 통합 분석 및 시각화 시작")
        print("=" * 80)

        if not self.load_results():
            return False

        if not self.create_dataframe():
            return False

        print("\n📝 텍스트 리포트 생성 중...")
        self.generate_text_report()

        print("\n📊 시각화 생성 중...")
        self.generate_visualizations()

        print("\n" + "=" * 80)
        print(f"✅ 분석 완료! 결과는 '{self.output_dir}' 디렉토리에 저장되었습니다.")
        print("=" * 80)
        print("\n생성된 파일:")
        print("  📄 COMPREHENSIVE_REPORT.txt - 종합 텍스트 보고서")
        print("  📊 model_f1_comparison.png - 모델별 F1 Score 비교")
        print("  📊 precision_recall_f1.png - Precision/Recall/F1 비교")
        print("  📊 agent_performance.png - 에이전트별 성능")
        print("  📊 model_response_time.png - 모델별 응답시간")
        print("  📊 algorithm_detection_overall.png - 알고리즘 탐지율")
        print("  📊 model_agent_heatmap.png - 모델-에이전트 히트맵")
        print()

        return True


def main():
    parser = argparse.ArgumentParser(
        description='통합 분석 및 시각화 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 전체 분석 및 시각화
  python analyze_and_visualize.py benchmark_results.json

  # 출력 디렉토리 지정
  python analyze_and_visualize.py benchmark_results.json --output-dir my_results

  # 최소 테스트 수 설정
  python analyze_and_visualize.py benchmark_results.json --min-tests 20

  # 텍스트 분석만
  python analyze_and_visualize.py benchmark_results.json --text-only

  # 시각화만
  python analyze_and_visualize.py benchmark_results.json --visualize-only
        """
    )

    parser.add_argument('results_file', help='벤치마크 결과 JSON 파일')
    parser.add_argument('--output-dir', default='result_analysis',
                       help='출력 디렉토리 (기본값: result_analysis)')
    parser.add_argument('--min-tests', type=int, default=10,
                       help='신뢰할 수 있는 결과로 간주하는 최소 테스트 수 (기본값: 10)')
    parser.add_argument('--text-only', action='store_true',
                       help='텍스트 분석만 수행')
    parser.add_argument('--visualize-only', action='store_true',
                       help='시각화만 수행')
    parser.add_argument('--all', action='store_true', default=True,
                       help='모든 분석 및 시각화 수행 (기본값)')

    args = parser.parse_args()

    # 파일 존재 확인
    if not Path(args.results_file).exists():
        print(f"❌ 결과 파일을 찾을 수 없습니다: {args.results_file}")
        sys.exit(1)

    # 분석기 생성
    analyzer = ComprehensiveAnalyzer(
        results_file=args.results_file,
        output_dir=args.output_dir,
        min_tests=args.min_tests
    )

    # 결과 로드 및 DataFrame 생성
    if not analyzer.load_results() or not analyzer.create_dataframe():
        sys.exit(1)

    # 분석 실행
    if args.text_only:
        print("\n📝 텍스트 리포트 생성 중...")
        analyzer.generate_text_report()
    elif args.visualize_only:
        analyzer.generate_visualizations()
    else:
        analyzer.run_all()


if __name__ == "__main__":
    main()
