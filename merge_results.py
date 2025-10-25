#!/usr/bin/env python3
"""
벤치마크 결과 병합 도구

여러 벤치마크 결과 파일을 하나로 병합하여 통합 분석을 가능하게 합니다.
이를 통해 기존 모델의 결과와 새로운 모델의 결과를 비교할 수 있습니다.

사용법:
    # 기본 사용 (모든 JSON 파일 자동 병합)
    python merge_results.py

    # 특정 파일들만 병합
    python merge_results.py --files result1.json result2.json result3.json

    # 출력 파일명 지정
    python merge_results.py --output merged_results.json

    # 중복 제거 옵션
    python merge_results.py --deduplicate
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class ResultMerger:
    """벤치마크 결과 병합 클래스"""

    def __init__(self, deduplicate: bool = False):
        self.deduplicate = deduplicate
        self.merged_results = {
            'metadata': {
                'merge_timestamp': datetime.now().isoformat(),
                'total_tests': 0,
                'total_successful': 0,
                'total_failed': 0,
                'source_files': [],
                'providers': set(),
                'models': set(),
                'agents': set()
            },
            'detailed_results': [],
            'summary': {}
        }

    def load_result_file(self, filepath: str) -> Dict[str, Any]:
        """단일 결과 파일 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"✅ 파일 로드: {filepath}")

            # 결과 파일 형식 통일
            if 'detailed_results' not in data and 'results' in data:
                data['detailed_results'] = data['results']

            if 'detailed_results' not in data:
                print(f"⚠️  경고: {filepath}에 'detailed_results' 또는 'results' 키가 없습니다.")
                return None

            return data

        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없음: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류 ({filepath}): {e}")
            return None
        except Exception as e:
            print(f"❌ 파일 로드 실패 ({filepath}): {e}")
            return None

    def merge_files(self, filepaths: List[str]) -> Dict[str, Any]:
        """여러 결과 파일을 병합"""
        print("\n" + "=" * 70)
        print("📂 벤치마크 결과 병합 시작")
        print("=" * 70)

        if not filepaths:
            print("❌ 병합할 파일이 없습니다.")
            return None

        # 중복 체크를 위한 해시 세트
        seen_tests = set() if self.deduplicate else None

        for filepath in filepaths:
            data = self.load_result_file(filepath)
            if not data:
                continue

            # 소스 파일 기록
            self.merged_results['metadata']['source_files'].append(filepath)

            # 상세 결과 병합
            detailed_results = data.get('detailed_results', [])

            for result in detailed_results:
                # 중복 제거 옵션이 활성화된 경우
                if self.deduplicate:
                    # 고유 식별자 생성 (provider + model + agent_type + test_id)
                    unique_id = (
                        result.get('provider', ''),
                        result.get('model', ''),
                        result.get('agent_type', ''),
                        result.get('test_id', '')
                    )

                    if unique_id in seen_tests:
                        print(f"   ⏭️  중복 건너뜀: {unique_id}")
                        continue

                    seen_tests.add(unique_id)

                # 결과 추가
                self.merged_results['detailed_results'].append(result)

                # 메타데이터 업데이트
                self.merged_results['metadata']['total_tests'] += 1

                if result.get('success', False):
                    self.merged_results['metadata']['total_successful'] += 1
                else:
                    self.merged_results['metadata']['total_failed'] += 1

                # Provider, Model, Agent 수집
                if 'provider' in result:
                    self.merged_results['metadata']['providers'].add(result['provider'])
                if 'model' in result:
                    self.merged_results['metadata']['models'].add(result['model'])
                if 'agent_type' in result:
                    self.merged_results['metadata']['agents'].add(result['agent_type'])

        # Set을 리스트로 변환 (JSON 직렬화를 위해)
        self.merged_results['metadata']['providers'] = sorted(list(self.merged_results['metadata']['providers']))
        self.merged_results['metadata']['models'] = sorted(list(self.merged_results['metadata']['models']))
        self.merged_results['metadata']['agents'] = sorted(list(self.merged_results['metadata']['agents']))

        # 요약 생성
        self._generate_summary()

        return self.merged_results

    def _generate_summary(self):
        """병합된 결과의 요약 생성"""
        detailed_results = self.merged_results['detailed_results']

        # Provider별 통계
        provider_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        # Model별 통계
        model_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        # Agent별 통계
        agent_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})

        for result in detailed_results:
            provider = result.get('provider', 'unknown')
            model = result.get('model', 'unknown')
            agent = result.get('agent_type', 'unknown')
            success = result.get('success', False)

            # Provider 통계
            provider_stats[provider]['total'] += 1
            if success:
                provider_stats[provider]['success'] += 1
            else:
                provider_stats[provider]['failed'] += 1

            # Model 통계
            model_key = f"{provider}/{model}"
            model_stats[model_key]['total'] += 1
            if success:
                model_stats[model_key]['success'] += 1
            else:
                model_stats[model_key]['failed'] += 1

            # Agent 통계
            agent_stats[agent]['total'] += 1
            if success:
                agent_stats[agent]['success'] += 1
            else:
                agent_stats[agent]['failed'] += 1

        # 성공률 계산
        for stats_dict in [provider_stats, model_stats, agent_stats]:
            for key in stats_dict:
                total = stats_dict[key]['total']
                success = stats_dict[key]['success']
                stats_dict[key]['success_rate'] = (success / total * 100) if total > 0 else 0

        self.merged_results['summary'] = {
            'by_provider': dict(provider_stats),
            'by_model': dict(model_stats),
            'by_agent': dict(agent_stats)
        }

    def save_merged_results(self, output_filepath: str):
        """병합된 결과를 파일로 저장"""
        output_path = Path(output_filepath)

        # 디렉토리 생성
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # JSON 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.merged_results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 병합된 결과 저장: {output_path}")

        # 병합 요약 출력
        self._print_merge_summary()

    def _print_merge_summary(self):
        """병합 요약 출력"""
        metadata = self.merged_results['metadata']
        summary = self.merged_results['summary']

        print("\n" + "=" * 70)
        print("📊 병합 요약")
        print("=" * 70)

        print(f"\n📁 소스 파일: {len(metadata['source_files'])}개")
        for f in metadata['source_files']:
            print(f"   - {f}")

        print(f"\n📈 전체 통계:")
        print(f"   총 테스트: {metadata['total_tests']}개")
        print(f"   성공: {metadata['total_successful']}개")
        print(f"   실패: {metadata['total_failed']}개")
        success_rate = (metadata['total_successful'] / metadata['total_tests'] * 100) if metadata['total_tests'] > 0 else 0
        print(f"   성공률: {success_rate:.1f}%")

        print(f"\n🤖 Provider: {len(metadata['providers'])}개")
        for provider in metadata['providers']:
            stats = summary['by_provider'].get(provider, {})
            print(f"   {provider}: {stats.get('total', 0)}개 테스트, {stats.get('success_rate', 0):.1f}% 성공률")

        print(f"\n🔬 Model: {len(metadata['models'])}개")
        for model_key in sorted(summary['by_model'].keys()):
            stats = summary['by_model'][model_key]
            print(f"   {model_key}: {stats['total']}개 테스트, {stats['success_rate']:.1f}% 성공률")

        print(f"\n🎯 Agent: {len(metadata['agents'])}개")
        for agent in metadata['agents']:
            stats = summary['by_agent'].get(agent, {})
            print(f"   {agent}: {stats.get('total', 0)}개 테스트, {stats.get('success_rate', 0):.1f}% 성공률")


