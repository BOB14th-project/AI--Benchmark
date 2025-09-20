#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROUNDS 32
#define BLOCK_SIZE 16
#define KEY_SIZE 32

typedef struct {
    uint32_t subkeys[ROUNDS + 1][4];
} serpent_ctx_t;

static const uint8_t sbox[8][16] = {
    {3, 8, 15, 1, 10, 6, 5, 11, 14, 13, 4, 2, 7, 0, 9, 12},
    {15, 12, 2, 7, 9, 0, 5, 10, 1, 11, 14, 8, 6, 13, 3, 4},
    {8, 6, 7, 14, 3, 11, 0, 4, 10, 13, 2, 12, 9, 5, 15, 1},
    {0, 15, 11, 8, 12, 9, 6, 3, 13, 1, 2, 4, 10, 7, 5, 14},
    {1, 15, 8, 3, 12, 0, 11, 6, 2, 5, 4, 10, 9, 14, 7, 13},
    {15, 5, 2, 11, 4, 10, 9, 12, 0, 3, 14, 8, 13, 6, 7, 1},
    {7, 2, 12, 5, 8, 4, 6, 11, 14, 9, 1, 15, 13, 3, 10, 0},
    {1, 13, 15, 0, 14, 8, 2, 11, 7, 4, 12, 10, 9, 3, 5, 6}
};

static const uint8_t inv_sbox[8][16] = {
    {13, 3, 11, 0, 10, 6, 5, 12, 1, 14, 4, 7, 15, 9, 8, 2},
    {5, 8, 2, 14, 15, 6, 12, 3, 11, 4, 7, 9, 1, 13, 10, 0},
    {12, 9, 15, 4, 11, 14, 1, 2, 0, 3, 6, 13, 5, 8, 10, 7},
    {0, 9, 10, 7, 11, 14, 6, 13, 3, 5, 12, 2, 4, 8, 15, 1},
    {5, 0, 8, 3, 10, 9, 7, 14, 2, 12, 11, 6, 4, 15, 13, 1},
    {8, 15, 2, 9, 4, 1, 13, 14, 11, 6, 5, 3, 7, 12, 10, 0},
    {15, 10, 1, 13, 5, 3, 6, 0, 4, 9, 14, 7, 2, 12, 8, 11},
    {3, 0, 6, 13, 9, 14, 15, 8, 5, 12, 11, 7, 10, 1, 4, 2}
};

static const int bit_permutation[128] = {
    0, 32, 64, 96, 1, 33, 65, 97, 2, 34, 66, 98, 3, 35, 67, 99,
    4, 36, 68, 100, 5, 37, 69, 101, 6, 38, 70, 102, 7, 39, 71, 103,
    8, 40, 72, 104, 9, 41, 73, 105, 10, 42, 74, 106, 11, 43, 75, 107,
    12, 44, 76, 108, 13, 45, 77, 109, 14, 46, 78, 110, 15, 47, 79, 111,
    16, 48, 80, 112, 17, 49, 81, 113, 18, 50, 82, 114, 19, 51, 83, 115,
    20, 52, 84, 116, 21, 53, 85, 117, 22, 54, 86, 118, 23, 55, 87, 119,
    24, 56, 88, 120, 25, 57, 89, 121, 26, 58, 90, 122, 27, 59, 91, 123,
    28, 60, 92, 124, 29, 61, 93, 125, 30, 62, 94, 126, 31, 63, 95, 127
};

static void apply_sbox(uint32_t *state, int sbox_num) {
    for (int i = 0; i < 4; i++) {
        uint32_t word = state[i];
        uint32_t result = 0;

        for (int j = 0; j < 8; j++) {
            uint8_t nibble = (word >> (j * 4)) & 0xF;
            uint8_t substituted = sbox[sbox_num][nibble];
            result |= ((uint32_t)substituted << (j * 4));
        }

        state[i] = result;
    }
}

static void apply_inverse_sbox(uint32_t *state, int sbox_num) {
    for (int i = 0; i < 4; i++) {
        uint32_t word = state[i];
        uint32_t result = 0;

        for (int j = 0; j < 8; j++) {
            uint8_t nibble = (word >> (j * 4)) & 0xF;
            uint8_t substituted = inv_sbox[sbox_num][nibble];
            result |= ((uint32_t)substituted << (j * 4));
        }

        state[i] = result;
    }
}

static void linear_transform(uint32_t *state) {
    uint32_t input[4];
    uint32_t output[4] = {0};

    memcpy(input, state, 16);

    for (int i = 0; i < 128; i++) {
        int input_bit = i;
        int output_bit = bit_permutation[i];

        int input_word = input_bit / 32;
        int input_pos = input_bit % 32;
        int output_word = output_bit / 32;
        int output_pos = output_bit % 32;

        if (input[input_word] & (1U << input_pos)) {
            output[output_word] |= (1U << output_pos);
        }
    }

    memcpy(state, output, 16);
}

