"""
Financial Transaction Security Module
Implements secure encryption for banking operations and integrity verification.
"""

import struct
import hashlib
from typing import Tuple, List


class FinancialDataEncryptor:
    """
    Production-grade encryption module for banking transactions.
    Uses symmetric block cipher with Feistel network structure.
    """

    def __init__(self, master_key: bytes):
        if len(master_key) != 16:
            raise ValueError("Master key must be 128 bits")

        self.master_key = master_key
        self.round_count = 16
        self.block_bytes = 16
        self.round_keys = self._derive_round_keys()

    def _derive_round_keys(self) -> List[bytes]:
        """Derive round keys using key schedule algorithm"""
        keys = []
        key_state = list(self.master_key)

        # Key constant for mixing
        kc = [0x9e3779b9, 0x3c6ef373, 0x78dde6e6, 0xf1bbcdcc]

        for round_num in range(self.round_count):
            # Generate round key through mixing operations
            round_key = []
            for i in range(16):
                idx = (round_num * 16 + i) % len(key_state)
                mixed = key_state[idx] ^ (kc[i % 4] & 0xff)
                round_key.append(mixed)
                key_state[idx] = (key_state[idx] + mixed) & 0xff

            keys.append(bytes(round_key))

        return keys

    def _feistel_round_function(self, half_block: bytes, round_key: bytes) -> bytes:
        """
        Feistel network round function with substitution and permutation.
        """
        result = bytearray(8)

        # Key mixing
        mixed = bytes(a ^ b for a, b in zip(half_block, round_key[:8]))

        # Substitution layer (S-boxes)
        for i in range(8):
            byte_val = mixed[i]
            # Two-stage substitution
            s1 = ((byte_val * 31) + 127) & 0xff
            s2 = ((s1 ^ 0x63) + byte_val) & 0xff
            result[i] = s2

        # Permutation layer
        permuted = bytearray(8)
        perm_table = [6, 2, 7, 3, 5, 1, 4, 0]
        for i in range(8):
            permuted[i] = result[perm_table[i]]

        return bytes(permuted)

    def encrypt_block(self, plaintext: bytes) -> bytes:
        """Encrypt a single 128-bit block"""
        if len(plaintext) != self.block_bytes:
            raise ValueError(f"Block must be {self.block_bytes} bytes")

        # Split into two halves
        left = plaintext[:8]
        right = plaintext[8:]

        # Feistel network iterations
        for round_idx in range(self.round_count):
            round_key = self.round_keys[round_idx]

            # F function output
            f_output = self._feistel_round_function(right, round_key)

            # XOR with left half and swap
            new_right = bytes(a ^ b for a, b in zip(left, f_output))
            left = right
            right = new_right

        # Final swap
        return right + left

    def decrypt_block(self, ciphertext: bytes) -> bytes:
        """Decrypt a single 128-bit block"""
        if len(ciphertext) != self.block_bytes:
            raise ValueError(f"Block must be {self.block_bytes} bytes")

        # Split into two halves
        left = ciphertext[:8]
        right = ciphertext[8:]

        # Reverse Feistel network
        for round_idx in range(self.round_count - 1, -1, -1):
            round_key = self.round_keys[round_idx]

            f_output = self._feistel_round_function(left, round_key)
            new_left = bytes(a ^ b for a, b in zip(right, f_output))
            right = left
            left = new_left

        return right + left

    def encrypt_transaction(self, data: bytes) -> bytes:
        """Encrypt transaction data with PKCS7 padding"""
        # Apply padding
        pad_len = self.block_bytes - (len(data) % self.block_bytes)
        padded = data + bytes([pad_len] * pad_len)

        # Encrypt blocks
        encrypted = b''
        for i in range(0, len(padded), self.block_bytes):
            block = padded[i:i + self.block_bytes]
            encrypted += self.encrypt_block(block)

        return encrypted


