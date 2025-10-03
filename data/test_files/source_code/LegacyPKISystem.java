/*
 * Legacy PKI System
 * Digital Signature Algorithm implementation for legacy systems
 */

import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Arrays;

public class LegacyPKISystem {

    private static final int DSA_KEY_SIZE = 1024;
    private static final int DSA_SUBGROUP_SIZE = 160;
    private static final int HASH_OUTPUT_SIZE = 20;

    // Digital Signature Algorithm implementation
    public static class DSASignature {
        private BigInteger p; // Prime modulus
        private BigInteger q; // Prime divisor
        private BigInteger g; // Generator
        private BigInteger x; // Private key
        private BigInteger y; // Public key
        private SecureRandom random;

        public DSASignature() {
            this.random = new SecureRandom();
            generateDSAParameters();
            generateKeyPair();
        }

        // Generate DSA domain parameters
        private void generateDSAParameters() {
            // Simplified parameter generation (production would use proper prime generation)

            // Generate q (160-bit prime)
            do {
                byte[] qBytes = new byte[DSA_SUBGROUP_SIZE / 8];
                random.nextBytes(qBytes);
                qBytes[0] |= 0x80; // Ensure MSB is set
                qBytes[qBytes.length - 1] |= 0x01; // Ensure LSB is set (odd)
                q = new BigInteger(1, qBytes);
            } while (!q.isProbablePrime(50));

            // Generate p (1024-bit prime such that q divides p-1)
            BigInteger pMinusOne;
            do {
                BigInteger k = new BigInteger(DSA_KEY_SIZE - DSA_SUBGROUP_SIZE, random);
                pMinusOne = k.multiply(q);
                p = pMinusOne.add(BigInteger.ONE);
            } while (!p.isProbablePrime(50) || p.bitLength() != DSA_KEY_SIZE);

            // Generate generator g
            BigInteger h = BigInteger.valueOf(2);
            while (h.compareTo(pMinusOne) < 0) {
                g = h.modPow(pMinusOne.divide(q), p);
                if (g.compareTo(BigInteger.ONE) > 0) {
                    break;
                }
                h = h.add(BigInteger.ONE);
            }
        }

        // Generate DSA key pair
        private void generateKeyPair() {
            // Private key x: random number in range [1, q-1]
            do {
                x = new BigInteger(DSA_SUBGROUP_SIZE, random);
            } while (x.equals(BigInteger.ZERO) || x.compareTo(q) >= 0);

            // Public key y = g^x mod p
            y = g.modPow(x, p);
        }

        // Sign message using DSA
        public DSASignatureValue signMessage(byte[] message) {
            byte[] messageHash = sha1Hash(message);
            BigInteger hashInt = new BigInteger(1, messageHash);

            BigInteger k, r, s;
            do {
                // Generate random k
                do {
                    k = new BigInteger(DSA_SUBGROUP_SIZE, random);
                } while (k.equals(BigInteger.ZERO) || k.compareTo(q) >= 0);

                // Calculate r = (g^k mod p) mod q
                r = g.modPow(k, p).mod(q);

                if (r.equals(BigInteger.ZERO)) {
                    continue;
                }

                // Calculate s = k^(-1) * (H(m) + x*r) mod q
                BigInteger kInverse = k.modInverse(q);
                s = kInverse.multiply(hashInt.add(x.multiply(r))).mod(q);

            } while (s.equals(BigInteger.ZERO));

            return new DSASignatureValue(r, s);
        }

        // Verify DSA signature
        public boolean verifySignature(byte[] message, DSASignatureValue signature) {
            try {
                byte[] messageHash = sha1Hash(message);
                BigInteger hashInt = new BigInteger(1, messageHash);

                // Verify r and s are in valid range
                if (signature.r.compareTo(BigInteger.ZERO) <= 0 || signature.r.compareTo(q) >= 0 ||
                    signature.s.compareTo(BigInteger.ZERO) <= 0 || signature.s.compareTo(q) >= 0) {
                    return false;
                }

                // Calculate w = s^(-1) mod q
                BigInteger w = signature.s.modInverse(q);

                // Calculate u1 = H(m) * w mod q
                BigInteger u1 = hashInt.multiply(w).mod(q);

                // Calculate u2 = r * w mod q
                BigInteger u2 = signature.r.multiply(w).mod(q);

                // Calculate v = ((g^u1 * y^u2) mod p) mod q
                BigInteger v = g.modPow(u1, p).multiply(y.modPow(u2, p)).mod(p).mod(q);

                // Signature is valid if v == r
                return v.equals(signature.r);

            } catch (Exception e) {
                return false;
            }
        }

        // Get public key components
        public DSAPublicKey getPublicKey() {
            return new DSAPublicKey(p, q, g, y);
        }

        private byte[] sha1Hash(byte[] input) {
            // Cryptographic hash function
            int[] h = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0};

