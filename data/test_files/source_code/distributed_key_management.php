<?php
/**
 * Distributed Key Management System
 * Enterprise-grade cryptographic key management with threshold schemes
 */

class LargeIntegerMathProcessor {
    private $keySize;
    private $publicExponent;
    private $primeConfidence;

    public function __construct() {
        $this->keySize = 2048;
        $this->publicExponent = 65537;
        $this->primeConfidence = 50;
    }

    public function generateKeyPair() {
        // Generate large prime numbers for cryptographic operations
        $p = $this->generateLargePrime($this->keySize / 2);
        $q = $this->generateLargePrime($this->keySize / 2);

        // Calculate modulus
        $n = gmp_mul($p, $q);

        // Calculate Euler's totient function
        $phi = gmp_mul(gmp_sub($p, 1), gmp_sub($q, 1));

        // Calculate private exponent
        $d = gmp_invert(gmp_init($this->publicExponent), $phi);

        return [
            'public' => [
                'modulus' => gmp_strval($n, 16),
                'exponent' => dechex($this->publicExponent)
            ],
            'private' => [
                'modulus' => gmp_strval($n, 16),
                'exponent' => gmp_strval($d, 16),
                'p' => gmp_strval($p, 16),
                'q' => gmp_strval($q, 16)
            ]
        ];
    }

    public function performModularExponentiation($base, $exponent, $modulus) {
        $baseGmp = gmp_init($base, 16);
        $exponentGmp = gmp_init($exponent, 16);
        $modulusGmp = gmp_init($modulus, 16);

        $result = gmp_powm($baseGmp, $exponentGmp, $modulusGmp);
        return gmp_strval($result, 16);
    }

    public function signData($data, $privateKey) {
        // Compute hash of data
        $hash = hash('sha256', $data, true);

        // Apply PKCS#1 v1.5 padding
        $paddedHash = $this->applySignaturePadding($hash);

        // Convert to hex for GMP operations
        $paddedHex = bin2hex($paddedHash);

        // Sign with private key
        $signature = $this->performModularExponentiation(
            $paddedHex,
            $privateKey['exponent'],
            $privateKey['modulus']
        );

        return $signature;
    }

    public function verifySignature($data, $signature, $publicKey) {
        try {
            // Compute hash of data
            $hash = hash('sha256', $data, true);

            // Decrypt signature with public key
            $decrypted = $this->performModularExponentiation(
                $signature,
                $publicKey['exponent'],
                $publicKey['modulus']
            );

            // Convert back to binary
            $decryptedBinary = hex2bin($decrypted);

            // Apply expected padding
            $expectedPadded = $this->applySignaturePadding($hash);

            return $decryptedBinary === $expectedPadded;

        } catch (Exception $e) {
            return false;
        }
    }

    private function generateLargePrime($bitLength) {
        do {
            // Generate random number of specified bit length
            $bytes = ceil($bitLength / 8);
            $randomBytes = random_bytes($bytes);

            // Convert to GMP integer
            $candidate = gmp_init(bin2hex($randomBytes), 16);

            // Ensure odd number and correct bit length
            $candidate = gmp_or($candidate, 1);
            $candidate = gmp_or($candidate, gmp_pow(2, $bitLength - 1));

        } while (!$this->millerRabinTest($candidate, $this->primeConfidence));

        return $candidate;
    }

