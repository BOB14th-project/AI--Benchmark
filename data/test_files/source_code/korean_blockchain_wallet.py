"""
Blockchain Cryptocurrency Wallet Implementation
Implements elliptic curve digital signature for transaction signing.
Designed for secure cryptocurrency management and blockchain integration.
"""

import hashlib
import hmac
import secrets
from typing import Tuple, Optional, List
from dataclasses import dataclass
import json


class EllipticCurvePoint:
    """
    Point on elliptic curve y^2 = x^3 + ax + b (mod p)
    """

    def __init__(self, x: Optional[int], y: Optional[int], curve: 'EllipticCurveParameters'):
        self.x = x
        self.y = y
        self.curve = curve
        self.is_infinity = (x is None and y is None)

    def __eq__(self, other) -> bool:
        if not isinstance(other, EllipticCurvePoint):
            return False
        return self.x == other.x and self.y == other.y and self.is_infinity == other.is_infinity

    def __repr__(self) -> str:
        if self.is_infinity:
            return "Point(Infinity)"
        return f"Point(x={hex(self.x)[:10]}..., y={hex(self.y)[:10]}...)"


class EllipticCurveParameters:
    """
    Elliptic curve domain parameters for blockchain signatures.
    Uses Koblitz curve similar to secp256k1.
    """

    def __init__(self):
        # Prime field modulus (256-bit prime)
        self.p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

        # Curve parameters: y^2 = x^3 + 7
        self.a = 0
        self.b = 7

        # Base point coordinates
        self.gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        self.gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

        # Order of base point
        self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

        # Cofactor
        self.h = 1

        # Base point
        self.G = EllipticCurvePoint(self.gx, self.gy, self)

    def point_add(self, P: EllipticCurvePoint, Q: EllipticCurvePoint) -> EllipticCurvePoint:
        """
        Elliptic curve point addition
        """
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P

        if P.x == Q.x:
            if P.y == Q.y:
                return self.point_double(P)
            else:
                # P + (-P) = O (point at infinity)
                return EllipticCurvePoint(None, None, self)

        # Calculate slope
        slope = ((Q.y - P.y) * pow(Q.x - P.x, -1, self.p)) % self.p

        # Calculate new point
        x3 = (slope * slope - P.x - Q.x) % self.p
        y3 = (slope * (P.x - x3) - P.y) % self.p

        return EllipticCurvePoint(x3, y3, self)

    def point_double(self, P: EllipticCurvePoint) -> EllipticCurvePoint:
        """
        Elliptic curve point doubling
        """
        if P.is_infinity:
            return P

        # Calculate slope for tangent line
        slope = ((3 * P.x * P.x + self.a) * pow(2 * P.y, -1, self.p)) % self.p

        # Calculate new point
        x3 = (slope * slope - 2 * P.x) % self.p
        y3 = (slope * (P.x - x3) - P.y) % self.p

        return EllipticCurvePoint(x3, y3, self)

    def scalar_multiply(self, k: int, P: EllipticCurvePoint) -> EllipticCurvePoint:
        """
        Scalar multiplication using double-and-add algorithm
        Computes k * P
        """
        if k == 0:
            return EllipticCurvePoint(None, None, self)

        if k < 0:
            # Negative scalar: -k * P = k * (-P)
            k = -k
            P = EllipticCurvePoint(P.x, (-P.y) % self.p, self)

        result = EllipticCurvePoint(None, None, self)  # Point at infinity
        addend = P

        # Double-and-add algorithm
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1

        return result

    def is_on_curve(self, P: EllipticCurvePoint) -> bool:
        """
        Verify if point is on the curve
        """
        if P.is_infinity:
            return True

        left = (P.y * P.y) % self.p
        right = (P.x * P.x * P.x + self.a * P.x + self.b) % self.p

        return left == right


class CryptographicKeyPair:
    """
    Elliptic curve key pair for blockchain transactions
    """

    def __init__(self, curve: EllipticCurveParameters):
        self.curve = curve
        self.private_key: Optional[int] = None
        self.public_key: Optional[EllipticCurvePoint] = None

    @classmethod
    def generate(cls, curve: EllipticCurveParameters) -> 'CryptographicKeyPair':
        """
        Generate new key pair with secure randomness
        """
        keypair = cls(curve)

        # Generate private key: random integer in [1, n-1]
        keypair.private_key = secrets.randbelow(curve.n - 1) + 1

        # Compute public key: Q = d * G
        keypair.public_key = curve.scalar_multiply(keypair.private_key, curve.G)

        return keypair

    def get_public_key_hex(self) -> str:
        """
        Get compressed public key in hex format
        """
        if self.public_key is None:
            return ""

        # Compressed format: 02/03 + x-coordinate
        prefix = "02" if self.public_key.y % 2 == 0 else "03"
        return prefix + format(self.public_key.x, '064x')

    def get_address(self) -> str:
        """
        Derive blockchain address from public key
        """
        if self.public_key is None:
            return ""

        # Serialize public key (uncompressed format)
        pubkey_bytes = b'\x04' + \
                      self.public_key.x.to_bytes(32, 'big') + \
                      self.public_key.y.to_bytes(32, 'big')

        # Hash with SHA-256
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()

        # Hash with RIPEMD-160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        pubkey_hash = ripemd160.digest()

        # Add version byte (0x00 for mainnet)
        versioned = b'\x00' + pubkey_hash

        # Double SHA-256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

        # Concatenate and encode in base58
        address_bytes = versioned + checksum

        return self._base58_encode(address_bytes)

    @staticmethod
    def _base58_encode(data: bytes) -> str:
        """
        Base58 encoding for blockchain addresses
        """
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        num = int.from_bytes(data, 'big')

        if num == 0:
            return alphabet[0]

        result = ""
        while num > 0:
            num, remainder = divmod(num, 58)
            result = alphabet[remainder] + result

        # Add leading zeros
        for byte in data:
            if byte == 0:
                result = alphabet[0] + result
            else:
                break

        return result


