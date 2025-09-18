from typing import List
from .base_agent import BaseAnalysisAgent
import re
import json

class DynamicAnalysisAgent(BaseAnalysisAgent):
    def __init__(self, prompt_template: str = None):
        if prompt_template is None:
            prompt_template = "Analyze the following dynamic analysis parameters and extract: {analysis_points}"

        super().__init__(
            name="Dynamic Analysis Vulnerable Crypto Detection Agent",
            description="Analyzes runtime behavior to identify quantum-vulnerable cryptography usage including Korean algorithms",
            prompt_template=prompt_template
        )

    def get_analysis_points(self) -> List[str]:
        return [
            "RSA key generation and modular exponentiation API calls and performance signatures",
            "elliptic curve cryptography operations and point multiplication behaviors",
            "discrete logarithm algorithm usage patterns (DSA, DH, ElGamal)",
            "Korean algorithm runtime signatures (SEED, ARIA, HIGHT, LEA, KCDSA operations)",
            "symmetric cipher usage vulnerable to quantum attacks (DES, 3DES, RC4, AES-128)",
            "cryptographic hash function calls and timing patterns (MD5, SHA-1, SHA-256)",
            "vulnerable random number generation and entropy collection patterns",
            "cryptographic library loading and initialization behaviors",
            "memory allocation patterns for large cryptographic keys and operations",
            "network protocol usage with quantum-vulnerable cipher suites",
            "certificate validation and PKI operations with vulnerable algorithms",
            "performance characteristics indicating quantum-vulnerable crypto computations",
            "Korean cryptographic library usage and domestic algorithm API calls",
            "side-channel information leakage in vulnerable crypto implementations"
        ]

    def validate_input(self, input_data: str) -> bool:
        if not input_data or not input_data.strip():
            return False

        # Try to parse as JSON first
        try:
            json.loads(input_data)
            return True
        except json.JSONDecodeError:
            pass

        # Standard dynamic analysis indicators
        dynamic_indicators = [
            r'"pid":\s*\d+',
            r'"timestamp":\s*["\d]',
            r'"memory_usage":\s*\d+',
            r'"cpu_usage":\s*[\d.]+',
            r'"network_connections":\s*\[',
            r'"file_operations":\s*\[',
            r'"api_calls":\s*\[',
            r'"syscalls":\s*\[',
            r'"process_tree":\s*\{',
            r'"performance_counters":\s*\{',
            r'CreateFile|ReadFile|WriteFile',
            r'VirtualAlloc|HeapAlloc',
            r'connect|send|recv|socket',
            r'CreateProcess|ExitProcess',
            r'RegOpenKey|RegSetValue|RegQueryValue',
            r'malloc\(\)|free\(\)',
            r'open\(\)|read\(\)|write\(\)',
            r'execution_time:\s*[\d.]+',
            r'memory_peak:\s*\d+',
            r'thread_count:\s*\d+'
        ]

        # Quantum-vulnerable crypto dynamic patterns
        vulnerable_crypto_dynamic_patterns = [
            # RSA patterns
            r'"library":\s*".*(?:rsa|RSA|openssl|OpenSSL).*"',
            r'"api_call":\s*".*(?:RSA_|rsa_|modexp|BIGNUM).*"',
            r'"function":\s*".*(?:RSA_generate_key|RSA_public_encrypt|RSA_sign).*"',

            # ECC patterns
            r'"library":\s*".*(?:ecc|ECC|ecdsa|ECDSA).*"',
            r'"api_call":\s*".*(?:EC_|ECDSA_|ECDH_|point_mul).*"',
            r'"curve":\s*".*(?:secp|prime|sect).*"',

            # DH/DSA patterns
            r'"library":\s*".*(?:dh|DH|dsa|DSA).*"',
            r'"api_call":\s*".*(?:DH_|DSA_|diffie|hellman).*"',

            # Korean algorithm patterns
            r'"algorithm":\s*".*(?:seed|SEED|aria|ARIA|hight|HIGHT|lea|LEA).*"',
            r'"library":\s*".*(?:kisa|KISA|kcmvp|KCMVP|crypton|CRYPTON).*"',
            r'"api_call":\s*".*(?:SEED_|ARIA_|HIGHT_|LEA_|KCDSA_|HAS160).*"',

            # Symmetric vulnerable patterns
            r'"cipher":\s*".*(?:des|DES|3des|3DES|rc4|RC4).*"',
            r'"algorithm":\s*".*(?:aes.{0,5}128|AES.{0,5}128).*"',

            # Hash function patterns
            r'"hash":\s*".*(?:md5|MD5|sha1|SHA1|sha.{0,5}256).*"',
            r'"api_call":\s*".*(?:MD5_|SHA1_|SHA256_).*"',

            # Large key sizes indicating vulnerable crypto
            r'"key_size":\s*(?:1024|2048|3072|4096|512)',  # RSA/DH key sizes
            r'"modulus_size":\s*(?:1024|2048|3072|4096)',

            # Performance patterns
            r'"crypto_operation":\s*"(?:modular_exponentiation|point_multiplication|discrete_log).*"',
            r'"timing":\s*{.*"rsa|ecdsa|dsa|korean_algo"',

            # TLS/SSL patterns with vulnerable ciphers
            r'"tls_cipher":\s*".*(?:RSA|ECDSA|DHE|ECDHE).*"',
            r'"ssl_version":\s*".*(?:1\.0|1\.1|1\.2).*"',  # Older SSL/TLS versions

            # Memory allocation patterns
            r'"memory_allocation":\s*(?:[0-9]{4,})',  # Large allocations for crypto
            r'"heap_usage":\s*{.*"crypto|rsa|ecc|korean"',

            # Random number generation
            r'"random_source":\s*".*(?:mersenne|linear|weak).*"',
            r'"entropy":\s*{.*"weak|insufficient"',

            # Certificate and PKI patterns
            r'"certificate":\s*{.*"rsa|ecdsa|korean"',
            r'"pki_operation":\s*".*(?:rsa_verify|ecdsa_verify|korean_verify).*"'
        ]

        all_indicators = dynamic_indicators + vulnerable_crypto_dynamic_patterns

        for pattern in all_indicators:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True

        return False