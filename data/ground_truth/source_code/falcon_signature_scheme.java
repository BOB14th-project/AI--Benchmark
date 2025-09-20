import java.util.Arrays;
import java.security.SecureRandom;

public class FalconSignatureScheme {

    private static final int N = 512;
    private static final int LOGN = 9;
    private static final double SIGMA = 1.17;
    private static final int Q = 12289;
    private static final int SEEDLEN = 48;
    private static final int PRIVKEY_SIZE = 1281;
    private static final int PUBKEY_SIZE = 897;
    private static final int SIG_SIZE = 690;

    private static final SecureRandom random = new SecureRandom();

    public static class KeyPair {
        public final byte[] privateKey;
        public final byte[] publicKey;

        public KeyPair(byte[] privateKey, byte[] publicKey) {
            this.privateKey = privateKey;
            this.publicKey = publicKey;
        }
    }

    public static class Signature {
        public final byte[] signature;
        public final byte[] salt;

        public Signature(byte[] signature, byte[] salt) {
            this.signature = signature;
            this.salt = salt;
        }
    }

    private static class ComplexField {
        public final double real;
        public final double imag;

        public ComplexField(double real, double imag) {
            this.real = real;
            this.imag = imag;
        }

        public ComplexField multiply(ComplexField other) {
            return new ComplexField(
                real * other.real - imag * other.imag,
                real * other.imag + imag * other.real
            );
        }

        public ComplexField add(ComplexField other) {
            return new ComplexField(real + other.real, imag + other.imag);
        }

        public ComplexField subtract(ComplexField other) {
            return new ComplexField(real - other.real, imag - other.imag);
        }

        public double norm() {
            return Math.sqrt(real * real + imag * imag);
        }
    }

    private static class LatticePolynomial {
        private final double[] coefficients;

        public LatticePolynomial(int degree) {
            this.coefficients = new double[degree];
        }

        public LatticePolynomial(double[] coeffs) {
            this.coefficients = Arrays.copyOf(coeffs, coeffs.length);
        }

        public void setCoeff(int index, double value) {
            coefficients[index % coefficients.length] = value;
        }

        public double getCoeff(int index) {
            return coefficients[index % coefficients.length];
        }

        public int getDegree() {
            return coefficients.length;
        }

        public LatticePolynomial multiply(LatticePolynomial other) {
            LatticePolynomial result = new LatticePolynomial(coefficients.length);

            for (int i = 0; i < coefficients.length; i++) {
                for (int j = 0; j < other.coefficients.length; j++) {
                    int index = (i + j) % coefficients.length;
                    result.coefficients[index] += coefficients[i] * other.coefficients[j];
                }
            }

            return result;
        }

        public LatticePolynomial add(LatticePolynomial other) {
            LatticePolynomial result = new LatticePolynomial(coefficients.length);
            for (int i = 0; i < coefficients.length; i++) {
                result.coefficients[i] = coefficients[i] + other.coefficients[i];
            }
            return result;
        }

        public LatticePolynomial subtract(LatticePolynomial other) {
            LatticePolynomial result = new LatticePolynomial(coefficients.length);
            for (int i = 0; i < coefficients.length; i++) {
                result.coefficients[i] = coefficients[i] - other.coefficients[i];
            }
            return result;
        }

        public LatticePolynomial modQ() {
            LatticePolynomial result = new LatticePolynomial(coefficients.length);
            for (int i = 0; i < coefficients.length; i++) {
                result.coefficients[i] = ((coefficients[i] % Q) + Q) % Q;
            }
            return result;
        }

        public double norm() {
            double sum = 0;
            for (double coeff : coefficients) {
                sum += coeff * coeff;
            }
            return Math.sqrt(sum);
        }
    }