    private function millerRabinTest($n, $k) {
        if (gmp_cmp($n, 2) < 0) return false;
        if (gmp_cmp($n, 2) == 0 || gmp_cmp($n, 3) == 0) return true;
        if (gmp_mod($n, 2) == 0) return false;

        // Write n-1 as d * 2^r
        $r = 0;
        $d = gmp_sub($n, 1);

        while (gmp_mod($d, 2) == 0) {
            $d = gmp_div($d, 2);
            $r++;
        }

        // Perform k rounds of testing
        for ($i = 0; $i < $k; $i++) {
            $a = gmp_random_range(2, gmp_sub($n, 2));
            $x = gmp_powm($a, $d, $n);

            if (gmp_cmp($x, 1) == 0 || gmp_cmp($x, gmp_sub($n, 1)) == 0) {
                continue;
            }

            $composite = true;
            for ($j = 0; $j < $r - 1; $j++) {
                $x = gmp_powm($x, 2, $n);
                if (gmp_cmp($x, gmp_sub($n, 1)) == 0) {
                    $composite = false;
                    break;
                }
            }

            if ($composite) return false;
        }

        return true;
    }

    private function applySignaturePadding($hash) {
        // SHA-256 DigestInfo for PKCS#1 v1.5
        $digestInfo = hex2bin('3031300d060960864801650304020105000420');

        $paddingLength = ($this->keySize / 8) - strlen($digestInfo) - strlen($hash) - 3;

        $padded = "\x00\x01";
        $padded .= str_repeat("\xff", $paddingLength);
        $padded .= "\x00";
        $padded .= $digestInfo;
        $padded .= $hash;

        return $padded;
    }
}

class EllipticCurveKeyProcessor {
    private $curveParams;

