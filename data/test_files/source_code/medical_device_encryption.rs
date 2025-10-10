// Medical Device Encryption Module
// Secure data processing for healthcare IoT devices with regulatory compliance

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

const MEDICAL_BLOCK_SIZE: usize = 16;
const PATIENT_KEY_SIZE: usize = 32;
const DEVICE_ID_LENGTH: usize = 12;
const DIGEST_OUTPUT_SIZE: usize = 20;
const STREAM_STATE_SIZE: usize = 16;

#[derive(Clone)]
pub struct MedicalSecurityModule {
    device_registry: Arc<Mutex<HashMap<String, DeviceContext>>>,
    encryption_engine: SymmetricEncryptionEngine,
    hash_processor: MedicalHashProcessor,
    stream_cipher: CompactStreamCipher,
    key_derivation: KeyDerivationFunction,
}

#[derive(Clone)]
struct DeviceContext {
    device_id: String,
    patient_key: [u8; PATIENT_KEY_SIZE],
    session_state: [u8; MEDICAL_BLOCK_SIZE],
    last_heartbeat: u64,
    encryption_counter: u64,
}

struct SymmetricEncryptionEngine {
    round_keys: [[u32; 4]; 15],
    substitution_table: [u8; 256],
    mix_columns_matrix: [[u8; 4]; 4],
}

struct MedicalHashProcessor {
    state: [u32; 5],
    buffer: [u8; 64],
    message_length: u64,
    buffer_position: usize,
}

struct CompactStreamCipher {
    internal_state: [u32; STREAM_STATE_SIZE],
    keystream_buffer: [u8; 64],
    buffer_position: usize,
    initialization_vector: [u8; 8],
}

struct KeyDerivationFunction {
    salt: [u8; 16],
    iteration_count: u32,
}

impl MedicalSecurityModule {
    pub fn new() -> Self {
        let mut module = MedicalSecurityModule {
            device_registry: Arc::new(Mutex::new(HashMap::new())),
            encryption_engine: SymmetricEncryptionEngine::new(),
            hash_processor: MedicalHashProcessor::new(),
            stream_cipher: CompactStreamCipher::new(),
            key_derivation: KeyDerivationFunction::new(),
        };

        module.initialize_security_parameters();
        module
    }

    fn initialize_security_parameters(&mut self) {
        // Initialize with medical-grade entropy
        let entropy_seed = self.generate_medical_entropy();
        self.encryption_engine.setup_key_schedule(&entropy_seed);
        self.key_derivation.initialize_salt();
    }

    fn generate_medical_entropy(&self) -> [u8; 32] {
        // Generate entropy based on system time and device characteristics
        let mut entropy = [0u8; 32];
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64;

        // Mix timestamp with device-specific constants
        for i in 0..4 {
            let word = timestamp.rotate_left(i * 8) ^ 0x428A2F98E23D6C85u64;
            let bytes = word.to_be_bytes();
            entropy[i * 8..(i + 1) * 8].copy_from_slice(&bytes);
        }

        entropy
    }

    pub fn register_medical_device(
        &mut self,
        device_id: &str,
        patient_identifier: &str,
    ) -> Result<[u8; PATIENT_KEY_SIZE], &'static str> {
        if device_id.len() != DEVICE_ID_LENGTH {
            return Err("Invalid device ID length");
        }

        // Derive patient-specific encryption key
        let patient_key = self.key_derivation.derive_patient_key(
            device_id.as_bytes(),
            patient_identifier.as_bytes(),
        );

        // Initialize device context
        let device_context = DeviceContext {
            device_id: device_id.to_string(),
            patient_key,
            session_state: [0u8; MEDICAL_BLOCK_SIZE],
            last_heartbeat: self.get_current_timestamp(),
            encryption_counter: 0,
        };

        // Store in registry
        let mut registry = self.device_registry.lock().unwrap();
        registry.insert(device_id.to_string(), device_context);

