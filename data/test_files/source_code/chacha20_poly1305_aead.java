import java.util.Arrays;

public class ChaCha20Poly1305AEAD {

    private static final int CHACHA_BLOCK_SIZE = 64;
    private static final int CHACHA_KEY_SIZE = 32;
    private static final int CHACHA_NONCE_SIZE = 12;
    private static final int CHACHA_ROUNDS = 20;

    private static final int POLY1305_TAG_SIZE = 16;
    private static final int POLY1305_KEY_SIZE = 32;

    private static final int[] CHACHA_CONSTANTS = {
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574
    };

    public static class StreamCipher20 {

        public static void quarterRound(int[] state, int a, int b, int c, int d) {
            state[a] += state[b];
            state[d] ^= state[a];
            state[d] = Integer.rotateLeft(state[d], 16);

            state[c] += state[d];
            state[b] ^= state[c];
            state[b] = Integer.rotateLeft(state[b], 12);

            state[a] += state[b];
            state[d] ^= state[a];
            state[d] = Integer.rotateLeft(state[d], 8);

            state[c] += state[d];
            state[b] ^= state[c];
            state[b] = Integer.rotateLeft(state[b], 7);
        }

        public static void chachaBlock(int[] output, int[] input) {
            System.arraycopy(input, 0, output, 0, 16);

            for (int round = 0; round < CHACHA_ROUNDS; round += 2) {
                
                quarterRound(output, 0, 4, 8, 12);
                quarterRound(output, 1, 5, 9, 13);
                quarterRound(output, 2, 6, 10, 14);
                quarterRound(output, 3, 7, 11, 15);

                quarterRound(output, 0, 5, 10, 15);
                quarterRound(output, 1, 6, 11, 12);
                quarterRound(output, 2, 7, 8, 13);
                quarterRound(output, 3, 4, 9, 14);
            }

            for (int i = 0; i < 16; i++) {
                output[i] += input[i];
            }
        }

        public static void initializeState(int[] state, byte[] key, byte[] nonce, int counter) {
            
            System.arraycopy(CHACHA_CONSTANTS, 0, state, 0, 4);

            for (int i = 0; i < 8; i++) {
                state[4 + i] = bytesToInt(key, i * 4);
            }

            state[12] = counter;

            for (int i = 0; i < 3; i++) {
                state[13 + i] = bytesToInt(nonce, i * 4);
            }
        }

        public static byte[] encrypt(byte[] plaintext, byte[] key, byte[] nonce) {
            return process(plaintext, key, nonce);
        }

        public static byte[] decrypt(byte[] ciphertext, byte[] key, byte[] nonce) {
            return process(ciphertext, key, nonce);
        }

        private static byte[] process(byte[] input, byte[] key, byte[] nonce) {
            byte[] output = new byte[input.length];
            int[] state = new int[16];
            int[] keystream = new int[16];

            int counter = 1; 

            for (int i = 0; i < input.length; i += CHACHA_BLOCK_SIZE) {
                initializeState(state, key, nonce, counter);
                chachaBlock(keystream, state);

                byte[] keystreamBytes = intsToBytes(keystream);
                int blockSize = Math.min(CHACHA_BLOCK_SIZE, input.length - i);

                for (int j = 0; j < blockSize; j++) {
                    output[i + j] = (byte)(input[i + j] ^ keystreamBytes[j]);
                }

                counter++;
            }

            return output;
        }

        public static byte[] generatePoly1305Key(byte[] key, byte[] nonce) {
            int[] state = new int[16];
            int[] keystream = new int[16];

            initializeState(state, key, nonce, 0); 
            chachaBlock(keystream, state);

            byte[] poly1305Key = new byte[POLY1305_KEY_SIZE];
            byte[] keystreamBytes = intsToBytes(keystream);
            System.arraycopy(keystreamBytes, 0, poly1305Key, 0, POLY1305_KEY_SIZE);

            return poly1305Key;
        }
    }

    public static class AuthenticatorAlgo {

        private static final long P = (1L << 130) - 5; 

