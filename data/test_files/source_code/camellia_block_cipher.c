#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define BLOCK_SIZE 16
#define CAMELLIA_128_ROUNDS 18
#define CAMELLIA_256_ROUNDS 24

typedef struct {
    uint64_t subkeys[34]; 
    int rounds;
} camellia_ctx_t;

static const uint8_t camellia_sbox[256] = {
    112, 130, 44, 236, 179, 39, 192, 229, 228, 133, 87, 53, 234, 12, 174, 65,
    35, 239, 107, 147, 69, 25, 165, 33, 237, 14, 79, 78, 29, 101, 146, 189,
    134, 184, 175, 143, 124, 235, 31, 206, 62, 48, 220, 95, 94, 197, 11, 26,
    166, 225, 57, 202, 213, 71, 93, 61, 217, 1, 90, 214, 81, 86, 108, 77,
    139, 13, 154, 102, 251, 204, 176, 45, 116, 18, 43, 32, 240, 177, 132, 153,
    223, 76, 203, 194, 52, 126, 118, 5, 109, 183, 169, 49, 209, 23, 4, 215,
    20, 88, 58, 97, 222, 27, 17, 28, 50, 15, 156, 22, 83, 24, 242, 34,
    254, 68, 207, 178, 195, 181, 122, 145, 36, 8, 232, 168, 96, 252, 105, 80,
    170, 208, 160, 125, 161, 137, 98, 151, 84, 91, 30, 149, 224, 255, 100, 210,
    16, 196, 0, 72, 163, 247, 117, 219, 138, 3, 230, 218, 9, 63, 221, 148,
    135, 92, 131, 2, 205, 74, 144, 51, 115, 103, 246, 243, 157, 127, 191, 226,
    82, 155, 216, 38, 200, 55, 198, 59, 129, 150, 111, 75, 19, 190, 99, 46,
    233, 121, 167, 140, 159, 110, 188, 142, 41, 245, 249, 182, 47, 253, 180, 89,
    120, 152, 6, 106, 231, 70, 113, 186, 212, 37, 171, 66, 136, 162, 141, 250,
    114, 7, 185, 85, 248, 238, 172, 10, 54, 73, 42, 104, 60, 56, 241, 164,
    64, 40, 211, 123, 187, 201, 67, 193, 21, 227, 173, 244, 119, 199, 128, 158
};

static const int left_rotations[34] = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34
};

static uint64_t rotl64(uint64_t x, int n) {
    return (x << n) | (x >> (64 - n));
}

static uint64_t rotr64(uint64_t x, int n) {
    return (x >> n) | (x << (64 - n));
}

static uint64_t camellia_f(uint64_t x, uint64_t k) {
    uint64_t y = x ^ k;

    uint8_t bytes[8];
    for (int i = 0; i < 8; i++) {
        bytes[i] = camellia_sbox[(y >> (8 * i)) & 0xFF];
    }

    uint64_t z = 0;
    for (int i = 0; i < 8; i++) {
        z |= ((uint64_t)bytes[i]) << (8 * i);
    }

    return rotl64(z, 1) ^ rotl64(z, 8) ^ rotl64(z, 16) ^ rotl64(z, 24);
}

static uint64_t camellia_fl(uint64_t x, uint64_t k) {
    uint32_t xl = x & 0xFFFFFFFF;
    uint32_t xr = (x >> 32) & 0xFFFFFFFF;
    uint32_t kl = k & 0xFFFFFFFF;
    uint32_t kr = (k >> 32) & 0xFFFFFFFF;

    xr ^= rotl64(xl & kl, 1);
    xl ^= (xr | kr);

    return ((uint64_t)xr << 32) | xl;
}

static uint64_t camellia_flinv(uint64_t x, uint64_t k) {
    uint32_t xl = x & 0xFFFFFFFF;
    uint32_t xr = (x >> 32) & 0xFFFFFFFF;
    uint32_t kl = k & 0xFFFFFFFF;
    uint32_t kr = (k >> 32) & 0xFFFFFFFF;

    xl ^= (xr | kr);
    xr ^= rotl64(xl & kl, 1);

    return ((uint64_t)xr << 32) | xl;
}

