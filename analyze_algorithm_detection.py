#!/usr/bin/env python3
"""
모델별/전체 암호화 알고리즘 탐지 성공/실패 분석 도구
"""

import json
import os
import glob
from collections import defaultdict
from typing import Dict, List, Any
import argparse


class AlgorithmDetectionAnalyzer:
    def __init__(self, results_file: str = None):
        self.results_file = results_file
        self.results_data = None
        self.ground_truth_cache = {}

    def load_results(self):
        """벤치마크 결과 파일 로드"""
        if not self.results_file:
            # 최신 결과 파일 찾기
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

    def load_ground_truth(self, file_name: str, agent_type: str) -> Dict[str, Any]:
        """Ground truth 파일 로드 (캐싱)"""
        cache_key = f"{agent_type}/{file_name}"
        if cache_key in self.ground_truth_cache:
            return self.ground_truth_cache[cache_key]

        # 파일명에서 확장자 제거
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

    def extract_expected_algorithms(self, ground_truth: Dict[str, Any]) -> List[str]:
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

    def extract_detected_algorithms(self, actual_response: Dict[str, Any]) -> List[str]:
        """실제 응답에서 탐지된 알고리즘 추출"""
        detected = []

        if not actual_response.get('valid_json'):
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

        # analysis_results 값에서 DETECTED 패턴 찾기
        import re
        for key, value in analysis.items():
            if isinstance(value, str) and 'DETECTED:' in value.upper():
                # "DETECTED: RSA (Evidence...)" 형식에서 알고리즘 추출
                matches = re.findall(r'DETECTED:\s*([A-Z0-9\-/]+)', value.upper())
                detected.extend(matches)

        return list(set(detected))  # 중복 제거

    def normalize_algorithm_name(self, name: str) -> str:
        """알고리즘 이름 정규화"""
        name = name.upper().strip()

        # 변형 통일
        mappings = {
            'TRIPLE DES': '3DES',
            'TRIPLE-DES': '3DES',
            'TDES': '3DES',
            'TRIPLEDES': '3DES',
            'EC-KCDSA': 'KCDSA',
            'ECKCDSA': 'KCDSA',
            'DIFFIE-HELLMAN': 'DH',
            'DIFFIE HELLMAN': 'DH',
            'SHA1': 'SHA-1',
            'SHA256': 'SHA-256',
            'SHA512': 'SHA-512',
        }

        for pattern, replacement in mappings.items():
            if pattern in name:
                return replacement

        return name

    def check_algorithm_match(self, expected: str, detected_list: List[str]) -> bool:
        """알고리즘이 탐지되었는지 확인 (유연한 매칭)"""
        expected_norm = self.normalize_algorithm_name(expected)
        detected_norm = [self.normalize_algorithm_name(d) for d in detected_list]

        # 정확한 매치
        if expected_norm in detected_norm:
            return True

        # 부분 매치 (예: RSA-2048 -> RSA)
        for detected in detected_norm:
            if expected_norm in detected or detected in expected_norm:
                return True

        return False

    def analyze_by_model(self) -> Dict[str, Any]:
        """모델별 알고리즘 탐지 분석"""
        model_stats = defaultdict(lambda: {
            'total_tests': 0,
            'algorithm_stats': defaultdict(lambda: {'expected': 0, 'detected': 0, 'missed': 0}),
            'total_expected': 0,
            'total_detected': 0,
            'total_missed': 0
        })

        for result in self.results_data.get('results', []):
            # 필드명 매핑: model 또는 model_name
            model_name = result.get('model', result.get('model_name', 'unknown'))
            # 파일 경로에서 파일명 추출
            file_path = result.get('file_path', result.get('file_name', ''))
            file_name = os.path.basename(file_path) if file_path else ''
            agent_type = result.get('agent_type', '')

            # Ground truth 로드
            gt = self.load_ground_truth(file_name, agent_type)
            if not gt:
                continue

            expected_algos = self.extract_expected_algorithms(gt)
            if not expected_algos:
                continue

            detected_algos = self.extract_detected_algorithms(result)

            stats = model_stats[model_name]
            stats['total_tests'] += 1

            # 각 알고리즘별 통계
            for expected in expected_algos:
                expected_norm = self.normalize_algorithm_name(expected)
                stats['algorithm_stats'][expected_norm]['expected'] += 1
                stats['total_expected'] += 1

                if self.check_algorithm_match(expected, detected_algos):
                    stats['algorithm_stats'][expected_norm]['detected'] += 1
                    stats['total_detected'] += 1
                else:
                    stats['algorithm_stats'][expected_norm]['missed'] += 1
                    stats['total_missed'] += 1

        return dict(model_stats)

    def analyze_overall(self) -> Dict[str, Any]:
        """전체 알고리즘 탐지 분석 (모델 구분 없이)"""
        overall_stats = {
            'total_tests': 0,
            'algorithm_stats': defaultdict(lambda: {'expected': 0, 'detected': 0, 'missed': 0}),
            'total_expected': 0,
            'total_detected': 0,
            'total_missed': 0
        }

        for result in self.results_data.get('results', []):
            # 파일 경로에서 파일명 추출
            file_path = result.get('file_path', result.get('file_name', ''))
            file_name = os.path.basename(file_path) if file_path else ''
            agent_type = result.get('agent_type', '')

            # Ground truth 로드
            gt = self.load_ground_truth(file_name, agent_type)
            if not gt:
                continue

            expected_algos = self.extract_expected_algorithms(gt)
            if not expected_algos:
                continue

            detected_algos = self.extract_detected_algorithms(result)

            overall_stats['total_tests'] += 1

            # 각 알고리즘별 통계
            for expected in expected_algos:
                expected_norm = self.normalize_algorithm_name(expected)
                overall_stats['algorithm_stats'][expected_norm]['expected'] += 1
                overall_stats['total_expected'] += 1

                if self.check_algorithm_match(expected, detected_algos):
                    overall_stats['algorithm_stats'][expected_norm]['detected'] += 1
                    overall_stats['total_detected'] += 1
                else:
                    overall_stats['algorithm_stats'][expected_norm]['missed'] += 1
                    overall_stats['total_missed'] += 1

        return overall_stats

    def print_model_analysis(self, model_stats: Dict[str, Any]):
        """모델별 분석 결과 출력"""
        print("=" * 100)
        print("📊 모델별 알고리즘 탐지 분석")
        print("=" * 100)

        for model_name, stats in sorted(model_stats.items()):
            print(f"\n🤖 모델: {model_name}")
            print(f"   총 테스트: {stats['total_tests']}개")
            print(f"   총 예상 알고리즘: {stats['total_expected']}개")
            print(f"   총 탐지 성공: {stats['total_detected']}개 ({stats['total_detected']/stats['total_expected']*100:.1f}%)")
            print(f"   총 탐지 실패: {stats['total_missed']}개 ({stats['total_missed']/stats['total_expected']*100:.1f}%)")

            print(f"\n   📈 알고리즘별 탐지율:")

            # 탐지율 순으로 정렬
            algo_list = []
            for algo, algo_stats in stats['algorithm_stats'].items():
                detection_rate = algo_stats['detected'] / algo_stats['expected'] * 100 if algo_stats['expected'] > 0 else 0
                algo_list.append((algo, algo_stats, detection_rate))

            algo_list.sort(key=lambda x: x[2], reverse=True)

            for algo, algo_stats, detection_rate in algo_list:
                status = "✅" if detection_rate >= 80 else "⚠️" if detection_rate >= 50 else "❌"
                print(f"      {status} {algo:15s}: {algo_stats['detected']:3d}/{algo_stats['expected']:3d} ({detection_rate:5.1f}%)")

    def print_overall_analysis(self, overall_stats: Dict[str, Any]):
        """전체 분석 결과 출력"""
        print("=" * 100)
        print("📊 전체 알고리즘 탐지 분석 (모든 모델 통합)")
        print("=" * 100)

        print(f"\n총 테스트: {overall_stats['total_tests']}개")
        print(f"총 예상 알고리즘: {overall_stats['total_expected']}개")
        print(f"총 탐지 성공: {overall_stats['total_detected']}개 ({overall_stats['total_detected']/overall_stats['total_expected']*100:.1f}%)")
        print(f"총 탐지 실패: {overall_stats['total_missed']}개 ({overall_stats['total_missed']/overall_stats['total_expected']*100:.1f}%)")

        print(f"\n📈 알고리즘별 탐지율:")

        # 탐지율 순으로 정렬
        algo_list = []
        for algo, algo_stats in overall_stats['algorithm_stats'].items():
            detection_rate = algo_stats['detected'] / algo_stats['expected'] * 100 if algo_stats['expected'] > 0 else 0
            algo_list.append((algo, algo_stats, detection_rate))

        algo_list.sort(key=lambda x: x[2], reverse=True)

        for algo, algo_stats, detection_rate in algo_list:
            status = "✅" if detection_rate >= 80 else "⚠️" if detection_rate >= 50 else "❌"
            print(f"   {status} {algo:15s}: {algo_stats['detected']:4d}/{algo_stats['expected']:4d} ({detection_rate:5.1f}%)")

        print("\n" + "=" * 100)


def main():
    parser = argparse.ArgumentParser(description='알고리즘 탐지 성공/실패 분석 도구')
    parser.add_argument('--file', '-f', help='벤치마크 결과 JSON 파일 (기본: 최신 파일)')
    parser.add_argument('--by-model', '-m', action='store_true', help='모델별 분석')
    parser.add_argument('--overall', '-o', action='store_true', help='전체 통합 분석')

    args = parser.parse_args()

    # 기본값: 둘 다 출력
    if not args.by_model and not args.overall:
        args.by_model = True
        args.overall = True

    analyzer = AlgorithmDetectionAnalyzer(args.file)

    if not analyzer.load_results():
        return

    if args.by_model:
        model_stats = analyzer.analyze_by_model()
        analyzer.print_model_analysis(model_stats)
        print()

    if args.overall:
        overall_stats = analyzer.analyze_overall()
        analyzer.print_overall_analysis(overall_stats)


if __name__ == "__main__":
    main()