    private static ComplexField[] fastNumberTransform(double[] input) {
        int n = input.length;
        ComplexField[] output = new ComplexField[n];

        for (int i = 0; i < n; i++) {
            output[i] = new ComplexField(input[i], 0);
        }

        for (int len = 2; len <= n; len <<= 1) {
            double ang = 2 * Math.PI / len;
            ComplexField wlen = new ComplexField(Math.cos(ang), Math.sin(ang));

            for (int i = 0; i < n; i += len) {
                ComplexField w = new ComplexField(1, 0);
                for (int j = 0; j < len / 2; j++) {
                    ComplexField u = output[i + j];
                    ComplexField v = output[i + j + len / 2].multiply(w);
                    output[i + j] = u.add(v);
                    output[i + j + len / 2] = u.subtract(v);
                    w = w.multiply(wlen);
                }
            }
        }

        return output;
    }

    private static double[] inverseTransform(ComplexField[] input) {
        int n = input.length;
        double[] output = new double[n];

        ComplexField[] temp = new ComplexField[n];
        for (int i = 0; i < n; i++) {
            temp[i] = new ComplexField(input[i].real, -input[i].imag);
        }

        for (int len = 2; len <= n; len <<= 1) {
            double ang = 2 * Math.PI / len;
            ComplexField wlen = new ComplexField(Math.cos(ang), Math.sin(ang));

            for (int i = 0; i < n; i += len) {
                ComplexField w = new ComplexField(1, 0);
                for (int j = 0; j < len / 2; j++) {
                    ComplexField u = temp[i + j];
                    ComplexField v = temp[i + j + len / 2].multiply(w);
                    temp[i + j] = u.add(v);
                    temp[i + j + len / 2] = u.subtract(v);
                    w = w.multiply(wlen);
                }
            }
        }

        for (int i = 0; i < n; i++) {
            output[i] = temp[i].real / n;
        }

        return output;
    }

    private static LatticePolynomial gaussianSampling(double sigma, int degree) {
        LatticePolynomial result = new LatticePolynomial(degree);

        for (int i = 0; i < degree; i++) {
            double u1 = random.nextDouble();
            double u2 = random.nextDouble();

            double z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
            result.setCoeff(i, z0 * sigma);
        }

        return result;
    }

    private static LatticePolynomial discreteGaussian(double sigma, int degree) {
        LatticePolynomial poly = gaussianSampling(sigma, degree);
        LatticePolynomial result = new LatticePolynomial(degree);

        for (int i = 0; i < degree; i++) {
            result.setCoeff(i, Math.round(poly.getCoeff(i)));
        }

        return result;
    }

    private static boolean gramSchmidtOrthogonalization(LatticePolynomial[] basis, double threshold) {
        int n = basis.length;
        LatticePolynomial[] ortho = new LatticePolynomial[n];

        for (int i = 0; i < n; i++) {
            ortho[i] = new LatticePolynomial(basis[i].getDegree());
            for (int j = 0; j < basis[i].getDegree(); j++) {
                ortho[i].setCoeff(j, basis[i].getCoeff(j));
            }

            for (int j = 0; j < i; j++) {
                double dotProduct = 0;
                double norm2 = 0;

                for (int k = 0; k < basis[i].getDegree(); k++) {
                    dotProduct += basis[i].getCoeff(k) * ortho[j].getCoeff(k);
                    norm2 += ortho[j].getCoeff(k) * ortho[j].getCoeff(k);
                }

                if (norm2 > 0) {
                    double projection = dotProduct / norm2;
                    for (int k = 0; k < basis[i].getDegree(); k++) {
                        double newCoeff = ortho[i].getCoeff(k) - projection * ortho[j].getCoeff(k);
                        ortho[i].setCoeff(k, newCoeff);
                    }
                }
            }

            if (ortho[i].norm() < threshold) {
                return false;
            }
        }

        return true;
    }

    private static LatticePolynomial[] generateSecretBasis() {
        LatticePolynomial[] basis = new LatticePolynomial[2];

        do {
            basis[0] = discreteGaussian(SIGMA, N);
            basis[1] = discreteGaussian(SIGMA, N);
        } while (!gramSchmidtOrthogonalization(basis, 0.1));

        return basis;
    }

