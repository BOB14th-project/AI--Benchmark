/**
 * Enterprise Authentication Server
 * Implements SSO (Single Sign-On) with lightweight encryption and digital signatures.
 * Combines session token encryption with authentication signatures.
 */

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cstring>
#include <ctime>
#include <random>
#include <sstream>
#include <iomanip>
#include <openssl/bn.h>
#include <openssl/sha.h>

/**
 * Lightweight Session Token Encryption
 * Optimized for low-latency authentication flows
 */
class SessionTokenEncryptor {
private:
    static const int DATA_BLOCK_SIZE = 8;      // 64-bit blocks
    static const int TRANSFORMATION_ROUNDS = 32;
    static const int KEY_SIZE = 16;            // 128-bit key
    static const int SUBKEY_COUNT = 136;

    uint8_t master_key[KEY_SIZE];
    uint8_t subkeys[SUBKEY_COUNT];

    // Delta constant for mixing operations
    static constexpr uint32_t MIXING_DELTA = 0x5A827999;

    /**
     * Generate subkeys for all rounds
     */
    void generate_subkeys() {
        uint8_t working_key[KEY_SIZE];
        memcpy(working_key, master_key, KEY_SIZE);

        for (int round = 0; round < TRANSFORMATION_ROUNDS; round++) {
            for (int sub = 0; sub < 4; sub++) {
                int idx = round * 4 + sub;

                // Rotate key material
                uint8_t temp = working_key[0];
                for (int i = 0; i < KEY_SIZE - 1; i++) {
                    working_key[i] = working_key[i + 1];
                }
                working_key[KEY_SIZE - 1] = temp;

                // Mix with constants
                working_key[sub % KEY_SIZE] ^= (MIXING_DELTA >> (sub * 8)) & 0xFF;
                working_key[(sub + 7) % KEY_SIZE] ^= round;

                // Store subkey
                subkeys[idx] = working_key[sub * 2] ^ working_key[sub * 2 + 1];
            }
        }

        // Final whitening keys
        for (int i = 0; i < 8; i++) {
            subkeys[TRANSFORMATION_ROUNDS * 4 + i] =
                working_key[i] ^ working_key[KEY_SIZE - 1 - i];
        }
    }

    /**
     * Byte rotation operations
     */
    inline uint8_t rotate_left(uint8_t value, int shift) const {
        shift &= 7;
        return (value << shift) | (value >> (8 - shift));
    }

    /**
     * Round transformation function
     */
    void apply_round_transformation(uint8_t* block, uint8_t* round_keys, int round_num) {
        if (round_num % 2 == 0) {
            // Even round: Transform bytes 0-3
            block[0] = rotate_left(block[0] ^ round_keys[0], 1) + block[1];
            block[1] = rotate_left(block[1] ^ round_keys[1], 3) ^ block[2];
            block[2] = rotate_left(block[2] + round_keys[2], 4) ^ block[3];
            block[3] = rotate_left(block[3] ^ round_keys[3], 5) + block[0];
        } else {
            // Odd round: Transform bytes 4-7
            block[4] = rotate_left(block[4] + round_keys[0], 2) ^ block[5];
            block[5] = rotate_left(block[5] ^ round_keys[1], 4) + block[6];
            block[6] = rotate_left(block[6] + round_keys[2], 5) ^ block[7];
            block[7] = rotate_left(block[7] ^ round_keys[3], 6) + block[4];
        }
    }

public:
    SessionTokenEncryptor(const uint8_t* key) {
        memcpy(master_key, key, KEY_SIZE);
        generate_subkeys();
    }

    /**
     * Encrypt session token block
     */
    void encrypt_block(const uint8_t* plaintext, uint8_t* ciphertext) {
        // Copy to output
        memcpy(ciphertext, plaintext, DATA_BLOCK_SIZE);

        // Initial whitening
        for (int i = 0; i < DATA_BLOCK_SIZE; i++) {
            ciphertext[i] ^= subkeys[i];
        }

        // Main rounds
        for (int round = 0; round < TRANSFORMATION_ROUNDS; round++) {
            uint8_t* round_keys = &subkeys[8 + round * 4];
            apply_round_transformation(ciphertext, round_keys, round);
        }

        // Final whitening
        for (int i = 0; i < DATA_BLOCK_SIZE; i++) {
            ciphertext[i] ^= subkeys[TRANSFORMATION_ROUNDS * 4 + i];
        }
    }

