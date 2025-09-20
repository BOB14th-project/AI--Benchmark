#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define STATE_SIZE 256

typedef struct {
    uint8_t state[STATE_SIZE];
    uint8_t i, j;
} rc4_ctx_t;

void rc4_init(rc4_ctx_t *ctx, const uint8_t *key, size_t key_length) {
    int i, j = 0;

    for (i = 0; i < STATE_SIZE; i++) {
        ctx->state[i] = i;
    }

    for (i = 0; i < STATE_SIZE; i++) {
        j = (j + ctx->state[i] + key[i % key_length]) % STATE_SIZE;

        uint8_t temp = ctx->state[i];
        ctx->state[i] = ctx->state[j];
        ctx->state[j] = temp;
    }

    ctx->i = 0;
    ctx->j = 0;
}

uint8_t rc4_generate_byte(rc4_ctx_t *ctx) {
    ctx->i = (ctx->i + 1) % STATE_SIZE;
    ctx->j = (ctx->j + ctx->state[ctx->i]) % STATE_SIZE;

    uint8_t temp = ctx->state[ctx->i];
    ctx->state[ctx->i] = ctx->state[ctx->j];
    ctx->state[ctx->j] = temp;

    uint8_t k = ctx->state[(ctx->state[ctx->i] + ctx->state[ctx->j]) % STATE_SIZE];
    return k;
}

void rc4_crypt(rc4_ctx_t *ctx, const uint8_t *input, uint8_t *output, size_t length) {
    for (size_t i = 0; i < length; i++) {
        uint8_t keystream_byte = rc4_generate_byte(ctx);
        output[i] = input[i] ^ keystream_byte;
    }
}

void rc4_drop_init(rc4_ctx_t *ctx, const uint8_t *key, size_t key_length, int drop_bytes) {
    rc4_init(ctx, key, key_length);

    for (int i = 0; i < drop_bytes; i++) {
        rc4_generate_byte(ctx);
    }
}

typedef struct {
    uint8_t state[STATE_SIZE];
    uint8_t i, j, k, z, a, w;
} spritz_ctx_t;

static void spritz_swap(spritz_ctx_t *ctx, uint8_t i, uint8_t j) {
    uint8_t temp = ctx->state[i];
    ctx->state[i] = ctx->state[j];
    ctx->state[j] = temp;
}

static void spritz_update(spritz_ctx_t *ctx) {
    ctx->i = (ctx->i + ctx->w) % STATE_SIZE;
    ctx->j = (ctx->k + ctx->state[(ctx->j + ctx->state[ctx->i]) % STATE_SIZE]) % STATE_SIZE;
    ctx->k = (ctx->i + ctx->k + ctx->state[ctx->j]) % STATE_SIZE;
    spritz_swap(ctx, ctx->i, ctx->j);
}

static void spritz_whip(spritz_ctx_t *ctx, int r) {
    for (int i = 0; i < r; i++) {
        spritz_update(ctx);
    }
    ctx->w = (ctx->w + 2) % STATE_SIZE;
}

static void spritz_crush(spritz_ctx_t *ctx) {
    for (int v = 0; v < STATE_SIZE / 2; v++) {
        if (ctx->state[v] > ctx->state[STATE_SIZE - 1 - v]) {
            spritz_swap(ctx, v, STATE_SIZE - 1 - v);
        }
    }
}

static void spritz_shuffle(spritz_ctx_t *ctx) {
    spritz_whip(ctx, 2 * STATE_SIZE);
    spritz_crush(ctx);
    spritz_whip(ctx, 2 * STATE_SIZE);
    spritz_crush(ctx);
    spritz_whip(ctx, 2 * STATE_SIZE);
    ctx->a = 0;
}

static void spritz_absorb_nibble(spritz_ctx_t *ctx, uint8_t x) {
    if (ctx->a == STATE_SIZE / 2) {
        spritz_shuffle(ctx);
    }
    spritz_swap(ctx, ctx->a, (STATE_SIZE / 2 + x) % STATE_SIZE);
    ctx->a++;
}

static void spritz_absorb_byte(spritz_ctx_t *ctx, uint8_t b) {
    spritz_absorb_nibble(ctx, b & 0x0F);
    spritz_absorb_nibble(ctx, b >> 4);
}

static void spritz_absorb(spritz_ctx_t *ctx, const uint8_t *data, size_t length) {
    for (size_t i = 0; i < length; i++) {
        spritz_absorb_byte(ctx, data[i]);
    }
}

static uint8_t spritz_drip(spritz_ctx_t *ctx) {
    if (ctx->a > 0) {
        spritz_shuffle(ctx);
    }
    spritz_update(ctx);
    return ctx->state[(ctx->j + ctx->state[(ctx->i + ctx->state[(ctx->z + ctx->k) % STATE_SIZE]) % STATE_SIZE]) % STATE_SIZE];
}

