class KoreanFinancialProcessor:

    def __init__(self):

        self.block_size = 16
        self.rounds = 12

        self.kfss_constants = [
            0x517cc1b7, 0x27220a94, 0xfe13abe8, 0xfa9a6ee0,
            0x6db14acc, 0x9e21c820, 0xff28b1d5, 0xef5de2b0,
            0xdb92371d, 0x2126e970, 0x03249775, 0xc7d98e73
        ]

        self.domestic_s1 = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
            0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
            0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0
        ]

        self.domestic_s2 = [
            0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38,
            0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
            0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87,
            0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb
        ]

    def _apply_domestic_substitution(self, state, round_num):
        result = bytearray(16)
        if round_num % 2 == 1:

            for i in range(16):
                result[i] = self.domestic_s1[state[i]]
        else:

            for i in range(16):
                result[i] = self.domestic_s2[state[i]]
        return result

    def _korean_diffusion_layer(self, state):
        result = bytearray(16)

        for i in range(4):
            base = i * 4
            col = [state[base], state[base+1], state[base+2], state[base+3]]

            result[base] = self._gf_multiply(0x02, col[0]) ^ self._gf_multiply(0x03, col[1]) ^ col[2] ^ col[3]
            result[base+1] = col[0] ^ self._gf_multiply(0x02, col[1]) ^ self._gf_multiply(0x03, col[2]) ^ col[3]
            result[base+2] = col[0] ^ col[1] ^ self._gf_multiply(0x02, col[2]) ^ self._gf_multiply(0x03, col[3])
            result[base+3] = self._gf_multiply(0x03, col[0]) ^ col[1] ^ col[2] ^ self._gf_multiply(0x02, col[3])

        return result

    def _gf_multiply(self, a, b):
        result = 0
        while a and b:
            if b & 1:
                result ^= a
            if a & 0x80:
                a = (a << 1) ^ 0x1b
            else:
                a <<= 1
            b >>= 1
            a &= 0xff
        return result

    def _korean_key_schedule(self, master_key):
        round_keys = []
        current = bytearray(master_key)

        for round_num in range(self.rounds + 1):
            round_keys.append(current[:])

            if round_num < self.rounds:

                constant = self.kfss_constants[round_num % len(self.kfss_constants)]
                for i in range(4):
                    current[i] ^= (constant >> (8 * i)) & 0xff

                temp = current[0]
                for i in range(15):
                    current[i] = current[i + 1]
                current[15] = temp

                current[0] = self.domestic_s1[current[0]]

        return round_keys

    def process_financial_block(self, plaintext, key):
        round_keys = self._korean_key_schedule(key)
        state = bytearray(plaintext)

        for i in range(16):
            state[i] ^= round_keys[0][i]

        for round_num in range(1, self.rounds):

            state = self._apply_domestic_substitution(state, round_num)

            if round_num < self.rounds - 1:
                state = self._korean_diffusion_layer(state)

            for i in range(16):
                state[i] ^= round_keys[round_num][i]

        state = self._apply_domestic_substitution(state, self.rounds)
        for i in range(16):
            state[i] ^= round_keys[self.rounds][i]

        return bytes(state)

class GovernmentApprovedHasher:

    def __init__(self):

        self.digest_size = 32

        self.initial_state = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]

        self.round_constants = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174
        ]

    def _ch_function(self, x, y, z):
        return (x & y) ^ (~x & z)

    def _maj_function(self, x, y, z):
        return (x & y) ^ (x & z) ^ (y & z)

    def _sigma0(self, x):
        return self._rotr(x, 2) ^ self._rotr(x, 13) ^ self._rotr(x, 22)

    def _sigma1(self, x):
        return self._rotr(x, 6) ^ self._rotr(x, 11) ^ self._rotr(x, 25)

    def _gamma0(self, x):
        return self._rotr(x, 7) ^ self._rotr(x, 18) ^ (x >> 3)

    def _gamma1(self, x):
        return self._rotr(x, 17) ^ self._rotr(x, 19) ^ (x >> 10)

    def _rotr(self, value, amount):
        return ((value >> amount) | (value << (32 - amount))) & 0xffffffff

    def _process_message_block(self, block, state):

        w = list(struct.unpack('>16I', block))

        for i in range(16, 64):
            s0 = self._gamma0(w[i-15])
            s1 = self._gamma1(w[i-2])
            w.append((w[i-16] + s0 + w[i-7] + s1) & 0xffffffff)

        a, b, c, d, e, f, g, h = state

        for i in range(64):
            s1 = self._sigma1(e)
            ch = self._ch_function(e, f, g)
            temp1 = (h + s1 + ch + self.round_constants[i % 16] + w[i]) & 0xffffffff
            s0 = self._sigma0(a)
            maj = self._maj_function(a, b, c)
            temp2 = (s0 + maj) & 0xffffffff

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff

        return [
            (state[0] + a) & 0xffffffff,
            (state[1] + b) & 0xffffffff,
            (state[2] + c) & 0xffffffff,
            (state[3] + d) & 0xffffffff,
            (state[4] + e) & 0xffffffff,
            (state[5] + f) & 0xffffffff,
            (state[6] + g) & 0xffffffff,
            (state[7] + h) & 0xffffffff
        ]

    def compute_government_digest(self, message):
        """Compute message digest for government use"""
        import struct

        state = self.initial_state[:]

        msg_len = len(message)
        message += b'\x80'

        while len(message) % 64 != 56:
            message += b'\x00'

        message += struct.pack('>Q', msg_len * 8)

        for i in range(0, len(message), 64):
            block = message[i:i+64]
            state = self._process_message_block(block, state)

        return struct.pack('>8I', *state)

