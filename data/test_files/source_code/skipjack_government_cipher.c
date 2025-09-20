#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROUNDS 32
#define BLOCK_SIZE 8

typedef struct {
    uint8_t key[10]; 
} skipjack_ctx_t;

static const uint8_t f_table[256] = {
    0xa3, 0xd7, 0x09, 0x83, 0xf8, 0x48, 0xf6, 0xf4, 0xb3, 0x21, 0x15, 0x78, 0x99, 0xb1, 0xaf, 0xf9,
    0xe7, 0x2d, 0x4d, 0x8a, 0xce, 0x4c, 0xca, 0x2e, 0x52, 0x95, 0xd9, 0x1e, 0x4e, 0x38, 0x44, 0x28,
    0x0a, 0xdf, 0x02, 0xa0, 0x17, 0xf1, 0x60, 0x68, 0x12, 0xb7, 0x7a, 0xc3, 0xe9, 0xfa, 0x3d, 0x53,
    0x96, 0x84, 0x6b, 0xba, 0xf2, 0x63, 0x9a, 0x19, 0x7c, 0xae, 0xe5, 0xf5, 0xf7, 0x16, 0x6a, 0xa2,
    0x39, 0xb6, 0x7b, 0x0f, 0xc1, 0x93, 0x81, 0x1b, 0xee, 0xb4, 0x1a, 0xea, 0xd0, 0x91, 0x2f, 0xb8,
    0x55, 0xb9, 0xda, 0x85, 0x3f, 0x41, 0xbf, 0xe0, 0x5a, 0x58, 0x80, 0x5f, 0x66, 0x0b, 0xd8, 0x90,
    0x35, 0xd5, 0xc0, 0xa7, 0x33, 0x06, 0x65, 0x69, 0x45, 0x00, 0x94, 0x56, 0x6d, 0x98, 0x9b, 0x76,
    0x97, 0xfc, 0xb2, 0xc2, 0xb0, 0xfe, 0xdb, 0x20, 0xe1, 0xeb, 0xd6, 0xe4, 0xdd, 0x47, 0x4a, 0x1d,
    0x42, 0xed, 0x9e, 0x6e, 0x49, 0x3c, 0xcd, 0x43, 0x27, 0xd2, 0x07, 0xd4, 0xde, 0xc7, 0x67, 0x18,
    0x89, 0xcb, 0x30, 0x1f, 0x8d, 0xc6, 0x8f, 0xaa, 0xc8, 0x74, 0xdc, 0xc9, 0x5d, 0x5c, 0x31, 0xa4,
    0x70, 0x88, 0x61, 0x2c, 0x9f, 0x0d, 0x2b, 0x87, 0x50, 0x82, 0x54, 0x64, 0x26, 0x7d, 0x03, 0x40,
    0x34, 0x4b, 0x1c, 0x73, 0xd1, 0xc4, 0xfd, 0x3b, 0xcc, 0xfb, 0x7f, 0xab, 0xe6, 0x3e, 0x5b, 0xa5,
    0xad, 0x04, 0x23, 0x9c, 0x14, 0x51, 0x22, 0xf0, 0x29, 0x79, 0x71, 0x7e, 0xff, 0x8c, 0x0e, 0xe2,
    0x0c, 0xef, 0xbc, 0x72, 0x75, 0x6f, 0x37, 0xa1, 0xec, 0xd3, 0x8e, 0x62, 0x8b, 0x86, 0x10, 0xe8,
    0x08, 0x77, 0x11, 0xbe, 0x92, 0x4f, 0x24, 0xc5, 0x32, 0x36, 0x9d, 0xcf, 0xf3, 0xa6, 0xbb, 0xac,
    0x5e, 0x6c, 0xa9, 0x13, 0x57, 0x25, 0xb5, 0xe3, 0xbd, 0xa8, 0x3a, 0x01, 0x05, 0x59, 0x2a, 0x46
};

static uint16_t g_permutation(uint16_t w, const uint8_t *key, int step) {
    uint8_t g1 = (w >> 8) & 0xFF;
    uint8_t g2 = w & 0xFF;

    g1 ^= f_table[g2 ^ key[(4 * step) % 10]];
    g2 ^= f_table[g1 ^ key[(4 * step + 1) % 10]];
    g1 ^= f_table[g2 ^ key[(4 * step + 2) % 10]];
    g2 ^= f_table[g1 ^ key[(4 * step + 3) % 10]];

    return ((uint16_t)g1 << 8) | g2;
}

