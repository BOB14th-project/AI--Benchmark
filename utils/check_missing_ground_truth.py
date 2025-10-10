#!/usr/bin/env python3
"""
ground_truth 파일이 없는 테스트 파일들을 찾는 스크립트
"""

import os
import glob
from pathlib import Path

def check_missing_ground_truth(agent_type: str):
    """특정 에이전트 타입에서 누락된 ground_truth 파일 확인"""
    test_dir = f"data/test_files/{agent_type}"
    gt_dir = f"data/ground_truth/{agent_type}"

    # 테스트 파일 목록
    test_files = set()
    for ext in ['*.java', '*.py', '*.c', '*.cpp', '*.rs', '*.rb', '*.go', '*.js',
                '*.scala', '*.swift', '*.s', '*.asm', '*.conf', '*.yaml', '*.log', '*.ini']:
        for filepath in glob.glob(os.path.join(test_dir, ext)):
            filename = os.path.basename(filepath)
            # 확장자 제거
            base_name = os.path.splitext(filename)[0]
            test_files.add(base_name)

    # Ground truth 파일 목록
    gt_files = set()
    for filepath in glob.glob(os.path.join(gt_dir, "*.json")):
        filename = os.path.basename(filepath)
        # .json 제거
        base_name = os.path.splitext(filename)[0]
        gt_files.add(base_name)

    # 누락된 파일들
    missing = sorted(test_files - gt_files)
    extra = sorted(gt_files - test_files)

    return {
        'test_count': len(test_files),
        'gt_count': len(gt_files),
        'missing': missing,
        'extra': extra
    }

def main():
    agent_types = ['source_code', 'assembly_binary', 'logs_config']

    print(f"\n{'=' * 80}")
    print(f"Ground Truth 파일 누락 검사")
    print(f"{'=' * 80}\n")

    total_missing = 0
    total_extra = 0

    for agent_type in agent_types:
        result = check_missing_ground_truth(agent_type)

        print(f"\n📁 {agent_type.upper()}")
        print(f"   테스트 파일: {result['test_count']}개")
        print(f"   Ground Truth: {result['gt_count']}개")

        if result['missing']:
            print(f"\n   ⚠️  Ground Truth 누락: {len(result['missing'])}개")
            for filename in result['missing'][:10]:
                print(f"      - {filename}")
            if len(result['missing']) > 10:
                print(f"      ... 외 {len(result['missing']) - 10}개 더")
            total_missing += len(result['missing'])

        if result['extra']:
            print(f"\n   ⚠️  테스트 파일 없음: {len(result['extra'])}개")
            for filename in result['extra'][:5]:
                print(f"      - {filename}")
            if len(result['extra']) > 5:
                print(f"      ... 외 {len(result['extra']) - 5}개 더")
            total_extra += len(result['extra'])

        if not result['missing'] and not result['extra']:
            print(f"   ✅ 모든 파일 일치")

    print(f"\n{'=' * 80}")
    print(f"📊 전체 요약")
    print(f"{'=' * 80}")
    print(f"총 누락된 Ground Truth: {total_missing}개")
    print(f"총 불필요한 Ground Truth: {total_extra}개")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    main()