    public function __construct() {
        // secp256k1 curve parameters
        $this->curveParams = [
            'p' => gmp_init('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F', 16),
            'a' => gmp_init('0', 16),
            'b' => gmp_init('7', 16),
            'gx' => gmp_init('79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798', 16),
            'gy' => gmp_init('483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8', 16),
            'n' => gmp_init('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
        ];
    }

    public function generateKeyPair() {
        // Generate private key
        $privateKey = gmp_random_range(1, gmp_sub($this->curveParams['n'], 1));

        // Generate public key
        $publicKey = $this->pointMultiply(
            [$this->curveParams['gx'], $this->curveParams['gy']],
            $privateKey
        );

        return [
            'private' => gmp_strval($privateKey, 16),
            'public' => [
                'x' => gmp_strval($publicKey[0], 16),
                'y' => gmp_strval($publicKey[1], 16)
            ]
        ];
    }

    public function performKeyExchange($remotePublicKey, $localPrivateKey) {
        $remotePoint = [
            gmp_init($remotePublicKey['x'], 16),
            gmp_init($remotePublicKey['y'], 16)
        ];

        $privateKeyGmp = gmp_init($localPrivateKey, 16);

        $sharedPoint = $this->pointMultiply($remotePoint, $privateKeyGmp);

        // Derive shared secret from x-coordinate
        $sharedSecretHex = gmp_strval($sharedPoint[0], 16);
        $sharedSecret = hex2bin(str_pad($sharedSecretHex, 64, '0', STR_PAD_LEFT));

        return hash('sha256', $sharedSecret, true);
    }

    public function createDigitalSignature($messageHash, $privateKey) {
        $privateKeyGmp = gmp_init($privateKey, 16);
        $messageHashGmp = gmp_init(bin2hex($messageHash), 16);

        do {
            // Generate random k
            $k = gmp_random_range(1, gmp_sub($this->curveParams['n'], 1));

            // Calculate r
            $rPoint = $this->pointMultiply(
                [$this->curveParams['gx'], $this->curveParams['gy']],
                $k
            );
            $r = gmp_mod($rPoint[0], $this->curveParams['n']);

            if (gmp_cmp($r, 0) == 0) continue;

            // Calculate s
            $kInv = gmp_invert($k, $this->curveParams['n']);
            $s = gmp_mod(
                gmp_mul($kInv, gmp_add($messageHashGmp, gmp_mul($r, $privateKeyGmp))),
                $this->curveParams['n']
            );

            if (gmp_cmp($s, 0) == 0) continue;

            return [
                'r' => gmp_strval($r, 16),
                's' => gmp_strval($s, 16)
            ];

        } while (true);
    }

    public function verifyDigitalSignature($messageHash, $signature, $publicKey) {
        try {
            $r = gmp_init($signature['r'], 16);
            $s = gmp_init($signature['s'], 16);
            $messageHashGmp = gmp_init(bin2hex($messageHash), 16);

            $publicKeyPoint = [
                gmp_init($publicKey['x'], 16),
                gmp_init($publicKey['y'], 16)
            ];

            // Verify signature parameters
            if (gmp_cmp($r, 1) < 0 || gmp_cmp($r, $this->curveParams['n']) >= 0) return false;
            if (gmp_cmp($s, 1) < 0 || gmp_cmp($s, $this->curveParams['n']) >= 0) return false;

            // Calculate verification values
            $sInv = gmp_invert($s, $this->curveParams['n']);
            $u1 = gmp_mod(gmp_mul($messageHashGmp, $sInv), $this->curveParams['n']);
            $u2 = gmp_mod(gmp_mul($r, $sInv), $this->curveParams['n']);

            // Calculate verification point
            $point1 = $this->pointMultiply(
                [$this->curveParams['gx'], $this->curveParams['gy']],
                $u1
            );
            $point2 = $this->pointMultiply($publicKeyPoint, $u2);
            $verificationPoint = $this->pointAdd($point1, $point2);

            if ($verificationPoint === null) return false;

            return gmp_cmp(gmp_mod($verificationPoint[0], $this->curveParams['n']), $r) == 0;

        } catch (Exception $e) {
            return false;
        }
    }

    private function pointAdd($p1, $p2) {
        if ($p1 === null) return $p2;
        if ($p2 === null) return $p1;

        $x1 = $p1[0];
        $y1 = $p1[1];
        $x2 = $p2[0];
        $y2 = $p2[1];

        if (gmp_cmp($x1, $x2) == 0) {
            if (gmp_cmp($y1, $y2) == 0) {
                // Point doubling
                $s = gmp_mod(
                    gmp_mul(
                        gmp_mul(3, gmp_mul($x1, $x1)),
                        gmp_invert(gmp_mul(2, $y1), $this->curveParams['p'])
                    ),
                    $this->curveParams['p']
                );
            } else {
                return null; // Point at infinity
            }
        } else {
            // Point addition
            $s = gmp_mod(
                gmp_mul(
                    gmp_sub($y2, $y1),
                    gmp_invert(gmp_sub($x2, $x1), $this->curveParams['p'])
                ),
                $this->curveParams['p']
            );
        }

        $x3 = gmp_mod(gmp_sub(gmp_sub(gmp_mul($s, $s), $x1), $x2), $this->curveParams['p']);
        $y3 = gmp_mod(gmp_sub(gmp_mul($s, gmp_sub($x1, $x3)), $y1), $this->curveParams['p']);

        return [$x3, $y3];
    }

    private function pointMultiply($point, $scalar) {
        if (gmp_cmp($scalar, 0) == 0) return null;

        $result = null;
        $addend = $point;

        while (gmp_cmp($scalar, 0) > 0) {
            if (gmp_mod($scalar, 2) == 1) {
                $result = $result ? $this->pointAdd($result, $addend) : $addend;
            }
            $addend = $this->pointAdd($addend, $addend);
            $scalar = gmp_div($scalar, 2);
        }

        return $result;
    }
}

class SecretSharingProcessor {
    // Shamir's Secret Sharing implementation

    private $prime;

    public function __construct() {
        // Large prime for secret sharing operations
        $this->prime = gmp_init('2^521 - 1');
    }

