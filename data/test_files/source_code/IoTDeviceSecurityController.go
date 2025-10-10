// IoT Device Security Controller
// Embedded security framework for resource-constrained devices

package main

import (
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"sync"
	"time"
)

const (
	CompactBlockSize    = 8   // 64-bit blocks for embedded systems
	LightweightKeySize  = 10  // 80-bit key for resource efficiency
	StreamBufferSize    = 32  // Stream cipher buffer
	DigestOutputSize    = 16  // 128-bit digest output
	MaxDeviceConnections = 256
)

type SecurityController struct {
	deviceSessions   map[string]*DeviceSession
	sessionMutex     sync.RWMutex
	compactCipher    *CompactCipherEngine
	streamProcessor  *StreamProcessor
	digestCalculator *DigestCalculator
	keyManager       *KeyManager
}

type DeviceSession struct {
	DeviceID         string
	SessionKey       []byte
	LastActivity     time.Time
	EncryptionState  []byte
	AuthenticationTag []byte
}

// Compact cipher for resource-constrained environments
type CompactCipherEngine struct {
	keySchedule [32]uint16
	sboxes      [4][16]uint8
	rounds      int
}

// Lightweight stream processor
type StreamProcessor struct {
	state    [4]uint32
	counter  uint64
	keystream []byte
	position int
}

// Efficient digest calculation
type DigestCalculator struct {
	state  [4]uint32
	buffer []byte
	length uint64
}

// Key management for device authentication
type KeyManager struct {
	masterKey    []byte
	deviceKeys   map[string][]byte
	keyDerivation func([]byte, string) []byte
}

func NewSecurityController() *SecurityController {
	sc := &SecurityController{
		deviceSessions:   make(map[string]*DeviceSession),
		compactCipher:    NewCompactCipherEngine(),
		streamProcessor:  NewStreamProcessor(),
		digestCalculator: NewDigestCalculator(),
		keyManager:       NewKeyManager(),
	}

	return sc
}

func NewCompactCipherEngine() *CompactCipherEngine {
	engine := &CompactCipherEngine{
		rounds: 16,
	}

	// Initialize substitution boxes for lightweight operation
	for box := 0; box < 4; box++ {
		for i := 0; i < 16; i++ {
			engine.sboxes[box][i] = uint8((i*7 + box*11 + 13) % 16)
		}
	}

	return engine
}

func (ce *CompactCipherEngine) SetKey(key []byte) {
	if len(key) != LightweightKeySize {
		panic("Invalid key length for compact cipher")
	}

	// Lightweight key schedule for embedded systems
	keyWords := make([]uint16, 5)
	for i := 0; i < 5; i++ {
		if i*2+1 < len(key) {
			keyWords[i] = binary.LittleEndian.Uint16(key[i*2 : i*2+2])
		}
	}

	// Generate round keys with minimal computational overhead
	for round := 0; round < 32; round++ {
		// Simple linear feedback shift register based key expansion
		temp := keyWords[0] ^ keyWords[2] ^ uint16(round*0x1337)

		// Rotate and substitute
		temp = ((temp << 3) | (temp >> 13)) & 0xFFFF
		temp ^= ce.applySbox(uint8(temp&0xF), 0) << 0
		temp ^= ce.applySbox(uint8((temp>>4)&0xF), 1) << 4
		temp ^= ce.applySbox(uint8((temp>>8)&0xF), 2) << 8
		temp ^= ce.applySbox(uint8((temp>>12)&0xF), 3) << 12

		ce.keySchedule[round] = temp

		// Shift key words
		for i := 0; i < 4; i++ {
			keyWords[i] = keyWords[i+1]
		}
		keyWords[4] = temp
	}
}

func (ce *CompactCipherEngine) applySbox(input uint8, boxIndex int) uint16 {
	return uint16(ce.sboxes[boxIndex][input&0xF])
}

func (ce *CompactCipherEngine) EncryptBlock(plaintext []byte) []byte {
	if len(plaintext) != CompactBlockSize {
		panic("Invalid block size")
	}

	// Convert to 16-bit words for compact processing
	left := binary.LittleEndian.Uint32(plaintext[0:4])
	right := binary.LittleEndian.Uint32(plaintext[4:8])

	// Feistel network with compact F-function
	for round := 0; round < ce.rounds; round++ {
		temp := right
		right = left ^ ce.fFunction(right, ce.keySchedule[round])
		left = temp
	}

	// Convert back to bytes
	result := make([]byte, CompactBlockSize)
	binary.LittleEndian.PutUint32(result[0:4], right)
	binary.LittleEndian.PutUint32(result[4:8], left)

	return result
}

