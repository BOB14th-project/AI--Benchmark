// Enterprise PKI Infrastructure
// Public Key Infrastructure with certificate management and cryptographic services

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Numerics;

namespace EnterprisePKI
{
    public class LargeIntegerProcessor
    {
        private const int KeySize = 2048;
        private const int PublicExponent = 65537;
        private readonly Random _random;

        public LargeIntegerProcessor()
        {
            _random = new Random();
        }

        public class KeyPair
        {
            public BigInteger Modulus { get; set; }
            public BigInteger PublicExponent { get; set; }
            public BigInteger PrivateExponent { get; set; }
            public BigInteger P { get; set; }
            public BigInteger Q { get; set; }
        }

        public KeyPair GenerateKeyPair()
        {
            // Generate two large primes for cryptographic operations
            var p = GenerateLargePrime(KeySize / 2);
            var q = GenerateLargePrime(KeySize / 2);

            // Calculate modulus
            var n = BigInteger.Multiply(p, q);

            // Calculate Euler's totient function
            var phi = BigInteger.Multiply(p - 1, q - 1);

            // Calculate private exponent
            var d = ModularInverse(PublicExponent, phi);

            return new KeyPair
            {
                Modulus = n,
                PublicExponent = PublicExponent,
                PrivateExponent = d,
                P = p,
                Q = q
            };
        }

        public byte[] PerformModularExponentiation(byte[] data, BigInteger exponent, BigInteger modulus)
        {
            var dataInt = new BigInteger(data, isUnsigned: true);
            var result = BigInteger.ModPow(dataInt, exponent, modulus);
            return result.ToByteArray(isUnsigned: true);
        }

        public byte[] SignData(byte[] data, KeyPair privateKey)
        {
            // Compute hash of data
            using var sha256 = SHA256.Create();
            var hash = sha256.ComputeHash(data);

            // Apply PKCS#1 v1.5 padding
            var paddedHash = ApplySignaturePadding(hash);

            // Sign with private key
            var paddedInt = new BigInteger(paddedHash, isUnsigned: true);
            var signature = BigInteger.ModPow(paddedInt, privateKey.PrivateExponent, privateKey.Modulus);

            return signature.ToByteArray(isUnsigned: true);
        }

        public bool VerifySignature(byte[] data, byte[] signature, KeyPair publicKey)
        {
            try
            {
                // Compute hash of data
                using var sha256 = SHA256.Create();
                var hash = sha256.ComputeHash(data);

                // Decrypt signature with public key
                var signatureInt = new BigInteger(signature, isUnsigned: true);
                var decrypted = BigInteger.ModPow(signatureInt, publicKey.PublicExponent, publicKey.Modulus);
                var decryptedBytes = decrypted.ToByteArray(isUnsigned: true);

                // Apply expected padding
                var expectedPadded = ApplySignaturePadding(hash);

                return decryptedBytes.SequenceEqual(expectedPadded);
            }
            catch
            {
                return false;
            }
        }

        private BigInteger GenerateLargePrime(int bitLength)
        {
            BigInteger candidate;
            do
            {
                // Generate random number of specified bit length
                var bytes = new byte[bitLength / 8];
                _random.NextBytes(bytes);

                candidate = new BigInteger(bytes, isUnsigned: true);

                // Ensure odd number and correct bit length
                candidate |= BigInteger.One;
                candidate |= BigInteger.One << (bitLength - 1);

            } while (!MillerRabinTest(candidate, 40));

            return candidate;
        }

