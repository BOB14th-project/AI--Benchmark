#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define WHIRLPOOL_DIGEST_SIZE 64
#define WHIRLPOOL_BLOCK_SIZE 64
#define WHIRLPOOL_ROUNDS 10

typedef struct {
    uint64_t state[8];
    uint64_t count;
    uint8_t buffer[WHIRLPOOL_BLOCK_SIZE];
    int buffer_len;
} whirlpool_ctx_t;

static const uint8_t whirlpool_sbox[256] = {
    0x18, 0x23, 0xc6, 0xe8, 0x87, 0xb8, 0x01, 0x4f, 0x36, 0xa6, 0xd2, 0xf5, 0x79, 0x6f, 0x91, 0x52,
    0x60, 0xbc, 0x9b, 0x8e, 0xa3, 0x0c, 0x7b, 0x35, 0x1d, 0xe0, 0xd7, 0xc2, 0x2e, 0x4b, 0xfe, 0x57,
    0x15, 0x77, 0x37, 0xe5, 0x9f, 0xf0, 0x4a, 0xda, 0x58, 0xc9, 0x29, 0x0a, 0xb1, 0xa0, 0x6b, 0x85,
    0xbd, 0x5d, 0x10, 0xf4, 0xcb, 0x3e, 0x05, 0x67, 0xe4, 0x27, 0x41, 0x8b, 0xa7, 0x7d, 0x95, 0xd8,
    0xfb, 0xee, 0x7c, 0x66, 0xdd, 0x17, 0x47, 0x9e, 0xca, 0x2d, 0xbf, 0x07, 0xad, 0x5a, 0x83, 0x33,
    0x63, 0x02, 0xaa, 0x71, 0xc8, 0x19, 0x49, 0xd9, 0xf2, 0xe3, 0x5b, 0x88, 0x9a, 0x26, 0x32, 0xb0,
    0xe9, 0x0f, 0xd5, 0x80, 0xbe, 0xcd, 0x34, 0x48, 0xff, 0x7a, 0x90, 0x5f, 0x20, 0x68, 0x1a, 0xae,
    0xb4, 0x54, 0x93, 0x22, 0x64, 0xf1, 0x73, 0x12, 0x40, 0x08, 0xc3, 0xec, 0xdb, 0xa1, 0x8d, 0x3d,
    0x97, 0x00, 0xcf, 0x2b, 0x76, 0x82, 0xd6, 0x1b, 0xb5, 0xaf, 0x6a, 0x50, 0x45, 0xf3, 0x30, 0xef,
    0x3f, 0x55, 0xa2, 0xea, 0x65, 0xba, 0x2f, 0xc0, 0xde, 0x1c, 0xfd, 0x4d, 0x92, 0x75, 0x06, 0x8a,
    0xb2, 0xe6, 0x0e, 0x1f, 0x62, 0xd4, 0xa8, 0x96, 0xf9, 0xc5, 0x25, 0x59, 0x84, 0x72, 0x39, 0x4c,
    0x5e, 0x78, 0x38, 0x8c, 0xd1, 0xa5, 0xe2, 0x61, 0xb3, 0x21, 0x9c, 0x1e, 0x43, 0xc7, 0xfc, 0x04,
    0x51, 0x99, 0x6d, 0x0d, 0xfa, 0xdf, 0x7e, 0x24, 0x3b, 0xab, 0xce, 0x11, 0x8f, 0x4e, 0xb7, 0xeb,
    0x3c, 0x81, 0x94, 0xf7, 0xb9, 0x13, 0x2c, 0xd3, 0xe7, 0x6e, 0xc4, 0x03, 0x56, 0x44, 0x7f, 0xa9,
    0x2a, 0xbb, 0xc1, 0x53, 0xdc, 0x0b, 0x9d, 0x6c, 0x31, 0x74, 0xf6, 0x46, 0xac, 0x89, 0x14, 0xe1,
    0x16, 0x3a, 0x69, 0x09, 0x70, 0xb6, 0xd0, 0xed, 0xcc, 0x42, 0x98, 0xa4, 0x28, 0x5c, 0xf8, 0x86
};

