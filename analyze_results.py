#!/usr/bin/env python3
"""
벤치마크 결과 분석 도구
다양한 관점에서 결과를 분석하고 시각화합니다.
"""

import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

class ResultAnalyzer:
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.df = self._create_dataframe()

    def _load_results(self) -> Dict[str, Any]:
        """결과 파일 로드"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_dataframe(self) -> pd.DataFrame:
        """결과를 DataFrame으로 변환"""
        detailed_results = self.results.get('detailed_results', [])

        # 성공한 테스트만 필터링
        successful_results = [r for r in detailed_results if r.get('success', False)]

        if not successful_results:
            print("❌ 분석할 성공한 테스트 결과가 없습니다.")
            return pd.DataFrame()

        df = pd.DataFrame(successful_results)

        # 추가 계산 컬럼
        if not df.empty:
            df['provider_model'] = df['provider'] + '/' + df['model']
            df['total_tokens'] = df['usage'].apply(lambda x: x.get('total_tokens', 0) if isinstance(x, dict) else 0)
            df['efficiency'] = df.apply(
                lambda row: row['confidence_score'] / max(row['total_tokens'], 1) * 1000 if row['total_tokens'] > 0 else 0,
                axis=1
            )

        return df

    def compare_models(self) -> None:
        """모델별 성능 비교"""
        print("\n" + "=" * 60)
        print("🏆 모델별 성능 비교")
        print("=" * 60)

        if self.df.empty:
            print("❌ 분석할 데이터가 없습니다.")
            return

        # 모델별 집계
        model_stats = self.df.groupby('provider_model').agg({
            'confidence_score': ['mean', 'std', 'count'],
            'response_time': ['mean', 'std'],
            'detected_vulnerabilities': ['mean', 'std'],
            'valid_json': 'mean',
            'total_tokens': 'mean',
            'efficiency': 'mean'
        }).round(3)

        # 컬럼명 정리
        model_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in model_stats.columns]

        # F1 점수 계산 (단순화된 버전)
        model_stats['f1_score'] = model_stats['mean_confidence_score'] * model_stats['mean_valid_json']

        print("\n📊 모델별 상세 통계:")
        print("-" * 60)

        for model in model_stats.index:
            stats = model_stats.loc[model]
            print(f"\n🤖 {model}:")
            print(f"  테스트 수: {int(stats['count_confidence_score'])}")
            print(f"  평균 신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})")
            print(f"  평균 응답시간: {stats['mean_response_time']:.2f}초 (±{stats['std_response_time']:.2f})")
            print(f"  평균 취약점 탐지: {stats['mean_detected_vulnerabilities']:.1f}개")
            print(f"  JSON 유효성: {stats['mean_valid_json']:.1%}")
            print(f"  평균 토큰 사용: {stats['mean_total_tokens']:.0f}")
            print(f"  효율성: {stats['mean_efficiency']:.3f}")
            print(f"  F1 점수: {stats['f1_score']:.3f}")

        # 순위 출력
        print(f"\n🥇 모델 순위 (F1 점수 기준):")
        ranked_models = model_stats.sort_values('f1_score', ascending=False)
        for i, (model, stats) in enumerate(ranked_models.iterrows(), 1):
            print(f"  {i}. {model}: {stats['f1_score']:.3f}")

    def compare_agents(self) -> None:
        """에이전트별 성능 비교"""
        print("\n" + "=" * 60)
        print("🎯 에이전트별 성능 분석")
        print("=" * 60)

        if self.df.empty:
            return

        agent_stats = self.df.groupby('agent_type').agg({
            'confidence_score': ['mean', 'std', 'count'],
            'response_time': 'mean',
            'detected_vulnerabilities': 'mean',
            'valid_json': 'mean'
        }).round(3)

        agent_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in agent_stats.columns]

        for agent in agent_stats.index:
            stats = agent_stats.loc[agent]
            print(f"\n🔍 {agent}:")
            print(f"  테스트 수: {int(stats['count_confidence_score'])}")
            print(f"  평균 신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})")
            print(f"  평균 응답시간: {stats['mean_response_time']:.2f}초")
            print(f"  평균 취약점 탐지: {stats['mean_detected_vulnerabilities']:.1f}개")
            print(f"  JSON 유효성: {stats['mean_valid_json']:.1%}")

    def analyze_vulnerabilities(self) -> None:
        """취약점 탐지 분석"""
        print("\n" + "=" * 60)
        print("🔍 취약점 탐지 분석")
        print("=" * 60)

        if self.df.empty:
            return

        # 전체 통계
        total_tests = len(self.df)
        avg_vulnerabilities = self.df['detected_vulnerabilities'].mean()
        max_vulnerabilities = self.df['detected_vulnerabilities'].max()

        print(f"📊 전체 통계:")
        print(f"  총 테스트: {total_tests}")
        print(f"  평균 취약점 탐지: {avg_vulnerabilities:.1f}개")
        print(f"  최대 취약점 탐지: {int(max_vulnerabilities)}개")

        # 모델별 취약점 탐지 능력
        vuln_by_model = self.df.groupby('provider_model')['detected_vulnerabilities'].agg(['mean', 'max', 'count'])
        vuln_by_model = vuln_by_model.sort_values('mean', ascending=False)

        print(f"\n🎯 모델별 취약점 탐지 능력:")
        for model, stats in vuln_by_model.iterrows():
            print(f"  {model}: 평균 {stats['mean']:.1f}개, 최대 {int(stats['max'])}개 ({int(stats['count'])}개 테스트)")

        # 에이전트별 취약점 탐지
        vuln_by_agent = self.df.groupby('agent_type')['detected_vulnerabilities'].agg(['mean', 'max'])
        vuln_by_agent = vuln_by_agent.sort_values('mean', ascending=False)

        print(f"\n🔍 에이전트별 취약점 탐지:")
        for agent, stats in vuln_by_agent.iterrows():
            print(f"  {agent}: 평균 {stats['mean']:.1f}개, 최대 {int(stats['max'])}개")

    def performance_analysis(self) -> None:
        """성능 분석"""
        print("\n" + "=" * 60)
        print("⚡ 성능 분석")
        print("=" * 60)

        if self.df.empty:
            return

        # 응답 시간 분석
        response_stats = self.df.groupby('provider_model')['response_time'].agg(['mean', 'min', 'max', 'std'])
        response_stats = response_stats.sort_values('mean')

        print(f"📈 응답 시간 분석 (초):")
        for model, stats in response_stats.iterrows():
            print(f"  {model}: {stats['mean']:.2f}s (±{stats['std']:.2f}s, 범위: {stats['min']:.2f}s-{stats['max']:.2f}s)")

        # 토큰 효율성
        if 'total_tokens' in self.df.columns:
            token_stats = self.df.groupby('provider_model')['total_tokens'].agg(['mean', 'std'])
            efficiency_stats = self.df.groupby('provider_model')['efficiency'].agg(['mean', 'std'])

            print(f"\n💰 토큰 사용량 및 효율성:")
            for model in token_stats.index:
                token_mean = token_stats.loc[model, 'mean']
                token_std = token_stats.loc[model, 'std']
                eff_mean = efficiency_stats.loc[model, 'mean']
                print(f"  {model}: {token_mean:.0f} 토큰 (±{token_std:.0f}), 효율성: {eff_mean:.3f}")

    def correlation_analysis(self) -> None:
        """상관관계 분석"""
        print("\n" + "=" * 60)
        print("🔗 상관관계 분석")
        print("=" * 60)

        if self.df.empty or len(self.df) < 10:
            print("❌ 상관관계 분석에 충분한 데이터가 없습니다.")
            return

        # 수치형 컬럼만 선택
        numeric_cols = ['confidence_score', 'response_time', 'detected_vulnerabilities', 'total_tokens']
        available_cols = [col for col in numeric_cols if col in self.df.columns]

        if len(available_cols) < 2:
            print("❌ 상관관계 분석에 충분한 수치형 컬럼이 없습니다.")
            return

        correlation_matrix = self.df[available_cols].corr()

        print("📊 상관관계 매트릭스:")
        print(correlation_matrix.round(3))

        # 주요 상관관계 해석
        print("\n🔍 주요 발견사항:")
        if 'confidence_score' in available_cols and 'detected_vulnerabilities' in available_cols:
            corr_conf_vuln = correlation_matrix.loc['confidence_score', 'detected_vulnerabilities']
            print(f"  신뢰도 vs 취약점 탐지: {corr_conf_vuln:.3f}")

        if 'response_time' in available_cols and 'confidence_score' in available_cols:
            corr_time_conf = correlation_matrix.loc['response_time', 'confidence_score']
            print(f"  응답시간 vs 신뢰도: {corr_time_conf:.3f}")

    def generate_report(self, output_file: str = None) -> None:
        """종합 리포트 생성"""
        if output_file is None:
            output_file = f"analysis_report_{int(self.results['metadata']['timestamp'])}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            # 기본 정보 저장
            f.write("AI 벤치마크 결과 분석 리포트\n")
            f.write("=" * 60 + "\n\n")

            metadata = self.results.get('metadata', {})
            f.write(f"실행 시간: {metadata.get('timestamp', 'Unknown')}\n")
            f.write(f"총 테스트: {metadata.get('total_tests', 'Unknown')}\n")
            f.write(f"프로바이더: {', '.join(metadata.get('providers', []))}\n")
            f.write(f"에이전트: {', '.join(metadata.get('agents', []))}\n\n")

            # 요약 통계 저장
            summary = self.results.get('summary', {})
            f.write(f"성공률: {summary.get('success_rate', 0):.1%}\n")
            f.write(f"성공한 테스트: {summary.get('successful_tests', 0)}\n\n")

        print(f"📄 분석 리포트가 {output_file}에 저장되었습니다.")

    def create_visualizations(self) -> None:
        """시각화 생성"""
        if self.df.empty:
            print("❌ 시각화할 데이터가 없습니다.")
            return

        print("\n📊 시각화 생성 중...")

        # 스타일 설정
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Malgun Gothic', 'Apple Gothic']

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI 벤치마크 결과 분석', fontsize=16)

        # 1. 모델별 성능 비교
        model_performance = self.df.groupby('provider_model')['confidence_score'].mean().sort_values(ascending=True)
        axes[0, 0].barh(range(len(model_performance)), model_performance.values)
        axes[0, 0].set_yticks(range(len(model_performance)))
        axes[0, 0].set_yticklabels(model_performance.index)
        axes[0, 0].set_xlabel('평균 신뢰도 점수')
        axes[0, 0].set_title('모델별 성능 비교')

        # 2. 응답 시간 분포
        self.df.boxplot(column='response_time', by='provider_model', ax=axes[0, 1])
        axes[0, 1].set_xlabel('모델')
        axes[0, 1].set_ylabel('응답 시간 (초)')
        axes[0, 1].set_title('모델별 응답 시간 분포')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. 에이전트별 성능
        agent_performance = self.df.groupby('agent_type')['confidence_score'].mean()
        axes[1, 0].bar(range(len(agent_performance)), agent_performance.values)
        axes[1, 0].set_xticks(range(len(agent_performance)))
        axes[1, 0].set_xticklabels(agent_performance.index, rotation=45)
        axes[1, 0].set_ylabel('평균 신뢰도 점수')
        axes[1, 0].set_title('에이전트별 성능')

        # 4. 취약점 탐지 vs 신뢰도
        if 'detected_vulnerabilities' in self.df.columns:
            axes[1, 1].scatter(self.df['detected_vulnerabilities'], self.df['confidence_score'], alpha=0.6)
            axes[1, 1].set_xlabel('탐지된 취약점 수')
            axes[1, 1].set_ylabel('신뢰도 점수')
            axes[1, 1].set_title('취약점 탐지 vs 신뢰도')

        plt.tight_layout()
        plt.savefig('benchmark_analysis.png', dpi=300, bbox_inches='tight')
        print("📊 시각화가 benchmark_analysis.png에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(description='벤치마크 결과 분석')
    parser.add_argument('results_file', help='분석할 결과 파일')
    parser.add_argument('--compare-models', action='store_true', help='모델별 성능 비교')
    parser.add_argument('--compare-agents', action='store_true', help='에이전트별 성능 비교')
    parser.add_argument('--vulnerability-analysis', action='store_true', help='취약점 탐지 분석')
    parser.add_argument('--performance-analysis', action='store_true', help='성능 분석')
    parser.add_argument('--correlation', action='store_true', help='상관관계 분석')
    parser.add_argument('--visualize', action='store_true', help='시각화 생성')
    parser.add_argument('--report', help='리포트 파일명')
    parser.add_argument('--all', action='store_true', help='모든 분석 실행')

    args = parser.parse_args()

    if not Path(args.results_file).exists():
        print(f"❌ 결과 파일을 찾을 수 없습니다: {args.results_file}")
        return

    analyzer = ResultAnalyzer(args.results_file)

    if args.all or args.compare_models:
        analyzer.compare_models()

    if args.all or args.compare_agents:
        analyzer.compare_agents()

    if args.all or args.vulnerability_analysis:
        analyzer.analyze_vulnerabilities()

    if args.all or args.performance_analysis:
        analyzer.performance_analysis()

    if args.all or args.correlation:
        analyzer.correlation_analysis()

    if args.all or args.visualize:
        try:
            analyzer.create_visualizations()
        except ImportError:
            print("⚠️  matplotlib가 설치되지 않아 시각화를 건너뜁니다.")

    if args.report or args.all:
        analyzer.generate_report(args.report)

if __name__ == "__main__":
    main()