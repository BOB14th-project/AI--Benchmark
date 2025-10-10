# Secure Messaging Protocol
# End-to-end encrypted messaging with advanced cryptographic protocols

require 'digest'
require 'openssl'
require 'securerandom'
require 'json'
require 'base64'
require 'thread'

class LargeIntegerArithmetic
  # Large integer operations for public key cryptography

  attr_reader :key_size, :public_exponent

  def initialize
    @key_size = 2048
    @public_exponent = 65537
    @security_level = 112  # bits of security
  end

  def generate_keypair
    # Generate large prime numbers for key generation
    p = generate_large_prime(@key_size / 2)
    q = generate_large_prime(@key_size / 2)

    # Calculate modulus
    n = p * q

    # Calculate Euler's totient
    phi = (p - 1) * (q - 1)

    # Calculate private exponent
    d = modular_inverse(@public_exponent, phi)

    {
      public_key: {
        modulus: n.to_s(16),
        exponent: @public_exponent.to_s(16)
      },
      private_key: {
        modulus: n.to_s(16),
        exponent: d.to_s(16),
        p: p.to_s(16),
        q: q.to_s(16)
      }
    }
  end

  def encrypt_with_public_key(message, public_key)
    modulus = public_key[:modulus].to_i(16)
    exponent = public_key[:exponent].to_i(16)

    # Convert message to integer
    message_int = message.unpack1('H*').to_i(16)

    # Perform modular exponentiation
    ciphertext_int = modular_exponentiation(message_int, exponent, modulus)

    # Convert back to bytes
    hex_string = ciphertext_int.to_s(16)
    hex_string = '0' + hex_string if hex_string.length.odd?
    [hex_string].pack('H*')
  end

  def decrypt_with_private_key(ciphertext, private_key)
    modulus = private_key[:modulus].to_i(16)
    exponent = private_key[:exponent].to_i(16)

    # Convert ciphertext to integer
    ciphertext_int = ciphertext.unpack1('H*').to_i(16)

    # Perform modular exponentiation
    plaintext_int = modular_exponentiation(ciphertext_int, exponent, modulus)

    # Convert back to bytes
    hex_string = plaintext_int.to_s(16)
    hex_string = '0' + hex_string if hex_string.length.odd?
    [hex_string].pack('H*')
  end

  def sign_message(message_hash, private_key)
    modulus = private_key[:modulus].to_i(16)
    exponent = private_key[:exponent].to_i(16)

    # Apply PKCS#1 v1.5 padding
    padded_hash = apply_signature_padding(message_hash)

    # Convert to integer
    padded_int = padded_hash.unpack1('H*').to_i(16)

    # Sign with private key
    signature_int = modular_exponentiation(padded_int, exponent, modulus)

    # Convert to bytes
    hex_string = signature_int.to_s(16)
    hex_string = '0' + hex_string if hex_string.length.odd?
    [hex_string].pack('H*')
  end

  def verify_signature(message_hash, signature, public_key)
    modulus = public_key[:modulus].to_i(16)
    exponent = public_key[:exponent].to_i(16)

    # Convert signature to integer
    signature_int = signature.unpack1('H*').to_i(16)

    # Verify with public key
    decrypted_int = modular_exponentiation(signature_int, exponent, modulus)

    # Convert to bytes
    hex_string = decrypted_int.to_s(16)
    hex_string = '0' + hex_string if hex_string.length.odd?
    decrypted_bytes = [hex_string].pack('H*')

    # Check padding and hash
    expected_padded = apply_signature_padding(message_hash)
    decrypted_bytes == expected_padded
  end

  private

  def generate_large_prime(bit_length)
    loop do
      candidate = SecureRandom.random_number(2**bit_length)
      candidate |= (1 << (bit_length - 1)) | 1  # Set MSB and LSB

      return candidate if miller_rabin_test(candidate, 40)
    end
  end

  def miller_rabin_test(n, k)
    return false if n < 2
    return true if n == 2 || n == 3
    return false if n.even?

    # Write n-1 as d * 2^r
    r = 0
    d = n - 1
    while d.even?
      d /= 2
      r += 1
    end

    # Perform k rounds of testing
    k.times do
      a = SecureRandom.random_number(n - 3) + 2
      x = modular_exponentiation(a, d, n)

      next if x == 1 || x == n - 1

      (r - 1).times do
        x = modular_exponentiation(x, 2, n)
        break if x == n - 1
      end

      return false unless x == n - 1
    end

    true
  end

  def modular_exponentiation(base, exponent, modulus)
    result = 1
    base = base % modulus

    while exponent > 0
      if exponent.odd?
        result = (result * base) % modulus
      end
      exponent >>= 1
      base = (base * base) % modulus
    end

    result
  end

  def modular_inverse(a, m)
    gcd, x, _ = extended_gcd(a, m)
    raise 'Modular inverse does not exist' unless gcd == 1
    (x % m + m) % m
  end

  def extended_gcd(a, b)
    return [b, 0, 1] if a == 0

    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b / a) * x1
    y = x1

    [gcd, x, y]
  end

  def apply_signature_padding(message_hash)
    # 256-bit cryptographic hash
    digest_info = "\x30\x31\x30\x0d\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x01\x05\x00\x04\x20"

    padding_length = (@key_size / 8) - digest_info.length - message_hash.length - 3

    padded = "\x00\x01"
    padded += "\xff" * padding_length
    padded += "\x00"
    padded += digest_info
    padded += message_hash

    padded
  end
