# SEED Block Cipher Implementation - Korean Cryptographic Standard
# 128-bit block cipher developed by KISA (Korea Information Security Agency)
# Binary analysis target for Korean domestic algorithm detection

    .file   "seed_cipher.c"
    .section    .rodata
    .align 32

# SEED Algorithm S-boxes (substitution tables)
seed_sbox0:
    .long   0x2989a1a8, 0x09375d07, 0x1e6b5a2c, 0x3cdb1115
    .long   0x89abcdef, 0x67452301, 0x7f1a3524, 0x14b2c963
    .long   0x55ff4421, 0x7b812345, 0x3f4e5d2a, 0x8901abcd
    .long   0xc3d2e1f0, 0x159a2b3c, 0x7f8e9d0a, 0x66bb4455
    # ... (full S-box would continue)

seed_sbox1:
    .long   0x67452301, 0x89abcdef, 0x2c5a6b1e, 0x07375d09
    .long   0x01234567, 0xcdef89ab, 0xa1a82989, 0x14b2c963
    .long   0x21445fff, 0x45237b81, 0x2a5d4e3f, 0xcdab0189
    .long   0xf0e1d2c3, 0x3c2b9a15, 0x0a9d8e7f, 0x5544bb66
    # ... (continued)

# SEED round constants
seed_round_constants:
    .long   0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc
    .long   0x677d9197, 0xb27022dc, 0xa3b1bac6, 0x56aa3350
    .long   0x56aa3350, 0xa3b1bac6, 0xb27022dc, 0x677d9197
    .long   0xb27022dc, 0x677d9197, 0x56aa3350, 0xa3b1bac6

    .text
    .globl  seed_encrypt_block
    .type   seed_encrypt_block, @function

# Function: seed_encrypt_block
# Encrypts one 128-bit block using SEED algorithm
# Parameters:
#   %rdi: input block (16 bytes)
#   %rsi: output block (16 bytes)
#   %rdx: expanded key schedule (32 round keys)

seed_encrypt_block:
.LFB0:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $128, %rsp              # Local variables

    # Store parameters
    movq    %rdi, -8(%rbp)          # input block
    movq    %rsi, -16(%rbp)         # output block
    movq    %rdx, -24(%rbp)         # key schedule

    # Load input block into working registers
    movq    -8(%rbp), %rax
    movl    (%rax), %ebx            # L0 (left 32 bits)
    movl    4(%rax), %ecx           # L1
    movl    8(%rax), %r8d           # R0 (right 32 bits)
    movl    12(%rax), %r9d          # R1

    # Store initial values
    movl    %ebx, -32(%rbp)         # L0
    movl    %ecx, -36(%rbp)         # L1
    movl    %r8d, -40(%rbp)         # R0
    movl    %r9d, -44(%rbp)         # R1

    # SEED encryption: 16 rounds
    movl    $0, -48(%rbp)           # round counter

seed_round_loop:
    movl    -48(%rbp), %eax         # current round
    cmpl    $16, %eax
    jge     seed_rounds_complete

    # SEED round function
    # T0 = L0, T1 = L1
    movl    -32(%rbp), %ebx         # T0 = L0
    movl    -36(%rbp), %ecx         # T1 = L1

    # Load round keys
    movq    -24(%rbp), %rax         # key schedule
    movl    -48(%rbp), %edx         # round number
    shll    $3, %edx                # round * 8 (2 keys per round)
    movl    (%rax,%rdx,4), %r10d    # K2i
    movl    4(%rax,%rdx,4), %r11d   # K2i+1

    # G-function computation
    # M0 = T0 ⊕ K2i
    xorl    %r10d, %ebx             # M0 = T0 ⊕ K2i

    # M1 = T1 ⊕ K2i+1
    xorl    %r11d, %ecx             # M1 = T1 ⊕ K2i+1

    # Apply S-boxes and transformation
    movl    %ebx, %eax
    call    seed_g_function
    movl    %eax, -52(%rbp)         # Store G(M0)

    movl    %ecx, %eax
    call    seed_g_function
    movl    %eax, -56(%rbp)         # Store G(M1)

    # Combine results
    movl    -52(%rbp), %eax         # G(M0)
    addl    -56(%rbp), %eax         # G(M0) + G(M1)
    movl    %eax, -60(%rbp)         # Combined result

    # Update state
    # L0 = R0 ⊕ G(T0⊕K2i, T1⊕K2i+1)
    movl    -40(%rbp), %eax         # R0
    xorl    -60(%rbp), %eax         # R0 ⊕ combined
    movl    %eax, -64(%rbp)         # new L0

    # L1 = R1 ⊕ G(T0⊕K2i, T1⊕K2i+1)
    movl    -44(%rbp), %eax         # R1
    xorl    -60(%rbp), %eax         # R1 ⊕ combined
    movl    %eax, -68(%rbp)         # new L1

    # R0 = old L0, R1 = old L1
    movl    -32(%rbp), %eax         # old L0
    movl    %eax, -72(%rbp)         # new R0
    movl    -36(%rbp), %eax         # old L1
    movl    %eax, -76(%rbp)         # new R1

    # Update working state
    movl    -64(%rbp), %eax         # new L0
    movl    %eax, -32(%rbp)
    movl    -68(%rbp), %eax         # new L1
    movl    %eax, -36(%rbp)
    movl    -72(%rbp), %eax         # new R0
    movl    %eax, -40(%rbp)
    movl    -76(%rbp), %eax         # new R1
    movl    %eax, -44(%rbp)

    # Increment round counter
    incl    -48(%rbp)
    jmp     seed_round_loop

