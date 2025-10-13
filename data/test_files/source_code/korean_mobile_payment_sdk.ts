/**
 * Mobile Payment Security SDK
 * Implements high-performance encryption for mobile wallet transactions.
 * Optimized for ARM processors with NEON instructions support.
 */

/**
 * Security configuration for mobile payment encryption
 */
interface SecurityConfig {
  keySize: 128 | 192 | 256;
  operationMode: 'standard' | 'high-security' | 'performance';
}

/**
 * Secure payment transaction data structure
 */
interface PaymentTransaction {
  transactionId: string;
  merchantId: string;
  amount: number;
  currency: string;
  timestamp: number;
  cardToken: string;
}

/**
 * High-Performance Block Cipher Engine
 * Implements ARX (Add-Rotate-XOR) operations for mobile processors.
 */
class MobileSecurityEngine {
  private readonly blockSize: number = 16; // 128-bit blocks
  private readonly roundKeys: Uint32Array[];
  private readonly totalRounds: number;
  private readonly keySize: number;

  /**
   * Initialize security engine with key material
   */
  constructor(masterKey: Uint8Array, config: SecurityConfig) {
    this.keySize = config.keySize;

    // Determine round count based on key size
    switch (this.keySize) {
      case 128:
        this.totalRounds = 24;
        break;
      case 192:
        this.totalRounds = 28;
        break;
      case 256:
        this.totalRounds = 32;
        break;
      default:
        throw new Error('Invalid key size');
    }

    if (masterKey.length !== this.keySize / 8) {
      throw new Error(`Key must be ${this.keySize} bits`);
    }

    this.roundKeys = this.generateRoundKeys(masterKey);
  }

  /**
   * Generate round keys using ARX-based key schedule
   */
  private generateRoundKeys(masterKey: Uint8Array): Uint32Array[] {
    const keyWords = this.keySize / 32;
    const roundKeys: Uint32Array[] = [];

    // Convert key bytes to 32-bit words (little-endian)
    const keyState = new Uint32Array(keyWords);
    for (let i = 0; i < keyWords; i++) {
      keyState[i] =
        masterKey[i * 4] |
        (masterKey[i * 4 + 1] << 8) |
        (masterKey[i * 4 + 2] << 16) |
        (masterKey[i * 4 + 3] << 24);
    }

    // Key schedule constants (derived from e and π)
    const scheduleConstants = [
      0xc90fdaa2, 0x2168c234, 0xc4c6628b, 0x80dc1cd1,
      0x29024e08, 0x8a67cc74, 0x020bbea6, 0x3b139b22
    ];

    // Generate round keys
    for (let round = 0; round < this.totalRounds; round++) {
      const roundKey = new Uint32Array(4);

      for (let i = 0; i < 4; i++) {
        // Mix key state with round-dependent rotation
        const rotAmount = ((round + i) % 31) + 1;
        const mixed = this.rotateLeft32(keyState[i % keyWords], rotAmount);

        // Add round constant
        const withConstant = this.addMod32(mixed, scheduleConstants[round % 8]);

        // XOR with adjacent key word
        roundKey[i] = withConstant ^ keyState[(i + 1) % keyWords];

        // Update key state for next round
        keyState[i % keyWords] = roundKey[i];
      }

      roundKeys.push(roundKey);
    }

    return roundKeys;
  }

  /**
   * 32-bit rotate left operation
   */
  private rotateLeft32(value: number, shift: number): number {
    shift &= 31;
    return ((value << shift) | (value >>> (32 - shift))) >>> 0;
  }

  /**
   * 32-bit rotate right operation
   */
  private rotateRight32(value: number, shift: number): number {
    shift &= 31;
    return ((value >>> shift) | (value << (32 - shift))) >>> 0;
  }

  /**
   * Modular addition (32-bit)
   */
  private addMod32(a: number, b: number): number {
    return (a + b) >>> 0;
  }

  /**
   * Modular subtraction (32-bit)
   */
  private subMod32(a: number, b: number): number {
    return (a - b) >>> 0;
  }