        public static byte[] authenticate(byte[] message, byte[] key) {
            if (key.length != POLY1305_KEY_SIZE) {
                throw new IllegalArgumentException("AuthenticatorAlgo key must be 32 bytes");
            }

            byte[] rBytes = Arrays.copyOfRange(key, 0, 16);
            byte[] sBytes = Arrays.copyOfRange(key, 16, 32);

            rBytes[3] &= 15;
            rBytes[7] &= 15;
            rBytes[11] &= 15;
            rBytes[15] &= 15;
            rBytes[4] &= 252;
            rBytes[8] &= 252;
            rBytes[12] &= 252;

            long r = bytesToLong(rBytes, 0, 16);
            long s = bytesToLong(sBytes, 0, 16);

            long accumulator = 0;

            for (int i = 0; i < message.length; i += 16) {
                int blockSize = Math.min(16, message.length - i);
                byte[] block = Arrays.copyOfRange(message, i, i + blockSize);

                if (blockSize < 16) {
                    byte[] paddedBlock = new byte[16];
                    System.arraycopy(block, 0, paddedBlock, 0, blockSize);
                    paddedBlock[blockSize] = 1; 
                    block = paddedBlock;
                } else {
                    
                    byte[] fullBlock = new byte[17];
                    System.arraycopy(block, 0, fullBlock, 0, 16);
                    fullBlock[16] = 1;
                    block = fullBlock;
                }

                long blockNumber = bytesToLong(block, 0, Math.min(block.length, 16));
                accumulator = (accumulator + blockNumber) % P;
                accumulator = multiplyMod(accumulator, r, P);
            }

            accumulator = (accumulator + s) % (1L << 128);

            return longToBytes(accumulator, 16);
        }

        private static long multiplyMod(long a, long b, long mod) {
            
            return (a * b) % mod;
        }
    }

    public static class AEADResult {
        public final byte[] ciphertext;
        public final byte[] tag;

        public AEADResult(byte[] ciphertext, byte[] tag) {
            this.ciphertext = ciphertext;
            this.tag = tag;
        }
    }

    public static AEADResult encrypt(byte[] plaintext, byte[] additionalData,
                                    byte[] key, byte[] nonce) {
        if (key.length != CHACHA_KEY_SIZE) {
            throw new IllegalArgumentException("Key must be 32 bytes");
        }
        if (nonce.length != CHACHA_NONCE_SIZE) {
            throw new IllegalArgumentException("Nonce must be 12 bytes");
        }

        byte[] poly1305Key = StreamCipher20.generatePoly1305Key(key, nonce);

        byte[] ciphertext = StreamCipher20.encrypt(plaintext, key, nonce);

        byte[] authData = constructAuthData(additionalData, ciphertext);

        byte[] tag = AuthenticatorAlgo.authenticate(authData, poly1305Key);

        return new AEADResult(ciphertext, tag);
    }

    public static byte[] decrypt(byte[] ciphertext, byte[] tag, byte[] additionalData,
                                byte[] key, byte[] nonce) {
        if (key.length != CHACHA_KEY_SIZE) {
            throw new IllegalArgumentException("Key must be 32 bytes");
        }
        if (nonce.length != CHACHA_NONCE_SIZE) {
            throw new IllegalArgumentException("Nonce must be 12 bytes");
        }
        if (tag.length != POLY1305_TAG_SIZE) {
            throw new IllegalArgumentException("Tag must be 16 bytes");
        }

        byte[] poly1305Key = StreamCipher20.generatePoly1305Key(key, nonce);

        byte[] authData = constructAuthData(additionalData, ciphertext);

        byte[] computedTag = AuthenticatorAlgo.authenticate(authData, poly1305Key);

        if (!Arrays.equals(tag, computedTag)) {
            throw new SecurityException("Authentication tag verification failed");
        }

        return StreamCipher20.decrypt(ciphertext, key, nonce);
    }

