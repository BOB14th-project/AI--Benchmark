"""
High-speed mobile payment cipher
ARX (Add-Rotate-XOR) design for software efficiency
"""

class MobilePaymentARXCipher:
    """ARX-based cipher optimized for mobile processors"""

    def __init__(self, key_size=128):
        self.block_size = 16  # 128 bits
        self.key_size = key_size // 8

        # Determine rounds based on key size
        if key_size == 128:
            self.rounds = 24
        elif key_size == 192:
            self.rounds = 28
        elif key_size == 256:
            self.rounds = 32
        else:
            raise ValueError("Key size must be 128, 192, or 256 bits")

        # Rotation constants for ARX operations
        self.rotation_left = [9, 5, 3]
        self.rotation_right = [9, 5, 3]

        # Delta constant for key schedule
        self.delta = [0xc3efe9db, 0x44626b02, 0x79e27c8a, 0x78df30ec]

    def _rotl32(self, value, shift):
        """32-bit left rotation"""
        return ((value << shift) | (value >> (32 - shift))) & 0xffffffff

    def _rotr32(self, value, shift):
        """32-bit right rotation"""
        return ((value >> shift) | (value << (32 - shift))) & 0xffffffff

    def generate_round_keys(self, master_key):
        """
        Generate round keys using ARX operations
        Very fast key schedule
        """
        # Split key into 32-bit words
        key_words = []
        for i in range(0, len(master_key), 4):
            word = int.from_bytes(master_key[i:i+4], 'little')
            key_words.append(word)

        round_keys = []

        for round_num in range(self.rounds):
            # Generate 6 words per round using ARX
            rk = []
            for i in range(6):
                temp = key_words[i % len(key_words)]

                # Add delta
                temp = (temp + self.delta[i % 4]) & 0xffffffff

                # Rotate
                temp = self._rotl32(temp, self.rotation_left[i % 3])

                # XOR with round number
                temp ^= round_num

                rk.append(temp)

                # Update key state
                key_words[i % len(key_words)] = temp

            round_keys.append(rk)

        return round_keys

    def arx_round_function(self, state, round_keys):
        """
        Single ARX round
        Only uses: Addition, Rotation, XOR (no S-boxes!)
        """
        # Split state into four 32-bit words
        s0 = int.from_bytes(state[0:4], 'little')
        s1 = int.from_bytes(state[4:8], 'little')
        s2 = int.from_bytes(state[8:12], 'little')
        s3 = int.from_bytes(state[12:16], 'little')

        # ARX operations
        # Step 1: Add
        s0 = (s0 + round_keys[0]) & 0xffffffff
        s1 = (s1 + round_keys[1]) & 0xffffffff

        # Step 2: Rotate
        s0 = self._rotl32(s0, self.rotation_left[0])
        s1 = self._rotl32(s1, self.rotation_left[1])

        # Step 3: XOR
        s0 ^= round_keys[2]
        s1 ^= round_keys[3]

        # Step 4: Mix
        s2 = (s2 + s0) & 0xffffffff
        s3 = (s3 + s1) & 0xffffffff

        # Step 5: More rotation
        s2 = self._rotl32(s2, self.rotation_left[2])
        s3 = self._rotr32(s3, self.rotation_right[0])

        # Step 6: Final XOR
        s2 ^= round_keys[4]
        s3 ^= round_keys[5]

        # Reconstruct state
        result = bytearray(16)
        result[0:4] = s0.to_bytes(4, 'little')
        result[4:8] = s1.to_bytes(4, 'little')
        result[8:12] = s2.to_bytes(4, 'little')
        result[12:16] = s3.to_bytes(4, 'little')

        return result

    def encrypt_block(self, plaintext, key):
        """
        Encrypt block using ARX structure
        Extremely fast in software (no table lookups)
        """
        round_keys = self.generate_round_keys(key)
        state = bytearray(plaintext)

        # Execute all rounds
        for round_num in range(self.rounds):
            state = self.arx_round_function(state, round_keys[round_num])

        return bytes(state)

def encrypt_payment_transaction(transaction_data, app_key):
    """Encrypt mobile payment transaction at high speed"""
    cipher = MobilePaymentARXCipher(key_size=len(app_key) * 8)

    # Pad to block size
    padding = 16 - (len(transaction_data) % 16)
    if padding != 16:
        transaction_data += bytes([padding] * padding)

    # Encrypt blocks
    encrypted = b""
    for i in range(0, len(transaction_data), 16):
        block = transaction_data[i:i+16]
        encrypted += cipher.encrypt_block(block, app_key)

    return encrypted

if __name__ == "__main__":
    # Mobile payment example
    app_secret_key = b"PaymentAppKey123"  # 128-bit
    transaction = b"Payment: $100.00 to Merchant #12345"

    encrypted = encrypt_payment_transaction(transaction, app_secret_key)
    print(f"Encrypted transaction: {encrypted.hex()}")
    print("ARX cipher provides very fast encryption on mobile devices!")