static const uint64_t whirlpool_constants[WHIRLPOOL_ROUNDS] = {
    0x1823c6e887b8014f, 0x36a6d2f5796f9152, 0x60bc9b8ea30c7b35, 0x1de0d7c22e4bfe57,
    0x157737e59ff04ada, 0x58c9290ab1a06b85, 0xbd5d10f4cb3e0567, 0xe427418ba77d95d8,
    0xfbee7c66dd17479e, 0xca2dbf07ad5a8333
};

static uint64_t whirlpool_sub_bytes(uint64_t x) {
    uint64_t result = 0;
    for (int i = 0; i < 8; i++) {
        uint8_t byte = (x >> (i * 8)) & 0xFF;
        result |= ((uint64_t)whirlpool_sbox[byte]) << (i * 8);
    }
    return result;
}

static void whirlpool_shift_columns(uint64_t *state) {
    uint64_t temp[8];

    temp[0] = state[0];
    temp[1] = (state[1] << 8) | (state[1] >> 56);
    temp[2] = (state[2] << 16) | (state[2] >> 48);
    temp[3] = (state[3] << 24) | (state[3] >> 40);
    temp[4] = (state[4] << 32) | (state[4] >> 32);
    temp[5] = (state[5] << 40) | (state[5] >> 24);
    temp[6] = (state[6] << 48) | (state[6] >> 16);
    temp[7] = (state[7] << 56) | (state[7] >> 8);

    memcpy(state, temp, sizeof(temp));
}

static uint8_t whirlpool_mul(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    while (a && b) {
        if (b & 1) {
            result ^= a;
        }
        if (a & 0x80) {
            a = (a << 1) ^ 0x11d; 
        } else {
            a <<= 1;
        }
        b >>= 1;
    }
    return result;
}

static void whirlpool_mix_columns(uint64_t *state) {
    
    uint64_t temp[8];

    for (int i = 0; i < 8; i++) {
        temp[i] = 0;
        for (int j = 0; j < 8; j++) {
            uint8_t byte = (state[j] >> (i * 8)) & 0xFF;

            temp[i] ^= ((uint64_t)whirlpool_mul(0x01, byte)) << (0 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x01, byte)) << (1 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x04, byte)) << (2 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x01, byte)) << (3 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x08, byte)) << (4 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x05, byte)) << (5 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x02, byte)) << (6 * 8);
            temp[i] ^= ((uint64_t)whirlpool_mul(0x09, byte)) << (7 * 8);
        }
    }

    memcpy(state, temp, sizeof(temp));
}

static void whirlpool_round(uint64_t *state, uint64_t *key, int round) {
    
    for (int i = 0; i < 8; i++) {
        state[i] = whirlpool_sub_bytes(state[i]);
        key[i] = whirlpool_sub_bytes(key[i]);
    }

    whirlpool_shift_columns(state);
    whirlpool_shift_columns(key);

    whirlpool_mix_columns(state);
    whirlpool_mix_columns(key);

    key[0] ^= whirlpool_constants[round];
    for (int i = 0; i < 8; i++) {
        state[i] ^= key[i];
    }
}

static void whirlpool_compress(whirlpool_ctx_t *ctx, const uint8_t *block) {
    uint64_t state[8];
    uint64_t key[8];

    for (int i = 0; i < 8; i++) {
        state[i] = 0;
        key[i] = ctx->state[i];
        for (int j = 0; j < 8; j++) {
            state[i] |= ((uint64_t)block[i * 8 + j]) << (j * 8);
        }
    }

    for (int i = 0; i < 8; i++) {
        state[i] ^= key[i];
    }

    for (int round = 0; round < WHIRLPOOL_ROUNDS; round++) {
        whirlpool_round(state, key, round);
    }

    for (int i = 0; i < 8; i++) {
        ctx->state[i] ^= state[i] ^ key[i];
    }
}

void whirlpool_init(whirlpool_ctx_t *ctx) {
    memset(ctx->state, 0, sizeof(ctx->state));
    ctx->count = 0;
    ctx->buffer_len = 0;
}

