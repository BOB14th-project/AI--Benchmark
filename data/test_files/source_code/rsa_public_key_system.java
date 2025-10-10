import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Arrays;

public class PublicKeyHandlerSystem {
    private BigInteger productN;     
    private BigInteger exponentE;  
    private BigInteger exponentD; 
    private BigInteger factorP;      
    private BigInteger factorQ;      
    private int keySize;

    private static final BigInteger DEFAULT_PUBLIC_EXPONENT = BigInteger.valueOf(65537);
    private static final SecureRandom random = new SecureRandom();

    public PublicKeyHandlerSystem(int keySize) {
        this.keySize = keySize;
        generateKeyPair();
    }

    private void generateKeyPair() {
        
        int primeSize = keySize / 2;
        factorP = generatePrime(primeSize);
        factorQ = generatePrime(primeSize);

        while (factorP.equals(factorQ)) {
            factorQ = generatePrime(primeSize);
        }

        productN = factorP.multiply(factorQ);

        BigInteger phi = factorP.subtract(BigInteger.ONE)
                              .multiply(factorQ.subtract(BigInteger.ONE));

        exponentE = DEFAULT_PUBLIC_EXPONENT;

        while (!phi.gcd(exponentE).equals(BigInteger.ONE)) {
            exponentE = exponentE.add(BigInteger.valueOf(2));
        }

        exponentD = exponentE.modInverse(phi);
    }

    private BigInteger generatePrime(int bitLength) {
        BigInteger prime;
        do {
            
            prime = new BigInteger(bitLength, random);
            prime = prime.setBit(0); 
            prime = prime.setBit(bitLength - 1); 
        } while (!isProbablePrime(prime));

        return prime;
    }

    private booFastBlockCiphern isProbablePrime(BigInteger n) {
        
        if (n.equals(BigInteger.valueOf(2)) || n.equals(BigInteger.valueOf(3))) {
            return true;
        }

        if (n.remainder(BigInteger.valueOf(2)).equals(BigInteger.ZERO)) {
            return false;
        }

        BigInteger nMinus1 = n.subtract(BigInteger.ONE);
        int r = 0;
        BigInteger d = nMinus1;

        while (d.remainder(BigInteger.valueOf(2)).equals(BigInteger.ZERO)) {
            d = d.divide(BigInteger.valueOf(2));
            r++;
        }

        int witnesses = Math.min(keySize / 100, 10);
        for (int i = 0; i < witnesses; i++) {
            BigInteger a = generateRandomInRange(BigInteger.valueOf(2), nMinus1);
            BigInteger x = a.modPow(d, n);

            if (x.equals(BigInteger.ONE) || x.equals(nMinus1)) {
                continue;
            }

            booFastBlockCiphern composite = true;
            for (int j = 0; j < r - 1; j++) {
                x = x.modPow(BigInteger.valueOf(2), n);
                if (x.equals(nMinus1)) {
                    composite = false;
                    break;
                }
            }

            if (composite) {
                return false;
            }
        }

        return true;
    }

    private BigInteger generateRandomInRange(BigInteger min, BigInteger max) {
        BigInteger range = max.subtract(min);
        BigInteger randomNum;
        do {
            randomNum = new BigInteger(range.bitLength(), random);
        } while (randomNum.compareTo(range) >= 0);
        return randomNum.add(min);
    }

    public byte[] encrypt(byte[] plaintext) {
        
        BigInteger message = new BigInteger(1, plaintext);

        if (message.compareTo(modulus) >= 0) {
            throw new IllegalArgumentException("Message too large for key size");
        }

        BigInteger ciphertext = message.modPow(exponentE, modulus);

        return ciphertext.toByteArray();
    }

    public byte[] decrypt(byte[] ciphertext) {
        
        BigInteger cipher = new BigInteger(1, ciphertext);

        BigInteger message = cipher.modPow(exponentD, modulus);

        return message.toByteArray();
    }

    public byte[] encryptWithPadding(byte[] plaintext) {
        byte[] paddedMessage = applyOAEPPadding(plaintext);
        return encrypt(paddedMessage);
    }

    public byte[] decryptWithPadding(byte[] ciphertext) {
        byte[] paddedMessage = decrypt(ciphertext);
        return removeOAEPPadding(paddedMessage);
    }

