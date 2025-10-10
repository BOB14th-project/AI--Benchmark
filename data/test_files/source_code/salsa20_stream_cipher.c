#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROUNDS 20
#define BLOCK_SIZE 64

typedef struct {
    uint32_t input[16];
    uint32_t counter[2];
    uint8_t keystream[BLOCK_SIZE];
    int keystream_pos;
} salsa_ctx_t;

static void quarter_round(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d) {
    *b ^= ((*a + *d) << 7) | ((*a + *d) >> 25);
    *c ^= ((*b + *a) << 9) | ((*b + *a) >> 23);
    *d ^= ((*c + *b) << 13) | ((*c + *b) >> 19);
    *a ^= ((*d + *c) << 18) | ((*d + *c) >> 14);
}

static void salsa_core(uint32_t *output, const uint32_t *input) {
    int i;

    for (i = 0; i < 16; i++) {
        output[i] = input[i];
    }

    for (i = 0; i < ROUNDS; i += 2) {
        
        quarter_round(&output[0], &output[4], &output[8], &output[12]);
        quarter_round(&output[5], &output[9], &output[13], &output[1]);
        quarter_round(&output[10], &output[14], &output[2], &output[6]);
        quarter_round(&output[15], &output[3], &output[7], &output[11]);

        quarter_round(&output[0], &output[1], &output[2], &output[3]);
        quarter_round(&output[5], &output[6], &output[7], &output[4]);
        quarter_round(&output[10], &output[11], &output[8], &output[9]);
        quarter_round(&output[15], &output[12], &output[13], &output[14]);
    }

    for (i = 0; i < 16; i++) {
        output[i] += input[i];
    }
}

void salsa_init(salsa_ctx_t *ctx, const uint8_t *key, const uint8_t *nonce) {
    const uint8_t *constants = (const uint8_t *)"expand 32-byte k";

    ctx->input[0] = ((uint32_t)constants[3] << 24) | ((uint32_t)constants[2] << 16) |
                    ((uint32_t)constants[1] << 8) | constants[0];
    ctx->input[5] = ((uint32_t)constants[7] << 24) | ((uint32_t)constants[6] << 16) |
                    ((uint32_t)constants[5] << 8) | constants[4];
    ctx->input[10] = ((uint32_t)constants[11] << 24) | ((uint32_t)constants[10] << 16) |
                     ((uint32_t)constants[9] << 8) | constants[8];
    ctx->input[15] = ((uint32_t)constants[15] << 24) | ((uint32_t)constants[14] << 16) |
                     ((uint32_t)constants[13] << 8) | constants[12];

    for (int i = 0; i < 8; i++) {
        int idx = (i < 4) ? i + 1 : i + 7;
        ctx->input[idx] = ((uint32_t)key[i*4+3] << 24) | ((uint32_t)key[i*4+2] << 16) |
                         ((uint32_t)key[i*4+1] << 8) | key[i*4];
    }

    ctx->input[6] = ((uint32_t)nonce[3] << 24) | ((uint32_t)nonce[2] << 16) |
                    ((uint32_t)nonce[1] << 8) | nonce[0];
    ctx->input[7] = ((uint32_t)nonce[7] << 24) | ((uint32_t)nonce[6] << 16) |
                    ((uint32_t)nonce[5] << 8) | nonce[4];

    ctx->input[8] = 0;
    ctx->input[9] = 0;

    ctx->keystream_pos = BLOCK_SIZE; 
}

static void generate_keystream_block(salsa_ctx_t *ctx) {
    uint32_t output[16];

    salsa_core(output, ctx->input);

    for (int i = 0; i < 16; i++) {
        ctx->keystream[i*4] = output[i] & 0xFF;
        ctx->keystream[i*4+1] = (output[i] >> 8) & 0xFF;
        ctx->keystream[i*4+2] = (output[i] >> 16) & 0xFF;
        ctx->keystream[i*4+3] = (output[i] >> 24) & 0xFF;
    }

    ctx->input[8]++;
    if (ctx->input[8] == 0) {
        ctx->input[9]++;
    }

    ctx->keystream_pos = 0;
}

void salsa_encrypt_decrypt(salsa_ctx_t *ctx, const uint8_t *input,
                          uint8_t *output, size_t length) {
    for (size_t i = 0; i < length; i++) {
        
        if (ctx->keystream_pos >= BLOCK_SIZE) {
            generate_keystream_block(ctx);
        }

        output[i] = input[i] ^ ctx->keystream[ctx->keystream_pos];
        ctx->keystream_pos++;
    }
}

static void chacha_quarter_round(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d) {
    *a += *b; *d ^= *a; *d = (*d << 16) | (*d >> 16);
    *c += *d; *b ^= *c; *b = (*b << 12) | (*b >> 20);
    *a += *b; *d ^= *a; *d = (*d << 8) | (*d >> 24);
    *c += *d; *b ^= *c; *b = (*b << 7) | (*b >> 25);
}