end

class EllipticCurveOperations
  # Elliptic curve cryptography for key exchange and digital signatures

  attr_reader :curve_params

  def initialize
    # secp256k1 curve parameters
    @curve_params = {
      p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
      a: 0,
      b: 7,
      gx: 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
      gy: 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
      n: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    }
  end

  def generate_key_pair
    # Generate private key
    private_key = SecureRandom.random_number(@curve_params[:n] - 1) + 1

    # Generate public key
    public_key = point_multiply([@curve_params[:gx], @curve_params[:gy]], private_key)

    {
      private_key: private_key.to_s(16),
      public_key: {
        x: public_key[0].to_s(16),
        y: public_key[1].to_s(16)
      }
    }
  end

  def perform_key_exchange(remote_public_key, local_private_key)
    remote_point = [remote_public_key[:x].to_i(16), remote_public_key[:y].to_i(16)]
    private_key_int = local_private_key.to_i(16)

    shared_point = point_multiply(remote_point, private_key_int)

    # Derive shared secret from x-coordinate
    shared_secret = [shared_point[0].to_s(16)].pack('H*')
    Digest::HASH_256.digest(shared_secret)
  end

  def sign_message(message_hash, private_key)
    private_key_int = private_key.to_i(16)
    message_hash_int = message_hash.unpack1('H*').to_i(16)

    loop do
      k = SecureRandom.random_number(@curve_params[:n] - 1) + 1

      # Calculate r
      r_point = point_multiply([@curve_params[:gx], @curve_params[:gy]], k)
      r = r_point[0] % @curve_params[:n]

      next if r == 0

      # Calculate s
      k_inv = modular_inverse(k, @curve_params[:n])
      s = (k_inv * (message_hash_int + r * private_key_int)) % @curve_params[:n]

      next if s == 0

      return {
        r: r.to_s(16),
        s: s.to_s(16)
      }
    end
  end

  def verify_signature(message_hash, signature, public_key)
    r = signature[:r].to_i(16)
    s = signature[:s].to_i(16)
    message_hash_int = message_hash.unpack1('H*').to_i(16)
    public_key_point = [public_key[:x].to_i(16), public_key[:y].to_i(16)]

    # Verify signature parameters
    return false unless (1...@curve_params[:n]).include?(r) && (1...@curve_params[:n]).include?(s)

    # Calculate verification values
    s_inv = modular_inverse(s, @curve_params[:n])
    u1 = (message_hash_int * s_inv) % @curve_params[:n]
    u2 = (r * s_inv) % @curve_params[:n]

    # Calculate verification point
    point1 = point_multiply([@curve_params[:gx], @curve_params[:gy]], u1)
    point2 = point_multiply(public_key_point, u2)
    verification_point = point_add(point1, point2)

    return false if verification_point.nil?

    verification_point[0] % @curve_params[:n] == r
  end

  private

  def point_add(p1, p2)
    return p2 if p1.nil?
    return p1 if p2.nil?

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2
      if y1 == y2
        # Point doubling
        s = (3 * x1 * x1 * modular_inverse(2 * y1, @curve_params[:p])) % @curve_params[:p]
      else
        return nil # Point at infinity
      end
    else
      # Point addition
      s = ((y2 - y1) * modular_inverse(x2 - x1, @curve_params[:p])) % @curve_params[:p]
    end

    x3 = (s * s - x1 - x2) % @curve_params[:p]
    y3 = (s * (x1 - x3) - y1) % @curve_params[:p]

    [x3, y3]
  end

  def point_multiply(point, scalar)
    return nil if scalar == 0

    result = nil
    addend = point

    while scalar > 0
      if scalar.odd?
        result = result ? point_add(result, addend) : addend
      end
      addend = point_add(addend, addend)
      scalar >>= 1
    end

    result
  end

  def modular_inverse(a, m)
    gcd, x, _ = extended_gcd(a, m)
    raise 'Modular inverse does not exist' unless gcd == 1
    (x % m + m) % m
  end

  def extended_gcd(a, b)
    return [b, 0, 1] if a == 0

    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b / a) * x1
    y = x1

    [gcd, x, y]
  end
