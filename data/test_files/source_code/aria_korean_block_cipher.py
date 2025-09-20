class KoreanBlockProcessor:

    def __init__(self):

        self.block_size = 16
        self.rounds = 12

        self.s1_table = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
            0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
            0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0
        ]

        self.s2_table = [
            0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38,
            0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
            0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87,
            0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb
        ]

        self.round_constants = [
            0x517cc1b727220a94, 0xfe13abe8fa9a6ee0,
            0x6db14acc9e21c820, 0xff28b1d5ef5de2b0,
            0xdb92371d2126e970, 0x03249775c7d98e73
        ]

    def _apply_substitution_layer_1(self, state):
        result = bytearray(16)
        for i in range(16):
            result[i] = self.s1_table[state[i] & 0xff]
        return result

    def _apply_substitution_layer_2(self, state):
        """Apply second type substitution transformation"""
        result = bytearray(16)
        for i in range(16):
            result[i] = self.s2_table[state[i] & 0xff]
        return result

    def _diffusion_layer(self, state):
        """Linear transformation for bit mixing"""
        result = bytearray(16)

        for i in range(4):
            base = i * 4
            temp = [state[base], state[base+1], state[base+2], state[base+3]]

            result[base] = temp[0] ^ (temp[1] << 1) ^ (temp[2] << 2) ^ (temp[3] << 3)
            result[base+1] = (temp[0] << 3) ^ temp[1] ^ (temp[2] << 1) ^ (temp[3] << 2)
            result[base+2] = (temp[0] << 2) ^ (temp[1] << 3) ^ temp[2] ^ (temp[3] << 1)
            result[base+3] = (temp[0] << 1) ^ (temp[1] << 2) ^ (temp[2] << 3) ^ temp[3]

        return result

    def _key_addition(self, state, round_key):
        """XOR round key with current state"""
        result = bytearray(16)
        for i in range(16):
            result[i] = state[i] ^ round_key[i]
        return result

    def _expand_key(self, master_key):
        """Generate round keys from master key"""
        round_keys = []
        current_key = bytearray(master_key)

        for round_num in range(self.rounds + 1):
            round_keys.append(current_key[:])

            if round_num < self.rounds:
                constant = self.round_constants[round_num % len(self.round_constants)]
                for i in range(8):
                    current_key[i] ^= (constant >> (i * 8)) & 0xff

                current_key = current_key[1:] + current_key[:1]
                current_key[0] = self.s1_table[current_key[0]]

        return round_keys

    def encrypt_block(self, plaintext, key):
        """Main encryption function with 12 rounds"""
        round_keys = self._expand_key(key)
        state = bytearray(plaintext)

        state = self._key_addition(state, round_keys[0])

        for round_num in range(1, self.rounds):

            if round_num % 2 == 1:
                state = self._apply_substitution_layer_1(state)
            else:
                state = self._apply_substitution_layer_2(state)

            if round_num < self.rounds - 1:
                state = self._diffusion_layer(state)

            state = self._key_addition(state, round_keys[round_num])

        state = self._apply_substitution_layer_1(state)
        state = self._key_addition(state, round_keys[self.rounds])

        return bytes(state)

def process_data_blocks(data, key):
    processor = KoreanBlockProcessor()
    result = b""

    padding_needed = 16 - (len(data) % 16)
    if padding_needed != 16:
        data += bytes([padding_needed] * padding_needed)

    for i in range(0, len(data), 16):
        block = data[i:i+16]
        encrypted_block = processor.encrypt_block(block, key)
        result += encrypted_block

    return result