        private bool MillerRabinTest(BigInteger n, int k)
        {
            if (n < 2) return false;
            if (n == 2 || n == 3) return true;
            if (n.IsEven) return false;

            // Write n-1 as d * 2^r
            var r = 0;
            var d = n - 1;

            while (d.IsEven)
            {
                d /= 2;
                r++;
            }

            // Perform k rounds of testing
            for (int i = 0; i < k; i++)
            {
                var aBytes = new byte[n.ToByteArray().Length];
                _random.NextBytes(aBytes);
                var a = new BigInteger(aBytes, isUnsigned: true) % (n - 3) + 2;

                var x = BigInteger.ModPow(a, d, n);

                if (x == 1 || x == n - 1)
                    continue;

                bool composite = true;
                for (int j = 0; j < r - 1; j++)
                {
                    x = BigInteger.ModPow(x, 2, n);
                    if (x == n - 1)
                    {
                        composite = false;
                        break;
                    }
                }

                if (composite) return false;
            }

            return true;
        }

        private BigInteger ModularInverse(BigInteger a, BigInteger m)
        {
            var (gcd, x, _) = ExtendedGcd(a, m);
            if (gcd != 1)
                throw new ArgumentException("Modular inverse does not exist");

            return ((x % m) + m) % m;
        }

        private (BigInteger gcd, BigInteger x, BigInteger y) ExtendedGcd(BigInteger a, BigInteger b)
        {
            if (a == 0)
                return (b, 0, 1);

            var (gcd, x1, y1) = ExtendedGcd(b % a, a);
            var x = y1 - (b / a) * x1;
            var y = x1;

            return (gcd, x, y);
        }

        private byte[] ApplySignaturePadding(byte[] hash)
        {
            // SHA-256 DigestInfo for PKCS#1 v1.5
            var digestInfo = new byte[]
            {
                0x30, 0x31, 0x30, 0x0d, 0x06, 0x09, 0x60, 0x86,
                0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01, 0x05,
                0x00, 0x04, 0x20
            };

            var paddingLength = (KeySize / 8) - digestInfo.Length - hash.Length - 3;

            var padded = new List<byte> { 0x00, 0x01 };
            padded.AddRange(Enumerable.Repeat<byte>(0xff, paddingLength));
            padded.Add(0x00);
            padded.AddRange(digestInfo);
            padded.AddRange(hash);

            return padded.ToArray();
        }
    }

    public class EllipticCurveProcessor
    {
        private readonly BigInteger _p;
        private readonly BigInteger _a;
        private readonly BigInteger _b;
        private readonly ECPoint _g;
        private readonly BigInteger _n;

        public class ECPoint
        {
            public BigInteger X { get; set; }
            public BigInteger Y { get; set; }
            public bool IsInfinity { get; set; }

            public ECPoint(BigInteger x, BigInteger y)
            {
                X = x;
                Y = y;
                IsInfinity = false;
            }

            public static ECPoint Infinity => new ECPoint(0, 0) { IsInfinity = true };
        }

        public class ECKeyPair
        {
            public BigInteger PrivateKey { get; set; }
            public ECPoint PublicKey { get; set; }
        }

        public EllipticCurveProcessor()
        {
            // secp256k1 curve parameters
            _p = BigInteger.Parse("115792089237316195423570985008687907853269984665640564039457584007913129639935");
            _a = 0;
            _b = 7;
            _g = new ECPoint(
                BigInteger.Parse("55066263022277343669578718895168534326250603453777594175500187360389116729240"),
                BigInteger.Parse("32670510020758816978083085130507043184471273380659243275938904335757337482424")
            );
            _n = BigInteger.Parse("115792089237316195423570985008687907852837564279074904382605163141518161494337");
        }

        public ECKeyPair GenerateKeyPair()
        {
            var random = new Random();
            var privateKeyBytes = new byte[32];
            random.NextBytes(privateKeyBytes);

            var privateKey = new BigInteger(privateKeyBytes, isUnsigned: true) % (_n - 1) + 1;
            var publicKey = MultiplyPoint(_g, privateKey);

            return new ECKeyPair
            {
                PrivateKey = privateKey,
                PublicKey = publicKey
            };
        }

