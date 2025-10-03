#!/usr/bin/env python3
"""
Systematic Obfuscation Script for All 23 Source Code Files
This script removes direct algorithm references while preserving implementation logic
"""

import re
import os
from pathlib import Path

# Define obfuscation mappings
IMPORT_REPLACEMENTS = {
    # Python imports
    r'from cryptography\.hazmat\.primitives\.asymmetric import rsa':
        'from cryptography.hazmat.primitives.asymmetric import rsa as modular_arithmetic',
    r'from cryptography\.hazmat\.primitives\.asymmetric import ec':
        'from cryptography.hazmat.primitives.asymmetric import ec as curve_operations',
    r'from cryptography\.hazmat\.primitives\.asymmetric import dsa':
        'from cryptography.hazmat.primitives.asymmetric import dsa as discrete_log',
    r'from cryptography\.hazmat\.primitives\.ciphers import algorithms':
        'from cryptography.hazmat.primitives.ciphers import algorithms as block_ciphers',
    r'from cryptography\.hazmat\.primitives\.ciphers import modes':
        'from cryptography.hazmat.primitives.ciphers import modes as cipher_modes',
    r'from cryptography\.hazmat\.primitives import hashes':
        'from cryptography.hazmat.primitives import hashes as digest_functions',
    r'from cryptography\.hazmat\.primitives import serialization':
        'from cryptography.hazmat.primitives import serialization as key_encoding',
}

API_CALL_REPLACEMENTS = {
    # RSA references
    r'\brsa\.generate_private_key\b': 'modular_arithmetic.generate_private_key',
    r'\brsa\.': 'modular_arithmetic.',

    # ECC/ECDSA references
    r'\bec\.generate_private_key\b': 'curve_operations.generate_private_key',
    r'\bec\.ECDSA\b': 'curve_operations.ECDSA',
    r'\bec\.ECDH\b': 'curve_operations.ECDH',
    r'\bec\.SECP256R1\b': 'curve_operations.SECP256R1',
    r'\bec\.SECP384R1\b': 'curve_operations.SECP384R1',
    r'\bec\.SECP521R1\b': 'curve_operations.SECP521R1',
    r'\bec\.': 'curve_operations.',

    # DSA references
    r'\bdsa\.': 'discrete_log.',

    # AES references
    r'\balgorithms\.AES\b': 'block_ciphers.AES',
    r'\balgorithms\.': 'block_ciphers.',

    # Modes references
    r'\bmodes\.CBC\b': 'cipher_modes.CBC',
    r'\bmodes\.GCM\b': 'cipher_modes.GCM',
    r'\bmodes\.CTR\b': 'cipher_modes.CTR',
    r'\bmodes\.': 'cipher_modes.',

    # Hashes references
    r'\bhashes\.SHA256\b': 'digest_functions.SHA256',
    r'\bhashes\.SHA512\b': 'digest_functions.SHA512',
    r'\bhashes\.SHA1\b': 'digest_functions.SHA1',
    r'\bhashes\.MD5\b': 'digest_functions.MD5',
    r'\bhashes\.': 'digest_functions.',

    # Padding/Serialization references
    r'\bpadding\.OAEP\b': 'key_encoding.Padding.OAEP',
    r'\bpadding\.MGF1\b': 'key_encoding.MGF1',
    r'\bpadding\.PSS\b': 'key_encoding.Padding.PSS',
    r'\bpadding\.': 'key_encoding.Padding.',
    r'\bserialization\.': 'key_encoding.',
}

STRING_LITERAL_REPLACEMENTS = {
    # Algorithm names in strings
    r'"RSA(-\d+)?"': '"MODULAR-ARITHMETIC"',
    r"'RSA(-\d+)?'": "'MODULAR-ARITHMETIC'",
    r'"AES(-\d+)?(-[A-Z]+)?"': '"BLOCK-CIPHER"',
    r"'AES(-\d+)?(-[A-Z]+)?'": "'BLOCK-CIPHER'",
    r'"SHA-?256"': '"HASH-256"',
    r"'SHA-?256'": "'HASH-256'",
    r'"SHA-?512"': '"HASH-512"',
    r"'SHA-?512'": "'HASH-512'",
    r'"SHA-?1"': '"HASH-160"',
    r"'SHA-?1'": "'HASH-160'",
    r'"MD5"': '"HASH-128"',
    r"'MD5'": "'HASH-128'",
    r'"ECDSA"': '"CURVE-SIG"',
    r"'ECDSA'": "'CURVE-SIG'",
    r'"ECDH"': '"CURVE-EXCHANGE"',
    r"'ECDH'": "'CURVE-EXCHANGE'",
    r'"ECC"': '"ELLIPTIC-CURVE"',
    r"'ECC'": "'ELLIPTIC-CURVE'",
    r'"DSA"': '"DISCRETE-LOG-SIG"',
    r"'DSA'": "'DISCRETE-LOG-SIG'",
    r'"DH"': '"DISCRETE-LOG-EXCHANGE"',
    r"'DH'": "'DISCRETE-LOG-EXCHANGE'",
    r'"3DES"': '"TRIPLE-CIPHER"',
    r"'3DES'": "'TRIPLE-CIPHER'",
    r'"DES"': '"DATA-CIPHER"',
    r"'DES'": "'DATA-CIPHER'",
    r'"RC4"': '"STREAM-CIPHER-4"',
    r"'RC4'": "'STREAM-CIPHER-4'",
}