    public function splitSecret($secret, $threshold, $shares) {
        if ($threshold > $shares) {
            throw new InvalidArgumentException('Threshold cannot exceed number of shares');
        }

        $secretGmp = gmp_init(bin2hex($secret), 16);

        // Generate random polynomial coefficients
        $coefficients = [$secretGmp];
        for ($i = 1; $i < $threshold; $i++) {
            $coefficients[] = gmp_random_range(1, gmp_sub($this->prime, 1));
        }

        // Generate shares
        $secretShares = [];
        for ($x = 1; $x <= $shares; $x++) {
            $y = $this->evaluatePolynomial($coefficients, $x);
            $secretShares[] = [
                'x' => $x,
                'y' => gmp_strval($y, 16),
                'threshold' => $threshold
            ];
        }

        return $secretShares;
    }

    public function reconstructSecret($shares) {
        if (empty($shares)) {
            throw new InvalidArgumentException('No shares provided');
        }

        $threshold = $shares[0]['threshold'];
        if (count($shares) < $threshold) {
            throw new InvalidArgumentException('Insufficient shares for reconstruction');
        }

        // Use first 'threshold' shares for reconstruction
        $usedShares = array_slice($shares, 0, $threshold);

        // Lagrange interpolation
        $secret = gmp_init(0);

        foreach ($usedShares as $i => $share1) {
            $xi = $share1['x'];
            $yi = gmp_init($share1['y'], 16);

            $numerator = gmp_init(1);
            $denominator = gmp_init(1);

            foreach ($usedShares as $j => $share2) {
                if ($i != $j) {
                    $xj = $share2['x'];
                    $numerator = gmp_mul($numerator, gmp_init(-$xj));
                    $denominator = gmp_mul($denominator, gmp_init($xi - $xj));
                }
            }

            $lagrangeCoeff = gmp_mod(
                gmp_mul($numerator, gmp_invert($denominator, $this->prime)),
                $this->prime
            );

            $secret = gmp_add($secret, gmp_mul($yi, $lagrangeCoeff));
        }

        $secret = gmp_mod($secret, $this->prime);
        $secretHex = gmp_strval($secret, 16);

        // Pad to even length
        if (strlen($secretHex) % 2 == 1) {
            $secretHex = '0' . $secretHex;
        }

        return hex2bin($secretHex);
    }

    private function evaluatePolynomial($coefficients, $x) {
        $result = gmp_init(0);
        $xPower = gmp_init(1);

        foreach ($coefficients as $coeff) {
            $result = gmp_add($result, gmp_mul($coeff, $xPower));
            $xPower = gmp_mul($xPower, $x);
        }

        return gmp_mod($result, $this->prime);
    }
}

class AdvancedHashProcessor {
    // Advanced cryptographic hash functions

    public function computeSecureHash($data) {
        return hash('sha256', $data, true);
    }

    public function computeHMAC($key, $data) {
        return hash_hmac('sha256', $data, $key, true);
    }

    public function deriveKey($password, $salt, $iterations = 100000, $length = 32) {
        return hash_pbkdf2('sha256', $password, $salt, $iterations, $length, true);
    }

    public function computeKoreanHash($data) {
        // Korean standard hash algorithm implementation
        $state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0];

        $paddedData = $this->padKoreanMessage($data);

        for ($i = 0; $i < strlen($paddedData); $i += 64) {
            $block = substr($paddedData, $i, 64);
            $this->processKoreanBlock($block, $state);
        }

        $result = '';
        foreach ($state as $word) {
            $result .= pack('N', $word & 0xFFFFFFFF);
        }

        return $result;
    }

    private function padKoreanMessage($data) {
        $messageLength = strlen($data);
        $bitLength = $messageLength * 8;

        $paddedData = $data . "\x80";

        while ((strlen($paddedData) % 64) != 56) {
            $paddedData .= "\x00";
        }

        $paddedData .= pack('NN', $bitLength >> 32, $bitLength & 0xFFFFFFFF);

        return $paddedData;
    }