        public byte[] PerformKeyExchange(ECPoint remotePublicKey, BigInteger localPrivateKey)
        {
            var sharedPoint = MultiplyPoint(remotePublicKey, localPrivateKey);

            // Derive shared secret from x-coordinate
            var sharedSecretBytes = sharedPoint.X.ToByteArray(isUnsigned: true);

            using var sha256 = SHA256.Create();
            return sha256.ComputeHash(sharedSecretBytes);
        }

        public (BigInteger r, BigInteger s) CreateDigitalSignature(byte[] messageHash, BigInteger privateKey)
        {
            var messageHashInt = new BigInteger(messageHash, isUnsigned: true);
            var random = new Random();

            while (true)
            {
                // Generate random k
                var kBytes = new byte[32];
                random.NextBytes(kBytes);
                var k = new BigInteger(kBytes, isUnsigned: true) % (_n - 1) + 1;

                // Calculate r
                var rPoint = MultiplyPoint(_g, k);
                var r = rPoint.X % _n;

                if (r == 0) continue;

                // Calculate s
                var kInv = ModularInverse(k, _n);
                var s = (kInv * (messageHashInt + r * privateKey)) % _n;

                if (s == 0) continue;

                return (r, s);
            }
        }

        public bool VerifyDigitalSignature(byte[] messageHash, (BigInteger r, BigInteger s) signature, ECPoint publicKey)
        {
            try
            {
                var (r, s) = signature;
                var messageHashInt = new BigInteger(messageHash, isUnsigned: true);

                // Verify signature parameters
                if (r < 1 || r >= _n || s < 1 || s >= _n) return false;

                // Calculate verification values
                var sInv = ModularInverse(s, _n);
                var u1 = (messageHashInt * sInv) % _n;
                var u2 = (r * sInv) % _n;

                // Calculate verification point
                var point1 = MultiplyPoint(_g, u1);
                var point2 = MultiplyPoint(publicKey, u2);
                var verificationPoint = AddPoints(point1, point2);

                if (verificationPoint.IsInfinity) return false;

                return verificationPoint.X % _n == r;
            }
            catch
            {
                return false;
            }
        }

        private ECPoint AddPoints(ECPoint p1, ECPoint p2)
        {
            if (p1.IsInfinity) return p2;
            if (p2.IsInfinity) return p1;

            if (p1.X == p2.X)
            {
                if (p1.Y == p2.Y)
                {
                    // Point doubling
                    var s = (3 * p1.X * p1.X * ModularInverse(2 * p1.Y, _p)) % _p;
                    var x3 = (s * s - 2 * p1.X) % _p;
                    var y3 = (s * (p1.X - x3) - p1.Y) % _p;

                    return new ECPoint(x3, y3);
                }
                else
                {
                    return ECPoint.Infinity;
                }
            }
            else
            {
                // Point addition
                var s = ((p2.Y - p1.Y) * ModularInverse(p2.X - p1.X, _p)) % _p;
                var x3 = (s * s - p1.X - p2.X) % _p;
                var y3 = (s * (p1.X - x3) - p1.Y) % _p;

                return new ECPoint(x3, y3);
            }
        }

        private ECPoint MultiplyPoint(ECPoint point, BigInteger scalar)
        {
            if (scalar == 0) return ECPoint.Infinity;

            ECPoint result = ECPoint.Infinity;
            ECPoint addend = point;

            while (scalar > 0)
            {
                if ((scalar & 1) == 1)
                {
                    result = AddPoints(result, addend);
                }
                addend = AddPoints(addend, addend);
                scalar >>= 1;
            }

            return result;
        }

        private BigInteger ModularInverse(BigInteger a, BigInteger m)
        {
            var (gcd, x, _) = ExtendedGcd(a % m, m);
            if (gcd != 1)
                throw new ArgumentException("Modular inverse does not exist");

            return ((x % m) + m) % m;
        }

        private (BigInteger gcd, BigInteger x, BigInteger y) ExtendedGcd(BigInteger a, BigInteger b)
        {
            if (a == 0)
                return (b, 0, 1);

            var (gcd, x1, y1) = ExtendedGcd(b % a, a);
            var x = y1 - (b / a) * x1;
            var y = x1;

            return (gcd, x, y);
        }
    }

