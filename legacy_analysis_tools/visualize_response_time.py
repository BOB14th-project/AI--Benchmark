#!/usr/bin/env python3
"""
에이전트별 모델 응답시간 시각화 도구
각 에이전트에서 모델별 평균 응답시간 비교
"""

import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

class ResponseTimeVisualizer:
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
        return df

    def create_response_time_comparison(self, min_tests=10):
        """에이전트별 모델 응답시간 비교 그래프"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 응답시간 집계
        response_time_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'response_time': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()

        # 컬럼명 정리
        response_time_stats.columns = ['agent_type', 'provider_model', 'mean', 'std', 'min', 'max', 'count']

        # 최소 테스트 수 필터링
        response_time_stats = response_time_stats[response_time_stats['count'] >= min_tests]

        if response_time_stats.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        agents = sorted(response_time_stats['agent_type'].unique())
        n_agents = len(agents)

        # 그래프 생성
        fig, axes = plt.subplots(1, n_agents, figsize=(7*n_agents, 6))
        if n_agents == 1:
            axes = [axes]

        for idx, agent in enumerate(agents):
            ax = axes[idx]

            # 해당 에이전트 데이터 필터링 및 정렬 (응답시간 빠른 순)
            agent_data = response_time_stats[response_time_stats['agent_type'] == agent].copy()
            agent_data = agent_data.sort_values('mean')

            # 모델명 간략화
            model_labels = [m.split('/')[-1] for m in agent_data['provider_model']]

            # 막대 그래프 (에러바 포함)
            x_pos = np.arange(len(agent_data))
            bars = ax.bar(
                x_pos,
                agent_data['mean'],
                yerr=agent_data['std'],
                capsize=5,
                alpha=0.7,
                edgecolor='black',
                linewidth=1.5,
                error_kw={'linewidth': 2, 'ecolor': 'darkred'}
            )

            # 색상 그라데이션 (빠를수록 초록색, 느릴수록 빨간색)
            max_time = agent_data['mean'].max()
            colors = plt.cm.RdYlGn_r(agent_data['mean'] / max_time)
            for bar, color in zip(bars, colors):
                bar.set_facecolor(color)

            # 레이블 설정
            ax.set_xticks(x_pos)
            ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=10)
            ax.set_ylabel('Average Response Time (seconds)', fontsize=11, fontweight='bold')
            ax.set_title(f'{agent}\nModel Response Times', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')

            # 값 표시
            for i, (bar, mean_time, count) in enumerate(zip(bars, agent_data['mean'], agent_data['count'])):
                # 평균 시간
                ax.text(
                    i,
                    mean_time + agent_data['std'].iloc[i] + max_time * 0.02,
                    f'{mean_time:.2f}s',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )
                # 테스트 수 (막대 안)
                ax.text(
                    i,
                    mean_time / 2,
                    f'n={int(count)}',
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='white',
                    fontweight='bold'
                )

            # 범위 표시 (최소-최대)
            y_max = (agent_data['mean'] + agent_data['std']).max() * 1.15
            ax.set_ylim(0, y_max)

        plt.suptitle('Average Response Time by Agent and Model',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        filename = 'agent_response_time_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 응답시간 비교 그래프가 {filename}에 저장되었습니다.")
        plt.close()

    def create_response_time_heatmap(self, min_tests=10):
        """응답시간 히트맵"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 평균 응답시간
        pivot_data = self.df.groupby(['agent_type', 'provider_model']).agg({
            'response_time': 'mean',
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
            values='response_time'
        )

        # 그래프 생성
        plt.figure(figsize=(14, 8))

        # 히트맵 (녹색=빠름, 빨간색=느림)
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn_r',  # 역순으로 빠를수록 녹색
            cbar_kws={'label': 'Average Response Time (seconds)'},
            linewidths=0.5,
            linecolor='gray'
        )

        plt.title('Response Time Heatmap: Agent vs Model (seconds)',
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Model', fontsize=12, fontweight='bold')
        plt.ylabel('Agent Type', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        filename = 'agent_response_time_heatmap.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 응답시간 히트맵이 {filename}에 저장되었습니다.")
        plt.close()

    def create_response_time_boxplot(self, min_tests=10):
        """응답시간 박스플롯 (분포 비교)"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 테스트 수 계산
        test_counts = self.df.groupby(['agent_type', 'provider_model']).size().reset_index(name='count')

        # 최소 테스트 수 필터링을 위한 조합 생성
        valid_combinations = test_counts[test_counts['count'] >= min_tests][['agent_type', 'provider_model']]

        # 필터링된 데이터
        filtered_df = self.df.merge(
            valid_combinations,
            on=['agent_type', 'provider_model'],
            how='inner'
        )

        if filtered_df.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        agents = sorted(filtered_df['agent_type'].unique())
        n_agents = len(agents)

        # 그래프 생성
        fig, axes = plt.subplots(1, n_agents, figsize=(7*n_agents, 6))
        if n_agents == 1:
            axes = [axes]

        for idx, agent in enumerate(agents):
            ax = axes[idx]

            # 해당 에이전트 데이터
            agent_data = filtered_df[filtered_df['agent_type'] == agent]

            # 모델별로 데이터 준비
            models = sorted(agent_data['provider_model'].unique())
            data_to_plot = [agent_data[agent_data['provider_model'] == model]['response_time'].values
                           for model in models]
            model_labels = [m.split('/')[-1] for m in models]

            # 박스플롯
            bp = ax.boxplot(
                data_to_plot,
                labels=model_labels,
                patch_artist=True,
                notch=True,
                showmeans=True,
                meanline=True
            )

            # 색상 설정
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(models)))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            # 레이블
            ax.set_xlabel('Model', fontsize=11, fontweight='bold')
            ax.set_ylabel('Response Time (seconds)', fontsize=11, fontweight='bold')
            ax.set_title(f'{agent}\nResponse Time Distribution', fontsize=12, fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.suptitle('Response Time Distribution by Agent and Model',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        filename = 'agent_response_time_boxplot.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 응답시간 박스플롯이 {filename}에 저장되었습니다.")
        plt.close()

    def print_response_time_summary(self, min_tests=10):
        """응답시간 요약 출력"""
        if self.df.empty:
            print("❌ 데이터가 없습니다.")
            return

        # 에이전트-모델별 응답시간 집계
        response_time_stats = self.df.groupby(['agent_type', 'provider_model']).agg({
            'response_time': ['mean', 'std', 'min', 'max', 'median', 'count']
        }).reset_index()

        # 컬럼명 정리
        response_time_stats.columns = ['agent_type', 'provider_model', 'mean', 'std', 'min', 'max', 'median', 'count']

        # 최소 테스트 수 필터링
        response_time_stats = response_time_stats[response_time_stats['count'] >= min_tests]

        if response_time_stats.empty:
            print(f"❌ 최소 {min_tests}개 테스트를 만족하는 데이터가 없습니다.")
            return

        print("\n" + "=" * 80)
        print("⚡ 에이전트별 모델 응답시간 요약")
        print("=" * 80)

        agents = sorted(response_time_stats['agent_type'].unique())

        for agent in agents:
            agent_data = response_time_stats[response_time_stats['agent_type'] == agent].copy()
            agent_data = agent_data.sort_values('mean')

            print(f"\n🎯 {agent}")
            print("-" * 80)

            # 가장 빠른 모델
            fastest = agent_data.iloc[0]
            print(f"  ⚡ 가장 빠른 모델: {fastest['provider_model']}")
            print(f"     - 평균: {fastest['mean']:.2f}초 (±{fastest['std']:.2f})")
            print(f"     - 중앙값: {fastest['median']:.2f}초")
            print(f"     - 범위: {fastest['min']:.2f}~{fastest['max']:.2f}초")
            print(f"     - 테스트 수: {int(fastest['count'])}개")

            # 가장 느린 모델
            slowest = agent_data.iloc[-1]
            if slowest['provider_model'] != fastest['provider_model']:
                print(f"\n  🐌 가장 느린 모델: {slowest['provider_model']}")
                print(f"     - 평균: {slowest['mean']:.2f}초 (±{slowest['std']:.2f})")
                print(f"     - 속도 차이: {slowest['mean'] / fastest['mean']:.1f}배 느림")

            # 전체 모델 순위
            print(f"\n  전체 모델 순위 (평균 응답시간 기준):")
            for i, row in enumerate(agent_data.itertuples(), 1):
                print(f"    {i}. {row.provider_model}: {row.mean:.2f}s (±{row.std:.2f}, 범위: {row.min:.2f}~{row.max:.2f})")

        # 전체 통합 순위
        print("\n" + "=" * 80)
        print("🏆 전체 모델 평균 응답시간 순위 (모든 에이전트 통합)")
        print("=" * 80)

        overall_stats = self.df.groupby('provider_model').agg({
            'response_time': ['mean', 'std', 'count']
        }).reset_index()
        overall_stats.columns = ['provider_model', 'mean', 'std', 'count']
        overall_stats = overall_stats[overall_stats['count'] >= min_tests * len(agents)]
        overall_stats = overall_stats.sort_values('mean')

        for i, row in enumerate(overall_stats.itertuples(), 1):
            print(f"  {i}. {row.provider_model}: {row.mean:.2f}s (±{row.std:.2f})")

        print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(description='에이전트별 모델 응답시간 시각화')
    parser.add_argument('results_file', help='벤치마크 결과 파일 (JSON)')
    parser.add_argument('--min-tests', type=int, default=10, help='최소 테스트 수 (기본값: 10)')
    parser.add_argument('--comparison', action='store_true', help='응답시간 비교 그래프 생성')
    parser.add_argument('--heatmap', action='store_true', help='응답시간 히트맵 생성')
    parser.add_argument('--boxplot', action='store_true', help='응답시간 박스플롯 생성')
    parser.add_argument('--summary', action='store_true', help='응답시간 요약 출력')
    parser.add_argument('--all', action='store_true', help='모든 그래프 및 요약 생성')

    args = parser.parse_args()

    if not Path(args.results_file).exists():
        print(f"❌ 결과 파일을 찾을 수 없습니다: {args.results_file}")
        return

    visualizer = ResponseTimeVisualizer(args.results_file)

    if args.all or args.summary:
        visualizer.print_response_time_summary(args.min_tests)

    if args.all or args.comparison:
        print("\n📊 응답시간 비교 그래프 생성 중...")
        visualizer.create_response_time_comparison(args.min_tests)

    if args.all or args.heatmap:
        print("\n📊 응답시간 히트맵 생성 중...")
        visualizer.create_response_time_heatmap(args.min_tests)

    if args.all or args.boxplot:
        print("\n📊 응답시간 박스플롯 생성 중...")
        visualizer.create_response_time_boxplot(args.min_tests)

    print("\n✅ 완료!")

if __name__ == "__main__":
    main()
