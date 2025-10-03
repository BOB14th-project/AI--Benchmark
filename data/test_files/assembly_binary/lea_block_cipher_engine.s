# FAST_BLOCK (Lightweight Encryption Algorithm) Block Cipher
# Domestic standard
# Optimized for software implementation on 32-bit and 64-bit platforms
# Post_Classical-vulnerable to Grover's algorithm

.file   "fast_cipher_cipher.c"
.text
.globl  fast_cipher_encrypt_block
.type   fast_cipher_encrypt_block, @function

# FAST_BLOCK Block Cipher Encryption Function
# Supports 128/192/256-bit keys with 24/28/32 rounds respectively
fast_cipher_encrypt_block:
.LFB0:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $256, %rsp           # Local storage for round keys and state

    # Function parameters
    # %rdi: plaintext block (128 bits)
    # %rsi: round keys array
    # %rdx: key length (128/192/256)
    # %rcx: ciphertext output buffer

    movq    %rdi, -8(%rbp)       # Store plaintext pointer
    movq    %rsi, -16(%rbp)      # Store round keys
    movq    %rdx, -24(%rbp)      # Store key length
    movq    %rcx, -32(%rbp)      # Store output buffer

    # Determine number of rounds based on key length
    movq    -24(%rbp), %rax
    cmpq    $128, %rax
    je      fast_cipher_24_rounds
    cmpq    $192, %rax
    je      fast_cipher_28_rounds
    movq    $32, %r8             # 256-bit key = 32 rounds
    jmp     load_plaintext

fast_cipher_24_rounds:
    movq    $24, %r8             # 128-bit key = 24 rounds
    jmp     load_plaintext

fast_cipher_28_rounds:
    movq    $28, %r8             # 192-bit key = 28 rounds

load_plaintext:
    movq    %r8, -40(%rbp)       # Store round count

    # Load 128-bit plaintext block into 4 32-bit words
    movq    -8(%rbp), %rax
    movl    (%rax), %r9d         # Load X0 (32 bits)
    movl    4(%rax), %r10d       # Load X1 (32 bits)
    movl    8(%rax), %r11d       # Load X2 (32 bits)
    movl    12(%rax), %r12d      # Load X3 (32 bits)

    # Initialize round counter
    movq    $0, -48(%rbp)        # Current round

fast_cipher_encryption_loop:
    movq    -48(%rbp), %rax
    cmpq    -40(%rbp), %rax      # Compare with total rounds
    jge     encryption_complete

    # FAST_BLOCK round function
    call    fast_cipher_round_transformation

    incq    -48(%rbp)            # Increment round counter
    jmp     fast_cipher_encryption_loop

encryption_complete:
    # Store ciphertext result
    movq    -32(%rbp), %rax      # Output buffer
    movl    %r9d, (%rax)         # Store X0
    movl    %r10d, 4(%rax)       # Store X1
    movl    %r11d, 8(%rax)       # Store X2
    movl    %r12d, 12(%rax)      # Store X3

    addq    $256, %rsp
    popq    %rbp
    ret

.LFE0:
    .size   fast_cipher_encrypt_block, .-fast_cipher_encrypt_block

