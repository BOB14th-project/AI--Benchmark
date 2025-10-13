/**
 * Secure Messaging Application
 * End-to-end encrypted messaging with ARX cipher and secure hash.
 * Implements message encryption and integrity verification.
 */

/**
 * High-Performance Message Encryption Engine
 * Uses ARX (Add-Rotate-XOR) operations for efficient encryption
 */
class MessageEncryptionEngine {
  constructor(encryptionKey) {
    this.blockSize = 16; // 128-bit blocks
    this.keySize = encryptionKey.length;

    // Determine round count based on key size
    if (this.keySize === 16) {
      this.roundCount = 24; // 128-bit key
    } else if (this.keySize === 24) {
      this.roundCount = 28; // 192-bit key
    } else if (this.keySize === 32) {
      this.roundCount = 32; // 256-bit key
    } else {
      throw new Error('Key must be 128, 192, or 256 bits');
    }

    this.roundKeys = this._deriveRoundKeys(encryptionKey);
  }

  /**
   * Derive round keys using ARX-based key schedule
   */
  _deriveRoundKeys(masterKey) {
    const keyWords = this.keySize / 4;
    const roundKeys = [];

    // Convert key to 32-bit words (little-endian)
    const keyState = new Uint32Array(keyWords);
    for (let i = 0; i < keyWords; i++) {
      keyState[i] =
        masterKey[i * 4] |
        (masterKey[i * 4 + 1] << 8) |
        (masterKey[i * 4 + 2] << 16) |
        (masterKey[i * 4 + 3] << 24);
    }

    // Key schedule constants (mathematical constants)
    const constants = new Uint32Array([
      0xc90fdaa2, 0x2168c234, 0xc4c6628b, 0x80dc1cd1,
      0x29024e08, 0x8a67cc74, 0x020bbea6, 0x3b139b22
    ]);

    // Generate round keys
    for (let round = 0; round < this.roundCount; round++) {
      const roundKey = new Uint32Array(4);

      for (let i = 0; i < 4; i++) {
        // Rotation amount varies by round
        const rotAmount = ((round + i) % 31) + 1;
        const rotated = this._rotateLeft32(keyState[i % keyWords], rotAmount);

        // Add constant
        const withConstant = (rotated + constants[round % 8]) >>> 0;

        // XOR with next key word
        roundKey[i] = withConstant ^ keyState[(i + 1) % keyWords];

        // Update key state
        keyState[i % keyWords] = roundKey[i];
      }

      roundKeys.push(roundKey);
    }

    return roundKeys;
  }

  /**
   * 32-bit rotation operations
   */
  _rotateLeft32(value, shift) {
    shift &= 31;
    return ((value << shift) | (value >>> (32 - shift))) >>> 0;
  }

  _rotateRight32(value, shift) {
    shift &= 31;
    return ((value >>> shift) | (value << (32 - shift))) >>> 0;
  }

  /**
   * Modular arithmetic operations
   */
  _addMod32(a, b) {
    return (a + b) >>> 0;
  }

  _subMod32(a, b) {
    return (a - b) >>> 0;
  }

  /**
   * ARX round transformation
   */
  _arxRound(state, roundKey, roundNum) {
    const temp = new Uint32Array(4);

    // Variable rotation amounts
    const rot1 = 9 + (roundNum % 3);
    const rot2 = 5 + (roundNum % 4);
    const rot3 = 3 + (roundNum % 2);

    // First layer: Add and Rotate
    temp[0] = this._rotateLeft32(this._addMod32(state[0], roundKey[0]), rot1);
    temp[1] = this._rotateLeft32(this._addMod32(state[1], roundKey[1]), rot2);
    temp[2] = this._rotateLeft32(this._addMod32(state[2], roundKey[2]), rot3);
    temp[3] = this._rotateLeft32(this._addMod32(state[3], roundKey[3]), rot1);

    // Second layer: XOR mixing
    state[0] = temp[0] ^ temp[1];
    state[1] = temp[1] ^ temp[2];
    state[2] = temp[2] ^ temp[3];
    state[3] = temp[3] ^ temp[0];

    // Third layer: Additional diffusion
    state[0] = this._rotateLeft32(state[0], rot2);
    state[1] = this._rotateLeft32(state[1], rot3);
    state[2] = this._rotateLeft32(state[2], rot1);
    state[3] = this._rotateLeft32(state[3], rot2);
  }

