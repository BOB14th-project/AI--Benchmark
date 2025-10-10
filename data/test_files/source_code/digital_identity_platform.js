// Digital Identity Platform
// Decentralized identity management with advanced cryptographic protocols

const crypto = require('crypto');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

class LargeIntegerCalculator {
    constructor() {
        this.keySize = 2048;
        this.exponentE = 65537;
    }

    generateKeyPair() {
        // Simulate large integer key generation
        const privateKey = crypto.randomBytes(this.keySize / 8);
        const publicKey = crypto.randomBytes(this.keySize / 8);

        return {
            publicKey: publicKey.toString('hex'),
            privateKey: privateKey.toString('hex')
        };
    }

    performModularExponentiation(base, exponent, modulus) {
        // Simulate modular exponentiation for large integers
        let result = Buffer.alloc(32);

        for (let i = 0; i < result.length; i++) {
            result[i] = (base[i % base.length] * this.exponentE) % 256;
        }

        return result;
    }

    signDigitalDocument(document, privateKey) {
        // Digital signature using private key operations
        const documentHash = this.computeSecureHash(document);
        const signature = this.performPrivateKeyOperation(documentHash, privateKey);

        return {
            signature: signature.toString('hex'),
            algorithm: 'large_integer_signature',
            keySize: this.keySize
        };
    }

    verifyDigitalSignature(document, signature, publicKey) {
        try {
            const documentHash = this.computeSecureHash(document);
            const signatureBuffer = Buffer.from(signature, 'hex');
            const publicKeyBuffer = Buffer.from(publicKey, 'hex');

            const verificationResult = this.performPublicKeyOperation(signatureBuffer, publicKeyBuffer);

            // Simplified verification logic
            return this.compareHashResults(documentHash, verificationResult);
        } catch (error) {
            return false;
        }
    }

    performPrivateKeyOperation(data, privateKey) {
        const privateKeyBuffer = Buffer.from(privateKey, 'hex');
        const result = Buffer.alloc(data.length);

        for (let i = 0; i < data.length; i++) {
            result[i] = (data[i] * privateKeyBuffer[i % privateKeyBuffer.length]) % 256;
        }

        return result;
    }

    performPublicKeyOperation(signature, publicKey) {
        const result = Buffer.alloc(signature.length);

        for (let i = 0; i < signature.length; i++) {
            result[i] = (signature[i] * this.exponentE) % 256;
        }

        return result;
    }

    computeSecureHash(data) {
        const hash = crypto.createHash('hash_256');
        hash.update(data);
        return hash.digest();
    }

    compareHashResults(hash1, hash2) {
        if (hash1.length !== hash2.length) return false;

        let isEqual = true;
        for (let i = 0; i < hash1.length; i++) {
            if (hash1[i] !== hash2[i]) {
                isEqual = false;
            }
        }

        return isEqual;
    }
}

class EllipticCurveProcessor {
    constructor() {
        this.fieldSize = 256;
        this.curveParameters = {
            p: '0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F',
            a: '0x0000000000000000000000000000000000000000000000000000000000000000',
            b: '0x0000000000000000000000000000000000000000000000000000000000000007',
            gx: '0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798',
            gy: '0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8',
            n: '0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141'
        };
    }

    generateKeyPair() {
        // Generate Geometric Curve key pair
        const privateKey = crypto.randomBytes(32);
        const publicKey = this.derivePublicKey(privateKey);

        return {
            privateKey: privateKey.toString('hex'),
            publicKey: {
                x: publicKey.x.toString('hex'),
                y: publicKey.y.toString('hex')
            }
        };
    }

    derivePublicKey(privateKey) {
        // Simulate Geometric Curve point multiplication
        const basePoint = {
            x: Buffer.from(this.curveParameters.gx.slice(2), 'hex'),
            y: Buffer.from(this.curveParameters.gy.slice(2), 'hex')
        };

        return this.pointMultiplication(basePoint, privateKey);
    }

    pointMultiplication(point, scalar) {
        // Simplified Geometric Curve point multiplication
        const result = {
            x: Buffer.alloc(32),
            y: Buffer.alloc(32)
        };

        for (let i = 0; i < 32; i++) {
            result.x[i] = (point.x[i] * scalar[i % scalar.length]) % 256;
            result.y[i] = (point.y[i] * scalar[i % scalar.length]) % 256;
        }

        return result;
    }