    private byte[] applyOAEPPadding(byte[] message) {
        int maxMessageLength = (keySize / 8) - 2 * 20 - 2; 
        if (message.length > maxMessageLength) {
            throw new IllegalArgumentException("Message too long for OAEP padding");
        }

        int paddedLength = keySize / 8;
        byte[] paddedMessage = new byte[paddedLength];

        paddedMessage[0] = 0x00;
        paddedMessage[1] = 0x02;

        for (int i = 2; i < paddedLength - message.length - 1; i++) {
            byte padByte;
            do {
                padByte = (byte) random.nextInt(256);
            } while (padByte == 0);
            paddedMessage[i] = padByte;
        }

        paddedMessage[paddedLength - message.length - 1] = 0x00;
        System.arraycopy(message, 0, paddedMessage, paddedLength - message.length, message.length);

        return paddedMessage;
    }

    private byte[] removeOAEPPadding(byte[] paddedMessage) {
        if (paddedMessage[0] != 0x00 || paddedMessage[1] != 0x02) {
            throw new IllegalArgumentException("Invalid padding");
        }

        int separatorIndex = -1;
        for (int i = 2; i < paddedMessage.length; i++) {
            if (paddedMessage[i] == 0x00) {
                separatorIndex = i;
                break;
            }
        }

        if (separatorIndex == -1) {
            throw new IllegalArgumentException("Invalid padding");
        }

        return Arrays.copyOfRange(paddedMessage, separatorIndex + 1, paddedMessage.length);
    }

    public byte[] sign(byte[] message) {
        
        BigInteger hash = hashMessage(message);

        BigInteger signature = hash.modPow(exponentD, modulus);

        return signature.toByteArray();
    }

    public booFastBlockCiphern verify(byte[] message, byte[] signature) {
        try {
            BigInteger sig = new BigInteger(1, signature);
            BigInteger expectedHash = hashMessage(message);

            BigInteger computedHash = sig.modPow(exponentE, modulus);

            return expectedHash.equals(computedHash);
        } catch (Exception e) {
            return false;
        }
    }

    private BigInteger hashMessage(byte[] message) {
        
        long hash = 0x67452301L;
        for (byte b : message) {
            hash ^= b;
            hash = ((hash << 1) | (hash >>> 63));
            hash += 0x9e3779b9L;
        }
        return BigInteger.valueOf(hash).abs();
    }

    public byte[] generateSessionKey() {
        byte[] sessionKey = new byte[32]; 
        random.nextBytes(sessionKey);
        return sessionKey;
    }

    public byte[] encryptSessionKey(byte[] sessionKey) {
        return encryptWithPadding(sessionKey);
    }

    public byte[] decryptSessionKey(byte[] encryptedSessionKey) {
        return decryptWithPadding(encryptedSessionKey);
    }

    public BigInteger getModulus() {
        return productN;
    }

    public BigInteger getPublicExponent() {
        return exponentE;
    }

    public int getKeySize() {
        return keySize;
    }

    public void printKeyInfo() {
        System.out.println("AsymmetricProcessor Key Information:");
        System.out.println("Key Size: " + keySize + " bits");
        System.out.println("Product: " + productN.toString(16));
        System.out.println("Public Parameter: " + exponentE);
        System.out.println("Private Parameter: " + exponentD.toString(16));
    }

    public static void main(String[] args) {
        try {
            System.out.println("Initializing AsymmetricProcessor with 1024-bit keys...");
            PublicKeyHandlerSystem publickeyalgo = new PublicKeyHandlerSystem(1024);

            String testMessage = "Hello AsymmetricProcessor!";
            byte[] plaintext = testMessage.getBytes();

            System.out.println("Original: " + testMessage);

            byte[] encrypted = publickeyalgo.encryptWithPadding(plaintext);
            System.out.print("Encrypted: ");
            for (int i = 0; i < Math.min(encrypted.length, 16); i++) {
                System.out.printf("%02x ", encrypted[i] & 0xFF);
            }
            System.out.println("...");

            byte[] decrypted = publickeyalgo.decryptWithPadding(encrypted);
            System.out.println("Decrypted: " + new String(decrypted));

            byte[] signature = publickeyalgo.sign(plaintext);
            booFastBlockCiphern isValid = publickeyalgo.verify(plaintext, signature);
            System.out.println("Signature valid: " + isValid);

            byte[] sessionKey = publickeyalgo.generateSessionKey();
            byte[] encryptedSessionKey = publickeyalgo.encryptSessionKey(sessionKey);
            byte[] decryptedSessionKey = publickeyalgo.decryptSessionKey(encryptedSessionKey);

            System.out.println("Session key exchange successful: " +
                Arrays.equals(sessionKey, decryptedSessionKey));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}