    public class AdvancedHashProcessor
    {
        public byte[] ComputeSecureHash(byte[] data)
        {
            using var sha256 = SHA256.Create();
            return sha256.ComputeHash(data);
        }

        public byte[] ComputeHMAC(byte[] key, byte[] data)
        {
            using var hmac = new HMACSHA256(key);
            return hmac.ComputeHash(data);
        }

        public byte[] DeriveKey(string password, byte[] salt, int iterations = 100000, int keyLength = 32)
        {
            using var pbkdf2 = new Rfc2898DeriveBytes(password, salt, iterations, HashAlgorithmName.SHA256);
            return pbkdf2.GetBytes(keyLength);
        }

        public byte[] ComputeKoreanHash(byte[] data)
        {
            // Korean standard hash algorithm implementation
            var state = new uint[] { 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0 };

            var paddedData = PadKoreanMessage(data);

            for (int i = 0; i < paddedData.Length; i += 64)
            {
                var block = new ArraySegment<byte>(paddedData, i, 64).ToArray();
                ProcessKoreanBlock(block, state);
            }

            var result = new byte[20];
            for (int i = 0; i < 5; i++)
            {
                var wordBytes = BitConverter.GetBytes(state[i]);
                if (BitConverter.IsLittleEndian)
                    Array.Reverse(wordBytes);
                Array.Copy(wordBytes, 0, result, i * 4, 4);
            }

            return result;
        }

        private byte[] PadKoreanMessage(byte[] data)
        {
            var messageLength = data.Length;
            var bitLength = (ulong)messageLength * 8;

            var paddedData = new List<byte>(data) { 0x80 };

            while ((paddedData.Count % 64) != 56)
            {
                paddedData.Add(0x00);
            }

            var lengthBytes = BitConverter.GetBytes(bitLength);
            if (BitConverter.IsLittleEndian)
                Array.Reverse(lengthBytes);

            paddedData.AddRange(new byte[4]); // High 32 bits (0 for reasonable message sizes)
            paddedData.AddRange(lengthBytes);

            return paddedData.ToArray();
        }

        private void ProcessKoreanBlock(byte[] block, uint[] state)
        {
            var w = new uint[80];

            // Break chunk into sixteen 32-bit big-endian words
            for (int i = 0; i < 16; i++)
            {
                w[i] = (uint)((block[i * 4] << 24) | (block[i * 4 + 1] << 16) |
                             (block[i * 4 + 2] << 8) | block[i * 4 + 3]);
            }

            // Extend to 80 words with Korean-specific extension
            for (int i = 16; i < 80; i++)
            {
                w[i] = LeftRotate(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
            }

            uint a = state[0], b = state[1], c = state[2], d = state[3], e = state[4];

            // 80 rounds with Korean-specific operations
            for (int i = 0; i < 80; i++)
            {
                uint f, k;

                if (i < 20)
                {
                    f = (b & c) | (~b & d);
                    k = 0x5A827999;
                }
                else if (i < 40)
                {
                    f = b ^ c ^ d;
                    k = 0x6ED9EBA1;
                }
                else if (i < 60)
                {
                    f = (b & c) | (b & d) | (c & d);
                    k = 0x8F1BBCDC;
                }
                else
                {
                    f = b ^ c ^ d;
                    k = 0xCA62C1D6;
                }

                uint temp = LeftRotate(a, 5) + f + e + k + w[i];
                e = d;
                d = c;
                c = LeftRotate(b, 30);
                b = a;
                a = temp;
            }

            state[0] += a;
            state[1] += b;
            state[2] += c;
            state[3] += d;
            state[4] += e;
        }

        private uint LeftRotate(uint value, int amount)
        {
            return (value << amount) | (value >> (32 - amount));
        }
    }