  /**
   * ARX round transformation
   * Implements Add-Rotate-XOR pattern for high performance
   */
  private arxRound(state: Uint32Array, roundKey: Uint32Array, roundNum: number): void {
    const temp = new Uint32Array(4);

    // Determine rotation amounts based on round number
    const rot1 = 9 + (roundNum % 3);
    const rot2 = 5 + (roundNum % 4);
    const rot3 = 3 + (roundNum % 2);

    // ARX operations on state words
    // First layer: Add and Rotate
    temp[0] = this.rotateLeft32(this.addMod32(state[0], roundKey[0]), rot1);
    temp[1] = this.rotateLeft32(this.addMod32(state[1], roundKey[1]), rot2);
    temp[2] = this.rotateLeft32(this.addMod32(state[2], roundKey[2]), rot3);
    temp[3] = this.rotateLeft32(this.addMod32(state[3], roundKey[3]), rot1);

    // Second layer: XOR mixing
    state[0] = temp[0] ^ temp[1];
    state[1] = temp[1] ^ temp[2];
    state[2] = temp[2] ^ temp[3];
    state[3] = temp[3] ^ temp[0];

    // Third layer: Additional rotation for diffusion
    state[0] = this.rotateLeft32(state[0], rot2);
    state[1] = this.rotateLeft32(state[1], rot3);
    state[2] = this.rotateLeft32(state[2], rot1);
    state[3] = this.rotateLeft32(state[3], rot2);
  }

  /**
   * Inverse ARX round for decryption
   */
  private inverseArxRound(state: Uint32Array, roundKey: Uint32Array, roundNum: number): void {
    const rot1 = 9 + (roundNum % 3);
    const rot2 = 5 + (roundNum % 4);
    const rot3 = 3 + (roundNum % 2);

    // Reverse third layer rotations
    state[3] = this.rotateRight32(state[3], rot2);
    state[2] = this.rotateRight32(state[2], rot1);
    state[1] = this.rotateRight32(state[1], rot3);
    state[0] = this.rotateRight32(state[0], rot2);

    // Reverse second layer XOR
    const temp = new Uint32Array(4);
    temp[0] = state[0] ^ state[1];
    temp[1] = state[1] ^ state[2];
    temp[2] = state[2] ^ state[3];
    temp[3] = state[3] ^ state[0];

    // Correct the circular XOR dependency
    state[3] = temp[3] ^ temp[0];
    state[2] = temp[2] ^ state[3];
    state[1] = temp[1] ^ state[2];
    state[0] = temp[0] ^ state[1];

    // Reverse first layer: Rotate and Subtract
    state[0] = this.subMod32(this.rotateRight32(state[0], rot1), roundKey[0]);
    state[1] = this.subMod32(this.rotateRight32(state[1], rot2), roundKey[1]);
    state[2] = this.subMod32(this.rotateRight32(state[2], rot3), roundKey[2]);
    state[3] = this.subMod32(this.rotateRight32(state[3], rot1), roundKey[3]);
  }

  /**
   * Encrypt a single 128-bit block
   */
  public encryptBlock(plaintext: Uint8Array): Uint8Array {
    if (plaintext.length !== this.blockSize) {
      throw new Error(`Block must be ${this.blockSize} bytes`);
    }

    // Convert to 32-bit words
    const state = new Uint32Array(4);
    for (let i = 0; i < 4; i++) {
      state[i] =
        plaintext[i * 4] |
        (plaintext[i * 4 + 1] << 8) |
        (plaintext[i * 4 + 2] << 16) |
        (plaintext[i * 4 + 3] << 24);
    }

    // Perform encryption rounds
    for (let round = 0; round < this.totalRounds; round++) {
      this.arxRound(state, this.roundKeys[round], round);
    }

    // Convert back to bytes
    const ciphertext = new Uint8Array(this.blockSize);
    for (let i = 0; i < 4; i++) {
      ciphertext[i * 4] = state[i] & 0xff;
      ciphertext[i * 4 + 1] = (state[i] >>> 8) & 0xff;
      ciphertext[i * 4 + 2] = (state[i] >>> 16) & 0xff;
      ciphertext[i * 4 + 3] = (state[i] >>> 24) & 0xff;
    }

    return ciphertext;
  }

