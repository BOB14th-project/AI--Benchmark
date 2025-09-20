#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define BLOCK_SIZE 16
#define KEY_SCHEDULE_SIZE 40
#define ROUNDS 16

typedef struct {
    uint32_t subkeys[KEY_SCHEDULE_SIZE];
    uint32_t sbox_keys[4];
    uint8_t key_length;
} twofish_ctx_t;

static const uint8_t mds_matrix[4][4] = {
    {0x01, 0xEF, 0x5B, 0x5B},
    {0x5B, 0xEF, 0xEF, 0x01},
    {0xEF, 0x5B, 0x01, 0xEF},
    {0xEF, 0x01, 0xEF, 0x5B}
};

static const uint8_t q0[256] = {
    0xA9, 0x67, 0xB3, 0xE8, 0x04, 0xFD, 0xA3, 0x76,
    0x9A, 0x92, 0x80, 0x78, 0xE4, 0xDD, 0xD1, 0x38,
    
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38
};

static const uint8_t q1[256] = {
    0x75, 0xF3, 0xC6, 0xF4, 0xDB, 0x7B, 0xFB, 0xC8,
    0x4A, 0xD3, 0xE6, 0x6B, 0x45, 0x7D, 0xE8, 0x4B,
    
    0x29, 0xAA, 0x81, 0x81, 0x05, 0x05, 0xA8, 0xA8
};

static uint8_t galois_multiply(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    while (a && b) {
        if (b & 1) {
            result ^= a;
        }
        if (a & 0x80) {
            a = (a << 1) ^ 0x14D; 
        } else {
            a <<= 1;
        }
        b >>= 1;
    }
    return result;
}

static uint32_t mds_column_mix(uint32_t input) {
    uint8_t bytes[4];
    uint8_t result[4] = {0};

    bytes[0] = input & 0xFF;
    bytes[1] = (input >> 8) & 0xFF;
    bytes[2] = (input >> 16) & 0xFF;
    bytes[3] = (input >> 24) & 0xFF;

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            result[i] ^= galois_multiply(mds_matrix[i][j], bytes[j]);
        }
    }

    return (result[3] << 24) | (result[2] << 16) | (result[1] << 8) | result[0];
}

static uint32_t g_function(uint32_t x, const uint32_t *sbox_keys, int key_length) {
    uint8_t a = x & 0xFF;
    uint8_t b = (x >> 8) & 0xFF;
    uint8_t c = (x >> 16) & 0xFF;
    uint8_t d = (x >> 24) & 0xFF;

    if (key_length >= 32) {
        a = q1[a] ^ ((sbox_keys[3] >> 24) & 0xFF);
        b = q0[b] ^ ((sbox_keys[3] >> 16) & 0xFF);
        c = q0[c] ^ ((sbox_keys[3] >> 8) & 0xFF);
        d = q1[d] ^ (sbox_keys[3] & 0xFF);
    }

    if (key_length >= 24) {
        a = q1[a] ^ ((sbox_keys[2] >> 24) & 0xFF);
        b = q1[b] ^ ((sbox_keys[2] >> 16) & 0xFF);
        c = q0[c] ^ ((sbox_keys[2] >> 8) & 0xFF);
        d = q0[d] ^ (sbox_keys[2] & 0xFF);
    }

    a = q1[q0[q0[a] ^ ((sbox_keys[1] >> 24) & 0xFF)] ^ ((sbox_keys[0] >> 24) & 0xFF)];
    b = q0[q0[q1[b] ^ ((sbox_keys[1] >> 16) & 0xFF)] ^ ((sbox_keys[0] >> 16) & 0xFF)];
    c = q1[q1[q0[c] ^ ((sbox_keys[1] >> 8) & 0xFF)] ^ ((sbox_keys[0] >> 8) & 0xFF)];
    d = q0[q1[q1[d] ^ (sbox_keys[1] & 0xFF)] ^ (sbox_keys[0] & 0xFF)];

    uint32_t result = (d << 24) | (c << 16) | (b << 8) | a;
    return mds_column_mix(result);
}