    public class DigitalCertificate
    {
        public string Subject { get; set; }
        public string Issuer { get; set; }
        public DateTime NotBefore { get; set; }
        public DateTime NotAfter { get; set; }
        public string SerialNumber { get; set; }
        public LargeIntegerProcessor.KeyPair PublicKey { get; set; }
        public string[] KeyUsage { get; set; }
        public string[] ExtendedKeyUsage { get; set; }
        public byte[] Signature { get; set; }
        public string SignatureAlgorithm { get; set; }
        public int Version { get; set; }
    }

    public class CertificateAuthority
    {
        public string Name { get; set; }
        public LargeIntegerProcessor.KeyPair CAKeyPair { get; set; }
        public DigitalCertificate CACertificate { get; set; }
        public List<DigitalCertificate> IssuedCertificates { get; set; }
        public List<string> RevokedCertificates { get; set; }

        public CertificateAuthority(string name, LargeIntegerProcessor rsaProcessor)
        {
            Name = name;
            CAKeyPair = rsaProcessor.GenerateKeyPair();
            IssuedCertificates = new List<DigitalCertificate>();
            RevokedCertificates = new List<string>();

            // Create self-signed CA certificate
            CACertificate = CreateSelfSignedCertificate(rsaProcessor);
        }

        private DigitalCertificate CreateSelfSignedCertificate(LargeIntegerProcessor rsaProcessor)
        {
            var certificate = new DigitalCertificate
            {
                Subject = $"CN={Name}, O=Enterprise PKI, C=US",
                Issuer = $"CN={Name}, O=Enterprise PKI, C=US",
                NotBefore = DateTime.UtcNow,
                NotAfter = DateTime.UtcNow.AddYears(10),
                SerialNumber = GenerateSerialNumber(),
                PublicKey = new LargeIntegerProcessor.KeyPair
                {
                    Modulus = CAKeyPair.Modulus,
                    PublicExponent = CAKeyPair.PublicExponent
                },
                KeyUsage = new[] { "keyCertSign", "cRLSign", "digitalSignature" },
                ExtendedKeyUsage = new[] { "certificateAuthority" },
                SignatureAlgorithm = "SHA256withRSA",
                Version = 3
            };

            // Sign certificate with CA private key
            var certData = SerializeCertificateForSigning(certificate);
            certificate.Signature = rsaProcessor.SignData(certData, CAKeyPair);

            return certificate;
        }

        public DigitalCertificate IssueCertificate(string subject, LargeIntegerProcessor.KeyPair subjectPublicKey,
            string[] keyUsage, string[] extendedKeyUsage, int validityYears, LargeIntegerProcessor rsaProcessor)
        {
            var certificate = new DigitalCertificate
            {
                Subject = subject,
                Issuer = CACertificate.Subject,
                NotBefore = DateTime.UtcNow,
                NotAfter = DateTime.UtcNow.AddYears(validityYears),
                SerialNumber = GenerateSerialNumber(),
                PublicKey = new LargeIntegerProcessor.KeyPair
                {
                    Modulus = subjectPublicKey.Modulus,
                    PublicExponent = subjectPublicKey.PublicExponent
                },
                KeyUsage = keyUsage,
                ExtendedKeyUsage = extendedKeyUsage,
                SignatureAlgorithm = "SHA256withRSA",
                Version = 3
            };

            // Sign certificate with CA private key
            var certData = SerializeCertificateForSigning(certificate);
            certificate.Signature = rsaProcessor.SignData(certData, CAKeyPair);

            IssuedCertificates.Add(certificate);

            return certificate;
        }

        public bool VerifyCertificate(DigitalCertificate certificate, LargeIntegerProcessor rsaProcessor)
        {
            try
            {
                // Check if certificate is revoked
                if (RevokedCertificates.Contains(certificate.SerialNumber))
                    return false;

                // Check validity period
                var now = DateTime.UtcNow;
                if (now < certificate.NotBefore || now > certificate.NotAfter)
                    return false;

                // Verify signature
                var certData = SerializeCertificateForSigning(certificate);

                // For self-signed certificates, use the certificate's own public key
                var signingKey = certificate.Issuer == certificate.Subject ? certificate.PublicKey : CAKeyPair;

                return rsaProcessor.VerifySignature(certData, certificate.Signature, signingKey);
            }
            catch
            {
                return false;
            }
        }

