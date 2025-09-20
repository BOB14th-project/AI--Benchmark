#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define TIGER_DIGEST_SIZE 24
#define TIGER_BLOCK_SIZE 64

typedef struct {
    uint64_t state[3];
    uint64_t count;
    uint8_t buffer[TIGER_BLOCK_SIZE];
    int buffer_len;
} tiger_ctx_t;

static const uint64_t tiger_sbox[4][256] = {
    
    {
        0x02AAB17CF7E90C5EULL, 0xAC424B03E243A8ECULL, 0x72CD5BE30DD5FCD3ULL, 0x6D019B93F6F97F3AULL,
        0xCD9978FFD21F9193ULL, 0x7573A1C9708029E2ULL, 0xB164326B922A83C3ULL, 0x46883EEE04915870ULL,
        
        0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A
    },
    
    {
        0xEAD54739FFD0F2AEULL, 0x766A2F5CE2EB0DCAULL, 0x16B36F64CA6BD9A1ULL, 0xBE83E1B56B48F2F7ULL,
        0x45B7D03B0D47C88DULL, 0x3A8EC2F0CAA92B46ULL, 0x4A84A2F4C74D3295ULL, 0x4533DC9F7C89A962ULL,
        
        0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419
    },
    
    {
        0x97E69D93ACE4AC86ULL, 0x06A7B9F8B9B8F5B2ULL, 0x24FA4D8D4EB1A3D3ULL, 0x40C286FA2C621C38ULL,
        0x76A2F25C6B62B7EDULL, 0x46FF10F9B1A7FE0DULL, 0x8C66196F34B63F20ULL, 0x4A3A2BB3F1A7DCCDULL,
        
        0x242070DB, 0xC1BDCEEE, 0xF57C0FAF, 0x4787C62A
    },
    
    {
        0xF90E5D0A3E4C32BBULL, 0x5EE1C39D5A02F77CULL, 0x72EF2F8F1CB78D48ULL, 0x4691E90B8CE4A9CCULL,
        0x8E8F3F87A2A0BA07ULL, 0xCBDC905DD7F9D7B0ULL, 0x2EEB2DC94FEF4AB4ULL, 0x8B3EE33D5EF32B1AULL,
        
        0xA8304613, 0xFD469501, 0x698098D8, 0x8B44F7AF
    }
};

static uint64_t tiger_f(uint64_t a, uint64_t b, uint64_t c, uint64_t x, int mul) {
    c ^= x;
    a -= tiger_sbox[0][(c) & 0xFF] ^ tiger_sbox[1][(c >> 16) & 0xFF] ^
         tiger_sbox[2][(c >> 32) & 0xFF] ^ tiger_sbox[3][(c >> 48) & 0xFF];
    b += tiger_sbox[3][(c >> 8) & 0xFF] ^ tiger_sbox[2][(c >> 24) & 0xFF] ^
         tiger_sbox[1][(c >> 40) & 0xFF] ^ tiger_sbox[0][(c >> 56) & 0xFF];
    b *= mul;
    return a;
}

static void tiger_round(uint64_t *a, uint64_t *b, uint64_t *c, uint64_t x, int mul) {
    *c ^= x;
    *a -= tiger_sbox[0][(*c) & 0xFF] ^ tiger_sbox[1][(*c >> 16) & 0xFF] ^
          tiger_sbox[2][(*c >> 32) & 0xFF] ^ tiger_sbox[3][(*c >> 48) & 0xFF];
    *b += tiger_sbox[3][(*c >> 8) & 0xFF] ^ tiger_sbox[2][(*c >> 24) & 0xFF] ^
          tiger_sbox[1][(*c >> 40) & 0xFF] ^ tiger_sbox[0][(*c >> 56) & 0xFF];
    *b *= mul;
}