static void inverse_linear_transform(uint32_t *state) {
    uint32_t input[4];
    uint32_t output[4] = {0};

    memcpy(input, state, 16);

    for (int i = 0; i < 128; i++) {
        int output_bit = i;
        int input_bit = bit_permutation[i];

        int input_word = input_bit / 32;
        int input_pos = input_bit % 32;
        int output_word = output_bit / 32;
        int output_pos = output_bit % 32;

        if (input[input_word] & (1U << input_pos)) {
            output[output_word] |= (1U << output_pos);
        }
    }

    memcpy(state, output, 16);
}

void serpent_key_schedule(serpent_ctx_t *ctx, const uint8_t *key) {
    uint32_t w[140]; 

    for (int i = 0; i < 8; i++) {
        w[i] = (key[i*4+3] << 24) | (key[i*4+2] << 16) |
               (key[i*4+1] << 8) | key[i*4];
    }

    for (int i = 8; i < 140; i++) {
        uint32_t temp = w[i-8] ^ w[i-5] ^ w[i-3] ^ w[i-1] ^ 0x9E3779B9 ^ (i-8);
        w[i] = (temp << 11) | (temp >> 21); 
    }

    for (int round = 0; round <= ROUNDS; round++) {
        uint32_t temp[4];
        temp[0] = w[round * 4 + 8];
        temp[1] = w[round * 4 + 9];
        temp[2] = w[round * 4 + 10];
        temp[3] = w[round * 4 + 11];

        apply_sbox(temp, (ROUNDS + 3 - round) % 8);

        ctx->subkeys[round][0] = temp[0];
        ctx->subkeys[round][1] = temp[1];
        ctx->subkeys[round][2] = temp[2];
        ctx->subkeys[round][3] = temp[3];
    }
}

void serpent_encrypt_block(serpent_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32_t state[4];

    for (int i = 0; i < 4; i++) {
        state[i] = (input[i*4+3] << 24) | (input[i*4+2] << 16) |
                   (input[i*4+1] << 8) | input[i*4];
    }

    for (int i = 0; i < 4; i++) {
        state[i] ^= ctx->subkeys[0][i];
    }

    for (int round = 0; round < ROUNDS; round++) {
        
        apply_sbox(state, round % 8);

        for (int i = 0; i < 4; i++) {
            state[i] ^= ctx->subkeys[round + 1][i];
        }

        if (round < ROUNDS - 1) {
            linear_transform(state);
        }
    }

    for (int i = 0; i < 4; i++) {
        output[i*4] = state[i] & 0xFF;
        output[i*4+1] = (state[i] >> 8) & 0xFF;
        output[i*4+2] = (state[i] >> 16) & 0xFF;
        output[i*4+3] = (state[i] >> 24) & 0xFF;
    }
}

void serpent_decrypt_block(serpent_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32_t state[4];

    for (int i = 0; i < 4; i++) {
        state[i] = (input[i*4+3] << 24) | (input[i*4+2] << 16) |
                   (input[i*4+1] << 8) | input[i*4];
    }

    for (int round = ROUNDS - 1; round >= 0; round--) {
        
        if (round < ROUNDS - 1) {
            inverse_linear_transform(state);
        }

        for (int i = 0; i < 4; i++) {
            state[i] ^= ctx->subkeys[round + 1][i];
        }

        apply_inverse_sbox(state, round % 8);
    }

    for (int i = 0; i < 4; i++) {
        state[i] ^= ctx->subkeys[0][i];
    }

    for (int i = 0; i < 4; i++) {
        output[i*4] = state[i] & 0xFF;
        output[i*4+1] = (state[i] >> 8) & 0xFF;
        output[i*4+2] = (state[i] >> 16) & 0xFF;
        output[i*4+3] = (state[i] >> 24) & 0xFF;
    }
}

int substitution_network_process(const uint8_t *input, uint8_t *output,
                                size_t length, const uint8_t *key, int encrypt) {
    if (length % BLOCK_SIZE != 0) {
        return -1;
    }

    serpent_ctx_t ctx;
    serpent_key_schedule(&ctx, key);

    size_t blocks = length / BLOCK_SIZE;
    for (size_t i = 0; i < blocks; i++) {
        if (encrypt) {
            serpent_encrypt_block(&ctx, input + i * BLOCK_SIZE,
                                output + i * BLOCK_SIZE);
        } else {
            serpent_decrypt_block(&ctx, input + i * BLOCK_SIZE,
                                output + i * BLOCK_SIZE);
        }
    }

    return 0;
}

int main() {
    uint8_t key[32] = "This is a 256-bit secret key!!!!";
    uint8_t plaintext[32] = "Test data for substitution net!!";
    uint8_t ciphertext[32];
    uint8_t decrypted[32];

    printf("Original: %.*s\n", 32, plaintext);

    if (substitution_network_process(plaintext, ciphertext, 32, key, 1) == 0) {
        printf("Encrypted: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\n");

        if (substitution_network_process(ciphertext, decrypted, 32, key, 0) == 0) {
            printf("Decrypted: %.*s\n", 32, decrypted);
        }
    }

    return 0;
}