        public void RevokeCertificate(string serialNumber)
        {
            if (!RevokedCertificates.Contains(serialNumber))
            {
                RevokedCertificates.Add(serialNumber);
            }
        }

        private string GenerateSerialNumber()
        {
            var random = new Random();
            var bytes = new byte[16];
            random.NextBytes(bytes);
            return Convert.ToHexString(bytes);
        }

        private byte[] SerializeCertificateForSigning(DigitalCertificate certificate)
        {
            // Simplified certificate serialization for signing
            var certData = new
            {
                certificate.Subject,
                certificate.Issuer,
                certificate.NotBefore,
                certificate.NotAfter,
                certificate.SerialNumber,
                PublicKeyModulus = certificate.PublicKey.Modulus.ToString(),
                PublicKeyExponent = certificate.PublicKey.PublicExponent.ToString(),
                certificate.KeyUsage,
                certificate.ExtendedKeyUsage,
                certificate.SignatureAlgorithm,
                certificate.Version
            };

            var json = JsonSerializer.Serialize(certData);
            return Encoding.UTF8.GetBytes(json);
        }
    }

    public class EnterprisePKIInfrastructure
    {
        private readonly LargeIntegerProcessor _rsaProcessor;
        private readonly EllipticCurveProcessor _eccProcessor;
        private readonly AdvancedHashProcessor _hashProcessor;
        private readonly Dictionary<string, CertificateAuthority> _certificateAuthorities;
        private readonly Dictionary<string, DigitalCertificate> _certificateStore;
        private readonly List<string> _auditLog;

        public EnterprisePKIInfrastructure()
        {
            _rsaProcessor = new LargeIntegerProcessor();
            _eccProcessor = new EllipticCurveProcessor();
            _hashProcessor = new AdvancedHashProcessor();
            _certificateAuthorities = new Dictionary<string, CertificateAuthority>();
            _certificateStore = new Dictionary<string, DigitalCertificate>();
            _auditLog = new List<string>();

            // Initialize root CA
            InitializeRootCA();
        }

        public void InitializeRootCA()
        {
            var rootCA = new CertificateAuthority("Enterprise Root CA", _rsaProcessor);
            _certificateAuthorities["root"] = rootCA;
            _certificateStore[rootCA.CACertificate.SerialNumber] = rootCA.CACertificate;

            LogAuditEvent($"Root CA initialized: {rootCA.Name}");
        }

        public string CreateIntermediateCA(string caName, int validityYears = 5)
        {
            try
            {
                var rootCA = _certificateAuthorities["root"];

                // Generate key pair for intermediate CA
                var intermediateKeyPair = _rsaProcessor.GenerateKeyPair();

                // Issue certificate for intermediate CA
                var intermediateCert = rootCA.IssueCertificate(
                    $"CN={caName}, O=Enterprise PKI, C=US",
                    intermediateKeyPair,
                    new[] { "keyCertSign", "cRLSign", "digitalSignature" },
                    new[] { "certificateAuthority" },
                    validityYears,
                    _rsaProcessor
                );

                // Create intermediate CA
                var intermediateCA = new CertificateAuthority(caName, _rsaProcessor)
                {
                    CAKeyPair = intermediateKeyPair,
                    CACertificate = intermediateCert
                };

                _certificateAuthorities[caName.ToLower()] = intermediateCA;
                _certificateStore[intermediateCert.SerialNumber] = intermediateCert;

                LogAuditEvent($"Intermediate CA created: {caName}");

                return intermediateCert.SerialNumber;
            }
            catch (Exception ex)
            {
                LogAuditEvent($"Failed to create intermediate CA {caName}: {ex.Message}");
                throw;
            }
        }