static uint16_t g_inverse(uint16_t w, const uint8_t *key, int step) {
    uint8_t g1 = (w >> 8) & 0xFF;
    uint8_t g2 = w & 0xFF;

    g2 ^= f_table[g1 ^ key[(4 * step + 3) % 10]];
    g1 ^= f_table[g2 ^ key[(4 * step + 2) % 10]];
    g2 ^= f_table[g1 ^ key[(4 * step + 1) % 10]];
    g1 ^= f_table[g2 ^ key[(4 * step) % 10]];

    return ((uint16_t)g1 << 8) | g2;
}

void skipjack_init(skipjack_ctx_t *ctx, const uint8_t *key) {
    memcpy(ctx->key, key, 10);
}

void skipjack_encrypt_block(skipjack_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint16_t w1 = (input[0] << 8) | input[1];
    uint16_t w2 = (input[2] << 8) | input[3];
    uint16_t w3 = (input[4] << 8) | input[5];
    uint16_t w4 = (input[6] << 8) | input[7];

    for (int round = 0; round < ROUNDS; round++) {
        if (round < 8 || (round >= 16 && round < 24)) {
            
            uint16_t temp = w4;
            w4 = w3;
            w3 = w2;
            w2 = g_permutation(w1, ctx->key, round + 1) ^ w4 ^ (round + 1);
            w1 = temp;
        } else {
            
            uint16_t temp = w4;
            w4 = w3;
            w3 = g_permutation(w2, ctx->key, round + 1) ^ w1 ^ (round + 1);
            w2 = w1;
            w1 = temp;
        }
    }

    output[0] = (w1 >> 8) & 0xFF;
    output[1] = w1 & 0xFF;
    output[2] = (w2 >> 8) & 0xFF;
    output[3] = w2 & 0xFF;
    output[4] = (w3 >> 8) & 0xFF;
    output[5] = w3 & 0xFF;
    output[6] = (w4 >> 8) & 0xFF;
    output[7] = w4 & 0xFF;
}

void skipjack_decrypt_block(skipjack_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint16_t w1 = (input[0] << 8) | input[1];
    uint16_t w2 = (input[2] << 8) | input[3];
    uint16_t w3 = (input[4] << 8) | input[5];
    uint16_t w4 = (input[6] << 8) | input[7];

    for (int round = ROUNDS - 1; round >= 0; round--) {
        if (round < 8 || (round >= 16 && round < 24)) {
            
            uint16_t temp = w1;
            w1 = w2;
            w2 = w3;
            w3 = w4;
            w4 = g_inverse(w2 ^ w4 ^ (round + 1), ctx->key, round + 1);
            w2 = temp;
        } else {
            
            uint16_t temp = w1;
            w1 = w2;
            w2 = w3;
            w3 = g_inverse(w3 ^ w1 ^ (round + 1), ctx->key, round + 1);
            w1 = temp;
        }
    }

    output[0] = (w1 >> 8) & 0xFF;
    output[1] = w1 & 0xFF;
    output[2] = (w2 >> 8) & 0xFF;
    output[3] = w2 & 0xFF;
    output[4] = (w3 >> 8) & 0xFF;
    output[5] = w3 & 0xFF;
    output[6] = (w4 >> 8) & 0xFF;
    output[7] = w4 & 0xFF;
}

void tea_encrypt_block(const uint8_t *input, uint8_t *output, const uint8_t *key) {
    uint32_t v0 = (input[0] << 24) | (input[1] << 16) | (input[2] << 8) | input[3];
    uint32_t v1 = (input[4] << 24) | (input[5] << 16) | (input[6] << 8) | input[7];

    uint32_t k0 = (key[0] << 24) | (key[1] << 16) | (key[2] << 8) | key[3];
    uint32_t k1 = (key[4] << 24) | (key[5] << 16) | (key[6] << 8) | key[7];
    uint32_t k2 = (key[8] << 24) | (key[9] << 16) | (key[10] << 8) | key[11];
    uint32_t k3 = (key[12] << 24) | (key[13] << 16) | (key[14] << 8) | key[15];

    uint32_t sum = 0;
    uint32_t delta = 0x9e3779b9;

    for (int i = 0; i < 32; i++) {
        sum += delta;
        v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
        v1 += ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);
    }

    output[0] = (v0 >> 24) & 0xFF;
    output[1] = (v0 >> 16) & 0xFF;
    output[2] = (v0 >> 8) & 0xFF;
    output[3] = v0 & 0xFF;
    output[4] = (v1 >> 24) & 0xFF;
    output[5] = (v1 >> 16) & 0xFF;
    output[6] = (v1 >> 8) & 0xFF;
    output[7] = v1 & 0xFF;
}

