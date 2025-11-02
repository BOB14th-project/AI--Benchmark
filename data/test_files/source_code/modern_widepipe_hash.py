"""
Modern hash function with wide-pipe design
Multiple output sizes: 224, 256, 384, 512 bits
"""

class ModernWid

ePipeHash:
    """Wide-pipe hash with novel compression function"""

    def __init__(self, output_size=256):
        if output_size not in [224, 256, 384, 512]:
            raise ValueError("Output size must be 224, 256, 384, or 512 bits")

        self.output_size = output_size
        self.digest_bytes = output_size // 8

        # Wide internal state (larger than output)
        if output_size <= 256:
            self.state_size = 16  # 512-bit internal state
            self.message_block_size = 128
        else:
            self.state_size = 32  # 1024-bit internal state
            self.message_block_size = 256

        # Step constants for compression
        self.step_constants = self._generate_step_constants()

    def _generate_step_constants(self):
        """Generate constants for step function"""
        constants = []
        for i in range(32):
            # Pseudo-random constants
            c = (0x428a2f98 + i * 0x71374491) & 0xffffffff
            constants.append(c)
        return constants

    def _mix_function(self, a, b, c):
        """Novel mixing function"""
        result = (a ^ b) + c
        result ^= (result >> 16)
        result = (result * 0x85ebca6b) & 0xffffffff
        result ^= (result >> 13)
        result = (result * 0xc2b2ae35) & 0xffffffff
        result ^= (result >> 16)
        return result & 0xffffffff

    def _step_function(self, state, msg_word, step_num):
        """
        Single step of compression function
        Different from SHA-2/SHA-3 design
        """
        new_state = []

        for i in range(len(state)):
            # Novel transformation
            temp = state[i]
            temp ^= msg_word
            temp = self._mix_function(temp, self.step_constants[step_num % 32], i)

            # Mix with neighbors
            if i > 0:
                temp ^= state[i-1]
            if i < len(state) - 1:
                temp = (temp + state[(i+1) % len(state)]) & 0xffffffff

            new_state.append(temp)

        return new_state

    def _message_expansion(self, message_block):
        """
        Expand message block
        Proprietary design different from SHA families
        """
        # Convert block to words
        words = []
        for i in range(0, len(message_block), 4):
            word = int.from_bytes(message_block[i:i+4], 'little')
            words.append(word)

        # Expand (different from SHA-2 expansion)
        expanded = words[:]
        for i in range(len(words), 64):
            # Novel expansion formula
            w1 = expanded[i-1]
            w2 = expanded[i-2]
            w7 = expanded[i-7]
            w16 = expanded[i-16]

            new_word = (w1 ^ w2) + (w7 ^ w16)
            new_word = self._mix_function(new_word, i, 0)
            expanded.append(new_word)

        return expanded

    def _compress_block(self, state, message_block):
        """
        Compression function with wide-pipe design
        Internal state larger than output
        """
        # Expand message
        expanded_msg = self._message_expansion(message_block)

        # Process in steps
        current_state = state[:]

        for step in range(min(len(expanded_msg), 48)):
            current_state = self._step_function(
                current_state,
                expanded_msg[step],
                step
            )

        # Combine with original state (Davies-Meyer style)
        for i in range(len(state)):
            state[i] = (state[i] + current_state[i]) & 0xffffffff

        return state

    def hash(self, message):
        """
        Compute hash with wide-pipe design
        Supports 224/256/384/512-bit outputs
        """
        # Initialize state based on output size
        state = []
        for i in range(self.state_size):
            init_val = (0x6a09e667 + i * 0xbb67ae85) & 0xffffffff
            state.append(init_val)

        # Padding
        msg_len = len(message)
        message += b'\x80'
        while (len(message) % self.message_block_size) != (self.message_block_size - 16):
            message += b'\x00'
        message += (msg_len * 8).to_bytes(16, 'little')

        # Process blocks
        for i in range(0, len(message), self.message_block_size):
            block = message[i:i+self.message_block_size]
            state = self._compress_block(state, block)

        # Truncate state to output size
        digest = b''
        words_needed = self.digest_bytes // 4
        for i in range(words_needed):
            digest += state[i].to_bytes(4, 'little')

        return digest[:self.digest_bytes]

def hash_blockchain_transaction(transaction, hash_size=256):
    """Hash blockchain transaction with modern hash function"""
    hasher = ModernWidePipeHash(output_size=hash_size)
    return hasher.hash(transaction)

if __name__ == "__main__":
    # Blockchain hashing example
    transaction = b"Transaction: Alice sends 5 BTC to Bob at block height 750000"

    # Hash with different sizes
    hash_256 = hash_blockchain_transaction(transaction, 256)
    print(f"256-bit hash: {hash_256.hex()}")

    hash_512 = hash_blockchain_transaction(transaction, 512)
    print(f"512-bit hash: {hash_512.hex()}")

    print("Wide-pipe design provides better security margin!")