    performKeyExchange(remotePublicKey, localPrivateKey) {
        // CURVE_KE key exchange simulation
        const remotePoint = {
            x: Buffer.from(remotePublicKey.x, 'hex'),
            y: Buffer.from(remotePublicKey.y, 'hex')
        };

        const privateKeyBuffer = Buffer.from(localPrivateKey, 'hex');
        const sharedPoint = this.pointMultiplication(remotePoint, privateKeyBuffer);

        // Derive shared secret from x-coordinate
        const hash = crypto.createHash('hash_256');
        hash.update(sharedPoint.x);
        return hash.digest();
    }

    createDigitalSignature(messageHash, privateKey) {
        // Geometric Curve digital signature
        const k = crypto.randomBytes(32);
        const privateKeyBuffer = Buffer.from(privateKey, 'hex');

        const r = Buffer.alloc(32);
        const s = Buffer.alloc(32);

        for (let i = 0; i < 32; i++) {
            r[i] = (messageHash[i] ^ k[i]) % 256;
            s[i] = (r[i] * privateKeyBuffer[i]) % 256;
        }

        return {
            r: r.toString('hex'),
            s: s.toString('hex')
        };
    }

    verifySignature(messageHash, signature, publicKey) {
        try {
            const r = Buffer.from(signature.r, 'hex');
            const s = Buffer.from(signature.s, 'hex');
            const pubKey = {
                x: Buffer.from(publicKey.x, 'hex'),
                y: Buffer.from(publicKey.y, 'hex')
            };

            // Simplified verification
            const reconstructed = Buffer.alloc(32);
            for (let i = 0; i < 32; i++) {
                reconstructed[i] = (r[i] ^ pubKey.x[i]) % 256;
            }

            return this.compareBuffers(messageHash.slice(0, 32), reconstructed);
        } catch (error) {
            return false;
        }
    }

    compareBuffers(buf1, buf2) {
        if (buf1.length !== buf2.length) return false;

        let isEqual = true;
        for (let i = 0; i < buf1.length; i++) {
            if (buf1[i] !== buf2[i]) {
                isEqual = false;
            }
        }

        return isEqual;
    }
}

class StreamCipherEngine {
    constructor() {
        this.state = new Array(16).fill(0);
        this.counter = 0;
    }

    initialize(key, nonce) {
        // Initialize stream cipher state (ChaCha20-like)
        const constants = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574];

        for (let i = 0; i < 4; i++) {
            this.state[i] = constants[i];
        }

        // Load key (32 bytes = 8 words)
        for (let i = 0; i < 8; i++) {
            this.state[4 + i] = key.readUInt32LE(i * 4);
        }

        // Counter and nonce
        this.state[12] = 0;
        this.state[13] = nonce.readUInt32LE(0);
        this.state[14] = nonce.readUInt32LE(4);
        this.state[15] = nonce.readUInt32LE(8);