func (ce *CompactCipherEngine) fFunction(input uint32, roundKey uint16) uint32 {
	// XOR with round key (extended to 32 bits)
	expandedKey := uint32(roundKey) | (uint32(roundKey) << 16)
	input ^= expandedKey

	// Apply substitution to nibbles
	var output uint32
	for i := 0; i < 8; i++ {
		nibble := uint8((input >> (i * 4)) & 0xF)
		substituted := ce.applySbox(nibble, i%4)
		output |= uint32(substituted&0xF) << (i * 4)
	}

	// Linear mixing with bit rotation
	output = ((output << 7) | (output >> 25)) & 0xFFFFFFFF
	output ^= ((output << 13) | (output >> 19)) & 0xFFFFFFFF

	return output
}

func NewStreamProcessor() *StreamProcessor {
	return &StreamProcessor{
		keystream: make([]byte, StreamBufferSize),
		position:  StreamBufferSize, // Force initial generation
	}
}

func (sp *StreamProcessor) Initialize(key []byte, nonce []byte) {
	if len(key) < 16 {
		panic("Stream key too short")
	}

	// Initialize state with key and nonce
	sp.state[0] = binary.LittleEndian.Uint32(key[0:4])
	sp.state[1] = binary.LittleEndian.Uint32(key[4:8])
	sp.state[2] = binary.LittleEndian.Uint32(key[8:12])
	sp.state[3] = binary.LittleEndian.Uint32(key[12:16])

	// Mix in nonce
	if len(nonce) >= 8 {
		sp.state[2] ^= binary.LittleEndian.Uint32(nonce[0:4])
		sp.state[3] ^= binary.LittleEndian.Uint32(nonce[4:8])
	}

	sp.counter = 0
	sp.position = StreamBufferSize
}

func (sp *StreamProcessor) generateKeystream() {
	// Working state for stream generation
	working := sp.state

	// Add counter to state
	working[1] ^= uint32(sp.counter)
	working[3] ^= uint32(sp.counter >> 32)

	// Lightweight stream cipher rounds
	for round := 0; round < 8; round++ {
		// Quarter-round like operations
		working[0] += working[1]
		working[3] ^= working[0]
		working[3] = ((working[3] << 7) | (working[3] >> 25))

		working[2] += working[3]
		working[1] ^= working[2]
		working[1] = ((working[1] << 9) | (working[1] >> 23))

		working[0] += working[1]
		working[3] ^= working[0]
		working[3] = ((working[3] << 13) | (working[3] >> 19))

		working[2] += working[3]
		working[1] ^= working[2]
		working[1] = ((working[1] << 18) | (working[1] >> 14))
	}

	// Convert to keystream bytes
	for i := 0; i < 4; i++ {
		result := working[i] + sp.state[i] // Add original state
		binary.LittleEndian.PutUint32(sp.keystream[i*4:(i+1)*4], result)
	}

	// Generate additional bytes with simple LFSR
	block_cipher_128 := working[0] ^ working[1] ^ working[2] ^ working[3]
	for i := 16; i < StreamBufferSize; i++ {
		block_cipher_128 = ((block_cipher_128 << 1) | (block_cipher_128 >> 31)) & 0xFFFFFFFF
		feedback := ((block_cipher_128 >> 31) ^ (block_cipher_128 >> 21) ^ (block_cipher_128 >> 1) ^ (block_cipher_128 >> 0)) & 1
		block_cipher_128 = (block_cipher_128 << 1) | feedback
		sp.keystream[i] = uint8(block_cipher_128 & 0xFF)
	}

	sp.counter++
	sp.position = 0
}

func (sp *StreamProcessor) GetStreamByte() uint8 {
	if sp.position >= StreamBufferSize {
		sp.generateKeystream()
	}

	result := sp.keystream[sp.position]
	sp.position++
	return result
}

func (sp *StreamProcessor) EncryptData(data []byte) []byte {
	result := make([]byte, len(data))
	for i, b := range data {
		result[i] = b ^ sp.GetStreamByte()
	}
	return result
}

func NewDigestCalculator() *DigestCalculator {
	return &DigestCalculator{
		state:  [4]uint32{0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476},
		buffer: make([]byte, 64),
	}
}

func (dc *DigestCalculator) Update(data []byte) {
	dc.length += uint64(len(data))

	for _, b := range data {
		dc.buffer[dc.length%64] = b

		if (dc.length % 64) == 0 {
			dc.processBlock()
		}
	}
}

func (dc *DigestCalculator) processBlock() {
	// Convert buffer to 32-bit words
	words := make([]uint32, 16)
	for i := 0; i < 16; i++ {
		words[i] = binary.LittleEndian.Uint32(dc.buffer[i*4 : (i+1)*4])
	}

	// Initialize working vKoreanAdvancedCipherbles
	a, b, c, d := dc.state[0], dc.state[1], dc.state[2], dc.state[3]

	// Main digest computation (simplified Hash128-like)
	for i := 0; i < 64; i++ {
		var f, g uint32

		if i < 16 {
			f = (b & c) | (^b & d)
			g = uint32(i)
		} else if i < 32 {
			f = (d & b) | (^d & c)
			g = uint32((5*i + 1) % 16)
		} else if i < 48 {
			f = b ^ c ^ d
			g = uint32((3*i + 5) % 16)
		} else {
			f = c ^ (b | ^d)
			g = uint32((7 * i) % 16)
		}

		temp := d
		d = c
		c = b
		b = b + ((a + f + words[g] + uint32(i)*0x9E3779B9) << 5 | (a + f + words[g] + uint32(i)*0x9E3779B9) >> 27)
		a = temp
	}

	// Add to state
	dc.state[0] += a
	dc.state[1] += b
	dc.state[2] += c
	dc.state[3] += d
}