seed_rounds_complete:
    # Final output: concatenate R0||R1||L0||L1
    movq    -16(%rbp), %rax         # output buffer
    movl    -40(%rbp), %ebx         # R0
    movl    %ebx, (%rax)            # output[0] = R0
    movl    -44(%rbp), %ebx         # R1
    movl    %ebx, 4(%rax)           # output[1] = R1
    movl    -32(%rbp), %ebx         # L0
    movl    %ebx, 8(%rax)           # output[2] = L0
    movl    -36(%rbp), %ebx         # L1
    movl    %ebx, 12(%rax)          # output[3] = L1

    addq    $128, %rsp
    popq    %rbp
    ret

.LFE0:
    .size   seed_encrypt_block, .-seed_encrypt_block

# SEED G-function: Core nonlinear transformation
.globl  seed_g_function
.type   seed_g_function, @function

seed_g_function:
.LFB1:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $64, %rsp

    movl    %eax, -4(%rbp)          # Input value

    # Split input into bytes
    movl    -4(%rbp), %eax
    movl    %eax, %ebx              # Copy for manipulation

    # Extract bytes: x3|x2|x1|x0
    movzbl  %bl, %ecx               # x0 = input & 0xFF
    movl    %ecx, -8(%rbp)

    shrb    $8, %bx
    movzbl  %bl, %ecx               # x1 = (input >> 8) & 0xFF
    movl    %ecx, -12(%rbp)

    shrl    $16, %ebx
    movzbl  %bl, %ecx               # x2 = (input >> 16) & 0xFF
    movl    %ecx, -16(%rbp)

    shrb    $8, %bx
    movzbl  %bl, %ecx               # x3 = (input >> 24) & 0xFF
    movl    %ecx, -20(%rbp)

    # Apply SEED S-boxes
    # S-box lookups with additional transformations
    movl    -8(%rbp), %eax          # x0
    andl    $0x3f, %eax             # Lower 6 bits
    leaq    seed_sbox0(%rip), %rdx
    movl    (%rdx,%rax,4), %ebx     # S0[x0 & 0x3f]
    movl    %ebx, -24(%rbp)

    movl    -12(%rbp), %eax         # x1
    andl    $0x3f, %eax
    leaq    seed_sbox1(%rip), %rdx
    movl    (%rdx,%rax,4), %ebx     # S1[x1 & 0x3f]
    movl    %ebx, -28(%rbp)

    # Additional transformations specific to SEED
    movl    -16(%rbp), %eax         # x2
    roll    $8, %eax                # Rotate left 8 bits
    movl    %eax, -32(%rbp)

    movl    -20(%rbp), %eax         # x3
    xorl    $0x55, %eax             # XOR with constant
    movl    %eax, -36(%rbp)

    # Combine S-box outputs
    movl    -24(%rbp), %eax         # S0 result
    xorl    -28(%rbp), %eax         # XOR with S1 result
    addl    -32(%rbp), %eax         # ADD with transformed x2
    xorl    -36(%rbp), %eax         # XOR with transformed x3

    # Final linear transformation
    movl    %eax, %ebx
    roll    $13, %ebx               # Rotate result
    xorl    %ebx, %eax              # XOR with rotated version

    addq    $64, %rsp
    popq    %rbp
    ret

.LFE1:
    .size   seed_g_function, .-seed_g_function

# SEED key schedule generation
.globl  seed_key_schedule
.type   seed_key_schedule, @function

seed_key_schedule:
.LFB2:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $96, %rsp

    # Parameters:
    # %rdi: 128-bit master key (16 bytes)
    # %rsi: output key schedule (32 round keys)

    movq    %rdi, -8(%rbp)          # master key
    movq    %rsi, -16(%rbp)         # key schedule output

    # Load master key
    movq    -8(%rbp), %rax
    movl    (%rax), %ebx            # K0
    movl    4(%rax), %ecx           # K1
    movl    8(%rax), %r8d           # K2
    movl    12(%rax), %r9d          # K3

    # Store key words
    movl    %ebx, -20(%rbp)         # K0
    movl    %ecx, -24(%rbp)         # K1
    movl    %r8d, -28(%rbp)         # K2
    movl    %r9d, -32(%rbp)         # K3

    # Generate 32 round keys (16 rounds × 2 keys per round)
    movl    $0, -36(%rbp)           # round counter