    /**
     * Encrypt session token data
     */
    std::vector<uint8_t> encrypt_token(const std::vector<uint8_t>& data) {
        // Calculate padded length
        size_t pad_len = DATA_BLOCK_SIZE - (data.size() % DATA_BLOCK_SIZE);
        std::vector<uint8_t> padded(data.size() + pad_len);

        memcpy(padded.data(), data.data(), data.size());
        for (size_t i = data.size(); i < padded.size(); i++) {
            padded[i] = static_cast<uint8_t>(pad_len);
        }

        // Encrypt blocks
        std::vector<uint8_t> encrypted(padded.size());
        for (size_t i = 0; i < padded.size(); i += DATA_BLOCK_SIZE) {
            encrypt_block(&padded[i], &encrypted[i]);
        }

        return encrypted;
    }
};

/**
 * Authentication Signature Engine
 * Based on discrete logarithm problem for user authentication
 */
class AuthenticationSignatureEngine {
private:
    struct DomainParams {
        BIGNUM* prime;           // Large prime p
        BIGNUM* generator;       // Generator g
        BIGNUM* subgroup_order;  // Order q
    };

    DomainParams params;
    BN_CTX* ctx;

    void initialize_domain_params(int bits) {
        ctx = BN_CTX_new();
        params.prime = BN_new();
        params.generator = BN_new();
        params.subgroup_order = BN_new();

        BIGNUM* one = BN_new();
        BIGNUM* two = BN_new();
        BN_set_word(one, 1);
        BN_set_word(two, 2);

        // Generate subgroup order q
        BN_generate_prime_ex(params.subgroup_order, bits / 2, 1,
                            nullptr, nullptr, nullptr);

        // Generate p = 2q + 1
        BN_mul(params.prime, params.subgroup_order, two, ctx);
        BN_add(params.prime, params.prime, one);

        // Find suitable prime
        while (!BN_is_prime_ex(params.prime, BN_prime_checks, ctx, nullptr)) {
            BN_generate_prime_ex(params.subgroup_order, bits / 2, 1,
                                nullptr, nullptr, nullptr);
            BN_mul(params.prime, params.subgroup_order, two, ctx);
            BN_add(params.prime, params.prime, one);
        }

        // Find generator
        BIGNUM* exp = BN_new();
        BIGNUM* pm1 = BN_new();
        BIGNUM* h = BN_new();

        BN_sub(pm1, params.prime, one);
        BN_div(exp, nullptr, pm1, params.subgroup_order, ctx);

        BN_set_word(h, 2);
        do {
            BN_mod_exp(params.generator, h, exp, params.prime, ctx);
            BN_add_word(h, 1);
        } while (BN_is_one(params.generator));

        BN_free(exp);
        BN_free(pm1);
        BN_free(h);
        BN_free(one);
        BN_free(two);
    }

    std::vector<uint8_t> hash_message(const std::string& message) {
        uint8_t hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, message.c_str(), message.length());
        SHA256_Final(hash, &sha256);

        return std::vector<uint8_t>(hash, hash + SHA256_DIGEST_LENGTH);
    }

