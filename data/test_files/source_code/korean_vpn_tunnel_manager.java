/**
 * VPN Tunnel Security Manager
 * Implements dual-algorithm encryption for VPN control and data planes.
 * Control plane: Feistel-based block cipher
 * Data plane: Involution-based SPN cipher
 */

import javax.crypto.Cipher;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.SecureRandom;
import java.util.*;

/**
 * Control Plane Security Engine
 * Uses Feistel network structure for control message encryption
 */
class ControlPlaneSecurityEngine {
    private static final int BLOCK_SIZE = 16;
    private static final int ROUND_COUNT = 16;

    private final byte[] masterKey;
    private final List<byte[]> roundKeys;

    public ControlPlaneSecurityEngine(byte[] key) throws Exception {
        if (key.length != 16) {
            throw new IllegalArgumentException("Key must be 128 bits");
        }
        this.masterKey = Arrays.copyOf(key, key.length);
        this.roundKeys = deriveRoundKeys();
    }

    /**
     * Key schedule for Feistel cipher
     */
    private List<byte[]> deriveRoundKeys() {
        List<byte[]> keys = new ArrayList<>();
        byte[] working = Arrays.copyOf(masterKey, masterKey.length);

        // Key constants for round key generation
        int[] constants = {0x9e3779b9, 0x3c6ef373, 0x78dde6e6, 0xf1bbcdcc};

        for (int round = 0; round < ROUND_COUNT; round++) {
            byte[] roundKey = new byte[16];

            // Mix key with round-specific operations
            for (int i = 0; i < 16; i++) {
                int idx = (round * 16 + i) % working.length;
                int constant = constants[i % 4] & 0xff;
                int mixed = (working[idx] & 0xff) ^ constant;

                roundKey[i] = (byte) mixed;
                working[idx] = (byte) ((working[idx] + mixed) & 0xff);
            }

            keys.add(roundKey);
        }

        return keys;
    }

    /**
     * Feistel round function with substitution-permutation
     */
    private byte[] feistelFunction(byte[] halfBlock, byte[] roundKey) {
        byte[] result = new byte[8];

        // Key mixing
        for (int i = 0; i < 8; i++) {
            result[i] = (byte) (halfBlock[i] ^ roundKey[i]);
        }

        // S-box substitution
        for (int i = 0; i < 8; i++) {
            int val = result[i] & 0xff;
            result[i] = (byte) (((val * 31 + 127) & 0xff) ^ 0x63);
        }

        // Permutation
        byte[] permuted = new byte[8];
        int[] permTable = {6, 2, 7, 3, 5, 1, 4, 0};
        for (int i = 0; i < 8; i++) {
            permuted[i] = result[permTable[i]];
        }

        return permuted;
    }

    public byte[] encryptBlock(byte[] plaintext) throws Exception {
        if (plaintext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Invalid block size");
        }

        byte[] left = Arrays.copyOfRange(plaintext, 0, 8);
        byte[] right = Arrays.copyOfRange(plaintext, 8, 16);

        // Feistel rounds
        for (int round = 0; round < ROUND_COUNT; round++) {
            byte[] fOutput = feistelFunction(right, roundKeys.get(round));

            // XOR left half with F output
            byte[] newRight = new byte[8];
            for (int i = 0; i < 8; i++) {
                newRight[i] = (byte) (left[i] ^ fOutput[i]);
            }

            left = right;
            right = newRight;
        }

        // Combine halves (swap at end)
        byte[] ciphertext = new byte[BLOCK_SIZE];
        System.arraycopy(right, 0, ciphertext, 0, 8);
        System.arraycopy(left, 0, ciphertext, 8, 8);

        return ciphertext;
    }

    public byte[] encryptData(byte[] data) throws Exception {
        // PKCS7 padding
        int padLen = BLOCK_SIZE - (data.length % BLOCK_SIZE);
        byte[] padded = new byte[data.length + padLen];
        System.arraycopy(data, 0, padded, 0, data.length);
        Arrays.fill(padded, data.length, padded.length, (byte) padLen);

        // Encrypt blocks
        byte[] encrypted = new byte[padded.length];
        for (int i = 0; i < padded.length; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(padded, i, i + BLOCK_SIZE);
            byte[] encBlock = encryptBlock(block);
            System.arraycopy(encBlock, 0, encrypted, i, BLOCK_SIZE);
        }

        return encrypted;
    }
}

