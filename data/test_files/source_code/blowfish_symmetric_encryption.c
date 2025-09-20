#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROUNDS 16
#define SUBKEY_COUNT 18

typedef struct {
    uint32_t parray[SUBKEY_COUNT];
    uint32_t sboxes[4][256];
    uint8_t initialized;
} fish_context_t;

static const uint32_t initial_p[SUBKEY_COUNT] = {
    0x243f6a88, 0x85a308d3, 0x13198a2e, 0x03707344,
    0xa4093822, 0x299f31d0, 0x082efa98, 0xec4e6c89,
    0x452821e6, 0x38d01377, 0xbe5466cf, 0x34e90c6c,
    0xc0ac29b7, 0xc97c50dd, 0x3f84d5b5, 0xb5470917,
    0x9216d5d9, 0x8979fb1b
};

static void f_function(fish_context_t *ctx, uint32_t x, uint32_t *result) {
    uint8_t a = (x >> 24) & 0xff;
    uint8_t b = (x >> 16) & 0xff;
    uint8_t c = (x >> 8) & 0xff;
    uint8_t d = x & 0xff;

    uint32_t y = ctx->sboxes[0][a] + ctx->sboxes[1][b];
    y ^= ctx->sboxes[2][c];
    y += ctx->sboxes[3][d];

    *result = y;
}

static void initialize_sboxes(fish_context_t *ctx) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 256; j++) {
            ctx->sboxes[i][j] = (i * 256 + j) * 0x9e3779b9;
        }
    }
}

void fish_init(fish_context_t *ctx, const uint8_t *key, size_t key_len) {
    memcpy(ctx->parray, initial_p, sizeof(initial_p));

    initialize_sboxes(ctx);

    int key_idx = 0;
    for (int i = 0; i < SUBKEY_COUNT; i++) {
        uint32_t key_word = 0;
        for (int j = 0; j < 4; j++) {
            key_word = (key_word << 8) | key[key_idx];
            key_idx = (key_idx + 1) % key_len;
        }
        ctx->parray[i] ^= key_word;
    }

    uint32_t left = 0, right = 0;
    for (int i = 0; i < SUBKEY_COUNT; i += 2) {
        for (int round = 0; round < ROUNDS; round++) {
            left ^= ctx->parray[round];
            uint32_t f_result;
            f_function(ctx, left, &f_result);
            right ^= f_result;

            uint32_t temp = left;
            left = right;
            right = temp;
        }

        ctx->parray[i] = left;
        if (i + 1 < SUBKEY_COUNT) {
            ctx->parray[i + 1] = right;
        }
    }

    ctx->initialized = 1;
}

void fish_encrypt_block(fish_context_t *ctx, uint32_t *left, uint32_t *right) {
    if (!ctx->initialized) return;

    for (int round = 0; round < ROUNDS; round++) {
        *left ^= ctx->parray[round];

        uint32_t f_result;
        f_function(ctx, *left, &f_result);
        *right ^= f_result;

        uint32_t temp = *left;
        *left = *right;
        *right = temp;
    }

    uint32_t temp = *left;
    *left = *right;
    *right = temp;

    *right ^= ctx->parray[ROUNDS];
    *left ^= ctx->parray[ROUNDS + 1];
}

void fish_decrypt_block(fish_context_t *ctx, uint32_t *left, uint32_t *right) {
    if (!ctx->initialized) return;

    *left ^= ctx->parray[ROUNDS + 1];
    *right ^= ctx->parray[ROUNDS];

    for (int round = ROUNDS - 1; round >= 0; round--) {
        uint32_t temp = *left;
        *left = *right;
        *right = temp;

        uint32_t f_result;
        f_function(ctx, *left, &f_result);
        *right ^= f_result;

        *left ^= ctx->parray[round];
    }
}

int process_data_stream(const uint8_t *input, uint8_t *output, size_t length,
                       const uint8_t *key, size_t key_len, int encrypt) {
    fish_context_t ctx;
    fish_init(&ctx, key, key_len);

    size_t blocks = length / 8;

    for (size_t i = 0; i < blocks; i++) {
        uint32_t left = (input[i*8] << 24) | (input[i*8+1] << 16) |
                       (input[i*8+2] << 8) | input[i*8+3];
        uint32_t right = (input[i*8+4] << 24) | (input[i*8+5] << 16) |
                        (input[i*8+6] << 8) | input[i*8+7];

        if (encrypt) {
            fish_encrypt_block(&ctx, &left, &right);
        } else {
            fish_decrypt_block(&ctx, &left, &right);
        }

        output[i*8] = (left >> 24) & 0xff;
        output[i*8+1] = (left >> 16) & 0xff;
        output[i*8+2] = (left >> 8) & 0xff;
        output[i*8+3] = left & 0xff;
        output[i*8+4] = (right >> 24) & 0xff;
        output[i*8+5] = (right >> 16) & 0xff;
        output[i*8+6] = (right >> 8) & 0xff;
        output[i*8+7] = right & 0xff;
    }

    return 0;
}

int main() {
    uint8_t key[] = "SecretKey123";
    uint8_t plaintext[] = "HelloWorld!!";
    uint8_t ciphertext[16];
    uint8_t decrypted[16];

    printf("Original: ");
    for (int i = 0; i < 12; i++) {
        printf("%c", plaintext[i]);
    }
    printf("\n");

    process_data_stream(plaintext, ciphertext, 16, key, strlen((char*)key), 1);

    printf("Encrypted: ");
    for (int i = 0; i < 16; i++) {
        printf("%02x ", ciphertext[i]);
    }
    printf("\n");

    process_data_stream(ciphertext, decrypted, 16, key, strlen((char*)key), 0);

    printf("Decrypted: ");
    for (int i = 0; i < 12; i++) {
        printf("%c", decrypted[i]);
    }
    printf("\n");

    return 0;
}