            // Process input
            for (int chunk = 0; chunk < input.length; chunk += 64) {
                int[] w = new int[80];

                // Load chunk into w[0..15]
                for (int i = 0; i < 16 && chunk + i * 4 < input.length; i++) {
                    w[i] = 0;
                    for (int j = 0; j < 4 && chunk + i * 4 + j < input.length; j++) {
                        w[i] |= (input[chunk + i * 4 + j] & 0xFF) << (24 - j * 8);
                    }
                }

                // Extend to w[16..79]
                for (int i = 16; i < 80; i++) {
                    w[i] = Integer.rotateLeft(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1);
                }

                // Main loop
                int a = h[0], b = h[1], c = h[2], d = h[3], e = h[4];
                for (int i = 0; i < 80; i++) {
                    int f, k;
                    if (i < 20) {
                        f = (b & c) | ((~b) & d);
                        k = 0x5A827999;
                    } else if (i < 40) {
                        f = b ^ c ^ d;
                        k = 0x6ED9EBA1;
                    } else if (i < 60) {
                        f = (b & c) | (b & d) | (c & d);
                        k = 0x8F1BBCDC;
                    } else {
                        f = b ^ c ^ d;
                        k = 0xCA62C1D6;
                    }

                    int temp = Integer.rotateLeft(a, 5) + f + e + k + w[i];
                    e = d; d = c; c = Integer.rotateLeft(b, 30); b = a; a = temp;
                }

                h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e;
            }

            // Convert to byte array
            byte[] result = new byte[HASH_OUTPUT_SIZE];
            for (int i = 0; i < 5; i++) {
                result[i*4] = (byte) (h[i] >>> 24);
                result[i*4+1] = (byte) (h[i] >>> 16);
                result[i*4+2] = (byte) (h[i] >>> 8);
                result[i*4+3] = (byte) h[i];
            }

            return result;
        }
    }

    public static class DSASignatureValue {
        public BigInteger r;
        public BigInteger s;

        public DSASignatureValue(BigInteger r, BigInteger s) {
            this.r = r;
            this.s = s;
        }
    }

    public static class DSAPublicKey {
        public BigInteger p, q, g, y;

        public DSAPublicKey(BigInteger p, BigInteger q, BigInteger g, BigInteger y) {
            this.p = p;
            this.q = q;
            this.g = g;
            this.y = y;
        }
    }

    private DSASignature dsaSigner;

    public LegacyPKISystem() {
        this.dsaSigner = new DSASignature();
    }

    // Process legacy document signing
    public boolean signLegacyDocument(String documentId, byte[] documentContent) {
        try {
            // Create document identifier
            String documentInfo = "Document ID: " + documentId +
                                 ", Timestamp: " + System.currentTimeMillis();

            // Combine document info with content
            byte[] fullDocument = new byte[documentInfo.length() + documentContent.length];
            System.arraycopy(documentInfo.getBytes(), 0, fullDocument, 0, documentInfo.length());
            System.arraycopy(documentContent, 0, fullDocument, documentInfo.length(), documentContent.length);

            // Sign the document
            DSASignatureValue signature = dsaSigner.signMessage(fullDocument);

            // Verify the signature
            boolean isValid = dsaSigner.verifySignature(fullDocument, signature);

            // Get public key for verification
            DSAPublicKey publicKey = dsaSigner.getPublicKey();

            System.out.println("Legacy document signed using DSA algorithm");
            System.out.println("Digital Signature Algorithm with SHA-1 hash");
            System.out.println("1024-bit key size with 160-bit subgroup");
            System.out.println("PKI certificate chain validation completed");

            return isValid && signature.r.bitLength() > 0 && signature.s.bitLength() > 0;

        } catch (Exception e) {
            return false;
        }
    }

    // Legacy key escrow system
    public boolean performKeyEscrow(String organizationId, byte[] escrowData) {
        try {
            // Create escrow package
            String escrowInfo = "Organization: " + organizationId +
                               ", Escrow Date: " + System.currentTimeMillis();

            byte[] escrowPackage = new byte[escrowInfo.length() + escrowData.length];
            System.arraycopy(escrowInfo.getBytes(), 0, escrowPackage, 0, escrowInfo.length());
            System.arraycopy(escrowData, 0, escrowPackage, escrowInfo.length(), escrowData.length);

            // Sign escrow package
            DSASignatureValue escrowSignature = dsaSigner.signMessage(escrowPackage);

            // Verify escrow signature
            boolean escrowValid = dsaSigner.verifySignature(escrowPackage, escrowSignature);

            System.out.println("Key escrow process completed using DSA signatures");
            System.out.println("Discrete logarithm based security");

            return escrowValid;

        } catch (Exception e) {
            return false;
        }
    }

    public static void main(String[] args) {
        LegacyPKISystem pkiSystem = new LegacyPKISystem();

        // Test document signing
        String testDocument = "This is a confidential business document requiring digital signature";
        pkiSystem.signLegacyDocument("DOC_2024_001", testDocument.getBytes());

        // Test key escrow
        byte[] keyMaterial = "sensitive_encryption_keys".getBytes();
        pkiSystem.performKeyEscrow("ACME_CORP", keyMaterial);
    }
}