/**
 * Data Plane Security Engine
 * Uses Substitution-Permutation Network with involution property
 */
class DataPlaneSecurityEngine {
    private static final int BLOCK_SIZE = 16;
    private static final int CIPHER_ROUNDS = 12;

    private final byte[] masterKey;
    private final List<byte[]> roundKeys;

    // Dual S-boxes for involution-based transformation
    private static final int[] SBOX_TYPE1 = new int[256];
    private static final int[] SBOX_TYPE2 = new int[256];

    static {
        // Initialize S-boxes with algebraic properties
        for (int i = 0; i < 256; i++) {
            int x = i;

            // Type 1 S-box (involution property)
            x = ((x * 0x63) & 0xff) ^ 0x1f;
            SBOX_TYPE1[i] = x;

            // Type 2 S-box (different transformation)
            x = i;
            x = ((x * 0x97) & 0xff) ^ 0x5b;
            SBOX_TYPE2[i] = x;
        }
    }

    public DataPlaneSecurityEngine(byte[] key) throws Exception {
        if (key.length != 16) {
            throw new IllegalArgumentException("Key must be 128 bits");
        }
        this.masterKey = Arrays.copyOf(key, key.length);
        this.roundKeys = expandKey();
    }

    /**
     * Key expansion for SPN cipher
     */
    private List<byte[]> expandKey() {
        List<byte[]> keys = new ArrayList<>();
        byte[] state = Arrays.copyOf(masterKey, masterKey.length);

        for (int round = 0; round <= CIPHER_ROUNDS; round++) {
            byte[] roundKey = new byte[16];

            // Rotate state
            byte first = state[0];
            for (int i = 0; i < 15; i++) {
                state[i] = (byte) SBOX_TYPE1[state[i + 1] & 0xff];
            }
            state[15] = (byte) SBOX_TYPE1[first & 0xff];

            // Mix with round constant
            state[0] ^= (byte) (round * 0x13);
            state[1] ^= (byte) (round * 0x1f);

            System.arraycopy(state, 0, roundKey, 0, 16);
            keys.add(roundKey);
        }

        return keys;
    }

    /**
     * Substitution layer with dual S-boxes
     */
    private void substitutionLayer(byte[] state) {
        for (int i = 0; i < BLOCK_SIZE; i++) {
            int val = state[i] & 0xff;
            // Alternate S-box types
            state[i] = (byte) ((i % 2 == 0) ? SBOX_TYPE1[val] : SBOX_TYPE2[val]);
        }
    }

    /**
     * Diffusion layer using MDS matrix
     */
    private void diffusionLayer(byte[] state) {
        byte[] temp = new byte[BLOCK_SIZE];

        // 4x4 MDS matrix multiplication in GF(2^8)
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                int sum = 0;
                for (int k = 0; k < 4; k++) {
                    int matrixVal = getMDSElement(row, k);
                    int stateVal = state[k * 4 + col] & 0xff;
                    sum ^= multiplyGF256(matrixVal, stateVal);
                }
                temp[row * 4 + col] = (byte) sum;
            }
        }

        System.arraycopy(temp, 0, state, 0, BLOCK_SIZE);
    }

    private int getMDSElement(int row, int col) {
        int[][] matrix = {
            {2, 3, 1, 1},
            {1, 2, 3, 1},
            {1, 1, 2, 3},
            {3, 1, 1, 2}
        };
        return matrix[row][col];
    }

    private int multiplyGF256(int a, int b) {
        int result = 0;
        int poly = 0x11b;

        for (int i = 0; i < 8; i++) {
            if ((b & 1) != 0) {
                result ^= a;
            }
            boolean highBit = (a & 0x80) != 0;
            a <<= 1;
            if (highBit) {
                a ^= poly;
            }
            b >>= 1;
        }

        return result & 0xff;
    }

    public byte[] encryptBlock(byte[] plaintext) throws Exception {
        if (plaintext.length != BLOCK_SIZE) {
            throw new IllegalArgumentException("Invalid block size");
        }

        byte[] state = Arrays.copyOf(plaintext, BLOCK_SIZE);

        // Initial key whitening
        addRoundKey(state, roundKeys.get(0));

        // Main rounds
        for (int round = 1; round < CIPHER_ROUNDS; round++) {
            substitutionLayer(state);
            diffusionLayer(state);
            addRoundKey(state, roundKeys.get(round));
        }

        // Final round (no diffusion)
        substitutionLayer(state);
        addRoundKey(state, roundKeys.get(CIPHER_ROUNDS));

        return state;
    }

    private void addRoundKey(byte[] state, byte[] roundKey) {
        for (int i = 0; i < BLOCK_SIZE; i++) {
            state[i] ^= roundKey[i];
        }
    }

    public byte[] encryptData(byte[] data) throws Exception {
        // PKCS7 padding
        int padLen = BLOCK_SIZE - (data.length % BLOCK_SIZE);
        byte[] padded = new byte[data.length + padLen];
        System.arraycopy(data, 0, padded, 0, data.length);
        Arrays.fill(padded, data.length, padded.length, (byte) padLen);

        // Encrypt blocks
        byte[] encrypted = new byte[padded.length];
        for (int i = 0; i < padded.length; i += BLOCK_SIZE) {
            byte[] block = Arrays.copyOfRange(padded, i, i + BLOCK_SIZE);
            byte[] encBlock = encryptBlock(block);
            System.arraycopy(encBlock, 0, encrypted, i, BLOCK_SIZE);
        }

        return encrypted;
    }
}