class TransactionIntegrityVerifier:
    """
    Integrity verification using custom 160-bit hash function.
    Implements compression function with message expansion.
    """

    def __init__(self):
        # Initial hash values (160 bits = 5 x 32-bit words)
        self.h0 = 0x67452301
        self.h1 = 0xEFCDAB89
        self.h2 = 0x98BADCFE
        self.h3 = 0x10325476
        self.h4 = 0xC3D2E1F0

        self.block_size = 64  # 512 bits

    def _left_rotate(self, n: int, b: int) -> int:
        """Rotate left operation"""
        return ((n << b) | (n >> (32 - b))) & 0xffffffff

    def _compression_function(self, chunk: bytes, h: List[int]) -> List[int]:
        """
        Core compression function with message schedule expansion.
        """
        # Message schedule array (80 words)
        w = [0] * 80

        # Break chunk into 16 words
        for i in range(16):
            w[i] = struct.unpack('>I', chunk[i*4:(i+1)*4])[0]

        # Extend the 16 words into 80 words
        for i in range(16, 80):
            # Message expansion with rotation
            temp = w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]
            w[i] = self._left_rotate(temp, 1)

        # Initialize working variables
        a, b, c, d, e = h

        # Main compression loop (80 rounds)
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

            temp = (self._left_rotate(a, 5) + f + e + k + w[i]) & 0xffffffff
            e = d
            d = c
            c = self._left_rotate(b, 30)
            b = a
            a = temp

        # Add compressed chunk to hash value
        h[0] = (h[0] + a) & 0xffffffff
        h[1] = (h[1] + b) & 0xffffffff
        h[2] = (h[2] + c) & 0xffffffff
        h[3] = (h[3] + d) & 0xffffffff
        h[4] = (h[4] + e) & 0xffffffff

        return h

    def compute_hash(self, message: bytes) -> bytes:
        """
        Compute 160-bit hash digest of message.
        """
        # Pre-processing: add padding
        msg_len = len(message)
        message += b'\x80'

        # Pad to 448 bits (mod 512)
        while (len(message) % 64) != 56:
            message += b'\x00'

        # Append length as 64-bit big-endian
        message += struct.pack('>Q', msg_len * 8)

        # Initialize hash values
        h = [self.h0, self.h1, self.h2, self.h3, self.h4]

        # Process message in 512-bit chunks
        for i in range(0, len(message), 64):
            chunk = message[i:i+64]
            h = self._compression_function(chunk, h)

        # Produce final hash (160 bits)
        digest = b''
        for val in h:
            digest += struct.pack('>I', val)

        return digest


class SecureBankingService:
    """
    Production banking service integrating encryption and integrity verification.
    """

    def __init__(self, encryption_key: bytes):
        self.encryptor = FinancialDataEncryptor(encryption_key)
        self.integrity_checker = TransactionIntegrityVerifier()

    def process_transfer(self, account_from: str, account_to: str,
                        amount: float, timestamp: int) -> Tuple[bytes, bytes]:
        """
        Process secure bank transfer with encryption and integrity check.

        Returns:
            (encrypted_data, integrity_hash)
        """
        # Create transaction payload
        transaction = f"{account_from}|{account_to}|{amount:.2f}|{timestamp}".encode()

        # Encrypt transaction
        encrypted = self.encryptor.encrypt_transaction(transaction)

        # Compute integrity hash
        integrity_hash = self.integrity_checker.compute_hash(encrypted)

        return encrypted, integrity_hash

    def verify_and_decrypt_transfer(self, encrypted_data: bytes,
                                     provided_hash: bytes) -> str:
        """
        Verify integrity and decrypt bank transfer.

        Raises:
            ValueError: If integrity check fails
        """
        # Verify integrity
        computed_hash = self.integrity_checker.compute_hash(encrypted_data)
        if computed_hash != provided_hash:
            raise ValueError("Transaction integrity verification failed")

        # Decrypt
        decrypted = b''
        for i in range(0, len(encrypted_data), 16):
            block = encrypted_data[i:i+16]
            decrypted += self.encryptor.decrypt_block(block)

        # Remove padding
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]

        return decrypted.decode()


# Example usage for testing
if __name__ == "__main__":
    # Initialize banking service
    encryption_key = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' * 2
    banking_service = SecureBankingService(encryption_key)

    # Process transaction
    encrypted, hash_val = banking_service.process_transfer(
        account_from="KR1234567890",
        account_to="KR0987654321",
        amount=50000.00,
        timestamp=1640000000
    )

    print(f"Encrypted transaction: {encrypted.hex()}")
    print(f"Integrity hash: {hash_val.hex()}")

    # Verify and decrypt
    try:
        decrypted = banking_service.verify_and_decrypt_transfer(encrypted, hash_val)
        print(f"Decrypted: {decrypted}")
    except ValueError as e:
        print(f"Verification failed: {e}")
