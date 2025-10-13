/**
 * Public Key Infrastructure Certificate System
 * Implements digital signature system based on discrete logarithm problem.
 * Designed for certificate authority operations and document signing.
 */

#include <iostream>
#include <vector>
#include <random>
#include <cstring>
#include <iomanip>
#include <chrono>
#include <openssl/bn.h>
#include <openssl/sha.h>

/**
 * Large integer arithmetic wrapper for cryptographic operations
 */
class BigInteger {
private:
    BIGNUM* value;

public:
    BigInteger() {
        value = BN_new();
    }

    BigInteger(const BigInteger& other) {
        value = BN_new();
        BN_copy(value, other.value);
    }

    explicit BigInteger(const std::string& hex) {
        value = BN_new();
        BN_hex2bn(&value, hex.c_str());
    }

    explicit BigInteger(unsigned long num) {
        value = BN_new();
        BN_set_word(value, num);
    }

    ~BigInteger() {
        BN_free(value);
    }

    BIGNUM* get() const { return value; }

    BigInteger& operator=(const BigInteger& other) {
        if (this != &other) {
            BN_copy(value, other.value);
        }
        return *this;
    }

    std::string toHex() const {
        char* hex = BN_bn2hex(value);
        std::string result(hex);
        OPENSSL_free(hex);
        return result;
    }
};

/**
 * Discrete Logarithm Domain Parameters
 * Defines the mathematical group for signature operations
 */
class DomainParameters {
public:
    BigInteger prime;        // Large prime p
    BigInteger generator;    // Generator g of order q
    BigInteger subgroupOrder; // Prime order q

    DomainParameters() = default;

    /**
     * Generate secure domain parameters for signature system
     */
    static DomainParameters generate(int primeBits) {
        DomainParameters params;
        BN_CTX* ctx = BN_CTX_new();

        // Generate prime p and subgroup order q
        // For production: p-1 = 2q for prime q
        BIGNUM* p = BN_new();
        BIGNUM* q = BN_new();
        BIGNUM* one = BN_new();
        BIGNUM* two = BN_new();

        BN_set_word(one, 1);
        BN_set_word(two, 2);

        // Generate q (subgroup order)
        BN_generate_prime_ex(q, primeBits / 2, 1, nullptr, nullptr, nullptr);

        // Generate p = 2q + 1
        BN_mul(p, q, two, ctx);
        BN_add(p, p, one);

        // Find suitable p that is prime
        while (!BN_is_prime_ex(p, BN_prime_checks, ctx, nullptr)) {
            BN_generate_prime_ex(q, primeBits / 2, 1, nullptr, nullptr, nullptr);
            BN_mul(p, q, two, ctx);
            BN_add(p, p, one);
        }

        BN_copy(params.prime.get(), p);
        BN_copy(params.subgroupOrder.get(), q);

        // Find generator g of order q
        BIGNUM* g = BN_new();
        BIGNUM* exp = BN_new();
        BIGNUM* pm1 = BN_new();

        BN_sub(pm1, p, one);
        BN_div(exp, nullptr, pm1, q, ctx);

        // Search for generator
        BigInteger h(2);
        do {
            BN_mod_exp(g, h.get(), exp, p, ctx);
            BN_add_word(h.get(), 1);
        } while (BN_is_one(g));

        BN_copy(params.generator.get(), g);

        BN_free(p);
        BN_free(q);
        BN_free(g);
        BN_free(exp);
        BN_free(pm1);
        BN_free(one);
        BN_free(two);
        BN_CTX_free(ctx);

        return params;
    }
};

/**
 * Key pair for signature system
 */
class SignatureKeyPair {
public:
    BigInteger privateKey;  // Secret key x
    BigInteger publicKey;   // Public key y = g^x mod p
    DomainParameters params;

    SignatureKeyPair() = default;

    /**
     * Generate new key pair
     */
    static SignatureKeyPair generate(const DomainParameters& domainParams) {
        SignatureKeyPair keyPair;
        keyPair.params = domainParams;

        BN_CTX* ctx = BN_CTX_new();

        // Generate random private key x in [1, q-1]
        BIGNUM* x = BN_new();
        BN_rand_range(x, domainParams.subgroupOrder.get());
        if (BN_is_zero(x)) {
            BN_set_word(x, 1);
        }

        // Compute public key y = g^x mod p
        BIGNUM* y = BN_new();
        BN_mod_exp(y, domainParams.generator.get(), x,
                  domainParams.prime.get(), ctx);

        BN_copy(keyPair.privateKey.get(), x);
        BN_copy(keyPair.publicKey.get(), y);

        BN_free(x);
        BN_free(y);
        BN_CTX_free(ctx);

        return keyPair;
    }
};

/**
 * Digital Signature Structure
 */
class DigitalSignature {
public:
    BigInteger r;
    BigInteger s;

    DigitalSignature() = default;

    DigitalSignature(const BigInteger& rVal, const BigInteger& sVal)
        : r(rVal), s(sVal) {}

