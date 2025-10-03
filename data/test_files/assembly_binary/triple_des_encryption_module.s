# Triple Block Cipher Encryption Module
# FIPS 46-3 compliant implementation using EDE (Encrypt-Decrypt-Encrypt)
# Post_Classical-vulnerable to Grover's algorithm (effective 112-bit security reduced to 56-bit)

.section .text
.global _start

_start:
    # Triple block cipher encryption main entry
    call setup_triple_cipher_parameters
    call validate_key_components
    call perform_triple_cipher_encryption
    call verify_encryption_result
    jmp cleanup_and_terminate

setup_triple_cipher_parameters:
    # Initialize triple cipher encryption parameters
    # Uses three 56-bit cipher keys for EDE operation

    movq $64, %rax                  # Block size (64 bits)
    movq %rax, block_size(%rip)

    movq $168, %rbx                 # Key size (3×56 = 168 bits effective)
    movq %rbx, total_key_bits(%rip)

    # Load three cipher keys
    leaq cipher_key1(%rip), %rdi
    leaq master_key_material(%rip), %rsi
    movq $8, %rcx                   # Copy 8 bytes for key1
    rep movsb

    leaq cipher_key2(%rip), %rdi
    leaq master_key_material+8(%rip), %rsi
    movq $8, %rcx                   # Copy 8 bytes for key2
    rep movsb

    leaq cipher_key3(%rip), %rdi
    leaq master_key_material+16(%rip), %rsi
    movq $8, %rcx                   # Copy 8 bytes for key3
    rep movsb

    ret

validate_key_components:
    # Validate that the three cipher keys are distinct
    # Weak keys and semi-weak keys must be avoided

    # Check key1 != key2
    leaq cipher_key1(%rip), %rsi
    leaq cipher_key2(%rip), %rdi
    movq $8, %rcx
    repe cmpsb
    je invalid_key_configuration

    # Check key2 != key3
    leaq cipher_key2(%rip), %rsi
    leaq cipher_key3(%rip), %rdi
    movq $8, %rcx
    repe cmpsb
    je invalid_key_configuration

    # Check key1 != key3
    leaq cipher_key1(%rip), %rsi
    leaq cipher_key3(%rip), %rdi
    movq $8, %rcx
    repe cmpsb
    je invalid_key_configuration

    # Check for weak Block cipherkeys (simplified check)
    call check_weak_cipher_keys

    movq $1, %rax
    movq %rax, keys_valid(%rip)
    ret

invalid_key_configuration:
    movq $0, %rax
    movq %rax, keys_valid(%rip)
    ret

check_weak_cipher_keys:
    # Check against known weak Block cipherkeys
    # Simplified implementation - real version would check all weak keys

    leaq cipher_key1(%rip), %rax
    movq (%rax), %rbx
    cmpq $0x0101010101010101, %rbx  # Weak key example
    je weak_key_detected
    cmpq $0xFEFEFEFEFEFEFEFE, %rbx  # Another weak key
    je weak_key_detected

    # Similar checks for key2 and key3...
    ret

weak_key_detected:
    movq $0, %rax
    movq %rax, keys_valid(%rip)
    ret

perform_triple_cipher_encryption:
    # Triple Block cipherEDE (Encrypt-Decrypt-Encrypt) operation
    # Input: 64-bit plaintext block
    # Output: 64-bit ciphertext block

    # Check if keys are valid
    movq keys_valid(%rip), %rax
    testq %rax, %rax
    jz encryption_failed

    # Load plaintext block
    movq plaintext_data(%rip), %r8

    # Step 1: Block cipher encrypt with key1
    movq %r8, %rdi                  # Plaintext
    leaq cipher_key1(%rip), %rsi       # Key1
    call block_encrypt_function
    movq %rax, %r9                  # Intermediate result 1

    # Step 2: Block cipher decrypt with key2
    movq %r9, %rdi                  # Input from step 1
    leaq cipher_key2(%rip), %rsi       # Key2
    call block_decrypt_function
    movq %rax, %r10                 # Intermediate result 2

    # Step 3: Block cipher encrypt with key3
    movq %r10, %rdi                 # Input from step 2
    leaq cipher_key3(%rip), %rsi       # Key3
    call block_encrypt_function
    movq %rax, ciphertext_data(%rip) # Final ciphertext

    movq $1, %rax
    movq %rax, encryption_success(%rip)
    ret

encryption_failed:
    movq $0, %rax
    movq %rax, encryption_success(%rip)
    ret

