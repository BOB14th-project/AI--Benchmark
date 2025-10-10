#!/usr/bin/env python3
"""
테스트 파일에 남아있는 명시적 힌트를 찾는 스크립트
"""

import os
import re
import glob
from collections import defaultdict

# 검사할 명시적 힌트 패턴
EXPLICIT_PATTERNS = {
    'algorithm_names': [
        r'\bRSA\b',
        r'\bAES\b',
        r'\bDES\b(?!_)',  # DES_ prefix는 제외
        r'\b3DES\b',
        r'\bECC\b',
        r'\bECDSA\b',
        r'\bECDH\b',
        r'\bDSA\b',
        r'\bMD5\b',
        r'\bSHA-?1\b',
        r'\bSHA-?256\b',
        r'\bSEED\b',
        r'\bARIA\b',
        r'\bHIGHT\b',
        r'\bLEA\b(?!_)',
    ],
    'rsa_notation': [
        r'\(e\)',  # RSA public exponent notation
        r'\(d\)',  # RSA private exponent notation
        r'\(n\)',  # RSA modulus notation
        r'\(p\)',  # RSA prime notation
        r'\(q\)',  # RSA prime notation
    ],
    'descriptive_comments': [
        r'Rivest.*Shamir.*Adleman',
        r'Data Encryption Standard',
        r'Advanced Encryption Standard',
        r'Elliptic Curve Cryptography',
        r'Digital Signature Algorithm',
        r'Message Digest',
    ]
}

def check_file(filepath: str) -> dict:
    """파일에서 명시적 힌트를 찾기"""
    findings = defaultdict(list)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # 주석 제외 (일부)
            code_part = line.split('//', 1)[0].split('#', 1)[0]

            for category, patterns in EXPLICIT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, code_part, re.IGNORECASE):
                        findings[category].append({
                            'line': line_num,
                            'pattern': pattern,
                            'text': line.strip()[:80]
                        })

        return findings

    except Exception as e:
        return {'error': [str(e)]}

def scan_directory(directory: str):
    """디렉토리의 모든 파일 검사"""
    extensions = ['java', 'py', 'c', 'cpp', 'rs', 'rb', 'go', 'js', 'scala', 'swift', 's', 'asm']
    all_files = []

    for ext in extensions:
        all_files.extend(glob.glob(os.path.join(directory, f"*.{ext}")))

    print(f"\n{'=' * 70}")
    print(f"📁 디렉토리: {directory}")
    print(f"📄 검사할 파일: {len(all_files)}개")
    print(f"{'=' * 70}\n")

    problem_files = []
    total_issues = 0

    for filepath in sorted(all_files):
        findings = check_file(filepath)

        if findings and 'error' not in findings:
            has_issue = any(len(v) > 0 for v in findings.values())
            if has_issue:
                problem_files.append((filepath, findings))
                issue_count = sum(len(v) for v in findings.values())
                total_issues += issue_count

    # 결과 출력
    if problem_files:
        print(f"⚠️  명시적 힌트가 발견된 파일: {len(problem_files)}개\n")

        for filepath, findings in problem_files:
            filename = os.path.basename(filepath)
            print(f"\n📄 {filename}")
            print(f"   경로: {filepath}")

            for category, items in findings.items():
                if items:
                    print(f"\n   🔍 {category}:")
                    for item in items[:3]:  # 처음 3개만 표시
                        print(f"      Line {item['line']}: {item['text']}")
                    if len(items) > 3:
                        print(f"      ... 외 {len(items) - 3}개 더")

        print(f"\n{'=' * 70}")
        print(f"⚠️  총 {total_issues}개의 명시적 힌트 발견")
        print(f"{'=' * 70}\n")
    else:
        print(f"✅ 명시적 힌트가 없습니다!")
        print(f"{'=' * 70}\n")

    return problem_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description='명시적 힌트 검사 도구')
    parser.add_argument('--dir', default='data/test_files/source_code',
                       help='대상 디렉토리')
    parser.add_argument('--assembly', action='store_true',
                       help='assembly_binary도 검사')

    args = parser.parse_args()

    # source_code 검사
    scan_directory(args.dir)

    # assembly_binary 검사
    if args.assembly:
        assembly_dir = args.dir.replace('source_code', 'assembly_binary')
        if os.path.exists(assembly_dir):
            scan_directory(assembly_dir)

if __name__ == "__main__":
    main()
