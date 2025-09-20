import java.util.Arrays;

public class IDEAInternationalEncryption {
    private static final int BLOCK_SIZE = 8;
    private static final int KEY_SIZE = 16;
    private static final int ROUNDS = 8;

    private int[] encryptionKeys;
    private int[] decryptionKeys;

    private static final int MODULUS = 0x10001; 

    public IDEAInternationalEncryption() {
        encryptionKeys = new int[52]; 
        decryptionKeys = new int[52];
    }

    public void initialize(byte[] key) {
        if (key.length != KEY_SIZE) {
            throw new IllegalArgumentException("Key must be 128 bits");
        }

        generateEncryptionKeys(key);
        generateDecryptionKeys();
    }

    private void generateEncryptionKeys(byte[] masterKey) {
        
        int[] keyWords = new int[8];
        for (int i = 0; i < 8; i++) {
            keyWords[i] = ((masterKey[i * 2] & 0xFF) << 8) | (masterKey[i * 2 + 1] & 0xFF);
        }

        int keyIndex = 0;
        for (int i = 0; i < 52; i++) {
            encryptionKeys[i] = keyWords[keyIndex];
            keyIndex = (keyIndex + 1) % 8;

            if (i % 8 == 7) {
                rotateKeySchedule(keyWords);
            }
        }
    }

    private void rotateKeySchedule(int[] keyWords) {
        
        long key = 0;
        for (int i = 0; i < 8; i++) {
            key = (key << 16) | keyWords[i];
        }

        key = ((key << 25) | (key >>> (128 - 25))) & 0xFFFFFFFFFFFFFFFFL;

        for (int i = 7; i >= 0; i--) {
            keyWords[i] = (int)(key & 0xFFFF);
            key >>>= 16;
        }
    }

    private void generateDecryptionKeys() {
        
        int[] temp = new int[52];

        for (int round = 0; round < ROUNDS + 1; round++) {
            int encRound = ROUNDS - round;

            if (round == 0 || round == ROUNDS) {
                
                temp[round * 6] = multiplicativeInverse(encryptionKeys[encRound * 6]);
                temp[round * 6 + 1] = additiveInverse(encryptionKeys[encRound * 6 + 1]);
                temp[round * 6 + 2] = additiveInverse(encryptionKeys[encRound * 6 + 2]);
                temp[round * 6 + 3] = multiplicativeInverse(encryptionKeys[encRound * 6 + 3]);
            } else {
                
                temp[round * 6] = multiplicativeInverse(encryptionKeys[encRound * 6]);
                temp[round * 6 + 1] = additiveInverse(encryptionKeys[encRound * 6 + 2]);
                temp[round * 6 + 2] = additiveInverse(encryptionKeys[encRound * 6 + 1]);
                temp[round * 6 + 3] = multiplicativeInverse(encryptionKeys[encRound * 6 + 3]);
                temp[round * 6 + 4] = encryptionKeys[encRound * 6 + 4];
                temp[round * 6 + 5] = encryptionKeys[encRound * 6 + 5];
            }
        }

        decryptionKeys = temp;
    }

    private int multiplicativeInverse(int x) {
        if (x == 0) return 0; 
        return modularInverse(x, MODULUS);
    }

    private int additiveInverse(int x) {
        return (0x10000 - x) & 0xFFFF;
    }

    private int modularInverse(int a, int mod) {
        
        int t = 0, newT = 1;
        int r = mod, newR = a;

        while (newR != 0) {
            int quotient = r / newR;
            int tempT = t;
            t = newT;
            newT = tempT - quotient * newT;

            int tempR = r;
            r = newR;
            newR = tempR - quotient * newR;
        }

        if (r > 1) return 0; 
        if (t < 0) t += mod;

        return t;
    }

    public byte[] encryptBlock(byte[] plaintext) {
        if (plaintext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Block size must be 64 bits");
        }

        int x1 = ((plaintext[0] & 0xFF) << 8) | (plaintext[1] & 0xFF);
        int x2 = ((plaintext[2] & 0xFF) << 8) | (plaintext[3] & 0xFF);
        int x3 = ((plaintext[4] & 0xFF) << 8) | (plaintext[5] & 0xFF);
        int x4 = ((plaintext[6] & 0xFF) << 8) | (plaintext[7] & 0xFF);

        for (int round = 0; round < ROUNDS; round++) {
            int keyOffset = round * 6;

            x1 = multiply(x1, encryptionKeys[keyOffset]);
            x2 = add(x2, encryptionKeys[keyOffset + 1]);
            x3 = add(x3, encryptionKeys[keyOffset + 2]);
            x4 = multiply(x4, encryptionKeys[keyOffset + 3]);

            int t1 = x1 ^ x3;
            int t2 = x2 ^ x4;

            t1 = multiply(t1, encryptionKeys[keyOffset + 4]);
            t2 = add(t2, t1);
            t2 = multiply(t2, encryptionKeys[keyOffset + 5]);
            t1 = add(t1, t2);

            x1 ^= t2;
            x2 ^= t1;
            x3 ^= t2;
            x4 ^= t1;

            if (round < ROUNDS - 1) {
                int temp = x2;
                x2 = x3;
                x3 = temp;
            }
        }

        int keyOffset = ROUNDS * 6;
        x1 = multiply(x1, encryptionKeys[keyOffset]);
        x2 = add(x2, encryptionKeys[keyOffset + 1]);
        x3 = add(x3, encryptionKeys[keyOffset + 2]);
        x4 = multiply(x4, encryptionKeys[keyOffset + 3]);

        byte[] ciphertext = new byte[BLOCK_SIZE];
        ciphertext[0] = (byte)(x1 >>> 8);
        ciphertext[1] = (byte)(x1 & 0xFF);
        ciphertext[2] = (byte)(x2 >>> 8);
        ciphertext[3] = (byte)(x2 & 0xFF);
        ciphertext[4] = (byte)(x3 >>> 8);
        ciphertext[5] = (byte)(x3 & 0xFF);
        ciphertext[6] = (byte)(x4 >>> 8);
        ciphertext[7] = (byte)(x4 & 0xFF);

        return ciphertext;
    }