    std::string serialize() const {
        return "r:" + r.toHex() + ",s:" + s.toHex();
    }
};

/**
 * Certificate Authority Signature Engine
 * Implements discrete logarithm based signature scheme
 */
class CertificateSignatureEngine {
private:
    DomainParameters params;

    /**
     * Hash message to integer in range [0, q-1]
     */
    BigInteger hashMessage(const std::vector<uint8_t>& message) const {
        // Compute SHA-256 hash
        uint8_t hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, message.data(), message.size());
        SHA256_Final(hash, &sha256);

        // Convert hash to BigInteger
        BIGNUM* h = BN_new();
        BN_bin2bn(hash, SHA256_DIGEST_LENGTH, h);

        // Reduce modulo q
        BN_CTX* ctx = BN_CTX_new();
        BN_mod(h, h, params.subgroupOrder.get(), ctx);
        BN_CTX_free(ctx);

        BigInteger result;
        BN_copy(result.get(), h);
        BN_free(h);

        return result;
    }

    /**
     * Generate random k in [1, q-1]
     */
    BigInteger generateRandomK() const {
        BIGNUM* k = BN_new();
        BN_rand_range(k, params.subgroupOrder.get());
        if (BN_is_zero(k)) {
            BN_set_word(k, 1);
        }

        BigInteger result;
        BN_copy(result.get(), k);
        BN_free(k);

        return result;
    }

public:
    CertificateSignatureEngine(const DomainParameters& domainParams)
        : params(domainParams) {}

    /**
     * Sign message using private key
     * Implements modified DSA-like signature scheme
     */
    DigitalSignature signMessage(const std::vector<uint8_t>& message,
                                const SignatureKeyPair& keyPair) {
        BN_CTX* ctx = BN_CTX_new();

        // Hash message: e = H(M)
        BigInteger e = hashMessage(message);

        BIGNUM* r = BN_new();
        BIGNUM* s = BN_new();
        BIGNUM* k = BN_new();
        BIGNUM* kinv = BN_new();
        BIGNUM* temp = BN_new();

        do {
            // Generate random k
            BigInteger kBig = generateRandomK();
            BN_copy(k, kBig.get());

            // Compute r = (g^k mod p) mod q
            BN_mod_exp(temp, params.generator.get(), k,
                      params.prime.get(), ctx);
            BN_mod(r, temp, params.subgroupOrder.get(), ctx);

            if (BN_is_zero(r)) continue;

            // Compute k^-1 mod q
            BN_mod_inverse(kinv, k, params.subgroupOrder.get(), ctx);

            // Compute s = k^-1 * (e + x*r) mod q
            // Note: Modified signature equation for Korean standard
            BN_mod_mul(temp, keyPair.privateKey.get(), r,
                      params.subgroupOrder.get(), ctx);
            BN_mod_add(temp, e.get(), temp,
                      params.subgroupOrder.get(), ctx);
            BN_mod_mul(s, kinv, temp,
                      params.subgroupOrder.get(), ctx);

        } while (BN_is_zero(s));

        DigitalSignature signature;
        BN_copy(signature.r.get(), r);
        BN_copy(signature.s.get(), s);

        BN_free(r);
        BN_free(s);
        BN_free(k);
        BN_free(kinv);
        BN_free(temp);
        BN_CTX_free(ctx);

        return signature;
    }

    /**
     * Verify signature using public key
     */
    bool verifySignature(const std::vector<uint8_t>& message,
                        const DigitalSignature& signature,
                        const SignatureKeyPair& keyPair) {
        BN_CTX* ctx = BN_CTX_new();

        // Check 0 < r < q and 0 < s < q
        if (BN_is_zero(signature.r.get()) ||
            BN_cmp(signature.r.get(), params.subgroupOrder.get()) >= 0 ||
            BN_is_zero(signature.s.get()) ||
            BN_cmp(signature.s.get(), params.subgroupOrder.get()) >= 0) {
            BN_CTX_free(ctx);
            return false;
        }

        // Hash message: e = H(M)
        BigInteger e = hashMessage(message);

        BIGNUM* sinv = BN_new();
        BIGNUM* u1 = BN_new();
        BIGNUM* u2 = BN_new();
        BIGNUM* v1 = BN_new();
        BIGNUM* v2 = BN_new();
        BIGNUM* v = BN_new();

        // Compute s^-1 mod q
        BN_mod_inverse(sinv, signature.s.get(),
                      params.subgroupOrder.get(), ctx);

        // Compute u1 = e * s^-1 mod q
        BN_mod_mul(u1, e.get(), sinv,
                  params.subgroupOrder.get(), ctx);

        // Compute u2 = r * s^-1 mod q
        BN_mod_mul(u2, signature.r.get(), sinv,
                  params.subgroupOrder.get(), ctx);

        // Compute v1 = g^u1 mod p
        BN_mod_exp(v1, params.generator.get(), u1,
                  params.prime.get(), ctx);

        // Compute v2 = y^u2 mod p
        BN_mod_exp(v2, keyPair.publicKey.get(), u2,
                  params.prime.get(), ctx);

        // Compute v = (v1 * v2 mod p) mod q
        BN_mod_mul(v, v1, v2, params.prime.get(), ctx);
        BN_mod(v, v, params.subgroupOrder.get(), ctx);

        // Verify v == r
        bool valid = (BN_cmp(v, signature.r.get()) == 0);

        BN_free(sinv);
        BN_free(u1);
        BN_free(u2);
        BN_free(v1);
        BN_free(v2);
        BN_free(v);
        BN_CTX_free(ctx);

        return valid;
    }
};