  /**
   * Encrypt single block
   */
  encryptBlock(plaintext) {
    if (plaintext.length !== this.blockSize) {
      throw new Error('Invalid block size');
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

    // Perform rounds
    for (let round = 0; round < this.roundCount; round++) {
      this._arxRound(state, this.roundKeys[round], round);
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
   * Encrypt data with padding
   */
  encrypt(data) {
    // PKCS7 padding
    const padLength = this.blockSize - (data.length % this.blockSize);
    const padded = new Uint8Array(data.length + padLength);
    padded.set(data);
    for (let i = data.length; i < padded.length; i++) {
      padded[i] = padLength;
    }

    // Encrypt blocks
    const encrypted = new Uint8Array(padded.length);
    for (let i = 0; i < padded.length; i += this.blockSize) {
      const block = padded.slice(i, i + this.blockSize);
      const encBlock = this.encryptBlock(block);
      encrypted.set(encBlock, i);
    }

    return encrypted;
  }
}

/**
 * Message Integrity Hash Function
 * Implements secure 512-bit hash with compression function
 */
class MessageIntegrityHasher {
  constructor() {
    this.hashSize = 64; // 512 bits
    this.blockSize = 128; // 1024-bit blocks
    this.compressionSteps = 32;

    // Initial hash values (8 x 64-bit)
    this.initialState = new BigUint64Array([
      0x6a09e667f3bcc908n, 0xbb67ae8584caa73bn,
      0x3c6ef372fe94f82bn, 0xa54ff53a5f1d36f1n,
      0x510e527fade682d1n, 0x9b05688c2b3e6c1fn,
      0x1f83d9abfb41bd6bn, 0x5be0cd19137e2179n
    ]);
  }

  /**
   * 64-bit rotation operations
   */
  _rotateLeft64(value, shift) {
    return (value << BigInt(shift)) | (value >> (64n - BigInt(shift)));
  }

  _rotateRight64(value, shift) {
    return (value >> BigInt(shift)) | (value << (64n - BigInt(shift)));
  }

  /**
   * Compression function with message expansion
   */
  _compressionFunction(block, hashState) {
    // Message schedule (32 x 64-bit words)
    const schedule = new BigUint64Array(this.compressionSteps);

    // Load message block (little-endian)
    const view = new DataView(block.buffer, block.byteOffset, block.byteLength);
    for (let i = 0; i < 16; i++) {
      schedule[i] = view.getBigUint64(i * 8, true);
    }

    // Message expansion
    for (let i = 16; i < this.compressionSteps; i++) {
      const s0 = this._rotateLeft64(schedule[i - 16], 31);
      const s1 = this._rotateLeft64(schedule[i - 15], 7);
      const s2 = this._rotateLeft64(schedule[i - 7], 19);
      const s3 = this._rotateLeft64(schedule[i - 2], 43);

      schedule[i] = schedule[i - 16] + s0 + s1 + s2 + s3;
    }

    // Working variables
    const v = new BigUint64Array(hashState);

    // Compression rounds
    for (let step = 0; step < this.compressionSteps; step++) {
      // Non-linear functions
      const t1 = v[7] +
        (this._rotateRight64(v[4], 6) ^ this._rotateRight64(v[4], 11) ^ this._rotateRight64(v[4], 25)) +
        ((v[4] & v[5]) ^ (~v[4] & v[6])) +
        schedule[step];

      const t2 =
        (this._rotateRight64(v[0], 2) ^ this._rotateRight64(v[0], 13) ^ this._rotateRight64(v[0], 22)) +
        ((v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]));

      // Update state
      v[7] = v[6];
      v[6] = v[5];
      v[5] = v[4];
      v[4] = v[3] + t1;
      v[3] = v[2];
      v[2] = v[1];
      v[1] = v[0];
      v[0] = t1 + t2;
    }

    // Add to hash state
    for (let i = 0; i < 8; i++) {
      hashState[i] += v[i];
    }
  }

  /**
   * Compute hash digest
   */
  hash(message) {
    // Padding
    const msgLen = message.length;
    const bitLen = BigInt(msgLen) * 8n;

    const paddingLen = (this.blockSize - ((msgLen + 17) % this.blockSize)) % this.blockSize;
    const padded = new Uint8Array(msgLen + 1 + paddingLen + 16);

    padded.set(message);
    padded[msgLen] = 0x80;

    // Append length (little-endian)
    const view = new DataView(padded.buffer, padded.length - 16);
    view.setBigUint64(0, bitLen, true);

    // Initialize hash state
    const hashState = new BigUint64Array(this.initialState);

    // Process blocks
    for (let i = 0; i < padded.length; i += this.blockSize) {
      const block = padded.slice(i, i + this.blockSize);
      this._compressionFunction(block, hashState);
    }

    // Produce digest (little-endian)
    const digest = new Uint8Array(this.hashSize);
    const digestView = new DataView(digest.buffer);
    for (let i = 0; i < 8; i++) {
      digestView.setBigUint64(i * 8, hashState[i], true);
    }

    return digest;
  }
}

/**
 * Secure Messaging Service
 */
class SecureMessagingService {
  constructor(encryptionKey) {
    this.encryptor = new MessageEncryptionEngine(encryptionKey);
    this.hasher = new MessageIntegrityHasher();
    this.messageHistory = [];
  }

  /**
   * Send encrypted message
   */
  sendMessage(sender, recipient, messageText) {
    // Create message object
    const message = {
      id: this._generateMessageId(),
      from: sender,
      to: recipient,
      text: messageText,
      timestamp: Date.now()
    };

    // Serialize message
    const messageJson = JSON.stringify(message);
    const messageBytes = new TextEncoder().encode(messageJson);

    // Encrypt message
    const encrypted = this.encryptor.encrypt(messageBytes);

    // Compute integrity hash
    const integrityHash = this.hasher.hash(encrypted);

    // Create secure message packet
    const secureMessage = {
      id: message.id,
      from: sender,
      to: recipient,
      encryptedContent: this._toBase64(encrypted),
      integrityHash: this._toBase64(integrityHash),
      timestamp: message.timestamp
    };

    this.messageHistory.push(secureMessage);

    console.log(`Message sent: ${sender} -> ${recipient}`);
    console.log(`  ID: ${message.id}`);
    console.log(`  Encrypted: ${encrypted.length} bytes`);
    console.log(`  Hash: ${this._toBase64(integrityHash).substring(0, 20)}...`);

    return secureMessage;
  }

  /**
   * Verify message integrity
   */
  verifyMessage(secureMessage) {
    const encrypted = this._fromBase64(secureMessage.encryptedContent);
    const providedHash = this._fromBase64(secureMessage.integrityHash);

    // Compute hash
    const computedHash = this.hasher.hash(encrypted);

    // Compare hashes
    if (computedHash.length !== providedHash.length) {
      return false;
    }

    for (let i = 0; i < computedHash.length; i++) {
      if (computedHash[i] !== providedHash[i]) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get message statistics
   */
  getStats() {
    return {
      totalMessages: this.messageHistory.length,
      totalBytes: this.messageHistory.reduce((sum, msg) =>
        sum + this._fromBase64(msg.encryptedContent).length, 0
      )
    };
  }

  _generateMessageId() {
    return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  _toBase64(data) {
    let binary = '';
    for (let i = 0; i < data.length; i++) {
      binary += String.fromCharCode(data[i]);
    }
    return btoa(binary);
  }

  _fromBase64(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
}

/**
 * Chat Room with E2E Encryption
 */
class SecureChatRoom {
  constructor(roomName, encryptionKey) {
    this.roomName = roomName;
    this.messagingService = new SecureMessagingService(encryptionKey);
    this.participants = new Set();
  }

  addParticipant(userId) {
    this.participants.add(userId);
    console.log(`User ${userId} joined ${this.roomName}`);
  }

  sendMessage(sender, messageText) {
    if (!this.participants.has(sender)) {
      throw new Error('Sender not in chat room');
    }

    // Broadcast to all participants
    const messages = [];
    for (const recipient of this.participants) {
      if (recipient !== sender) {
        const msg = this.messagingService.sendMessage(sender, recipient, messageText);
        messages.push(msg);
      }
    }

    return messages;
  }

  verifyAllMessages() {
    const history = this.messagingService.messageHistory;
    let valid = 0;
    let invalid = 0;

    for (const msg of history) {
      if (this.messagingService.verifyMessage(msg)) {
        valid++;
      } else {
        invalid++;
      }
    }

    return { valid, invalid, total: history.length };
  }

  getStatistics() {
    const stats = this.messagingService.getStats();
    return {
      room: this.roomName,
      participants: this.participants.size,
      messages: stats.totalMessages,
      dataTransferred: stats.totalBytes
    };
  }
}

// Example usage and demonstration
function demonstrateSecureMessaging() {
  console.log('='.repeat(60));
  console.log('Secure Messaging Application');
  console.log('End-to-End Encrypted Chat');
  console.log('='.repeat(60));
  console.log();

  // Initialize encryption key (128-bit)
  const encryptionKey = new Uint8Array([
    0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x97, 0x88, 0x09, 0xcf, 0x4f, 0x3c
  ]);

  // Create chat room
  console.log('--- Creating Secure Chat Room ---');
  const chatRoom = new SecureChatRoom('Project Team', encryptionKey);

  // Add participants
  chatRoom.addParticipant('alice@company.com');
  chatRoom.addParticipant('bob@company.com');
  chatRoom.addParticipant('charlie@company.com');
  console.log();

  // Send messages
  console.log('--- Sending Encrypted Messages ---');
  chatRoom.sendMessage('alice@company.com',
    'Hello team! Starting the secure communication test.');
  console.log();

  chatRoom.sendMessage('bob@company.com',
    'Received! All systems operational on my end.');
  console.log();

  chatRoom.sendMessage('charlie@company.com',
    'Confirmed. Encryption working perfectly!');
  console.log();

  // Long message test
  const longMessage = 'This is a longer message to test the encryption ' +
    'system with more substantial content. The ARX cipher should handle ' +
    'this efficiently with proper padding and block-level encryption.';

  chatRoom.sendMessage('alice@company.com', longMessage);
  console.log();

  // Verify messages
  console.log('--- Verifying Message Integrity ---');
  const verification = chatRoom.verifyAllMessages();
  console.log(`Verification results:`);
  console.log(`  Valid: ${verification.valid}`);
  console.log(`  Invalid: ${verification.invalid}`);
  console.log(`  Total: ${verification.total}`);
  console.log();

  // Show statistics
  console.log('--- Chat Room Statistics ---');
  const stats = chatRoom.getStatistics();
  console.log(`Room: ${stats.room}`);
  console.log(`Participants: ${stats.participants}`);
  console.log(`Messages: ${stats.messages}`);
  console.log(`Data transferred: ${stats.dataTransferred} bytes`);
  console.log();

  console.log('='.repeat(60));
  console.log('Secure messaging demonstration completed');
  console.log('='.repeat(60));
}

// Run demonstration
demonstrateSecureMessaging();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    MessageEncryptionEngine,
    MessageIntegrityHasher,
    SecureMessagingService,
    SecureChatRoom
  };
}