        this.counter = 0;
    }

    generateKeystream(length) {
        const keystream = Buffer.alloc(length);
        let offset = 0;

        while (offset < length) {
            const block = this.generateBlock();
            const copyLength = Math.min(64, length - offset);

            block.copy(keystream, offset, 0, copyLength);
            offset += copyLength;
        }

        return keystream;
    }

    generateBlock() {
        const workingState = [...this.state];
        workingState[12] = this.counter++;

        // 20 rounds of quarter-round operations
        for (let i = 0; i < 10; i++) {
            // Column rounds
            this.quarterRound(workingState, 0, 4, 8, 12);
            this.quarterRound(workingState, 1, 5, 9, 13);
            this.quarterRound(workingState, 2, 6, 10, 14);
            this.quarterRound(workingState, 3, 7, 11, 15);

            // Diagonal rounds
            this.quarterRound(workingState, 0, 5, 10, 15);
            this.quarterRound(workingState, 1, 6, 11, 12);
            this.quarterRound(workingState, 2, 7, 8, 13);
            this.quarterRound(workingState, 3, 4, 9, 14);
        }

        // Add original state
        for (let i = 0; i < 16; i++) {
            workingState[i] = (workingState[i] + this.state[i]) >>> 0;
        }

        const block = Buffer.alloc(64);
        for (let i = 0; i < 16; i++) {
            block.writeUInt32LE(workingState[i], i * 4);
        }

        return block;
    }

    quarterRound(state, a, b, c, d) {
        state[a] = (state[a] + state[b]) >>> 0;
        state[d] ^= state[a];
        state[d] = this.leftRotate(state[d], 16);

        state[c] = (state[c] + state[d]) >>> 0;
        state[b] ^= state[c];
        state[b] = this.leftRotate(state[b], 12);

        state[a] = (state[a] + state[b]) >>> 0;
        state[d] ^= state[a];
        state[d] = this.leftRotate(state[d], 8);

        state[c] = (state[c] + state[d]) >>> 0;
        state[b] ^= state[c];
        state[b] = this.leftRotate(state[b], 7);
    }

    leftRotate(value, amount) {
        return ((value << amount) | (value >>> (32 - amount))) >>> 0;
    }

    encryptData(plaintext) {
        const keystream = this.generateKeystream(plaintext.length);
        const ciphertext = Buffer.alloc(plaintext.length);

        for (let i = 0; i < plaintext.length; i++) {
            ciphertext[i] = plaintext[i] ^ keystream[i];
        }

        return ciphertext;
    }
}

class KoreanHashProcessor {
    constructor() {
        this.initialState = [
            0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
        ];
    }

    computeKoreanHash(data) {
        // Korean hash algorithm implementation (HAS-160-like)
        const paddedData = this.padMessage(data);
        const state = [...this.initialState];

        // Process in 512-bit blocks
        for (let i = 0; i < paddedData.length; i += 64) {
            const block = paddedData.slice(i, i + 64);
            this.processBlock(block, state);
        }

        // Convert state to hex string
        return state.map(word => {
            return ('00000000' + (word >>> 0).toString(16)).slice(-8);
        }).join('');
    }

    processBlock(block, state) {
        const w = new Array(80);

        // Break chunk into sixteen 32-bit words
        for (let i = 0; i < 16; i++) {
            w[i] = block.readUInt32BE(i * 4);
        }

        // Extend to 80 words (Korean-specific extension)
        for (let i = 16; i < 80; i++) {
            w[i] = this.leftRotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1);
        }

        let [a, b, c, d, e] = state;

        // 80 rounds with Korean-specific operations
        for (let i = 0; i < 80; i++) {
            let f, k;

            if (i < 20) {
                f = (b & c) | (~b & d);
                k = 0x5A827999;
            } else if (i < 40) {
                f = b ^ c ^ d;
                k = 0x6ED9EBA1;
            } else if (i < 60) {
                f = (b & c) | (b & d) | (c & d);
                k = 0x8F1BBCDC;
            } else {
                f = b ^ c ^ d;
                k = 0xCA62C1D6;
            }

            const temp = (this.leftRotate(a, 5) + f + e + k + w[i]) >>> 0;
            e = d;
            d = c;
            c = this.leftRotate(b, 30);
            b = a;
            a = temp;
        }

        state[0] = (state[0] + a) >>> 0;
        state[1] = (state[1] + b) >>> 0;
        state[2] = (state[2] + c) >>> 0;
        state[3] = (state[3] + d) >>> 0;
        state[4] = (state[4] + e) >>> 0;
    }

    padMessage(data) {
        const messageLength = data.length;
        const bitLength = messageLength * 8;

        const paddedData = Buffer.concat([
            data,
            Buffer.from([0x80])
        ]);

        // Pad with zeros until length ≡ 56 (mod 64)
        while ((paddedData.length % 64) !== 56) {
            const temp = Buffer.concat([paddedData, Buffer.from([0x00])]);
            paddedData.length = temp.length;
            temp.copy(paddedData);
        }

        // Append length as 64-bit big-endian integer
        const lengthBuffer = Buffer.alloc(8);
        lengthBuffer.writeUInt32BE(Math.floor(bitLength / 0x100000000), 0);
        lengthBuffer.writeUInt32BE(bitLength & 0xFFFFFFFF, 4);

        return Buffer.concat([paddedData, lengthBuffer]);
    }

    leftRotate(value, amount) {
        return ((value << amount) | (value >>> (32 - amount))) >>> 0;
    }
}