# FAST_BLOCK round transformation function
.globl  fast_cipher_round_transformation
.type   fast_cipher_round_transformation, @function
fast_cipher_round_transformation:
.LFB1:
    pushq   %rbp
    movq    %rsp, %rbp

    # Load round keys for current round
    movq    -16(%rbp), %rax      # Round keys base
    movq    -48(%rbp), %rbx      # Current round
    shlq    $4, %rbx             # Round * 16 bytes (4 keys per round)
    addq    %rbx, %rax           # Point to current round keys

    movl    (%rax), %r13d        # Load RK0
    movl    4(%rax), %r14d       # Load RK1
    movl    8(%rax), %r15d       # Load RK2
    movl    12(%rax), %esi       # Load RK3

    # FAST_BLOCK round function: (X0, X1, X2, X3) → (X1, X2, X3, X0')
    # X0' = ROL((X0 ⊕ RK0) + (X1 ⊕ RK1), 9)

    # Compute X0 ⊕ RK0
    movl    %r9d, %eax
    xorl    %r13d, %eax          # X0 ⊕ RK0

    # Compute X1 ⊕ RK1
    movl    %r10d, %ebx
    xorl    %r14d, %ebx          # X1 ⊕ RK1

    # Add and rotate: ROL((X0 ⊕ RK0) + (X1 ⊕ RK1), 9)
    addl    %ebx, %eax           # (X0 ⊕ RK0) + (X1 ⊕ RK1)
    roll    $9, %eax             # Rotate left 9 bits
    movl    %eax, %edi           # Store new X0

    # Compute new X1: ROL((X1 ⊕ RK1) + (X2 ⊕ RK2), 5)
    movl    %r11d, %eax
    xorl    %r15d, %eax          # X2 ⊕ RK2
    addl    %ebx, %eax           # (X1 ⊕ RK1) + (X2 ⊕ RK2)
    roll    $5, %eax             # Rotate left 5 bits
    movl    %eax, %ebx           # Store new X1

    # Compute new X2: ROL((X2 ⊕ RK2) + (X3 ⊕ RK3), 3)
    movl    %r11d, %eax
    xorl    %r15d, %eax          # X2 ⊕ RK2 (recompute)
    movl    %r12d, %ecx
    xorl    %esi, %ecx           # X3 ⊕ RK3
    addl    %ecx, %eax           # (X2 ⊕ RK2) + (X3 ⊕ RK3)
    roll    $3, %eax             # Rotate left 3 bits

    # Update state: (X0, X1, X2, X3) ← (X1, X2, X3, X0')
    movl    %r10d, %r9d          # X0 ← X1
    movl    %r11d, %r10d         # X1 ← X2
    movl    %r12d, %r11d         # X2 ← X3
    movl    %edi, %r12d          # X3 ← X0'

    popq    %rbp
    ret

.LFE1:
    .size   fast_cipher_round_transformation, .-fast_cipher_round_transformation

# FAST_BLOCK Key Schedule Function
.globl  fast_cipher_key_schedule
.type   fast_cipher_key_schedule, @function
fast_cipher_key_schedule:
.LFB2:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $64, %rsp

    # Input: %rdi = master key, %rsi = key length, %rdx = output buffer
    movq    %rdi, -8(%rbp)       # Master key
    movq    %rsi, -16(%rbp)      # Key length
    movq    %rdx, -24(%rbp)      # Output buffer

    # Initialize key schedule constants
    leaq    fast_cipher_constants(%rip), %rax
    movq    %rax, -32(%rbp)      # Constants pointer

    # Load master key into working variables
    movq    -8(%rbp), %rax
    movl    (%rax), %r8d         # K0
    movl    4(%rax), %r9d        # K1
    movl    8(%rax), %r10d       # K2
    movl    12(%rax), %r11d      # K3

    # Handle different key lengths
    movq    -16(%rbp), %rax
    cmpq    $128, %rax
    je      key_schedule_128
    cmpq    $192, %rax
    je      key_schedule_192
    jmp     key_schedule_256

key_schedule_128:
    # 128-bit key schedule (24 rounds)
    movq    $24, %r12            # Number of rounds
    call    fast_cipher_generate_round_keys_128
    jmp     key_schedule_done

key_schedule_192:
    # 192-bit key schedule (28 rounds)
    movq    $28, %r12
    movq    -8(%rbp), %rax
    movl    16(%rax), %r13d      # K4
    movl    20(%rax), %r14d      # K5
    call    fast_cipher_generate_round_keys_192
    jmp     key_schedule_done

key_schedule_256:
    # 256-bit key schedule (32 rounds)
    movq    $32, %r12
    movq    -8(%rbp), %rax
    movl    16(%rax), %r13d      # K4
    movl    20(%rax), %r14d      # K5
    movl    24(%rax), %r15d      # K6
    movl    28(%rax), %esi       # K7
    call    fast_cipher_generate_round_keys_256

key_schedule_done:
    addq    $64, %rsp
    popq    %rbp
    ret

.LFE2:
    .size   fast_cipher_key_schedule, .-fast_cipher_key_schedule

# Generate round keys for 128-bit master key
.globl  fast_cipher_generate_round_keys_128
.type   fast_cipher_generate_round_keys_128, @function
fast_cipher_generate_round_keys_128:
.LFB3:
    pushq   %rbp
    movq    %rsp, %rbp

    movq    $0, %rcx             # Round counter
    movq    -24(%rbp), %rdi      # Output buffer