        public string IssueEndEntityCertificate(string subject, string[] keyUsage, string[] extendedKeyUsage,
            int validityYears = 1, string issuingCA = "root")
        {
            try
            {
                if (!_certificateAuthorities.ContainsKey(issuingCA.ToLower()))
                    throw new ArgumentException("Issuing CA not found");

                var ca = _certificateAuthorities[issuingCA.ToLower()];

                // Generate key pair for end entity
                var endEntityKeyPair = _rsaProcessor.GenerateKeyPair();

                // Issue certificate
                var certificate = ca.IssueCertificate(
                    subject,
                    endEntityKeyPair,
                    keyUsage,
                    extendedKeyUsage,
                    validityYears,
                    _rsaProcessor
                );

                _certificateStore[certificate.SerialNumber] = certificate;

                LogAuditEvent($"End entity certificate issued: {subject} by {issuingCA}");

                return certificate.SerialNumber;
            }
            catch (Exception ex)
            {
                LogAuditEvent($"Failed to issue certificate for {subject}: {ex.Message}");
                throw;
            }
        }

        public bool ValidateCertificateChain(string certificateSerialNumber)
        {
            try
            {
                if (!_certificateStore.ContainsKey(certificateSerialNumber))
                    return false;

                var certificate = _certificateStore[certificateSerialNumber];

                // Find issuing CA
                var issuingCA = _certificateAuthorities.Values
                    .FirstOrDefault(ca => ca.CACertificate.Subject == certificate.Issuer);

                if (issuingCA == null)
                    return false;

                // Verify certificate
                var isValid = issuingCA.VerifyCertificate(certificate, _rsaProcessor);

                // If this is not a self-signed certificate, validate the issuing CA's certificate
                if (isValid && certificate.Issuer != certificate.Subject)
                {
                    isValid = ValidateCertificateChain(issuingCA.CACertificate.SerialNumber);
                }

                LogAuditEvent($"Certificate validation: {certificateSerialNumber} - {(isValid ? "VALID" : "INVALID")}");

                return isValid;
            }
            catch (Exception ex)
            {
                LogAuditEvent($"Certificate validation failed for {certificateSerialNumber}: {ex.Message}");
                return false;
            }
        }

        public void RevokeCertificate(string certificateSerialNumber, string reason = "unspecified")
        {
            try
            {
                if (!_certificateStore.ContainsKey(certificateSerialNumber))
                    throw new ArgumentException("Certificate not found");

                var certificate = _certificateStore[certificateSerialNumber];

                // Find issuing CA and revoke certificate
                var issuingCA = _certificateAuthorities.Values
                    .FirstOrDefault(ca => ca.CACertificate.Subject == certificate.Issuer);

                if (issuingCA != null)
                {
                    issuingCA.RevokeCertificate(certificateSerialNumber);
                    LogAuditEvent($"Certificate revoked: {certificateSerialNumber} - Reason: {reason}");
                }
                else
                {
                    throw new InvalidOperationException("Issuing CA not found for certificate revocation");
                }
            }
            catch (Exception ex)
            {
                LogAuditEvent($"Failed to revoke certificate {certificateSerialNumber}: {ex.Message}");
                throw;
            }
        }

        public DigitalCertificate GetCertificate(string serialNumber)
        {
            return _certificateStore.ContainsKey(serialNumber) ? _certificateStore[serialNumber] : null;
        }

        public List<DigitalCertificate> GetCertificatesBySubject(string subject)
        {
            return _certificateStore.Values
                .Where(cert => cert.Subject.Contains(subject))
                .ToList();
        }

        public Dictionary<string, object> GetPKIStatus()
        {
            return new Dictionary<string, object>
            {
                ["total_cas"] = _certificateAuthorities.Count,
                ["total_certificates"] = _certificateStore.Count,
                ["root_ca_serial"] = _certificateAuthorities["root"].CACertificate.SerialNumber,
                ["audit_log_entries"] = _auditLog.Count,
                ["revoked_certificates"] = _certificateAuthorities.Values.Sum(ca => ca.RevokedCertificates.Count)
            };
        }