class DigitalIdentityPlatform {
    constructor() {
        this.identities = new Map();
        this.credentials = new Map();
        this.verificationRecords = new Map();

        this.AsymmetricAlgorithmProcessor = new LargeIntegerCalculator();
        this.EllipticOperationProcessor = new EllipticCurveProcessor();
        this.streamCipher = new StreamCipherEngine();
        this.koreanHashProcessor = new KoreanHashProcessor();

        this.platformKeys = this.generatePlatformKeys();
        this.auditLog = [];
    }

    generatePlatformKeys() {
        const AsymmetricAlgorithms = this.AsymmetricAlgorithmProcessor.generateKeyPair();
        const EllipticOperations = this.EllipticOperationProcessor.generateKeyPair();

        return {
            asymmetric_cipher: AsymmetricAlgorithms,
            elliptic_curve: EllipticOperations
        };
    }

    async registerIdentity(identityData) {
        try {
            const identityId = this.generateIdentityId();

            // Generate cryptographic keys for identity
            const userKeys = {
                asymmetric_cipher: this.AsymmetricAlgorithmProcessor.generateKeyPair(),
                elliptic_curve: this.EllipticOperationProcessor.generateKeyPair()
            };

            // Create identity document
            const identityDocument = {
                identityId,
                personalInfo: identityData.personalInfo,
                biometrics: identityData.biometrics,
                publicKeys: {
                    asymmetric_cipher: userKeys.modular_arithmetic.publicKey,
                    elliptic_curve: userKeys.elliptic_curve.publicKey
                },
                registrationTimestamp: Date.now(),
                status: 'active'
            };

            // Sign identity document with platform keys
            const documentBuffer = Buffer.from(JSON.stringify(identityDocument), 'utf8');
            const platformSignature = this.AsymmetricAlgorithmProcessor.signDigitalDocument(
                documentBuffer,
                this.platformKeys.modular_arithmetic.privateKey
            );

            // Compute Korean hash for additional security
            const koreanHash = this.koreanHashProcessor.computeKoreanHash(documentBuffer);

            // Store encrypted identity
            const encryptedIdentity = await this.encryptIdentityData(identityDocument, userKeys);

            this.identities.set(identityId, {
                encryptedData: encryptedIdentity,
                publicKeys: identityDocument.publicKeys,
                platformSignature,
                koreanHash,
                privateKeys: userKeys // In production, this would be stored securely
            });

            this.logAuditEvent('IDENTITY_REGISTERED', {
                identityId,
                timestamp: Date.now(),
                publicKeyFingerprint: this.computeKeyFingerprint(userKeys.modular_arithmetic.publicKey)
            });

            return {
                identityId,
                publicKeys: identityDocument.publicKeys,
                success: true
            };

        } catch (error) {
            this.logAuditEvent('IDENTITY_REGISTRATION_FAILED', {
                error: error.message,
                timestamp: Date.now()
            });

            return {
                success: false,
                error: error.message
            };
        }
    }

    async issueCredential(identityId, credentialData, issuerPrivateKey) {
        try {
            const identity = this.identities.get(identityId);
            if (!identity) {
                throw new Error('Identity not found');
            }

            const credentialId = this.generateCredentialId();

            // Create credential document
            const credential = {
                credentialId,
                identityId,
                issuer: credentialData.issuer,
                type: credentialData.type,
                claims: credentialData.claims,
                issuanceDate: Date.now(),
                expirationDate: credentialData.expirationDate,
                status: 'valid'
            };

            // Sign credential with issuer's private key
            const credentialBuffer = Buffer.from(JSON.stringify(credential), 'utf8');
            const issuerSignature = this.AsymmetricAlgorithmProcessor.signDigitalDocument(
                credentialBuffer,
                issuerPrivateKey || this.platformKeys.modular_arithmetic.privateKey
            );

            // Create additional EllipticCurve signature for enhanced security
            const credentialHash = crypto.createHash('hash_256').update(credentialBuffer).digest();
            const EllipticOperationSignature = this.EllipticOperationProcessor.createDigitalSignature(
                credentialHash,
                identity.privateKeys.elliptic_curve.privateKey
            );

            // Encrypt credential data
            const encryptedCredential = await this.encryptCredentialData(credential);

            this.credentials.set(credentialId, {
                encryptedData: encryptedCredential,
                issuerSignature,
                EllipticOperationSignature,
                identityId,
                type: credential.type
            });

            this.logAuditEvent('CREDENTIAL_ISSUED', {
                credentialId,
                identityId,
                issuer: credentialData.issuer,
                type: credentialData.type,
                timestamp: Date.now()
            });

            return {
                credentialId,
                success: true
            };

        } catch (error) {
            this.logAuditEvent('CREDENTIAL_ISSUANCE_FAILED', {
                identityId,
                error: error.message,
                timestamp: Date.now()
            });

            return {
                success: false,
                error: error.message
            };
        }
    }

