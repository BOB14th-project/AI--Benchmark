import math
import os

class GeometricMathManager:
    def __init__(self):
        self.curve_params = self._select_curve_parameters()
        self.private_scalar, self.public_point = self._generate_keypair()

    def _select_curve_parameters(self):
        """Select elliptic curve parameters over prime field"""

        p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
        a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
        b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

        gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
        gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

        n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

        return {
            'p': p, 'a': a, 'b': b,
            'gx': gx, 'gy': gy, 'n': n
        }

    def _generate_keypair(self):
        """Generate private-public key pair using elliptic curve mathematics"""

        private_key = self._random_in_range(1, self.curve_params['n'] - 1)

        public_key = self._point_multiply(
            private_key,
            (self.curve_params['gx'], self.curve_params['gy'])
        )

        return private_key, public_key

    def _random_in_range(self, min_val, max_val):
        """Generate mathematically secure random number in range"""
        range_size = max_val - min_val + 1
        bytes_needed = (range_size.bit_length() + 7) // 8

        while True:
            candidate = int.from_bytes(os.urandom(bytes_needed), 'big')
            if candidate <= range_size:
                return min_val + candidate

    def _point_multiply(self, scalar, point):
        """Scalar multiplication on elliptic curve using double-and-add"""
        if scalar == 0:
            return None

        result = None
        addend = point

        while scalar:
            if scalar & 1:
                result = self._point_add(result, addend)
            addend = self._point_double(addend)
            scalar >>= 1

        return result

    def _point_add(self, p1, p2):
        """Add two points on elliptic curve"""
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2:
            if y1 == y2:
                return self._point_double(p1)
            else:
                return None

        slope = ((y2 - y1) * self._mod_inverse(x2 - x1, self.curve_params['p'])) % self.curve_params['p']

        x3 = (slope * slope - x1 - x2) % self.curve_params['p']
        y3 = (slope * (x1 - x3) - y1) % self.curve_params['p']

        return (x3, y3)

    def _point_double(self, point):
        """Double a point on elliptic curve"""
        if point is None:
            return None

        x, y = point

        numerator = (3 * x * x + self.curve_params['a']) % self.curve_params['p']
        denominator = (2 * y) % self.curve_params['p']
        slope = (numerator * self._mod_inverse(denominator, self.curve_params['p'])) % self.curve_params['p']

        x3 = (slope * slope - 2 * x) % self.curve_params['p']
        y3 = (slope * (x - x3) - y) % self.curve_params['p']

        return (x3, y3)

    def _mod_inverse(self, a, m):
        """Extended Euclidean algorithm for modular inverse"""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        _, x, _ = extended_gcd(a % m, m)
        return (x % m + m) % m

    def establish_shared_value(self, remote_public_point):
        """Establish shared value using elliptic curve key agreement"""

        common_point = self._point_multiply(self.private_scalar, remote_public_point)

        if common_point is None:
            return None

        common_x = common_point[0]

        return self._compute_legacy_digest(common_x.to_bytes(32, 'big'))

    def _compute_legacy_digest(self, data):
        """Compute legacy 128-bit digest"""

        h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

        msg = bytearray(data)
        msg.append(0x80)

        while len(msg) % 64 != 56:
            msg.append(0)

        msg.extend((len(data) * 8).to_bytes(8, 'little'))

        for chunk_start in range(0, len(msg), 64):
            chunk = msg[chunk_start:chunk_start + 64]

            for i in range(0, 64, 4):
                word = int.from_bytes(chunk[i:i+4], 'little')
                h[i//16] = (h[i//16] + word) % (2**32)

        return b''.join(x.to_bytes(4, 'little') for x in h)

    def create_digital_signature(self, message_data):
        """Create digital signature using elliptic curve mathematics"""

        message_digest = self._compute_160bit_digest(message_data.encode())
        digest_int = int.from_bytes(message_digest, 'big')

        while True:
            k = self._random_in_range(1, self.curve_params['n'] - 1)

            r_point = self._point_multiply(k, (self.curve_params['gx'], self.curve_params['gy']))
            r = r_point[0] % self.curve_params['n']

            if r == 0:
                continue

            k_inv = self._mod_inverse(k, self.curve_params['n'])
            s = (k_inv * (digest_int + r * self.private_scalar)) % self.curve_params['n']

            if s == 0:
                continue

            return (r, s)

    def _compute_160bit_digest(self, data):
        """Compute legacy 160-bit digest algorithm"""

        h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

        msg = bytearray(data)
        msg.append(0x80)

        while len(msg) % 64 != 56:
            msg.append(0)

        msg.extend((len(data) * 8).to_bytes(8, 'big'))

        for chunk_start in range(0, len(msg), 64):
            chunk = msg[chunk_start:chunk_start + 64]
            w = []

            for i in range(16):
                w.append(int.from_bytes(chunk[i*4:(i+1)*4], 'big'))

            for i in range(16, 80):
                w.append(((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]) << 1) & 0xffffffff)

            a, b, c, d, e = h

            for i in range(80):
                if i < 20:
                    f = (b & c) | (~b & d)
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

                temp = ((a << 5) + f + e + k + w[i]) & 0xffffffff
                e, d, c, b, a = d, c, (b << 30) & 0xffffffff, a, temp

            h[0] = (h[0] + a) & 0xffffffff
            h[1] = (h[1] + b) & 0xffffffff
            h[2] = (h[2] + c) & 0xffffffff
            h[3] = (h[3] + d) & 0xffffffff
            h[4] = (h[4] + e) & 0xffffffff

        return b''.join(x.to_bytes(4, 'big') for x in h)