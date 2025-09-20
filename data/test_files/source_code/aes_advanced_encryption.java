import java.util.Arrays;

public class AdvancedBlockCipher {

    private static final int BLOCK_SIZE = 16;
    private static final int[] KEY_SIZES = {16, 24, 32}; 
    private static final int[] ROUNDS = {10, 12, 14};    

    private static final int[] SBOX = {
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    };

    private static final int[] INV_SBOX = {
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
    };

    private static final int[] RCON = {
        0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a
    };

    private int[][] roundKeys;
    private int numRounds;
    private int keySize;

    public AdvancedBlockCipher(byte[] key) {
        if (!isValidKeySize(key.length)) {
            throw new IllegalArgumentException("Invalid key size. Must be 16, 24, or 32 bytes.");
        }

        this.keySize = key.length;
        this.numRounds = getRoundsForKeySize(keySize);
        this.roundKeys = expandKey(key);
    }

    private boolean isValidKeySize(int size) {
        for (int validSize : KEY_SIZES) {
            if (size == validSize) return true;
        }
        return false;
    }

    private int getRoundsForKeySize(int keySize) {
        for (int i = 0; i < KEY_SIZES.length; i++) {
            if (KEY_SIZES[i] == keySize) return ROUNDS[i];
        }
        throw new IllegalArgumentException("Invalid key size");
    }

    private int[][] expandKey(byte[] key) {
        int keyWords = keySize / 4;
        int totalWords = 4 * (numRounds + 1);
        int[] w = new int[totalWords];

        for (int i = 0; i < keyWords; i++) {
            w[i] = bytesToWord(key, i * 4);
        }

        for (int i = keyWords; i < totalWords; i++) {
            int temp = w[i - 1];

            if (i % keyWords == 0) {
                temp = subWord(rotWord(temp)) ^ RCON[(i / keyWords) - 1];
            } else if (keyWords > 6 && i % keyWords == 4) {
                temp = subWord(temp);
            }

            w[i] = w[i - keyWords] ^ temp;
        }

        int[][] keys = new int[numRounds + 1][4];
        for (int round = 0; round <= numRounds; round++) {
            for (int col = 0; col < 4; col++) {
                keys[round][col] = w[round * 4 + col];
            }
        }

        return keys;
    }

    private int bytesToWord(byte[] bytes, int offset) {
        return ((bytes[offset] & 0xFF) << 24) |
               ((bytes[offset + 1] & 0xFF) << 16) |
               ((bytes[offset + 2] & 0xFF) << 8) |
               (bytes[offset + 3] & 0xFF);
    }

    private int rotWord(int word) {
        return ((word << 8) | (word >>> 24)) & 0xFFFFFFFF;
    }

    private int subWord(int word) {
        return (SBOX[(word >>> 24) & 0xFF] << 24) |
               (SBOX[(word >>> 16) & 0xFF] << 16) |
               (SBOX[(word >>> 8) & 0xFF] << 8) |
               SBOX[word & 0xFF];
    }