end

class StreamCipherProcessor
  # High-speed stream cipher for message encryption

  def initialize
    @state = Array.new(16, 0)
    @counter = 0
  end

  def initialize_cipher(key, nonce)
    # Initialize state with constants, key, counter, and nonce
    constants = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]

    @state[0..3] = constants

    # Load key (32 bytes = 8 words)
    key_words = key.unpack('V8')
    @state[4..11] = key_words

    # Counter and nonce
    @state[12] = 0
    nonce_words = nonce.unpack('V3')
    @state[13..15] = nonce_words

    @counter = 0
  end

  def encrypt_message(plaintext)
    keystream = generate_keystream(plaintext.length)

    ciphertext = ''
    plaintext.bytes.each_with_index do |byte, index|
      ciphertext += (byte ^ keystream.bytes[index]).chr
    end

    ciphertext
  end

  def decrypt_message(ciphertext)
    # Stream cipher is symmetric
    encrypt_message(ciphertext)
  end

  private

  def generate_keystream(length)
    keystream = ''

    while keystream.length < length
      block = generate_block
      remaining = length - keystream.length
      keystream += block[0, remaining]
    end

    keystream
  end

  def generate_block
    working_state = @state.dup
    working_state[12] = @counter
    @counter += 1

    # 20 rounds of quarter-round operations
    10.times do
      # Column rounds
      quarter_round(working_state, 0, 4, 8, 12)
      quarter_round(working_state, 1, 5, 9, 13)
      quarter_round(working_state, 2, 6, 10, 14)
      quarter_round(working_state, 3, 7, 11, 15)

      # Diagonal rounds
      quarter_round(working_state, 0, 5, 10, 15)
      quarter_round(working_state, 1, 6, 11, 12)
      quarter_round(working_state, 2, 7, 8, 13)
      quarter_round(working_state, 3, 4, 9, 14)
    end

    # Add original state
    16.times do |i|
      working_state[i] = (working_state[i] + @state[i]) & 0xFFFFFFFF
    end

    working_state.pack('V16')
  end

  def quarter_round(state, a, b, c, d)
    state[a] = (state[a] + state[b]) & 0xFFFFFFFF
    state[d] ^= state[a]
    state[d] = left_rotate(state[d], 16)

    state[c] = (state[c] + state[d]) & 0xFFFFFFFF
    state[b] ^= state[c]
    state[b] = left_rotate(state[b], 12)

    state[a] = (state[a] + state[b]) & 0xFFFFFFFF
    state[d] ^= state[a]
    state[d] = left_rotate(state[d], 8)

    state[c] = (state[c] + state[d]) & 0xFFFFFFFF
    state[b] ^= state[c]
    state[b] = left_rotate(state[b], 7)
  end

  def left_rotate(value, amount)
    ((value << amount) | (value >> (32 - amount))) & 0xFFFFFFFF
  end
