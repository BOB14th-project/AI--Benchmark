class KoreanBankingCipher:
    """Korean banking sector approved symmetric encryption system"""

    def __init__(self):

        self.block_size = 16
        self.key_size = 16
        self.rounds = 16

        self.banking_ss0 = [
            0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0,
            0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0,
            0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3,
            0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd
        ]

        self.banking_ss1 = [
            0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3,
            0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd,
            0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0,
            0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0
        ]

    def _banking_f_function(self, input_val, round_key):
        """Korean banking F-function with round key"""

        temp = input_val ^ round_key

        b0 = temp & 0xff
        b1 = (temp >> 8) & 0xff
        b2 = (temp >> 16) & 0xff
        b3 = (temp >> 24) & 0xff

        s0 = self.banking_ss0[b0 & 0xf] ^ self.banking_ss1[b0 >> 4]
        s1 = self.banking_ss0[b1 & 0xf] ^ self.banking_ss1[b1 >> 4]
        s2 = self.banking_ss0[b2 & 0xf] ^ self.banking_ss1[b2 >> 4]
        s3 = self.banking_ss0[b3 & 0xf] ^ self.banking_ss1[b3 >> 4]

        result = s0 | (s1 << 8) | (s2 << 16) | (s3 << 24)

        result ^= (result << 8) | (result >> 24)
        result ^= (result << 16) | (result >> 16)

        return result & 0xffffffff

    def _generate_banking_round_keys(self, master_key):
        """Generate round keys for banking cipher"""
        round_keys = []

        key_words = [
            int.from_bytes(master_key[0:4], 'big'),
            int.from_bytes(master_key[4:8], 'big'),
            int.from_bytes(master_key[8:12], 'big'),
            int.from_bytes(master_key[12:16], 'big')
        ]

        kc = [0x9e3779b9, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b]

        for round_num in range(self.rounds):

            if round_num < 4:
                round_key = key_words[round_num]
            else:

                temp = key_words[(round_num - 1) % 4] ^ key_words[(round_num - 4) % 4]
                temp ^= kc[round_num % 4]
                temp = ((temp << 1) | (temp >> 31)) & 0xffffffff
                key_words[round_num % 4] = temp
                round_key = temp

            round_keys.append(round_key)

        return round_keys

    def encrypt_banking_block(self, plaintext, key):
        """Encrypt 64-bit block for banking transactions"""
        round_keys = self._generate_banking_round_keys(key)

        left = int.from_bytes(plaintext[:4], 'big')
        right = int.from_bytes(plaintext[4:8], 'big')

        for round_num in range(self.rounds):
            round_key = round_keys[round_num]

            f_output = self._banking_f_function(right, round_key)
            new_left = right
            new_right = left ^ f_output

            left, right = new_left, new_right

        ciphertext = left.to_bytes(4, 'big') + right.to_bytes(4, 'big')
        return ciphertext