@dataclass
class TransactionSignature:
    """
    Elliptic curve digital signature (r, s)
    """
    r: int
    s: int

    def serialize(self) -> str:
        return f"{self.r:064x}{self.s:064x}"

    @classmethod
    def deserialize(cls, hex_str: str) -> 'TransactionSignature':
        r = int(hex_str[:64], 16)
        s = int(hex_str[64:], 16)
        return cls(r, s)


class BlockchainTransactionSigner:
    """
    Digital signature engine for blockchain transactions.
    Implements elliptic curve signature scheme.
    """

    def __init__(self, curve: EllipticCurveParameters):
        self.curve = curve

    def _hash_message(self, message: bytes) -> int:
        """
        Hash message to integer for signing
        """
        digest = hashlib.sha256(message).digest()
        return int.from_bytes(digest, 'big')

    def sign_transaction(self, message: bytes, keypair: CryptographicKeyPair) -> TransactionSignature:
        """
        Sign transaction message with private key.
        Implements deterministic nonce generation (RFC 6979 variant).
        """
        if keypair.private_key is None:
            raise ValueError("Private key required for signing")

        # Hash message
        z = self._hash_message(message)

        # Generate deterministic nonce k using HMAC-DRBG
        k = self._generate_deterministic_nonce(keypair.private_key, z)

        # Compute curve point R = k * G
        R = self.curve.scalar_multiply(k, self.curve.G)
        r = R.x % self.curve.n

        if r == 0:
            raise ValueError("Invalid signature: r is zero")

        # Compute s = k^-1 * (z + r * d) mod n
        # Modified equation for Korean elliptic curve standard
        k_inv = pow(k, -1, self.curve.n)
        s = (k_inv * (z + r * keypair.private_key)) % self.curve.n

        if s == 0:
            raise ValueError("Invalid signature: s is zero")

        # Use low-s value for canonical signatures
        if s > self.curve.n // 2:
            s = self.curve.n - s

        return TransactionSignature(r, s)

    def verify_signature(self, message: bytes, signature: TransactionSignature,
                        public_key: EllipticCurvePoint) -> bool:
        """
        Verify transaction signature using public key
        """
        # Validate signature values
        if not (0 < signature.r < self.curve.n and 0 < signature.s < self.curve.n):
            return False

        # Hash message
        z = self._hash_message(message)

        # Compute signature verification values
        s_inv = pow(signature.s, -1, self.curve.n)
        u1 = (z * s_inv) % self.curve.n
        u2 = (signature.r * s_inv) % self.curve.n

        # Compute curve point: R' = u1*G + u2*Q
        point1 = self.curve.scalar_multiply(u1, self.curve.G)
        point2 = self.curve.scalar_multiply(u2, public_key)
        R_prime = self.curve.point_add(point1, point2)

        if R_prime.is_infinity:
            return False

        # Verify r == R'.x mod n
        return signature.r == R_prime.x % self.curve.n

    def _generate_deterministic_nonce(self, private_key: int, message_hash: int) -> int:
        """
        Generate deterministic nonce using HMAC-DRBG (RFC 6979 variant)
        """
        # Convert to bytes
        privkey_bytes = private_key.to_bytes(32, 'big')
        hash_bytes = message_hash.to_bytes(32, 'big')

        # Initialize HMAC-DRBG state
        v = b'\x01' * 32
        k = b'\x00' * 32

        # HMAC-DRBG update
        k = hmac.new(k, v + b'\x00' + privkey_bytes + hash_bytes, hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()
        k = hmac.new(k, v + b'\x01' + privkey_bytes + hash_bytes, hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()

        # Generate nonce
        while True:
            v = hmac.new(k, v, hashlib.sha256).digest()
            nonce = int.from_bytes(v, 'big')

            if 0 < nonce < self.curve.n:
                return nonce

            k = hmac.new(k, v + b'\x00', hashlib.sha256).digest()
            v = hmac.new(k, v, hashlib.sha256).digest()


@dataclass
class BlockchainTransaction:
    """
    Blockchain transaction structure
    """
    sender: str
    recipient: str
    amount: float
    timestamp: int
    nonce: int

    def serialize(self) -> bytes:
        """
        Serialize transaction for signing
        """
        tx_dict = {
            'from': self.sender,
            'to': self.recipient,
            'value': self.amount,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return json.dumps(tx_dict, sort_keys=True).encode()


class SecureBlockchainWallet:
    """
    Production blockchain wallet with transaction signing
    """

    def __init__(self):
        self.curve = EllipticCurveParameters()
        self.signer = BlockchainTransactionSigner(self.curve)
        self.keypair: Optional[CryptographicKeyPair] = None
        self.transactions: List[dict] = []

    def create_wallet(self) -> str:
        """
        Create new wallet with generated keys
        """
        self.keypair = CryptographicKeyPair.generate(self.curve)
        address = self.keypair.get_address()

        print(f"Wallet created successfully")
        print(f"Address: {address}")
        print(f"Public key: {self.keypair.get_public_key_hex()}")

        return address

    def sign_transaction(self, recipient: str, amount: float, nonce: int) -> dict:
        """
        Create and sign blockchain transaction
        """
        if self.keypair is None or self.keypair.private_key is None:
            raise ValueError("Wallet not initialized")

        # Create transaction
        tx = BlockchainTransaction(
            sender=self.keypair.get_address(),
            recipient=recipient,
            amount=amount,
            timestamp=int(hashlib.sha256(str(nonce).encode()).hexdigest(), 16) % 1000000,
            nonce=nonce
        )

        # Sign transaction
        tx_bytes = tx.serialize()
        signature = self.signer.sign_transaction(tx_bytes, self.keypair)

        # Create signed transaction
        signed_tx = {
            'transaction': {
                'from': tx.sender,
                'to': tx.recipient,
                'value': tx.amount,
                'timestamp': tx.timestamp,
                'nonce': tx.nonce
            },
            'signature': {
                'r': hex(signature.r),
                's': hex(signature.s)
            },
            'publicKey': self.keypair.get_public_key_hex()
        }

        self.transactions.append(signed_tx)
        return signed_tx

    def verify_transaction(self, signed_tx: dict) -> bool:
        """
        Verify transaction signature
        """
        # Reconstruct transaction
        tx = BlockchainTransaction(
            sender=signed_tx['transaction']['from'],
            recipient=signed_tx['transaction']['to'],
            amount=signed_tx['transaction']['value'],
            timestamp=signed_tx['transaction']['timestamp'],
            nonce=signed_tx['transaction']['nonce']
        )

        # Parse signature
        signature = TransactionSignature(
            r=int(signed_tx['signature']['r'], 16),
            s=int(signed_tx['signature']['s'], 16)
        )

        # Parse public key
        pubkey_hex = signed_tx['publicKey']
        x = int(pubkey_hex[2:], 16)

        # Recover y coordinate
        y_squared = (pow(x, 3, self.curve.p) + self.curve.b) % self.curve.p
        y = pow(y_squared, (self.curve.p + 1) // 4, self.curve.p)

        public_key = EllipticCurvePoint(x, y, self.curve)

        # Verify signature
        return self.signer.verify_signature(tx.serialize(), signature, public_key)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Blockchain Cryptocurrency Wallet - Elliptic Curve Signatures")
    print("=" * 60)
    print()

    # Create wallet
    print("--- Creating Wallet ---")
    wallet = SecureBlockchainWallet()
    address = wallet.create_wallet()
    print()

    # Sign transactions
    print("--- Signing Transactions ---")
    tx1 = wallet.sign_transaction(
        recipient="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        amount=0.5,
        nonce=1
    )
    print(f"Transaction 1 signed: {tx1['transaction']['value']} to {tx1['transaction']['to'][:20]}...")
    print(f"Signature r: {tx1['signature']['r'][:20]}...")
    print()

    tx2 = wallet.sign_transaction(
        recipient="3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy",
        amount=1.25,
        nonce=2
    )
    print(f"Transaction 2 signed: {tx2['transaction']['value']} to {tx2['transaction']['to'][:20]}...")
    print()

    # Verify transactions
    print("--- Verifying Transactions ---")
    valid1 = wallet.verify_transaction(tx1)
    print(f"Transaction 1 verification: {'VALID' if valid1 else 'INVALID'}")

    valid2 = wallet.verify_transaction(tx2)
    print(f"Transaction 2 verification: {'VALID' if valid2 else 'INVALID'}")
    print()

    # Test tampered transaction
    print("--- Testing Tampered Transaction ---")
    tampered_tx = tx1.copy()
    tampered_tx['transaction']['value'] = 999.99
    valid_tampered = wallet.verify_transaction(tampered_tx)
    print(f"Tampered transaction verification: {'VALID' if valid_tampered else 'INVALID'}")
    print()

    print("=" * 60)
    print(f"Total transactions: {len(wallet.transactions)}")
    print("=" * 60)