/**
 * VPN Tunnel Session
 */
class VPNTunnelSession {
    private final String sessionId;
    private final String clientIp;
    private final String serverIp;
    private final long establishedTime;
    private long lastActivityTime;
    private long bytesTransferred;

    public VPNTunnelSession(String sessionId, String clientIp, String serverIp) {
        this.sessionId = sessionId;
        this.clientIp = clientIp;
        this.serverIp = serverIp;
        this.establishedTime = System.currentTimeMillis();
        this.lastActivityTime = this.establishedTime;
        this.bytesTransferred = 0;
    }

    public void updateActivity(int bytes) {
        this.lastActivityTime = System.currentTimeMillis();
        this.bytesTransferred += bytes;
    }

    public String getSessionId() { return sessionId; }
    public String getClientIp() { return clientIp; }
    public long getBytesTransferred() { return bytesTransferred; }
    public long getDuration() {
        return (System.currentTimeMillis() - establishedTime) / 1000;
    }
}

/**
 * Enterprise VPN Tunnel Manager
 * Manages secure VPN connections with dual-algorithm encryption
 */
public class VPNTunnelSecurityManager {
    private final ControlPlaneSecurityEngine controlPlaneEngine;
    private final DataPlaneSecurityEngine dataPlaneEngine;
    private final Map<String, VPNTunnelSession> activeSessions;
    private final SecureRandom random;

    public VPNTunnelSecurityManager(byte[] controlKey, byte[] dataKey) throws Exception {
        this.controlPlaneEngine = new ControlPlaneSecurityEngine(controlKey);
        this.dataPlaneEngine = new DataPlaneSecurityEngine(dataKey);
        this.activeSessions = new HashMap<>();
        this.random = new SecureRandom();
    }

    /**
     * Establish VPN tunnel with client
     */
    public VPNTunnelSession establishTunnel(String clientIp, String serverIp) throws Exception {
        // Generate session ID
        byte[] sessionIdBytes = new byte[16];
        random.nextBytes(sessionIdBytes);
        String sessionId = bytesToHex(sessionIdBytes);

        // Create session
        VPNTunnelSession session = new VPNTunnelSession(sessionId, clientIp, serverIp);

        // Encrypt session establishment message with control plane
        String handshake = String.format("SESSION_INIT|%s|%s|%s|%d",
            sessionId, clientIp, serverIp, System.currentTimeMillis());

        byte[] encryptedHandshake = controlPlaneEngine.encryptData(handshake.getBytes());

        System.out.println("VPN Tunnel Established:");
        System.out.println("  Session ID: " + sessionId);
        System.out.println("  Client: " + clientIp);
        System.out.println("  Server: " + serverIp);
        System.out.println("  Handshake encrypted: " + encryptedHandshake.length + " bytes");

        activeSessions.put(sessionId, session);
        return session;
    }

