/**
 * IoT Device Secure Communication Firmware
 * Lightweight encryption module for resource-constrained smart home devices.
 * Optimized for 8-bit/16-bit microcontrollers with minimal RAM.
 */

#include <stdint.h>
#include <string.h>
#include <stdio.h>

// Lightweight encryption configuration
#define DATA_UNIT_SIZE 8      // 64-bit blocks
#define ITERATION_COUNT 32    // Number of transformation rounds
#define KEY_MATERIAL_SIZE 16  // 128-bit key
#define SUBKEY_COUNT 136      // Derived subkeys needed

// Delta constant for key schedule mixing
#define MIXING_CONSTANT 0x5A827999

/**
 * IoT Device Encryption Context
 * Manages encryption state for smart home communication
 */
typedef struct {
    uint8_t master_key[KEY_MATERIAL_SIZE];
    uint8_t round_subkeys[SUBKEY_COUNT];
    uint32_t device_id;
    uint8_t initialized;
} iot_security_context_t;

/**
 * Key schedule generation for lightweight cipher
 * Derives round subkeys from master key using linear feedback
 */
static void generate_key_schedule(iot_security_context_t *ctx) {
    uint8_t working_key[KEY_MATERIAL_SIZE];
    memcpy(working_key, ctx->master_key, KEY_MATERIAL_SIZE);

    // Generate subkeys for all rounds
    for (int round = 0; round < ITERATION_COUNT; round++) {
        // Each round needs 4 subkeys (2 for even, 2 for odd)
        for (int sub = 0; sub < 4; sub++) {
            int idx = round * 4 + sub;

            // Linear mixing with rotation
            uint8_t temp = working_key[0];
            for (int i = 0; i < KEY_MATERIAL_SIZE - 1; i++) {
                working_key[i] = working_key[i + 1];
            }
            working_key[KEY_MATERIAL_SIZE - 1] = temp;

            // XOR with round-dependent constant
            working_key[sub % KEY_MATERIAL_SIZE] ^= (MIXING_CONSTANT >> (sub * 8)) & 0xFF;
            working_key[(sub + 7) % KEY_MATERIAL_SIZE] ^= round;

            // Store derived subkey
            ctx->round_subkeys[idx] = working_key[sub * 2] ^ working_key[sub * 2 + 1];
        }
    }

    // Generate final transformation subkeys
    for (int i = 0; i < 8; i++) {
        ctx->round_subkeys[ITERATION_COUNT * 4 + i] =
            working_key[i] ^ working_key[KEY_MATERIAL_SIZE - 1 - i];
    }
}

/**
 * Rotation operation optimized for 8-bit microcontrollers
 */
static inline uint8_t rotate_left_8(uint8_t value, int shift) {
    shift &= 7;
    return (value << shift) | (value >> (8 - shift));
}

static inline uint8_t rotate_right_8(uint8_t value, int shift) {
    shift &= 7;
    return (value >> shift) | (value << (8 - shift));
}

/**
 * Core round transformation function
 * Implements generalized Feistel structure with byte-level operations
 */
static void perform_round_transformation(uint8_t *data_block,
                                         uint8_t *subkeys,
                                         int round_num) {
    uint8_t temp[DATA_UNIT_SIZE];
    memcpy(temp, data_block, DATA_UNIT_SIZE);

    if (round_num % 2 == 0) {
        // Even round: Process bytes 0-3
        // F0 function with rotation and XOR
        temp[0] = rotate_left_8(temp[0] ^ subkeys[0], 1) + temp[1];
        temp[1] = rotate_left_8(temp[1] ^ subkeys[1], 3) ^ temp[2];
        temp[2] = rotate_left_8(temp[2] + subkeys[2], 4) ^ temp[3];
        temp[3] = rotate_left_8(temp[3] ^ subkeys[3], 5) + temp[0];

    } else {
        // Odd round: Process bytes 4-7
        // F1 function with different rotation pattern
        temp[4] = rotate_left_8(temp[4] + subkeys[0], 2) ^ temp[5];
        temp[5] = rotate_left_8(temp[5] ^ subkeys[1], 4) + temp[6];
        temp[6] = rotate_left_8(temp[6] + subkeys[2], 5) ^ temp[7];
        temp[7] = rotate_left_8(temp[7] ^ subkeys[3], 6) + temp[4];
    }

    memcpy(data_block, temp, DATA_UNIT_SIZE);
}

/**
 * Inverse round transformation for decryption
 */
