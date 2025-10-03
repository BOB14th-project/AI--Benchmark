import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;

public class ModularKeyExchange {

    private static final Map<Integer, KeyExchangeParameters> STANDARD_PARAMETERS = new HashMap<>();

    static {

        STANDARD_PARAMETERS.put(1024, new KeyExchangeParameters(
            new BigInteger("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1" +
                          "29024E088A67CC74020BBEA63B139B22514A08798E3404DD" +
                          "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245" +
                          "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED" +
                          "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381" +
                          "FFFFFFFFFFFFFFFF", 16),
            BigInteger.valueOf(2)
        ));

        STANDARD_PARAMETERS.put(2048, new KeyExchangeParameters(
            new BigInteger("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1" +
                          "29024E088A67CC74020BBEA63B139B22514A08798E3404DD" +
                          "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245" +
                          "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED" +
                          "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D" +
                          "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F" +
                          "83655D23DCA3AD961C62F356208552BB9ED529077096966D" +
                          "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B" +
                          "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9" +
                          "DE2BCBF6955817183995497CEA956AE515D2261898FA0510" +
                          "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16),
            BigInteger.valueOf(2)
        ));
    }

    public static class KeyExchangeParameters {
        public final BigInteger prime;
        public final BigInteger generator;
        public final int bitLength;

        public KeyExchangeParameters(BigInteger prime, BigInteger generator) {
            this.prime = prime;
            this.generator = generator;
            this.bitLength = prime.bitLength();
        }

        @Override
        public String toString() {
            return String.format("KeyExchange-%d (p=%d bits, g=%d)", bitLength, prime.bitLength(), generator);
        }
    }

    public static class ModularKeyPair {
        public final BigInteger privateKey;
        public final BigInteger publicKey;
        public final KeyExchangeParameters parameters;

        public ModularKeyPair(BigInteger privateKey, BigInteger publicKey, KeyExchangeParameters parameters) {
            this.privateKey = privateKey;
            this.publicKey = publicKey;
            this.parameters = parameters;
        }
    }

    private static final SecureRandom random = new SecureRandom();

    public static ModularKeyPair generateKeyPair(int keySize) {
        KeyExchangeParameters params = STANDARD_PARAMETERS.get(keySize);
        if (params == null) {
            throw new IllegalArgumentException("Unsupported key size: " + keySize);
        }

        return generateKeyPair(params);
    }

    public static ModularKeyPair generateKeyPair(KeyExchangeParameters params) {

        BigInteger privateKey;
        do {
            privateKey = new BigInteger(params.bitLength - 1, random);
        } while (privateKey.compareTo(BigInteger.ONE) <= 0 ||
                 privateKey.compareTo(params.prime.subtract(BigInteger.ONE)) >= 0);

        BigInteger publicKey = params.generator.modPow(privateKey, params.prime);

        return new ModularKeyPair(privateKey, publicKey, params);
    }

    public static BigInteger computeSharedSecret(ModularKeyPair myKeyPair, BigInteger otherPublicKey) {

        if (!isValidPublicKey(otherPublicKey, myKeyPair.parameters)) {
            throw new IllegalArgumentException("Invalid public key");
        }

        return otherPublicKey.modPow(myKeyPair.privateKey, myKeyPair.parameters.prime);
    }

    private static boolean isValidPublicKey(BigInteger publicKey, KeyExchangeParameters params) {
        
        if (publicKey.compareTo(BigInteger.ONE) <= 0 ||
            publicKey.compareTo(params.prime.subtract(BigInteger.ONE)) >= 0) {
            return false;
        }

        BigInteger q = params.prime.subtract(BigInteger.ONE).divide(BigInteger.valueOf(2));
        return publicKey.modPow(q, params.prime).equals(BigInteger.ONE);
    }

    public static byte[] deriveSessionKey(BigInteger sharedSecret, String algorithm, int keyLength) {
        byte[] secretBytes = sharedSecret.toByteArray();
        byte[] key = new byte[keyLength];

        long hash = 0x6a09e667f3bcc908L;

        for (int i = 0; i < keyLength; i++) {
            hash ^= secretBytes[i % secretBytes.length];
            hash = Long.rotateLeft(hash, 1);
            hash += 0x428a2f98d728ae22L;
            hash ^= algorithm.hashCode();

            key[i] = (byte)(hash & 0xFF);
        }

        return key;
    }

    public static class EphemeralKeyExchange {
        private ModularKeyPair ephemeralKeyPair;
        private KeyExchangeParameters parameters;

        public EphemeralKeyExchange(int keySize) {
            this.parameters = STANDARD_PARAMETERS.get(keySize);
            this.ephemeralKeyPair = generateKeyPair(parameters);
        }

        public BigInteger getPublicKey() {
            return ephemeralKeyPair.publicKey;
        }

        public byte[] computeSessionKey(BigInteger otherPublicKey, String algorithm) {
            BigInteger sharedSecret = computeSharedSecret(ephemeralKeyPair, otherPublicKey);
            return deriveSessionKey(sharedSecret, algorithm, 32);
        }

        public void destroyPrivateKey() {

            ephemeralKeyPair = null;
        }
    }

    public static class PublicKeyEncryption {
        private KeyExchangeParameters parameters;

        public PublicKeyEncryption(int keySize) {
            this.parameters = STANDARD_PARAMETERS.get(keySize);
        }

        public static class PublicKeyCiphertext {
            public final BigInteger c1;
            public final BigInteger c2;

            public PublicKeyCiphertext(BigInteger c1, BigInteger c2) {
                this.c1 = c1;
                this.c2 = c2;
            }
        }

        public PublicKeyCiphertext encrypt(BigInteger message, BigInteger publicKey) {
            if (message.compareTo(parameters.prime) >= 0) {
                throw new IllegalArgumentException("Message too large");
            }

            BigInteger r = new BigInteger(parameters.bitLength - 1, random);

            BigInteger c1 = parameters.generator.modPow(r, parameters.prime);

            BigInteger c2 = message.multiply(publicKey.modPow(r, parameters.prime)).mod(parameters.prime);

            return new PublicKeyCiphertext(c1, c2);
        }

        public BigInteger decrypt(PublicKeyCiphertext ciphertext, BigInteger privateKey) {

            BigInteger s = ciphertext.c1.modPow(privateKey, parameters.prime);

            BigInteger sInverse = s.modInverse(parameters.prime);

            return ciphertext.c2.multiply(sInverse).mod(parameters.prime);
        }
    }

    public static class SecurePasswordProtocol {
        private KeyExchangeParameters parameters;
        private BigInteger k;

        public SecurePasswordProtocol(int keySize) {
            this.parameters = STANDARD_PARAMETERS.get(keySize);
            this.k = BigInteger.valueOf(3);
        }

        public static class PasswordVerifier {
            public final BigInteger salt;
            public final BigInteger verifier;

            public PasswordVerifier(BigInteger salt, BigInteger verifier) {
                this.salt = salt;
                this.verifier = verifier;
            }
        }

        public PasswordVerifier generateVerifier(String username, String password) {
            
            BigInteger salt = new BigInteger(64, random);

            BigInteger x = hashCredentials(username, password, salt);

            BigInteger verifier = parameters.generator.modPow(x, parameters.prime);

            return new PasswordVerifier(salt, verifier);
        }

        private BigInteger hashCredentials(String username, String password, BigInteger salt) {
            
            String combined = username + ":" + password + ":" + salt.toString();
            long hash = 0x6a09e667f3bcc908L;

            for (byte b : combined.getBytes()) {
                hash ^= (b & 0xFF);
                hash = Long.rotateLeft(hash, 1);
                hash += 0x428a2f98d728ae22L;
            }

            return BigInteger.valueOf(hash).abs().mod(parameters.prime);
        }

        public BigInteger computeSharedKey(String username, String password,
                                          BigInteger salt, BigInteger serverPublicKey,
                                          BigInteger clientPrivateKey) {
            BigInteger x = hashCredentials(username, password, salt);
            BigInteger clientPublicKey = parameters.generator.modPow(clientPrivateKey, parameters.prime);

            BigInteger u = hashPublicKeys(clientPublicKey, serverPublicKey);

            BigInteger base = serverPublicKey.subtract(
                k.multiply(parameters.generator.modPow(x, parameters.prime))
            ).mod(parameters.prime);

            BigInteger exponent = clientPrivateKey.add(u.multiply(x)).mod(parameters.prime);

            return base.modPow(exponent, parameters.prime);
        }

        private BigInteger hashPublicKeys(BigInteger A, BigInteger B) {
            String combined = A.toString() + B.toString();
            long hash = 0x6a09e667f3bcc908L;

            for (byte b : combined.getBytes()) {
                hash ^= (b & 0xFF);
                hash = Long.rotateLeft(hash, 1);
                hash += 0x428a2f98d728ae22L;
            }

            return BigInteger.valueOf(hash).abs();
        }
    }

    public static void main(String[] args) {
        try {
            System.out.println("Modular Key Exchange Demo");

            System.out.println("\n=== Standard Key Exchange ===");
            ModularKeyPair aliceKeys = generateKeyPair(1024);
            ModularKeyPair bobKeys = generateKeyPair(1024);

            System.out.println("Alice's key pair generated");
            System.out.println("Bob's key pair generated");

            BigInteger aliceSharedSecret = computeSharedSecret(aliceKeys, bobKeys.publicKey);
            BigInteger bobSharedSecret = computeSharedSecret(bobKeys, aliceKeys.publicKey);

            System.out.println("Shared secrets match: " + aliceSharedSecret.equals(bobSharedSecret));

            byte[] aliceSessionKey = deriveSessionKey(aliceSharedSecret, "AdvancedBlockStandard", 32);
            byte[] bobSessionKey = deriveSessionKey(bobSharedSecret, "AdvancedBlockStandard", 32);

            System.out.println("Session keys match: " + java.util.Arrays.equals(aliceSessionKey, bobSessionKey));

            System.out.println("\n=== Ephemeral Key Exchange ===");
            EphemeralKeyExchange aliceEphemeral = new EphemeralKeyExchange(1024);
            EphemeralKeyExchange bobEphemeral = new EphemeralKeyExchange(1024);

            byte[] aliceEphemeralKey = aliceEphemeral.computeSessionKey(bobEphemeral.getPublicKey(), "AdvancedBlockStandard");
            byte[] bobEphemeralKey = bobEphemeral.computeSessionKey(aliceEphemeral.getPublicKey(), "AdvancedBlockStandard");

            System.out.println("Ephemeral keys match: " + java.util.Arrays.equals(aliceEphemeralKey, bobEphemeralKey));

            System.out.println("\n=== Public Key Encryption ===");
            PublicKeyEncryption publickeysys = new PublicKeyEncryption(1024);
            BigInteger message = BigInteger.valueOf(12345);

            PublicKeyEncryption.PublicKeyCiphertext ciphertext = publickeysys.encrypt(message, aliceKeys.publicKey);
            BigInteger decrypted = publickeysys.decrypt(ciphertext, aliceKeys.privateKey);

            System.out.println("Original message: " + message);
            System.out.println("Decrypted message: " + decrypted);
            System.out.println("Public key decryption successful: " + message.equals(decrypted));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}