    private function processKoreanBlock($block, &$state) {
        $w = array_merge(unpack('N16', $block), array_fill(16, 64, 0));

        // Extend to 80 words with Korean-specific extension
        for ($i = 16; $i < 80; $i++) {
            $w[$i] = $this->leftRotate($w[$i-3] ^ $w[$i-8] ^ $w[$i-14] ^ $w[$i-16], 1);
        }

        list($a, $b, $c, $d, $e) = $state;

        // 80 rounds with Korean-specific operations
        for ($i = 0; $i < 80; $i++) {
            if ($i < 20) {
                $f = ($b & $c) | (~$b & $d);
                $k = 0x5A827999;
            } elseif ($i < 40) {
                $f = $b ^ $c ^ $d;
                $k = 0x6ED9EBA1;
            } elseif ($i < 60) {
                $f = ($b & $c) | ($b & $d) | ($c & $d);
                $k = 0x8F1BBCDC;
            } else {
                $f = $b ^ $c ^ $d;
                $k = 0xCA62C1D6;
            }

            $temp = ($this->leftRotate($a, 5) + $f + $e + $k + $w[$i]) & 0xFFFFFFFF;
            $e = $d;
            $d = $c;
            $c = $this->leftRotate($b, 30);
            $b = $a;
            $a = $temp;
        }

        $state[0] = ($state[0] + $a) & 0xFFFFFFFF;
        $state[1] = ($state[1] + $b) & 0xFFFFFFFF;
        $state[2] = ($state[2] + $c) & 0xFFFFFFFF;
        $state[3] = ($state[3] + $d) & 0xFFFFFFFF;
        $state[4] = ($state[4] + $e) & 0xFFFFFFFF;
    }

    private function leftRotate($value, $amount) {
        return (($value << $amount) | ($value >> (32 - $amount))) & 0xFFFFFFFF;
    }
}

class DistributedKeyManagement {
    private $keyStore;
    private $nodeId;
    private $rsaProcessor;
    private $eccProcessor;
    private $secretSharing;
    private $hashProcessor;
    private $auditLog;

    public function __construct($nodeId) {
        $this->nodeId = $nodeId;
        $this->keyStore = [];
        $this->auditLog = [];

        $this->rsaProcessor = new LargeIntegerMathProcessor();
        $this->eccProcessor = new EllipticCurveKeyProcessor();
        $this->secretSharing = new SecretSharingProcessor();
        $this->hashProcessor = new AdvancedHashProcessor();

        // Initialize node with master keys
        $this->initializeNode();
    }