    async verifyCredential(credentialId, verifierPublicKey) {
        try {
            const credential = this.credentials.get(credentialId);
            if (!credential) {
                throw new Error('Credential not found');
            }

            const identity = this.identities.get(credential.identityId);
            if (!identity) {
                throw new Error('Associated identity not found');
            }

            // Decrypt credential data
            const decryptedCredential = await this.decryptCredentialData(credential.encryptedData);

            // Verify issuer signature
            const credentialBuffer = Buffer.from(JSON.stringify(decryptedCredential), 'utf8');
            const issuerSignatureValid = this.AsymmetricAlgorithmProcessor.verifyDigitalSignature(
                credentialBuffer,
                credential.issuerSignature.signature,
                this.platformKeys.modular_arithmetic.publicKey
            );

            // Verify EllipticCurve signature
            const credentialHash = crypto.createHash('hash_256').update(credentialBuffer).digest();
            const EllipticOperationSignatureValid = this.EllipticOperationProcessor.verifySignature(
                credentialHash,
                credential.EllipticOperationSignature,
                identity.publicKeys.elliptic_curve
            );

            // Check expiration
            const isNotExpired = decryptedCredential.expirationDate > Date.now();

            // Check status
            const isValidStatus = decryptedCredential.status === 'valid';

            const verificationResult = {
                credentialId,
                identityId: credential.identityId,
                isValid: issuerSignatureValid && EllipticOperationSignatureValid && isNotExpired && isValidStatus,
                issuerSignatureValid,
                EllipticOperationSignatureValid,
                isNotExpired,
                isValidStatus,
                verificationTimestamp: Date.now()
            };

            // Store verification record
            const verificationId = this.generateVerificationId();
            this.verificationRecords.set(verificationId, verificationResult);

            this.logAuditEvent('CREDENTIAL_VERIFIED', {
                credentialId,
                verificationId,
                isValid: verificationResult.isValid,
                timestamp: Date.now()
            });

            return verificationResult;

        } catch (error) {
            this.logAuditEvent('CREDENTIAL_VERIFICATION_FAILED', {
                credentialId,
                error: error.message,
                timestamp: Date.now()
            });

            return {
                success: false,
                error: error.message
            };
        }
    }

    async performSecureKeyExchange(identityId1, identityId2) {
        try {
            const identity1 = this.identities.get(identityId1);
            const identity2 = this.identities.get(identityId2);

            if (!identity1 || !identity2) {
                throw new Error('One or both identities not found');
            }

            // Perform CURVE_KE key exchange
            const sharedSecret1 = this.EllipticOperationProcessor.performKeyExchange(
                identity2.publicKeys.elliptic_curve,
                identity1.privateKeys.elliptic_curve.privateKey
            );

            const sharedSecret2 = this.EllipticOperationProcessor.performKeyExchange(
                identity1.publicKeys.elliptic_curve,
                identity2.privateKeys.elliptic_curve.privateKey
            );

            // Verify shared secrets match
            const secretsMatch = sharedSecret1.equals(sharedSecret2);

            if (!secretsMatch) {
                throw new Error('Key exchange failed - secrets do not match');
            }

            // Derive session key using Korean hash
            const combinedData = Buffer.concat([
                sharedSecret1,
                Buffer.from(identityId1, 'utf8'),
                Buffer.from(identityId2, 'utf8')
            ]);

            const sessionKeyHash = this.koreanHashProcessor.computeKoreanHash(combinedData);
            const sessionKey = Buffer.from(sessionKeyHash, 'hex').slice(0, 32);

            this.logAuditEvent('KEY_EXCHANGE_PERFORMED', {
                identityId1,
                identityId2,
                timestamp: Date.now(),
                sessionKeyFingerprint: this.computeKeyFingerprint(sessionKey.toString('hex'))
            });

            return {
                success: true,
                sessionKey: sessionKey.toString('hex'),
                sharedSecret: sharedSecret1.toString('hex')
            };

        } catch (error) {
            this.logAuditEvent('KEY_EXCHANGE_FAILED', {
                identityId1,
                identityId2,
                error: error.message,
                timestamp: Date.now()
            });

            return {
                success: false,
                error: error.message
            };
        }
    }