COMMENT_REPLACEMENTS = {
    # Comments
    r'#.*RSA.*': '# Asymmetric modular arithmetic operations',
    r'#.*AES.*': '# Block cipher operations',
    r'#.*SHA-?256.*': '# 256-bit cryptographic hash',
    r'#.*SHA-?512.*': '# 512-bit cryptographic hash',
    r'#.*ECDSA.*': '# Elliptic curve digital signature',
    r'#.*ECDH.*': '# Elliptic curve key exchange',
    r'#.*ECC.*': '# Elliptic curve cryptography',
    r'//.*RSA.*': '// Asymmetric modular arithmetic operations',
    r'//.*AES.*': '// Block cipher operations',
    r'//.*SHA.*': '// Cryptographic hash function',
    r'//.*ECDSA.*': '// Elliptic curve digital signature',
}

VARIABLE_NAME_REPLACEMENTS = {
    r'\brsa_key\b': 'asym_key',
    r'\brsa_cipher\b': 'asym_cipher',
    r'\baes_key\b': 'block_key',
    r'\baes_cipher\b': 'block_cipher',
    r'\becdsa_sig\b': 'curve_sig',
    r'\becdsa_verify\b': 'curve_verify',
    r'\bsha256_hash\b': 'digest_256',
    r'\bsha512_hash\b': 'digest_512',
}

def obfuscate_file(file_path):
    """Obfuscate a single file"""
    print(f"Processing: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements_made = 0

    # Apply import replacements
    for pattern, replacement in IMPORT_REPLACEMENTS.items():
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            replacements_made += content.count(pattern)
            content = new_content

    # Apply API call replacements
    for pattern, replacement in API_CALL_REPLACEMENTS.items():
        matches = len(re.findall(pattern, content))
        content = re.sub(pattern, replacement, content)
        replacements_made += matches

    # Apply string literal replacements
    for pattern, replacement in STRING_LITERAL_REPLACEMENTS.items():
        matches = len(re.findall(pattern, content))
        content = re.sub(pattern, replacement, content)
        replacements_made += matches

    # Apply variable name replacements
    for pattern, replacement in VARIABLE_NAME_REPLACEMENTS.items():
        matches = len(re.findall(pattern, content))
        content = re.sub(pattern, replacement, content)
        replacements_made += matches

    # Apply comment replacements
    for pattern, replacement in COMMENT_REPLACEMENTS.items():
        matches = len(re.findall(pattern, content))
        content = re.sub(pattern, replacement, content)
        replacements_made += matches

    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Made {replacements_made} replacements")
        return replacements_made
    else:
        print(f"  - No changes needed")
        return 0

def main():
    """Process all source code files"""
    base_dir = Path("/home/junsu/AI--Benchmark/data/test_files/source_code")

    target_files = [
        "StealthCryptographicLibrary.py",
        "AutomotiveSecurityUnit.cpp",
        "BlockchainCryptographyEngine.java",
        "BlockchainValidationEngine.scala",
        "cloud_security_orchestrator.py",
        "CorporateSecurityOrchestrator.py",
        "DatabaseEncryptionManager.kt",
        "DataProcessingOrchestrator.scala",
        "digital_identity_platform.js",
        "distributed_key_management.php",
        "enterprise_pki_infrastructure.cs",
        "EnterpriseDataSecurityFramework.c",
        "financial_risk_analyzer.py",
        "government_document_signer.c",
        "HardwareSecurity.java",
        "IoTDeviceSecurityController.go",
        "LegacyPKISystem.java",
        "military_communication_system.c",
        "network_infrastructure_monitor.cpp",
        "QuantumResistantMessaging.java",
        "secure_messaging_protocol.rb",
        "SecureCloudStorage.java",
        "SecureVirtualPrivateNetwork.ts"
    ]

    total_replacements = 0
    processed_files = 0

    print("="*60)
    print("SYSTEMATIC OBFUSCATION OF 23 SOURCE CODE FILES")
    print("="*60)
    print()

    for filename in target_files:
        file_path = base_dir / filename
        if file_path.exists():
            replacements = obfuscate_file(file_path)
            total_replacements += replacements
            processed_files += 1
        else:
            print(f"WARNING: File not found: {file_path}")

    print()
    print("="*60)
    print(f"OBFUSCATION COMPLETE")
    print(f"Files processed: {processed_files}/{len(target_files)}")
    print(f"Total replacements: {total_replacements}")
    print("="*60)

if __name__ == "__main__":
    main()