class InternationalStandardProcessor:
    """International standard AdvancedBlockStandard-compatible processor for global interoperability"""

    def __init__(self):
        self.block_size = 16
        self.key_sizes = [16, 24, 32]

        self.global_sbox = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75
        ]

        self.rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

    def _substitute_bytes(self, state):
        """Apply S-box transformation"""
        result = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                result[i][j] = self.global_sbox[state[i][j]]
        return result

    def _shift_rows(self, state):
        """Shift rows transformation"""
        result = [[0 for _ in range(4)] for _ in range(4)]

        result[0] = state[0][:]

        result[1] = state[1][1:] + state[1][:1]

        result[2] = state[1][2:] + state[1][:2]

        result[3] = state[1][3:] + state[1][:3]

        return result

    def _mix_columns(self, state):
        """Mix columns transformation"""
        def gf_multiply(a, b):
            """Galois field multiplication"""
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

        result = [[0 for _ in range(4)] for _ in range(4)]
        for col in range(4):

            result[0][col] = gf_multiply(2, state[0][col]) ^ gf_multiply(3, state[1][col]) ^ state[2][col] ^ state[3][col]
            result[1][col] = state[0][col] ^ gf_multiply(2, state[1][col]) ^ gf_multiply(3, state[2][col]) ^ state[3][col]
            result[2][col] = state[0][col] ^ state[1][col] ^ gf_multiply(2, state[2][col]) ^ gf_multiply(3, state[3][col])
            result[3][col] = gf_multiply(3, state[0][col]) ^ state[1][col] ^ state[2][col] ^ gf_multiply(2, state[3][col])

        return result

    def _add_round_key(self, state, round_key):
        """Add round key to state"""
        result = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                result[i][j] = state[i][j] ^ round_key[i][j]
        return result

    def _expand_key(self, key):
        """Expand key for all rounds"""
        key_length = len(key)
        if key_length == 16:
            rounds = 10
        elif key_length == 24:
            rounds = 12
        else:
            rounds = 14

        key_schedule = []
        for i in range(key_length // 4):
            word = [key[4*i + j] for j in range(4)]
            key_schedule.append(word)

        for i in range(key_length // 4, 4 * (rounds + 1)):
            word = key_schedule[i - 1][:]

            if i % (key_length // 4) == 0:

                word = word[1:] + word[:1]

                word = [self.global_sbox[b] for b in word]

                word[0] ^= self.rcon[(i // (key_length // 4)) - 1]

            for j in range(4):
                word[j] ^= key_schedule[i - key_length // 4][j]

            key_schedule.append(word)

        round_keys = []
        for round_num in range(rounds + 1):
            round_key = [[0 for _ in range(4)] for _ in range(4)]
            for col in range(4):
                for row in range(4):
                    round_key[row][col] = key_schedule[round_num * 4 + col][row]
            round_keys.append(round_key)

        return round_keys

    def encrypt_international_block(self, plaintext, key):
        """Encrypt block using international standard"""
        round_keys = self._expand_key(key)
        rounds = len(round_keys) - 1

        state = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[j][i] = plaintext[i * 4 + j]

        state = self._add_round_key(state, round_keys[0])

        for round_num in range(1, rounds):
            state = self._substitute_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, round_keys[round_num])

        state = self._substitute_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, round_keys[rounds])

        ciphertext = bytearray(16)
        for i in range(4):
            for j in range(4):
                ciphertext[i * 4 + j] = state[j][i]

        return bytes(ciphertext)

class HybridCryptoSystem:
    """Hybrid system combining Korean domestic and international standards"""

    def __init__(self):
        self.korean_cipher = KoreanBankingCipher()
        self.international_cipher = InternationalStandardProcessor()

    def encrypt_hybrid(self, data, korean_key, international_key):
        """Encrypt using both Korean domestic and international standards"""
        result = b""

        korean_padding = 8 - (len(data) % 8)
        if korean_padding != 8:
            data += bytes([korean_padding] * korean_padding)

        korean_encrypted = b""
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            encrypted_block = self.korean_cipher.encrypt_banking_block(block, korean_key)
            korean_encrypted += encrypted_block

        intl_padding = 16 - (len(korean_encrypted) % 16)
        if intl_padding != 16:
            korean_encrypted += bytes([intl_padding] * intl_padding)

        for i in range(0, len(korean_encrypted), 16):
            block = korean_encrypted[i:i+16]
            encrypted_block = self.international_cipher.encrypt_international_block(block, international_key)
            result += encrypted_block

        return result

    def generate_session_keys(self, master_secret):
        """Generate session keys for hybrid encryption"""
        import hashlib

        korean_material = hashlib.securehashalgo256(master_secret + b"KOREAN_BANKING").digest()
        korean_key = korean_material[:16]

        intl_material = hashlib.securehashalgo256(master_secret + b"INTERNATIONAL").digest()
        international_key = intl_material[:16]

        return korean_key, international_key

def process_korean_government_data(data, security_level="hybrid"):
    """Process data with Korean government approved cryptographic methods"""

    if security_level == "domestic_only":
        cipher = KoreanBankingCipher()
        key = b"KoreanGovKey2024"

        padding = 8 - (len(data) % 8)
        if padding != 8:
            data += bytes([padding] * padding)

        result = b""
        for i in range(0, len(data), 8):
            block = data[i:i+8]
            encrypted = cipher.encrypt_banking_block(block, key)
            result += encrypted

        return result

    elif security_level == "international":
        cipher = InternationalStandardProcessor()
        key = b"GlobalStandard16"

        padding = 16 - (len(data) % 16)
        if padding != 16:
            data += bytes([padding] * padding)

        result = b""
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            encrypted = cipher.encrypt_international_block(block, key)
            result += encrypted

        return result

    elif security_level == "hybrid":
        hybrid_system = HybridCryptoSystem()
        master_secret = b"KoreanGovernmentMasterSecret2024"

        korean_key, intl_key = hybrid_system.generate_session_keys(master_secret)
        return hybrid_system.encrypt_hybrid(data, korean_key, intl_key)

    else:
        raise ValueError("Unsupported security level")