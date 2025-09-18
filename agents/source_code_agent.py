from typing import List
from .base_agent import BaseAnalysisAgent
import re

class SourceCodeAgent(BaseAnalysisAgent):
    def __init__(self, prompt_template: str = None):
        if prompt_template is None:
            prompt_template = "Analyze the following source code and provide insights about: {analysis_points}"

        super().__init__(
            name="Source Code Vulnerable Crypto Detection Agent",
            description="Analyzes source code to detect quantum-vulnerable cryptographic algorithms including Korean domestic algorithms",
            prompt_template=prompt_template
        )

    def get_analysis_points(self) -> List[str]:
        return [
            "quantum-vulnerable RSA implementations and usage patterns",
            "elliptic curve cryptography (ECC/ECDSA/ECDH) implementations",
            "discrete logarithm based algorithms (DSA, DH, ElGamal)",
            "Korean domestic algorithms (SEED, ARIA, HIGHT, LEA, KCDSA, EC-KCDSA, HAS-160, LSH)",
            "symmetric ciphers vulnerable to Grover's algorithm (AES-128, 3DES, DES, RC4)",
            "weak hash functions (MD5, SHA-1, SHA-256 with reduced security)",
            "vulnerable padding schemes (PKCS#1 v1.5, weak OAEP)",
            "insecure random number generators and key derivation functions",
            "obfuscated or indirect implementations of vulnerable algorithms",
            "hybrid systems mixing quantum-vulnerable and quantum-resistant algorithms",
            "legacy cryptographic libraries and deprecated cipher suites",
            "implementation-specific vulnerabilities in quantum-vulnerable algorithms"
        ]

    def validate_input(self, input_data: str) -> bool:
        if not input_data or not input_data.strip():
            return False

        # Basic code patterns
        code_indicators = [
            r'function\s+\w+\s*\(',
            r'class\s+\w+',
            r'def\s+\w+\s*\(',
            r'#include\s*<',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'public\s+class',
            r'private\s+\w+',
            r'if\s*\(',
            r'for\s*\(',
            r'while\s*\(',
            r'\{[\s\S]*\}',
            r'return\s+',
            r'console\.log\s*\(',
            r'printf\s*\(',
            r'print\s*\('
        ]

        # Quantum-vulnerable crypto patterns (for validation and detection hints)
        vulnerable_crypto_patterns = [
            # RSA patterns
            r'rsa|RSA_|rsa_key|RSA_KEY',
            r'modexp|mod_exp|modular.{0,10}exponentiation',
            r'prime.{0,10}generation|miller.{0,10}rabin',

            # ECC patterns
            r'ecc|ECC_|ecdsa|ECDSA|ecdh|ECDH',
            r'elliptic.{0,10}curve|secp\d+|prime\d+v\d+',
            r'point.{0,10}multiplication|scalar.{0,10}mult',

            # DH/DSA patterns
            r'diffie.{0,10}hellman|dh_|DH_|dsa|DSA_',
            r'discrete.{0,10}log|elgamal|ElGamal',

            # Korean algorithms
            r'seed|SEED|aria|ARIA|hight|HIGHT|lea|LEA',
            r'kcdsa|KCDSA|has.{0,5}160|HAS.{0,5}160',
            r'lsh.{0,5}256|LSH.{0,5}256',

            # Symmetric vulnerable
            r'des|DES|3des|3DES|rc4|RC4',
            r'md5|MD5|sha1|SHA1|sha.{0,5}256',

            # Implementation patterns
            r'openssl|OpenSSL|crypto\+\+|cryptopp',
            r'javax\.crypto|java\.security',
            r'Cipher\.getInstance|MessageDigest',
            r'RSAPublicKey|ECPublicKey|DHPublicKey',

            # Korean crypto libraries
            r'kcmvp|KCMVP|kisa|KISA|crypton|CRYPTON',
            r'korean.{0,10}crypto|domestic.{0,10}algorithm'
        ]

        # Check for basic code patterns first
        for pattern in code_indicators:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True

        # Also check for crypto-specific patterns
        for pattern in vulnerable_crypto_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True

        return False