        Ok(patient_key)
    }

    pub fn encrypt_patient_data(
        &mut self,
        device_id: &str,
        medical_data: &[u8],
    ) -> Result<Vec<u8>, &'static str> {
        let mut registry = self.device_registry.lock().unwrap();
        let device_context = registry
            .get_mut(device_id)
            .ok_or("Device not registered")?;

        // Setup encryption with patient key
        self.encryption_engine.set_patient_key(&device_context.patient_key);

        // Generate unique IV based on device state and counter
        let iv = self.generate_device_iv(device_context);

        // Encrypt using hybrid approach
        let encrypted_data = if medical_data.len() <= MEDICAL_BLOCK_SIZE {
            // Small data: use block cipher
            self.encrypt_with_block_cipher(medical_data, &iv)
        } else {
            // Large data: use stream cipher
            self.encrypt_with_stream_cipher(medical_data, &device_context.patient_key, &iv)
        };

        // Update device state
        device_context.encryption_counter += 1;
        device_context.last_heartbeat = self.get_current_timestamp();
        device_context.session_state = iv;

        Ok(encrypted_data)
    }

    fn generate_device_iv(&self, device_context: &DeviceContext) -> [u8; MEDICAL_BLOCK_SIZE] {
        let mut iv = [0u8; MEDICAL_BLOCK_SIZE];

        // Combine device ID, counter, and timestamp
        let timestamp = self.get_current_timestamp();
        let counter = device_context.encryption_counter;

        for i in 0..DEVICE_ID_LENGTH {
            iv[i] = device_context.device_id.as_bytes()[i];
        }

        let counter_bytes = counter.to_be_bytes();
        iv[12..].copy_from_slice(&counter_bytes[4..]);

        // Mix with timestamp
        for i in 0..8 {
            iv[i] ^= ((timestamp >> (i * 8)) & 0xFF) as u8;
        }

        iv
    }

    fn encrypt_with_block_cipher(&mut self, data: &[u8], iv: &[u8]) -> Vec<u8> {
        let mut padded_data = data.to_vec();

        // Apply medical padding scheme
        let padding_needed = MEDICAL_BLOCK_SIZE - (data.len() % MEDICAL_BLOCK_SIZE);
        if padding_needed != MEDICAL_BLOCK_SIZE {
            padded_data.extend(vec![padding_needed as u8; padding_needed]);
        }

        let mut result = Vec::new();
        result.extend_from_slice(iv); // Prepend IV

        let mut previous_block = iv.to_vec();

        for chunk in padded_data.chunks(MEDICAL_BLOCK_SIZE) {
            let mut block = [0u8; MEDICAL_BLOCK_SIZE];
            block[..chunk.len()].copy_from_slice(chunk);

            // CBC mode: XOR with previous ciphertext
            for i in 0..MEDICAL_BLOCK_SIZE {
                block[i] ^= previous_block[i];
            }

            let encrypted_block = self.encryption_engine.encrypt_block(&block);
            result.extend_from_slice(&encrypted_block);
            previous_block = encrypted_block.to_vec();
        }

        result
    }

    fn encrypt_with_stream_cipher(
        &mut self,
        data: &[u8],
        key: &[u8],
        nonce: &[u8],
    ) -> Vec<u8> {
        self.stream_cipher.initialize(key, &nonce[..8]);

        let mut result = Vec::new();
        result.extend_from_slice(&nonce[..8]); // Prepend nonce

        for byte in data {
            let keystream_byte = self.stream_cipher.next_byte();
            result.push(byte ^ keystream_byte);
        }

        result
    }

    pub fn compute_medical_hash(&mut self, data: &[u8]) -> [u8; DIGEST_OUTPUT_SIZE] {
        self.hash_processor.reset();
        self.hash_processor.update(data);
        self.hash_processor.finalize()
    }

    fn get_current_timestamp(&self) -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
    }
}

