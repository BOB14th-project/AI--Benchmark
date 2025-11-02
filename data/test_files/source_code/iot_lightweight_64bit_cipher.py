"""
Lightweight 64-bit cipher for IoT devices
Optimized for low-power sensors and RFID tags
"""

class IoTLightweightCipher:
    """32-round generalized Feistel for resource-constrained devices"""

    def __init__(self):
        self.block_size = 8  # 64 bits
        self.key_size = 16   # 128 bits
        self.rounds = 32

        # Whitening key offsets
        self.wk_offset = [0, 1, 2, 3, 4, 5, 6, 7]

    def generate_whitening_keys(self, master_key):
        """Generate 8 whitening keys from master key"""
        wk = []
        for i in range(8):
            wk.append(master_key[i] ^ master_key[i + 8])
        return wk

    def generate_subkeys(self, master_key):
        """Generate 8 subkeys per round (256 total for 32 rounds)"""
        subkeys = []

        for round_num in range(self.rounds):
            round_subkeys = []
            for i in range(8):
                # Simple key schedule using rotation and XOR
                offset = (round_num * 8 + i) % 16
                sk = master_key[offset] ^ master_key[(offset + 8) % 16]
                sk ^= round_num & 0xff
                round_subkeys.append(sk)
            subkeys.append(round_subkeys)

        return subkeys

    def f0_function(self, x):
        """Simple F0 function for lightweight encryption"""
        # Rotation and XOR - efficient on 8-bit processors
        x = ((x << 1) | (x >> 7)) & 0xff
        x ^= 0x5A
        return x

    def f1_function(self, x):
        """Simple F1 function for lightweight encryption"""
        # Rotation and XOR - efficient on 8-bit processors
        x = ((x << 3) | (x >> 5)) & 0xff
        x ^= 0xA5
        return x

    def encryption_round(self, state, subkeys):
        """
        Single round of lightweight cipher
        Uses simple operations: XOR, addition, rotation
        """
        x0, x1, x2, x3, x4, x5, x6, x7 = state

        # Whitening operations
        x0 ^= subkeys[0]
        x2 += subkeys[1]
        x2 &= 0xff
        x4 ^= subkeys[2]
        x6 += subkeys[3]
        x6 &= 0xff

        # Apply lightweight F-functions
        x1 = self.f0_function(x1) ^ subkeys[4]
        x3 = self.f1_function(x3) + subkeys[5]
        x3 &= 0xff
        x5 = self.f0_function(x5) ^ subkeys[6]
        x7 = self.f1_function(x7) + subkeys[7]
        x7 &= 0xff

        return [x0, x1, x2, x3, x4, x5, x6, x7]

    def encrypt_block(self, plaintext, key):
        """
        Encrypt 64-bit block using 32-round generalized Feistel
        Designed for minimal memory and energy consumption
        """
        # Generate keys
        wk = self.generate_whitening_keys(key)
        subkeys = self.generate_subkeys(key)

        # Initialize state (8 bytes)
        state = list(plaintext)

        # Initial whitening
        for i in range(8):
            state[i] ^= wk[i]

        # 32 rounds
        for round_num in range(self.rounds):
            state = self.encryption_round(state, subkeys[round_num])

            # Rotate state for generalized Feistel
            if round_num < self.rounds - 1:
                state = state[1:] + state[:1]

        # Final whitening
        for i in range(8):
            state[i] ^= wk[(i + 4) % 8]

        return bytes(state)

def encrypt_sensor_data(sensor_reading, device_key):
    """Encrypt IoT sensor data with minimal overhead"""
    cipher = IoTLightweightCipher()

    # Pad to 64-bit blocks
    padding = 8 - (len(sensor_reading) % 8)
    if padding != 8:
        sensor_reading += bytes([padding] * padding)

    # Encrypt blocks
    encrypted = b""
    for i in range(0, len(sensor_reading), 8):
        block = sensor_reading[i:i+8]
        encrypted += cipher.encrypt_block(block, device_key)

    return encrypted

if __name__ == "__main__":
    # IoT device encryption example
    device_key = b"IoTDeviceKey1234"  # 128-bit key
    sensor_data = b"Temperature: 25.3C, Humidity: 60%"

    encrypted = encrypt_sensor_data(sensor_data, device_key)
    print(f"Encrypted sensor data: {encrypted.hex()}")