static void tiger_pass(uint64_t *a, uint64_t *b, uint64_t *c, uint64_t *x, int mul) {
    tiger_round(a, b, c, x[0], mul);
    tiger_round(b, c, a, x[1], mul);
    tiger_round(c, a, b, x[2], mul);
    tiger_round(a, b, c, x[3], mul);
    tiger_round(b, c, a, x[4], mul);
    tiger_round(c, a, b, x[5], mul);
    tiger_round(a, b, c, x[6], mul);
    tiger_round(b, c, a, x[7], mul);
}

static void tiger_key_schedule(uint64_t *x) {
    x[0] -= x[7] ^ 0xA5A5A5A5A5A5A5A5ULL;
    x[1] ^= x[0];
    x[2] += x[1];
    x[3] -= x[2] ^ ((~x[1]) << 19);
    x[4] ^= x[3];
    x[5] += x[4];
    x[6] -= x[5] ^ ((~x[4]) >> 23);
    x[7] ^= x[6];
    x[0] += x[7];
    x[1] -= x[0] ^ ((~x[7]) << 19);
    x[2] ^= x[1];
    x[3] += x[2];
    x[4] -= x[3] ^ ((~x[2]) >> 23);
    x[5] ^= x[4];
    x[6] += x[5];
    x[7] -= x[6] ^ 0x0123456789ABCDEFULL;
}

static void tiger_compress(tiger_ctx_t *ctx, const uint8_t *block) {
    uint64_t a = ctx->state[0];
    uint64_t b = ctx->state[1];
    uint64_t c = ctx->state[2];
    uint64_t x[8];

    for (int i = 0; i < 8; i++) {
        x[i] = 0;
        for (int j = 0; j < 8; j++) {
            x[i] |= ((uint64_t)block[i * 8 + j]) << (j * 8);
        }
    }

    uint64_t aa = a, bb = b, cc = c;

    tiger_pass(&a, &b, &c, x, 5);
    tiger_key_schedule(x);

    tiger_pass(&c, &a, &b, x, 7);
    tiger_key_schedule(x);

    tiger_pass(&b, &c, &a, x, 9);

    ctx->state[0] = a ^ aa;
    ctx->state[1] = b - bb;
    ctx->state[2] = c + cc;
}

void tiger_init(tiger_ctx_t *ctx) {
    ctx->state[0] = 0x0123456789ABCDEFULL;
    ctx->state[1] = 0xFEDCBA9876543210ULL;
    ctx->state[2] = 0xF096A5B4C3B2E187ULL;
    ctx->count = 0;
    ctx->buffer_len = 0;
}

void tiger_update(tiger_ctx_t *ctx, const uint8_t *data, size_t length) {
    while (length > 0) {
        size_t to_copy = TIGER_BLOCK_SIZE - ctx->buffer_len;
        if (to_copy > length) {
            to_copy = length;
        }

        memcpy(ctx->buffer + ctx->buffer_len, data, to_copy);
        ctx->buffer_len += to_copy;
        ctx->count += to_copy;
        data += to_copy;
        length -= to_copy;

        if (ctx->buffer_len == TIGER_BLOCK_SIZE) {
            tiger_compress(ctx, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
}

void tiger_final(tiger_ctx_t *ctx, uint8_t *digest) {
    
    uint64_t bit_count = ctx->count * 8;
    ctx->buffer[ctx->buffer_len++] = 0x01; 

    if (ctx->buffer_len > 56) {
        while (ctx->buffer_len < TIGER_BLOCK_SIZE) {
            ctx->buffer[ctx->buffer_len++] = 0x00;
        }
        tiger_compress(ctx, ctx->buffer);
        ctx->buffer_len = 0;
    }

    while (ctx->buffer_len < 56) {
        ctx->buffer[ctx->buffer_len++] = 0x00;
    }

    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (bit_count >> (i * 8)) & 0xFF;
    }

    tiger_compress(ctx, ctx->buffer);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 8; j++) {
            digest[i * 8 + j] = (ctx->state[i] >> (j * 8)) & 0xFF;
        }
    }
}

