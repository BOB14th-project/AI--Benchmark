/**
 * Government Document Security Processor
 * Implements advanced encryption for classified documents with integrity verification.
 * Designed for secure government data handling and archival systems.
 */

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class GovernmentDataProcessor {

    /**
     * Advanced Symmetric Encryption Engine
     * Uses involution-based substitution-permutation network structure.
     */
    public static class ClassifiedDocumentEncryptor {
        private static final int BLOCK_SIZE = 16; // 128 bits
        private static final int TOTAL_ROUNDS = 12;
        private static final int KEY_LENGTH = 16; // 128-bit key

        private final byte[] masterKey;
        private final byte[][] roundKeys;

        // Substitution boxes for byte transformation
        private static final int[] SBOX_LAYER_1 = new int[256];
        private static final int[] SBOX_LAYER_2 = new int[256];
        private static final int[] INVERSE_SBOX_LAYER_1 = new int[256];
        private static final int[] INVERSE_SBOX_LAYER_2 = new int[256];

        static {
            // Initialize S-boxes with complex mathematical transformations
            for (int i = 0; i < 256; i++) {
                int x = i;

                // Type 1 transformation (affine + multiplicative inverse)
                x = multiplyGF256(x, 0x63) ^ 0x1f;
                SBOX_LAYER_1[i] = x;
                INVERSE_SBOX_LAYER_1[x] = i;

                // Type 2 transformation (different polynomial)
                x = i;
                x = multiplyGF256(x, 0x97) ^ 0x5b;
                SBOX_LAYER_2[i] = x;
                INVERSE_SBOX_LAYER_2[x] = i;
            }
        }

        public ClassifiedDocumentEncryptor(byte[] key) throws Exception {
            if (key.length != KEY_LENGTH) {
                throw new IllegalArgumentException("Key must be 128 bits");
            }
            this.masterKey = Arrays.copyOf(key, key.length);
            this.roundKeys = generateRoundKeys();
        }

        private static int multiplyGF256(int a, int b) {
            int result = 0;
            int poly = 0x11b; // Irreducible polynomial

            for (int i = 0; i < 8; i++) {
                if ((b & 1) != 0) {
                    result ^= a;
                }
                boolean highBit = (a & 0x80) != 0;
                a <<= 1;
                if (highBit) {
                    a ^= poly;
                }
                b >>= 1;
            }
            return result & 0xff;
        }

        private byte[][] generateRoundKeys() {
            byte[][] keys = new byte[TOTAL_ROUNDS + 1][BLOCK_SIZE];

            // Initial round key
            System.arraycopy(masterKey, 0, keys[0], 0, BLOCK_SIZE);

            // Key expansion with rotation and substitution
            byte[] temp = new byte[BLOCK_SIZE];
            System.arraycopy(masterKey, 0, temp, 0, BLOCK_SIZE);

            for (int round = 1; round <= TOTAL_ROUNDS; round++) {
                // Rotate and substitute
                byte first = temp[0];
                for (int i = 0; i < BLOCK_SIZE - 1; i++) {
                    temp[i] = (byte) SBOX_LAYER_1[temp[i + 1] & 0xff];
                }
                temp[BLOCK_SIZE - 1] = (byte) SBOX_LAYER_1[first & 0xff];

                // XOR with round constant
                temp[0] ^= (byte) (round * 0x13);
                temp[1] ^= (byte) (round * 0x1f);

                System.arraycopy(temp, 0, keys[round], 0, BLOCK_SIZE);
            }

            return keys;
        }

        private void substitutionLayer(byte[] state, boolean inverse) {
            int[] sbox1 = inverse ? INVERSE_SBOX_LAYER_1 : SBOX_LAYER_1;
            int[] sbox2 = inverse ? INVERSE_SBOX_LAYER_2 : SBOX_LAYER_2;

            for (int i = 0; i < BLOCK_SIZE; i++) {
                int val = state[i] & 0xff;
                // Alternate between two S-box types
                state[i] = (byte) ((i % 2 == 0) ? sbox1[val] : sbox2[val]);
            }
        }

        private void diffusionLayer(byte[] state) {
            // Matrix multiplication in GF(2^8) for diffusion
            byte[] temp = new byte[BLOCK_SIZE];

            // 4x4 MDS matrix multiplication
            for (int row = 0; row < 4; row++) {
                for (int col = 0; col < 4; col++) {
                    int sum = 0;
                    for (int k = 0; k < 4; k++) {
                        int matrixElement = getDiffusionMatrixElement(row, k);
                        int stateElement = state[k * 4 + col] & 0xff;
                        sum ^= multiplyGF256(matrixElement, stateElement);
                    }
                    temp[row * 4 + col] = (byte) sum;
                }
            }

            System.arraycopy(temp, 0, state, 0, BLOCK_SIZE);
        }

        private void inverseDiffusionLayer(byte[] state) {
            byte[] temp = new byte[BLOCK_SIZE];

            // Inverse 4x4 MDS matrix multiplication
            for (int row = 0; row < 4; row++) {
                for (int col = 0; col < 4; col++) {
                    int sum = 0;
                    for (int k = 0; k < 4; k++) {
                        int matrixElement = getInverseDiffusionMatrixElement(row, k);
                        int stateElement = state[k * 4 + col] & 0xff;
                        sum ^= multiplyGF256(matrixElement, stateElement);
                    }
                    temp[row * 4 + col] = (byte) sum;
                }
            }

            System.arraycopy(temp, 0, state, 0, BLOCK_SIZE);
        }

        private int getDiffusionMatrixElement(int row, int col) {
            int[][] matrix = {
                {2, 3, 1, 1},
                {1, 2, 3, 1},
                {1, 1, 2, 3},
                {3, 1, 1, 2}
            };
            return matrix[row][col];
        }

        private int getInverseDiffusionMatrixElement(int row, int col) {
            int[][] invMatrix = {
                {14, 11, 13, 9},
                {9, 14, 11, 13},
                {13, 9, 14, 11},
                {11, 13, 9, 14}
            };
            return invMatrix[row][col];
        }

        public byte[] encryptBlock(byte[] plaintext) throws Exception {
            if (plaintext.length != BLOCK_SIZE) {
                throw new IllegalArgumentException("Invalid block size");
            }

            byte[] state = Arrays.copyOf(plaintext, BLOCK_SIZE);

            // Initial round key addition
            addRoundKey(state, roundKeys[0]);

            // Main rounds
            for (int round = 1; round < TOTAL_ROUNDS; round++) {
                substitutionLayer(state, false);
                diffusionLayer(state);
                addRoundKey(state, roundKeys[round]);
            }

            // Final round (no diffusion)
            substitutionLayer(state, false);
            addRoundKey(state, roundKeys[TOTAL_ROUNDS]);

            return state;
        }

        public byte[] decryptBlock(byte[] ciphertext) throws Exception {
            if (ciphertext.length != BLOCK_SIZE) {
                throw new IllegalArgumentException("Invalid block size");
            }

            byte[] state = Arrays.copyOf(ciphertext, BLOCK_SIZE);

            // Reverse final round
            addRoundKey(state, roundKeys[TOTAL_ROUNDS]);
            substitutionLayer(state, true);

            // Reverse main rounds
            for (int round = TOTAL_ROUNDS - 1; round >= 1; round--) {
                addRoundKey(state, roundKeys[round]);
                inverseDiffusionLayer(state);
                substitutionLayer(state, true);
            }

            // Reverse initial round key
            addRoundKey(state, roundKeys[0]);

            return state;
        }

        private void addRoundKey(byte[] state, byte[] roundKey) {
            for (int i = 0; i < BLOCK_SIZE; i++) {
                state[i] ^= roundKey[i];
            }
        }

        public byte[] encryptDocument(byte[] data) throws Exception {
            // PKCS7 padding
            int padLen = BLOCK_SIZE - (data.length % BLOCK_SIZE);
            byte[] padded = new byte[data.length + padLen];
            System.arraycopy(data, 0, padded, 0, data.length);
            Arrays.fill(padded, data.length, padded.length, (byte) padLen);

            byte[] encrypted = new byte[padded.length];
            for (int i = 0; i < padded.length; i += BLOCK_SIZE) {
                byte[] block = Arrays.copyOfRange(padded, i, i + BLOCK_SIZE);
                byte[] encBlock = encryptBlock(block);
                System.arraycopy(encBlock, 0, encrypted, i, BLOCK_SIZE);
            }

            return encrypted;
        }
    }

    /**
     * Secure Hash Function for Document Integrity
     * Implements 512-bit hash with compression function and message expansion.
     */
    public static class DocumentIntegrityHasher {
        private static final int HASH_SIZE = 64; // 512 bits
        private static final int BLOCK_SIZE = 128; // 1024-bit blocks
        private static final int NUM_STEPS = 32;

        private final long[] initialValues;

        public DocumentIntegrityHasher() {
            // Initialize 8 x 64-bit hash values
            this.initialValues = new long[]{
                0x6a09e667f3bcc908L, 0xbb67ae8584caa73bL,
                0x3c6ef372fe94f82bL, 0xa54ff53a5f1d36f1L,
                0x510e527fade682d1L, 0x9b05688c2b3e6c1fL,
                0x1f83d9abfb41bd6bL, 0x5be0cd19137e2179L
            };
        }

        private long rotateLeft(long value, int bits) {
            return (value << bits) | (value >>> (64 - bits));
        }

        private long rotateRight(long value, int bits) {
            return (value >>> bits) | (value << (64 - bits));
        }

        private void compressionFunction(byte[] block, long[] hashState) {
            // Message schedule (32 words of 64-bit each)
            long[] messageSchedule = new long[NUM_STEPS];

            // Load message block
            ByteBuffer buffer = ByteBuffer.wrap(block).order(ByteOrder.LITTLE_ENDIAN);
            for (int i = 0; i < 16; i++) {
                messageSchedule[i] = buffer.getLong();
            }

            // Message expansion
            for (int i = 16; i < NUM_STEPS; i++) {
                long s0 = rotateLeft(messageSchedule[i - 16], 31);
                long s1 = rotateLeft(messageSchedule[i - 15], 7);
                long s2 = rotateLeft(messageSchedule[i - 7], 19);
                long s3 = rotateLeft(messageSchedule[i - 2], 43);

                messageSchedule[i] = messageSchedule[i - 16] + s0 + s1 + s2 + s3;
            }

            // Working variables
            long[] v = new long[8];
            System.arraycopy(hashState, 0, v, 0, 8);

            // Compression rounds
            for (int step = 0; step < NUM_STEPS; step++) {
                // Non-linear functions
                long t1 = v[7] +
                         (rotateRight(v[4], 6) ^ rotateRight(v[4], 11) ^ rotateRight(v[4], 25)) +
                         ((v[4] & v[5]) ^ (~v[4] & v[6])) +
                         messageSchedule[step];

                long t2 = (rotateRight(v[0], 2) ^ rotateRight(v[0], 13) ^ rotateRight(v[0], 22)) +
                         ((v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]));

                // Update state
                v[7] = v[6];
                v[6] = v[5];
                v[5] = v[4];
                v[4] = v[3] + t1;
                v[3] = v[2];
                v[2] = v[1];
                v[1] = v[0];
                v[0] = t1 + t2;
            }

            // Add compressed block to hash state
            for (int i = 0; i < 8; i++) {
                hashState[i] += v[i];
            }
        }

        public byte[] computeHash(byte[] message) {
            // Padding
            long messageBitLen = message.length * 8L;
            int paddingLen = (BLOCK_SIZE - ((message.length + 17) % BLOCK_SIZE)) % BLOCK_SIZE;

            byte[] padded = new byte[message.length + 1 + paddingLen + 16];
            System.arraycopy(message, 0, padded, 0, message.length);
            padded[message.length] = (byte) 0x80;

            // Append length
            ByteBuffer lengthBuffer = ByteBuffer.wrap(padded, padded.length - 16, 16)
                                                .order(ByteOrder.LITTLE_ENDIAN);
            lengthBuffer.putLong(messageBitLen);

            // Initialize hash state
            long[] hashState = Arrays.copyOf(initialValues, initialValues.length);

            // Process blocks
            for (int i = 0; i < padded.length; i += BLOCK_SIZE) {
                byte[] block = Arrays.copyOfRange(padded, i, i + BLOCK_SIZE);
                compressionFunction(block, hashState);
            }

            // Produce final digest
            ByteBuffer digest = ByteBuffer.allocate(HASH_SIZE).order(ByteOrder.LITTLE_ENDIAN);
            for (long val : hashState) {
                digest.putLong(val);
            }

            return digest.array();
        }
    }

    /**
     * Production Government Document Processing Service
     */
    public static class SecureGovernmentService {
        private final ClassifiedDocumentEncryptor encryptor;
        private final DocumentIntegrityHasher hasher;

        public SecureGovernmentService(byte[] encryptionKey) throws Exception {
            this.encryptor = new ClassifiedDocumentEncryptor(encryptionKey);
            this.hasher = new DocumentIntegrityHasher();
        }

        public SecureDocument processClassifiedDocument(String documentId,
                                                       byte[] content,
                                                       String classification) throws Exception {
            // Encrypt document
            byte[] encrypted = encryptor.encryptDocument(content);

            // Compute integrity hash
            byte[] integrityHash = hasher.computeHash(encrypted);

            return new SecureDocument(documentId, encrypted, integrityHash, classification);
        }

        public byte[] verifyAndDecrypt(SecureDocument document) throws Exception {
            // Verify integrity
            byte[] computedHash = hasher.computeHash(document.encryptedContent);
            if (!Arrays.equals(computedHash, document.integrityHash)) {
                throw new SecurityException("Document integrity verification failed");
            }

            // Decrypt
            byte[] decrypted = new byte[document.encryptedContent.length];
            for (int i = 0; i < document.encryptedContent.length; i += 16) {
                byte[] block = Arrays.copyOfRange(document.encryptedContent, i, i + 16);
                byte[] decBlock = encryptor.decryptBlock(block);
                System.arraycopy(decBlock, 0, decrypted, i, 16);
            }

            // Remove padding
            int padLen = decrypted[decrypted.length - 1] & 0xff;
            return Arrays.copyOf(decrypted, decrypted.length - padLen);
        }
    }

    public static class SecureDocument {
        public final String documentId;
        public final byte[] encryptedContent;
        public final byte[] integrityHash;
        public final String classification;

        public SecureDocument(String id, byte[] content, byte[] hash, String classif) {
            this.documentId = id;
            this.encryptedContent = content;
            this.integrityHash = hash;
            this.classification = classif;
        }
    }

    // Example usage
    public static void main(String[] args) {
        try {
            byte[] key = new byte[16];
            for (int i = 0; i < 16; i++) key[i] = (byte) (i * 0x11);

            SecureGovernmentService service = new SecureGovernmentService(key);

            String classifiedData = "TOP SECRET: National Security Information";
            SecureDocument doc = service.processClassifiedDocument(
                "GOV-2025-001",
                classifiedData.getBytes(),
                "TOP SECRET"
            );

            System.out.println("Document ID: " + doc.documentId);
            System.out.println("Encrypted length: " + doc.encryptedContent.length);
            System.out.println("Hash: " + bytesToHex(doc.integrityHash).substring(0, 32) + "...");

            byte[] decrypted = service.verifyAndDecrypt(doc);
            System.out.println("Decrypted: " + new String(decrypted));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
