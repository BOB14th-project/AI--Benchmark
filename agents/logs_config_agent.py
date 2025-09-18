from typing import List
from .base_agent import BaseAnalysisAgent
import re

class LogsConfigAgent(BaseAnalysisAgent):
    def __init__(self, prompt_template: str = None):
        if prompt_template is None:
            prompt_template = "Analyze the following logs/configuration and determine: {analysis_points}"

        super().__init__(
            name="Configuration and Logs Vulnerable Crypto Analysis Agent",
            description="Analyzes configuration files and logs to detect quantum-vulnerable cryptography settings including Korean algorithms",
            prompt_template=prompt_template
        )

    def get_analysis_points(self) -> List[str]:
        return [
            "RSA certificate configurations and key specifications in config files",
            "elliptic curve cipher suite configurations and ECC parameter settings",
            "discrete logarithm based algorithm configurations (DSA, DH, ElGamal)",
            "Korean algorithm configuration parameters (SEED, ARIA, HIGHT, LEA, KCDSA, HAS-160, LSH)",
            "symmetric cipher configurations vulnerable to quantum attacks",
            "SSL/TLS configuration with quantum-vulnerable cipher suites and protocols",
            "cryptographic library configuration and algorithm selection settings",
            "certificate authority and PKI configurations using vulnerable algorithms",
            "log entries indicating quantum-vulnerable cryptographic operations",
            "authentication and key management system configurations",
            "legacy cryptographic protocol configurations and deprecated settings",
            "Korean domestic cryptographic standard compliance configurations",
            "error patterns and warnings related to vulnerable crypto implementations",
            "migration logs showing use of quantum-vulnerable to quantum-resistant transitions"
        ]

    def validate_input(self, input_data: str) -> bool:
        if not input_data or not input_data.strip():
            return False

        # Standard log indicators
        log_indicators = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
            r'\[INFO\]|\[ERROR\]|\[WARNING\]|\[DEBUG\]',
            r'ERROR:|WARN:|INFO:|DEBUG:',
            r'Exception|Error|Failed|Success',
            r'HTTP/\d\.\d\s+\d{3}',
            r'\d+\.\d+\.\d+\.\d+',
            r'GET|POST|PUT|DELETE|HEAD|OPTIONS',
            r'status:\s*\d{3}',
            r'response_time:\s*[\d.]+',
            r'user_id:\s*\w+',
            r'session_id:\s*\w+',
            r'request_id:\s*[\w-]+'
        ]

        # Standard configuration indicators
        config_indicators = [
            r'^\s*\w+\s*=\s*.+$',
            r'^\s*\[.*\]\s*$',
            r'^\s*#.*$',
            r'host:\s*\w+',
            r'port:\s*\d+',
            r'database:\s*\w+',
            r'username:\s*\w+',
            r'password:\s*\w+',
            r'timeout:\s*\d+',
            r'ssl:\s*(true|false)',
            r'debug:\s*(true|false)',
            r'max_connections:\s*\d+',
            r'buffer_size:\s*\d+',
            r'log_level:\s*\w+',
            r'{\s*".*":\s*".*"\s*}',
            r'<\w+.*>.*</\w+>',
            r'version:\s*[\d.]+',
            r'environment:\s*\w+'
        ]

        # Quantum-vulnerable crypto log and config patterns
        vulnerable_crypto_log_config_patterns = [
            # RSA patterns
            r'rsa|RSA|rsa.{0,10}key|RSA.{0,10}KEY',
            r'modulus.{0,10}size.*(?:1024|2048|3072|4096)',
            r'rsa.{0,10}cert|RSA.{0,10}CERT|rsa.{0,10}certificate',

            # ECC patterns
            r'ecc|ECC|ecdsa|ECDSA|ecdh|ECDH',
            r'elliptic.{0,10}curve|secp\d+|prime\d+v\d+',
            r'ec.{0,10}cert|EC.{0,10}CERT|ecc.{0,10}certificate',

            # DH/DSA patterns
            r'diffie.{0,10}hellman|dh.{0,10}key|DH.{0,10}KEY',
            r'dsa|DSA|dsa.{0,10}signature|DSA.{0,10}SIGNATURE',
            r'discrete.{0,10}log|elgamal|ElGamal',

            # Korean algorithm patterns
            r'seed|SEED|aria|ARIA|hight|HIGHT|lea|LEA',
            r'kcdsa|KCDSA|korean.{0,10}signature',
            r'has.{0,5}160|HAS.{0,5}160|lsh.{0,5}256|LSH.{0,5}256',

            # Symmetric vulnerable patterns
            r'des|DES|3des|3DES|triple.{0,10}des',
            r'rc4|RC4|stream.{0,10}cipher',
            r'aes.{0,5}128|AES.{0,5}128',

            # Hash function patterns
            r'md5|MD5|sha1|SHA1|sha.{0,5}256',
            r'hash.{0,10}algorithm.*(?:md5|sha1|sha256)',

            # SSL/TLS vulnerable patterns
            r'ssl.{0,10}version.*(?:1\.0|1\.1|1\.2|2\.0|3\.0)',
            r'tls.{0,10}version.*(?:1\.0|1\.1|1\.2)',
            r'cipher.{0,10}suite.*(?:rsa|ecdsa|dh|des|rc4)',
            r'protocol.*(?:sslv2|sslv3|tlsv1\.0|tlsv1\.1)',

            # Certificate patterns
            r'certificate.*(?:rsa|ecdsa|dsa|korean)',
            r'cert.*(?:1024|2048|3072|4096).*bit',
            r'x509.*(?:rsa|ecdsa|korean)',

            # Korean crypto library patterns
            r'kisa|KISA|kcmvp|KCMVP|crypton|CRYPTON',
            r'korean.{0,10}crypto|domestic.{0,10}algorithm',
            r'kc.{0,5}standard|KC.{0,5}STANDARD',

            # Crypto library patterns
            r'openssl|OpenSSL|crypto\+\+|cryptopp',
            r'javax\.crypto|java\.security',
            r'bouncy.{0,10}castle|BouncyCastle',

            # Vulnerable configuration patterns
            r'algorithm.*(?:rsa|ecdsa|dsa|des|rc4|md5|sha1)',
            r'key.{0,10}size.*(?:1024|2048|512|128)',
            r'cipher.*(?:des|rc4|export)',

            # Error and warning patterns
            r'deprecated.*(?:algorithm|cipher|protocol)',
            r'insecure.*(?:algorithm|cipher|key)',
            r'weak.*(?:encryption|signature|hash)',
            r'vulnerability.*(?:rsa|ecc|des|md5|sha1)',

            # Migration and compliance patterns
            r'migration.*(?:quantum|crypto|algorithm)',
            r'compliance.*(?:fips|cc|korean.{0,10}standard)',
            r'audit.*(?:crypto|algorithm|cipher)',
            r'upgrade.*(?:crypto|ssl|tls|algorithm)'
        ]

        all_indicators = log_indicators + config_indicators + vulnerable_crypto_log_config_patterns

        for pattern in all_indicators:
            if re.search(pattern, input_data, re.IGNORECASE | re.MULTILINE):
                return True

        return False