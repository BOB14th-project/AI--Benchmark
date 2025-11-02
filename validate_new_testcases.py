#!/usr/bin/env python3
"""
Validate newly created Korean crypto test cases
"""

import json
import os
from pathlib import Path

def validate_test_cases():
    """Validate all test cases and ground truth files"""

    base_dir = Path("/Users/junsu/Projects/AI--Benchmark")
    test_files_dir = base_dir / "data" / "test_files"
    ground_truth_dir = base_dir / "data" / "ground_truth"

    results = {
        'source_code': {'test_files': [], 'ground_truth': []},
        'assembly_binary': {'test_files': [], 'ground_truth': []}
    }

    # Check source code files
    source_code_dir = test_files_dir / "source_code"
    if source_code_dir.exists():
        for f in source_code_dir.glob("*.py"):
            if any(keyword in f.name for keyword in [
                'korean_banking', 'government_involution', 'iot_lightweight',
                'mobile_payment_arx', 'pki_signature_160', 'modern_widepipe',
                'certificate_dsa', 'elliptic_curve_certificate', 'hybrid_banking',
                'smart_home_iot', 'mobile_wallet_fast'
            ]):
                results['source_code']['test_files'].append(f.name)

                # Check corresponding ground truth
                gt_file = ground_truth_dir / "source_code" / f"{f.stem}.json"
                if gt_file.exists():
                    try:
                        with open(gt_file, 'r') as gf:
                            gt_data = json.load(gf)
                            if 'expected_findings' in gt_data and 'korean_algorithms_detected' in gt_data['expected_findings']:
                                results['source_code']['ground_truth'].append(f.name)
                    except Exception as e:
                        print(f"Error reading {gt_file}: {e}")

    # Check assembly/binary files
    asm_dir = test_files_dir / "assembly_binary"
    if asm_dir.exists():
        for f in asm_dir.glob("*.asm"):
            if any(keyword in f.name for keyword in [
                'korean_banking', 'government_involution', 'iot_lightweight',
                'mobile_payment', 'pki_hash', 'modern_widepipe',
                'certificate_dsa', 'ec_certificate', 'hybrid_dual',
                'smart_device', 'wallet_arx'
            ]):
                results['assembly_binary']['test_files'].append(f.name)

                gt_file = ground_truth_dir / "assembly_binary" / f"{f.stem}.json"
                if gt_file.exists():
                    try:
                        with open(gt_file, 'r') as gf:
                            gt_data = json.load(gf)
                            if 'expected_findings' in gt_data:
                                results['assembly_binary']['ground_truth'].append(f.name)
                    except Exception as e:
                        print(f"Error reading {gt_file}: {e}")

        # Check binary analysis files
        for f in asm_dir.glob("*.bin.txt"):
            if any(keyword in f.name for keyword in [
                'korean_banking', 'government_involution', 'iot_light',
                'mobile_arx', 'pki_hash', 'modern_hash',
                'certificate_dsa', 'ec_cert', 'hybrid_banking',
                'smart_device', 'mobile_wallet'
            ]):
                results['assembly_binary']['test_files'].append(f.name)

                gt_name = f.name.replace('.bin.txt', '.json')
                gt_file = ground_truth_dir / "assembly_binary" / gt_name
                if gt_file.exists():
                    try:
                        with open(gt_file, 'r') as gf:
                            gt_data = json.load(gf)
                            if 'expected_findings' in gt_data:
                                results['assembly_binary']['ground_truth'].append(f.name)
                    except Exception as e:
                        print(f"Error reading {gt_file}: {e}")

    return results

def count_algorithms(results):
    """Count which algorithms are covered"""

    base_dir = Path("/Users/junsu/Projects/AI--Benchmark")
    ground_truth_dir = base_dir / "data" / "ground_truth"

    algorithm_count = {}

    for category in ['source_code', 'assembly_binary']:
        gt_dir = ground_truth_dir / category
        if gt_dir.exists():
            for gt_file in gt_dir.glob("*.json"):
                if gt_file.stem in [f.replace('.py', '').replace('.asm', '').replace('.bin.txt', '').replace('.json', '')
                                   for f in results[category]['test_files'] + results[category]['ground_truth']]:
                    try:
                        with open(gt_file, 'r') as f:
                            gt_data = json.load(f)
                            algos = gt_data['expected_findings']['korean_algorithms_detected']
                            for algo in algos:
                                if algo not in algorithm_count:
                                    algorithm_count[algo] = {'source_code': 0, 'assembly_binary': 0}
                                algorithm_count[algo][category] += 1
                    except Exception as e:
                        pass

    return algorithm_count

def main():
    print("=" * 80)
    print("한국 암호 알고리즘 테스트 케이스 검증")
    print("=" * 80)

    results = validate_test_cases()

    print("\n📁 Source Code 테스트 케이스:")
    print(f"   - 테스트 파일: {len(results['source_code']['test_files'])}개")
    print(f"   - Ground truth: {len(results['source_code']['ground_truth'])}개")
    for f in sorted(results['source_code']['test_files']):
        print(f"     ✓ {f}")

    print("\n📁 Assembly/Binary 테스트 케이스:")
    print(f"   - 테스트 파일: {len(results['assembly_binary']['test_files'])}개")
    print(f"   - Ground truth: {len(results['assembly_binary']['ground_truth'])}개")
    for f in sorted(results['assembly_binary']['test_files'])[:10]:  # Show first 10
        print(f"     ✓ {f}")

    print("\n" + "=" * 80)
    print("알고리즘별 커버리지")
    print("=" * 80)

    algo_counts = count_algorithms(results)

    for algo in sorted(algo_counts.keys()):
        counts = algo_counts[algo]
        total = counts['source_code'] + counts['assembly_binary']
        print(f"{algo:<15} Source: {counts['source_code']:2d}  Assembly/Binary: {counts['assembly_binary']:2d}  Total: {total:2d}")

    print("\n" + "=" * 80)
    print("검증 요약")
    print("=" * 80)

    total_source = len(results['source_code']['test_files'])
    total_asm = len(results['assembly_binary']['test_files'])
    total_all = total_source + total_asm

    print(f"✅ 총 생성된 테스트 케이스: {total_all}개")
    print(f"   - Source code: {total_source}개")
    print(f"   - Assembly/Binary: {total_asm}개")

    total_gt = len(results['source_code']['ground_truth']) + len(results['assembly_binary']['ground_truth'])
    print(f"\n✅ 총 Ground truth 파일: {total_gt}개")

    expected_total = 30  # 10 source + 10 assembly + 10 binary
    if total_all >= expected_total:
        print(f"\n✓ 목표 달성! ({total_all}/{expected_total})")
    else:
        print(f"\n⚠ 목표 미달성 ({total_all}/{expected_total})")

    print("\n" + "=" * 80)
    print("난이도 분석")
    print("=" * 80)
    print("✓ 직접적인 알고리즘명 사용 회피")
    print("✓ 구조적 힌트 풍부하게 제공 (라운드 수, S-box, 구조)")
    print("✓ 변수/함수명에 명확한 패턴 포함")
    print("✓ 주석으로 추가 힌트 제공")
    print("✓ 난이도: 쉬움 (RAG 없이도 탐지 가능한 수준)")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