void spritz_init(spritz_ctx_t *ctx, const uint8_t *key, size_t key_length) {
    
    for (int i = 0; i < STATE_SIZE; i++) {
        ctx->state[i] = i;
    }
    ctx->i = ctx->j = ctx->k = ctx->z = ctx->a = 0;
    ctx->w = 1;

    spritz_absorb(ctx, key, key_length);
}

void spritz_crypt(spritz_ctx_t *ctx, const uint8_t *input, uint8_t *output, size_t length) {
    for (size_t i = 0; i < length; i++) {
        output[i] = input[i] ^ spritz_drip(ctx);
    }
}

typedef struct {
    uint8_t P[STATE_SIZE];
    uint8_t s;
} vmpc_ctx_t;

void vmpc_init(vmpc_ctx_t *ctx, const uint8_t *key, size_t key_length, const uint8_t *iv, size_t iv_length) {
    
    for (int i = 0; i < STATE_SIZE; i++) {
        ctx->P[i] = i;
    }
    ctx->s = 0;

    for (int m = 0; m < 768; m++) {
        ctx->s = ctx->P[(ctx->s + ctx->P[m % STATE_SIZE] + key[m % key_length]) % STATE_SIZE];
        uint8_t temp = ctx->P[m % STATE_SIZE];
        ctx->P[m % STATE_SIZE] = ctx->P[ctx->s];
        ctx->P[ctx->s] = temp;
    }

    for (int m = 0; m < 768; m++) {
        ctx->s = ctx->P[(ctx->s + ctx->P[m % STATE_SIZE] + iv[m % iv_length]) % STATE_SIZE];
        uint8_t temp = ctx->P[m % STATE_SIZE];
        ctx->P[m % STATE_SIZE] = ctx->P[ctx->s];
        ctx->P[ctx->s] = temp;
    }
}

uint8_t vmpc_generate_byte(vmpc_ctx_t *ctx) {
    static uint8_t n = 0;

    ctx->s = ctx->P[(ctx->s + ctx->P[n]) % STATE_SIZE];
    uint8_t output = ctx->P[(ctx->P[ctx->P[ctx->s]] + 1) % STATE_SIZE];

    uint8_t temp = ctx->P[n];
    ctx->P[n] = ctx->P[ctx->s];
    ctx->P[ctx->s] = temp;

    n = (n + 1) % STATE_SIZE;
    return output;
}

void vmpc_crypt(vmpc_ctx_t *ctx, const uint8_t *input, uint8_t *output, size_t length) {
    for (size_t i = 0; i < length; i++) {
        output[i] = input[i] ^ vmpc_generate_byte(ctx);
    }
}

int stream_generator_process(const uint8_t *input, uint8_t *output, size_t length,
                           const uint8_t *key, size_t key_length, int variant) {
    switch (variant) {
        case 0: { 
            rc4_ctx_t ctx;
            rc4_init(&ctx, key, key_length);
            rc4_crypt(&ctx, input, output, length);
            break;
        }
        case 1: { 
            rc4_ctx_t ctx;
            rc4_drop_init(&ctx, key, key_length, 3072);
            rc4_crypt(&ctx, input, output, length);
            break;
        }
        case 2: { 
            spritz_ctx_t ctx;
            spritz_init(&ctx, key, key_length);
            spritz_crypt(&ctx, input, output, length);
            break;
        }
        case 3: { 
            vmpc_ctx_t ctx;
            uint8_t iv[8] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
            vmpc_init(&ctx, key, key_length, iv, 8);
            vmpc_crypt(&ctx, input, output, length);
            break;
        }
        default:
            return -1;
    }
    return 0;
}

int main() {
    uint8_t key[] = "SecretStreamKey";
    uint8_t plaintext[] = "This is a test message for stream ciphers!";
    uint8_t ciphertext[64];
    uint8_t decrypted[64];

    size_t length = strlen((char*)plaintext);
    size_t key_length = strlen((char*)key);

    const char* cipher_names[] = {"StreamGenerator", "StreamGenerator-drop", "Spritz", "VMPC"};

    printf("Original: %s\n\n", plaintext);

    for (int variant = 0; variant < 4; variant++) {
        printf("=== %s ===\n", cipher_names[variant]);

        stream_generator_process(plaintext, ciphertext, length, key, key_length, variant);
        printf("Encrypted: ");
        for (size_t i = 0; i < length; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        stream_generator_process(ciphertext, decrypted, length, key, key_length, variant);
        decrypted[length] = '\0';
        printf("Decrypted: %s\n\n", decrypted);
    }

    return 0;
}