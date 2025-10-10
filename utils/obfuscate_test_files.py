#!/usr/bin/env python3
"""
테스트 파일의 명시적인 암호화 힌트를 제거하는 스크립트
"""

import os
import re
import glob
from pathlib import Path

# 난독화 규칙
OBFUSCATION_RULES = {
    # 주석 패턴
    r'RSA[\s\-_]*(algorithm|crypto|cipher|key|encryption)?': 'AsymmetricAlgorithm',
    r'AES[\s\-_]*(algorithm|crypto|cipher|key|encryption)?': 'SymmetricCipher',
    r'DES[\s\-_]*(algorithm|crypto|cipher|key|encryption)?': 'LegacyBlockCipher',
    r'3DES[\s\-_]*': 'TripleBlockCipher',
    r'ECC[\s\-_]*(algorithm|crypto|cipher|key)?': 'EllipticOperation',
    r'ECDSA[\s\-_]*': 'CurveSignature',
    r'ECDH[\s\-_]*': 'CurveExchange',
    r'SHA-?1[\s\-_]*': 'DigestFunction160',
    r'SHA-?256[\s\-_]*': 'DigestFunction256',
    r'MD5[\s\-_]*': 'DigestFunction128',
    r'SEED[\s\-_]*(algorithm|crypto|cipher)?': 'KoreanBlockCipher',
    r'ARIA[\s\-_]*(algorithm|crypto|cipher)?': 'KoreanAdvancedCipher',
    r'HIGHT[\s\-_]*': 'LightweightCipher',
    r'LEA[\s\-_]*': 'FastBlockCipher',

    # 변수명/함수명 패턴 (주석이 아닌 경우만)
    r'\bpublicExponent\b': 'exponentE',
    r'\bprivateExponent\b': 'exponentD',
    r'\bprimeP\b': 'factorP',
    r'\bprimeQ\b': 'factorQ',
    r'\bmodulus\b(?!\s*\))': 'productN',  # modulus 함수 호출은 제외

    # 출력 메시지
    r'PublicKeyCrypto': 'AsymmetricProcessor',
    r'RSA key': 'asymmetric key',
    r'RSA-\d+': 'AsymAlg',

    # 특정 설명문
    r'Rivest.*Shamir.*Adleman': 'Public Key Algorithm',
    r'Data Encryption Standard': 'Block Cipher Standard',
    r'Advanced Encryption Standard': 'Modern Block Cipher',
    r'Elliptic Curve': 'Geometric Curve',
    r'Digital Signature Algorithm': 'Signature Method',
}

# 특별히 조심해야 할 상수들 (주석 추가로 난독화)
SENSITIVE_CONSTANTS = {
    '65537': 'common_exponent',  # RSA 공개지수
    '0x10001': 'common_exponent_hex',
}

def obfuscate_file(filepath: str, dry_run: bool = False):
    """파일의 명시적인 암호화 힌트를 난독화"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        modified = False

        # 패턴 기반 난독화
        for pattern, replacement in OBFUSCATION_RULES.items():
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if new_content != content:
                modified = True
                content = new_content

        # 상수 난독화 (주석으로 설명 제거)
        for constant, desc in SENSITIVE_CONSTANTS.items():
            # 65537 뒤의 주석 제거
            pattern = rf'{re.escape(constant)}\s*//[^\n]*'
            new_content = re.sub(pattern, constant, content)
            if new_content != content:
                modified = True
                content = new_content

        if modified:
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 난독화 완료: {os.path.basename(filepath)}")
            else:
                print(f"🔍 변경 예정: {os.path.basename(filepath)}")
                # 변경사항 미리보기
                diff_lines = []
                for i, (orig, new) in enumerate(zip(original_content.split('\n')[:10],
                                                     content.split('\n')[:10])):
                    if orig != new:
                        diff_lines.append(f"  Line {i+1}:")
                        diff_lines.append(f"    - {orig[:80]}")
                        diff_lines.append(f"    + {new[:80]}")
                if diff_lines:
                    print('\n'.join(diff_lines[:6]))
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ 오류 ({os.path.basename(filepath)}): {e}")
        return False

def scan_and_obfuscate(directory: str, pattern: str = "*.{java,py,c,cpp,rs,rb,go,js,scala,swift,s,asm}",
                       dry_run: bool = False):
    """디렉토리의 모든 테스트 파일을 난독화"""
    extensions = ['java', 'py', 'c', 'cpp', 'rs', 'rb', 'go', 'js', 'scala', 'swift', 's', 'asm']
    all_files = []

    for ext in extensions:
        all_files.extend(glob.glob(os.path.join(directory, f"*.{ext}")))

    print(f"\n{'=' * 60}")
    print(f"📁 디렉토리: {directory}")
    print(f"📄 발견된 파일: {len(all_files)}개")
    print(f"{'=' * 60}\n")

    if dry_run:
        print("🔍 DRY RUN 모드 - 실제로 수정하지 않습니다\n")

    modified_count = 0
    for filepath in sorted(all_files):
        if obfuscate_file(filepath, dry_run):
            modified_count += 1

    print(f"\n{'=' * 60}")
    if dry_run:
        print(f"🔍 {modified_count}개 파일이 변경될 예정입니다")
    else:
        print(f"✅ {modified_count}개 파일 난독화 완료")
    print(f"{'=' * 60}\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='테스트 파일 난독화 도구')
    parser.add_argument('--dir', default='data/test_files/source_code',
                       help='대상 디렉토리')
    parser.add_argument('--dry-run', action='store_true',
                       help='실제 수정 없이 미리보기만')
    parser.add_argument('--assembly', action='store_true',
                       help='assembly_binary 파일도 처리')

    args = parser.parse_args()

    # source_code 처리
    scan_and_obfuscate(args.dir, dry_run=args.dry_run)

    # assembly_binary 처리 (선택)
    if args.assembly:
        assembly_dir = args.dir.replace('source_code', 'assembly_binary')
        if os.path.exists(assembly_dir):
            scan_and_obfuscate(assembly_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
