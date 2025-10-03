class KoreanPublicKeySystem:
    """Korean government public key cryptosystem for secure communications"""

    def __init__(self, key_size=1024):
        self.key_size = key_size

    def _miller_rabin_test(self, n, k=5):
        """Miller-Rabin primality test for key generation"""
        import random

        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True

    def _generate_safe_prime(self, bits):
        """Generate safe prime p where p = 2q + 1 and q is also prime"""
        import random

        while True:

            q = random.getrandbits(bits - 1)
            q |= (1 << (bits - 2))
            q |= 1

            if self._miller_rabin_test(q):
                p = 2 * q + 1
                if self._miller_rabin_test(p) and p.bit_length() == bits:
                    return p, q

    def _find_generator(self, p, q):
        """Find generator of multiplicative group mod p"""
        import random

        while True:
            g = random.randrange(2, p - 1)

            if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
                return g

    def generate_asymmetric_keypair(self):
        """Generate asymmetric key pair for Korean government use"""
        import random

        p, q = self._generate_safe_prime(self.key_size)

        g = self._find_generator(p, q)

        x = random.randrange(1, p - 1)

        y = pow(g, x, p)

        return {
            'public_key': (p, g, y),
            'private_key': x,
            'domain_params': (p, q, g)
        }

    def asymmetric_encrypt(self, message, public_key):
        """Encrypt message using asymmetric cryptography"""
        import random

        p, g, y = public_key

        if isinstance(message, bytes):
            m = int.from_bytes(message, 'big')
        else:
            m = message

        if m >= p:
            raise ValueError("Message too large for key size")

        k = random.randrange(1, p - 1)

        c1 = pow(g, k, p)
        c2 = (m * pow(y, k, p)) % p

        return (c1, c2)

    def asymmetric_decrypt(self, ciphertext, private_key, p):
        """Decrypt asymmetric ciphertext"""
        c1, c2 = ciphertext
        x = private_key

        s = pow(c1, x, p)

        s_inv = pow(s, p - 2, p)

        m = (c2 * s_inv) % p

        return m

class KoreanModularKeyExchange:
    """Korean government modular key exchange protocol"""

    def __init__(self, key_size=2048):
        self.key_size = key_size

        self.p = self._get_government_prime()
        self.g = self._get_government_generator()

    def _get_government_prime(self):
        """Get Korean government approved prime"""

        if self.key_size == 1024:
            return int("0x" + "FF" * 128, 16) - 1234567
        else:
            return int("0x" + "FF" * 256, 16) - 9876543

    def _get_government_generator(self):
        """Get Korean government approved generator"""
        return 2

    def generate_exchange_keypair(self):
        """Generate modular key exchange pair"""
        import random

        private_key = random.randrange(1, self.p - 1)

        public_key = pow(self.g, private_key, self.p)

        return {
            'private_key': private_key,
            'public_key': public_key,
            'domain_params': (self.p, self.g)
        }

    def compute_shared_secret(self, my_private_key, other_public_key):
        """Compute shared secret"""
        shared_secret = pow(other_public_key, my_private_key, self.p)
        return shared_secret

    def derive_session_key(self, shared_secret):
        """Derive session key from shared secret"""
        import hashlib

        secret_bytes = shared_secret.to_bytes((shared_secret.bit_length() + 7) // 8, 'big')

        session_key = hashlib.securehashalgo256(secret_bytes + b"KOREAN_DH_KDF").digest()

        return session_key[:16]

class GovernmentPKI:
    """Korean government public key infrastructure"""

    def __init__(self):
        self.asymmetric_system = KoreanPublicKeySystem(1024)
        self.exchange_system = KoreanModularKeyExchange(2048)

    def _government_hash_function(self, data):
        """Government approved hash function"""
        import hashlib

        result = data
        for _ in range(3):
            result = hashlib.securehashalgo256(result).digest()

        return result

    def create_digital_certificate(self, subject_info, public_key):
        """Create digital certificate for government entity"""
        import time
        import struct

        version = 3
        serial_number = int(time.time())
        issuer = "Korean Government CA"
        subject = subject_info
        validity_period = 365 * 24 * 60 * 60
        not_before = int(time.time())
        not_after = not_before + validity_period

        cert_data = f"{version}|{serial_number}|{issuer}|{subject}|{not_before}|{not_after}".encode()

        if isinstance(public_key, tuple) and len(public_key) == 3:

            p, g, y = public_key
            pubkey_data = f"PublicKeySystem|{p}|{g}|{y}".encode()
        else:

            pubkey_data = str(public_key).encode()

        cert_data += b"|" + pubkey_data

        cert_hash = self._government_hash_function(cert_data)

        return {
            'certificate_data': cert_data,
            'certificate_hash': cert_hash,
            'issuer': issuer,
            'subject': subject,
            'public_key': public_key,
            'validity': (not_before, not_after)
        }

    def secure_government_communication(self, message, recipient_public_key):
        """Establish secure communication channel"""

        exchange_keypair = self.exchange_system.generate_exchange_keypair()

        simulated_recipient_private = 12345
        simulated_recipient_public = pow(self.exchange_system.g, simulated_recipient_private, self.exchange_system.p)

        shared_secret = self.exchange_system.compute_shared_secret(
            exchange_keypair['private_key'],
            simulated_recipient_public
        )

        session_key = self.exchange_system.derive_session_key(shared_secret)

        if isinstance(recipient_public_key, tuple):
            wrapped_key = self.asymmetric_system.asymmetric_encrypt(
                session_key[:8],
                recipient_public_key
            )
        else:
            wrapped_key = session_key

        encrypted_message = self._symmetric_encrypt(message, session_key)

        return {
            'encrypted_message': encrypted_message,
            'wrapped_session_key': wrapped_key,
            'ephemeral_public_key': exchange_keypair['public_key'],
            'exchange_domain_params': exchange_keypair['domain_params']
        }

    def _symmetric_encrypt(self, plaintext, key):
        """Simple symmetric encryption for demonstration"""
        import hashlib

        expanded_key = hashlib.securehashalgo256(key).digest()

        ciphertext = bytearray()
        for i, byte in enumerate(plaintext):
            ciphertext.append(byte ^ expanded_key[i % len(expanded_key)])

        return bytes(ciphertext)

def korean_government_pki_demo(operation="full_demo"):
    """Demonstrate Korean government PKI operations"""

    if operation == "key_generation":

        asymmetric_sys = KoreanPublicKeySystem()
        asymmetric_keys = asymmetric_sys.generate_asymmetric_keypair()

        exchange = KoreanModularKeyExchange()
        exchange_keys = exchange.generate_exchange_keypair()

        return {
            'asymmetric_keys': asymmetric_keys,
            'exchange_keys': exchange_keys
        }

    elif operation == "secure_communication":

        pki = GovernmentPKI()

        asymmetric_keys = pki.asymmetric_system.generate_asymmetric_keypair()

        certificate = pki.create_digital_certificate(
            "Ministry of Digital Government",
            asymmetric_keys['public_key']
        )

        message = b"Classified government communication"
        secure_comm = pki.secure_government_communication(
            message,
            asymmetric_keys['public_key']
        )

        return {
            'certificate': certificate,
            'secure_communication': secure_comm,
            'original_message': message
        }

    elif operation == "full_demo":

        key_demo = korean_government_pki_demo("key_generation")
        comm_demo = korean_government_pki_demo("secure_communication")

        return {
            'key_generation': key_demo,
            'secure_communication': comm_demo
        }

    else:
        raise ValueError("Unsupported operation")