/**
 * Certificate Authority Service
 */
class CertificateAuthorityService {
private:
    DomainParameters params;
    SignatureKeyPair caKeyPair;
    CertificateSignatureEngine engine;

public:
    CertificateAuthorityService(int securityBits)
        : params(DomainParameters::generate(securityBits)),
          caKeyPair(SignatureKeyPair::generate(params)),
          engine(params) {
        std::cout << "Certificate Authority initialized" << std::endl;
        std::cout << "Security level: " << securityBits << " bits" << std::endl;
    }

    /**
     * Sign certificate request
     */
    DigitalSignature signCertificate(const std::string& certData) {
        std::vector<uint8_t> data(certData.begin(), certData.end());
        auto signature = engine.signMessage(data, caKeyPair);

        std::cout << "Certificate signed:" << std::endl;
        std::cout << "  Data: " << certData.substr(0, 50) << "..." << std::endl;
        std::cout << "  r: " << signature.r.toHex().substr(0, 16) << "..." << std::endl;
        std::cout << "  s: " << signature.s.toHex().substr(0, 16) << "..." << std::endl;

        return signature;
    }

    /**
     * Verify certificate signature
     */
    bool verifyCertificate(const std::string& certData,
                          const DigitalSignature& signature) {
        std::vector<uint8_t> data(certData.begin(), certData.end());
        bool valid = engine.verifySignature(data, signature, caKeyPair);

        std::cout << "Certificate verification: "
                  << (valid ? "VALID" : "INVALID") << std::endl;

        return valid;
    }

    /**
     * Issue user key pair
     */
    SignatureKeyPair issueUserKeyPair() {
        return SignatureKeyPair::generate(params);
    }

    DomainParameters getParameters() const {
        return params;
    }
};

/**
 * Certificate structure
 */
struct Certificate {
    std::string subject;
    std::string issuer;
    std::string serialNumber;
    uint64_t validFrom;
    uint64_t validUntil;
    std::string publicKey;

    std::string toString() const {
        return "CN=" + subject + ",O=" + issuer + ",SN=" + serialNumber +
               ",VF=" + std::to_string(validFrom) +
               ",VU=" + std::to_string(validUntil) +
               ",PK=" + publicKey;
    }
};

// Example usage and testing
int main() {
    std::cout << "=== PKI Certificate Authority System ===" << std::endl;
    std::cout << "Discrete Logarithm Signature Scheme" << std::endl;
    std::cout << "========================================\n" << std::endl;

    // Initialize Certificate Authority with 1024-bit security
    CertificateAuthorityService ca(1024);

    std::cout << "\n--- Generating User Key Pair ---" << std::endl;
    SignatureKeyPair userKeys = ca.issueUserKeyPair();
    std::cout << "User public key: "
              << userKeys.publicKey.toHex().substr(0, 32) << "..." << std::endl;

    // Create certificate
    std::cout << "\n--- Creating Certificate ---" << std::endl;
    Certificate cert;
    cert.subject = "user@example.com";
    cert.issuer = "Korean Certificate Authority";
    cert.serialNumber = "2025-KR-123456";

    auto now = std::chrono::system_clock::now();
    cert.validFrom = std::chrono::duration_cast<std::chrono::seconds>(
        now.time_since_epoch()).count();
    cert.validUntil = cert.validFrom + (365 * 24 * 60 * 60); // 1 year
    cert.publicKey = userKeys.publicKey.toHex();

    std::string certData = cert.toString();

    // Sign certificate
    std::cout << "\n--- Signing Certificate ---" << std::endl;
    auto signature = ca.signCertificate(certData);

    // Verify certificate
    std::cout << "\n--- Verifying Certificate ---" << std::endl;
    bool isValid = ca.verifyCertificate(certData, signature);

    // Test with tampered data
    std::cout << "\n--- Testing Tampered Certificate ---" << std::endl;
    std::string tamperedData = certData + "TAMPERED";
    bool isTamperedValid = ca.verifyCertificate(tamperedData, signature);

    std::cout << "\n=== Summary ===" << std::endl;
    std::cout << "Original certificate: " << (isValid ? "VALID" : "INVALID") << std::endl;
    std::cout << "Tampered certificate: " << (isTamperedValid ? "VALID" : "INVALID") << std::endl;

    return 0;
}
