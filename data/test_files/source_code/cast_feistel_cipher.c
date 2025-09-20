#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define CAST128_ROUNDS 16
#define CAST256_ROUNDS 48
#define BLOCK_SIZE 8

typedef struct {
    uint32_t subkeys[32];
    uint8_t rotations[16];
    int rounds;
} cast_ctx_t;

static const uint32_t cast_sbox1[256] = {
    0x30fb40d4, 0x9fa0ff0b, 0x6beccd2f, 0x3f258c7a, 0x1e213f2f, 0x9c004dd3, 0x6003e540, 0xcf9fc949,
    0xbfd4af27, 0x88bbbdb5, 0xe2034090, 0x98d09675, 0x6e63a0e0, 0x15c361d2, 0xc2e7661d, 0x22d4ff8e,
    
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38
};

static const uint32_t cast_sbox2[256] = {
    0x24c2ba0b, 0xa8bce5d0, 0xf9c6aef7, 0x7a24f3a9, 0xd7e07b35, 0x3e1c49ea, 0x52e96e5b, 0xc1f47eb4,
    0x8b6b15e9, 0x43b2d96f, 0xfe2b5f3c, 0x5bf86ba8, 0x91e6a7d2, 0x7d4f2b0a, 0x6e8d3f47, 0x2c1b957e,
    
    0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb
};

static const uint32_t cast_sbox3[256] = {
    0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6f52c06c, 0x2e6c0b5e, 0x2202e41b, 0x5b4b3d96,
    0x8fce5f5a, 0x1a0a2b9f, 0x3e39a1df, 0x62940d5c, 0xe0c6dac9, 0x73f5f55a, 0x5a04d6e3, 0x48b0c742,
    
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87
};

static const uint32_t cast_sbox4[256] = {
    0xc72e90bf, 0x5a6b99f4, 0xf8d37329, 0xbc5c462a, 0x4962bb4e, 0x31da7a8f, 0x35e4b15d, 0x8e5fd2a9,
    0x7d31c6e0, 0xa2bf85f4, 0x49bf5dc8, 0x6bc4af73, 0x93e8b2c1, 0x2e1da4b7, 0xf542e968, 0x8e4d3c9a,
    
    0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb
};

static uint32_t cast_f1(uint32_t x, uint32_t k, uint8_t r) {
    uint32_t temp = (x + k) & 0xFFFFFFFF;
    temp = (temp << r) | (temp >> (32 - r));
    return ((cast_sbox1[(temp >> 24) & 0xFF] ^ cast_sbox2[(temp >> 16) & 0xFF]) -
            cast_sbox3[(temp >> 8) & 0xFF]) + cast_sbox4[temp & 0xFF];
}

static uint32_t cast_f2(uint32_t x, uint32_t k, uint8_t r) {
    uint32_t temp = x ^ k;
    temp = (temp << r) | (temp >> (32 - r));
    return ((cast_sbox1[(temp >> 24) & 0xFF] - cast_sbox2[(temp >> 16) & 0xFF]) +
            cast_sbox3[(temp >> 8) & 0xFF]) ^ cast_sbox4[temp & 0xFF];
}

static uint32_t cast_f3(uint32_t x, uint32_t k, uint8_t r) {
    uint32_t temp = (x - k) & 0xFFFFFFFF;
    temp = (temp << r) | (temp >> (32 - r));
    return ((cast_sbox1[(temp >> 24) & 0xFF] + cast_sbox2[(temp >> 16) & 0xFF]) ^
            cast_sbox3[(temp >> 8) & 0xFF]) - cast_sbox4[temp & 0xFF];
}