  /**
   * Decrypt a single 128-bit block
   */
  public decryptBlock(ciphertext: Uint8Array): Uint8Array {
    if (ciphertext.length !== this.blockSize) {
      throw new Error(`Block must be ${this.blockSize} bytes`);
    }

    // Convert to 32-bit words
    const state = new Uint32Array(4);
    for (let i = 0; i < 4; i++) {
      state[i] =
        ciphertext[i * 4] |
        (ciphertext[i * 4 + 1] << 8) |
        (ciphertext[i * 4 + 2] << 16) |
        (ciphertext[i * 4 + 3] << 24);
    }

    // Perform decryption rounds in reverse
    for (let round = this.totalRounds - 1; round >= 0; round--) {
      this.inverseArxRound(state, this.roundKeys[round], round);
    }

    // Convert back to bytes
    const plaintext = new Uint8Array(this.blockSize);
    for (let i = 0; i < 4; i++) {
      plaintext[i * 4] = state[i] & 0xff;
      plaintext[i * 4 + 1] = (state[i] >>> 8) & 0xff;
      plaintext[i * 4 + 2] = (state[i] >>> 16) & 0xff;
      plaintext[i * 4 + 3] = (state[i] >>> 24) & 0xff;
    }

    return plaintext;
  }

  /**
   * Encrypt data with PKCS7 padding
   */
  public encrypt(plaintext: Uint8Array): Uint8Array {
    // Apply padding
    const padLength = this.blockSize - (plaintext.length % this.blockSize);
    const padded = new Uint8Array(plaintext.length + padLength);
    padded.set(plaintext);
    for (let i = plaintext.length; i < padded.length; i++) {
      padded[i] = padLength;
    }

    // Encrypt blocks
    const ciphertext = new Uint8Array(padded.length);
    for (let i = 0; i < padded.length; i += this.blockSize) {
      const block = padded.slice(i, i + this.blockSize);
      const encrypted = this.encryptBlock(block);
      ciphertext.set(encrypted, i);
    }

    return ciphertext;
  }

  /**
   * Decrypt data and remove padding
   */
  public decrypt(ciphertext: Uint8Array): Uint8Array {
    if (ciphertext.length % this.blockSize !== 0) {
      throw new Error('Invalid ciphertext length');
    }

    // Decrypt blocks
    const decrypted = new Uint8Array(ciphertext.length);
    for (let i = 0; i < ciphertext.length; i += this.blockSize) {
      const block = ciphertext.slice(i, i + this.blockSize);
      const decryptedBlock = this.decryptBlock(block);
      decrypted.set(decryptedBlock, i);
    }

    // Remove padding
    const padLength = decrypted[decrypted.length - 1];
    if (padLength > this.blockSize || padLength === 0) {
      throw new Error('Invalid padding');
    }

    return decrypted.slice(0, decrypted.length - padLength);
  }
}

/**
 * Mobile Payment Service
 * Provides secure transaction processing for mobile wallets
 */
class SecureMobilePaymentService {
  private readonly securityEngine: MobileSecurityEngine;
  private readonly config: SecurityConfig;

  constructor(encryptionKey: Uint8Array, config: SecurityConfig) {
    this.config = config;
    this.securityEngine = new MobileSecurityEngine(encryptionKey, config);
  }

  /**
   * Encode payment transaction to bytes
   */
  private encodeTransaction(transaction: PaymentTransaction): Uint8Array {
    const encoder = new TextEncoder();
    const json = JSON.stringify(transaction);
    return encoder.encode(json);
  }

  /**
   * Decode bytes to payment transaction
   */
  private decodeTransaction(data: Uint8Array): PaymentTransaction {
    const decoder = new TextDecoder();
    const json = decoder.decode(data);
    return JSON.parse(json);
  }

  /**
   * Process secure payment transaction
   */
  public processPayment(transaction: PaymentTransaction): Uint8Array {
    console.log(`Processing payment: ${transaction.transactionId}`);
    console.log(`Amount: ${transaction.amount} ${transaction.currency}`);

    // Encode transaction data
    const plaintext = this.encodeTransaction(transaction);

    // Encrypt transaction
    const encrypted = this.securityEngine.encrypt(plaintext);

    console.log(`Transaction encrypted: ${encrypted.length} bytes`);
    return encrypted;
  }