static void perform_inverse_round_transformation(uint8_t *data_block,
                                                 uint8_t *subkeys,
                                                 int round_num) {
    uint8_t temp[DATA_UNIT_SIZE];
    memcpy(temp, data_block, DATA_UNIT_SIZE);

    if (round_num % 2 == 0) {
        // Reverse even round operations
        temp[3] = rotate_right_8(temp[3] - temp[0], 5) ^ subkeys[3];
        temp[2] = rotate_right_8(temp[2] ^ temp[3], 4) - subkeys[2];
        temp[1] = rotate_right_8(temp[1] ^ temp[2], 3) ^ subkeys[1];
        temp[0] = rotate_right_8(temp[0] - temp[1], 1) ^ subkeys[0];

    } else {
        // Reverse odd round operations
        temp[7] = rotate_right_8(temp[7] - temp[4], 6) ^ subkeys[3];
        temp[6] = rotate_right_8(temp[6] ^ temp[7], 5) - subkeys[2];
        temp[5] = rotate_right_8(temp[5] - temp[6], 4) ^ subkeys[1];
        temp[4] = rotate_right_8(temp[4] ^ temp[5], 2) - subkeys[0];
    }

    memcpy(data_block, temp, DATA_UNIT_SIZE);
}

/**
 * Initialize IoT device security context
 */
int iot_security_init(iot_security_context_t *ctx,
                      const uint8_t *key,
                      uint32_t device_id) {
    if (!ctx || !key) {
        return -1;
    }

    memcpy(ctx->master_key, key, KEY_MATERIAL_SIZE);
    ctx->device_id = device_id;

    // Generate all round subkeys
    generate_key_schedule(ctx);

    ctx->initialized = 1;
    return 0;
}

/**
 * Encrypt single 64-bit data block
 * Main encryption routine for IoT device communication
 */
int iot_encrypt_block(iot_security_context_t *ctx,
                      const uint8_t *plaintext,
                      uint8_t *ciphertext) {
    if (!ctx || !ctx->initialized || !plaintext || !ciphertext) {
        return -1;
    }

    // Copy input to output buffer
    memcpy(ciphertext, plaintext, DATA_UNIT_SIZE);

    // Initial whitening with first subkeys
    for (int i = 0; i < DATA_UNIT_SIZE; i++) {
        ciphertext[i] ^= ctx->round_subkeys[i];
    }

    // Main transformation rounds
    for (int round = 0; round < ITERATION_COUNT; round++) {
        uint8_t *round_keys = &ctx->round_subkeys[8 + round * 4];
        perform_round_transformation(ciphertext, round_keys, round);
    }

    // Final whitening
    for (int i = 0; i < DATA_UNIT_SIZE; i++) {
        ciphertext[i] ^= ctx->round_subkeys[ITERATION_COUNT * 4 + i];
    }

    return 0;
}

/**
 * Decrypt single 64-bit data block
 */
int iot_decrypt_block(iot_security_context_t *ctx,
                      const uint8_t *ciphertext,
                      uint8_t *plaintext) {
    if (!ctx || !ctx->initialized || !ciphertext || !plaintext) {
        return -1;
    }

    // Copy input to output buffer
    memcpy(plaintext, ciphertext, DATA_UNIT_SIZE);

    // Reverse final whitening
    for (int i = 0; i < DATA_UNIT_SIZE; i++) {
        plaintext[i] ^= ctx->round_subkeys[ITERATION_COUNT * 4 + i];
    }

    // Reverse main rounds
    for (int round = ITERATION_COUNT - 1; round >= 0; round--) {
        uint8_t *round_keys = &ctx->round_subkeys[8 + round * 4];
        perform_inverse_round_transformation(plaintext, round_keys, round);
    }

    // Reverse initial whitening
    for (int i = 0; i < DATA_UNIT_SIZE; i++) {
        plaintext[i] ^= ctx->round_subkeys[i];
    }

    return 0;
}

/**
 * Encrypt message with padding for IoT communication
 */
int iot_encrypt_message(iot_security_context_t *ctx,
                        const uint8_t *message,
                        size_t msg_len,
                        uint8_t *output,
                        size_t *output_len) {
    if (!ctx || !message || !output || !output_len) {
        return -1;
    }

    // Calculate padded length
    size_t pad_len = DATA_UNIT_SIZE - (msg_len % DATA_UNIT_SIZE);
    size_t total_len = msg_len + pad_len;

    if (*output_len < total_len) {
        return -2; // Buffer too small
    }

    // Copy message and add padding
    memcpy(output, message, msg_len);
    for (size_t i = msg_len; i < total_len; i++) {
        output[i] = (uint8_t)pad_len;
    }

    // Encrypt each block
    for (size_t i = 0; i < total_len; i += DATA_UNIT_SIZE) {
        uint8_t temp[DATA_UNIT_SIZE];
        memcpy(temp, output + i, DATA_UNIT_SIZE);

        if (iot_encrypt_block(ctx, temp, output + i) != 0) {
            return -3;
        }
    }

    *output_len = total_len;
    return 0;
}

/**
 * Decrypt message and remove padding
 */
