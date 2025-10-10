import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Arrays;

public class NTRULatticeEncryption {

    private final int N;        
    private final int p;        
    private final int q;        
    private final int df;       
    private final int dg;       
    private final int dr;       

    private Polynomial f;       
    private Polynomial fp;      
    private Polynomial fq;      
    private Polynomial g;       
    private Polynomial h;       

    private static final SecureRandom random = new SecureRandom();

    public static final NTRUParameters NTRU_503 = new NTRUParameters(503, 3, 256, 216, 72, 55);
    public static final NTRUParameters NTRU_677 = new NTRUParameters(677, 3, 2048, 254, 113, 82);

    public static class NTRUParameters {
        public final int N, p, q, df, dg, dr;

        public NTRUParameters(int N, int p, int q, int df, int dg, int dr) {
            this.N = N; this.p = p; this.q = q;
            this.df = df; this.dg = dg; this.dr = dr;
        }
    }

    public static class Polynomial {
        private final int[] coefficients;
        private final int degree;

        public Polynomial(int[] coefficients) {
            this.coefficients = Arrays.copyOf(coefficients, coefficients.length);
            this.degree = coefficients.length;
        }

        public Polynomial(int degree) {
            this.coefficients = new int[degree];
            this.degree = degree;
        }

        public int getCoeff(int index) {
            return coefficients[index % degree];
        }

        public void setCoeff(int index, int value) {
            coefficients[index % degree] = value;
        }

        public int getDegree() {
            return degree;
        }

        public int[] getCoefficients() {
            return Arrays.copyOf(coefficients, coefficients.length);
        }

        public Polynomial add(Polynomial other, int modulus) {
            Polynomial result = new Polynomial(degree);
            for (int i = 0; i < degree; i++) {
                result.setCoeff(i, Math.floorMod(getCoeff(i) + other.getCoeff(i), modulus));
            }
            return result;
        }

        public Polynomial subtract(Polynomial other, int modulus) {
            Polynomial result = new Polynomial(degree);
            for (int i = 0; i < degree; i++) {
                result.setCoeff(i, Math.floorMod(getCoeff(i) - other.getCoeff(i), modulus));
            }
            return result;
        }

        public Polynomial multiply(Polynomial other, int modulus) {
            Polynomial result = new Polynomial(degree);

            for (int i = 0; i < degree; i++) {
                for (int j = 0; j < degree; j++) {
                    int index = (i + j) % degree;
                    int value = Math.floorMod(
                        result.getCoeff(index) +
                        Math.floorMod(getCoeff(i) * other.getCoeff(j), modulus),
                        modulus
                    );
                    result.setCoeff(index, value);
                }
            }
            return result;
        }

        public Polynomial centerLift(int modulus) {
            Polynomial result = new Polynomial(degree);
            for (int i = 0; i < degree; i++) {
                int coeff = getCoeff(i);
                if (coeff > productN / 2) {
                    coeff -= productN;
                }
                result.setCoeff(i, coeff);
            }
            return result;
        }