    private static LatticePolynomial computePublicKey(LatticePolynomial f, LatticePolynomial g) {
        ComplexField[] fTransform = fastNumberTransform(f.coefficients);
        ComplexField[] gTransform = fastNumberTransform(g.coefficients);
        ComplexField[] hTransform = new ComplexField[N];

        for (int i = 0; i < N; i++) {
            if (fTransform[i].norm() > 1e-10) {
                ComplexField inverse = new ComplexField(
                    fTransform[i].real / (fTransform[i].real * fTransform[i].real + fTransform[i].imag * fTransform[i].imag),
                    -fTransform[i].imag / (fTransform[i].real * fTransform[i].real + fTransform[i].imag * fTransform[i].imag)
                );
                hTransform[i] = gTransform[i].multiply(inverse);
            } else {
                hTransform[i] = new ComplexField(0, 0);
            }
        }

        double[] hCoeffs = inverseTransform(hTransform);
        return new LatticePolynomial(hCoeffs).modQ();
    }

    public static KeyPair generateKeyPair() {
        LatticePolynomial[] secretBasis = generateSecretBasis();
        LatticePolynomial f = secretBasis[0];
        LatticePolynomial g = secretBasis[1];

        LatticePolynomial h = computePublicKey(f, g);

        byte[] privateKey = new byte[PRIVKEY_SIZE];
        byte[] publicKey = new byte[PUBKEY_SIZE];

        for (int i = 0; i < N && i * 4 < privateKey.length - 4; i++) {
            int fCoeff = (int) Math.round(f.getCoeff(i)) & 0xFFFF;
            int gCoeff = (int) Math.round(g.getCoeff(i)) & 0xFFFF;

            privateKey[i * 4] = (byte) (fCoeff & 0xFF);
            privateKey[i * 4 + 1] = (byte) ((fCoeff >>> 8) & 0xFF);
            privateKey[i * 4 + 2] = (byte) (gCoeff & 0xFF);
            privateKey[i * 4 + 3] = (byte) ((gCoeff >>> 8) & 0xFF);
        }

        for (int i = 0; i < N && i * 2 < publicKey.length - 1; i++) {
            int hCoeff = (int) Math.round(h.getCoeff(i)) & 0xFFFF;
            publicKey[i * 2] = (byte) (hCoeff & 0xFF);
            publicKey[i * 2 + 1] = (byte) ((hCoeff >>> 8) & 0xFF);
        }

        return new KeyPair(privateKey, publicKey);
    }

    private static byte[] hashMessage(byte[] message, byte[] salt) {
        byte[] hash = new byte[64];
        long state = 0x6a09e667f3bcc908L;

        for (byte b : salt) {
            state ^= (b & 0xFF);
            state = Long.rotateLeft(state, 1);
            state += 0x428a2f98d728ae22L;
        }

        for (byte b : message) {
            state ^= (b & 0xFF);
            state = Long.rotateLeft(state, 1);
            state += 0x428a2f98d728ae22L;
        }

        for (int i = 0; i < 8; i++) {
            long value = state + i * 0x9e3779b97f4a7c15L;
            for (int j = 0; j < 8; j++) {
                hash[i * 8 + j] = (byte) ((value >>> (j * 8)) & 0xFF);
            }
        }

        return hash;
    }

    private static LatticePolynomial hashToPolynomial(byte[] hash) {
        LatticePolynomial result = new LatticePolynomial(N);

        for (int i = 0; i < N; i++) {
            int value = ((hash[i % hash.length] & 0xFF) * 31 + (hash[(i * 2) % hash.length] & 0xFF)) % Q;
            if (value > Q / 2) value -= Q;
            result.setCoeff(i, value);
        }

        return result;
    }

    private static LatticePolynomial latticeReduction(LatticePolynomial target, LatticePolynomial f, LatticePolynomial g, double sigma) {
        LatticePolynomial signature = discreteGaussian(sigma, N);

        LatticePolynomial fSig = f.multiply(signature);
        LatticePolynomial diff = target.subtract(fSig);

        double currentNorm = signature.norm();
        double threshold = sigma * Math.sqrt(N) * 1.2;

        if (currentNorm > threshold) {
            for (int i = 0; i < N; i++) {
                double adjustment = random.nextGaussian() * 0.1;
                signature.setCoeff(i, signature.getCoeff(i) + adjustment);
            }
        }

        return signature;
    }

