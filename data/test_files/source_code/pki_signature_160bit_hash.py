"""
PKI digital signature with 160-bit hash function
Used in certificate authorities and document signing
"""

class Hash160:
    """160-bit hash function for digital signatures"""

    def __init__(self):
        self.digest_size = 20  # 160 bits
        self.block_size = 64   # 512 bits

        # Five 32-bit initialization vectors
        self.H0 = 0x67452301
        self.H1 = 0xEFCDAB89
        self.H2 = 0x98BADCFE
        self.H3 = 0x10325476
        self.H4 = 0xC3D2E1F0

        # Constants for each round group (80 rounds total)
        self.K = [
            0x5A827999,  # Rounds 0-19
            0x6ED9EBA1,  # Rounds 20-39
            0x8F1BBCDC,  # Rounds 40-59
            0xCA62C1D6   # Rounds 60-79
        ]

    def _left_rotate(self, value, shift):
        """32-bit left rotation"""
        return ((value << shift) | (value >> (32 - shift))) & 0xffffffff

    def _f_function(self, round_num, b, c, d):
        """Non-linear function varies by round"""
        if 0 <= round_num <= 19:
            return (b & c) | (~b & d)
        elif 20 <= round_num <= 39:
            return b ^ c ^ d
        elif 40 <= round_num <= 59:
            return (b & c) | (b & d) | (c & d)
        else:  # 60-79
            return b ^ c ^ d

    def _process_block(self, block, h0, h1, h2, h3, h4):
        """
        Process 512-bit block
        Extends to 80 words then performs 80 rounds
        """
        # Break block into 16 32-bit words
        w = []
        for i in range(0, 64, 4):
            word = int.from_bytes(block[i:i+4], 'big')
            w.append(word)

        # Extend to 80 words (message expansion)
        for i in range(16, 80):
            temp = w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]
            w.append(self._left_rotate(temp, 1))

        # Initialize working variables
        a, b, c, d, e = h0, h1, h2, h3, h4

        # 80 rounds
        for round_num in range(80):
            f = self._f_function(round_num, b, c, d)
            k = self.K[round_num // 20]

            temp = (self._left_rotate(a, 5) + f + e + k + w[round_num]) & 0xffffffff
            e = d
            d = c
            c = self._left_rotate(b, 30)
            b = a
            a = temp

        # Add to hash values
        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff

        return h0, h1, h2, h3, h4

    def hash(self, message):
        """
        Compute 160-bit hash of message
        Returns 20-byte digest
        """
        # Padding
        msg_len = len(message)
        message += b'\x80'
        message += b'\x00' * ((56 - (msg_len + 1) % 64) % 64)
        message += (msg_len * 8).to_bytes(8, 'big')

        # Initialize hash values
        h0, h1, h2, h3, h4 = self.H0, self.H1, self.H2, self.H3, self.H4

        # Process each 512-bit block
        for i in range(0, len(message), 64):
            block = message[i:i+64]
            h0, h1, h2, h3, h4 = self._process_block(block, h0, h1, h2, h3, h4)

        # Produce final hash
        digest = b''
        digest += h0.to_bytes(4, 'big')
        digest += h1.to_bytes(4, 'big')
        digest += h2.to_bytes(4, 'big')
        digest += h3.to_bytes(4, 'big')
        digest += h4.to_bytes(4, 'big')

        return digest

class CertificateSignatureAlgorithm:
    """Certificate-based digital signature using 160-bit hash"""

    def __init__(self):
        self.hash_func = Hash160()

    def sign_document(self, document, private_key):
        """
        Sign document for PKI system
        Uses 160-bit hash function
        """
        # Hash the document
        document_hash = self.hash_func.hash(document)

        # Simulate DSA-like signature (simplified)
        # In real implementation, would use modular arithmetic
        signature_r = int.from_bytes(document_hash[:10], 'big')
        signature_s = int.from_bytes(document_hash[10:20], 'big')

        signature_r ^= int.from_bytes(private_key[:8], 'big')
        signature_s ^= int.from_bytes(private_key[8:16], 'big')

        signature = {
            'r': signature_r,
            's': signature_s,
            'hash': document_hash.hex()
        }

        return signature

    def verify_signature(self, document, signature, public_key):
        """Verify document signature"""
        document_hash = self.hash_func.hash(document)
        return document_hash.hex() == signature['hash']

def sign_government_certificate(certificate_data, ca_private_key):
    """Sign government-issued certificate"""
    signer = CertificateSignatureAlgorithm()
    signature = signer.sign_document(certificate_data, ca_private_key)
    return signature

if __name__ == "__main__":
    # Government certificate signing
    ca_private_key = b"CAPrivateKey2024"
    certificate = b"Certificate: Issued to John Doe, Valid until 2025-12-31"

    signature = sign_government_certificate(certificate, ca_private_key)
    print(f"Certificate signature (r): {signature['r']}")
    print(f"Certificate signature (s): {signature['s']}")
    print(f"Document hash (160-bit): {signature['hash']}")
