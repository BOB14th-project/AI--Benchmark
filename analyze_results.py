#!/usr/bin/env python3
"""
양자 취약 알고리즘 탐지 벤치마크 결과 분석 도구
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
        self.ground_truth_cache = {}
        self.df = self._create_dataframe()

    def _load_results(self) -> Dict[str, Any]:
        """결과 파일 로드"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_ground_truth(self, file_path: str) -> Dict[str, Any]:
        """Ground truth 파일 로드 (캐싱)"""
        if file_path in self.ground_truth_cache:
            return self.ground_truth_cache[file_path]

        # file_path에서 ground truth 경로 생성
        # data/test_files/source_code/file.py -> data/ground_truth/source_code/file.json
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
            except FileNotFoundError:
                return None
        return None

    def _calculate_precision_recall(self, detected: List[str], expected: List[str]) -> tuple:
        """Precision과 Recall 계산"""
        if not detected and not expected:
            return 1.0, 1.0, 1.0

        if not detected:
            return 0.0, 0.0, 0.0

        if not expected:
            return 0.0, 1.0, 0.0

        # 대소문자 무시하고 비교
        detected_set = set(alg.lower() for alg in detected)
        expected_set = set(alg.lower() for alg in expected)

        # 부분 매칭도 고려 (예: "RSA-2048" in detected, "RSA" in expected)
        true_positives = 0
        for exp in expected_set:
            for det in detected_set:
                if exp in det or det in exp:
                    true_positives += 1
                    break

        precision = true_positives / len(detected_set) if detected_set else 0.0
        recall = true_positives / len(expected_set) if expected_set else 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return precision, recall, f1

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

            # 취약점 관련 컬럼명 변경
            if 'detected_vulnerabilities' in df.columns:
                df['detected_quantum_vulnerable_count'] = df['detected_vulnerabilities']
                df = df.drop(columns=['detected_vulnerabilities'])

            # Precision, Recall, F1 계산
            print("📊 Ground truth 기반 Precision, Recall, F1 계산 중...")
            precisions = []
            recalls = []
            f1_scores = []

            for idx, row in df.iterrows():
                file_path = row.get('file_path', '')
                detected_algos = row.get('detected_algorithms', [])

                # Ground truth 로드
                gt = self._load_ground_truth(file_path)

                if gt and 'expected_findings' in gt:
                    expected_algos = gt['expected_findings'].get('vulnerable_algorithms_detected', [])
                    precision, recall, f1 = self._calculate_precision_recall(detected_algos, expected_algos)
                else:
                    # Ground truth가 없으면 confidence_score를 기준으로
                    precision = row['confidence_score']
                    recall = row['confidence_score']
                    f1 = row['confidence_score']

                precisions.append(precision)
                recalls.append(recall)
                f1_scores.append(f1)

            df['precision'] = precisions
            df['recall'] = recalls
            df['f1_score'] = f1_scores

            print(f"✅ Precision, Recall, F1 계산 완료 (평균 F1: {np.mean(f1_scores):.3f})")

        return df

    def compare_models(self, min_tests: int = 30) -> None:
        """모델별 성능 비교

        Args:
            min_tests: 순위에 포함되기 위한 최소 테스트 수 (기본값: 30)
        """
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
            'detected_quantum_vulnerable_count': ['mean', 'std'],
            'valid_json': 'mean',
            'total_tokens': 'mean',
            'efficiency': 'mean',
            'precision': ['mean', 'std'],
            'recall': ['mean', 'std'],
            'f1_score': ['mean', 'std']
        }).round(3)

        # 컬럼명 정리
        model_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in model_stats.columns]

        # F1 점수로 정렬
        model_stats = model_stats.sort_values('mean_f1_score', ascending=False)

        # 통계적 신뢰도 표시
        insufficient_tests = model_stats[model_stats['count_confidence_score'] < min_tests]
        if not insufficient_tests.empty:
            print(f"\n⚠️  경고: 다음 모델은 테스트 수가 부족하여 통계적 신뢰도가 낮을 수 있습니다 (최소 {min_tests}개 필요):")
            for model, stats in insufficient_tests.iterrows():
                print(f"  - {model}: {int(stats['count_confidence_score'])}개 테스트")

        print("\n📊 모델별 상세 통계:")
        print("-" * 60)

        for model in model_stats.index:
            stats = model_stats.loc[model]
            print(f"\n🤖 {model}:")
            print(f"  테스트 수: {int(stats['count_confidence_score'])}")
            print(f"  평균 신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})")
            print(f"  평균 응답시간: {stats['mean_response_time']:.2f}초 (±{stats['std_response_time']:.2f})")
            print(f"  평균 양자 취약 알고리즘 탐지: {stats['mean_detected_quantum_vulnerable_count']:.1f}개")
            print(f"  JSON 유효성: {stats['mean_valid_json']:.1%}")
            print(f"  평균 토큰 사용: {stats['mean_total_tokens']:.0f}")
            print(f"  효율성: {stats['mean_efficiency']:.3f}")
            print(f"  Precision: {stats['mean_precision']:.3f} (±{stats['std_precision']:.3f})")
            print(f"  Recall: {stats['mean_recall']:.3f} (±{stats['std_recall']:.3f})")
            print(f"  F1 점수: {stats['mean_f1_score']:.3f} (±{stats['std_f1_score']:.3f})")

        # 순위 출력 (전체)
        print(f"\n🥇 모델 순위 (F1 점수 기준) - 전체:")
        for i, (model, stats) in enumerate(model_stats.iterrows(), 1):
            test_count = int(stats['count_confidence_score'])
            warning = " ⚠️ " if test_count < min_tests else ""
            print(f"  {i}. {model}: {stats['mean_f1_score']:.3f} ({test_count}개 테스트){warning}")

        # 충분한 테스트가 있는 모델만 필터링
        reliable_models = model_stats[model_stats['count_confidence_score'] >= min_tests]
        if not reliable_models.empty and len(reliable_models) < len(model_stats):
            print(f"\n🏆 모델 순위 (F1 점수 기준) - 신뢰할 수 있는 결과만 (테스트 수 >= {min_tests}):")
            for i, (model, stats) in enumerate(reliable_models.iterrows(), 1):
                test_count = int(stats['count_confidence_score'])
                print(f"  {i}. {model}: {stats['mean_f1_score']:.3f} ({test_count}개 테스트)")

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
            'detected_quantum_vulnerable_count': 'mean',
            'valid_json': 'mean'
        }).round(3)

        agent_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in agent_stats.columns]

        for agent in agent_stats.index:
            stats = agent_stats.loc[agent]
            print(f"\n🔍 {agent}:")
            print(f"  테스트 수: {int(stats['count_confidence_score'])}")
            print(f"  평균 신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})")
            print(f"  평균 응답시간: {stats['mean_response_time']:.2f}초")
            print(f"  평균 양자 취약 알고리즘 탐지: {stats['mean_detected_quantum_vulnerable_count']:.1f}개")
            print(f"  JSON 유효성: {stats['mean_valid_json']:.1%}")

    def analyze_quantum_vulnerable_algorithms(self) -> None:
        """양자 취약 알고리즘 탐지 분석"""
        print("\n" + "=" * 60)
        print("🔍 양자 취약 알고리즘 탐지 분석")
        print("=" * 60)

        if self.df.empty:
            return

        # 전체 통계
        total_tests = len(self.df)
        avg_vulnerabilities = self.df['detected_quantum_vulnerable_count'].mean()
        max_vulnerabilities = self.df['detected_quantum_vulnerable_count'].max()

        print(f"📊 전체 통계:")
        print(f"  총 테스트: {total_tests}")
        print(f"  평균 양자 취약 알고리즘 탐지: {avg_vulnerabilities:.1f}개")
        print(f"  최대 양자 취약 알고리즘 탐지: {int(max_vulnerabilities)}개")

        # 모델별 양자 취약 알고리즘 탐지 능력
        vuln_by_model = self.df.groupby('provider_model')['detected_quantum_vulnerable_count'].agg(['mean', 'max', 'count'])
        vuln_by_model = vuln_by_model.sort_values('mean', ascending=False)

        print(f"\n🎯 모델별 양자 취약 알고리즘 탐지 능력:")
        for model, stats in vuln_by_model.iterrows():
            print(f"  {model}: 평균 {stats['mean']:.1f}개, 최대 {int(stats['max'])}개 ({int(stats['count'])}개 테스트)")

        # 에이전트별 양자 취약 알고리즘 탐지
        vuln_by_agent = self.df.groupby('agent_type')['detected_quantum_vulnerable_count'].agg(['mean', 'max'])
        vuln_by_agent = vuln_by_agent.sort_values('mean', ascending=False)

        print(f"\n🔍 에이전트별 양자 취약 알고리즘 탐지:")
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
        numeric_cols = ['confidence_score', 'response_time', 'detected_quantum_vulnerable_count', 'total_tokens']
        available_cols = [col for col in numeric_cols if col in self.df.columns]

        if len(available_cols) < 2:
            print("❌ 상관관계 분석에 충분한 수치형 컬럼이 없습니다.")
            return

        correlation_matrix = self.df[available_cols].corr()

        print("📊 상관관계 매트릭스:")
        print(correlation_matrix.round(3))

        # 주요 상관관계 해석
        print("\n🔍 주요 발견사항:")
        if 'confidence_score' in available_cols and 'detected_quantum_vulnerable_count' in available_cols:
            corr_conf_vuln = correlation_matrix.loc['confidence_score', 'detected_quantum_vulnerable_count']
            print(f"  신뢰도 vs 양자 취약 알고리즘 탐지: {corr_conf_vuln:.3f}")

        if 'response_time' in available_cols and 'confidence_score' in available_cols:
            corr_time_conf = correlation_matrix.loc['response_time', 'confidence_score']
            print(f"  응답시간 vs 신뢰도: {corr_time_conf:.3f}")

    def generate_report(self, output_file: str = None, min_tests: int = 30) -> None:
        """종합 리포트 생성

        Args:
            output_file: 리포트 파일 경로
            min_tests: 신뢰할 수 있는 결과로 간주하는 최소 테스트 수
        """
        if output_file is None:
            output_file = f"analysis_report_{int(self.results['metadata']['timestamp'])}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            # 헤더
            f.write("=" * 80 + "\n")
            f.write("AI 벤치마크 결과 분석 리포트 - 양자 취약 알고리즘 탐지 성능 평가\n")
            f.write("=" * 80 + "\n\n")

            # 메타데이터
            metadata = self.results.get('metadata', {})
            f.write("📋 실행 정보\n")
            f.write("-" * 80 + "\n")
            f.write(f"실행 시간: {metadata.get('timestamp', 'Unknown')}\n")
            f.write(f"총 테스트: {metadata.get('total_tests', 'Unknown')}\n")
            f.write(f"프로바이더: {', '.join(metadata.get('providers', []))}\n")
            f.write(f"에이전트: {', '.join(metadata.get('agents', []))}\n")
            f.write(f"테스트 파일 수: {len(metadata.get('test_files', []))}\n\n")

            # 요약 통계
            summary = self.results.get('summary', {})
            f.write("📊 요약 통계\n")
            f.write("-" * 80 + "\n")
            f.write(f"성공률: {summary.get('success_rate', 0):.1%}\n")
            f.write(f"성공한 테스트: {summary.get('successful_tests', 0)}\n")
            f.write(f"실패한 테스트: {summary.get('failed_tests', 0)}\n")
            f.write(f"평균 신뢰도: {summary.get('avg_confidence', 0):.3f}\n")
            f.write(f"평균 응답시간: {summary.get('avg_response_time', 0):.2f}초\n\n")

            if self.df.empty:
                f.write("❌ 분석할 데이터가 없습니다.\n")
                return

            # 모델별 성능 비교
            f.write("=" * 80 + "\n")
            f.write("🏆 모델별 성능 비교\n")
            f.write("=" * 80 + "\n\n")

            model_stats = self.df.groupby('provider_model').agg({
                'confidence_score': ['mean', 'std', 'min', 'max', 'count'],
                'response_time': ['mean', 'std', 'min', 'max'],
                'detected_quantum_vulnerable_count': ['mean', 'std', 'min', 'max', 'sum'],
                'valid_json': ['mean', 'sum'],
                'total_tokens': 'mean',
                'efficiency': 'mean',
                'precision': ['mean', 'std', 'min', 'max'],
                'recall': ['mean', 'std', 'min', 'max'],
                'f1_score': ['mean', 'std', 'min', 'max']
            }).round(3)

            model_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in model_stats.columns]
            model_stats = model_stats.sort_values('mean_f1_score', ascending=False)

            # 통계적 신뢰도 경고
            insufficient_tests = model_stats[model_stats['count_confidence_score'] < min_tests]
            if not insufficient_tests.empty:
                f.write(f"⚠️  경고: 다음 모델은 테스트 수가 부족하여 통계적 신뢰도가 낮습니다 (최소 {min_tests}개 필요):\n")
                for model, stats in insufficient_tests.iterrows():
                    f.write(f"  - {model}: {int(stats['count_confidence_score'])}개 테스트\n")
                f.write("\n")

            for i, (model, stats) in enumerate(model_stats.iterrows(), 1):
                test_count = int(stats['count_confidence_score'])
                warning_mark = " ⚠️  (통계적 신뢰도 낮음)" if test_count < min_tests else ""
                f.write(f"{i}. {model}{warning_mark}\n")
                f.write("-" * 80 + "\n")
                f.write(f"  테스트 수: {test_count}\n")
                f.write(f"  F1 점수: {stats['mean_f1_score']:.3f} (±{stats['std_f1_score']:.3f}, 범위: {stats['min_f1_score']:.3f}~{stats['max_f1_score']:.3f})\n")
                f.write(f"  Precision: {stats['mean_precision']:.3f} (±{stats['std_precision']:.3f}, 범위: {stats['min_precision']:.3f}~{stats['max_precision']:.3f})\n")
                f.write(f"  Recall: {stats['mean_recall']:.3f} (±{stats['std_recall']:.3f}, 범위: {stats['min_recall']:.3f}~{stats['max_recall']:.3f})\n")
                f.write(f"  신뢰도 점수:\n")
                f.write(f"    - 평균: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})\n")
                f.write(f"    - 범위: {stats['min_confidence_score']:.3f} ~ {stats['max_confidence_score']:.3f}\n")
                f.write(f"  응답 시간 (초):\n")
                f.write(f"    - 평균: {stats['mean_response_time']:.2f} (±{stats['std_response_time']:.2f})\n")
                f.write(f"    - 범위: {stats['min_response_time']:.2f} ~ {stats['max_response_time']:.2f}\n")
                f.write(f"  양자 취약 알고리즘 탐지:\n")
                f.write(f"    - 평균: {stats['mean_detected_quantum_vulnerable_count']:.1f}개 (±{stats['std_detected_quantum_vulnerable_count']:.1f})\n")
                f.write(f"    - 범위: {int(stats['min_detected_quantum_vulnerable_count'])} ~ {int(stats['max_detected_quantum_vulnerable_count'])}개\n")
                f.write(f"    - 총합: {int(stats['sum_detected_quantum_vulnerable_count'])}개\n")
                f.write(f"  JSON 유효성: {stats['mean_valid_json']:.1%} ({int(stats['sum_valid_json'])}/{int(stats['count_confidence_score'])})\n")
                f.write(f"  평균 토큰 사용: {stats['mean_total_tokens']:.0f}\n")
                f.write(f"  효율성 (신뢰도/토큰*1000): {stats['mean_efficiency']:.3f}\n\n")

            # 에이전트별 성능 분석
            f.write("=" * 80 + "\n")
            f.write("🎯 에이전트별 성능 분석\n")
            f.write("=" * 80 + "\n\n")

            agent_stats = self.df.groupby('agent_type').agg({
                'confidence_score': ['mean', 'std', 'min', 'max', 'count'],
                'response_time': ['mean', 'std', 'min', 'max'],
                'detected_quantum_vulnerable_count': ['mean', 'std', 'min', 'max', 'sum'],
                'valid_json': 'mean'
            }).round(3)

            agent_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in agent_stats.columns]

            for agent, stats in agent_stats.iterrows():
                f.write(f"🔍 {agent}\n")
                f.write("-" * 80 + "\n")
                f.write(f"  테스트 수: {int(stats['count_confidence_score'])}\n")
                f.write(f"  신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f}, 범위: {stats['min_confidence_score']:.3f}~{stats['max_confidence_score']:.3f})\n")
                f.write(f"  응답시간: {stats['mean_response_time']:.2f}초 (±{stats['std_response_time']:.2f}, 범위: {stats['min_response_time']:.2f}~{stats['max_response_time']:.2f})\n")
                f.write(f"  양자 취약 알고리즘 탐지: {stats['mean_detected_quantum_vulnerable_count']:.1f}개 (±{stats['std_detected_quantum_vulnerable_count']:.1f}, 범위: {int(stats['min_detected_quantum_vulnerable_count'])}~{int(stats['max_detected_quantum_vulnerable_count'])}개)\n")
                f.write(f"  총 탐지 수: {int(stats['sum_detected_quantum_vulnerable_count'])}개\n")
                f.write(f"  JSON 유효성: {stats['mean_valid_json']:.1%}\n\n")

            # 양자 취약 알고리즘 탐지 분석
            f.write("=" * 80 + "\n")
            f.write("🔍 양자 취약 알고리즘 탐지 상세 분석\n")
            f.write("=" * 80 + "\n\n")

            total_tests = len(self.df)
            total_detected = self.df['detected_quantum_vulnerable_count'].sum()
            avg_detected = self.df['detected_quantum_vulnerable_count'].mean()
            max_detected = self.df['detected_quantum_vulnerable_count'].max()

            f.write(f"총 테스트: {total_tests}\n")
            f.write(f"총 탐지 알고리즘 수: {int(total_detected)}개\n")
            f.write(f"평균 탐지 수: {avg_detected:.1f}개\n")
            f.write(f"최대 탐지 수: {int(max_detected)}개\n\n")

            # 모델별 양자 취약 알고리즘 탐지 능력
            f.write("📊 모델별 양자 취약 알고리즘 탐지 능력\n")
            f.write("-" * 80 + "\n")
            vuln_by_model = self.df.groupby('provider_model')['detected_quantum_vulnerable_count'].agg(['mean', 'std', 'min', 'max', 'sum', 'count'])
            vuln_by_model = vuln_by_model.sort_values('mean', ascending=False)

            for model, stats in vuln_by_model.iterrows():
                f.write(f"{model}:\n")
                f.write(f"  평균: {stats['mean']:.1f}개 (±{stats['std']:.1f})\n")
                f.write(f"  범위: {int(stats['min'])} ~ {int(stats['max'])}개\n")
                f.write(f"  총합: {int(stats['sum'])}개 ({int(stats['count'])}개 테스트)\n\n")

            # 에이전트별 양자 취약 알고리즘 탐지
            f.write("📊 에이전트별 양자 취약 알고리즘 탐지\n")
            f.write("-" * 80 + "\n")
            vuln_by_agent = self.df.groupby('agent_type')['detected_quantum_vulnerable_count'].agg(['mean', 'std', 'min', 'max', 'sum', 'count'])
            vuln_by_agent = vuln_by_agent.sort_values('mean', ascending=False)

            for agent, stats in vuln_by_agent.iterrows():
                f.write(f"{agent}:\n")
                f.write(f"  평균: {stats['mean']:.1f}개 (±{stats['std']:.1f})\n")
                f.write(f"  범위: {int(stats['min'])} ~ {int(stats['max'])}개\n")
                f.write(f"  총합: {int(stats['sum'])}개 ({int(stats['count'])}개 테스트)\n\n")

            # 성능 분석
            f.write("=" * 80 + "\n")
            f.write("⚡ 성능 분석\n")
            f.write("=" * 80 + "\n\n")

            # 응답 시간 분석
            f.write("📈 응답 시간 분석 (초)\n")
            f.write("-" * 80 + "\n")
            response_stats = self.df.groupby('provider_model')['response_time'].agg(['mean', 'std', 'min', 'max', 'median'])
            response_stats = response_stats.sort_values('mean')

            for model, stats in response_stats.iterrows():
                f.write(f"{model}:\n")
                f.write(f"  평균: {stats['mean']:.2f}초 (±{stats['std']:.2f})\n")
                f.write(f"  중앙값: {stats['median']:.2f}초\n")
                f.write(f"  범위: {stats['min']:.2f} ~ {stats['max']:.2f}초\n\n")

            # 토큰 효율성
            if 'total_tokens' in self.df.columns and self.df['total_tokens'].sum() > 0:
                f.write("💰 토큰 사용량 및 효율성\n")
                f.write("-" * 80 + "\n")
                token_stats = self.df.groupby('provider_model').agg({
                    'total_tokens': ['mean', 'std', 'sum'],
                    'efficiency': 'mean'
                }).round(3)
                token_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in token_stats.columns]

                for model in token_stats.index:
                    f.write(f"{model}:\n")
                    f.write(f"  평균 토큰: {token_stats.loc[model, 'mean_total_tokens']:.0f} (±{token_stats.loc[model, 'std_total_tokens']:.0f})\n")
                    f.write(f"  총 토큰: {token_stats.loc[model, 'sum_total_tokens']:.0f}\n")
                    f.write(f"  효율성: {token_stats.loc[model, 'mean_efficiency']:.3f}\n\n")

            # 상관관계 분석
            if len(self.df) >= 10:
                f.write("=" * 80 + "\n")
                f.write("🔗 상관관계 분석\n")
                f.write("=" * 80 + "\n\n")

                numeric_cols = ['confidence_score', 'response_time', 'detected_quantum_vulnerable_count', 'total_tokens']
                available_cols = [col for col in numeric_cols if col in self.df.columns]

                if len(available_cols) >= 2:
                    correlation_matrix = self.df[available_cols].corr()
                    f.write("상관관계 매트릭스:\n")
                    f.write("-" * 80 + "\n")
                    f.write(correlation_matrix.to_string())
                    f.write("\n\n")

                    # 주요 상관관계 해석
                    f.write("주요 발견사항:\n")
                    f.write("-" * 80 + "\n")
                    if 'confidence_score' in available_cols and 'detected_quantum_vulnerable_count' in available_cols:
                        corr = correlation_matrix.loc['confidence_score', 'detected_quantum_vulnerable_count']
                        f.write(f"신뢰도 vs 양자 취약 알고리즘 탐지: {corr:.3f}\n")
                    if 'response_time' in available_cols and 'confidence_score' in available_cols:
                        corr = correlation_matrix.loc['response_time', 'confidence_score']
                        f.write(f"응답시간 vs 신뢰도: {corr:.3f}\n")
                    if 'total_tokens' in available_cols and 'confidence_score' in available_cols:
                        corr = correlation_matrix.loc['total_tokens', 'confidence_score']
                        f.write(f"토큰 사용량 vs 신뢰도: {corr:.3f}\n")
                    f.write("\n")

            # 모델-에이전트 조합별 성능
            f.write("=" * 80 + "\n")
            f.write("🔬 모델-에이전트 조합별 상세 성능\n")
            f.write("=" * 80 + "\n\n")

            combo_stats = self.df.groupby(['provider_model', 'agent_type']).agg({
                'confidence_score': ['mean', 'std', 'count'],
                'response_time': 'mean',
                'detected_quantum_vulnerable_count': ['mean', 'sum']
            }).round(3)

            combo_stats.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in combo_stats.columns]

            for (model, agent), stats in combo_stats.iterrows():
                f.write(f"{model} + {agent}:\n")
                f.write(f"  테스트 수: {int(stats['count_confidence_score'])}\n")
                f.write(f"  평균 신뢰도: {stats['mean_confidence_score']:.3f} (±{stats['std_confidence_score']:.3f})\n")
                f.write(f"  평균 응답시간: {stats['mean_response_time']:.2f}초\n")
                f.write(f"  평균 탐지: {stats['mean_detected_quantum_vulnerable_count']:.1f}개 (총 {int(stats['sum_detected_quantum_vulnerable_count'])}개)\n\n")

            # 종합 결론
            f.write("=" * 80 + "\n")
            f.write("📌 종합 결론\n")
            f.write("=" * 80 + "\n\n")

            # 신뢰할 수 있는 모델 (충분한 테스트 수)
            reliable_models = model_stats[model_stats['count_confidence_score'] >= min_tests]

            if not reliable_models.empty:
                best_reliable_model = reliable_models.index[0]
                f.write(f"✅ 최고 성능 모델 (F1 점수, 신뢰할 수 있는 결과): {best_reliable_model}\n")
                f.write(f"   - F1: {reliable_models.loc[best_reliable_model, 'mean_f1_score']:.3f}\n")
                f.write(f"   - Precision: {reliable_models.loc[best_reliable_model, 'mean_precision']:.3f}\n")
                f.write(f"   - Recall: {reliable_models.loc[best_reliable_model, 'mean_recall']:.3f}\n")
                f.write(f"   - 테스트 수: {int(reliable_models.loc[best_reliable_model, 'count_confidence_score'])}개\n\n")

            # 전체 1위 (테스트 수 무관)
            best_model_overall = model_stats.index[0]
            best_model_test_count = int(model_stats.loc[best_model_overall, 'count_confidence_score'])
            if best_model_test_count < min_tests and not reliable_models.empty:
                f.write(f"⚠️  참고: 전체 1위는 {best_model_overall} (F1: {model_stats.loc[best_model_overall, 'mean_f1_score']:.3f})이지만,\n")
                f.write(f"    테스트 수가 {best_model_test_count}개로 부족하여 통계적 신뢰도가 낮습니다.\n\n")

            fastest_model = response_stats.index[0]
            best_detector = vuln_by_model.index[0]

            f.write(f"⚡ 가장 빠른 모델: {fastest_model} ({response_stats.loc[fastest_model, 'mean']:.2f}초)\n")
            f.write(f"🔍 최다 탐지 모델: {best_detector} (평균 {vuln_by_model.loc[best_detector, 'mean']:.1f}개)\n")
            f.write(f"🎯 최고 성능 에이전트: {agent_stats.index[agent_stats['mean_confidence_score'].argmax()]} ")
            f.write(f"(신뢰도 {agent_stats['mean_confidence_score'].max():.3f})\n\n")

            f.write("리포트 생성 완료.\n")

        print(f"📄 분석 리포트가 {output_file}에 저장되었습니다.")

    def create_visualizations(self) -> None:
        """시각화 생성"""
        if self.df.empty:
            print("❌ 시각화할 데이터가 없습니다.")
            return

        print("\n📊 시각화 생성 중...")

        # 스타일 설정
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        # macOS에서 사용 가능한 폰트 설정
        plt.rcParams['font.family'] = ['AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Benchmark Results Analysis', fontsize=16)

        # 1. Model Performance Comparison
        model_performance = self.df.groupby('provider_model')['confidence_score'].mean().sort_values(ascending=True)
        axes[0, 0].barh(range(len(model_performance)), model_performance.values)
        axes[0, 0].set_yticks(range(len(model_performance)))
        axes[0, 0].set_yticklabels(model_performance.index)
        axes[0, 0].set_xlabel('Average Confidence Score')
        axes[0, 0].set_title('Model Performance Comparison')

        # 2. Response Time Distribution
        self.df.boxplot(column='response_time', by='provider_model', ax=axes[0, 1])
        axes[0, 1].set_xlabel('Model')
        axes[0, 1].set_ylabel('Response Time (s)')
        axes[0, 1].set_title('Response Time Distribution by Model')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Agent Performance
        agent_performance = self.df.groupby('agent_type')['confidence_score'].mean()
        axes[1, 0].bar(range(len(agent_performance)), agent_performance.values)
        axes[1, 0].set_xticks(range(len(agent_performance)))
        axes[1, 0].set_xticklabels(agent_performance.index, rotation=45)
        axes[1, 0].set_ylabel('Average Confidence Score')
        axes[1, 0].set_title('Agent Performance')

        # 4. Quantum-Vulnerable Detection vs Confidence
        if 'detected_quantum_vulnerable_count' in self.df.columns:
            axes[1, 1].scatter(self.df['detected_quantum_vulnerable_count'], self.df['confidence_score'], alpha=0.6)
            axes[1, 1].set_xlabel('Detected Quantum-Vulnerable Algorithms')
            axes[1, 1].set_ylabel('Confidence Score')
            axes[1, 1].set_title('Detection Count vs Confidence')

        plt.tight_layout()
        plt.savefig('benchmark_analysis.png', dpi=300, bbox_inches='tight')
        print("📊 시각화가 benchmark_analysis.png에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(description='벤치마크 결과 분석')
    parser.add_argument('results_file', help='분석할 결과 파일')
    parser.add_argument('--compare-models', action='store_true', help='모델별 성능 비교')
    parser.add_argument('--compare-agents', action='store_true', help='에이전트별 성능 비교')
    parser.add_argument('--quantum-vulnerable-analysis', action='store_true', help='양자 취약 알고리즘 탐지 분석')
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

    if args.all or args.quantum_vulnerable_analysis:
        analyzer.analyze_quantum_vulnerable_algorithms()

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