void tea_decrypt_block(const uint8_t *input, uint8_t *output, const uint8_t *key) {
    uint32_t v0 = (input[0] << 24) | (input[1] << 16) | (input[2] << 8) | input[3];
    uint32_t v1 = (input[4] << 24) | (input[5] << 16) | (input[6] << 8) | input[7];

    uint32_t k0 = (key[0] << 24) | (key[1] << 16) | (key[2] << 8) | key[3];
    uint32_t k1 = (key[4] << 24) | (key[5] << 16) | (key[6] << 8) | key[7];
    uint32_t k2 = (key[8] << 24) | (key[9] << 16) | (key[10] << 8) | key[11];
    uint32_t k3 = (key[12] << 24) | (key[13] << 16) | (key[14] << 8) | key[15];

    uint32_t sum = 0xC6EF3720; 
    uint32_t delta = 0x9e3779b9;

    for (int i = 0; i < 32; i++) {
        v1 -= ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);
        v0 -= ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
        sum -= delta;
    }

    output[0] = (v0 >> 24) & 0xFF;
    output[1] = (v0 >> 16) & 0xFF;
    output[2] = (v0 >> 8) & 0xFF;
    output[3] = v0 & 0xFF;
    output[4] = (v1 >> 24) & 0xFF;
    output[5] = (v1 >> 16) & 0xFF;
    output[6] = (v1 >> 8) & 0xFF;
    output[7] = v1 & 0xFF;
}

int government_cipher_process(const uint8_t *input, uint8_t *output, size_t length,
                             const uint8_t *key, int algorithm, int encrypt) {
    if (length % BLOCK_SIZE != 0) {
        return -1;
    }

    size_t blocks = length / BLOCK_SIZE;

    if (algorithm == 0) { 
        skipjack_ctx_t ctx;
        skipjack_init(&ctx, key);

        for (size_t i = 0; i < blocks; i++) {
            if (encrypt) {
                skipjack_encrypt_block(&ctx, input + i * BLOCK_SIZE,
                                     output + i * BLOCK_SIZE);
            } else {
                skipjack_decrypt_block(&ctx, input + i * BLOCK_SIZE,
                                     output + i * BLOCK_SIZE);
            }
        }
    } else { 
        for (size_t i = 0; i < blocks; i++) {
            if (encrypt) {
                tea_encrypt_block(input + i * BLOCK_SIZE,
                                output + i * BLOCK_SIZE, key);
            } else {
                tea_decrypt_block(input + i * BLOCK_SIZE,
                                output + i * BLOCK_SIZE, key);
            }
        }
    }

    return 0;
}

int main() {
    uint8_t skipjack_key[10] = {0x00, 0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11};
    uint8_t tea_key[16] = "TeaSecretKey1234";
    uint8_t plaintext[16] = "TestData12345678";
    uint8_t ciphertext[16];
    uint8_t decrypted[16];

    printf("Original: %.*s\n", 16, plaintext);

    printf("\n=== GovernmentCipher (NSA) ===\n");
    if (government_cipher_process(plaintext, ciphertext, 16, skipjack_key, 0, 1) == 0) {
        printf("Encrypted: ");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        if (government_cipher_process(ciphertext, decrypted, 16, skipjack_key, 0, 0) == 0) {
            printf("Decrypted: %.*s\n", 16, decrypted);
        }
    }

    printf("\n=== TEA ===\n");
    if (government_cipher_process(plaintext, ciphertext, 16, tea_key, 1, 1) == 0) {
        printf("Encrypted: ");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        if (government_cipher_process(ciphertext, decrypted, 16, tea_key, 1, 0) == 0) {
            printf("Decrypted: %.*s\n", 16, decrypted);
        }
    }

    return 0;
}