#!/usr/bin/env python3
"""
에이전트별 모델 성능 시각화 도구
각 에이전트에서 어떤 모델이 가장 뛰어난지 비교 분석
"""

import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

class AgentPerformanceVisualizer:
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.df = self._create_dataframe()

    def _load_results(self):
        """결과 파일 로드"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_dataframe(self):
        """결과를 DataFrame으로 변환"""
        detailed_results = self.results.get('detailed_results', [])
        successful_results = [r for r in detailed_results if r.get('success', False)]

        if not successful_results:
            print("❌ 분석할 성공한 테스트 결과가 없습니다.")
            return pd.DataFrame()

        df = pd.DataFrame(successful_results)
        df['provider_model'] = df['provider'] + '/' + df['model']

        # F1, Precision, Recall이 이미 있다고 가정
        # 없으면 confidence_score 사용
        if 'f1_score' not in df.columns:
            df['f1_score'] = df['confidence_score']
        if 'precision' not in df.columns:
            df['precision'] = df['confidence_score']
        if 'recall' not in df.columns:
            df['recall'] = df['confidence_score']

        return df

    def create_agent_model_heatmap(self, metric='f1_score', min_tests=10):
        """에이전트-모델별 성능 히트맵 생성"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 집계
        pivot_data = self.df.groupby(['agent_type', 'provider_model']).agg({
            metric: 'mean',
            'confidence_score': 'count'
        }).reset_index()

        # 최소 테스트 수 필터링
        pivot_data = pivot_data[pivot_data['confidence_score'] >= min_tests]

        if pivot_data.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        # 피벗 테이블 생성
        heatmap_data = pivot_data.pivot(
            index='agent_type',
            columns='provider_model',
            values=metric
        )

        # 그래프 생성
        plt.figure(figsize=(14, 8))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.3f',
            cmap='YlOrRd',
            cbar_kws={'label': metric.replace('_', ' ').title()},
            linewidths=0.5,
            linecolor='gray'
        )

        plt.title(f'Agent-Model Performance Heatmap ({metric.replace("_", " ").title()})',
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Model', fontsize=12, fontweight='bold')
        plt.ylabel('Agent Type', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        filename = f'agent_model_heatmap_{metric}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 히트맵이 {filename}에 저장되었습니다.")
        plt.close()

    def create_agent_comparison_bar(self, min_tests=10):
        """에이전트별 최고 성능 모델 비교 막대 그래프"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 집계
        agent_model_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'f1_score': 'mean',
            'precision': 'mean',
            'recall': 'mean',
            'confidence_score': 'count'
        }).reset_index()

        # 최소 테스트 수 필터링
        agent_model_stats = agent_model_stats[agent_model_stats['confidence_score'] >= min_tests]

        if agent_model_stats.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        # 각 에이전트별 최고 성능 모델 찾기
        best_models = agent_model_stats.loc[
            agent_model_stats.groupby('agent_type')['f1_score'].idxmax()
        ]

        # 그래프 생성
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        metrics = ['f1_score', 'precision', 'recall']
        titles = ['F1 Score', 'Precision', 'Recall']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

        for idx, (metric, title, color) in enumerate(zip(metrics, titles, colors)):
            ax = axes[idx]

            # 막대 그래프
            bars = ax.barh(
                range(len(best_models)),
                best_models[metric],
                color=color,
                alpha=0.7,
                edgecolor='black',
                linewidth=1.5
            )

            # 레이블 설정
            ax.set_yticks(range(len(best_models)))
            ax.set_yticklabels(best_models['agent_type'])
            ax.set_xlabel(title, fontsize=11, fontweight='bold')
            ax.set_title(f'Best Model per Agent ({title})', fontsize=12, fontweight='bold')
            ax.set_xlim(0, 1.0)
            ax.grid(axis='x', alpha=0.3, linestyle='--')

            # 값과 모델명 표시
            for i, (bar, model, value) in enumerate(zip(bars, best_models['provider_model'], best_models[metric])):
                # 값 표시
                ax.text(
                    value + 0.02,
                    i,
                    f'{value:.3f}',
                    va='center',
                    fontsize=9,
                    fontweight='bold'
                )
                # 모델명 표시 (막대 안쪽)
                ax.text(
                    value / 2,
                    i,
                    model.split('/')[-1],  # 모델명만 표시
                    va='center',
                    ha='center',
                    fontsize=8,
                    color='white',
                    fontweight='bold'
                )

        plt.suptitle('Best Performing Model for Each Agent Type',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        filename = 'agent_best_models.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 막대 그래프가 {filename}에 저장되었습니다.")
        plt.close()

    def create_agent_model_ranking(self, min_tests=10):
        """에이전트별 모델 순위 차트"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 집계
        agent_model_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'f1_score': 'mean',
            'confidence_score': 'count'
        }).reset_index()

        # 최소 테스트 수 필터링
        agent_model_stats = agent_model_stats[agent_model_stats['confidence_score'] >= min_tests]

        agents = agent_model_stats['agent_type'].unique()
        n_agents = len(agents)

        # 그래프 생성 (각 에이전트별 서브플롯)
        fig, axes = plt.subplots(1, n_agents, figsize=(6*n_agents, 6))
        if n_agents == 1:
            axes = [axes]

        for idx, agent in enumerate(agents):
            ax = axes[idx]

            # 해당 에이전트 데이터 필터링
            agent_data = agent_model_stats[agent_model_stats['agent_type'] == agent].copy()
            agent_data = agent_data.sort_values('f1_score', ascending=True)

            # 막대 그래프
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(agent_data)))
            bars = ax.barh(
                range(len(agent_data)),
                agent_data['f1_score'],
                color=colors,
                edgecolor='black',
                linewidth=1.5
            )

            # 레이블
            ax.set_yticks(range(len(agent_data)))
            model_labels = [m.split('/')[-1] for m in agent_data['provider_model']]
            ax.set_yticklabels(model_labels, fontsize=10)
            ax.set_xlabel('F1 Score', fontsize=11, fontweight='bold')
            ax.set_title(f'{agent}\nModel Rankings', fontsize=12, fontweight='bold')
            ax.set_xlim(0, max(agent_data['f1_score']) * 1.2)
            ax.grid(axis='x', alpha=0.3, linestyle='--')

            # 값과 순위 표시
            for i, (bar, f1, count) in enumerate(zip(bars, agent_data['f1_score'], agent_data['confidence_score'])):
                # F1 점수
                ax.text(
                    f1 + 0.01,
                    i,
                    f'{f1:.3f}',
                    va='center',
                    fontsize=9,
                    fontweight='bold'
                )
                # 테스트 수
                ax.text(
                    f1 / 2,
                    i,
                    f'n={int(count)}',
                    va='center',
                    ha='center',
                    fontsize=8,
                    color='white',
                    fontweight='bold'
                )

        plt.suptitle('Model Performance Rankings by Agent Type',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        filename = 'agent_model_rankings.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 순위 차트가 {filename}에 저장되었습니다.")
        plt.close()

    def create_comprehensive_comparison(self, min_tests=10):
        """종합 비교 그래프 (F1, Precision, Recall 한눈에)"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 집계
        agent_model_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'f1_score': 'mean',
            'precision': 'mean',
            'recall': 'mean',
            'confidence_score': 'count'
        }).reset_index()

        # 최소 테스트 수 필터링
        agent_model_stats = agent_model_stats[agent_model_stats['confidence_score'] >= min_tests]

        agents = sorted(agent_model_stats['agent_type'].unique())

        # 그래프 생성
        fig, ax = plt.subplots(figsize=(16, 10))

        # 각 에이전트별로 그룹화
        bar_width = 0.25
        x_positions = {}
        current_x = 0

        for agent_idx, agent in enumerate(agents):
            agent_data = agent_model_stats[agent_model_stats['agent_type'] == agent].copy()
            agent_data = agent_data.sort_values('f1_score', ascending=False)

            n_models = len(agent_data)
            x_base = np.arange(n_models) * 4 + current_x
            x_positions[agent] = (x_base[0], x_base[-1])

            # F1, Precision, Recall 막대
            ax.bar(x_base - bar_width, agent_data['f1_score'],
                   bar_width, label='F1' if agent_idx == 0 else '',
                   color='#FF6B6B', alpha=0.8, edgecolor='black')
            ax.bar(x_base, agent_data['precision'],
                   bar_width, label='Precision' if agent_idx == 0 else '',
                   color='#4ECDC4', alpha=0.8, edgecolor='black')
            ax.bar(x_base + bar_width, agent_data['recall'],
                   bar_width, label='Recall' if agent_idx == 0 else '',
                   color='#45B7D1', alpha=0.8, edgecolor='black')

            # 모델명 표시
            model_labels = [m.split('/')[-1][:15] for m in agent_data['provider_model']]
            ax.set_xticks(x_base)
            ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=9)

            current_x = x_base[-1] + 6

        # 에이전트 구분선 및 라벨
        for agent in agents:
            x_start, x_end = x_positions[agent]
            ax.axvline(x_start - 2, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.text((x_start + x_end) / 2, 1.05, agent,
                   ha='center', va='bottom', fontsize=12, fontweight='bold',
                   transform=ax.get_xaxis_transform())

        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Comprehensive Agent-Model Performance Comparison',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, 1.1)
        ax.legend(loc='upper right', fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()

        filename = 'comprehensive_agent_model_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 종합 비교 그래프가 {filename}에 저장되었습니다.")
        plt.close()

    def print_best_models_summary(self, min_tests=10):
        """에이전트별 최고 모델 요약 출력"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 집계
        agent_model_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'f1_score': 'mean',
            'precision': 'mean',
            'recall': 'mean',
            'confidence_score': ['mean', 'count'],
            'response_time': 'mean'
        }).reset_index()

        # 컬럼명 정리
        agent_model_stats.columns = ['agent_type', 'provider_model', 'f1_score',
                                     'precision', 'recall', 'confidence_score',
                                     'test_count', 'response_time']

        # 최소 테스트 수 필터링
        agent_model_stats = agent_model_stats[agent_model_stats['test_count'] >= min_tests]

        if agent_model_stats.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        print("\n" + "=" * 80)
        print("🏆 에이전트별 최고 성능 모델 요약")
        print("=" * 80)

        agents = sorted(agent_model_stats['agent_type'].unique())

        for agent in agents:
            agent_data = agent_model_stats[agent_model_stats['agent_type'] == agent]

            # F1 기준 최고 모델
            best_f1 = agent_data.loc[agent_data['f1_score'].idxmax()]

            # Precision 기준 최고 모델
            best_precision = agent_data.loc[agent_data['precision'].idxmax()]

            # Recall 기준 최고 모델
            best_recall = agent_data.loc[agent_data['recall'].idxmax()]

            # 가장 빠른 모델
            fastest = agent_data.loc[agent_data['response_time'].idxmin()]

            print(f"\n🎯 {agent}")
            print("-" * 80)
            print(f"  🥇 최고 F1 점수: {best_f1['provider_model']}")
            print(f"     - F1: {best_f1['f1_score']:.3f}, Precision: {best_f1['precision']:.3f}, Recall: {best_f1['recall']:.3f}")
            print(f"     - 테스트 수: {int(best_f1['test_count'])}개, 응답시간: {best_f1['response_time']:.2f}초")

            if best_precision['provider_model'] != best_f1['provider_model']:
                print(f"  📊 최고 Precision: {best_precision['provider_model']} ({best_precision['precision']:.3f})")

            if best_recall['provider_model'] != best_f1['provider_model']:
                print(f"  📈 최고 Recall: {best_recall['provider_model']} ({best_recall['recall']:.3f})")

            if fastest['provider_model'] != best_f1['provider_model']:
                print(f"  ⚡ 가장 빠른 모델: {fastest['provider_model']} ({fastest['response_time']:.2f}초)")

            # 전체 모델 순위 (F1 기준)
            agent_data_sorted = agent_data.sort_values('f1_score', ascending=False)
            print(f"\n  전체 모델 순위 (F1 기준):")
            for i, row in enumerate(agent_data_sorted.itertuples(), 1):
                print(f"    {i}. {row.provider_model}: F1 {row.f1_score:.3f} ({int(row.test_count)}개 테스트)")

        print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(description='에이전트별 모델 성능 시각화')
    parser.add_argument('results_file', help='벤치마크 결과 파일 (JSON)')
    parser.add_argument('--min-tests', type=int, default=10, help='최소 테스트 수 (기본값: 10)')
    parser.add_argument('--heatmap', action='store_true', help='히트맵 생성')
    parser.add_argument('--bar', action='store_true', help='막대 그래프 생성')
    parser.add_argument('--ranking', action='store_true', help='순위 차트 생성')
    parser.add_argument('--comprehensive', action='store_true', help='종합 비교 그래프 생성')
    parser.add_argument('--summary', action='store_true', help='요약 출력')
    parser.add_argument('--all', action='store_true', help='모든 그래프 및 요약 생성')

    args = parser.parse_args()

    if not Path(args.results_file).exists():
        print(f"❌ 결과 파일을 찾을 수 없습니다: {args.results_file}")
        return

    visualizer = AgentPerformanceVisualizer(args.results_file)

    if args.all or args.summary:
        visualizer.print_best_models_summary(args.min_tests)

    if args.all or args.heatmap:
        print("\n📊 히트맵 생성 중...")
        visualizer.create_agent_model_heatmap('f1_score', args.min_tests)

    if args.all or args.bar:
        print("\n📊 막대 그래프 생성 중...")
        visualizer.create_agent_comparison_bar(args.min_tests)

    if args.all or args.ranking:
        print("\n📊 순위 차트 생성 중...")
        visualizer.create_agent_model_ranking(args.min_tests)

    if args.all or args.comprehensive:
        print("\n📊 종합 비교 그래프 생성 중...")
        visualizer.create_comprehensive_comparison(args.min_tests)

    print("\n✅ 완료!")

if __name__ == "__main__":
    main()
