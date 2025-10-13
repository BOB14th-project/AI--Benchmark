"""
Cloud Storage Encryption Service
Implements file encryption with integrity verification for cloud storage.
Designed for enterprise document management and secure file sharing.
"""

import os
import json
import hmac
import hashlib
import struct
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import secrets


class FileEncryptionEngine:
    """
    Advanced file encryption using involution-based SPN cipher.
    Optimized for large file processing with streaming support.
    """

    def __init__(self, encryption_key: bytes):
        if len(encryption_key) != 16:
            raise ValueError("Encryption key must be 128 bits")

        self.block_size = 16
        self.total_rounds = 12
        self.master_key = encryption_key
        self.round_keys = self._generate_round_keys()
        self._initialize_sbox_tables()

    def _initialize_sbox_tables(self):
        """Initialize substitution boxes for byte transformation"""
        self.sbox_type1 = []
        self.sbox_type2 = []
        self.inv_sbox_type1 = [0] * 256
        self.inv_sbox_type2 = [0] * 256

        for i in range(256):
            # Type 1 S-box (affine transformation)
            val1 = self._gf256_multiply(i, 0x63) ^ 0x1f
            self.sbox_type1.append(val1)
            self.inv_sbox_type1[val1] = i

            # Type 2 S-box (different polynomial)
            val2 = self._gf256_multiply(i, 0x97) ^ 0x5b
            self.sbox_type2.append(val2)
            self.inv_sbox_type2[val2] = i

    @staticmethod
    def _gf256_multiply(a: int, b: int) -> int:
        """Multiplication in GF(2^8)"""
        result = 0
        poly = 0x11b  # Irreducible polynomial

        for _ in range(8):
            if b & 1:
                result ^= a
            high_bit = a & 0x80
            a <<= 1
            if high_bit:
                a ^= poly
            b >>= 1

        return result & 0xff

    def _generate_round_keys(self) -> List[bytes]:
        """Generate round keys using key schedule"""
        keys = []
        state = bytearray(self.master_key)

        for round_num in range(self.total_rounds + 1):
            round_key = bytearray(16)

            # Rotate and substitute
            first = state[0]
            for i in range(15):
                state[i] = self.sbox_type1[state[i + 1]] if hasattr(self, 'sbox_type1') else state[i + 1]
            state[15] = self.sbox_type1[first] if hasattr(self, 'sbox_type1') else first

            # Mix with round constant
            state[0] ^= (round_num * 0x13) & 0xff
            state[1] ^= (round_num * 0x1f) & 0xff

            round_key[:] = state
            keys.append(bytes(round_key))

        return keys

    def _substitution_layer(self, state: bytearray, inverse: bool = False):
        """Apply S-box substitution to state"""
        sbox1 = self.inv_sbox_type1 if inverse else self.sbox_type1
        sbox2 = self.inv_sbox_type2 if inverse else self.sbox_type2

        for i in range(16):
            state[i] = sbox1[state[i]] if i % 2 == 0 else sbox2[state[i]]

    def _diffusion_layer(self, state: bytearray):
        """Apply MDS matrix for diffusion"""
        temp = bytearray(16)

        # 4x4 MDS matrix multiplication
        mds_matrix = [
            [2, 3, 1, 1],
            [1, 2, 3, 1],
            [1, 1, 2, 3],
            [3, 1, 1, 2]
        ]

        for row in range(4):
            for col in range(4):
                val = 0
                for k in range(4):
                    val ^= self._gf256_multiply(mds_matrix[row][k], state[k * 4 + col])
                temp[row * 4 + col] = val

        state[:] = temp

    def _add_round_key(self, state: bytearray, round_key: bytes):
        """XOR state with round key"""
        for i in range(16):
            state[i] ^= round_key[i]

    def encrypt_block(self, plaintext: bytes) -> bytes:
        """Encrypt single 128-bit block"""
        if len(plaintext) != self.block_size:
            raise ValueError(f"Block must be {self.block_size} bytes")

        state = bytearray(plaintext)

        # Initial round key
        self._add_round_key(state, self.round_keys[0])

        # Main rounds
        for round_num in range(1, self.total_rounds):
            self._substitution_layer(state)
            self._diffusion_layer(state)
            self._add_round_key(state, self.round_keys[round_num])

        # Final round (no diffusion)
        self._substitution_layer(state)
        self._add_round_key(state, self.round_keys[self.total_rounds])

        return bytes(state)

    def encrypt_file_data(self, data: bytes) -> bytes:
        """Encrypt file data with PKCS7 padding"""
        # Apply padding
        pad_len = self.block_size - (len(data) % self.block_size)
        padded = data + bytes([pad_len] * pad_len)

        # Encrypt blocks
        encrypted = b''
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            encrypted += self.encrypt_block(block)

        return encrypted

    def decrypt_file_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data and remove padding"""
        if len(encrypted_data) % self.block_size != 0:
            raise ValueError("Invalid encrypted data length")

        # For demonstration, we'll implement basic decryption
        # In production, implement full inverse operations
        decrypted = encrypted_data  # Placeholder
        pad_len = decrypted[-1]
        return decrypted[:-pad_len]


class FileIntegrityVerifier:
    """
    File integrity verification using 160-bit hash function.
    Implements Merkle-Damgård construction with compression function.
    """

    def __init__(self):
        # Initial hash values (160 bits = 5 x 32-bit words)
        self.h0 = 0x67452301
        self.h1 = 0xEFCDAB89
        self.h2 = 0x98BADCFE
        self.h3 = 0x10325476
        self.h4 = 0xC3D2E1F0

        self.block_size = 64  # 512-bit blocks

    @staticmethod
    def _rotate_left(n: int, b: int) -> int:
        """Rotate left operation (32-bit)"""
        return ((n << b) | (n >> (32 - b))) & 0xffffffff

    def _compression_function(self, chunk: bytes, h: List[int]) -> List[int]:
        """Core compression function with message expansion"""
        # Message schedule (80 words)
        w = [0] * 80

        # Break chunk into 16 words
        for i in range(16):
            w[i] = struct.unpack('>I', chunk[i*4:(i+1)*4])[0]

        # Extend to 80 words
        for i in range(16, 80):
            temp = w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]
            w[i] = self._rotate_left(temp, 1)

        # Initialize working variables
        a, b, c, d, e = h

        # 80 compression rounds
        for i in range(80):
            if i < 20:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif i < 40:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif i < 60:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = (self._rotate_left(a, 5) + f + e + k + w[i]) & 0xffffffff
            e = d
            d = c
            c = self._rotate_left(b, 30)
            b = a
            a = temp

        # Add to hash
        h[0] = (h[0] + a) & 0xffffffff
        h[1] = (h[1] + b) & 0xffffffff
        h[2] = (h[2] + c) & 0xffffffff
        h[3] = (h[3] + d) & 0xffffffff
        h[4] = (h[4] + e) & 0xffffffff

        return h

    def compute_hash(self, data: bytes) -> bytes:
        """Compute 160-bit hash digest"""
        # Padding
        msg_len = len(data)
        data += b'\x80'

        while (len(data) % 64) != 56:
            data += b'\x00'

        # Append length
        data += struct.pack('>Q', msg_len * 8)

        # Initialize hash
        h = [self.h0, self.h1, self.h2, self.h3, self.h4]

        # Process blocks
        for i in range(0, len(data), 64):
            chunk = data[i:i+64]
            h = self._compression_function(chunk, h)

        # Produce digest
        digest = b''
        for val in h:
            digest += struct.pack('>I', val)

        return digest


@dataclass
class FileMetadata:
    """Metadata for encrypted file"""
    file_id: str
    original_name: str
    original_size: int
    encrypted_size: int
    owner: str
    upload_time: str
    content_type: str
    integrity_hash: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'FileMetadata':
        return cls(**data)


class SecureCloudStorage:
    """
    Production cloud storage service with encryption and integrity verification.
    Implements secure file upload, download, and management.
    """

    def __init__(self, encryption_key: bytes, storage_path: str = "/tmp/secure_cloud"):
        self.encryptor = FileEncryptionEngine(encryption_key)
        self.verifier = FileIntegrityVerifier()
        self.storage_path = storage_path
        self.file_registry: Dict[str, FileMetadata] = {}

        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)

    def _generate_file_id(self) -> str:
        """Generate unique file identifier"""
        return 'file_' + secrets.token_hex(16)

    def upload_file(self, file_data: bytes, filename: str, owner: str,
                   content_type: str = "application/octet-stream") -> FileMetadata:
        """
        Upload and encrypt file to cloud storage.

        Args:
            file_data: Original file content
            filename: Original filename
            owner: File owner identifier
            content_type: MIME type

        Returns:
            FileMetadata object
        """
        print(f"Uploading file: {filename}")
        print(f"  Original size: {len(file_data)} bytes")

        # Generate file ID
        file_id = self._generate_file_id()

        # Encrypt file
        encrypted_data = self.encryptor.encrypt_file_data(file_data)
        print(f"  Encrypted size: {len(encrypted_data)} bytes")

        # Compute integrity hash
        integrity_hash = self.verifier.compute_hash(encrypted_data)
        hash_hex = integrity_hash.hex()
        print(f"  Integrity hash: {hash_hex[:32]}...")

        # Save encrypted file
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)

        # Create metadata
        metadata = FileMetadata(
            file_id=file_id,
            original_name=filename,
            original_size=len(file_data),
            encrypted_size=len(encrypted_data),
            owner=owner,
            upload_time=datetime.now().isoformat(),
            content_type=content_type,
            integrity_hash=hash_hex
        )

        # Save metadata
        self.file_registry[file_id] = metadata
        self._save_metadata(metadata)

        print(f"  File ID: {file_id}")
        print(f"  Upload complete!\n")

        return metadata

    def download_file(self, file_id: str, verify_integrity: bool = True) -> Tuple[bytes, FileMetadata]:
        """
        Download and decrypt file from cloud storage.

        Args:
            file_id: File identifier
            verify_integrity: Whether to verify file integrity

        Returns:
            Tuple of (decrypted_data, metadata)
        """
        if file_id not in self.file_registry:
            raise ValueError(f"File not found: {file_id}")

        metadata = self.file_registry[file_id]
        print(f"Downloading file: {metadata.original_name}")

        # Load encrypted file
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        # Verify integrity
        if verify_integrity:
            computed_hash = self.verifier.compute_hash(encrypted_data)
            if computed_hash.hex() != metadata.integrity_hash:
                raise ValueError("File integrity verification failed!")
            print(f"  Integrity verified: OK")

        # Decrypt file (placeholder - would implement full decryption)
        # For demonstration, we'll return the encrypted data as-is
        print(f"  File downloaded: {len(encrypted_data)} bytes\n")

        return encrypted_data, metadata

    def list_files(self, owner: Optional[str] = None) -> List[FileMetadata]:
        """List all files, optionally filtered by owner"""
        files = list(self.file_registry.values())

        if owner:
            files = [f for f in files if f.owner == owner]

        return files

    def delete_file(self, file_id: str) -> bool:
        """Delete file from storage"""
        if file_id not in self.file_registry:
            return False

        metadata = self.file_registry[file_id]
        print(f"Deleting file: {metadata.original_name}")

        # Delete encrypted file
        encrypted_path = os.path.join(self.storage_path, f"{file_id}.enc")
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)

        # Delete metadata file
        metadata_path = os.path.join(self.storage_path, f"{file_id}.meta")
        if os.path.exists(metadata_path):
            os.remove(metadata_path)

        # Remove from registry
        del self.file_registry[file_id]

        print(f"  File deleted: {file_id}\n")
        return True

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_files = len(self.file_registry)
        total_original_size = sum(f.original_size for f in self.file_registry.values())
        total_encrypted_size = sum(f.encrypted_size for f in self.file_registry.values())

        return {
            'total_files': total_files,
            'total_original_size': total_original_size,
            'total_encrypted_size': total_encrypted_size,
            'encryption_overhead': total_encrypted_size - total_original_size
        }

    def _save_metadata(self, metadata: FileMetadata):
        """Save metadata to disk"""
        metadata_path = os.path.join(self.storage_path, f"{metadata.file_id}.meta")
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)


def demonstrate_cloud_storage():
    """Demonstration of secure cloud storage service"""
    print("=" * 70)
    print("Secure Cloud Storage Service")
    print("Enterprise File Encryption and Integrity Verification")
    print("=" * 70)
    print()

    # Initialize storage service
    encryption_key = secrets.token_bytes(16)
    storage = SecureCloudStorage(encryption_key)

    print("--- Uploading Files ---")

    # Upload document
    document_content = b"""
    CONFIDENTIAL BUSINESS PLAN
    ==========================

    This document contains proprietary information about our Q1 2025
    business strategy, market analysis, and financial projections.

    Revenue targets: $10M
    Market expansion: APAC region
    New product launch: Q2 2025
    """

    doc_metadata = storage.upload_file(
        document_content,
        "business_plan_2025.txt",
        "ceo@company.com",
        "text/plain"
    )

    # Upload configuration
    config_content = json.dumps({
        "database": {
            "host": "db.internal.company.com",
            "port": 5432,
            "username": "admin",
            "ssl_mode": "require"
        },
        "api_keys": {
            "stripe": "sk_live_xxxxxxxxxxxxx",
            "aws": "AKIA..."
        }
    }, indent=2).encode()

    config_metadata = storage.upload_file(
        config_content,
        "production_config.json",
        "devops@company.com",
        "application/json"
    )

    # Upload large file
    large_file = secrets.token_bytes(5000)
    large_metadata = storage.upload_file(
        large_file,
        "database_backup.dat",
        "admin@company.com",
        "application/octet-stream"
    )

    # List files
    print("--- File Listing ---")
    all_files = storage.list_files()
    for f in all_files:
        print(f"  {f.original_name}")
        print(f"    ID: {f.file_id}")
        print(f"    Owner: {f.owner}")
        print(f"    Size: {f.original_size} bytes -> {f.encrypted_size} bytes")
        print(f"    Uploaded: {f.upload_time}")
        print()

    # Download and verify
    print("--- Downloading and Verifying File ---")
    try:
        downloaded_data, metadata = storage.download_file(doc_metadata.file_id)
        print(f"Successfully downloaded: {metadata.original_name}")
    except ValueError as e:
        print(f"Download failed: {e}")

    # Storage statistics
    print("--- Storage Statistics ---")
    stats = storage.get_storage_stats()
    print(f"Total files: {stats['total_files']}")
    print(f"Original data: {stats['total_original_size']} bytes")
    print(f"Encrypted data: {stats['total_encrypted_size']} bytes")
    print(f"Overhead: {stats['encryption_overhead']} bytes " +
          f"({stats['encryption_overhead']/stats['total_original_size']*100:.1f}%)")
    print()

    # Delete file
    print("--- Deleting File ---")
    storage.delete_file(config_metadata.file_id)

    # Final statistics
    print("--- Final Statistics ---")
    final_stats = storage.get_storage_stats()
    print(f"Remaining files: {final_stats['total_files']}")
    print()

    print("=" * 70)
    print("Cloud storage demonstration completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_cloud_storage()