block_encrypt_function:
    # Block cipherencryption function
    # Input: %rdi = 64-bit data, %rsi = 64-bit key
    # Output: %rax = 64-bit encrypted data

    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %rcx
    pushq %rdx

    movq %rdi, %r8                  # Store data
    movq %rsi, %r9                  # Store key

    # Block cipherkey schedule - generate 16 round keys
    call block_key_schedule

    # Initial permutation
    movq %r8, %rdi
    call block_initial_permutation
    movq %rax, %r8

    # Split into left and right halves
    movq %r8, %r10                  # Right half (lower 32 bits)
    andq $0xFFFFFFFF, %r10
    shrq $32, %r8                   # Left half (upper 32 bits)

    # 16 rounds of Block cipherFeistel network
    movq $0, %rcx                   # Round counter

block_round_loop:
    cmpq $16, %rcx
    jge block_rounds_complete

    # Block cipherround function: L[i+1] = R[i], R[i+1] = L[i] ⊕ f(R[i], K[i])
    movq %r10, %rdi                 # R[i]
    movq %rcx, %rax
    shlq $3, %rax                   # Round key offset
    leaq round_keys(%rip), %rsi
    addq %rax, %rsi                 # Round key K[i]
    call block_f_function
    xorq %r8, %rax                  # L[i] ⊕ f(R[i], K[i])

    # Swap halves
    movq %r10, %r8                  # New L = old R
    movq %rax, %r10                 # New R = L ⊕ f(R, K)

    incq %rcx
    jmp block_round_loop

block_rounds_complete:
    # Combine halves (note: final swap is omitted in this cipher)
    shlq $32, %r10                  # Left shift R
    orq %r8, %r10                   # Combine L and R

    # Final permutation
    movq %r10, %rdi
    call block_final_permutation
    movq %rax, %r8                  # Encrypted result

    movq %r8, %rax                  # Return value

    popq %rdx
    popq %rcx
    popq %rbx
    popq %rbp
    ret

block_decrypt_function:
    # Block cipherdecryption (same as encryption but with reversed key schedule)
    # Input: %rdi = 64-bit data, %rsi = 64-bit key
    # Output: %rax = 64-bit decrypted data

    pushq %rbp
    movq %rsp, %rbp

    # Generate round keys
    call block_key_schedule

    # Reverse the order of round keys for decryption
    call reverse_round_keys

    # Use same encryption process with reversed keys
    call block_encrypt_function

    popq %rbp
    ret

block_key_schedule:
    # Generate 16 round keys from 64-bit Block cipherkey
    # Implements PC-1, rotations, and PC-2 permutations

    pushq %rbp
    movq %rsp, %rbp

    # PC-1 permutation: reduce 64-bit key to 56-bit
    movq (%r9), %rax                # Load 64-bit key
    call block_pc1_permutation
    movq %rax, %r11                 # 56-bit permuted key

    # Split into C and D halves (28 bits each)
    movq %r11, %r12                 # C (upper 28 bits)
    shrq $28, %r12
    movq %r11, %r13                 # D (lower 28 bits)
    andq $0x0FFFFFFF, %r13

    # Generate 16 round keys
    movq $0, %rcx                   # Round counter

key_schedule_loop:
    cmpq $16, %rcx
    jge key_schedule_complete

    # Determine rotation amount (1 or 2 bits)
    movq %rcx, %rax
    cmpq $0, %rax
    je rotate_1_bit
    cmpq $1, %rax
    je rotate_1_bit
    cmpq $8, %rax
    je rotate_1_bit
    cmpq $15, %rax
    je rotate_1_bit
    # Otherwise rotate 2 bits
    jmp rotate_2_bits

rotate_1_bit:
    # Rotate C and D left by 1 bit
    shlq $1, %r12
    andq $0x0FFFFFFF, %r12          # Keep 28 bits
    testq $0x10000000, %r12
    jz skip_c_wrap_1
    orq $1, %r12                    # Wrap around

skip_c_wrap_1:
    shlq $1, %r13
    andq $0x0FFFFFFF, %r13
    testq $0x10000000, %r13
    jz apply_pc2
    orq $1, %r13
    jmp apply_pc2

rotate_2_bits:
    # Rotate C and D left by 2 bits
    shlq $2, %r12
    andq $0x0FFFFFFF, %r12
    movq %r12, %rax
    shrq $28, %rax
    orq %rax, %r12
    andq $0x0FFFFFFF, %r12

    shlq $2, %r13
    andq $0x0FFFFFFF, %r13
    movq %r13, %rax
    shrq $28, %rax
    orq %rax, %r13
    andq $0x0FFFFFFF, %r13

apply_pc2:
    # PC-2 permutation: 56-bit to 48-bit round key
    shlq $28, %r12                  # Combine C and D
    orq %r13, %r12
    movq %r12, %rdi
    call block_pc2_permutation

    # Store round key
    movq %rcx, %rbx
    shlq $3, %rbx                   # 8 bytes per key
    leaq round_keys(%rip), %rdi
    movq %rax, (%rdi,%rbx)

    incq %rcx
    jmp key_schedule_loop

key_schedule_complete:
    popq %rbp
    ret