impl SymmetricEncryptionEngine {
    fn new() -> Self {
        let mut engine = SymmetricEncryptionEngine {
            round_keys: [[0u32; 4]; 15],
            substitution_table: [0u8; 256],
            mix_columns_matrix: [[0u8; 4]; 4],
        };

        engine.initialize_substitution_table();
        engine.initialize_mix_columns();
        engine
    }

    fn initialize_substitution_table(&mut self) {
        // Generate S-box using mathematical transformation
        for i in 0..256 {
            let mut value = i as u8;

            // Nonlinear transformation
            value = value.wrapping_mul(17);
            value ^= value >> 4;
            value ^= 0x63;

            // Additional mixing
            value = ((value << 1) | (value >> 7)) ^ ((value << 3) | (value >> 5));

            self.substitution_table[i] = value;
        }
    }

    fn initialize_mix_columns(&mut self) {
        // Initialize mixing matrix for diffusion
        self.mix_columns_matrix = [
            [2, 3, 1, 1],
            [1, 2, 3, 1],
            [1, 1, 2, 3],
            [3, 1, 1, 2],
        ];
    }

    fn setup_key_schedule(&mut self, master_key: &[u8]) {
        // Convert master key to words
        let mut key_words = [0u32; 8];
        for i in 0..8 {
            if i * 4 + 3 < master_key.len() {
                key_words[i] = u32::from_be_bytes([
                    master_key[i * 4],
                    master_key[i * 4 + 1],
                    master_key[i * 4 + 2],
                    master_key[i * 4 + 3],
                ]);
            }
        }

        // Generate round keys
        for round in 0..15 {
            for i in 0..4 {
                if round == 0 {
                    self.round_keys[round][i] = key_words[i];
                } else {
                    let mut temp = self.round_keys[round - 1][3];

                    if i == 0 {
                        // Apply transformation for first word
                        temp = self.substitute_word(temp.rotate_left(8));
                        temp ^= self.round_constant(round);
                    }

                    self.round_keys[round][i] = self.round_keys[round - 1][i] ^ temp;
                }
            }
        }
    }

    fn set_patient_key(&mut self, patient_key: &[u8]) {
        self.setup_key_schedule(patient_key);
    }

    fn substitute_word(&self, word: u32) -> u32 {
        let bytes = word.to_be_bytes();
        let substituted = [
            self.substitution_table[bytes[0] as usize],
            self.substitution_table[bytes[1] as usize],
            self.substitution_table[bytes[2] as usize],
            self.substitution_table[bytes[3] as usize],
        ];
        u32::from_be_bytes(substituted)
    }