public:
    struct KeyPair {
        BIGNUM* private_key;
        BIGNUM* public_key;
    };

    struct Signature {
        BIGNUM* r;
        BIGNUM* s;
    };

    AuthenticationSignatureEngine(int security_bits = 1024) {
        initialize_domain_params(security_bits);
    }

    ~AuthenticationSignatureEngine() {
        BN_free(params.prime);
        BN_free(params.generator);
        BN_free(params.subgroup_order);
        BN_CTX_free(ctx);
    }

    /**
     * Generate authentication key pair
     */
    KeyPair generate_keypair() {
        KeyPair keypair;
        keypair.private_key = BN_new();
        keypair.public_key = BN_new();

        // Generate private key x in [1, q-1]
        BN_rand_range(keypair.private_key, params.subgroup_order);
        if (BN_is_zero(keypair.private_key)) {
            BN_set_word(keypair.private_key, 1);
        }

        // Compute public key y = g^x mod p
        BN_mod_exp(keypair.public_key, params.generator, keypair.private_key,
                  params.prime, ctx);

        return keypair;
    }

    /**
     * Sign authentication challenge
     */
    Signature sign_challenge(const std::string& challenge, const KeyPair& keypair) {
        Signature sig;
        sig.r = BN_new();
        sig.s = BN_new();

        // Hash challenge
        auto hash_vec = hash_message(challenge);
        BIGNUM* e = BN_new();
        BN_bin2bn(hash_vec.data(), hash_vec.size(), e);
        BN_mod(e, e, params.subgroup_order, ctx);

        BIGNUM* k = BN_new();
        BIGNUM* kinv = BN_new();
        BIGNUM* temp = BN_new();

        do {
            // Generate random k
            BN_rand_range(k, params.subgroup_order);
            if (BN_is_zero(k)) {
                BN_set_word(k, 1);
            }

            // Compute r = (g^k mod p) mod q
            BN_mod_exp(temp, params.generator, k, params.prime, ctx);
            BN_mod(sig.r, temp, params.subgroup_order, ctx);

            if (BN_is_zero(sig.r)) continue;

            // Compute k^-1 mod q
            BN_mod_inverse(kinv, k, params.subgroup_order, ctx);

            // Compute s = k^-1 * (e + x*r) mod q
            BN_mod_mul(temp, keypair.private_key, sig.r,
                      params.subgroup_order, ctx);
            BN_mod_add(temp, e, temp, params.subgroup_order, ctx);
            BN_mod_mul(sig.s, kinv, temp, params.subgroup_order, ctx);

        } while (BN_is_zero(sig.s));

        BN_free(e);
        BN_free(k);
        BN_free(kinv);
        BN_free(temp);

        return sig;
    }

    /**
     * Verify authentication signature
     */
    bool verify_signature(const std::string& challenge, const Signature& sig,
                         const KeyPair& keypair) {
        // Validate signature values
        if (BN_is_zero(sig.r) || BN_cmp(sig.r, params.subgroup_order) >= 0 ||
            BN_is_zero(sig.s) || BN_cmp(sig.s, params.subgroup_order) >= 0) {
            return false;
        }

        // Hash challenge
        auto hash_vec = hash_message(challenge);
        BIGNUM* e = BN_new();
        BN_bin2bn(hash_vec.data(), hash_vec.size(), e);
        BN_mod(e, e, params.subgroup_order, ctx);

        BIGNUM* sinv = BN_new();
        BIGNUM* u1 = BN_new();
        BIGNUM* u2 = BN_new();
        BIGNUM* v1 = BN_new();
        BIGNUM* v2 = BN_new();
        BIGNUM* v = BN_new();

        // Compute s^-1 mod q
        BN_mod_inverse(sinv, sig.s, params.subgroup_order, ctx);

        // Compute u1 = e * s^-1 mod q
        BN_mod_mul(u1, e, sinv, params.subgroup_order, ctx);

        // Compute u2 = r * s^-1 mod q
        BN_mod_mul(u2, sig.r, sinv, params.subgroup_order, ctx);

        // Compute v = (g^u1 * y^u2 mod p) mod q
        BN_mod_exp(v1, params.generator, u1, params.prime, ctx);
        BN_mod_exp(v2, keypair.public_key, u2, params.prime, ctx);
        BN_mod_mul(v, v1, v2, params.prime, ctx);
        BN_mod(v, v, params.subgroup_order, ctx);

        bool valid = (BN_cmp(v, sig.r) == 0);

        BN_free(e);
        BN_free(sinv);
        BN_free(u1);
        BN_free(u2);
        BN_free(v1);
        BN_free(v2);
        BN_free(v);

        return valid;
    }
};

/**
 * User Session for SSO
 */
struct UserSession {
    std::string session_id;
    std::string username;
    std::string ip_address;
    time_t created_at;
    time_t expires_at;
    bool is_authenticated;
    std::vector<uint8_t> encrypted_token;
};

/**
 * Enterprise Authentication Server
 */
class EnterpriseAuthenticationServer {
private:
    SessionTokenEncryptor* token_encryptor;
    AuthenticationSignatureEngine* sig_engine;
    std::map<std::string, UserSession> active_sessions;
    std::map<std::string, AuthenticationSignatureEngine::KeyPair> user_keys;

    std::string generate_session_id() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 255);

        std::stringstream ss;
        for (int i = 0; i < 16; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << dis(gen);
        }
        return ss.str();
    }

    std::string generate_challenge() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 255);

        std::stringstream ss;
        ss << "AUTH_CHALLENGE_" << time(nullptr) << "_";
        for (int i = 0; i < 8; i++) {
            ss << std::hex << dis(gen);
        }
        return ss.str();
    }