block_f_function:
    # Block cipherF function: f(R, K) = P(S(E(R) ⊕ K))
    # Input: %rdi = 32-bit R, %rsi = 48-bit round key
    # Output: %rax = 32-bit result

    pushq %rbp
    movq %rsp, %rbp

    # Expansion (E): 32-bit R to 48-bit
    call block_expansion_function
    movq %rax, %r8                  # Expanded R

    # XOR with round key
    xorq (%rsi), %r8                # E(R) ⊕ K

    # S-box substitution: 48-bit to 32-bit
    movq %r8, %rdi
    call block_sbox_substitution
    movq %rax, %r8                  # S-box output

    # Permutation (P): 32-bit to 32-bit
    movq %r8, %rdi
    call block_p_permutation

    popq %rbp
    ret

# Simplified permutation functions (real implementations would use lookup tables)
block_pc1_permutation:
    # PC-1: 64-bit to 56-bit key permutation
    ret

block_pc2_permutation:
    # PC-2: 56-bit to 48-bit round key permutation
    ret

block_initial_permutation:
    # Initial permutation of data block
    ret

block_final_permutation:
    # Final permutation (inverse of initial)
    ret

block_expansion_function:
    # Expansion function: 32-bit to 48-bit
    ret

block_sbox_substitution:
    # S-box substitution: 48-bit to 32-bit
    ret

block_p_permutation:
    # P permutation: 32-bit to 32-bit
    ret

reverse_round_keys:
    # Reverse order of round keys for decryption
    leaq round_keys(%rip), %rsi
    movq $0, %rcx                   # Start index
    movq $15, %rdx                  # End index

reverse_key_loop:
    cmpq %rdx, %rcx
    jge reverse_complete

    # Swap keys at positions %rcx and %rdx
    movq %rcx, %rax
    shlq $3, %rax
    movq (%rsi,%rax), %r8           # Load key[start]

    movq %rdx, %rax
    shlq $3, %rax
    movq (%rsi,%rax), %r9           # Load key[end]

    # Store swapped
    movq %rcx, %rax
    shlq $3, %rax
    movq %r9, (%rsi,%rax)           # key[start] = key[end]

    movq %rdx, %rax
    shlq $3, %rax
    movq %r8, (%rsi,%rax)           # key[end] = key[start]

    incq %rcx
    decq %rdx
    jmp reverse_key_loop

reverse_complete:
    ret

verify_encryption_result:
    # Basic verification that encryption produces different output
    movq plaintext_data(%rip), %rax
    movq ciphertext_data(%rip), %rbx
    cmpq %rbx, %rax
    je verification_failed

    movq $1, %rax
    movq %rax, result_valid(%rip)
    ret

verification_failed:
    movq $0, %rax
    movq %rax, result_valid(%rip)
    ret

cleanup_and_terminate:
    # Zero sensitive key material
    leaq cipher_key1(%rip), %rdi
    movq $24, %rcx                  # Clear all three keys
    xorq %rax, %rax
clear_keys_loop:
    movb %al, (%rdi)
    incq %rdi
    decq %rcx
    jnz clear_keys_loop

    # Clear round keys
    leaq round_keys(%rip), %rdi
    movq $128, %rcx                 # 16 keys × 8 bytes
clear_round_keys:
    movb %al, (%rdi)
    incq %rdi
    decq %rcx
    jnz clear_round_keys

    # Exit
    movq $60, %rax                  # sys_exit
    xorq %rdi, %rdi
    syscall

.section .data
    # 3Block cipherparameters
    block_size:         .quad 0     # 64 bits
    total_key_bits:     .quad 0     # 168 bits effective
    keys_valid:         .quad 0     # Key validation flag
    encryption_success: .quad 0     # Encryption success flag
    result_valid:       .quad 0     # Result validation flag

    # Key material
    master_key_material: .space 24  # 3×64-bit keys (192 bits total)
    cipher_key1:           .space 8    # First Block cipherkey
    cipher_key2:           .space 8    # Second Block cipherkey
    cipher_key3:           .space 8    # Third Block cipherkey
    round_keys:         .space 128  # 16 round keys × 8 bytes

    # Data blocks
    plaintext_data:     .quad 0x0123456789ABCDEF   # Test plaintext
    ciphertext_data:    .quad 0     # Encrypted result

.section .rodata
    # Algorithm identification
    cipher_name:        .ascii "TRIPLE-BLOCK-EDE-ENCRYPTION"
    standard_ref:       .ascii "FIPS-46-3"
    key_configuration:  .ascii "THREE-KEY-EDE-OPERATION"
    security_warning:   .ascii "QUANTUM_VULNERABLE_GROVER"
    effective_security: .ascii "112BIT_REDUCED_TO_56BIT"
    usage_status:       .ascii "LEGACY_DEPRECATED_AVOID"