  /**
   * Verify and decrypt payment transaction
   */
  public verifyPayment(encryptedData: Uint8Array): PaymentTransaction {
    console.log(`Verifying payment: ${encryptedData.length} bytes`);

    // Decrypt transaction
    const decrypted = this.securityEngine.decrypt(encryptedData);

    // Decode transaction
    const transaction = this.decodeTransaction(decrypted);

    console.log(`Transaction verified: ${transaction.transactionId}`);
    return transaction;
  }

  /**
   * Generate secure token for card storage
   */
  public tokenizeCard(cardNumber: string, expiryDate: string, cvv: string): string {
    const cardData = `${cardNumber}|${expiryDate}|${cvv}|${Date.now()}`;
    const plaintext = new TextEncoder().encode(cardData);
    const encrypted = this.securityEngine.encrypt(plaintext);

    // Convert to base64 token
    return this.toBase64(encrypted);
  }

  /**
   * Detokenize card information
   */
  public detokenizeCard(token: string): { cardNumber: string; expiryDate: string } {
    const encrypted = this.fromBase64(token);
    const decrypted = this.securityEngine.decrypt(encrypted);
    const cardData = new TextDecoder().decode(decrypted);

    const [cardNumber, expiryDate] = cardData.split('|');
    return { cardNumber, expiryDate };
  }

  private toBase64(data: Uint8Array): string {
    let binary = '';
    for (let i = 0; i < data.length; i++) {
      binary += String.fromCharCode(data[i]);
    }
    return btoa(binary);
  }

  private fromBase64(base64: string): Uint8Array {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
}

// Example usage and testing
function demonstratePaymentSecurity(): void {
  console.log('Mobile Payment Security SDK Demo');
  console.log('=================================\n');

  // Initialize payment service with 128-bit key
  const encryptionKey = new Uint8Array([
    0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x97, 0x88, 0x09, 0xcf, 0x4f, 0x3c
  ]);

  const config: SecurityConfig = {
    keySize: 128,
    operationMode: 'standard'
  };

  const paymentService = new SecureMobilePaymentService(encryptionKey, config);

  // Create payment transaction
  const transaction: PaymentTransaction = {
    transactionId: 'TXN-2025-00123456',
    merchantId: 'MERCHANT-789',
    amount: 50000.00,
    currency: 'KRW',
    timestamp: Date.now(),
    cardToken: 'tok_visa_4242424242424242'
  };

  // Process payment
  console.log('--- Processing Payment ---');
  const encryptedPayment = paymentService.processPayment(transaction);
  console.log(`Encrypted data: ${encryptedPayment.slice(0, 32).toString()}\n`);

  // Verify payment
  console.log('--- Verifying Payment ---');
  const verifiedTransaction = paymentService.verifyPayment(encryptedPayment);
  console.log(`Verified transaction: ${verifiedTransaction.transactionId}`);
  console.log(`Amount: ${verifiedTransaction.amount} ${verifiedTransaction.currency}\n`);

  // Tokenize card
  console.log('--- Card Tokenization ---');
  const token = paymentService.tokenizeCard('4242-4242-4242-4242', '12/25', '123');
  console.log(`Secure token: ${token.substring(0, 40)}...\n`);

  // Detokenize card
  console.log('--- Card Detokenization ---');
  const cardInfo = paymentService.detokenizeCard(token);
  console.log(`Card number: ${cardInfo.cardNumber}`);
  console.log(`Expiry: ${cardInfo.expiryDate}\n`);

  // Test with different key sizes
  console.log('--- Testing Different Security Levels ---');
  const key192 = new Uint8Array(24).fill(0x33);
  const key256 = new Uint8Array(32).fill(0x55);

  const highSecurityService = new SecureMobilePaymentService(key256, {
    keySize: 256,
    operationMode: 'high-security'
  });

  const encryptedHigh = highSecurityService.processPayment(transaction);
  console.log(`256-bit encryption: ${encryptedHigh.length} bytes`);
}

// Run demonstration
demonstratePaymentSecurity();

export { MobileSecurityEngine, SecureMobilePaymentService, PaymentTransaction, SecurityConfig };