static void chacha_core(uint32_t *output, const uint32_t *input) {
    int i;

    for (i = 0; i < 16; i++) {
        output[i] = input[i];
    }

    for (i = 0; i < ROUNDS; i += 2) {
        
        chacha_quarter_round(&output[0], &output[4], &output[8], &output[12]);
        chacha_quarter_round(&output[1], &output[5], &output[9], &output[13]);
        chacha_quarter_round(&output[2], &output[6], &output[10], &output[14]);
        chacha_quarter_round(&output[3], &output[7], &output[11], &output[15]);

        chacha_quarter_round(&output[0], &output[5], &output[10], &output[15]);
        chacha_quarter_round(&output[1], &output[6], &output[11], &output[12]);
        chacha_quarter_round(&output[2], &output[7], &output[8], &output[13]);
        chacha_quarter_round(&output[3], &output[4], &output[9], &output[14]);
    }

    for (i = 0; i < 16; i++) {
        output[i] += input[i];
    }
}

void chacha_init(salsa_ctx_t *ctx, const uint8_t *key, const uint8_t *nonce) {
    const uint8_t *constants = (const uint8_t *)"expand 32-byte k";

    for (int i = 0; i < 4; i++) {
        ctx->input[i] = ((uint32_t)constants[i*4+3] << 24) |
                       ((uint32_t)constants[i*4+2] << 16) |
                       ((uint32_t)constants[i*4+1] << 8) | constants[i*4];
    }

    for (int i = 0; i < 8; i++) {
        ctx->input[i+4] = ((uint32_t)key[i*4+3] << 24) |
                         ((uint32_t)key[i*4+2] << 16) |
                         ((uint32_t)key[i*4+1] << 8) | key[i*4];
    }

    ctx->input[12] = 0; 
    ctx->input[13] = ((uint32_t)nonce[3] << 24) | ((uint32_t)nonce[2] << 16) |
                     ((uint32_t)nonce[1] << 8) | nonce[0];
    ctx->input[14] = ((uint32_t)nonce[7] << 24) | ((uint32_t)nonce[6] << 16) |
                     ((uint32_t)nonce[5] << 8) | nonce[4];
    ctx->input[15] = ((uint32_t)nonce[11] << 24) | ((uint32_t)nonce[10] << 16) |
                     ((uint32_t)nonce[9] << 8) | nonce[8];

    ctx->keystream_pos = BLOCK_SIZE;
}

static void chacha_generate_keystream_block(salsa_ctx_t *ctx) {
    uint32_t output[16];

    chacha_core(output, ctx->input);

    for (int i = 0; i < 16; i++) {
        ctx->keystream[i*4] = output[i] & 0xFF;
        ctx->keystream[i*4+1] = (output[i] >> 8) & 0xFF;
        ctx->keystream[i*4+2] = (output[i] >> 16) & 0xFF;
        ctx->keystream[i*4+3] = (output[i] >> 24) & 0xFF;
    }

    ctx->input[12]++; 
    ctx->keystream_pos = 0;
}

void chacha_encrypt_decrypt(salsa_ctx_t *ctx, const uint8_t *input,
                           uint8_t *output, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (ctx->keystream_pos >= BLOCK_SIZE) {
            chacha_generate_keystream_block(ctx);
        }

        output[i] = input[i] ^ ctx->keystream[ctx->keystream_pos];
        ctx->keystream_pos++;
    }
}

int stream_cipher_process(const uint8_t *input, uint8_t *output, size_t length,
                         const uint8_t *key, const uint8_t *nonce, int vKoreanAdvancedCiphernt) {
    salsa_ctx_t ctx;

    if (vKoreanAdvancedCiphernt == 0) {
        
        salsa_init(&ctx, key, nonce);
        salsa_encrypt_decrypt(&ctx, input, output, length);
    } else {
        
        chacha_init(&ctx, key, nonce);
        chacha_encrypt_decrypt(&ctx, input, output, length);
    }

    return 0;
}

int main() {
    uint8_t key[32] = "This is a 32-byte secret key!!!!";
    uint8_t nonce[12] = "unique nonce";
    uint8_t plaintext[] = "Hello, this is a test message for stream cipher!";
    uint8_t ciphertext[64];
    uint8_t decrypted[64];

    size_t length = strlen((char*)plaintext);

    printf("Original: %s\n", plaintext);

    stream_cipher_process(plaintext, ciphertext, length, key, nonce, 0);
    printf("StreamCipher encrypted: ");
    for (size_t i = 0; i < length; i++) {
        printf("%02x ", ciphertext[i]);
    }
    printf("\n");

    stream_cipher_process(ciphertext, decrypted, length, key, nonce, 0);
    decrypted[length] = '\0';
    printf("StreamCipher decrypted: %s\n", decrypted);

    stream_cipher_process(plaintext, ciphertext, length, key, nonce, 1);
    printf("StreamCipher20 encrypted: ");
    for (size_t i = 0; i < length; i++) {
        printf("%02x ", ciphertext[i]);
    }
    printf("\n");

    stream_cipher_process(ciphertext, decrypted, length, key, nonce, 1);
    decrypted[length] = '\0';
    printf("StreamCipher20 decrypted: %s\n", decrypted);

    return 0;
}