    /**
     * Send control message through VPN tunnel
     */
    public byte[] sendControlMessage(String sessionId, String message) throws Exception {
        VPNTunnelSession session = activeSessions.get(sessionId);
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID");
        }

        // Encrypt with control plane cipher
        byte[] encrypted = controlPlaneEngine.encryptData(message.getBytes());
        session.updateActivity(encrypted.length);

        System.out.println("Control message sent: " + message.length() + " bytes -> " +
                         encrypted.length + " bytes encrypted");

        return encrypted;
    }

    /**
     * Send data through VPN tunnel
     */
    public byte[] sendData(String sessionId, byte[] data) throws Exception {
        VPNTunnelSession session = activeSessions.get(sessionId);
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID");
        }

        // Encrypt with data plane cipher
        byte[] encrypted = dataPlaneEngine.encryptData(data);
        session.updateActivity(encrypted.length);

        System.out.println("Data sent: " + data.length + " bytes -> " +
                         encrypted.length + " bytes encrypted");

        return encrypted;
    }

    /**
     * Get session statistics
     */
    public void printSessionStats(String sessionId) {
        VPNTunnelSession session = activeSessions.get(sessionId);
        if (session == null) {
            System.out.println("Session not found: " + sessionId);
            return;
        }

        System.out.println("\nVPN Session Statistics:");
        System.out.println("  Session ID: " + session.getSessionId());
        System.out.println("  Client IP: " + session.getClientIp());
        System.out.println("  Duration: " + session.getDuration() + " seconds");
        System.out.println("  Data transferred: " + session.getBytesTransferred() + " bytes");
    }

    /**
     * Terminate VPN tunnel
     */
    public void terminateTunnel(String sessionId) throws Exception {
        VPNTunnelSession session = activeSessions.get(sessionId);
        if (session == null) {
            return;
        }

        // Send termination message
        String terminateMsg = "SESSION_TERMINATE|" + sessionId;
        controlPlaneEngine.encryptData(terminateMsg.getBytes());

        activeSessions.remove(sessionId);
        System.out.println("VPN tunnel terminated: " + sessionId);
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }

    // Example usage
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Enterprise VPN Tunnel Security Manager");
        System.out.println("Dual-Algorithm Encryption System");
        System.out.println("=".repeat(60));
        System.out.println();

        try {
            // Initialize keys
            byte[] controlKey = new byte[16];
            byte[] dataKey = new byte[16];

            for (int i = 0; i < 16; i++) {
                controlKey[i] = (byte) (i * 0x11);
                dataKey[i] = (byte) ((15 - i) * 0x11);
            }

            // Create VPN manager
            VPNTunnelSecurityManager vpnManager =
                new VPNTunnelSecurityManager(controlKey, dataKey);

            // Establish tunnel
            System.out.println("--- Establishing VPN Tunnel ---");
            VPNTunnelSession session = vpnManager.establishTunnel(
                "192.168.1.100",
                "10.0.0.1"
            );
            System.out.println();

            // Send control messages
            System.out.println("--- Sending Control Messages ---");
            vpnManager.sendControlMessage(session.getSessionId(),
                "KEEPALIVE|timestamp=" + System.currentTimeMillis());

            vpnManager.sendControlMessage(session.getSessionId(),
                "ROUTE_UPDATE|10.0.0.0/8|gateway=10.0.0.1");
            System.out.println();

            // Send data
            System.out.println("--- Sending Data Packets ---");
            String userData = "GET /api/secure/data HTTP/1.1\r\n" +
                            "Host: internal.company.com\r\n" +
                            "Authorization: Bearer secret_token\r\n\r\n";

            vpnManager.sendData(session.getSessionId(), userData.getBytes());

            byte[] largeData = new byte[1024];
            new SecureRandom().nextBytes(largeData);
            vpnManager.sendData(session.getSessionId(), largeData);
            System.out.println();

            // Print statistics
            vpnManager.printSessionStats(session.getSessionId());
            System.out.println();

            // Terminate tunnel
            System.out.println("--- Terminating Tunnel ---");
            vpnManager.terminateTunnel(session.getSessionId());

            System.out.println();
            System.out.println("=".repeat(60));
            System.out.println("VPN tunnel lifecycle completed successfully");
            System.out.println("=".repeat(60));

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