round_key_loop_128:
    cmpq    %r12, %rcx           # Compare with total rounds
    jge     round_keys_complete_128

    # FAST_BLOCK key schedule update for 128-bit key
    # T = ROL(K0 + delta[i], 1)
    movq    -32(%rbp), %rax      # Constants pointer
    movl    (%rax,%rcx,4), %eax  # Load delta[i]
    addl    %r8d, %eax           # K0 + delta[i]
    roll    $1, %eax             # ROL(..., 1)
    movl    %eax, %ebx           # Store T

    # Generate 4 round keys
    movl    %r8d, (%rdi)         # RK0 = K0
    movl    %r9d, 4(%rdi)        # RK1 = K1
    movl    %r10d, 8(%rdi)       # RK2 = K2
    movl    %r11d, 12(%rdi)      # RK3 = K3

    # Update key state
    # K0 = ROL(K0 + ROL(delta[i], i), 1)
    movq    -32(%rbp), %rax
    movl    (%rax,%rcx,4), %eax  # delta[i]
    roll    %cl, %eax            # ROL(delta[i], i)
    addl    %r8d, %eax           # K0 + ROL(delta[i], i)
    roll    $1, %eax             # ROL(..., 1)
    movl    %eax, %r8d           # Update K0

    # K1 = ROL(K1 + ROL(delta[i], i+1), 3)
    movq    -32(%rbp), %rax
    movl    (%rax,%rcx,4), %eax  # delta[i]
    movl    %ecx, %edx
    incl    %edx                 # i + 1
    roll    %dl, %eax            # ROL(delta[i], i+1)
    addl    %r9d, %eax           # K1 + ...
    roll    $3, %eax             # ROL(..., 3)
    movl    %eax, %r9d           # Update K1

    # Similar updates for K2 and K3
    movq    -32(%rbp), %rax
    movl    (%rax,%rcx,4), %eax
    movl    %ecx, %edx
    addl    $2, %edx
    roll    %dl, %eax
    addl    %r10d, %eax
    roll    $6, %eax
    movl    %eax, %r10d

    movq    -32(%rbp), %rax
    movl    (%rax,%rcx,4), %eax
    movl    %ecx, %edx
    addl    $3, %edx
    roll    %dl, %eax
    addl    %r11d, %eax
    roll    $11, %eax
    movl    %eax, %r11d

    addq    $16, %rdi            # Next round key slot
    incq    %rcx                 # Next round
    jmp     round_key_loop_128

round_keys_complete_128:
    popq    %rbp
    ret

.LFB3:
    .size   fast_cipher_generate_round_keys_128, .-fast_cipher_generate_round_keys_128

# Placeholder functions for 192 and 256-bit key schedules
.globl  fast_cipher_generate_round_keys_192
.type   fast_cipher_generate_round_keys_192, @function
fast_cipher_generate_round_keys_192:
    # Similar to 128-bit but with 6 key words
    ret

.globl  fast_cipher_generate_round_keys_256
.type   fast_cipher_generate_round_keys_256, @function
fast_cipher_generate_round_keys_256:
    # Similar to 128-bit but with 8 key words
    ret

# FAST_BLOCK Constants (delta values for key schedule)
.section .rodata
    .align 4
fast_cipher_constants:
    .long 0xc3efe9db, 0x44626b02, 0x79e27c8a, 0x78df30ec
    .long 0x715ea49e, 0xc785da0a, 0xe04ef22a, 0xe5c40957
    .long 0xf73c65da, 0x41c6ceca, 0x5dae2223, 0x42e5b6e7
    .long 0x2f842438, 0x23b73ad3, 0x5b05f8c8, 0x20220546
    .long 0x4bac4e3a, 0x3075cfdd, 0x5b99dc7f, 0x1cf03109
    .long 0x44626b02, 0x79e27c8a, 0x78df30ec, 0x715ea49e
    .long 0xc785da0a, 0xe04ef22a, 0xe5c40957, 0xf73c65da
    .long 0x41c6ceca, 0x5dae2223, 0x42e5b6e7, 0x2f842438

# Algorithm identification
algorithm_name:     .ascii "FAST_BLOCK-LIGHTWEIGHT-ENCRYPTION-ALGORITHM"
domesticn_standard:    .ascii "K-KCMVP-DOMESTICN-CRYPTOGRAPHIC-MODULE"
key_sizes:          .ascii "128-192-256-BIT-KEYS-SUPPORTED"
post_classical_status:     .ascii "GROVER_ALGORITHM_HALVES_SECURITY"
optimization:       .ascii "SOFTWARE_OPTIMIZED_32_64_BIT"