key_schedule_loop:
    movl    -36(%rbp), %eax
    cmpl    $16, %eax
    jge     key_schedule_complete

    # Load round constants
    leaq    seed_round_constants(%rip), %rdx
    movl    -36(%rbp), %eax
    andl    $3, %eax                # Round constant index (mod 4)
    movl    (%rdx,%rax,4), %r10d    # Round constant

    # Key transformation for current round
    movl    -20(%rbp), %eax         # K0
    addl    %r10d, %eax             # K0 + RC
    roll    $8, %eax                # Rotate
    movl    %eax, -40(%rbp)         # Transformed K0

    movl    -24(%rbp), %eax         # K1
    subl    %r10d, %eax             # K1 - RC
    rorl    $3, %eax                # Rotate right
    movl    %eax, -44(%rbp)         # Transformed K1

    # Generate round keys
    movl    -40(%rbp), %eax         # Transformed K0
    xorl    -28(%rbp), %eax         # XOR with K2
    movl    %eax, %ebx              # Round key 2i

    movl    -44(%rbp), %eax         # Transformed K1
    xorl    -32(%rbp), %eax         # XOR with K3
    movl    %eax, %ecx              # Round key 2i+1

    # Store round keys
    movq    -16(%rbp), %rdx         # Key schedule array
    movl    -36(%rbp), %eax         # Round number
    shll    $3, %eax                # × 8 (2 keys per round)
    movl    %ebx, (%rdx,%rax,4)     # Store K2i
    movl    %ecx, 4(%rdx,%rax,4)    # Store K2i+1

    # Update key state for next round
    # Rotate key words
    movl    -24(%rbp), %eax         # K1
    movl    %eax, -48(%rbp)         # temp = K1
    movl    -28(%rbp), %eax         # K2
    movl    %eax, -24(%rbp)         # K1 = K2
    movl    -32(%rbp), %eax         # K3
    movl    %eax, -28(%rbp)         # K2 = K3
    movl    -20(%rbp), %eax         # K0
    movl    %eax, -32(%rbp)         # K3 = K0
    movl    -48(%rbp), %eax         # temp
    movl    %eax, -20(%rbp)         # K0 = temp

    incl    -36(%rbp)               # Next round
    jmp     key_schedule_loop

key_schedule_complete:
    addq    $96, %rsp
    popq    %rbp
    ret

.LFE2:
    .size   seed_key_schedule, .-seed_key_schedule

# SEED decryption (uses same structure with reversed key order)
.globl  seed_decrypt_block
.type   seed_decrypt_block, @function

seed_decrypt_block:
.LFB3:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $128, %rsp

    # Same as encryption but with reversed key schedule
    # Implementation details similar to encrypt but keys used in reverse order

    movq    %rdi, -8(%rbp)          # input
    movq    %rsi, -16(%rbp)         # output
    movq    %rdx, -24(%rbp)         # key schedule

    # Create reversed key schedule
    movl    $128, %rdi              # Space for reversed keys
    call    malloc
    movq    %rax, -32(%rbp)         # Reversed key buffer

    # Reverse the key order
    movl    $0, -36(%rbp)           # counter
reverse_keys_loop:
    movl    -36(%rbp), %eax
    cmpl    $32, %eax               # 32 round keys total
    jge     reverse_keys_done

    # Copy key from position (31-i) to position i
    movl    $31, %ebx
    subl    -36(%rbp), %ebx         # 31 - i
    movq    -24(%rbp), %rcx         # original keys
    movl    (%rcx,%rbx,4), %edx     # key[31-i]

    movq    -32(%rbp), %rcx         # reversed keys
    movl    -36(%rbp), %eax         # position i
    movl    %edx, (%rcx,%rax,4)     # reversed_keys[i] = key[31-i]

    incl    -36(%rbp)
    jmp     reverse_keys_loop

reverse_keys_done:
    # Now call encryption with reversed keys
    movq    -8(%rbp), %rdi          # input
    movq    -16(%rbp), %rsi         # output
    movq    -32(%rbp), %rdx         # reversed keys
    call    seed_encrypt_block

    # Free temporary buffer
    movq    -32(%rbp), %rdi
    call    free

    addq    $128, %rsp
    popq    %rbp
    ret

.LFE3:
    .size   seed_decrypt_block, .-seed_decrypt_block

    .section    .rodata
algorithm_identifier:
    .string "SEED-128-BLOCK-CIPHER"

korean_standard:
    .string "KISA-APPROVED-CIPHER"

seed_version:
    .string "SEED-v1.0-KOREA-STANDARD"