void camellia_key_schedule(camellia_ctx_t *ctx, const uint8_t *key, int key_bits) {
    uint64_t kl, kr, ka, kb;
    uint64_t constants[6] = {
        0xA09E667F3BCC908B, 0xB67AE8584CAA73B2, 0xC6EF372FE94F82BE,
        0x54FF53A5F1D36F1C, 0x10E527FADE682D1D, 0xB05688C2B3E6C1FD
    };

    kl = 0;
    kr = 0;
    for (int i = 0; i < 8; i++) {
        kl = (kl << 8) | key[i];
    }

    if (key_bits == 128) {
        kr = 0;
        ctx->rounds = CAMELLIA_128_ROUNDS;
    } else {
        for (int i = 8; i < 16; i++) {
            kr = (kr << 8) | key[i];
        }
        if (key_bits == 192) {
            kr ^= 0xFFFFFFFFFFFFFFFF;
        }
        ctx->rounds = CAMELLIA_256_ROUNDS;
    }

    uint64_t d1 = kl ^ kr;
    uint64_t d2 = camellia_f(d1, constants[0]) ^ kr;
    d1 = camellia_f(d2, constants[1]) ^ d1;
    ka = d1;
    d2 = camellia_f(d1, constants[2]) ^ d2;
    kb = d2;

    int key_idx = 0;

    if (key_bits == 128) {
        ctx->subkeys[0] = kl;
        ctx->subkeys[1] = ka;
        ctx->subkeys[2] = rotl64(kl, 15);
        ctx->subkeys[3] = rotl64(ka, 15);
        ctx->subkeys[4] = rotl64(ka, 30);
        ctx->subkeys[5] = rotl64(kl, 45);
        ctx->subkeys[6] = rotl64(ka, 45);
        ctx->subkeys[7] = rotl64(kl, 60);
        ctx->subkeys[8] = rotl64(ka, 60);

        ctx->subkeys[9] = rotl64(kl, 77);
        ctx->subkeys[10] = rotl64(ka, 77);

        ctx->subkeys[11] = rotl64(kl, 94);
        ctx->subkeys[12] = rotl64(ka, 94);
        ctx->subkeys[13] = rotl64(kl, 111);
        ctx->subkeys[14] = rotl64(ka, 111);

        ctx->subkeys[15] = rotl64(kl, 128);
        ctx->subkeys[16] = rotl64(ka, 128);

        ctx->subkeys[17] = rotl64(ka, 143);
    }
}

void camellia_encrypt_block(camellia_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint64_t left = 0, right = 0;

    for (int i = 0; i < 8; i++) {
        left = (left << 8) | input[i];
        right = (right << 8) | input[i + 8];
    }

    left ^= ctx->subkeys[0];
    right ^= ctx->subkeys[1];

    int round = 0;

    for (int i = 0; i < ctx->rounds; i++) {
        if (i == 6 || i == 12 || i == 18) {
            
            left = camellia_fl(left, ctx->subkeys[round + 2]);
            right = camellia_flinv(right, ctx->subkeys[round + 3]);
            round += 4;
        } else {
            
            uint64_t temp = right ^ camellia_f(left, ctx->subkeys[round + 2]);
            right = left;
            left = temp;
            round += 2;
        }
    }

    uint64_t temp = left;
    left = right ^ ctx->subkeys[round];
    right = temp ^ ctx->subkeys[round + 1];

    for (int i = 7; i >= 0; i--) {
        output[i] = left & 0xFF;
        output[i + 8] = right & 0xFF;
        left >>= 8;
        right >>= 8;
    }
}

void camellia_decrypt_block(camellia_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint64_t left = 0, right = 0;

    for (int i = 0; i < 8; i++) {
        left = (left << 8) | input[i];
        right = (right << 8) | input[i + 8];
    }

    int round = ctx->rounds * 2;

    uint64_t temp = left ^ ctx->subkeys[round + 1];
    left = right ^ ctx->subkeys[round];
    right = temp;

    for (int i = ctx->rounds - 1; i >= 0; i--) {
        if (i == 18 || i == 12 || i == 6) {
            
            round -= 4;
            left = camellia_flinv(left, ctx->subkeys[round + 2]);
            right = camellia_fl(right, ctx->subkeys[round + 3]);
        } else {
            
            round -= 2;
            temp = right;
            right = left ^ camellia_f(right, ctx->subkeys[round + 2]);
            left = temp;
        }
    }

    left ^= ctx->subkeys[0];
    right ^= ctx->subkeys[1];

    for (int i = 7; i >= 0; i--) {
        output[i] = left & 0xFF;
        output[i + 8] = right & 0xFF;
        left >>= 8;
        right >>= 8;
    }
}

int camellia_process(const uint8_t *input, uint8_t *output, size_t length,
                    const uint8_t *key, int key_bits, int encrypt) {
    if (length % BLOCK_SIZE != 0) {
        return -1;
    }

    camellia_ctx_t ctx;
    camellia_key_schedule(&ctx, key, key_bits);

    size_t blocks = length / BLOCK_SIZE;
    for (size_t i = 0; i < blocks; i++) {
        if (encrypt) {
            camellia_encrypt_block(&ctx, input + i * BLOCK_SIZE,
                                 output + i * BLOCK_SIZE);
        } else {
            camellia_decrypt_block(&ctx, input + i * BLOCK_SIZE,
                                 output + i * BLOCK_SIZE);
        }
    }

    return 0;
}

int main() {
    uint8_t key128[16] = "CamelliaKey12345";
    uint8_t key256[32] = "CamelliaKey256bit_SecretKey!!!!";
    uint8_t plaintext[32] = "This is test data for CamelliaEncryption!!";
    uint8_t ciphertext[32];
    uint8_t decrypted[32];

    printf("Original: %.*s\n", 32, plaintext);

    printf("\n=== CamelliaEncryption-128 ===\n");
    if (camellia_process(plaintext, ciphertext, 32, key128, 128, 1) == 0) {
        printf("Encrypted: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        if (camellia_process(ciphertext, decrypted, 32, key128, 128, 0) == 0) {
            printf("Decrypted: %.*s\n", 32, decrypted);
        }
    }

    printf("\n=== CamelliaEncryption-256 ===\n");
    if (camellia_process(plaintext, ciphertext, 32, key256, 256, 1) == 0) {
        printf("Encrypted: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        if (camellia_process(ciphertext, decrypted, 32, key256, 256, 0) == 0) {
            printf("Decrypted: %.*s\n", 32, decrypted);
        }
    }

    return 0;
}