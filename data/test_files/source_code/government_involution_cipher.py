"""
Government-approved involution cipher
SPN structure with dual substitution layers
"""

class GovernmentInvolutionCipher:
    """Involutional SPN cipher for government communications"""

    def __init__(self, key_size=128):
        self.block_size = 16  # 128 bits
        self.key_size = key_size // 8

        # Determine rounds based on key size
        if key_size == 128:
            self.rounds = 12
        elif key_size == 192:
            self.rounds = 14
        elif key_size == 256:
            self.rounds = 16
        else:
            raise ValueError("Key size must be 128, 192, or 256 bits")

        # Dual substitution layers - characteristic of involution design
        self.substitution_layer_1 = self._create_sbox_type1()
        self.substitution_layer_2 = self._create_sbox_type2()

        # Round constants for key expansion
        self.round_constants = [
            0x517cc1b727220a94, 0xfe13abe8fa9a6ee0,
            0x6db14acc9e21c820, 0xff28b1d5ef5de2b0,
            0xdb92371d2126e970, 0x03249775c7d98e73,
            0x1a8b5f2c9e47d360, 0x8f6d3a1c5b2e9047
        ]

    def _create_sbox_type1(self):
        """First type substitution box"""
        return [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
            0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
            0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0
        ]

    def _create_sbox_type2(self):
        """Second type substitution box"""
        return [
            0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38,
            0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
            0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87,
            0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb
        ]

    def apply_substitution_layer_1(self, state):
        """Apply first substitution layer"""
        result = bytearray(16)
        for i in range(16):
            result[i] = self.substitution_layer_1[state[i] % len(self.substitution_layer_1)]
        return result

    def apply_substitution_layer_2(self, state):
        """Apply second substitution layer"""
        result = bytearray(16)
        for i in range(16):
            result[i] = self.substitution_layer_2[state[i] % len(self.substitution_layer_2)]
        return result

    def diffusion_layer(self, state):
        """Linear diffusion transformation"""
        result = bytearray(16)

        # Mix each 4-byte word
        for word in range(4):
            base = word * 4
            t0, t1, t2, t3 = state[base:base+4]

            # Linear mixing operations
            result[base] = t0 ^ (t1 << 1) ^ (t2 << 2) ^ (t3 << 3)
            result[base+1] = (t0 << 3) ^ t1 ^ (t2 << 1) ^ (t3 << 2)
            result[base+2] = (t0 << 2) ^ (t1 << 3) ^ t2 ^ (t3 << 1)
            result[base+3] = (t0 << 1) ^ (t1 << 2) ^ (t2 << 3) ^ t3

            # Keep values in byte range
            result[base] &= 0xff
            result[base+1] &= 0xff
            result[base+2] &= 0xff
            result[base+3] &= 0xff

        return result

    def add_round_key(self, state, round_key):
        """XOR state with round key"""
        result = bytearray(16)
        for i in range(16):
            result[i] = state[i] ^ round_key[i]
        return result

    def expand_key(self, master_key):
        """Expand master key to round keys"""
        round_keys = []
        current_key = bytearray(master_key)

        for round_num in range(self.rounds + 1):
            round_keys.append(current_key[:])

            if round_num < self.rounds:
                # Apply round constant
                rc = self.round_constants[round_num % len(self.round_constants)]
                for i in range(8):
                    current_key[i] ^= (rc >> (i * 8)) & 0xff

                # Rotate and substitute
                current_key = current_key[1:] + current_key[:1]
                current_key[0] = self.substitution_layer_1[current_key[0]]

        return round_keys

    def encrypt_block(self, plaintext, key):
        """
        Encrypt block using involution SPN structure
        Key feature: encryption and decryption use same structure
        """
        round_keys = self.expand_key(key)
        state = bytearray(plaintext)

        # Initial round key addition
        state = self.add_round_key(state, round_keys[0])

        # Main rounds
        for round_num in range(1, self.rounds):
            # Alternate between two substitution layers
            if round_num % 2 == 1:
                state = self.apply_substitution_layer_1(state)
            else:
                state = self.apply_substitution_layer_2(state)

            # Diffusion (skip in last round)
            if round_num < self.rounds - 1:
                state = self.diffusion_layer(state)

            # Round key addition
            state = self.add_round_key(state, round_keys[round_num])

        # Final substitution and key addition
        state = self.apply_substitution_layer_1(state)
        state = self.add_round_key(state, round_keys[self.rounds])

        return bytes(state)

def encrypt_classified_document(document, key):
    """Encrypt classified government documents"""
    cipher = GovernmentInvolutionCipher(key_size=len(key) * 8)

    # Pad to block size
    padding = 16 - (len(document) % 16)
    if padding != 16:
        document += bytes([padding] * padding)

    # Encrypt blocks
    encrypted = b""
    for i in range(0, len(document), 16):
        block = document[i:i+16]
        encrypted += cipher.encrypt_block(block, key)

    return encrypted

if __name__ == "__main__":
    # Encrypt top-secret government document
    secret_key = b"GovSecretKey2024"  # 128-bit key
    classified_doc = b"TOP SECRET: Military deployment coordinates"

    encrypted = encrypt_classified_document(classified_doc, secret_key)
    print(f"Encrypted government data: {encrypted.hex()}")
