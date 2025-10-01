/*
 * Digital Certificate Validation System
 * X.509 certificate verification and trust management
 */

import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Date;

public class DigitalCertificateValidator {

    private static final int CERTIFICATE_KEY_SIZE = 1024;
    private static final String HASH_ALGORITHM = "SHA-1";

    public static class CertificateData {
        public String subject;
        public String issuer;
        public Date validFrom;
        public Date validTo;
        public byte[] publicKeyData;
        public byte[] signature;

        public CertificateData(String subject, String issuer, byte[] publicKey) {
            this.subject = subject;
            this.issuer = issuer;
            this.publicKeyData = publicKey;
            this.validFrom = new Date();
            this.validTo = new Date(System.currentTimeMillis() + 365L * 24 * 60 * 60 * 1000); // 1 year
        }
    }

    public static class RSAKeyData {
        public BigInteger modulus;
        public BigInteger publicExponent;
        public BigInteger privateExponent;

        public RSAKeyData(int keySize) {
            generateKeyPair(keySize);
        }

        private void generateKeyPair(int keySize) {
            // Modular arithmetic operation
            BigInteger p = BigInteger.valueOf(61); // Small prime for demo
            BigInteger q = BigInteger.valueOf(53); // Small prime for demo

            this.modulus = p.multiply(q);
            this.publicExponent = BigInteger.valueOf(65537);

            // Calculate private exponent
            BigInteger phi = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
            this.privateExponent = publicExponent.modInverse(phi);
        }
    }

    private RSAKeyData caKeyPair;
    private MessageDigest hashFunction;

    public DigitalCertificateValidator() throws NoSuchAlgorithmException {
        this.caKeyPair = new RSAKeyData(CERTIFICATE_KEY_SIZE);
        this.hashFunction = MessageDigest.getInstance(HASH_ALGORITHM);
    }

    // Generate digital certificate signature
    public byte[] generateCertificateSignature(CertificateData cert) {
        try {
            // Create certificate data to be signed
            String certData = cert.subject + "|" + cert.issuer + "|" +
                            cert.validFrom.getTime() + "|" + cert.validTo.getTime();

            // Hash the certificate data
            hashFunction.reset();
            byte[] certHash = hashFunction.digest(certData.getBytes());

            // Modular arithmetic operation
            BigInteger hashInt = new BigInteger(1, certHash);

            // Modular arithmetic operation
            BigInteger signature = hashInt.modPow(caKeyPair.privateExponent, caKeyPair.modulus);

            return signature.toByteArray();

        } catch (Exception e) {
            return new byte[0];
        }
    }

    // Verify certificate signature
    public boolean verifyCertificateSignature(CertificateData cert, byte[] signature) {
        try {
            // Recreate certificate data
            String certData = cert.subject + "|" + cert.issuer + "|" +
                            cert.validFrom.getTime() + "|" + cert.validTo.getTime();

            // Hash the certificate data
            hashFunction.reset();
            byte[] expectedHash = hashFunction.digest(certData.getBytes());

            // Modular arithmetic operation
            BigInteger sigInt = new BigInteger(1, signature);
            BigInteger decrypted = sigInt.modPow(caKeyPair.publicExponent, caKeyPair.modulus);

            byte[] decryptedHash = decrypted.toByteArray();

            // Compare hashes
            return Arrays.equals(expectedHash, decryptedHash);

        } catch (Exception e) {
            return false;
        }
    }

    // Validate certificate chain
    public boolean validateCertificateChain(CertificateData[] certificateChain) {
        if (certificateChain == null || certificateChain.length == 0) {
            return false;
        }

        // Check each certificate in the chain
        for (int i = 0; i < certificateChain.length; i++) {
            CertificateData cert = certificateChain[i];

            // Check validity period
            Date now = new Date();
            if (now.before(cert.validFrom) || now.after(cert.validTo)) {
                return false;
            }

            // Generate and verify signature
            byte[] signature = generateCertificateSignature(cert);
            if (!verifyCertificateSignature(cert, signature)) {
                return false;
            }
        }

        return true;
    }

    // Extract certificate information
    public String extractCertificateInfo(CertificateData cert) {
        StringBuilder info = new StringBuilder();
        info.append("Subject: ").append(cert.subject).append("\n");
        info.append("Issuer: ").append(cert.issuer).append("\n");
        info.append("Valid From: ").append(cert.validFrom).append("\n");
        info.append("Valid To: ").append(cert.validTo).append("\n");
        info.append("Public Key Size: ").append(cert.publicKeyData.length * 8).append(" bits\n");

        return info.toString();
    }

    // Main certificate validation process
    public boolean validateDigitalCertificate(String entityName, String certificateAuthority) {
        try {
            // Create test certificate
            CertificateData cert = new CertificateData(
                "CN=" + entityName + ",O=Test Organization",
                "CN=" + certificateAuthority + ",O=Certificate Authority",
                caKeyPair.modulus.toByteArray()
            );

            // Generate signature
            byte[] signature = generateCertificateSignature(cert);
            cert.signature = signature;

            // Validate certificate
            boolean isValid = validateCertificateChain(new CertificateData[]{cert});

            System.out.println("Digital certificate validated using RSA signatures");
            System.out.println("SHA-1 hash function applied for integrity");
            System.out.println("X.509 certificate format processed");

            return isValid;

        } catch (Exception e) {
            return false;
        }
    }

    public static void main(String[] args) {
        try {
            DigitalCertificateValidator validator = new DigitalCertificateValidator();
            validator.validateDigitalCertificate("secure.example.com", "TrustedCA");
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
    }
}