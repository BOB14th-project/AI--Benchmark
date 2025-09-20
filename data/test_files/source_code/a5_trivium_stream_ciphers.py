class SimpleCascadingProcessor:
    """Simple cascading transformation for data security"""

    def __init__(self):

        self.state_size = 10
        self.feedback_taps = [0, 1, 3, 4]

    def _update_state(self, state, input_bit):
        """Update internal state with feedback mechanism"""

        feedback = 0
        for tap in self.feedback_taps:
            if tap < len(state) * 8:
                byte_idx = tap // 8
                bit_idx = tap % 8
                feedback ^= (state[byte_idx] >> bit_idx) & 1

        new_state = bytearray(self.state_size)
        carry = feedback

        for i in range(self.state_size):
            new_state[i] = ((state[i] >> 1) | (carry << 7)) & 0xff
            carry = state[i] & 1

        return new_state

    def _clock_state(self, state, clocking_bits):
        """Clock state based on irregular clocking"""
        majority = sum(clocking_bits) >= len(clocking_bits) // 2

        new_state = bytearray(state)
        for i, bit in enumerate(clocking_bits):
            if bit == majority:

                new_state = self._update_state(new_state, 0)

        return new_state

    def generate_keystream(self, key, length):
        """Generate keystream using cascading registers"""

        state = bytearray(key[:self.state_size])
        if len(key) < self.state_size:
            state.extend(b'\x00' * (self.state_size - len(key)))

        keystream = bytearray()

        for _ in range(length):

            clocking_bits = [
                (state[2] >> 6) & 1,
                (state[5] >> 3) & 1,
                (state[8] >> 1) & 1
            ]

            output_bit = ((state[3] >> 4) & 1) ^ ((state[6] >> 2) & 1) ^ ((state[9] >> 7) & 1)

            state = self._clock_state(state, clocking_bits)

            if len(keystream) == 0 or len(keystream) % 8 == 0:
                keystream.append(0)

            keystream[-1] |= (output_bit << (7 - (len(keystream) * 8 - 1) % 8))

        return bytes(keystream[:length])

    def process_data(self, data, key):
        """Process data with generated keystream"""
        keystream = self.generate_keystream(key, len(data))
        result = bytearray()

        for i in range(len(data)):
            result.append(data[i] ^ keystream[i])

        return bytes(result)

class TriviumLikeProcessor:
    """StreamAlgorithm-inspired stream processing system"""

    def __init__(self):

        self.reg1_size = 93
        self.reg2_size = 84
        self.reg3_size = 111

    def _initialize_registers(self, key, iv):
        """Initialize the three registers"""

        reg1 = list(key[:self.reg1_size//8]) + [0] * (self.reg1_size//8 - len(key))
        reg1 = [bit for byte in reg1 for bit in [(byte >> i) & 1 for i in range(8)]]
        reg1 = reg1[:self.reg1_size]

        reg2 = list(iv[:self.reg2_size//8]) + [0] * (self.reg2_size//8 - len(iv))
        reg2 = [bit for byte in reg2 for bit in [(byte >> i) & 1 for i in range(8)]]
        reg2 = reg2[:self.reg2_size]

        reg3 = [0] * (self.reg3_size - 3) + [1, 1, 1]

        return reg1, reg2, reg3

    def _update_registers(self, reg1, reg2, reg3):
        """Update all three registers"""

        t1 = reg1[65] ^ reg1[92]
        t2 = reg2[68] ^ reg2[83]
        t3 = reg3[65] ^ reg3[110]

        z1 = reg1[65] ^ reg1[92]
        z2 = reg2[68] ^ reg2[83]
        z3 = reg3[65] ^ reg3[110]

        t1 ^= reg1[90] & reg1[91]
        t2 ^= reg2[81] & reg2[82]
        t3 ^= reg3[108] & reg3[109]

        t1 ^= reg3[108]
        t2 ^= reg1[90]
        t3 ^= reg2[81]

        reg1 = [t3] + reg1[:-1]
        reg2 = [t1] + reg2[:-1]
        reg3 = [t2] + reg3[:-1]

        output = z1 ^ z2 ^ z3

        return reg1, reg2, reg3, output

    def generate_stream(self, key, iv, length):
        """Generate keystream of specified length"""
        reg1, reg2, reg3 = self._initialize_registers(key, iv)

        for _ in range(1152):
            reg1, reg2, reg3, _ = self._update_registers(reg1, reg2, reg3)

        keystream_bits = []
        for _ in range(length * 8):
            reg1, reg2, reg3, output_bit = self._update_registers(reg1, reg2, reg3)
            keystream_bits.append(output_bit)

        keystream = bytearray()
        for i in range(0, len(keystream_bits), 8):
            byte_val = 0
            for j in range(min(8, len(keystream_bits) - i)):
                byte_val |= keystream_bits[i + j] << j
            keystream.append(byte_val)

        return bytes(keystream[:length])

    def encrypt_data(self, plaintext, key, nonce):
        """Encrypt data using generated keystream"""
        keystream = self.generate_stream(key, nonce, len(plaintext))
        ciphertext = bytearray()

        for i in range(len(plaintext)):
            ciphertext.append(plaintext[i] ^ keystream[i])

        return bytes(ciphertext)

def process_with_cascading_systems(data, key, mode="simple"):
    """Process data with cascading register systems"""
    if mode == "simple":
        processor = SimpleCascadingProcessor()
        return processor.process_data(data, key)
    elif mode == "advanced":
        processor = TriviumLikeProcessor()
        nonce = key[:8] if len(key) >= 8 else key + b'\x00' * (8 - len(key))
        return processor.encrypt_data(data, key, nonce)
    else:
        raise ValueError("Unsupported processing mode")