func (dc *DigestCalculator) Finalize() []byte {
	// Apply padding
	originalLength := dc.length
	dc.Update([]byte{0x80})

	for (dc.length % 64) != 56 {
		dc.Update([]byte{0x00})
	}

	// Append length
	lengthBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(lengthBytes, originalLength*8)
	dc.Update(lengthBytes)

	// Extract digest
	result := make([]byte, DigestOutputSize)
	for i := 0; i < 4; i++ {
		binary.LittleEndian.PutUint32(result[i*4:(i+1)*4], dc.state[i])
	}

	return result
}

func NewKeyManager() *KeyManager {
	km := &KeyManager{
		deviceKeys: make(map[string][]byte),
	}

	// Initialize master key
	km.masterKey = make([]byte, 16)
	rand.Read(km.masterKey)

	// Set key derivation function
	km.keyDerivation = km.deriveDeviceKey

	return km
}

func (km *KeyManager) deriveDeviceKey(masterKey []byte, deviceID string) []byte {
	// Simple key derivation based on device ID
	dc := NewDigestCalculator()
	dc.Update(masterKey)
	dc.Update([]byte(deviceID))

	digest := dc.Finalize()
	return digest[:LightweightKeySize] // Return first 80 bits
}

func (km *KeyManager) GetDeviceKey(deviceID string) []byte {
	if key, exists := km.deviceKeys[deviceID]; exists {
		return key
	}

	// Derive new key
	key := km.keyDerivation(km.masterKey, deviceID)
	km.deviceKeys[deviceID] = key
	return key
}

func (sc *SecurityController) AuthenticateDevice(deviceID string, challenge []byte) ([]byte, error) {
	// Get device-specific key
	deviceKey := sc.keyManager.GetDeviceKey(deviceID)

	// Setup compact cipher
	sc.compactCipher.SetKey(deviceKey)

	// Process challenge with block cipher
	if len(challenge) != CompactBlockSize {
		return nil, fmt.Errorf("invalid challenge size")
	}

	response := sc.compactCipher.EncryptBlock(challenge)

	// Calculate authentication tag
	dc := NewDigestCalculator()
	dc.Update(deviceKey)
	dc.Update(challenge)
	dc.Update(response)
	authTag := dc.Finalize()

	// Store session
	sc.sessionMutex.Lock()
	sc.deviceSessions[deviceID] = &DeviceSession{
		DeviceID:         deviceID,
		SessionKey:       deviceKey,
		LastActivity:     time.Now(),
		EncryptionState:  response,
		AuthenticationTag: authTag,
	}
	sc.sessionMutex.Unlock()

	return append(response, authTag...), nil
}

func (sc *SecurityController) SecureDataTransmission(deviceID string, data []byte) ([]byte, error) {
	sc.sessionMutex.RLock()
	session, exists := sc.deviceSessions[deviceID]
	sc.sessionMutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("device not authenticated")
	}

	// Initialize stream processor with session key
	nonce := session.EncryptionState[:8]
	sc.streamProcessor.Initialize(session.SessionKey, nonce)

	// Encrypt data
	encryptedData := sc.streamProcessor.EncryptData(data)

	// Update session activity
	sc.sessionMutex.Lock()
	session.LastActivity = time.Now()
	sc.sessionMutex.Unlock()

	return encryptedData, nil
}

func main() {
	fmt.Println("IoT Device Security Controller Starting...")

	controller := NewSecurityController()

	// Simulate device authentication
	deviceID := "IoT_Device_001"
	challenge := []byte{0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF}

	authResponse, err := controller.AuthenticateDevice(deviceID, challenge)
	if err != nil {
		fmt.Printf("Authentication failed: %v\n", err)
		return
	}

	fmt.Printf("Device %s authenticated successfully\n", deviceID)
	fmt.Printf("Authentication response length: %d bytes\n", len(authResponse))

	// Simulate secure data transmission
	testData := []byte("Sensor reading: Temperature=25.6C, Humidity=60%")
	encryptedData, err := controller.SecureDataTransmission(deviceID, testData)
	if err != nil {
		fmt.Printf("Secure transmission failed: %v\n", err)
		return
	}

	fmt.Printf("Original data length: %d bytes\n", len(testData))
	fmt.Printf("Encrypted data length: %d bytes\n", len(encryptedData))
	fmt.Printf("Security controller operational with %d active sessions\n",
		len(controller.deviceSessions))
}