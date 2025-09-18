from typing import List
from .base_agent import BaseAnalysisAgent
import re

class AssemblyBinaryAgent(BaseAnalysisAgent):
    def __init__(self, prompt_template: str = None):
        if prompt_template is None:
            prompt_template = "Analyze the following assembly/binary code and identify: {analysis_points}"

        super().__init__(
            name="Assembly Binary Vulnerable Crypto Detection Agent",
            description="Analyzes compiled assembly/binary code to detect quantum-vulnerable cryptographic operations including Korean algorithms",
            prompt_template=prompt_template
        )

    def get_analysis_points(self) -> List[str]:
        return [
            "RSA modular exponentiation and large integer arithmetic patterns",
            "elliptic curve point operations and scalar multiplication patterns",
            "discrete logarithm computation signatures (DSA, DH, ElGamal)",
            "Korean algorithm signatures (SEED S-boxes, ARIA transformations, HIGHT operations, LEA rotations)",
            "symmetric cipher patterns vulnerable to quantum attacks (DES, 3DES, RC4, AES-128)",
            "cryptographic hash function implementations (MD5, SHA-1, vulnerable SHA variants)",
            "big integer libraries and modular arithmetic operations",
            "cryptographic library calls and API signatures",
            "optimization patterns specific to vulnerable crypto algorithms",
            "Korean cryptographic library signatures and domestic algorithm implementations",
            "memory allocation patterns for cryptographic key storage",
            "side-channel vulnerable implementation patterns",
            "assembly-level obfuscation of vulnerable crypto operations"
        ]

    def validate_input(self, input_data: str) -> bool:
        if not input_data or not input_data.strip():
            return False

        # Standard assembly indicators
        assembly_indicators = [
            r'\b(mov|push|pop|call|ret|jmp|je|jne|cmp|add|sub|mul|div|imul|idiv)\b',
            r'\b(eax|ebx|ecx|edx|esp|ebp|esi|edi|rax|rbx|rcx|rdx|rsp|rbp|rsi|rdi)\b',
            r'\b(0x[0-9a-fA-F]+)\b',
            r'\.text\b|\.data\b|\.bss\b',
            r'\[.*\]',
            r';\s*.*$',
            r'^\s*[0-9a-fA-F]+:\s+',
            r'\b(DWORD|WORD|BYTE)\s+PTR\b',
            r'section\s+\.',
            r'global\s+\w+',
            r'extern\s+\w+'
        ]

        # Binary file indicators
        binary_indicators = [
            r'^[0-9a-fA-F\s]+$',
            r'\\x[0-9a-fA-F]{2}',
            r'ELF|PE32|Mach-O',
            r'\x7fELF|\x4d\x5a'
        ]

        # Quantum-vulnerable crypto assembly patterns
        vulnerable_crypto_assembly_patterns = [
            # RSA patterns
            r'imul\s+.*,\s*\d{4,}',  # Large integer multiplications
            r'call.*rsa|call.*RSA|call.*modexp',
            r'call.*bignum|call.*BIGNUM',
            r'div\s+.*\d{512,}|idiv\s+.*\d{512,}',  # Large divisions

            # ECC patterns
            r'call.*ecc|call.*ECC|call.*ecdsa|call.*ECDSA',
            r'call.*point_mul|call.*scalar_mult',
            r'call.*ec_|call.*EC_',

            # DH/DSA patterns
            r'call.*dh_|call.*DH_|call.*dsa|call.*DSA',
            r'call.*diffie|call.*hellman',

            # Korean algorithm patterns
            r'call.*seed|call.*SEED',
            r'call.*aria|call.*ARIA',
            r'call.*hight|call.*HIGHT',
            r'call.*lea_|call.*LEA_',
            r'call.*kcdsa|call.*KCDSA',
            r'call.*has160|call.*HAS160',

            # Symmetric crypto patterns
            r'call.*des|call.*DES|call.*3des|call.*3DES',
            r'call.*rc4|call.*RC4',
            r'call.*aes128|call.*AES128',

            # Hash function patterns
            r'call.*md5|call.*MD5|call.*sha1|call.*SHA1',
            r'call.*sha256|call.*SHA256',

            # Crypto library patterns
            r'call.*openssl|call.*OpenSSL',
            r'call.*crypto|call.*CRYPTO',
            r'call.*ssl_|call.*SSL_',

            # Korean crypto library patterns
            r'call.*kisa|call.*KISA|call.*kcmvp|call.*KCMVP',
            r'call.*crypton|call.*CRYPTON',

            # Mathematical operation patterns for crypto
            r'vpmadd|vpmul|vpand|vpxor',  # SIMD operations
            r'pclmulqdq',  # Polynomial multiplication (AES-related)
            r'rdrand|rdseed',  # Random number generation

            # Memory patterns for crypto
            r'movdqa.*xmm|movdqu.*ymm',  # Vector operations for crypto
            r'lea.*0x[0-9a-fA-F]{8,}',  # Large constant addresses
        ]

        all_indicators = assembly_indicators + binary_indicators + vulnerable_crypto_assembly_patterns

        for pattern in all_indicators:
            if re.search(pattern, input_data, re.IGNORECASE | re.MULTILINE):
                return True

        return False