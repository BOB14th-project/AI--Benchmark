/*
 * Banking Security Module
 * Financial transaction processing with block-based encryption
 */

import java.security.SecureRandom;
import java.util.Arrays;

public class BankingSecurityModule {

    private static final int BLOCK_SIZE = 16;
    private static final int KEY_SIZE = 16;
    private static final int ROUNDS = 16;

    // Block cipher implementation
    public static class BlockCipher {
        private byte[] masterKey;
        private int[][] roundKeys;

        // Substitution box constants
        private static final int[] SS0 = {
            0x2989a1a8, 0x09858ea0, 0x46ae1584, 0x42e9e2c8, 0xebe4e4a1, 0x16429244,
            // ... Additional S-box values would be here
        };

        private static final int[] SS1 = {
            0xd2da8068, 0x40fa4415, 0x21b46f41, 0x5e4b9154, 0xdf9c8052, 0x2f98b041,
            // ... Additional S-box values would be here
        };

        public BlockCipher(byte[] key) {
            this.masterKey = Arrays.copyOf(key, KEY_SIZE);
            generateRoundKeys();
        }

        // Key schedule generation
        private void generateRoundKeys() {
            roundKeys = new int[ROUNDS][2];

            // Convert key to 32-bit words
            int[] keyWords = new int[4];
            for (int i = 0; i < 4; i++) {
                keyWords[i] = bytesToInt(masterKey, i * 4);
            }

            // Generate round keys
            for (int i = 0; i < ROUNDS; i++) {
                // Simplified key schedule (production would be more complex)
                roundKeys[i][0] = keyWords[i % 4] ^ (i * 0x9e3779b9);
                roundKeys[i][1] = keyWords[(i + 1) % 4] ^ ((i + 1) * 0x9e3779b9);

                // Rotate for next round
                int temp = keyWords[0];
                keyWords[0] = keyWords[1];
                keyWords[1] = keyWords[2];
                keyWords[2] = keyWords[3];
                keyWords[3] = temp ^ i;
            }
        }

        // Substitution function
        private int gFunction(int input) {
            int c0 = input & 0xFF;
            int c1 = (input >>> 8) & 0xFF;
            int c2 = (input >>> 16) & 0xFF;
            int c3 = (input >>> 24) & 0xFF;

            // Apply S-boxes (simplified)
            c0 = SS0[c0 % SS0.length] & 0xFF;
            c1 = SS1[c1 % SS1.length] & 0xFF;
            c2 = SS0[c2 % SS0.length] & 0xFF;
            c3 = SS1[c3 % SS1.length] & 0xFF;

            return (c3 << 24) | (c2 << 16) | (c1 << 8) | c0;
        }

        // Round function
        private int fFunction(int left, int right, int k0, int k1) {
            int c = left ^ k0;
            int d = right ^ k1;

            d ^= gFunction(c);
            c = (c + d) & 0xFFFFFFFF;
            c ^= gFunction(d);

            return c;
        }

        // Encrypt single block
        public byte[] encryptBlock(byte[] plaintext) {
            if (plaintext.length != BLOCK_SIZE) {
                throw new IllegalArgumentException("Block size must be " + BLOCK_SIZE + " bytes");
            }

            // Convert to 32-bit words
            int left0 = bytesToInt(plaintext, 0);
            int left1 = bytesToInt(plaintext, 4);
            int right0 = bytesToInt(plaintext, 8);
            int right1 = bytesToInt(plaintext, 12);

            // Block cipher rounds
            for (int round = 0; round < ROUNDS; round++) {
                int temp0 = right0;
                int temp1 = right1;

                right0 = left0 ^ fFunction(left1, right1, roundKeys[round][0], roundKeys[round][1]);
                right1 = left1;
                left0 = temp0;
                left1 = temp1;
            }

            // Convert back to bytes
            byte[] ciphertext = new byte[BLOCK_SIZE];
            intToBytes(right0, ciphertext, 0);
            intToBytes(right1, ciphertext, 4);
            intToBytes(left0, ciphertext, 8);
            intToBytes(left1, ciphertext, 12);

            return ciphertext;
        }

        private int bytesToInt(byte[] bytes, int offset) {
            return ((bytes[offset] & 0xFF) << 24) |
                   ((bytes[offset + 1] & 0xFF) << 16) |
                   ((bytes[offset + 2] & 0xFF) << 8) |
                   (bytes[offset + 3] & 0xFF);
        }

        private void intToBytes(int value, byte[] bytes, int offset) {
            bytes[offset] = (byte) (value >>> 24);
            bytes[offset + 1] = (byte) (value >>> 16);
            bytes[offset + 2] = (byte) (value >>> 8);
            bytes[offset + 3] = (byte) value;
        }
    }