void whirlpool_update(whirlpool_ctx_t *ctx, const uint8_t *data, size_t length) {
    while (length > 0) {
        size_t to_copy = WHIRLPOOL_BLOCK_SIZE - ctx->buffer_len;
        if (to_copy > length) {
            to_copy = length;
        }

        memcpy(ctx->buffer + ctx->buffer_len, data, to_copy);
        ctx->buffer_len += to_copy;
        ctx->count += to_copy;
        data += to_copy;
        length -= to_copy;

        if (ctx->buffer_len == WHIRLPOOL_BLOCK_SIZE) {
            whirlpool_compress(ctx, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
}

void whirlpool_final(whirlpool_ctx_t *ctx, uint8_t *digest) {
    
    uint64_t bit_count = ctx->count * 8;
    ctx->buffer[ctx->buffer_len++] = 0x80;

    if (ctx->buffer_len > 32) {
        while (ctx->buffer_len < WHIRLPOOL_BLOCK_SIZE) {
            ctx->buffer[ctx->buffer_len++] = 0x00;
        }
        whirlpool_compress(ctx, ctx->buffer);
        ctx->buffer_len = 0;
    }

    while (ctx->buffer_len < 32) {
        ctx->buffer[ctx->buffer_len++] = 0x00;
    }

    for (int i = 0; i < 32; i++) {
        ctx->buffer[32 + i] = 0; 
    }

    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (bit_count >> (56 - i * 8)) & 0xFF;
    }

    whirlpool_compress(ctx, ctx->buffer);

    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            digest[i * 8 + j] = (ctx->state[i] >> (56 - j * 8)) & 0xFF;
        }
    }
}

typedef struct {
    uint32_t state[5];
    uint64_t count;
    uint8_t buffer[64];
    int buffer_len;
} ripemd160_ctx_t;

static uint32_t ripemd_f(int round, uint32_t x, uint32_t y, uint32_t z) {
    switch (round / 16) {
        case 0: return x ^ y ^ z;
        case 1: return (x & y) | (~x & z);
        case 2: return (x | ~y) ^ z;
        case 3: return (x & z) | (y & ~z);
        case 4: return x ^ (y | ~z);
        default: return 0;
    }
}

static uint32_t ripemd_rotl(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

void ripemd160_init(ripemd160_ctx_t *ctx) {
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xEFCDAB89;
    ctx->state[2] = 0x98BADCFE;
    ctx->state[3] = 0x10325476;
    ctx->state[4] = 0xC3D2E1F0;
    ctx->count = 0;
    ctx->buffer_len = 0;
}

int hash_digest_compute(const uint8_t *input, size_t length, uint8_t *output, int algorithm) {
    if (algorithm == 0) { 
        whirlpool_ctx_t ctx;
        whirlpool_init(&ctx);
        whirlpool_update(&ctx, input, length);
        whirlpool_final(&ctx, output);
        return WHIRLPOOL_DIGEST_SIZE;
    } else { 
        ripemd160_ctx_t ctx;
        ripemd160_init(&ctx);

        uint32_t hash[5];
        memcpy(hash, ctx.state, sizeof(hash));

        for (size_t i = 0; i < length; i++) {
            hash[i % 5] ^= input[i];
            hash[i % 5] = ripemd_rotl(hash[i % 5], 11);
            hash[i % 5] += 0x5A827999;
        }

        for (int i = 0; i < 5; i++) {
            output[i * 4] = hash[i] & 0xFF;
            output[i * 4 + 1] = (hash[i] >> 8) & 0xFF;
            output[i * 4 + 2] = (hash[i] >> 16) & 0xFF;
            output[i * 4 + 3] = (hash[i] >> 24) & 0xFF;
        }
        return 20;
    }
}

int main() {
    uint8_t input[] = "The quick brown fox jumps over the lazy dog";
    uint8_t hash[64];

    const char* algorithms[] = {"HashDigest", "RIPEMD-160"};

    for (int alg = 0; alg < 2; alg++) {
        printf("=== %s ===\n", algorithms[alg]);

        int hash_len = hash_digest_compute(input, strlen((char*)input), hash, alg);

        printf("Input: %s\n", input);
        printf("Hash:  ");
        for (int i = 0; i < hash_len; i++) {
            printf("%02x", hash[i]);
        }
        printf("\n\n");
    }

    return 0;
}