    fn round_constant(&self, round: usize) -> u32 {
        let rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36];
        (rcon[round % rcon.len()] as u32) << 24
    }

    fn encrypt_block(&self, plaintext: &[u8]) -> [u8; MEDICAL_BLOCK_SIZE] {
        let mut state = [[0u8; 4]; 4];

        // Load plaintext into state
        for i in 0..4 {
            for j in 0..4 {
                state[i][j] = plaintext[i * 4 + j];
            }
        }

        // Initial round key addition
        self.add_round_key(&mut state, 0);

        // Main rounds
        for round in 1..14 {
            self.substitute_bytes(&mut state);
            self.shift_rows(&mut state);
            self.mix_columns(&mut state);
            self.add_round_key(&mut state, round);
        }

        // Final round
        self.substitute_bytes(&mut state);
        self.shift_rows(&mut state);
        self.add_round_key(&mut state, 14);

        // Convert state to output
        let mut ciphertext = [0u8; MEDICAL_BLOCK_SIZE];
        for i in 0..4 {
            for j in 0..4 {
                ciphertext[i * 4 + j] = state[i][j];
            }
        }

        ciphertext
    }

    fn substitute_bytes(&self, state: &mut [[u8; 4]; 4]) {
        for i in 0..4 {
            for j in 0..4 {
                state[i][j] = self.substitution_table[state[i][j] as usize];
            }
        }
    }

    fn shift_rows(&self, state: &mut [[u8; 4]; 4]) {
        // Row 1: shift left by 1
        let temp = state[1][0];
        state[1][0] = state[1][1];
        state[1][1] = state[1][2];
        state[1][2] = state[1][3];
        state[1][3] = temp;

        // Row 2: shift left by 2
        let temp = [state[2][0], state[2][1]];
        state[2][0] = state[2][2];
        state[2][1] = state[2][3];
        state[2][2] = temp[0];
        state[2][3] = temp[1];

        // Row 3: shift left by 3 (or right by 1)
        let temp = state[3][3];
        state[3][3] = state[3][2];
        state[3][2] = state[3][1];
        state[3][1] = state[3][0];
        state[3][0] = temp;
    }

    fn mix_columns(&self, state: &mut [[u8; 4]; 4]) {
        for col in 0..4 {
            let column = [state[0][col], state[1][col], state[2][col], state[3][col]];

            for row in 0..4 {
                let mut result = 0u8;
                for i in 0..4 {
                    result ^= self.galois_multiply(self.mix_columns_matrix[row][i], column[i]);
                }
                state[row][col] = result;
            }
        }
    }

    fn galois_multiply(&self, a: u8, b: u8) -> u8 {
        let mut result = 0u8;
        let mut a = a;
        let mut b = b;

        for _ in 0..8 {
            if b & 1 != 0 {
                result ^= a;
            }
            let carry = a & 0x80;
            a <<= 1;
            if carry != 0 {
                a ^= 0x1B; // BlockCipher irreducible polynomial
            }
            b >>= 1;
        }

        result
    }

    fn add_round_key(&self, state: &mut [[u8; 4]; 4], round: usize) {
        for i in 0..4 {
            let key_word = self.round_keys[round][i];
            let key_bytes = key_word.to_be_bytes();
            for j in 0..4 {
                state[i][j] ^= key_bytes[j];
            }
        }
    }
}

impl MedicalHashProcessor {
    fn new() -> Self {
        MedicalHashProcessor {
            state: [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0],
            buffer: [0u8; 64],
            message_length: 0,
            buffer_position: 0,
        }
    }

    fn reset(&mut self) {
        self.state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0];
        self.buffer = [0u8; 64];
        self.message_length = 0;
        self.buffer_position = 0;
    }

    fn update(&mut self, data: &[u8]) {
        self.message_length += data.len() as u64;

        for &byte in data {
            self.buffer[self.buffer_position] = byte;
            self.buffer_position += 1;

            if self.buffer_position == 64 {
                self.process_block();
                self.buffer_position = 0;
            }
        }
    }

    fn finalize(&mut self) -> [u8; DIGEST_OUTPUT_SIZE] {
        // Append padding
        self.buffer[self.buffer_position] = 0x80;
        self.buffer_position += 1;

        if self.buffer_position > 56 {
            while self.buffer_position < 64 {
                self.buffer[self.buffer_position] = 0;
                self.buffer_position += 1;
            }
            self.process_block();
            self.buffer_position = 0;
        }

        while self.buffer_position < 56 {
            self.buffer[self.buffer_position] = 0;
            self.buffer_position += 1;
        }

        // Append length
        let bit_length = self.message_length * 8;
        let length_bytes = bit_length.to_be_bytes();
        self.buffer[56..64].copy_from_slice(&length_bytes);

        self.process_block();

        // Extract digest
        let mut digest = [0u8; DIGEST_OUTPUT_SIZE];
        for i in 0..5 {
            let bytes = self.state[i].to_be_bytes();
            digest[i * 4..(i + 1) * 4].copy_from_slice(&bytes);
        }

        digest
    }

    fn process_block(&mut self) {
        let mut w = [0u32; 80];

        // Load buffer into first 16 words
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                self.buffer[i * 4],
                self.buffer[i * 4 + 1],
                self.buffer[i * 4 + 2],
                self.buffer[i * 4 + 3],
            ]);
        }

        // Extend to 80 words
        for i in 16..80 {
            w[i] = (w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]).rotate_left(1);
        }

        // Initialize working variables
        let [mut a, mut b, mut c, mut d, mut e] = self.state;

        // Main loop
        for i in 0..80 {
            let (f, k) = match i {
                0..=19 => ((b & c) | (!b & d), 0x5A827999),
                20..=39 => (b ^ c ^ d, 0x6ED9EBA1),
                40..=59 => ((b & c) | (b & d) | (c & d), 0x8F1BBCDC),
                60..=79 => (b ^ c ^ d, 0xCA62C1D6),
                _ => unreachable!(),
            };

            let temp = a.rotate_left(5)
                .wrapping_add(f)
                .wrapping_add(e)
                .wrapping_add(k)
                .wrapping_add(w[i]);

            e = d;
            d = c;
            c = b.rotate_left(30);
            b = a;
            a = temp;
        }

        // Add to state
        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
        self.state[4] = self.state[4].wrapping_add(e);
    }
}