    private void subBytes(int[][] state) {
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                int byteVal = (state[row][col / 4] >>> (8 * (3 - col % 4))) & 0xFF;
                byteVal = SBOX[byteVal];
                state[row][col / 4] = (state[row][col / 4] & ~(0xFF << (8 * (3 - col % 4)))) |
                                     (byteVal << (8 * (3 - col % 4)));
            }
        }
    }

    private void invSubBytes(int[][] state) {
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                int byteVal = (state[row][col / 4] >>> (8 * (3 - col % 4))) & 0xFF;
                byteVal = INV_SBOX[byteVal];
                state[row][col / 4] = (state[row][col / 4] & ~(0xFF << (8 * (3 - col % 4)))) |
                                     (byteVal << (8 * (3 - col % 4)));
            }
        }
    }

    private void shiftRows(int[][] state) {

        for (int row = 1; row < 4; row++) {
            byte[] rowBytes = new byte[4];
            for (int col = 0; col < 4; col++) {
                rowBytes[col] = (byte)((state[row][col] >>> (8 * (3 - row))) & 0xFF);
            }

            byte[] shifted = new byte[4];
            for (int i = 0; i < 4; i++) {
                shifted[i] = rowBytes[(i + row) % 4];
            }

            for (int col = 0; col < 4; col++) {
                state[row][col] = (state[row][col] & ~(0xFF << (8 * (3 - row)))) |
                                 ((shifted[col] & 0xFF) << (8 * (3 - row)));
            }
        }
    }

    private void invShiftRows(int[][] state) {
        for (int row = 1; row < 4; row++) {
            byte[] rowBytes = new byte[4];
            for (int col = 0; col < 4; col++) {
                rowBytes[col] = (byte)((state[row][col] >>> (8 * (3 - row))) & 0xFF);
            }

            byte[] shifted = new byte[4];
            for (int i = 0; i < 4; i++) {
                shifted[i] = rowBytes[(i - row + 4) % 4];
            }

            for (int col = 0; col < 4; col++) {
                state[row][col] = (state[row][col] & ~(0xFF << (8 * (3 - row)))) |
                                 ((shifted[col] & 0xFF) << (8 * (3 - row)));
            }
        }
    }

    private int gfMultiply(int a, int b) {
        int result = 0;
        while (a != 0 && b != 0) {
            if ((b & 1) != 0) {
                result ^= a;
            }
            if ((a & 0x80) != 0) {
                a = (a << 1) ^ 0x1b;
            } else {
                a <<= 1;
            }
            b >>>= 1;
        }
        return result & 0xFF;
    }

    private void mixColumns(int[][] state) {
        int[][] mixMatrix = {{2, 3, 1, 1}, {1, 2, 3, 1}, {1, 1, 2, 3}, {3, 1, 1, 2}};

        for (int col = 0; col < 4; col++) {
            int[] column = new int[4];
            for (int row = 0; row < 4; row++) {
                column[row] = (state[row][col] >>> (8 * (3 - row))) & 0xFF;
            }

            for (int row = 0; row < 4; row++) {
                int result = 0;
                for (int i = 0; i < 4; i++) {
                    result ^= gfMultiply(mixMatrix[row][i], column[i]);
                }
                state[row][col] = (state[row][col] & ~(0xFF << (8 * (3 - row)))) |
                                 (result << (8 * (3 - row)));
            }
        }
    }

    private void invMixColumns(int[][] state) {
        int[][] invMixMatrix = {{14, 11, 13, 9}, {9, 14, 11, 13}, {13, 9, 14, 11}, {11, 13, 9, 14}};

        for (int col = 0; col < 4; col++) {
            int[] column = new int[4];
            for (int row = 0; row < 4; row++) {
                column[row] = (state[row][col] >>> (8 * (3 - row))) & 0xFF;
            }

            for (int row = 0; row < 4; row++) {
                int result = 0;
                for (int i = 0; i < 4; i++) {
                    result ^= gfMultiply(invMixMatrix[row][i], column[i]);
                }
                state[row][col] = (state[row][col] & ~(0xFF << (8 * (3 - row)))) |
                                 (result << (8 * (3 - row)));
            }
        }
    }

    private void addRoundKey(int[][] state, int round) {
        for (int col = 0; col < 4; col++) {
            state[0][col] ^= roundKeys[round][col];
        }
    }

    private int[][] bytesToState(byte[] input) {
        int[][] state = new int[4][4];
        for (int col = 0; col < 4; col++) {
            state[0][col] = bytesToWord(input, col * 4);
        }
        return state;
    }

    private byte[] stateToBytes(int[][] state) {
        byte[] output = new byte[16];
        for (int col = 0; col < 4; col++) {
            int word = state[0][col];
            output[col * 4] = (byte)(word >>> 24);
            output[col * 4 + 1] = (byte)(word >>> 16);
            output[col * 4 + 2] = (byte)(word >>> 8);
            output[col * 4 + 3] = (byte)word;
        }
        return output;
    }

    public byte[] encryptBlock(byte[] plaintext) {
        if (plaintext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Block size must be 16 bytes");
        }

        int[][] state = bytesToState(plaintext);

        addRoundKey(state, 0);

        for (int round = 1; round < numRounds; round++) {
            subBytes(state);
            shiftRows(state);
            mixColumns(state);
            addRoundKey(state, round);
        }

        subBytes(state);
        shiftRows(state);
        addRoundKey(state, numRounds);

        return stateToBytes(state);
    }

    public byte[] decryptBlock(byte[] ciphertext) {
        if (ciphertext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Block size must be 16 bytes");
        }

        int[][] state = bytesToState(ciphertext);

        addRoundKey(state, numRounds);
        invShiftRows(state);
        invSubBytes(state);

        for (int round = numRounds - 1; round > 0; round--) {
            addRoundKey(state, round);
            invMixColumns(state);
            invShiftRows(state);
            invSubBytes(state);
        }

        addRoundKey(state, 0);

        return stateToBytes(state);
    }

    public byte[] encrypt(byte[] plaintext) {
        if (plaintext.length % BLOCK_SIZE != 0) {
            throw new IllegalArgumentException("Plaintext length must be multiple of 16 bytes");
        }

        byte[] ciphertext = new byte[plaintext.length];

        for (int i = 0; i < plaintext.length; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(plaintext, i, i + BLOCK_SIZE);
            byte[] encryptedBlock = encryptBlock(block);
            System.arraycopy(encryptedBlock, 0, ciphertext, i, BLOCK_SIZE);
        }

        return ciphertext;
    }

    public byte[] decrypt(byte[] ciphertext) {
        if (ciphertext.length % BLOCK_SIZE != 0) {
            throw new IllegalArgumentException("Ciphertext length must be multiple of 16 bytes");
        }

        byte[] plaintext = new byte[ciphertext.length];

        for (int i = 0; i < ciphertext.length; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(ciphertext, i, i + BLOCK_SIZE);
            byte[] decryptedBlock = decryptBlock(block);
            System.arraycopy(decryptedBlock, 0, plaintext, i, BLOCK_SIZE);
        }

        return plaintext;
    }

    public static void main(String[] args) {
        try {
            
            System.out.println("=== 128-bit Test ===");
            byte[] key128 = "SecretKey1234567".getBytes(); 
            AdvancedBlockCipher cipher128 = new AdvancedBlockCipher(key128);

            String testData = "Hello Block World!"; 
            byte[] plaintext = testData.getBytes();

            System.out.println("Original: " + testData);

            byte[] encrypted = cipher128.encrypt(plaintext);
            System.out.print("Encrypted: ");
            for (byte b : encrypted) {
                System.out.printf("%02x ", b & 0xFF);
            }
            System.out.println();

            byte[] decrypted = cipher128.decrypt(encrypted);
            System.out.println("Decrypted: " + new String(decrypted));

            System.out.println("\n=== 256-bit Test ===");
            byte[] key256 = "SecretKey1234567890123456789012".getBytes(); 
            AdvancedBlockCipher cipher256 = new AdvancedBlockCipher(key256);

            byte[] encrypted256 = cipher256.encrypt(plaintext);
            byte[] decrypted256 = cipher256.decrypt(encrypted256);

            System.out.println("256-bit encryption successful: " +
                Arrays.equals(plaintext, decrypted256));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}