def auto_find_result_files(directory: str = ".") -> List[str]:
    """현재 디렉토리에서 결과 파일 자동 검색"""
    result_files = []

    # benchmark_results_*.json 패턴 검색
    for json_file in Path(directory).glob("benchmark_results_*.json"):
        result_files.append(str(json_file))

    # results 디렉토리 검색
    results_dir = Path(directory) / "results"
    if results_dir.exists():
        for json_file in results_dir.glob("*.json"):
            result_files.append(str(json_file))

    return sorted(result_files)


def main():
    parser = argparse.ArgumentParser(
        description="벤치마크 결과 병합 도구 - 여러 결과 파일을 하나로 통합"
    )
    parser.add_argument(
        '--files', '-f',
        nargs='+',
        help="병합할 JSON 파일 목록"
    )
    parser.add_argument(
        '--output', '-o',
        default='merged_benchmark_results.json',
        help="출력 파일명 (기본값: merged_benchmark_results.json)"
    )
    parser.add_argument(
        '--deduplicate', '-d',
        action='store_true',
        help="중복된 테스트 결과 제거"
    )
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help="현재 디렉토리의 모든 결과 파일 자동 검색 및 병합"
    )

    args = parser.parse_args()

    # 파일 목록 결정
    if args.auto or not args.files:
        print("🔍 결과 파일 자동 검색 중...")
        files_to_merge = auto_find_result_files()

        if not files_to_merge:
            print("❌ 병합할 결과 파일을 찾을 수 없습니다.")
            print("\n다음 위치에서 검색했습니다:")
            print("  - ./benchmark_results_*.json")
            print("  - ./results/*.json")
            print("\n수동으로 파일을 지정하려면:")
            print("  python merge_results.py --files file1.json file2.json")
            sys.exit(1)

        print(f"✅ {len(files_to_merge)}개 파일 발견:")
        for f in files_to_merge:
            print(f"   - {f}")

        response = input("\n이 파일들을 병합하시겠습니까? (Y/n): ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("⏭️  병합 취소")
            sys.exit(0)
    else:
        files_to_merge = args.files

    # 병합 실행
    merger = ResultMerger(deduplicate=args.deduplicate)
    merged_data = merger.merge_files(files_to_merge)

    if not merged_data:
        print("❌ 병합할 데이터가 없습니다.")
        sys.exit(1)

    # 결과 저장
    merger.save_merged_results(args.output)

    print("\n✅ 병합 완료!")
    print(f"\n다음 명령어로 통합 분석을 실행하세요:")
    print(f"  python analyze_and_visualize.py {args.output}")


if __name__ == "__main__":
    main()