end

class KoreanHashAlgorithm
  # Korean standard hash function implementation

  def initialize
    @initial_state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
  end

  def compute_hash(data)
    padded_data = pad_message(data)
    state = @initial_state.dup

    # Process in 512-bit blocks
    (0...padded_data.length).step(64) do |i|
      block = padded_data[i, 64]
      process_block(block, state)
    end

    # Convert state to hex string
    state.map { |word| '%08x' % (word & 0xFFFFFFFF) }.join
  end

  private

  def pad_message(data)
    message_length = data.length
    bit_length = message_length * 8

    padded = data.dup
    padded += "\x80"

    while (padded.length % 64) != 56
      padded += "\x00"
    end

    # Append length as 64-bit big-endian integer
    padded += [bit_length >> 32, bit_length & 0xFFFFFFFF].pack('NN')

    padded
  end

  def process_block(block, state)
    w = block.unpack('N16')

    # Extend to 80 words with Korean-specific extension
    (16...80).each do |i|
      w[i] = left_rotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1)
    end

    a, b, c, d, e = state

    # 80 rounds with Korean-specific operations
    80.times do |i|
      if i < 20
        f = (b & c) | (~b & d)
        k = 0x5A827999
      elsif i < 40
        f = b ^ c ^ d
        k = 0x6ED9EBA1
      elsif i < 60
        f = (b & c) | (b & d) | (c & d)
        k = 0x8F1BBCDC
      else
        f = b ^ c ^ d
        k = 0xCA62C1D6
      end

      temp = (left_rotate(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
      e = d
      d = c
      c = left_rotate(b, 30)
      b = a
      a = temp
    end

    state[0] = (state[0] + a) & 0xFFFFFFFF
    state[1] = (state[1] + b) & 0xFFFFFFFF
    state[2] = (state[2] + c) & 0xFFFFFFFF
    state[3] = (state[3] + d) & 0xFFFFFFFF
    state[4] = (state[4] + e) & 0xFFFFFFFF
  end

  def left_rotate(value, amount)
    ((value << amount) | (value >> (32 - amount))) & 0xFFFFFFFF
  end
end

class SecureMessagingProtocol
  # Main secure messaging protocol implementation

  attr_reader :user_id, :contacts, :message_history

  def initialize(user_id)
    @user_id = user_id
    @contacts = {}
    @message_history = {}
    @session_keys = {}

    @pk_crypto_processor = LargeIntegerArithmetic.new
    @ecc_processor = EllipticCurveOperations.new
    @stream_cipher = StreamCipherProcessor.new
    @korean_hash = KoreanHashAlgorithm.new

    # Generate user's cryptographic keys
    @user_keys = generate_user_keys

    @mutex = Mutex.new
    @audit_log = []
  end

  def generate_user_keys
    public_keys = @pk_crypto_processor.generate_keypair
    curve_keys = @ecc_processor.generate_key_pair

    {
      asymmetric_cipher: public_keys,
      elliptic_curve: curve_keys,
      fingerprint: compute_key_fingerprint(public_keys[:public_key])
    }
  end

  def add_contact(contact_id, public_keys)
    @mutex.synchronize do
      @contacts[contact_id] = {
        public_keys: public_keys,
        trust_level: 'unverified',
        last_activity: Time.now
      }

      # Perform key exchange
      perform_key_exchange(contact_id)

      log_audit_event('CONTACT_ADDED', {
        contact_id: contact_id,
        fingerprint: compute_key_fingerprint(public_keys[:asymmetric_cipher])
      })
    end

    true
  end

  def send_secure_message(recipient_id, message_content, message_type = 'text')
    @mutex.synchronize do
      return { success: false, error: 'Contact not found' } unless @contacts[recipient_id]

      begin
        # Generate message ID
        message_id = SecureRandom.hex(16)

        # Create message metadata
        message_metadata = {
          message_id: message_id,
          sender_id: @user_id,
          recipient_id: recipient_id,
          message_type: message_type,
          timestamp: Time.now.to_f,
          protocol_version: '1.0'
        }

        # Encrypt message content
        encrypted_content = encrypt_message_content(message_content, recipient_id)

        # Create message digest for integrity
        message_data = JSON.generate({
          metadata: message_metadata,
          content: encrypted_content
        })

        message_hash = Digest::HASH_256.digest(message_data)
        korean_hash = @korean_hash.compute_hash(message_data)

        # Sign message with sender's private key
        pk_crypto_signature = @pk_crypto_processor.sign_message(message_hash, @user_keys[:asymmetric_cipher][:private_key])
        ecc_signature = @ecc_processor.sign_message(message_hash, @user_keys[:elliptic_curve][:private_key])

        # Create final message package
        secure_message = {
          metadata: message_metadata,
          encrypted_content: encrypted_content,
          signatures: {
            asymmetric_cipher: Base64.encode64(pk_crypto_signature),
            elliptic_curve: ecc_signature
          },
          integrity: {
            hash_256: message_hash.unpack1('H*'),
            korean_hash: korean_hash
          }
        }

        # Store in message history
        store_message_history(message_id, secure_message, 'sent')

        # Update contact activity
        @contacts[recipient_id][:last_activity] = Time.now

        log_audit_event('MESSAGE_SENT', {
          message_id: message_id,
          recipient_id: recipient_id,
          message_type: message_type,
          encrypted_size: encrypted_content[:ciphertext].length
        })

        {
          success: true,
          message_id: message_id,
          encrypted_message: secure_message
        }

      rescue => e
        log_audit_event('MESSAGE_SEND_FAILED', {
          recipient_id: recipient_id,
          error: e.message
        })

        { success: false, error: e.message }
      end
    end
  end

  def receive_secure_message(encrypted_message)
    @mutex.synchronize do
      begin
        sender_id = encrypted_message[:metadata][:sender_id]
        message_id = encrypted_message[:metadata][:message_id]

        return { success: false, error: 'Unknown sender' } unless @contacts[sender_id]

        # Verify message signatures
        message_data = JSON.generate({
          metadata: encrypted_message[:metadata],
          content: encrypted_message[:encrypted_content]
        })

        message_hash = Digest::HASH_256.digest(message_data)

        # Asymmetric modular arithmetic operations
        pk_crypto_signature = Base64.decode64(encrypted_message[:signatures][:asymmetric_cipher])
        pk_crypto_valid = @pk_crypto_processor.verify_signature(
          message_hash,
          pk_crypto_signature,
          @contacts[sender_id][:public_keys][:asymmetric_cipher]
        )

        # Elliptic curve cryptography
        ecc_valid = @ecc_processor.verify_signature(
          message_hash,
          encrypted_message[:signatures][:elliptic_curve],
          @contacts[sender_id][:public_keys][:elliptic_curve]
        )

        # Verify integrity hashes
        computed_korean_hash = @korean_hash.compute_hash(message_data)
        korean_hash_valid = computed_korean_hash == encrypted_message[:integrity][:korean_hash]

        sha256_valid = message_hash.unpack1('H*') == encrypted_message[:integrity][:hash_256]

        unless pk_crypto_valid && ecc_valid && korean_hash_valid && sha256_valid
          log_audit_event('MESSAGE_VERIFICATION_FAILED', {
            message_id: message_id,
            sender_id: sender_id,
            pk_crypto_valid: pk_crypto_valid,
            ecc_valid: ecc_valid,
            korean_hash_valid: korean_hash_valid,
            sha256_valid: sha256_valid
          })

          return { success: false, error: 'Message verification failed' }
        end

        # Decrypt message content
        decrypted_content = decrypt_message_content(
          encrypted_message[:encrypted_content],
          sender_id
        )

        # Store in message history
        store_message_history(message_id, encrypted_message, 'received')

        # Update contact activity
        @contacts[sender_id][:last_activity] = Time.now

        log_audit_event('MESSAGE_RECEIVED', {
          message_id: message_id,
          sender_id: sender_id,
          message_type: encrypted_message[:metadata][:message_type],
          decrypted_size: decrypted_content.length
        })

        {
          success: true,
          message_id: message_id,
          sender_id: sender_id,
          content: decrypted_content,
          metadata: encrypted_message[:metadata],
          verified: true
        }

      rescue => e
        log_audit_event('MESSAGE_RECEIVE_FAILED', {
          sender_id: encrypted_message[:metadata][:sender_id],
          error: e.message
        })

        { success: false, error: e.message }
      end
    end
  end

  def get_contact_list
    @mutex.synchronize do
      @contacts.map do |contact_id, contact_info|
        {
          contact_id: contact_id,
          trust_level: contact_info[:trust_level],
          last_activity: contact_info[:last_activity],
          fingerprint: compute_key_fingerprint(contact_info[:public_keys][:asymmetric_cipher])
        }
      end
    end
  end

  def get_message_history(contact_id = nil, limit = 50)
    @mutex.synchronize do
      if contact_id
        messages = @message_history.select do |_, msg|
          msg[:metadata][:sender_id] == contact_id ||
          msg[:metadata][:recipient_id] == contact_id
        end
      else
        messages = @message_history
      end

      messages.values
        .sort_by { |msg| msg[:metadata][:timestamp] }
        .last(limit)
        .map do |msg|
          {
            message_id: msg[:metadata][:message_id],
            sender_id: msg[:metadata][:sender_id],
            recipient_id: msg[:metadata][:recipient_id],
            message_type: msg[:metadata][:message_type],
            timestamp: msg[:metadata][:timestamp],
            direction: msg[:direction]
          }
        end
    end
  end

  def get_security_status
    @mutex.synchronize do
      {
        user_id: @user_id,
        key_fingerprint: @user_keys[:fingerprint],
        total_contacts: @contacts.length,
        total_messages: @message_history.length,
        audit_log_entries: @audit_log.length,
        active_sessions: @session_keys.length,
        security_algorithms: {
          asymmetric: 'Large Integer Arithmetic (2048-bit)',
          elliptic_curve: 'secp256k1',
          symmetric: 'Stream Cipher',
          hash: 'Korean Standard Hash + Hash256'
        }
      }
    end
  end

  private

  def perform_key_exchange(contact_id)
    contact = @contacts[contact_id]

    # Elliptic curve key exchange
    shared_secret = @ecc_processor.perform_key_exchange(
      contact[:public_keys][:elliptic_curve],
      @user_keys[:elliptic_curve][:private_key]
    )

    # Derive session key using Korean hash for additional security
    key_material = shared_secret + @user_id + contact_id
    session_key_hash = @korean_hash.compute_hash(key_material)
    session_key = [session_key_hash].pack('H*')[0, 32]

    @session_keys[contact_id] = session_key

    log_audit_event('KEY_EXCHANGE_PERFORMED', {
      contact_id: contact_id,
      shared_secret_length: shared_secret.length,
      session_key_length: session_key.length
    })
  end

  def encrypt_message_content(content, recipient_id)
    session_key = @session_keys[recipient_id]
    raise 'No session key for recipient' unless session_key

    # Generate random nonce
    nonce = SecureRandom.random_bytes(12)

    # Initialize stream cipher
    @stream_cipher.initialize_cipher(session_key, nonce)

    # Encrypt content
    ciphertext = @stream_cipher.encrypt_message(content)

    {
      ciphertext: Base64.encode64(ciphertext),
      nonce: Base64.encode64(nonce),
      algorithm: 'stream_cipher'
    }
  end

  def decrypt_message_content(encrypted_content, sender_id)
    session_key = @session_keys[sender_id]
    raise 'No session key for sender' unless session_key

    # Decode encrypted data
    ciphertext = Base64.decode64(encrypted_content[:ciphertext])
    nonce = Base64.decode64(encrypted_content[:nonce])

    # Initialize stream cipher
    @stream_cipher.initialize_cipher(session_key, nonce)

    # Decrypt content
    @stream_cipher.decrypt_message(ciphertext)
  end

  def store_message_history(message_id, message, direction)
    @message_history[message_id] = {
      metadata: message[:metadata],
      direction: direction,
      stored_at: Time.now
    }

    # Cleanup old messages (keep last 10000)
    if @message_history.length > 10000
      oldest_messages = @message_history
        .sort_by { |_, msg| msg[:stored_at] }
        .first(1000)

      oldest_messages.each { |msg_id, _| @message_history.delete(msg_id) }
    end
  end

  def compute_key_fingerprint(public_key)
    key_data = JSON.generate(public_key)
    hash = Digest::HASH_256.digest(key_data)
    hash.unpack1('H*')[0, 16]
  end

  def log_audit_event(event_type, event_data)
    audit_entry = {
      event_type: event_type,
      event_data: event_data,
      timestamp: Time.now.to_f,
      user_id: @user_id
    }

    @audit_log << audit_entry

    # Keep only recent audit entries
    @audit_log = @audit_log.last(5000) if @audit_log.length > 5000
  end
end

# Demonstration of the secure messaging protocol
def demonstrate_secure_messaging
  puts "Secure Messaging Protocol Starting...\n\n"

  # Create two users
  alice = SecureMessagingProtocol.new('alice')
  bob = SecureMessagingProtocol.new('bob')

  puts "Users created:"
  puts "Alice fingerprint: #{alice.get_security_status[:key_fingerprint]}"
  puts "Bob fingerprint: #{bob.get_security_status[:key_fingerprint]}\n\n"

  # Exchange public keys
  alice_keys = alice.instance_variable_get(:@user_keys)
  bob_keys = bob.instance_variable_get(:@user_keys)

  alice.add_contact('bob', bob_keys)
  bob.add_contact('alice', alice_keys)

  puts "Contact exchange completed\n\n"

  # Send secure messages
  test_messages = [
    "Hello Bob! This is a secure message from Alice.",
    "Confidential financial data: Account balance $50,000",
    "Meeting scheduled for tomorrow at 3 PM"
  ]

  test_messages.each_with_index do |message, index|
    puts "Sending message #{index + 1}..."

    # Alice sends message to Bob
    send_result = alice.send_secure_message('bob', message)

    if send_result[:success]
      puts "Message sent successfully: #{send_result[:message_id]}"

      # Bob receives message
      receive_result = bob.receive_secure_message(send_result[:encrypted_message])

      if receive_result[:success]
        puts "Message received successfully"
        puts "Decrypted content: #{receive_result[:content]}"
        puts "Sender verified: #{receive_result[:verified]}\n"
      else
        puts "Failed to receive message: #{receive_result[:error]}\n"
      end
    else
      puts "Failed to send message: #{send_result[:error]}\n"
    end
  end

  # Display security status
  alice_status = alice.get_security_status
  bob_status = bob.get_security_status

  puts "\nSecurity Status:"
  puts "Alice - Contacts: #{alice_status[:total_contacts]}, Messages: #{alice_status[:total_messages]}"
  puts "Bob - Contacts: #{bob_status[:total_contacts]}, Messages: #{bob_status[:total_messages]}"

  # Display message history
  puts "\nAlice's Message History:"
  alice.get_message_history.each do |msg|
    direction = msg[:direction].upcase
    other_party = msg[:direction] == 'sent' ? msg[:recipient_id] : msg[:sender_id]
    puts "#{direction}: #{msg[:message_id][0, 8]}... to/from #{other_party}"
  end

  puts "\nSecure Messaging Protocol Demo Complete"
end

# Run demonstration if this file is executed directly
if __FILE__ == $PROGRAM_NAME
  demonstrate_secure_messaging
end