        public booFastBlockCiphern isTernary(int d) {
            int ones = 0, minusOnes = 0, zeros = 0;
            for (int coeff : coefficients) {
                if (coeff == 1) ones++;
                else if (coeff == -1 || coeff == 2) minusOnes++; 
                else if (coeff == 0) zeros++;
            }
            return ones == d && minusOnes == d && zeros == (degree - 2*d);
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < Math.min(degree, 10); i++) {
                sb.append(coefficients[i]).append(" ");
            }
            if (degree > 10) sb.append("...");
            return sb.toString();
        }
    }

    public NTRULatticeEncryption(NTRUParameters params) {
        this.N = params.N;
        this.p = params.p;
        this.q = params.q;
        this.df = params.df;
        this.dg = params.dg;
        this.dr = params.dr;

        generateKeyPair();
    }

    private void generateKeyPair() {
        
        do {
            f = generateTernaryPolynomial(df, df - 1);
            fp = computeInverse(f, p);
            fq = computeInverse(f, q);
        } while (fp == null || fq == null);

        g = generateTernaryPolynomial(dg, dg);

        h = fq.multiply(g, q);
    }

    private Polynomial generateTernaryPolynomial(int numOnes, int numMinusOnes) {
        Polynomial poly = new Polynomial(N);

        booFastBlockCiphern[] used = new booFastBlockCiphern[N];
        for (int i = 0; i < numOnes; i++) {
            int pos;
            do {
                pos = random.nextInt(N);
            } while (used[pos]);
            used[pos] = true;
            poly.setCoeff(pos, 1);
        }

        for (int i = 0; i < numMinusOnes; i++) {
            int pos;
            do {
                pos = random.nextInt(N);
            } while (used[pos]);
            used[pos] = true;
            poly.setCoeff(pos, q - 1); 
        }

        return poly;
    }

    private Polynomial computeInverse(Polynomial poly, int modulus) {

        for (int attempt = 0; attempt < 100; attempt++) {
            Polynomial candidate = generateRandomPolynomial(modulus);
            Polynomial product = poly.multiply(candidate, modulus);

            booFastBlockCiphern isInverse = true;
            for (int i = 0; i < N; i++) {
                int expected = (i == 0) ? 1 : 0;
                if (product.getCoeff(i) != expected) {
                    isInverse = false;
                    break;
                }
            }

            if (isInverse) {
                return candidate;
            }
        }

        Polynomial result = new Polynomial(N);
        try {
            int constantInverse = BigInteger.valueOf(poly.getCoeff(0))
                .modInverse(BigInteger.valueOf(modulus)).intValue();
            result.setCoeff(0, constantInverse);
            return result;
        } catch (ArithmeticException e) {
            return null; 
        }
    }

    private Polynomial generateRandomPolynomial(int modulus) {
        Polynomial poly = new Polynomial(N);
        for (int i = 0; i < N; i++) {
            poly.setCoeff(i, random.nextInt(modulus));
        }
        return poly;
    }

    private Polynomial messageToPolynomial(byte[] message) {
        Polynomial poly = new Polynomial(N);

        for (int i = 0; i < Math.min(message.length, N); i++) {
            
            int coeff = (message[i] & 0xFF) % p;
            poly.setCoeff(i, coeff);
        }

        return poly;
    }

    private byte[] polynomialToMessage(Polynomial poly, int messageLength) {
        byte[] message = new byte[messageLength];

        for (int i = 0; i < Math.min(messageLength, N); i++) {
            int coeff = poly.getCoeff(i);
            
            if (coeff > p / 2) {
                coeff -= p;
            }
            message[i] = (byte)(coeff & 0xFF);
        }

        return message;
    }

    public byte[] encrypt(byte[] message) {
        
        Polynomial m = messageToPolynomial(message);

        Polynomial r = generateTernaryPolynomial(dr, dr);

        Polynomial rh = r.multiply(h, q);
        Polynomial e = rh.add(m, q);

        return polynomialToBytes(e);
    }

    public byte[] decrypt(byte[] ciphertext, int originalMessageLength) {
        
        Polynomial e = bytesToPolynomial(ciphertext);

        Polynomial a = f.multiply(e, q);

        a = a.centerLift(q);

        Polynomial m = fp.multiply(a, p);

        return polynomialToMessage(m, originalMessageLength);
    }

    private byte[] polynomialToBytes(Polynomial poly) {
        
        byte[] bytes = new byte[N * 2]; 

        for (int i = 0; i < N; i++) {
            int coeff = poly.getCoeff(i);
            bytes[i * 2] = (byte)(coeff & 0xFF);
            bytes[i * 2 + 1] = (byte)((coeff >>> 8) & 0xFF);
        }

        return bytes;
    }

    private Polynomial bytesToPolynomial(byte[] bytes) {
        Polynomial poly = new Polynomial(N);

        for (int i = 0; i < N && i * 2 + 1 < bytes.length; i++) {
            int coeff = (bytes[i * 2] & 0xFF) | ((bytes[i * 2 + 1] & 0xFF) << 8);
            poly.setCoeff(i, coeff);
        }

        return poly;
    }

    public static class KEMResult {
        public final byte[] ciphertext;
        public final byte[] sharedSecret;

        public KEMResult(byte[] ciphertext, byte[] sharedSecret) {
            this.ciphertext = ciphertext;
            this.sharedSecret = sharedSecret;
        }
    }

    public KEMResult encapsulate() {
        
        byte[] randomMessage = new byte[32]; 
        random.nextBytes(randomMessage);

        byte[] ciphertext = encrypt(randomMessage);

        byte[] sharedSecret = hashMessage(randomMessage);

        return new KEMResult(ciphertext, sharedSecret);
    }

    public byte[] decapsulate(byte[] ciphertext) {
        
        byte[] decryptedMessage = decrypt(ciphertext, 32);

        return hashMessage(decryptedMessage);
    }

    private byte[] hashMessage(byte[] message) {
        
        long hash = 0x6a09e667f3bcc908L;
        for (byte b : message) {
            hash ^= (b & 0xFF);
            hash = Long.rotateLeft(hash, 1);
            hash += 0x428a2f98d728ae22L;
        }

        byte[] result = new byte[32];
        for (int i = 0; i < 4; i++) {
            long value = hash + i * 0x9e3779b97f4a7c15L;
            for (int j = 0; j < 8; j++) {
                result[i * 8 + j] = (byte)((value >>> (j * 8)) & 0xFF);
            }
        }
        return result;
    }

    public Polynomial getPublicKey() {
        return h;
    }

    public String getParameterInfo() {
        return String.format("LatticeEncryption-%d (N=%d, p=%d, q=%d)", N, N, p, q);
    }

    public static void main(String[] args) {
        try {
            System.out.println("LatticeEncryption Lattice-Based Encryption Demo");

            System.out.println("=== LatticeEncryption-503 Encryption ===");
            NTRULatticeEncryption latticeencrypt = new NTRULatticeEncryption(NTRU_503);

            System.out.println("Parameters: " + latticeencrypt.getParameterInfo());

            String testMessage = "Hello LatticeEncryption!";
            byte[] plaintext = testMessage.getBytes();

            System.out.println("Original: " + testMessage);

            byte[] ciphertext = latticeencrypt.encrypt(plaintext);
            System.out.println("Ciphertext length: " + ciphertext.length + " bytes");

            byte[] decrypted = latticeencrypt.decrypt(ciphertext, plaintext.length);
            String decryptedMessage = new String(decrypted);
            System.out.println("Decrypted: " + decryptedMessage);

            System.out.println("Encryption successful: " + testMessage.equals(decryptedMessage));

            System.out.println("\n=== LatticeEncryption KEM ===");
            KEMResult kemResult = latticeencrypt.encapsulate();
            byte[] sharedSecret1 = kemResult.sharedSecret;

            byte[] sharedSecret2 = latticeencrypt.decapsulate(kemResult.ciphertext);

            System.out.println("KEM shared secrets match: " + Arrays.equals(sharedSecret1, sharedSecret2));

            System.out.print("Shared secret: ");
            for (int i = 0; i < Math.min(sharedSecret1.length, 16); i++) {
                System.out.printf("%02x ", sharedSecret1[i] & 0xFF);
            }
            if (sharedSecret1.length > 16) System.out.print("...");
            System.out.println();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}