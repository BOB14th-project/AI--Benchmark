/*
 * IoT Device Security Module
 * Lightweight security for resource-constrained devices
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define DEVICE_KEY_SIZE 16
#define ROUND_CONSTANT_COUNT 32
#define SUBSTITUTION_BOX_SIZE 16

typedef struct {
    uint16_t state_matrix[4][4];
    uint8_t device_key[DEVICE_KEY_SIZE];
    uint32_t round_constants[ROUND_CONSTANT_COUNT];
    uint8_t sub_box[SUBSTITUTION_BOX_SIZE];
} IoTSecurityContext;

// Lightweight substitution box for IoT
static const uint8_t iot_sbox[16] = {
    0x6, 0xB, 0x5, 0x4, 0x2, 0xE, 0x7, 0xA,
    0x9, 0xD, 0xF, 0xC, 0x3, 0x1, 0x0, 0x8
};

// Round constants for IoT cipher
static const uint32_t iot_round_constants[32] = {
    0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3E, 0x7D, 0xFB,
    0xF7, 0xEF, 0xDF, 0xBF, 0x7F, 0xFE, 0xFD, 0xFA,
    0xF5, 0xEB, 0xD7, 0xAF, 0x5F, 0xBE, 0x7C, 0xF8,
    0xF1, 0xE3, 0xC7, 0x8F, 0x1E, 0x3C, 0x78, 0xF0
};

// Initialize IoT security context
void init_iot_security(IoTSecurityContext *ctx, const uint8_t *master_key) {
    // Copy device key
    memcpy(ctx->device_key, master_key, DEVICE_KEY_SIZE);

    // Initialize substitution box
    memcpy(ctx->sub_box, iot_sbox, SUBSTITUTION_BOX_SIZE);

    // Set round constants
    memcpy(ctx->round_constants, iot_round_constants, sizeof(iot_round_constants));

    // Initialize state matrix
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ctx->state_matrix[i][j] = master_key[i*4 + j] | (master_key[i*4 + j + 1] << 8);
        }
    }
}

// Lightweight transformation function
uint16_t iot_transform(uint16_t input, uint8_t round_key) {
    uint8_t high = (input >> 8) & 0xFF;
    uint8_t low = input & 0xFF;

    // Apply S-box to both halves
    high = iot_sbox[high & 0x0F] | (iot_sbox[high >> 4] << 4);
    low = iot_sbox[low & 0x0F] | (iot_sbox[low >> 4] << 4);

    // Mix with round key
    high ^= round_key;
    low ^= (round_key >> 4);

    return (high << 8) | low;
}

// Process IoT data block (64-bit)
void process_iot_block(IoTSecurityContext *ctx, uint8_t *data) {
    uint16_t block[4];

    // Load 64-bit block
    for (int i = 0; i < 4; i++) {
        block[i] = data[i*2] | (data[i*2 + 1] << 8);
    }

    // 32 rounds of encryption
    for (int round = 0; round < 32; round++) {
        uint16_t temp[4];
        uint8_t round_key = ctx->device_key[round % DEVICE_KEY_SIZE];

        // Apply transformation to each 16-bit word
        for (int i = 0; i < 4; i++) {
            temp[i] = iot_transform(block[i], round_key);
        }

        // Linear layer (simplified)
        block[0] = temp[0] ^ temp[1];
        block[1] = temp[1] ^ temp[2];
        block[2] = temp[2] ^ temp[3];
        block[3] = temp[3] ^ temp[0];

        // Add round constant
        block[0] ^= ctx->round_constants[round];
    }

    // Store result back
    for (int i = 0; i < 4; i++) {
        data[i*2] = block[i] & 0xFF;
        data[i*2 + 1] = (block[i] >> 8) & 0xFF;
    }
}

// Secure key derivation for IoT
void derive_session_key(IoTSecurityContext *ctx, const char *device_id,
                       uint8_t *session_key) {
    uint8_t temp_block[8];

    // Prepare device ID block
    strncpy((char*)temp_block, device_id, 7);
    temp_block[7] = 0x80; // Padding

    // Process through cipher
    process_iot_block(ctx, temp_block);

    // Copy result to session key
    memcpy(session_key, temp_block, 8);

    // Second round for 16-byte key
    temp_block[0] ^= 0x01;
    process_iot_block(ctx, temp_block);
    memcpy(session_key + 8, temp_block, 8);
}

// Encrypt IoT sensor data
void encrypt_sensor_data(IoTSecurityContext *ctx, uint8_t *sensor_data, int length) {
    uint8_t keystream[8];
    uint8_t counter[8] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};

    for (int i = 0; i < length; i += 8) {
        // Generate keystream block
        memcpy(keystream, counter, 8);
        process_iot_block(ctx, keystream);

        // XOR with sensor data
        int block_size = (i + 8 <= length) ? 8 : (length - i);
        for (int j = 0; j < block_size; j++) {
            sensor_data[i + j] ^= keystream[j];
        }

        // Increment counter
        for (int k = 7; k >= 0; k--) {
            counter[k]++;
            if (counter[k] != 0) break;
        }
    }
}

// Main IoT security function
int secure_iot_communication(const char *device_id, uint8_t *sensor_reading) {
    IoTSecurityContext ctx;
    uint8_t master_key[16] = {
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
    };
    uint8_t session_key[16];

    init_iot_security(&ctx, master_key);
    derive_session_key(&ctx, device_id, session_key);

    // Encrypt sensor data
    int data_length = 32; // Assume 32 bytes of sensor data
    encrypt_sensor_data(&ctx, sensor_reading, data_length);

    printf("IoT device secured using lightweight Korean cipher\n");
    printf("64-bit block cipher with 32 rounds applied\n");

    return 1;
}