void twofish_key_schedule(twofish_ctx_t *ctx, const uint8_t *key, int key_length) {
    ctx->key_length = key_length;

    for (int i = 0; i < (key_length / 8); i++) {
        ctx->sbox_keys[i] = (key[i*8+3] << 24) | (key[i*8+2] << 16) |
                           (key[i*8+1] << 8) | key[i*8];
    }

    for (int i = 0; i < KEY_SCHEDULE_SIZE; i += 2) {
        uint32_t A = g_function(i * 0x02020202, ctx->sbox_keys, key_length);
        uint32_t B = g_function((i + 1) * 0x02020202, ctx->sbox_keys, key_length);
        B = (B << 8) | (B >> 24); 

        ctx->subkeys[i] = A + B;
        ctx->subkeys[i + 1] = ((A + 2 * B) << 9) | ((A + 2 * B) >> 23); 
    }
}

void twofish_encrypt_block(twofish_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32_t blocks[4];

    for (int i = 0; i < 4; i++) {
        blocks[i] = (input[i*4+3] << 24) | (input[i*4+2] << 16) |
                   (input[i*4+1] << 8) | input[i*4];
        blocks[i] ^= ctx->subkeys[i];
    }

    for (int round = 0; round < ROUNDS; round++) {
        uint32_t t0 = g_function(blocks[0], ctx->sbox_keys, ctx->key_length);
        uint32_t t1 = g_function((blocks[1] << 8) | (blocks[1] >> 24), ctx->sbox_keys, ctx->key_length);

        blocks[2] ^= (t0 + t1 + ctx->subkeys[round * 2 + 8]);
        blocks[2] = (blocks[2] >> 1) | (blocks[2] << 31); 

        blocks[3] = ((blocks[3] << 1) | (blocks[3] >> 31)) ^ 
                   (t0 + 2 * t1 + ctx->subkeys[round * 2 + 9]);

        uint32_t temp = blocks[0];
        blocks[0] = blocks[2];
        blocks[2] = temp;
        temp = blocks[1];
        blocks[1] = blocks[3];
        blocks[3] = temp;
    }

    uint32_t temp = blocks[0];
    blocks[0] = blocks[2];
    blocks[2] = temp;
    temp = blocks[1];
    blocks[1] = blocks[3];
    blocks[3] = temp;

    for (int i = 0; i < 4; i++) {
        blocks[i] ^= ctx->subkeys[i + 4];
        output[i*4] = blocks[i] & 0xFF;
        output[i*4+1] = (blocks[i] >> 8) & 0xFF;
        output[i*4+2] = (blocks[i] >> 16) & 0xFF;
        output[i*4+3] = (blocks[i] >> 24) & 0xFF;
    }
}

int advanced_symmetric_encrypt(const uint8_t *plaintext, uint8_t *ciphertext,
                              size_t length, const uint8_t *key, int key_length) {
    if (length % BLOCK_SIZE != 0) {
        return -1; 
    }

    twofish_ctx_t ctx;
    twofish_key_schedule(&ctx, key, key_length);

    size_t blocks = length / BLOCK_SIZE;
    for (size_t i = 0; i < blocks; i++) {
        twofish_encrypt_block(&ctx, plaintext + i * BLOCK_SIZE,
                             ciphertext + i * BLOCK_SIZE);
    }

    return 0;
}

int main() {
    uint8_t key[32] = "This is a 32-byte secret key!!!!";
    uint8_t plaintext[32] = "Hello, this is test data!!!!!!!!";
    uint8_t ciphertext[32];

    printf("Plaintext: ");
    for (int i = 0; i < 32; i++) {
        printf("%c", plaintext[i]);
    }
    printf("\n");

    if (advanced_symmetric_encrypt(plaintext, ciphertext, 32, key, 32) == 0) {
        printf("Ciphertext: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");
    }

    return 0;
}