public:
    EnterpriseAuthenticationServer(const uint8_t* session_key) {
        token_encryptor = new SessionTokenEncryptor(session_key);
        sig_engine = new AuthenticationSignatureEngine(1024);
    }

    ~EnterpriseAuthenticationServer() {
        delete token_encryptor;
        delete sig_engine;

        for (auto& pair : user_keys) {
            BN_free(pair.second.private_key);
            BN_free(pair.second.public_key);
        }
    }

    /**
     * Register new user
     */
    void register_user(const std::string& username) {
        std::cout << "Registering user: " << username << std::endl;

        // Generate authentication keys
        auto keypair = sig_engine->generate_keypair();
        user_keys[username] = keypair;

        char* pubkey_hex = BN_bn2hex(keypair.public_key);
        std::cout << "  Public key: " << std::string(pubkey_hex).substr(0, 20)
                  << "..." << std::endl;
        OPENSSL_free(pubkey_hex);
    }

    /**
     * Initiate authentication
     */
    std::string initiate_authentication(const std::string& username,
                                       const std::string& ip_address) {
        std::cout << "\nInitiating authentication for: " << username << std::endl;

        // Create session
        UserSession session;
        session.session_id = generate_session_id();
        session.username = username;
        session.ip_address = ip_address;
        session.created_at = time(nullptr);
        session.expires_at = session.created_at + 3600; // 1 hour
        session.is_authenticated = false;

        active_sessions[session.session_id] = session;

        std::cout << "  Session ID: " << session.session_id << std::endl;

        return session.session_id;
    }

    /**
     * Complete authentication with signature verification
     */
    bool complete_authentication(const std::string& session_id,
                                const std::string& challenge_response) {
        auto it = active_sessions.find(session_id);
        if (it == active_sessions.end()) {
            return false;
        }

        UserSession& session = it->second;

        // Find user keys
        auto key_it = user_keys.find(session.username);
        if (key_it == user_keys.end()) {
            return false;
        }

        // Generate and sign challenge
        std::string challenge = generate_challenge();
        auto signature = sig_engine->sign_challenge(challenge, key_it->second);

        // Verify signature
        bool valid = sig_engine->verify_signature(challenge, signature, key_it->second);

        if (valid) {
            session.is_authenticated = true;

            // Create encrypted session token
            std::string token_data = session.session_id + "|" +
                                    session.username + "|" +
                                    std::to_string(session.expires_at);

            std::vector<uint8_t> token_vec(token_data.begin(), token_data.end());
            session.encrypted_token = token_encryptor->encrypt_token(token_vec);

            std::cout << "  Authentication successful" << std::endl;
            std::cout << "  Token encrypted: " << session.encrypted_token.size()
                      << " bytes" << std::endl;
        }

        BN_free(signature.r);
        BN_free(signature.s);

        return valid;
    }

    /**
     * Get session info
     */
    void print_session_info(const std::string& session_id) {
        auto it = active_sessions.find(session_id);
        if (it == active_sessions.end()) {
            std::cout << "Session not found" << std::endl;
            return;
        }

        const UserSession& session = it->second;
        std::cout << "\nSession Information:" << std::endl;
        std::cout << "  Session ID: " << session.session_id << std::endl;
        std::cout << "  Username: " << session.username << std::endl;
        std::cout << "  IP Address: " << session.ip_address << std::endl;
        std::cout << "  Authenticated: " << (session.is_authenticated ? "Yes" : "No")
                  << std::endl;
        std::cout << "  Created: " << ctime(&session.created_at);
        std::cout << "  Expires: " << ctime(&session.expires_at);
    }
};

// Main demonstration
int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "Enterprise SSO Authentication Server" << std::endl;
    std::cout << "========================================" << std::endl;

    // Initialize server
    uint8_t session_key[16];
    for (int i = 0; i < 16; i++) {
        session_key[i] = i * 0x11;
    }

    EnterpriseAuthenticationServer auth_server(session_key);

    // Register users
    std::cout << "\n--- User Registration ---" << std::endl;
    auth_server.register_user("alice@company.com");
    auth_server.register_user("bob@company.com");

    // Authenticate user
    std::cout << "\n--- User Authentication ---" << std::endl;
    std::string session_id = auth_server.initiate_authentication(
        "alice@company.com",
        "192.168.1.100"
    );

    // Complete authentication
    bool auth_result = auth_server.complete_authentication(
        session_id,
        "challenge_response_data"
    );

    // Print session info
    auth_server.print_session_info(session_id);

    std::cout << "\n========================================" << std::endl;
    std::cout << "Authentication flow completed" << std::endl;
    std::cout << "========================================" << std::endl;

    return 0;
}