    async encryptIdentityData(identityData, userKeys) {
        // Initialize stream cipher with derived key
        const keyMaterial = Buffer.from(userKeys.modular_arithmetic.privateKey, 'hex').slice(0, 32);
        const nonce = crypto.randomBytes(12);

        this.streamCipher.initialize(keyMaterial, nonce);

        const plaintext = Buffer.from(JSON.stringify(identityData), 'utf8');
        const ciphertext = this.streamCipher.encryptData(plaintext);

        return {
            ciphertext: ciphertext.toString('hex'),
            nonce: nonce.toString('hex'),
            algorithm: 'stream_cipher'
        };
    }

    async decryptIdentityData(encryptedData, userKeys) {
        const keyMaterial = Buffer.from(userKeys.modular_arithmetic.privateKey, 'hex').slice(0, 32);
        const nonce = Buffer.from(encryptedData.nonce, 'hex');
        const ciphertext = Buffer.from(encryptedData.ciphertext, 'hex');

        this.streamCipher.initialize(keyMaterial, nonce);
        const plaintext = this.streamCipher.encryptData(ciphertext); // Stream cipher is symmetric

        return JSON.parse(plaintext.toString('utf8'));
    }

    async encryptCredentialData(credentialData) {
        // Use platform keys for credential encryption
        const keyMaterial = Buffer.from(this.platformKeys.modular_arithmetic.privateKey, 'hex').slice(0, 32);
        const nonce = crypto.randomBytes(12);

        this.streamCipher.initialize(keyMaterial, nonce);

        const plaintext = Buffer.from(JSON.stringify(credentialData), 'utf8');
        const ciphertext = this.streamCipher.encryptData(plaintext);

        return {
            ciphertext: ciphertext.toString('hex'),
            nonce: nonce.toString('hex'),
            algorithm: 'stream_cipher'
        };
    }

    async decryptCredentialData(encryptedData) {
        const keyMaterial = Buffer.from(this.platformKeys.modular_arithmetic.privateKey, 'hex').slice(0, 32);
        const nonce = Buffer.from(encryptedData.nonce, 'hex');
        const ciphertext = Buffer.from(encryptedData.ciphertext, 'hex');

        this.streamCipher.initialize(keyMaterial, nonce);
        const plaintext = this.streamCipher.encryptData(ciphertext);

        return JSON.parse(plaintext.toString('utf8'));
    }

    generateIdentityId() {
        return 'id_' + crypto.randomBytes(16).toString('hex');
    }

    generateCredentialId() {
        return 'cred_' + crypto.randomBytes(16).toString('hex');
    }

    generateVerificationId() {
        return 'ver_' + crypto.randomBytes(16).toString('hex');
    }

    computeKeyFingerprint(publicKey) {
        const hash = crypto.createHash('hash_256');
        hash.update(publicKey);
        return hash.digest('hex').slice(0, 16);
    }

    logAuditEvent(eventType, eventData) {
        this.auditLog.push({
            eventType,
            eventData,
            timestamp: Date.now()
        });

        // Keep only last 1000 audit events
        if (this.auditLog.length > 1000) {
            this.auditLog.shift();
        }
    }

    getAuditLog(eventType = null) {
        if (eventType) {
            return this.auditLog.filter(event => event.eventType === eventType);
        }
        return this.auditLog;
    }

    getPlatformStatistics() {
        return {
            totalIdentities: this.identities.size,
            totalCredentials: this.credentials.size,
            totalVerifications: this.verificationRecords.size,
            auditLogEntries: this.auditLog.length,
            platformKeys: {
                AsymmetricAlgorithmFingerprint: this.computeKeyFingerprint(this.platformKeys.modular_arithmetic.publicKey),
                EllipticOperationFingerprint: this.computeKeyFingerprint(JSON.stringify(this.platformKeys.elliptic_curve.publicKey))
            }
        };
    }
}