    private BlockCipher blockCipher;
    private SecureRandom secureRandom;

    public BankingSecurityModule(byte[] masterKey) {
        this.blockCipher = new BlockCipher(masterKey);
        this.secureRandom = new SecureRandom();
    }

    // Encrypt banking transaction data
    public byte[] encryptTransactionData(String transactionData) {
        byte[] plaintext = transactionData.getBytes();

        // Pad to block size
        int paddedLength = ((plaintext.length + BLOCK_SIZE - 1) / BLOCK_SIZE) * BLOCK_SIZE;
        byte[] paddedData = Arrays.copyOf(plaintext, paddedLength);

        // Encrypt in CBC mode
        byte[] iv = new byte[BLOCK_SIZE];
        secureRandom.nextBytes(iv);

        byte[] encrypted = new byte[BLOCK_SIZE + paddedLength]; // IV + ciphertext
        System.arraycopy(iv, 0, encrypted, 0, BLOCK_SIZE);

        byte[] previousBlock = iv;
        for (int i = 0; i < paddedLength; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(paddedData, i, i + BLOCK_SIZE);

            // CBC mode: XOR with previous ciphertext block
            for (int j = 0; j < BLOCK_SIZE; j++) {
                block[j] ^= previousBlock[j];
            }

            byte[] encryptedBlock = blockCipher.encryptBlock(block);
            System.arraycopy(encryptedBlock, 0, encrypted, BLOCK_SIZE + i, BLOCK_SIZE);

            previousBlock = encryptedBlock;
        }

        return encrypted;
    }

    // Generate transaction authentication code
    public byte[] generateTransactionMAC(String transactionData, byte[] secretKey) {
        // HMAC-like authentication
        byte[] ipad = new byte[BLOCK_SIZE];
        byte[] opad = new byte[BLOCK_SIZE];

        // Prepare key
        byte[] key = Arrays.copyOf(secretKey, BLOCK_SIZE);

        for (int i = 0; i < BLOCK_SIZE; i++) {
            ipad[i] = (byte) (key[i] ^ 0x36);
            opad[i] = (byte) (key[i] ^ 0x5C);
        }

        // Inner hash
        BlockCipher innerCipher = new BlockCipher(key);
        byte[] innerResult = innerCipher.encryptBlock(ipad);

        // Process message
        byte[] messageBytes = transactionData.getBytes();
        for (int i = 0; i < messageBytes.length; i += BLOCK_SIZE) {
            byte[] block = new byte[BLOCK_SIZE];
            int blockSize = Math.min(BLOCK_SIZE, messageBytes.length - i);
            System.arraycopy(messageBytes, i, block, 0, blockSize);

            for (int j = 0; j < BLOCK_SIZE; j++) {
                block[j] ^= innerResult[j];
            }

            innerResult = innerCipher.encryptBlock(block);
        }

        // Outer hash
        BlockCipher outerCipher = new BlockCipher(key);
        byte[] outerInput = new byte[BLOCK_SIZE];
        System.arraycopy(opad, 0, outerInput, 0, BLOCK_SIZE);

        for (int i = 0; i < BLOCK_SIZE; i++) {
            outerInput[i] ^= innerResult[i];
        }

        return outerCipher.encryptBlock(outerInput);
    }

    // Process secure banking transaction
    public boolean processSecureBankingTransaction(String accountFrom, String accountTo, double amount) {
        String transactionData = accountFrom + ":" + accountTo + ":" + amount + ":" + System.currentTimeMillis();

        // Encrypt transaction data
        byte[] encryptedData = encryptTransactionData(transactionData);

        // Generate authentication code
        byte[] macKey = new byte[KEY_SIZE];
        secureRandom.nextBytes(macKey);
        byte[] authCode = generateTransactionMAC(transactionData, macKey);

        System.out.println("Banking transaction secured using block cipher");
        System.out.println("128-bit block encryption in CBC mode");
        System.out.println("HMAC-style authentication applied");

        return encryptedData.length > 0 && authCode.length > 0;
    }

    public static void main(String[] args) {
        byte[] bankingKey = {
            (byte) 0x2b, (byte) 0x7e, (byte) 0x15, (byte) 0x16,
            (byte) 0x28, (byte) 0xae, (byte) 0xd2, (byte) 0xa6,
            (byte) 0xab, (byte) 0xf7, (byte) 0x15, (byte) 0x88,
            (byte) 0x09, (byte) 0xcf, (byte) 0x4f, (byte) 0x3c
        };

        BankingSecurityModule securityModule = new BankingSecurityModule(bankingKey);
        securityModule.processSecureBankingTransaction("1234567890", "0987654321", 1000.00);
    }
}