void cast128_key_schedule(cast_ctx_t *ctx, const uint8_t *key, int key_length) {
    uint32_t x[4];
    uint32_t z[4];

    for (int i = 0; i < 4; i++) {
        x[i] = 0;
        for (int j = 0; j < 4 && i * 4 + j < key_length; j++) {
            x[i] |= ((uint32_t)key[i * 4 + j]) << (8 * j);
        }
    }

    for (int i = 0; i < 4; i++) {
        z[0] = x[0] ^ cast_sbox4[x[3] & 0xFF] ^ cast_sbox3[(x[3] >> 8) & 0xFF] ^
               cast_sbox2[(x[3] >> 16) & 0xFF] ^ cast_sbox1[(x[3] >> 24) & 0xFF];
        z[1] = x[2] ^ cast_sbox1[z[0] & 0xFF] ^ cast_sbox2[(z[0] >> 8) & 0xFF] ^
               cast_sbox3[(z[0] >> 16) & 0xFF] ^ cast_sbox4[(z[0] >> 24) & 0xFF];
        z[2] = x[3] ^ cast_sbox2[z[1] & 0xFF] ^ cast_sbox3[(z[1] >> 8) & 0xFF] ^
               cast_sbox4[(z[1] >> 16) & 0xFF] ^ cast_sbox1[(z[1] >> 24) & 0xFF];
        z[3] = x[1] ^ cast_sbox3[z[2] & 0xFF] ^ cast_sbox4[(z[2] >> 8) & 0xFF] ^
               cast_sbox1[(z[2] >> 16) & 0xFF] ^ cast_sbox2[(z[2] >> 24) & 0xFF];

        ctx->subkeys[i * 4] = z[2] ^ cast_sbox1[z[1] & 0xFF];
        ctx->subkeys[i * 4 + 1] = z[0] ^ cast_sbox2[(z[1] >> 8) & 0xFF];
        ctx->subkeys[i * 4 + 2] = z[1] ^ cast_sbox3[(z[1] >> 16) & 0xFF];
        ctx->subkeys[i * 4 + 3] = z[3] ^ cast_sbox4[(z[1] >> 24) & 0xFF];

        ctx->rotations[i * 4] = (z[0] >> 8) & 0x1F;
        ctx->rotations[i * 4 + 1] = (z[2] >> 16) & 0x1F;
        ctx->rotations[i * 4 + 2] = (z[1] >> 8) & 0x1F;
        ctx->rotations[i * 4 + 3] = (z[3] >> 16) & 0x1F;

        memcpy(x, z, sizeof(x));
    }

    ctx->rounds = CAST128_ROUNDS;
}

void cast128_encrypt_block(cast_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32_t left = (input[0] << 24) | (input[1] << 16) | (input[2] << 8) | input[3];
    uint32_t right = (input[4] << 24) | (input[5] << 16) | (input[6] << 8) | input[7];

    for (int round = 0; round < ctx->rounds; round++) {
        uint32_t temp = right;

        if (round < 4 || (round >= 8 && round < 12)) {
            right = left ^ cast_f1(right, ctx->subkeys[round], ctx->rotations[round]);
        } else if ((round >= 4 && round < 8) || (round >= 12 && round < 16)) {
            right = left ^ cast_f2(right, ctx->subkeys[round], ctx->rotations[round]);
        } else {
            right = left ^ cast_f3(right, ctx->subkeys[round], ctx->rotations[round]);
        }

        left = temp;
    }

    output[0] = (right >> 24) & 0xFF;
    output[1] = (right >> 16) & 0xFF;
    output[2] = (right >> 8) & 0xFF;
    output[3] = right & 0xFF;
    output[4] = (left >> 24) & 0xFF;
    output[5] = (left >> 16) & 0xFF;
    output[6] = (left >> 8) & 0xFF;
    output[7] = left & 0xFF;
}

void cast128_decrypt_block(cast_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32_t left = (input[4] << 24) | (input[5] << 16) | (input[6] << 8) | input[7];
    uint32_t right = (input[0] << 24) | (input[1] << 16) | (input[2] << 8) | input[3];

    for (int round = ctx->rounds - 1; round >= 0; round--) {
        uint32_t temp = left;

        if (round < 4 || (round >= 8 && round < 12)) {
            left = right ^ cast_f1(left, ctx->subkeys[round], ctx->rotations[round]);
        } else if ((round >= 4 && round < 8) || (round >= 12 && round < 16)) {
            left = right ^ cast_f2(left, ctx->subkeys[round], ctx->rotations[round]);
        } else {
            left = right ^ cast_f3(left, ctx->subkeys[round], ctx->rotations[round]);
        }

        right = temp;
    }

    output[0] = (left >> 24) & 0xFF;
    output[1] = (left >> 16) & 0xFF;
    output[2] = (left >> 8) & 0xFF;
    output[3] = left & 0xFF;
    output[4] = (right >> 24) & 0xFF;
    output[5] = (right >> 16) & 0xFF;
    output[6] = (right >> 8) & 0xFF;
    output[7] = right & 0xFF;
}