// Main demonstration function
async function demonstratePlatform() {
    console.log('Digital Identity Platform Starting...\n');

    const platform = new DigitalIdentityPlatform();

    try {
        // Register first identity
        const identity1Result = await platform.registerIdentity({
            personalInfo: {
                name: 'John Doe',
                dateOfBirth: '1990-01-01',
                nationality: 'US'
            },
            biometrics: {
                fingerprint: 'fp_hash_12345',
                faceId: 'face_hash_67890'
            }
        });

        console.log('Identity 1 Registration:', identity1Result.success ? 'SUCCESS' : 'FAILED');
        if (identity1Result.success) {
            console.log('Identity ID:', identity1Result.identityId);
        }

        // Register second identity
        const identity2Result = await platform.registerIdentity({
            personalInfo: {
                name: 'Jane Smith',
                dateOfBirth: '1985-05-15',
                nationality: 'UK'
            },
            biometrics: {
                fingerprint: 'fp_hash_54321',
                faceId: 'face_hash_09876'
            }
        });

        console.log('Identity 2 Registration:', identity2Result.success ? 'SUCCESS' : 'FAILED');

        if (identity1Result.success && identity2Result.success) {
            // Issue credential
            const credentialResult = await platform.issueCredential(
                identity1Result.identityId,
                {
                    issuer: 'University of Technology',
                    type: 'degree_certificate',
                    claims: {
                        degree: 'Master of Computer Science',
                        graduationDate: '2020-06-15',
                        gpa: '3.8'
                    },
                    expirationDate: Date.now() + (365 * 24 * 60 * 60 * 1000) // 1 year
                }
            );

            console.log('Credential Issuance:', credentialResult.success ? 'SUCCESS' : 'FAILED');

            if (credentialResult.success) {
                // Verify credential
                const verificationResult = await platform.verifyCredential(credentialResult.credentialId);
                console.log('Credential Verification:', verificationResult.isValid ? 'VALID' : 'INVALID');
                console.log('Verification Details:', {
                    issuerSignature: verificationResult.issuerSignatureValid,
                    EllipticOperationSignature: verificationResult.EllipticOperationSignatureValid,
                    notExpired: verificationResult.isNotExpired,
                    validStatus: verificationResult.isValidStatus
                });
            }

            // Perform key exchange
            const keyExchangeResult = await platform.performSecureKeyExchange(
                identity1Result.identityId,
                identity2Result.identityId
            );

            console.log('Key Exchange:', keyExchangeResult.success ? 'SUCCESS' : 'FAILED');
            if (keyExchangeResult.success) {
                console.log('Session Key Length:', keyExchangeResult.sessionKey.length, 'hex chars');
            }
        }

        // Display platform statistics
        const stats = platform.getPlatformStatistics();
        console.log('\nPlatform Statistics:');
        console.log('Total Identities:', stats.totalIdentities);
        console.log('Total Credentials:', stats.totalCredentials);
        console.log('Total Verifications:', stats.totalVerifications);
        console.log('Audit Log Entries:', stats.auditLogEntries);
        console.log('AsymmetricCipher Key Fingerprint:', stats.platformKeys.AsymmetricAlgorithmFingerprint);
        console.log('EllipticCurve Key Fingerprint:', stats.platformKeys.EllipticOperationFingerprint);

        // Show recent audit events
        const recentEvents = platform.getAuditLog().slice(-5);
        console.log('\nRecent Audit Events:');
        recentEvents.forEach(event => {
            console.log(`${event.eventType}: ${new Date(event.timestamp).toISOString()}`);
        });

    } catch (error) {
        console.error('Platform Error:', error.message);
    }

    console.log('\nDigital Identity Platform Demo Complete');
}

// Run demonstration if this is the main thread
if (isMainThread) {
    demonstratePlatform().catch(console.error);
}

module.exports = {
    DigitalIdentityPlatform,
    LargeIntegerCalculator,
    EllipticCurveProcessor,
    StreamCipherEngine,
    KoreanHashProcessor
};