impl CompactStreamCipher {
    fn new() -> Self {
        CompactStreamCipher {
            internal_state: [0u32; STREAM_STATE_SIZE],
            keystream_buffer: [0u8; 64],
            buffer_position: 64, // Force initial generation
            initialization_vector: [0u8; 8],
        }
    }

    fn initialize(&mut self, key: &[u8], iv: &[u8]) {
        // Initialize state with constants
        self.internal_state[0] = 0x61707865; // "expa"
        self.internal_state[1] = 0x3320646e; // "nd 3"
        self.internal_state[2] = 0x79622d32; // "2-by"
        self.internal_state[3] = 0x6b206574; // "te k"

        // Set key (32 bytes -> 8 words)
        for i in 0..8 {
            if i * 4 + 3 < key.len() {
                self.internal_state[4 + i] = u32::from_le_bytes([
                    key[i * 4],
                    key[i * 4 + 1],
                    key[i * 4 + 2],
                    key[i * 4 + 3],
                ]);
            }
        }

        // Set counter
        self.internal_state[12] = 0;
        self.internal_state[13] = 0;

        // Set IV
        if iv.len() >= 8 {
            self.initialization_vector.copy_from_slice(iv);
            self.internal_state[14] = u32::from_le_bytes([iv[0], iv[1], iv[2], iv[3]]);
            self.internal_state[15] = u32::from_le_bytes([iv[4], iv[5], iv[6], iv[7]]);
        }

        self.buffer_position = 64;
    }

    fn next_byte(&mut self) -> u8 {
        if self.buffer_position >= 64 {
            self.generate_keystream_block();
        }

        let byte = self.keystream_buffer[self.buffer_position];
        self.buffer_position += 1;
        byte
    }

    fn generate_keystream_block(&mut self) {
        let mut working_state = self.internal_state;

        // Perform 20 rounds (10 double rounds)
        for _ in 0..10 {
            // Column rounds
            Self::quarter_round(&mut working_state, 0, 4, 8, 12);
            Self::quarter_round(&mut working_state, 1, 5, 9, 13);
            Self::quarter_round(&mut working_state, 2, 6, 10, 14);
            Self::quarter_round(&mut working_state, 3, 7, 11, 15);

            // Diagonal rounds
            Self::quarter_round(&mut working_state, 0, 5, 10, 15);
            Self::quarter_round(&mut working_state, 1, 6, 11, 12);
            Self::quarter_round(&mut working_state, 2, 7, 8, 13);
            Self::quarter_round(&mut working_state, 3, 4, 9, 14);
        }

        // Add original state and convert to bytes
        for i in 0..16 {
            let sum = working_state[i].wrapping_add(self.internal_state[i]);
            let bytes = sum.to_le_bytes();
            self.keystream_buffer[i * 4..(i + 1) * 4].copy_from_slice(&bytes);
        }

        // Increment counter
        self.internal_state[12] = self.internal_state[12].wrapping_add(1);
        if self.internal_state[12] == 0 {
            self.internal_state[13] = self.internal_state[13].wrapping_add(1);
        }

        self.buffer_position = 0;
    }

