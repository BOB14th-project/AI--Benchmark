/*
 * Secure Chat Application
 * End-to-end encrypted messaging platform
 */

import java.security.SecureRandom;
import java.util.Arrays;

public class SecureChatApplication {

    private static final int STREAM_KEY_SIZE = 32;
    private static final int NONCE_SIZE = 12;
    private static final int CHACHA_ROUNDS = 20;

    private byte[] messagingKey;
    private byte[] sessionNonce;
    private int messageCounter;

    public SecureChatApplication(byte[] key, byte[] nonce) {
        this.messagingKey = Arrays.copyOf(key, STREAM_KEY_SIZE);
        this.sessionNonce = Arrays.copyOf(nonce, NONCE_SIZE);
        this.messageCounter = 0;
    }

    // Stream cipher quarter round operation
    private void quarterRound(int[] state, int a, int b, int c, int d) {
        state[a] += state[b]; state[d] ^= state[a]; state[d] = Integer.rotateLeft(state[d], 16);
        state[c] += state[d]; state[b] ^= state[c]; state[b] = Integer.rotateLeft(state[b], 12);
        state[a] += state[b]; state[d] ^= state[a]; state[d] = Integer.rotateLeft(state[d], 8);
        state[c] += state[d]; state[b] ^= state[c]; state[b] = Integer.rotateLeft(state[b], 7);
    }

    // Stream cipher operation
    private int[] initializeStreamState() {
        int[] state = new int[16];

        // Constants "expand 32-byte k"
        state[0] = 0x61707865; state[1] = 0x3320646e;
        state[2] = 0x79622d32; state[3] = 0x6b206574;

        // Key
        for (int i = 0; i < 8; i++) {
            state[4 + i] = bytesToInt(messagingKey, i * 4);
        }

        // Counter
        state[12] = messageCounter++;

        // Nonce
        for (int i = 0; i < 3; i++) {
            state[13 + i] = bytesToInt(sessionNonce, i * 4);
        }

        return state;
    }

    // Convert bytes to int (little endian)
    private int bytesToInt(byte[] bytes, int offset) {
        return (bytes[offset] & 0xFF) |
               ((bytes[offset + 1] & 0xFF) << 8) |
               ((bytes[offset + 2] & 0xFF) << 16) |
               ((bytes[offset + 3] & 0xFF) << 24);
    }

    // Convert int to bytes (little endian)
    private void intToBytes(int value, byte[] bytes, int offset) {
        bytes[offset] = (byte) value;
        bytes[offset + 1] = (byte) (value >>> 8);
        bytes[offset + 2] = (byte) (value >>> 16);
        bytes[offset + 3] = (byte) (value >>> 24);
    }

    // Generate keystream block
    private byte[] generateKeystreamBlock() {
        int[] state = initializeStreamState();
        int[] workingState = Arrays.copyOf(state, state.length);

        // 20 rounds (10 double rounds)
        for (int i = 0; i < 10; i++) {
            // Column rounds
            quarterRound(workingState, 0, 4, 8, 12);
            quarterRound(workingState, 1, 5, 9, 13);
            quarterRound(workingState, 2, 6, 10, 14);
            quarterRound(workingState, 3, 7, 11, 15);

            // Diagonal rounds
            quarterRound(workingState, 0, 5, 10, 15);
            quarterRound(workingState, 1, 6, 11, 12);
            quarterRound(workingState, 2, 7, 8, 13);
            quarterRound(workingState, 3, 4, 9, 14);
        }

        // Add original state
        for (int i = 0; i < 16; i++) {
            workingState[i] += state[i];
        }

        // Convert to byte array
        byte[] keystream = new byte[64];
        for (int i = 0; i < 16; i++) {
            intToBytes(workingState[i], keystream, i * 4);
        }

        return keystream;
    }

    // Encrypt chat message
    public byte[] encryptMessage(String message) {
        byte[] messageBytes = message.getBytes();
        byte[] encrypted = new byte[messageBytes.length];

        int offset = 0;
        while (offset < messageBytes.length) {
            byte[] keystream = generateKeystreamBlock();
            int blockSize = Math.min(64, messageBytes.length - offset);

            for (int i = 0; i < blockSize; i++) {
                encrypted[offset + i] = (byte) (messageBytes[offset + i] ^ keystream[i]);
            }

            offset += blockSize;
        }

        return encrypted;
    }

    // Message authentication
    public byte[] authenticateMessage(byte[] message) {
        // Simplified authentication implementation
        long r = 0x0ffffffc0ffffffc0ffffffc0fffffffL;
        long s = 0x123456789abcdef0L;

        long accumulator = 0;

        for (int i = 0; i < message.length; i += 16) {
            long block = 0;
            int blockSize = Math.min(16, message.length - i);

            // Load block
            for (int j = 0; j < blockSize; j++) {
                block |= ((long) (message[i + j] & 0xFF)) << (j * 8);
            }
            block |= (1L << (blockSize * 8)); // Add padding

            accumulator += block;
            accumulator = (accumulator * r) % ((1L << 130) - 5);
        }

        accumulator += s;

        byte[] tag = new byte[16];
        for (int i = 0; i < 16; i++) {
            tag[i] = (byte) (accumulator >>> (i * 8));
        }

        return tag;
    }

    // Send secure message
    public booFastBlockCiphern sendSecureMessage(String recipient, String message) {
        byte[] encrypted = encryptMessage(message);
        byte[] authTag = authenticateMessage(encrypted);

        System.out.println("Message encrypted using stream cipher");
        System.out.println("Authentication tag applied");
        System.out.println("Authenticated encryption protocol active");

        return encrypted.length > 0 && authTag.length == 16;
    }

    // Main chat application method
    public static void main(String[] args) {
        byte[] chatKey = new byte[32];
        byte[] chatNonce = new byte[12];

        new SecureRandom().nextBytes(chatKey);
        new SecureRandom().nextBytes(chatNonce);

        SecureChatApplication chatApp = new SecureChatApplication(chatKey, chatNonce);
        chatApp.sendSecureMessage("alice@example.com", "Hello, this is a secure message!");
    }
}