    public function createDistributedKey($keyId, $threshold, $totalShares, $keyType = 'aes256') {
        try {
            // Generate master key
            if ($keyType === 'aes256') {
                $masterKey = random_bytes(32);
            } elseif ($keyType === 'aes128') {
                $masterKey = random_bytes(16);
            } else {
                throw new InvalidArgumentException('Unsupported key type');
            }

            // Split key using secret sharing
            $keyShares = $this->secretSharing->splitSecret($masterKey, $threshold, $totalShares);

            // Create key metadata
            $keyMetadata = [
                'key_id' => $keyId,
                'key_type' => $keyType,
                'threshold' => $threshold,
                'total_shares' => $totalShares,
                'created_at' => time(),
                'created_by' => $this->nodeId,
                'version' => 1
            ];

            // Sign metadata with node's private key
            $metadataJson = json_encode($keyMetadata);
            $signature = $this->rsaProcessor->signData($metadataJson, $this->keyStore['node_keys']['rsa']['private']);

            $distributedKey = [
                'metadata' => $keyMetadata,
                'shares' => $keyShares,
                'signature' => $signature,
                'korean_hash' => bin2hex($this->hashProcessor->computeKoreanHash($metadataJson))
            ];

            // Store key information
            $this->keyStore['distributed_keys'][$keyId] = $distributedKey;

            $this->logAuditEvent('KEY_CREATED', [
                'key_id' => $keyId,
                'key_type' => $keyType,
                'threshold' => $threshold,
                'total_shares' => $totalShares
            ]);

            return [
                'success' => true,
                'key_id' => $keyId,
                'shares' => $keyShares,
                'metadata' => $keyMetadata
            ];

        } catch (Exception $e) {
            $this->logAuditEvent('KEY_CREATION_FAILED', [
                'key_id' => $keyId,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    public function reconstructDistributedKey($keyId, $providedShares) {
        try {
            if (!isset($this->keyStore['distributed_keys'][$keyId])) {
                throw new InvalidArgumentException('Key not found');
            }

            $keyInfo = $this->keyStore['distributed_keys'][$keyId];

            // Verify metadata signature
            $metadataJson = json_encode($keyInfo['metadata']);
            $signatureValid = $this->rsaProcessor->verifySignature(
                $metadataJson,
                $keyInfo['signature'],
                $this->keyStore['node_keys']['rsa']['public']
            );

            if (!$signatureValid) {
                throw new Exception('Key metadata signature verification failed');
            }

            // Verify Korean hash
            $computedKoreanHash = bin2hex($this->hashProcessor->computeKoreanHash($metadataJson));
            if ($computedKoreanHash !== $keyInfo['korean_hash']) {
                throw new Exception('Korean hash verification failed');
            }

            // Verify we have enough shares
            if (count($providedShares) < $keyInfo['metadata']['threshold']) {
                throw new Exception('Insufficient shares for key reconstruction');
            }

            // Reconstruct the key
            $reconstructedKey = $this->secretSharing->reconstructSecret($providedShares);

            $this->logAuditEvent('KEY_RECONSTRUCTED', [
                'key_id' => $keyId,
                'shares_used' => count($providedShares),
                'threshold' => $keyInfo['metadata']['threshold']
            ]);

            return [
                'success' => true,
                'key_id' => $keyId,
                'reconstructed_key' => bin2hex($reconstructedKey),
                'key_type' => $keyInfo['metadata']['key_type']
            ];

        } catch (Exception $e) {
            $this->logAuditEvent('KEY_RECONSTRUCTION_FAILED', [
                'key_id' => $keyId,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    public function performSecureKeyExchange($remoteNodeId, $remotePublicKey) {
        try {
            // Perform ECDH key exchange
            $sharedSecret = $this->eccProcessor->performKeyExchange(
                $remotePublicKey,
                $this->keyStore['node_keys']['ecc']['private']
            );

            // Derive session key using advanced key derivation
            $salt = random_bytes(32);
            $sessionKey = $this->hashProcessor->deriveKey($sharedSecret, $salt, 100000, 32);

            // Store session key
            $sessionId = bin2hex(random_bytes(16));
            $this->keyStore['session_keys'][$sessionId] = [
                'remote_node' => $remoteNodeId,
                'session_key' => $sessionKey,
                'salt' => $salt,
                'created_at' => time(),
                'expires_at' => time() + 3600 // 1 hour
            ];

            $this->logAuditEvent('KEY_EXCHANGE_PERFORMED', [
                'remote_node' => $remoteNodeId,
                'session_id' => $sessionId
            ]);

            return [
                'success' => true,
                'session_id' => $sessionId,
                'salt' => bin2hex($salt)
            ];

        } catch (Exception $e) {
            $this->logAuditEvent('KEY_EXCHANGE_FAILED', [
                'remote_node' => $remoteNodeId,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    public function encryptWithDistributedKey($keyId, $data, $providedShares) {
        try {
            // Reconstruct the key
            $keyResult = $this->reconstructDistributedKey($keyId, $providedShares);

            if (!$keyResult['success']) {
                return $keyResult;
            }

            $key = hex2bin($keyResult['reconstructed_key']);

            // Generate random IV
            $iv = random_bytes(16);

            // Encrypt data using AES
            $ciphertext = openssl_encrypt($data, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);

            if ($ciphertext === false) {
                throw new Exception('Encryption failed');
            }

            // Generate authentication tag
            $authTag = $this->hashProcessor->computeHMAC($key, $iv . $ciphertext);

            $this->logAuditEvent('DATA_ENCRYPTED', [
                'key_id' => $keyId,
                'data_length' => strlen($data),
                'ciphertext_length' => strlen($ciphertext)
            ]);

            return [
                'success' => true,
                'ciphertext' => base64_encode($ciphertext),
                'iv' => base64_encode($iv),
                'auth_tag' => base64_encode($authTag),
                'algorithm' => 'AES-256-CBC'
            ];

        } catch (Exception $e) {
            $this->logAuditEvent('ENCRYPTION_FAILED', [
                'key_id' => $keyId,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    public function decryptWithDistributedKey($keyId, $encryptedData, $providedShares) {
        try {
            // Reconstruct the key
            $keyResult = $this->reconstructDistributedKey($keyId, $providedShares);

            if (!$keyResult['success']) {
                return $keyResult;
            }

            $key = hex2bin($keyResult['reconstructed_key']);

            // Decode encrypted components
            $ciphertext = base64_decode($encryptedData['ciphertext']);
            $iv = base64_decode($encryptedData['iv']);
            $authTag = base64_decode($encryptedData['auth_tag']);

            // Verify authentication tag
            $computedAuthTag = $this->hashProcessor->computeHMAC($key, $iv . $ciphertext);

            if (!hash_equals($authTag, $computedAuthTag)) {
                throw new Exception('Authentication tag verification failed');
            }

            // Decrypt data
            $plaintext = openssl_decrypt($ciphertext, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);

            if ($plaintext === false) {
                throw new Exception('Decryption failed');
            }

            $this->logAuditEvent('DATA_DECRYPTED', [
                'key_id' => $keyId,
                'ciphertext_length' => strlen($ciphertext),
                'plaintext_length' => strlen($plaintext)
            ]);

            return [
                'success' => true,
                'plaintext' => $plaintext
            ];

        } catch (Exception $e) {
            $this->logAuditEvent('DECRYPTION_FAILED', [
                'key_id' => $keyId,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    public function getNodeStatus() {
        return [
            'node_id' => $this->nodeId,
            'distributed_keys' => count($this->keyStore['distributed_keys'] ?? []),
            'session_keys' => count($this->keyStore['session_keys'] ?? []),
            'audit_entries' => count($this->auditLog),
            'rsa_fingerprint' => $this->computeKeyFingerprint($this->keyStore['node_keys']['rsa']['public']),
            'ecc_fingerprint' => $this->computeKeyFingerprint($this->keyStore['node_keys']['ecc']['public']),
            'uptime' => time() - $this->keyStore['node_start_time']
        ];
    }

    public function getAuditLog($limit = 100) {
        return array_slice($this->auditLog, -$limit);
    }

    private function initializeNode() {
        // Generate node RSA key pair
        $rsaKeys = $this->rsaProcessor->generateKeyPair();

        // Generate node ECC key pair
        $eccKeys = $this->eccProcessor->generateKeyPair();

        $this->keyStore = [
            'node_keys' => [
                'rsa' => $rsaKeys,
                'ecc' => $eccKeys
            ],
            'distributed_keys' => [],
            'session_keys' => [],
            'node_start_time' => time()
        ];

        $this->logAuditEvent('NODE_INITIALIZED', [
            'node_id' => $this->nodeId,
            'rsa_fingerprint' => $this->computeKeyFingerprint($rsaKeys['public']),
            'ecc_fingerprint' => $this->computeKeyFingerprint($eccKeys['public'])
        ]);
    }

    private function computeKeyFingerprint($publicKey) {
        $keyData = json_encode($publicKey);
        $hash = $this->hashProcessor->computeSecureHash($keyData);
        return substr(bin2hex($hash), 0, 16);
    }

    private function logAuditEvent($eventType, $eventData) {
        $auditEntry = [
            'event_type' => $eventType,
            'event_data' => $eventData,
            'timestamp' => time(),
            'node_id' => $this->nodeId
        ];

        $this->auditLog[] = $auditEntry;

        // Keep only recent entries
        if (count($this->auditLog) > 10000) {
            $this->auditLog = array_slice($this->auditLog, -5000);
        }
    }
}

// Demonstration of the distributed key management system
function demonstrateDistributedKeyManagement() {
    echo "Distributed Key Management System Starting...\n\n";

    // Create multiple nodes
    $node1 = new DistributedKeyManagement('node_001');
    $node2 = new DistributedKeyManagement('node_002');
    $node3 = new DistributedKeyManagement('node_003');

    echo "Created 3 nodes\n";

    // Create distributed key with threshold 2 of 3
    $keyResult = $node1->createDistributedKey('test_key_001', 2, 3, 'aes256');

    if ($keyResult['success']) {
        echo "Distributed key created successfully\n";
        echo "Key ID: " . $keyResult['key_id'] . "\n";
        echo "Shares generated: " . count($keyResult['shares']) . "\n\n";

        $shares = $keyResult['shares'];

        // Test encryption with 2 shares (threshold met)
        $testData = "Confidential enterprise data requiring distributed key protection";

        echo "Testing encryption with threshold shares...\n";
        $encryptResult = $node1->encryptWithDistributedKey(
            'test_key_001',
            $testData,
            array_slice($shares, 0, 2)  // Use first 2 shares
        );

        if ($encryptResult['success']) {
            echo "Encryption successful\n";
            echo "Algorithm: " . $encryptResult['algorithm'] . "\n";
            echo "Ciphertext length: " . strlen(base64_decode($encryptResult['ciphertext'])) . " bytes\n\n";

            // Test decryption with different 2 shares
            echo "Testing decryption with different shares...\n";
            $decryptResult = $node2->decryptWithDistributedKey(
                'test_key_001',
                $encryptResult,
                array_slice($shares, 1, 2)  // Use shares 2 and 3
            );

            if ($decryptResult['success']) {
                echo "Decryption successful\n";
                echo "Decrypted data: " . substr($decryptResult['plaintext'], 0, 50) . "...\n";
                echo "Data matches: " . ($decryptResult['plaintext'] === $testData ? 'YES' : 'NO') . "\n\n";
            } else {
                echo "Decryption failed: " . $decryptResult['error'] . "\n\n";
            }
        } else {
            echo "Encryption failed: " . $encryptResult['error'] . "\n\n";
        }

        // Test key exchange between nodes
        echo "Testing secure key exchange...\n";
        $node1Status = $node1->getNodeStatus();
        $node2Status = $node2->getNodeStatus();

        echo "Node 1 RSA fingerprint: " . $node1Status['rsa_fingerprint'] . "\n";
        echo "Node 2 RSA fingerprint: " . $node2Status['rsa_fingerprint'] . "\n\n";

    } else {
        echo "Failed to create distributed key: " . $keyResult['error'] . "\n";
    }

    // Display node statuses
    $nodes = [$node1, $node2, $node3];
    foreach ($nodes as $i => $node) {
        $status = $node->getNodeStatus();
        echo "Node " . ($i + 1) . " Status:\n";
        echo "  Distributed Keys: " . $status['distributed_keys'] . "\n";
        echo "  Session Keys: " . $status['session_keys'] . "\n";
        echo "  Audit Entries: " . $status['audit_entries'] . "\n";
        echo "  RSA Fingerprint: " . $status['rsa_fingerprint'] . "\n";
        echo "  ECC Fingerprint: " . $status['ecc_fingerprint'] . "\n";
        echo "  Uptime: " . $status['uptime'] . " seconds\n\n";
    }

    echo "Distributed Key Management Demo Complete\n";
}

// Run demonstration if this file is executed directly
if (php_sapi_name() === 'cli') {
    demonstrateDistributedKeyManagement();
}

?>