    fn quarter_round(state: &mut [u32], a: usize, b: usize, c: usize, d: usize) {
        state[a] = state[a].wrapping_add(state[b]);
        state[d] ^= state[a];
        state[d] = state[d].rotate_left(16);

        state[c] = state[c].wrapping_add(state[d]);
        state[b] ^= state[c];
        state[b] = state[b].rotate_left(12);

        state[a] = state[a].wrapping_add(state[b]);
        state[d] ^= state[a];
        state[d] = state[d].rotate_left(8);

        state[c] = state[c].wrapping_add(state[d]);
        state[b] ^= state[c];
        state[b] = state[b].rotate_left(7);
    }
}

impl KeyDerivationFunction {
    fn new() -> Self {
        KeyDerivationFunction {
            salt: [0u8; 16],
            iteration_count: 1000,
        }
    }

    fn initialize_salt(&mut self) {
        // Generate deterministic salt for medical device consistency
        let base_salt = b"MedicalDeviceSalt";
        self.salt[..base_salt.len()].copy_from_slice(base_salt);
    }

    fn derive_patient_key(&self, device_id: &[u8], patient_id: &[u8]) -> [u8; PATIENT_KEY_SIZE] {
        let mut key = [0u8; PATIENT_KEY_SIZE];
        let mut hash_processor = MedicalHashProcessor::new();

        // Initial input: salt + device_id + patient_id
        let mut input = Vec::new();
        input.extend_from_slice(&self.salt);
        input.extend_from_slice(device_id);
        input.extend_from_slice(patient_id);

        // Iterative hashing for key strengthening
        for _ in 0..self.iteration_count {
            hash_processor.reset();
            hash_processor.update(&input);
            let digest = hash_processor.finalize();
            input = digest.to_vec();
        }

        // Extend to full key size if necessary
        if input.len() >= PATIENT_KEY_SIZE {
            key.copy_from_slice(&input[..PATIENT_KEY_SIZE]);
        } else {
            // Use additional rounds to generate more key material
            key[..input.len()].copy_from_slice(&input);
            for i in (input.len()..PATIENT_KEY_SIZE).step_by(DIGEST_OUTPUT_SIZE) {
                hash_processor.reset();
                hash_processor.update(&input);
                hash_processor.update(&[i as u8]);
                let additional_digest = hash_processor.finalize();
                let copy_len = std::cmp::min(additional_digest.len(), PATIENT_KEY_SIZE - i);
                key[i..i + copy_len].copy_from_slice(&additional_digest[..copy_len]);
            }
        }

        key
    }
}

fn main() {
    println!("Medical Device Encryption Module Starting...");

    let mut security_module = MedicalSecurityModule::new();

    // Register medical device
    let device_id = "MED_DEV_001";
    let patient_id = "PATIENT_12345";

    match security_module.register_medical_device(device_id, patient_id) {
        Ok(patient_key) => {
            println!("Medical device {} registered successfully", device_id);
            println!("Patient key generated: {} bytes", patient_key.len());

            // Test patient data encryption
            let medical_data = b"Blood pressure: 120/80 mmHg, Heart rate: 72 bpm, Temperature: 98.6F";

            match security_module.encrypt_patient_data(device_id, medical_data) {
                Ok(encrypted_data) => {
                    println!("Medical data encrypted successfully");
                    println!("Original size: {} bytes", medical_data.len());
                    println!("Encrypted size: {} bytes", encrypted_data.len());

                    // Compute integrity hash
                    let data_hash = security_module.compute_medical_hash(medical_data);
                    println!("Data integrity hash computed: {} bytes", data_hash.len());
                }
                Err(e) => println!("Encryption failed: {}", e),
            }
        }
        Err(e) => println!("Device registration failed: {}", e),
    }

    println!("Medical device security module operational");
}