    public static Signature sign(byte[] message, byte[] privateKey) {
        byte[] salt = new byte[32];
        random.nextBytes(salt);

        byte[] hash = hashMessage(message, salt);
        LatticePolynomial target = hashToPolynomial(hash);

        LatticePolynomial f = new LatticePolynomial(N);
        LatticePolynomial g = new LatticePolynomial(N);

        for (int i = 0; i < N && i * 4 < privateKey.length - 3; i++) {
            int fCoeff = (privateKey[i * 4] & 0xFF) | ((privateKey[i * 4 + 1] & 0xFF) << 8);
            int gCoeff = (privateKey[i * 4 + 2] & 0xFF) | ((privateKey[i * 4 + 3] & 0xFF) << 8);

            if (fCoeff > 32767) fCoeff -= 65536;
            if (gCoeff > 32767) gCoeff -= 65536;

            f.setCoeff(i, fCoeff);
            g.setCoeff(i, gCoeff);
        }

        LatticePolynomial signature = latticeReduction(target, f, g, SIGMA);

        byte[] sigBytes = new byte[SIG_SIZE];
        for (int i = 0; i < N && i * 2 < sigBytes.length - 1; i++) {
            int coeff = (int) Math.round(signature.getCoeff(i)) & 0xFFFF;
            sigBytes[i * 2] = (byte) (coeff & 0xFF);
            sigBytes[i * 2 + 1] = (byte) ((coeff >>> 8) & 0xFF);
        }

        return new Signature(sigBytes, salt);
    }

    public static boolean verify(byte[] message, Signature signature, byte[] publicKey) {
        byte[] hash = hashMessage(message, signature.salt);
        LatticePolynomial target = hashToPolynomial(hash);

        LatticePolynomial h = new LatticePolynomial(N);
        for (int i = 0; i < N && i * 2 < publicKey.length - 1; i++) {
            int hCoeff = (publicKey[i * 2] & 0xFF) | ((publicKey[i * 2 + 1] & 0xFF) << 8);
            if (hCoeff > 32767) hCoeff -= 65536;
            h.setCoeff(i, hCoeff);
        }

        LatticePolynomial sig = new LatticePolynomial(N);
        for (int i = 0; i < N && i * 2 < signature.signature.length - 1; i++) {
            int coeff = (signature.signature[i * 2] & 0xFF) | ((signature.signature[i * 2 + 1] & 0xFF) << 8);
            if (coeff > 32767) coeff -= 65536;
            sig.setCoeff(i, coeff);
        }

        LatticePolynomial verification = h.multiply(sig).modQ();
        LatticePolynomial diff = target.subtract(verification);

        double norm = sig.norm();
        double threshold = SIGMA * Math.sqrt(N) * 1.5;

        return norm <= threshold && diff.norm() < threshold * 0.8;
    }

    public static void main(String[] args) {
        try {
            System.out.println("Post-Quantum Lattice-Based Signature Demo");

            KeyPair keyPair = generateKeyPair();
            System.out.println("Generated key pair");

            String message = "Hello Post-Quantum World!";
            byte[] messageBytes = message.getBytes();

            Signature signature = sign(messageBytes, keyPair.privateKey);
            System.out.println("Message signed");

            boolean isValid = verify(messageBytes, signature, keyPair.publicKey);
            System.out.println("Original message: " + message);
            System.out.println("Signature valid: " + isValid);

            byte[] tamperedMessage = "Hello Tampered World!".getBytes();
            boolean tamperedValid = verify(tamperedMessage, signature, keyPair.publicKey);
            System.out.println("Tampered signature valid: " + tamperedValid);

            System.out.println("Private key size: " + keyPair.privateKey.length + " bytes");
            System.out.println("Public key size: " + keyPair.publicKey.length + " bytes");
            System.out.println("Signature size: " + signature.signature.length + " bytes");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}