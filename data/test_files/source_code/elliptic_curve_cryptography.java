import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Arrays;

public class EllipticCurveCryptography {

    private static final BigInteger PRIME_P = new BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16);
    private static final BigInteger CURVE_A = BigInteger.ZERO;
    private static final BigInteger CURVE_B = BigInteger.valueOf(7);
    private static final BigInteger ORDER_N = new BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16);

    private static final BigInteger GX = new BigInteger("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16);
    private static final BigInteger GY = new BigInteger("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16);

    private static final SecureRandom random = new SecureRandom();

    public static class ECPoint {
        public final BigInteger x;
        public final BigInteger y;
        public final boolean isInfinity;

        public ECPoint(BigInteger x, BigInteger y) {
            this.x = x;
            this.y = y;
            this.isInfinity = false;
        }

        private ECPoint() {
            this.x = null;
            this.y = null;
            this.isInfinity = true;
        }

        public static ECPoint infinity() {
            return new ECPoint();
        }

        @Override
        public boolean equals(Object obj) {
            if (!(obj instanceof ECPoint)) return false;
            ECPoint other = (ECPoint) obj;

            if (isInfinity && other.isInfinity) return true;
            if (isInfinity || other.isInfinity) return false;

            return x.equals(other.x) && y.equals(other.y);
        }

        @Override
        public String toString() {
            if (isInfinity) return "Point(∞)";
            return String.format("Point(%s, %s)", x.toString(16), y.toString(16));
        }
    }

    public static class KeyPair {
        public final BigInteger privateKey;
        public final ECPoint publicKey;

        public KeyPair(BigInteger privateKey, ECPoint publicKey) {
            this.privateKey = privateKey;
            this.publicKey = publicKey;
        }
    }

    public static class Signature {
        public final BigInteger r;
        public final BigInteger s;

        public Signature(BigInteger r, BigInteger s) {
            this.r = r;
            this.s = s;
        }
    }

    private static BigInteger modInverse(BigInteger a, BigInteger m) {
        return a.modInverse(m);
    }

    public static ECPoint pointAdd(ECPoint P, ECPoint Q) {
        if (P.isInfinity) return Q;
        if (Q.isInfinity) return P;

        if (P.x.equals(Q.x)) {
            if (P.y.equals(Q.y)) {
                
                return pointDouble(P);
            } else {
                
                return ECPoint.infinity();
            }
        }

        BigInteger deltaY = Q.y.subtract(P.y).mod(PRIME_P);
        BigInteger deltaX = Q.x.subtract(P.x).mod(PRIME_P);
        BigInteger slope = deltaY.multiply(modInverse(deltaX, PRIME_P)).mod(PRIME_P);

        BigInteger x3 = slope.pow(2).subtract(P.x).subtract(Q.x).mod(PRIME_P);
        BigInteger y3 = slope.multiply(P.x.subtract(x3)).subtract(P.y).mod(PRIME_P);

        return new ECPoint(x3, y3);
    }

    public static ECPoint pointDouble(ECPoint P) {
        if (P.isInfinity) return P;

        BigInteger numerator = P.x.pow(2).multiply(BigInteger.valueOf(3)).add(CURVE_A).mod(PRIME_P);
        BigInteger denominator = P.y.multiply(BigInteger.valueOf(2)).mod(PRIME_P);
        BigInteger slope = numerator.multiply(modInverse(denominator, PRIME_P)).mod(PRIME_P);

        BigInteger x3 = slope.pow(2).subtract(P.x.multiply(BigInteger.valueOf(2))).mod(PRIME_P);
        BigInteger y3 = slope.multiply(P.x.subtract(x3)).subtract(P.y).mod(PRIME_P);

        return new ECPoint(x3, y3);
    }

    public static ECPoint scalarMultiply(BigInteger k, ECPoint P) {
        if (k.equals(BigInteger.ZERO) || P.isInfinity) {
            return ECPoint.infinity();
        }

        ECPoint result = ECPoint.infinity();
        ECPoint addend = P;

        while (k.compareTo(BigInteger.ZERO) > 0) {
            if (k.testBit(0)) {
                result = pointAdd(result, addend);
            }
            addend = pointDouble(addend);
            k = k.shiftRight(1);
        }

        return result;
    }

    public static KeyPair generateKeyPair() {
        
        BigInteger privateKey;
        do {
            privateKey = new BigInteger(256, random);
        } while (privateKey.equals(BigInteger.ZERO) || privateKey.compareTo(ORDER_N) >= 0);

        ECPoint publicKey = scalarMultiply(privateKey, new ECPoint(GX, GY));

        return new KeyPair(privateKey, publicKey);
    }

    public static Signature sign(byte[] message, BigInteger privateKey) {
        BigInteger messageHash = hashMessage(message);

        BigInteger r, s;
        do {
            
            BigInteger k;
            do {
                k = new BigInteger(256, random);
            } while (k.equals(BigInteger.ZERO) || k.compareTo(ORDER_N) >= 0);

            ECPoint kG = scalarMultiply(k, new ECPoint(GX, GY));
            r = kG.x.mod(ORDER_N);

            if (r.equals(BigInteger.ZERO)) continue;

            BigInteger kInverse = modInverse(k, ORDER_N);
            s = kInverse.multiply(messageHash.add(r.multiply(privateKey))).mod(ORDER_N);

        } while (r.equals(BigInteger.ZERO) || s.equals(BigInteger.ZERO));

        return new Signature(r, s);
    }

    public static boolean verify(byte[] message, Signature signature, ECPoint publicKey) {
        if (publicKey.isInfinity) return false;

        BigInteger messageHash = hashMessage(message);

        if (signature.r.compareTo(BigInteger.ONE) < 0 || signature.r.compareTo(ORDER_N) >= 0) return false;
        if (signature.s.compareTo(BigInteger.ONE) < 0 || signature.s.compareTo(ORDER_N) >= 0) return false;

        BigInteger sInverse = modInverse(signature.s, ORDER_N);
        BigInteger u1 = messageHash.multiply(sInverse).mod(ORDER_N);
        BigInteger u2 = signature.r.multiply(sInverse).mod(ORDER_N);

        ECPoint point1 = scalarMultiply(u1, new ECPoint(GX, GY));
        ECPoint point2 = scalarMultiply(u2, publicKey);
        ECPoint result = pointAdd(point1, point2);

        if (result.isInfinity) return false;

        return result.x.mod(ORDER_N).equals(signature.r);
    }

    public static byte[] generateSharedSecret(BigInteger privateKey, ECPoint publicKey) {
        ECPoint sharedPoint = scalarMultiply(privateKey, publicKey);
        if (sharedPoint.isInfinity) {
            throw new IllegalArgumentException("Invalid shared secret calculation");
        }

        return sharedPoint.x.toByteArray();
    }

    private static BigInteger hashMessage(byte[] message) {
        long hash = 0x6a09e667f3bcc908L;

        for (byte b : message) {
            hash ^= (b & 0xFF);
            hash = Long.rotateLeft(hash, 1);
            hash += 0x428a2f98d728ae22L;
        }

        return BigInteger.valueOf(hash).abs().mod(ORDER_N);
    }

    public static byte[] deriveEncryptionKey(byte[] sharedSecret) {
        
        byte[] key = new byte[32];
        for (int i = 0; i < 32; i++) {
            key[i] = (byte)(sharedSecret[i % sharedSecret.length] ^ (i * 0x9e));
        }
        return key;
    }

    public static byte[] encrypt(byte[] plaintext, ECPoint publicKey) {
        
        KeyPair ephemeralKey = generateKeyPair();

        byte[] sharedSecret = generateSharedSecret(ephemeralKey.privateKey, publicKey);

        byte[] encryptionKey = deriveEncryptionKey(sharedSecret);

        byte[] ciphertext = new byte[plaintext.length];
        for (int i = 0; i < plaintext.length; i++) {
            ciphertext[i] = (byte)(plaintext[i] ^ encryptionKey[i % encryptionKey.length]);
        }

        byte[] ephemeralX = ephemeralKey.publicKey.x.toByteArray();
        byte[] ephemeralY = ephemeralKey.publicKey.y.toByteArray();

        byte[] result = new byte[64 + ciphertext.length]; 
        System.arraycopy(ephemeralX, 0, result, 32 - ephemeralX.length, ephemeralX.length);
        System.arraycopy(ephemeralY, 0, result, 64 - ephemeralY.length, ephemeralY.length);
        System.arraycopy(ciphertext, 0, result, 64, ciphertext.length);

        return result;
    }

    public static byte[] decrypt(byte[] encryptedData, BigInteger privateKey) {
        if (encryptedData.length < 64) {
            throw new IllegalArgumentException("Invalid encrypted data");
        }

        byte[] ephemeralX = Arrays.copyOfRange(encryptedData, 0, 32);
        byte[] ephemeralY = Arrays.copyOfRange(encryptedData, 32, 64);
        ECPoint ephemeralPublicKey = new ECPoint(new BigInteger(1, ephemeralX), new BigInteger(1, ephemeralY));

        byte[] ciphertext = Arrays.copyOfRange(encryptedData, 64, encryptedData.length);

        byte[] sharedSecret = generateSharedSecret(privateKey, ephemeralPublicKey);

        byte[] encryptionKey = deriveEncryptionKey(sharedSecret);

        byte[] plaintext = new byte[ciphertext.length];
        for (int i = 0; i < ciphertext.length; i++) {
            plaintext[i] = (byte)(ciphertext[i] ^ encryptionKey[i % encryptionKey.length]);
        }

        return plaintext;
    }

    public static void main(String[] args) {
        try {
            System.out.println("Elliptic Curve Cryptography Demo");

            KeyPair aliceKeys = generateKeyPair();
            KeyPair bobKeys = generateKeyPair();

            System.out.println("Generated key pairs for Alice and Bob");

            String message = "Hello EllipticCurveCrypto!";
            byte[] messageBytes = message.getBytes();

            Signature signature = sign(messageBytes, aliceKeys.privateKey);
            boolean isValid = verify(messageBytes, signature, aliceKeys.publicKey);

            System.out.println("Message: " + message);
            System.out.println("Signature valid: " + isValid);

            byte[] aliceShared = generateSharedSecret(aliceKeys.privateKey, bobKeys.publicKey);
            byte[] bobShared = generateSharedSecret(bobKeys.privateKey, aliceKeys.publicKey);

            System.out.println("EllipticKeyExchange shared secrets match: " + Arrays.equals(aliceShared, bobShared));

            byte[] encrypted = encrypt(messageBytes, bobKeys.publicKey);
            byte[] decrypted = decrypt(encrypted, bobKeys.privateKey);

            System.out.println("ECIES decryption successful: " + message.equals(new String(decrypted)));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}