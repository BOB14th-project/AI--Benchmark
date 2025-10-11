#!/usr/bin/env python3
"""
Precision, Recall, F1 Score 정확도 분석 도구
거짓 양성(False Positive)과 거짓 음성(False Negative)을 명확히 구분하여 분석
"""

import json
import argparse
from typing import Dict, List, Any
from collections import defaultdict


class PrecisionRecallAnalyzer:
    """정밀도/재현율 분석기"""

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
    }

    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = None

    def load_results(self) -> bool:
        """결과 파일 로드"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            print(f"✅ 결과 파일 로드: {self.results_file}\n")
            return True
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            return False

    def normalize_algorithm_name(self, algorithm: str) -> str:
        """알고리즘 이름을 표준화"""
        algorithm_lower = algorithm.lower()

        for standard_name, variations in self.ALGORITHM_VARIATIONS.items():
            if any(var in algorithm_lower for var in variations):
                return standard_name.upper()

        return algorithm.upper()

    def extract_detected_algorithms(self, analysis_results: Dict[str, Any]) -> set:
        """분석 결과에서 탐지된 알고리즘 추출"""
        detected = set()
        analysis_text = json.dumps(analysis_results).lower()

        for standard_name, variations in self.ALGORITHM_VARIATIONS.items():
            for variation in variations:
                if variation in analysis_text:
                    detected.add(standard_name.upper())
                    break

        return detected

    def calculate_metrics_for_test(self, test_result: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """단일 테스트에 대한 정밀도/재현율 계산"""

        # 예상 알고리즘
        expected_algorithms = set()
        for algo in ground_truth.get('expected_findings', {}).get('vulnerable_algorithms_detected', []):
            normalized = self.normalize_algorithm_name(algo)
            expected_algorithms.add(normalized)

        # 한국 알고리즘 추가
        for algo in ground_truth.get('expected_findings', {}).get('korean_algorithms_detected', []):
            normalized = self.normalize_algorithm_name(algo)
            expected_algorithms.add(normalized)

        # 탐지된 알고리즘
        detected_algorithms = self.extract_detected_algorithms(
            test_result.get('analysis_results', {})
        )

        # TP, FP, FN 계산
        true_positives = expected_algorithms & detected_algorithms
        false_positives = detected_algorithms - expected_algorithms
        false_negatives = expected_algorithms - detected_algorithms

        tp_count = len(true_positives)
        fp_count = len(false_positives)
        fn_count = len(false_negatives)

        # Precision, Recall, F1 계산
        precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0.0
        recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            'expected_algorithms': sorted(list(expected_algorithms)),
            'detected_algorithms': sorted(list(detected_algorithms)),
            'true_positives': sorted(list(true_positives)),
            'false_positives': sorted(list(false_positives)),
            'false_negatives': sorted(list(false_negatives)),
            'tp_count': tp_count,
            'fp_count': fp_count,
            'fn_count': fn_count,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }

    def analyze_by_model(self) -> Dict[str, Any]:
        """모델별 Precision/Recall/F1 분석"""
        if not self.results:
            return {}

        model_metrics = defaultdict(lambda: {
            'tests': [],
            'total_tp': 0,
            'total_fp': 0,
            'total_fn': 0
        })

        # Ground truth 로드
        ground_truths = {}
        for test in self.results.get('detailed_results', []):
            test_id = test.get('test_id')
            if test_id and test_id not in ground_truths:
                gt_path = f"data/ground_truth/source_code/{test_id}.json"
                try:
                    with open(gt_path, 'r', encoding='utf-8') as f:
                        ground_truths[test_id] = json.load(f)
                except:
                    pass

        # 모델별 메트릭 계산
        for test in self.results.get('detailed_results', []):
            if not test.get('success'):
                continue

            model = test.get('model', 'unknown')
            test_id = test.get('test_id')

            if test_id not in ground_truths:
                continue

            metrics = self.calculate_metrics_for_test(test, ground_truths[test_id])

            model_metrics[model]['tests'].append(metrics)
            model_metrics[model]['total_tp'] += metrics['tp_count']
            model_metrics[model]['total_fp'] += metrics['fp_count']
            model_metrics[model]['total_fn'] += metrics['fn_count']

        # 평균 계산
        results = {}
        for model, data in model_metrics.items():
            tests = data['tests']
            if not tests:
                continue

            avg_precision = sum(t['precision'] for t in tests) / len(tests)
            avg_recall = sum(t['recall'] for t in tests) / len(tests)
            avg_f1 = sum(t['f1_score'] for t in tests) / len(tests)

            # Micro-averaged metrics (전체 TP, FP, FN 기준)
            total_tp = data['total_tp']
            total_fp = data['total_fp']
            total_fn = data['total_fn']

            micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
            micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
            micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

            results[model] = {
                'test_count': len(tests),
                'macro_avg': {
                    'precision': avg_precision,
                    'recall': avg_recall,
                    'f1_score': avg_f1
                },
                'micro_avg': {
                    'precision': micro_precision,
                    'recall': micro_recall,
                    'f1_score': micro_f1
                },
                'totals': {
                    'tp': total_tp,
                    'fp': total_fp,
                    'fn': total_fn
                },
                'detailed_tests': tests
            }

        return results

    def print_analysis(self):
        """분석 결과 출력"""
        model_metrics = self.analyze_by_model()

        if not model_metrics:
            print("❌ 분석할 데이터가 없습니다.")
            return

        print("=" * 100)
        print("📊 Precision, Recall, F1 Score 정밀 분석")
        print("=" * 100)
        print()

        # 모델별 결과를 F1 점수 기준으로 정렬
        sorted_models = sorted(
            model_metrics.items(),
            key=lambda x: x[1]['micro_avg']['f1_score'],
            reverse=True
        )

        for rank, (model, metrics) in enumerate(sorted_models, 1):
            print(f"{'🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '📊'} 모델: {model}")
            print(f"   테스트 수: {metrics['test_count']}개")
            print()

            # Macro-averaged (테스트별 평균)
            print(f"   📈 Macro-Averaged (테스트별 평균):")
            print(f"      Precision: {metrics['macro_avg']['precision']:.3f} (정밀도)")
            print(f"      Recall:    {metrics['macro_avg']['recall']:.3f} (재현율)")
            print(f"      F1 Score:  {metrics['macro_avg']['f1_score']:.3f}")
            print()

            # Micro-averaged (전체 TP/FP/FN 기준)
            print(f"   📊 Micro-Averaged (전체 알고리즘 기준):")
            print(f"      Precision: {metrics['micro_avg']['precision']:.3f}")
            print(f"      Recall:    {metrics['micro_avg']['recall']:.3f}")
            print(f"      F1 Score:  {metrics['micro_avg']['f1_score']:.3f}")
            print()

            # TP, FP, FN 통계
            print(f"   🔍 탐지 통계:")
            print(f"      ✅ True Positives:  {metrics['totals']['tp']}개 (정확히 탐지)")
            print(f"      ⚠️  False Positives: {metrics['totals']['fp']}개 (잘못 탐지)")
            print(f"      ❌ False Negatives: {metrics['totals']['fn']}개 (놓친 탐지)")
            print()

            # 상세 테스트별 결과
            print(f"   📋 테스트별 상세:")
            for i, test in enumerate(metrics['detailed_tests'], 1):
                print(f"      테스트 {i}:")
                print(f"         예상: {', '.join(test['expected_algorithms']) if test['expected_algorithms'] else '없음'}")
                print(f"         탐지: {', '.join(test['detected_algorithms']) if test['detected_algorithms'] else '없음'}")
                print(f"         ✅ TP: {', '.join(test['true_positives']) if test['true_positives'] else '없음'}")
                if test['false_positives']:
                    print(f"         ⚠️  FP: {', '.join(test['false_positives'])}")
                if test['false_negatives']:
                    print(f"         ❌ FN: {', '.join(test['false_negatives'])}")
                print(f"         F1: {test['f1_score']:.3f}")
                print()

            print("-" * 100)
            print()

        # 종합 순위 테이블
        print("=" * 100)
        print("🏆 모델 성능 순위 (F1 Score 기준)")
        print("=" * 100)
        print(f"{'순위':<6} {'모델':<25} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'TP':<8} {'FP':<8} {'FN':<8}")
        print("-" * 100)

        for rank, (model, metrics) in enumerate(sorted_models, 1):
            m = metrics['micro_avg']
            t = metrics['totals']
            medal = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '  '
            print(f"{medal} {rank:<3} {model:<25} {m['precision']:<12.3f} {m['recall']:<12.3f} {m['f1_score']:<12.3f} {t['tp']:<8} {t['fp']:<8} {t['fn']:<8}")

        print("=" * 100)


def main():
    parser = argparse.ArgumentParser(description='Precision, Recall, F1 Score 분석')
    parser.add_argument('--file', type=str, help='벤치마크 결과 JSON 파일')

    args = parser.parse_args()

    # 파일 지정
    results_file = args.file if args.file else 'benchmark_results_1760143167.json'

    # 분석 실행
    analyzer = PrecisionRecallAnalyzer(results_file)

    if analyzer.load_results():
        analyzer.print_analysis()


if __name__ == '__main__':
    main()