class KoreanPublicKeyProcessor:

    def __init__(self, curve_type="korean_standard"):
        if curve_type == "korean_standard":

            self.p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
            self.a = 0
            self.b = 7
            self.n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

            self.gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
            self.gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

    def _mod_inverse(self, a, m):
        if a < 0:
            a = (a % m + m) % m

        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        gcd, x, _ = extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m

    def _point_double(self, px, py):
        """Double a point on elliptic curve"""
        if py == 0:
            return None, None

        s = (3 * px * px + self.a) * self._mod_inverse(2 * py, self.p) % self.p

        rx = (s * s - 2 * px) % self.p
        ry = (s * (px - rx) - py) % self.p

        return rx, ry

    def _point_add(self, px, py, qx, qy):
        if px is None:
            return qx, qy
        if qx is None:
            return px, py

        if px == qx:
            if py == qy:
                return self._point_double(px, py)
            else:
                return None, None

        s = (qy - py) * self._mod_inverse(qx - px, self.p) % self.p

        rx = (s * s - px - qx) % self.p
        ry = (s * (px - rx) - py) % self.p

        return rx, ry

    def _scalar_multiply(self, k, px, py):
        """Scalar multiplication using double-and-add"""
        if k == 0:
            return None, None

        result_x, result_y = None, None
        addend_x, addend_y = px, py

        while k:
            if k & 1:
                result_x, result_y = self._point_add(result_x, result_y, addend_x, addend_y)
            addend_x, addend_y = self._point_double(addend_x, addend_y)
            k >>= 1

        return result_x, result_y

    def generate_keypair(self):
        import secrets

        private_key = secrets.randbelow(self.n - 1) + 1

        public_x, public_y = self._scalar_multiply(private_key, self.gx, self.gy)

        return private_key, (public_x, public_y)

    def sign_message(self, message_hash, private_key):
        import secrets

        z = int.from_bytes(message_hash[:32], 'big')

        while True:

            k = secrets.randbelow(self.n - 1) + 1

            r_x, _ = self._scalar_multiply(k, self.gx, self.gy)
            r = r_x % self.n

            if r == 0:
                continue

            k_inv = self._mod_inverse(k, self.n)
            s = (k_inv * (z + r * private_key)) % self.n

            if s == 0:
                continue

            return (r, s)

def process_government_data(data, operation_type="encrypt"):
    if operation_type == "encrypt":
        processor = KoreanFinancialProcessor()
        key = b"GovernmentKey123"

        padding_needed = 16 - (len(data) % 16)
        if padding_needed != 16:
            data += bytes([padding_needed] * padding_needed)

        result = b""
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            encrypted_block = processor.process_financial_block(block, key)
            result += encrypted_block

        return result

    elif operation_type == "hash":
        hasher = GovernmentApprovedHasher()
        return hasher.compute_government_digest(data)

    elif operation_type == "digital_signature":
        ecc_processor = KoreanPublicKeyProcessor()
        hasher = GovernmentApprovedHasher()

        message_hash = hasher.compute_government_digest(data)

        private_key, public_key = ecc_processor.generate_keypair()

        signature = ecc_processor.sign_message(message_hash, private_key)

        return {
            'signature': signature,
            'public_key': public_key,
            'message_hash': message_hash
        }