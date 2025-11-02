"""
Banking-grade 128-bit block cipher implementation
Used in Korean financial institutions for secure transactions
"""

class BankingBlockCipher:
    """16-round Feistel network cipher for banking security"""

    def __init__(self):
        # 128-bit block size (16 bytes)
        self.block_size = 128 // 8
        self.rounds = 16

        # Four substitution boxes as per banking standard
        self.ss0 = self._init_sbox_0()
        self.ss1 = self._init_sbox_1()
        self.ss2 = self._init_sbox_2()
        self.ss3 = self._init_sbox_3()

        # Key constants for round key generation
        self.KC = [
            0x9e3779b9, 0x3c6ef373, 0x78dde6e6, 0xf1bbcdcc,
            0xe3779b99, 0xc6ef3733, 0x8dde6e67, 0x1bbcdccf
        ]

    def _init_sbox_0(self):
        """Initialize substitution box 0"""
        return [
            0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0,
            0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0,
        ]

    def _init_sbox_1(self):
        """Initialize substitution box 1"""
        return [
            0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3,
            0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd,
        ]

    def _init_sbox_2(self):
        """Initialize substitution box 2"""
        return [
            0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0,
            0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0,
        ]

    def _init_sbox_3(self):
        """Initialize substitution box 3"""
        return [
            0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3,
            0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd,
        ]

    def f_function(self, right_half, round_key):
        """Feistel F-function with S-box substitution"""
        temp = right_half ^ round_key

        # Split into bytes
        b0 = temp & 0xff
        b1 = (temp >> 8) & 0xff
        b2 = (temp >> 16) & 0xff
        b3 = (temp >> 24) & 0xff

        # S-box substitution
        s0 = self.ss0[b0 % len(self.ss0)]
        s1 = self.ss1[b1 % len(self.ss1)]
        s2 = self.ss2[b2 % len(self.ss2)]
        s3 = self.ss3[b3 % len(self.ss3)]

        # Combine and mix
        result = s0 ^ s1 ^ s2 ^ s3
        result ^= (result << 8) | (result >> 24)

        return result & 0xffffffff

    def generate_round_keys(self, master_key):
        """Generate 16 round keys from master key"""
        round_keys = []
        key_words = [
            int.from_bytes(master_key[i:i+4], 'big')
            for i in range(0, 16, 4)
        ]

        for round_num in range(self.rounds):
            if round_num < 4:
                rk = key_words[round_num]
            else:
                temp = key_words[(round_num - 1) % 4] ^ key_words[(round_num - 4) % 4]
                temp ^= self.KC[round_num % len(self.KC)]
                temp = ((temp << 1) | (temp >> 31)) & 0xffffffff
                key_words[round_num % 4] = temp
                rk = temp
            round_keys.append(rk)

        return round_keys

    def encrypt_block(self, plaintext, key):
        """Encrypt 128-bit block using 16-round Feistel network"""
        round_keys = self.generate_round_keys(key)

        # Split into left and right halves (64 bits each)
        left = int.from_bytes(plaintext[:8], 'big')
        right = int.from_bytes(plaintext[8:16], 'big')

        # 16 Feistel rounds
        for round_num in range(self.rounds):
            f_output = self.f_function(right, round_keys[round_num])
            new_left = right
            new_right = left ^ f_output
            left, right = new_left, new_right

        # Combine halves
        ciphertext = left.to_bytes(8, 'big') + right.to_bytes(8, 'big')
        return ciphertext

def encrypt_banking_data(data, key):
    """Encrypt sensitive banking data using Korean banking standard"""
    cipher = BankingBlockCipher()

    # Pad data to block size
    padding_length = 16 - (len(data) % 16)
    if padding_length != 16:
        data += bytes([padding_length] * padding_length)

    # Encrypt each block
    encrypted = b""
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        encrypted += cipher.encrypt_block(block, key)

    return encrypted

if __name__ == "__main__":
    # Example: Encrypt customer account data
    secret_key = b"BankMasterKey123"  # 16 bytes = 128 bits
    customer_data = b"Account: 1234567890, Balance: $50000"

    encrypted = encrypt_banking_data(customer_data, secret_key)
    print(f"Encrypted banking data: {encrypted.hex()}")