    public byte[] decryptBlock(byte[] ciphertext) {
        if (ciphertext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Block size must be 64 bits");
        }

        int x1 = ((ciphertext[0] & 0xFF) << 8) | (ciphertext[1] & 0xFF);
        int x2 = ((ciphertext[2] & 0xFF) << 8) | (ciphertext[3] & 0xFF);
        int x3 = ((ciphertext[4] & 0xFF) << 8) | (ciphertext[5] & 0xFF);
        int x4 = ((ciphertext[6] & 0xFF) << 8) | (ciphertext[7] & 0xFF);

        for (int round = 0; round < ROUNDS; round++) {
            int keyOffset = round * 6;

            x1 = multiply(x1, decryptionKeys[keyOffset]);
            x2 = add(x2, decryptionKeys[keyOffset + 1]);
            x3 = add(x3, decryptionKeys[keyOffset + 2]);
            x4 = multiply(x4, decryptionKeys[keyOffset + 3]);

            int t1 = x1 ^ x3;
            int t2 = x2 ^ x4;

            t1 = multiply(t1, decryptionKeys[keyOffset + 4]);
            t2 = add(t2, t1);
            t2 = multiply(t2, decryptionKeys[keyOffset + 5]);
            t1 = add(t1, t2);

            x1 ^= t2;
            x2 ^= t1;
            x3 ^= t2;
            x4 ^= t1;

            if (round < ROUNDS - 1) {
                int temp = x2;
                x2 = x3;
                x3 = temp;
            }
        }

        int keyOffset = ROUNDS * 6;
        x1 = multiply(x1, decryptionKeys[keyOffset]);
        x2 = add(x2, decryptionKeys[keyOffset + 1]);
        x3 = add(x3, decryptionKeys[keyOffset + 2]);
        x4 = multiply(x4, decryptionKeys[keyOffset + 3]);

        byte[] plaintext = new byte[BLOCK_SIZE];
        plaintext[0] = (byte)(x1 >>> 8);
        plaintext[1] = (byte)(x1 & 0xFF);
        plaintext[2] = (byte)(x2 >>> 8);
        plaintext[3] = (byte)(x2 & 0xFF);
        plaintext[4] = (byte)(x3 >>> 8);
        plaintext[5] = (byte)(x3 & 0xFF);
        plaintext[6] = (byte)(x4 >>> 8);
        plaintext[7] = (byte)(x4 & 0xFF);

        return plaintext;
    }

    private int multiply(int a, int b) {
        if (a == 0) a = 0x10000;
        if (b == 0) b = 0x10000;

        long result = ((long)a * b) % MODULUS;
        if (result == 0) result = MODULUS;

        return (int)result & 0xFFFF;
    }

    private int add(int a, int b) {
        return (a + b) & 0xFFFF;
    }

    public byte[] processData(byte[] data, boolean encrypt) {
        if (data.length % BLOCK_SIZE != 0) {
            throw new IllegalArgumentException("Data length must be multiple of block size");
        }

        byte[] result = new byte[data.length];

        for (int i = 0; i < data.length; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(data, i, i + BLOCK_SIZE);
            byte[] processedBlock = encrypt ? encryptBlock(block) : decryptBlock(block);
            System.arraycopy(processedBlock, 0, result, i, BLOCK_SIZE);
        }

        return result;
    }

    public static void main(String[] args) {
        try {
            IDEAInternationalEncryption cipher = new IDEAInternationalEncryption();

            byte[] key = "SecretKey1234567".getBytes();
            cipher.initialize(key);

            String testData = "TestData";
            byte[] plaintext = testData.getBytes();

            byte[] paddedPlaintext = new byte[BLOCK_SIZE];
            System.arraycopy(plaintext, 0, paddedPlaintext, 0, Math.min(plaintext.length, BLOCK_SIZE));

            System.out.println("Original: " + new String(paddedPlaintext).trim());

            byte[] ciphertext = cipher.processData(paddedPlaintext, true);
            System.out.print("Encrypted: ");
            for (byte b : ciphertext) {
                System.out.printf("%02x ", b & 0xFF);
            }
            System.out.println();

            byte[] decrypted = cipher.processData(ciphertext, false);
            System.out.println("Decrypted: " + new String(decrypted).trim());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}