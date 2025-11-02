"""
Elliptic curve certificate signature
EC variant of certificate-based signature algorithm
"""

import hashlib

class EllipticCurveCertificateSignature:
    """
    EC-based certificate signature for modern PKI
    Elliptic curve variant with certificate support
    """

    def __init__(self, curve_bits=256):
        self.curve_bits = curve_bits

        # Simplified elliptic curve parameters
        # In real implementation, would use standardized curves
        # For demonstration: y^2 = x^3 + ax + b (mod p)

        # Prime field
        if curve_bits == 256:
            self.p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
            self.a = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
            self.b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
            self.gx = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
            self.gy = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
            self.n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
        else:
            # Default parameters for other sizes
            self.p = 2**curve_bits - 1
            self.a = -3
            self.b = 123456
            self.gx = 1
            self.gy = 2
            self.n = 2**curve_bits - 1000

        # Base point G
        self.G = (self.gx, self.gy)

    def _point_add(self, P, Q):
        """Add two points on elliptic curve"""
        if P is None:
            return Q
        if Q is None:
            return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2:
            if y1 == y2:
                # Point doubling
                s = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p)
            else:
                return None  # Point at infinity
        else:
            # Point addition
            s = (y2 - y1) * pow(x2 - x1, -1, self.p)

        s %= self.p
        x3 = (s * s - x1 - x2) % self.p
        y3 = (s * (x1 - x3) - y1) % self.p

        return (x3, y3)

    def _scalar_multiply(self, k, P):
        """Multiply point P by scalar k"""
        if k == 0:
            return None
        if k == 1:
            return P

        result = None
        addend = P

        while k:
            if k & 1:
                result = self._point_add(result, addend)
            addend = self._point_add(addend, addend)
            k >>= 1

        return result

    def generate_keypair(self, seed=None):
        """
        Generate EC certificate key pair
        Private key d, Public key Q = d*G
        """
        # Private key: random integer d where 1 <= d <= n-1
        if seed:
            import random
            random.seed(seed)
            d = random.randint(1, self.n - 1)
        else:
            import os
            d = int.from_bytes(os.urandom(32), 'big') % (self.n - 1) + 1

        # Public key: Q = d*G
        Q = self._scalar_multiply(d, self.G)

        return {'private': d, 'public': Q}

    def sign_ec_certificate(self, certificate_data, private_key, hash_func='hash160'):
        """
        Sign certificate using EC certificate-based signature
        Returns EC signature (r, s)
        """
        # Hash the certificate
        if hash_func == 'hash160':
            h = hashlib.sha1(certificate_data).digest()
        else:
            h = hashlib.sha256(certificate_data).digest()

        hash_int = int.from_bytes(h, 'big') % self.n

        # Generate random k (1 <= k <= n-1)
        import os
        k = int.from_bytes(os.urandom(32), 'big') % (self.n - 1) + 1

        # Compute k*G = (x1, y1)
        kG = self._scalar_multiply(k, self.G)
        x1, y1 = kG

        # Compute r = x1 mod n
        r = x1 % self.n

        if r == 0:
            # Retry with new k (simplified, in real implementation would loop)
            k = (k + 1) % self.n
            kG = self._scalar_multiply(k, self.G)
            r = kG[0] % self.n

        # Compute k^-1 mod n
        k_inv = pow(k, -1, self.n)

        # Compute s = k^-1(H(m) + dr) mod n
        s = (k_inv * (hash_int + private_key * r)) % self.n

        return {'r': r, 's': s, 'hash_used': hash_func, 'curve_bits': self.curve_bits}

    def verify_ec_signature(self, certificate_data, signature, public_key, hash_func='hash160'):
        """Verify EC certificate signature"""
        r, s = signature['r'], signature['s']

        # Verify 1 <= r,s <= n-1
        if not (1 <= r <= self.n - 1 and 1 <= s <= self.n - 1):
            return False

        # Hash certificate
        if hash_func == 'hash160':
            h = hashlib.sha1(certificate_data).digest()
        else:
            h = hashlib.sha256(certificate_data).digest()

        hash_int = int.from_bytes(h, 'big') % self.n

        # Compute w = s^-1 mod n
        w = pow(s, -1, self.n)

        # Compute u1 = H(m)*w mod n and u2 = r*w mod n
        u1 = (hash_int * w) % self.n
        u2 = (r * w) % self.n

        # Compute (x1, y1) = u1*G + u2*Q
        u1G = self._scalar_multiply(u1, self.G)
        u2Q = self._scalar_multiply(u2, public_key)
        point = self._point_add(u1G, u2Q)

        if point is None:
            return False

        x1, y1 = point

        # Signature valid if r == x1 mod n
        return r == (x1 % self.n)

def sign_mobile_authentication_cert(cert_data, device_private_key):
    """Sign mobile device authentication certificate"""
    ec_signer = EllipticCurveCertificateSignature(curve_bits=256)
    signature = ec_signer.sign_ec_certificate(cert_data, device_private_key, hash_func='hash160')
    return signature

if __name__ == "__main__":
    # Mobile device certificate signing
    ec_ca = EllipticCurveCertificateSignature(curve_bits=256)
    device_keypair = ec_ca.generate_keypair(seed=54321)

    mobile_cert = b"MOBILE CERT: Device ID=ABC123, IMEI=123456789012345, Valid=2024-2025"

    # Sign certificate
    signature = sign_mobile_authentication_cert(mobile_cert, device_keypair['private'])

    print(f"EC Certificate signature r: {hex(signature['r'])[:50]}...")
    print(f"EC Certificate signature s: {hex(signature['s'])[:50]}...")
    print(f"Curve bits: {signature['curve_bits']}")
    print(f"Hash function: {signature['hash_used']}")
    print("Elliptic Curve certificate-based signature for mobile PKI")