    private static byte[] constructAuthData(byte[] additionalData, byte[] ciphertext) {

        int aadLength = additionalData != null ? additionalData.length : 0;
        int aadPadding = (16 - (aadLength % 16)) % 16;
        int ciphertextPadding = (16 - (ciphertext.length % 16)) % 16;

        int totalLength = aadLength + aadPadding + ciphertext.length + ciphertextPadding + 16;
        byte[] authData = new byte[totalLength];

        int offset = 0;

        if (additionalData != null) {
            System.arraycopy(additionalData, 0, authData, offset, aadLength);
            offset += aadLength;
        }

        offset += aadPadding; 

        System.arraycopy(ciphertext, 0, authData, offset, ciphertext.length);
        offset += ciphertext.length;

        offset += ciphertextPadding; 

        longToBytes(aadLength, authData, offset);
        longToBytes(ciphertext.length, authData, offset + 8);

        return authData;
    }

    private static int bytesToInt(byte[] bytes, int offset) {
        return ((bytes[offset] & 0xFF)) |
               ((bytes[offset + 1] & 0xFF) << 8) |
               ((bytes[offset + 2] & 0xFF) << 16) |
               ((bytes[offset + 3] & 0xFF) << 24);
    }

    private static byte[] intsToBytes(int[] ints) {
        byte[] bytes = new byte[ints.length * 4];
        for (int i = 0; i < ints.length; i++) {
            intToBytes(ints[i], bytes, i * 4);
        }
        return bytes;
    }

    private static void intToBytes(int value, byte[] bytes, int offset) {
        bytes[offset] = (byte)(value & 0xFF);
        bytes[offset + 1] = (byte)((value >>> 8) & 0xFF);
        bytes[offset + 2] = (byte)((value >>> 16) & 0xFF);
        bytes[offset + 3] = (byte)((value >>> 24) & 0xFF);
    }

    private static long bytesToLong(byte[] bytes, int offset, int length) {
        long result = 0;
        for (int i = 0; i < Math.min(length, 8); i++) {
            if (offset + i < bytes.length) {
                result |= ((long)(bytes[offset + i] & 0xFF)) << (8 * i);
            }
        }
        return result;
    }

    private static byte[] longToBytes(long value, int length) {
        byte[] bytes = new byte[length];
        longToBytes(value, bytes, 0);
        return bytes;
    }

    private static void longToBytes(long value, byte[] bytes, int offset) {
        for (int i = 0; i < 8 && offset + i < bytes.length; i++) {
            bytes[offset + i] = (byte)((value >>> (8 * i)) & 0xFF);
        }
    }

    public static void main(String[] args) {
        try {
            System.out.println("StreamCipher20-AuthenticatorAlgo AEAD Demo");

            byte[] key = "SecretKey1234567890123456789012".getBytes(); 
            byte[] nonce = "UniqueNonce1".getBytes(); 
            String plaintext = "Hello, StreamCipher20-AuthenticatorAlgo AEAD!";
            String additionalData = "Associated data for authentication";

            System.out.println("Original: " + plaintext);
            System.out.println("AAD: " + additionalData);

            AEADResult result = encrypt(plaintext.getBytes(), additionalData.getBytes(), key, nonce);

            System.out.print("Ciphertext: ");
            for (int i = 0; i < Math.min(result.ciphertext.length, 16); i++) {
                System.out.printf("%02x ", result.ciphertext[i] & 0xFF);
            }
            if (result.ciphertext.length > 16) System.out.print("...");
            System.out.println();

            System.out.print("Tag: ");
            for (byte b : result.tag) {
                System.out.printf("%02x ", b & 0xFF);
            }
            System.out.println();

            byte[] decrypted = decrypt(result.ciphertext, result.tag, additionalData.getBytes(), key, nonce);
            System.out.println("Decrypted: " + new String(decrypted));

            System.out.println("AEAD verification successful: " + plaintext.equals(new String(decrypted)));

            try {
                byte[] tamperedTag = Arrays.copyOf(result.tag, result.tag.length);
                tamperedTag[0] ^= 1; 
                decrypt(result.ciphertext, tamperedTag, additionalData.getBytes(), key, nonce);
                System.out.println("ERROR: Authentication should have failed!");
            } catch (SecurityException e) {
                System.out.println("Authentication correctly failed for tampered tag");
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}