void tiger2_init(tiger_ctx_t *ctx) {
    ctx->state[0] = 0x0123456789ABCDEFULL;
    ctx->state[1] = 0xFEDCBA9876543210ULL;
    ctx->state[2] = 0xF096A5B4C3B2E187ULL;
    ctx->count = 0;
    ctx->buffer_len = 0;
}

void tiger2_final(tiger_ctx_t *ctx, uint8_t *digest) {
    
    uint64_t bit_count = ctx->count * 8;
    ctx->buffer[ctx->buffer_len++] = 0x80; 

    if (ctx->buffer_len > 56) {
        while (ctx->buffer_len < TIGER_BLOCK_SIZE) {
            ctx->buffer[ctx->buffer_len++] = 0x00;
        }
        tiger_compress(ctx, ctx->buffer);
        ctx->buffer_len = 0;
    }

    while (ctx->buffer_len < 56) {
        ctx->buffer[ctx->buffer_len++] = 0x00;
    }

    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (bit_count >> (i * 8)) & 0xFF;
    }

    tiger_compress(ctx, ctx->buffer);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 8; j++) {
            digest[i * 8 + j] = (ctx->state[i] >> (j * 8)) & 0xFF;
        }
    }
}

typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[128];
    int buffer_len;
    int passes;
    int hash_size;
} haval_ctx_t;

static uint32_t haval_f(int pass, uint32_t x, uint32_t y, uint32_t z) {
    switch (pass) {
        case 0: return (z ^ (x & (y ^ z)));
        case 1: return ((x ^ y) ^ z);
        case 2: return ((x & y) | (z & (x ^ y)));
        case 3: return ((x & z) | (y & (~z)));
        case 4: return (x ^ (y | (~z)));
        default: return 0;
    }
}

void haval_init(haval_ctx_t *ctx, int passes, int hash_bits) {
    ctx->state[0] = 0x243F6A88;
    ctx->state[1] = 0x85A308D3;
    ctx->state[2] = 0x13198A2E;
    ctx->state[3] = 0x03707344;
    ctx->state[4] = 0xA4093822;
    ctx->state[5] = 0x299F31D0;
    ctx->state[6] = 0x082EFA98;
    ctx->state[7] = 0xEC4E6C89;

    ctx->count = 0;
    ctx->buffer_len = 0;
    ctx->passes = passes;
    ctx->hash_size = hash_bits / 8;
}

int hash_function_compute(const uint8_t *input, size_t length, uint8_t *output, int algorithm) {
    if (algorithm == 0) { 
        tiger_ctx_t ctx;
        tiger_init(&ctx);
        tiger_update(&ctx, input, length);
        tiger_final(&ctx, output);
        return TIGER_DIGEST_SIZE;
    } else if (algorithm == 1) { 
        tiger_ctx_t ctx;
        tiger2_init(&ctx);
        tiger_update(&ctx, input, length);
        tiger2_final(&ctx, output);
        return TIGER_DIGEST_SIZE;
    } else { 
        haval_ctx_t ctx;
        haval_init(&ctx, 3, 256); 

        uint32_t hash = 0x12345678;
        for (size_t i = 0; i < length; i++) {
            hash ^= input[i];
            hash = (hash << 1) | (hash >> 31);
            hash += 0x9e3779b9;
        }

        for (int i = 0; i < 32; i++) {
            output[i] = (hash >> (8 * (i % 4))) & 0xFF;
            if (i % 4 == 3) hash += 0x12345678;
        }
        return 32;
    }
}

int main() {
    uint8_t input[] = "The quick brown fox jumps over the lazy dog";
    uint8_t hash[32];

    const char* algorithms[] = {"DigestFunction", "Tiger2", "HAVAL"};

    for (int alg = 0; alg < 3; alg++) {
        printf("=== %s ===\n", algorithms[alg]);

        int hash_len = hash_function_compute(input, strlen((char*)input), hash, alg);

        printf("Input: %s\n", input);
        printf("Hash:  ");
        for (int i = 0; i < hash_len; i++) {
            printf("%02x", hash[i]);
        }
        printf("\n\n");
    }

    return 0;
}