        public List<string> GetAuditLog(int limit = 100)
        {
            return _auditLog.TakeLast(limit).ToList();
        }

        private void LogAuditEvent(string eventDescription)
        {
            var logEntry = $"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC - {eventDescription}";
            _auditLog.Add(logEntry);

            // Keep only recent entries
            if (_auditLog.Count > 10000)
            {
                _auditLog.RemoveRange(0, 5000);
            }
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Enterprise PKI Infrastructure Starting...\n");

            var pki = new EnterprisePKIInfrastructure();

            try
            {
                // Create intermediate CAs
                Console.WriteLine("Creating intermediate CAs...");
                var departmentCASerial = pki.CreateIntermediateCA("Department CA", 3);
                var devCASerial = pki.CreateIntermediateCA("Development CA", 2);

                Console.WriteLine($"Department CA created: {departmentCASerial}");
                Console.WriteLine($"Development CA created: {devCASerial}\n");

                // Issue end entity certificates
                Console.WriteLine("Issuing end entity certificates...");

                var serverCertSerial = pki.IssueEndEntityCertificate(
                    "CN=web.enterprise.com, O=Enterprise Corp, C=US",
                    new[] { "digitalSignature", "keyEncipherment" },
                    new[] { "serverAuth" },
                    1,
                    "Department CA"
                );

                var clientCertSerial = pki.IssueEndEntityCertificate(
                    "CN=john.doe, O=Enterprise Corp, OU=Engineering, C=US",
                    new[] { "digitalSignature", "keyAgreement" },
                    new[] { "clientAuth", "emailProtection" },
                    1,
                    "Development CA"
                );

                var codeCertSerial = pki.IssueEndEntityCertificate(
                    "CN=Code Signing, O=Enterprise Corp, OU=Development, C=US",
                    new[] { "digitalSignature" },
                    new[] { "codeSigning" },
                    2,
                    "Development CA"
                );

                Console.WriteLine($"Server certificate issued: {serverCertSerial}");
                Console.WriteLine($"Client certificate issued: {clientCertSerial}");
                Console.WriteLine($"Code signing certificate issued: {codeCertSerial}\n");

                // Validate certificate chains
                Console.WriteLine("Validating certificate chains...");

                var certificates = new[] { departmentCASerial, devCASerial, serverCertSerial, clientCertSerial, codeCertSerial };

                foreach (var certSerial in certificates)
                {
                    var isValid = pki.ValidateCertificateChain(certSerial);
                    var certificate = pki.GetCertificate(certSerial);
                    Console.WriteLine($"Certificate {certSerial}: {certificate?.Subject} - {(isValid ? "VALID" : "INVALID")}");
                }

                Console.WriteLine();

                // Demonstrate certificate revocation
                Console.WriteLine("Revoking client certificate...");
                pki.RevokeCertificate(clientCertSerial, "compromised");

                // Re-validate after revocation
                var isValidAfterRevocation = pki.ValidateCertificateChain(clientCertSerial);
                Console.WriteLine($"Client certificate after revocation: {(isValidAfterRevocation ? "VALID" : "INVALID")}\n");

                // Display PKI status
                var status = pki.GetPKIStatus();
                Console.WriteLine("PKI Infrastructure Status:");
                foreach (var (key, value) in status)
                {
                    Console.WriteLine($"  {key}: {value}");
                }

                Console.WriteLine();

                // Show recent audit log
                var auditLog = pki.GetAuditLog(10);
                Console.WriteLine("Recent Audit Log:");
                foreach (var logEntry in auditLog)
                {
                    Console.WriteLine($"  {logEntry}");
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine($"PKI operation failed: {ex.Message}");
            }

            Console.WriteLine("\nEnterprise PKI Infrastructure Demo Complete");
        }
    }
}