int iot_decrypt_message(iot_security_context_t *ctx,
                        const uint8_t *ciphertext,
                        size_t cipher_len,
                        uint8_t *output,
                        size_t *output_len) {
    if (!ctx || !ciphertext || !output || !output_len) {
        return -1;
    }

    if (cipher_len % DATA_UNIT_SIZE != 0) {
        return -2; // Invalid ciphertext length
    }

    // Decrypt each block
    for (size_t i = 0; i < cipher_len; i += DATA_UNIT_SIZE) {
        if (iot_decrypt_block(ctx, ciphertext + i, output + i) != 0) {
            return -3;
        }
    }

    // Remove padding
    uint8_t pad_len = output[cipher_len - 1];
    if (pad_len > DATA_UNIT_SIZE || pad_len == 0) {
        return -4; // Invalid padding
    }

    *output_len = cipher_len - pad_len;
    return 0;
}

/**
 * Smart home device communication example
 */
typedef struct {
    uint32_t device_id;
    uint32_t timestamp;
    uint16_t temperature;  // x10 for precision
    uint16_t humidity;     // x10 for precision
    uint8_t status;
    uint8_t battery_level;
} smart_device_status_t;

/**
 * Secure smart home device status transmission
 */
int transmit_device_status(iot_security_context_t *ctx,
                          const smart_device_status_t *status,
                          uint8_t *secure_packet,
                          size_t *packet_len) {
    // Serialize device status
    uint8_t raw_data[14];
    memcpy(raw_data, &status->device_id, 4);
    memcpy(raw_data + 4, &status->timestamp, 4);
    memcpy(raw_data + 8, &status->temperature, 2);
    memcpy(raw_data + 10, &status->humidity, 2);
    raw_data[12] = status->status;
    raw_data[13] = status->battery_level;

    // Encrypt the status packet
    return iot_encrypt_message(ctx, raw_data, sizeof(raw_data),
                              secure_packet, packet_len);
}

// Example usage and testing
int main(void) {
    printf("IoT Device Security Firmware - Smart Home Communication\n");
    printf("=======================================================\n\n");

    // Initialize security context for smart thermostat
    iot_security_context_t device_ctx;
    uint8_t device_key[KEY_MATERIAL_SIZE] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x97, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };

    if (iot_security_init(&device_ctx, device_key, 0x12345678) != 0) {
        printf("Failed to initialize security context\n");
        return 1;
    }

    // Create device status
    smart_device_status_t status = {
        .device_id = 0x12345678,
        .timestamp = 1640000000,
        .temperature = 235,  // 23.5°C
        .humidity = 650,     // 65.0%
        .status = 0x01,      // Online
        .battery_level = 85  // 85%
    };

    // Encrypt status packet
    uint8_t encrypted[32];
    size_t encrypted_len = sizeof(encrypted);

    if (transmit_device_status(&device_ctx, &status, encrypted, &encrypted_len) != 0) {
        printf("Failed to encrypt device status\n");
        return 1;
    }

    printf("Device ID: 0x%08X\n", status.device_id);
    printf("Temperature: %.1f°C\n", status.temperature / 10.0);
    printf("Humidity: %.1f%%\n", status.humidity / 10.0);
    printf("Battery: %d%%\n", status.battery_level);
    printf("\nEncrypted packet (%zu bytes): ", encrypted_len);
    for (size_t i = 0; i < encrypted_len; i++) {
        printf("%02X ", encrypted[i]);
    }
    printf("\n\n");

    // Decrypt for verification
    uint8_t decrypted[32];
    size_t decrypted_len = sizeof(decrypted);

    if (iot_decrypt_message(&device_ctx, encrypted, encrypted_len,
                           decrypted, &decrypted_len) != 0) {
        printf("Failed to decrypt device status\n");
        return 1;
    }

    printf("Decryption successful - %zu bytes recovered\n", decrypted_len);

    // Test single block encryption
    uint8_t test_block[DATA_UNIT_SIZE] = {
        0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77
    };
    uint8_t cipher_block[DATA_UNIT_SIZE];
    uint8_t plain_block[DATA_UNIT_SIZE];

    iot_encrypt_block(&device_ctx, test_block, cipher_block);
    iot_decrypt_block(&device_ctx, cipher_block, plain_block);

    printf("\nBlock cipher test:\n");
    printf("Original:  ");
    for (int i = 0; i < DATA_UNIT_SIZE; i++) printf("%02X ", test_block[i]);
    printf("\nEncrypted: ");
    for (int i = 0; i < DATA_UNIT_SIZE; i++) printf("%02X ", cipher_block[i]);
    printf("\nDecrypted: ");
    for (int i = 0; i < DATA_UNIT_SIZE; i++) printf("%02X ", plain_block[i]);
    printf("\n");

    // Verify correctness
    if (memcmp(test_block, plain_block, DATA_UNIT_SIZE) == 0) {
        printf("\nVerification: PASSED\n");
    } else {
        printf("\nVerification: FAILED\n");
    }

    return 0;
}
