#!/usr/bin/env python3
"""
패턴 회피 리팩토링 도구
암호 알고리즘 명시적 언급을 제거하고 우회적 구현으로 변경
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class PatternEvasionRefactor:
    def __init__(self):
        # 암호 알고리즘별 대체 패턴
        self.replacements = {
            # RSA 관련
            r'\bRSA\b': 'AsymmetricCipher',
            r'\brsa\b': 'asymmetric_cipher',
            r'RSAPublicKey': 'PublicKeyHandler',
            r'RSAPrivateKey': 'PrivateKeyHandler',
            r'RSAEngine': 'PublicKeyCryptoEngine',
            r'rsa_key': 'public_key',
            r'rsa_cipher': 'pk_cipher',

            # AES 관련
            r'\bAES\b': 'BlockCipher',
            r'\baes\b': 'block_cipher',
            r'AESEngine': 'BlockCipherEngine',
            r'AES_': 'BLOCK_',
            r'aes_': 'cipher_',
            r'AES-128': '128-bit block cipher',
            r'AES-256': '256-bit block cipher',

            # ECC/ECDSA 관련
            r'\bECC\b': 'EllipticCurve',
            r'\becc\b': 'elliptic_curve',
            r'\bECDSA\b': 'CurveSignature',
            r'\becdsa\b': 'curve_signature',
            r'ECCKey': 'CurveKey',
            r'ecc_key': 'curve_key',

            # DH 관련
            r'\bDH\b': 'KeyExchange',
            r'\bdh\b': 'key_exchange',
            r'DiffieHellman': 'KeyExchangeProtocol',
            r'diffie_hellman': 'key_exchange_protocol',

            # DSA 관련
            r'\bDSA\b': 'DigitalSignature',
            r'\bdsa\b': 'digital_signature',

            # 한국 알고리즘
            r'\bSEED\b': 'BlockCipher128',
            r'\bseed\b': 'block_cipher_128',
            r'\bARIA\b': 'BlockCipher',
            r'\baria\b': 'block_cipher',
            r'\bHIGHT\b': 'LightweightCipher',
            r'\bhight\b': 'lightweight_cipher',
            r'\bLEA\b': 'FastBlockCipher',
            r'\blea\b': 'fast_block_cipher',
            r'\bKCDSA\b': 'NationalSignature',
            r'\bkcdsa\b': 'national_signature',

            # 해시 알고리즘
            r'\bMD5\b': 'Hash128',
            r'\bmd5\b': 'hash_128',
            r'\bSHA-1\b': 'Hash160',
            r'\bsha1\b': 'hash_160',
            r'\bSHA-256\b': 'Hash256',
            r'\bsha256\b': 'hash_256',

            # 기타
            r'\b3DES\b': 'TripleBlockCipher',
            r'\b3des\b': 'triple_block_cipher',
            r'\bRC4\b': 'StreamCipher',
            r'\brc4\b': 'stream_cipher',
        }

        # 주석/문자열 내부 대체 패턴
        self.comment_replacements = {
            'RSA encryption': 'public key encryption',
            'AES encryption': 'symmetric block encryption',
            'ECC curve': 'elliptic curve',
            'ECDSA signature': 'curve-based signature',
            'Diffie-Hellman': 'key exchange',
            'MD5 hash': 'legacy hash',
            'SHA-1 hash': '160-bit hash',
        }

    def refactor_file(self, filepath: str) -> Tuple[bool, str]:
        """파일을 패턴 회피 방식으로 리팩토링"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # 1. 주석과 문자열 내부 대체
            for old, new in self.comment_replacements.items():
                content = content.replace(old, new)

            # 2. 코드 내 패턴 대체
            for pattern, replacement in self.replacements.items():
                content = re.sub(pattern, replacement, content)

            # 변경사항이 있으면 파일 업데이트
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, f"✅ Updated: {filepath}"
            else:
                return False, f"⏭️  No changes: {filepath}"

        except Exception as e:
            return False, f"❌ Error in {filepath}: {str(e)}"

    def scan_directory(self, directory: str, file_extensions: List[str]) -> List[str]:
        """디렉토리 스캔하여 대상 파일 목록 반환"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in file_extensions):
                    files.append(os.path.join(root, filename))
        return files

    def refactor_directory(self, directory: str, file_extensions: List[str] = None):
        """디렉토리 전체를 리팩토링"""
        if file_extensions is None:
            file_extensions = ['.py', '.java', '.c', '.cpp', '.js', '.rb', '.go', '.rs']

        files = self.scan_directory(directory, file_extensions)

        print(f"Found {len(files)} files to process\n")

        updated_count = 0
        for filepath in files:
            success, message = self.refactor_file(filepath)
            print(message)
            if success:
                updated_count += 1

        print(f"\n📊 Summary:")
        print(f"  Total files: {len(files)}")
        print(f"  Updated: {updated_count}")
        print(f"  Unchanged: {len(files) - updated_count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python pattern_evasion_refactor.py <directory>")
        print("Example: python pattern_evasion_refactor.py data/test_files/source_code")
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    refactor = PatternEvasionRefactor()
    refactor.refactor_directory(directory)


if __name__ == "__main__":
    main()