typedef struct {
    uint32_t key_schedule[40];
} mars_ctx_t;

static uint32_t mars_s_box[512] = {
    
    0x09d0c479, 0x28c8ffe0, 0x84aa6c39, 0x9dad7287, 0x7dff9be7, 0xd4268361, 0xc96da1d4, 0x7974cc93,
    
};

static uint32_t mars_forward_mixing(uint32_t a, uint32_t b) {
    uint32_t temp = a + b;
    return ((temp << 13) | (temp >> 19)) ^ temp;
}

void mars_key_schedule(mars_ctx_t *ctx, const uint8_t *key) {
    uint32_t T[15];

    for (int i = 0; i < 4; i++) {
        T[i] = (key[i*4+3] << 24) | (key[i*4+2] << 16) | (key[i*4+1] << 8) | key[i*4];
    }

    for (int i = 4; i < 15; i++) {
        T[i] = T[i-4] ^ T[i-1];
    }

    for (int j = 0; j < 4; j++) {
        for (int i = 0; i < 15; i++) {
            T[i] = ((T[i] << 3) | (T[i] >> 29)) + mars_s_box[i + j * 15];
        }
    }

    for (int i = 0; i < 40; i++) {
        ctx->key_schedule[i] = T[i % 15];
    }
}

int feistel_cipher_process(const uint8_t *input, uint8_t *output, size_t length,
                          const uint8_t *key, int key_length, int algorithm, int encrypt) {
    if (length % BLOCK_SIZE != 0) {
        return -1;
    }

    size_t blocks = length / BLOCK_SIZE;

    if (algorithm == 0) { 
        cast_ctx_t ctx;
        cast128_key_schedule(&ctx, key, key_length);

        for (size_t i = 0; i < blocks; i++) {
            if (encrypt) {
                cast128_encrypt_block(&ctx, input + i * BLOCK_SIZE,
                                    output + i * BLOCK_SIZE);
            } else {
                cast128_decrypt_block(&ctx, input + i * BLOCK_SIZE,
                                    output + i * BLOCK_SIZE);
            }
        }
    } else { 
        mars_ctx_t ctx;
        mars_key_schedule(&ctx, key);

        for (size_t i = 0; i < blocks; i++) {
            
            uint32_t block[2];
            block[0] = (input[i*8] << 24) | (input[i*8+1] << 16) |
                      (input[i*8+2] << 8) | input[i*8+3];
            block[1] = (input[i*8+4] << 24) | (input[i*8+5] << 16) |
                      (input[i*8+6] << 8) | input[i*8+7];

            for (int round = 0; round < 16; round++) {
                uint32_t temp = block[1];
                block[1] = block[0] ^ mars_forward_mixing(block[1], ctx.key_schedule[round]);
                block[0] = temp;
            }

            output[i*8] = (block[0] >> 24) & 0xFF;
            output[i*8+1] = (block[0] >> 16) & 0xFF;
            output[i*8+2] = (block[0] >> 8) & 0xFF;
            output[i*8+3] = block[0] & 0xFF;
            output[i*8+4] = (block[1] >> 24) & 0xFF;
            output[i*8+5] = (block[1] >> 16) & 0xFF;
            output[i*8+6] = (block[1] >> 8) & 0xFF;
            output[i*8+7] = block[1] & 0xFF;
        }
    }

    return 0;
}

int main() {
    uint8_t key[16] = "CastSecretKey123";
    uint8_t plaintext[16] = "TestDataForCAST!";
    uint8_t ciphertext[16];
    uint8_t decrypted[16];

    const char* algorithms[] = {"FeistelCipher-128", "MARS"};

    printf("Original: %.*s\n", 16, plaintext);

    for (int alg = 0; alg < 2; alg++) {
        printf("\n=== %s ===\n", algorithms[alg]);

        if (feistel_cipher_process(plaintext, ciphertext, 16, key, 16, alg, 1) == 0) {
            printf("Encrypted: ");
            for (int i = 0; i < 16; i++) {
                printf("%02x ", ciphertext[i]);
            }
            printf("\n");

            if (feistel_cipher_process(ciphertext, decrypted, 16, key, 16, alg, 0) == 0) {
                printf("Decrypted: %.*s\n", 16, decrypted);
            }
        }
    }

    return 0;
}