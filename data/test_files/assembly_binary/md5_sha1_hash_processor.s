# MD5 and SHA-1 Hash Function Processor
# Legacy cryptographic hash functions
# Quantum-vulnerable to Grover's algorithm and collision attacks
# Used for legacy system compatibility

.file   "legacy_hash.c"
.text
.globl  process_legacy_hashes
.type   process_legacy_hashes, @function

# Legacy Hash Processing Main Function
# Supports both MD5 and SHA-1 for backward compatibility
process_legacy_hashes:
.LFB0:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $256, %rsp           # Local variables for hash states

    # Function parameters
    # %rdi: input message pointer
    # %rsi: message length
    # %rdx: hash type selector (0=MD5, 1=SHA1)
    # %rcx: output buffer

    movq    %rdi, -8(%rbp)       # Store message pointer
    movq    %rsi, -16(%rbp)      # Store message length
    movq    %rdx, -24(%rbp)      # Store hash type
    movq    %rcx, -32(%rbp)      # Store output buffer

    # Initialize hash contexts
    call    initialize_hash_contexts

    # Select hash algorithm
    movq    -24(%rbp), %rax
    testq   %rax, %rax
    jz      process_md5_hash
    jmp     process_sha1_hash

process_md5_hash:
    call    md5_hash_computation
    jmp     hash_processing_complete

process_sha1_hash:
    call    sha1_hash_computation

hash_processing_complete:
    # Copy result to output buffer
    call    copy_hash_result

    addq    $256, %rsp
    popq    %rbp
    ret

.LFE0:
    .size   process_legacy_hashes, .-process_legacy_hashes

# Initialize hash contexts for both MD5 and SHA-1
.globl  initialize_hash_contexts
.type   initialize_hash_contexts, @function
initialize_hash_contexts:
.LFB1:
    pushq   %rbp
    movq    %rsp, %rbp

    # Initialize MD5 context (RFC 1321)
    leaq    md5_state(%rip), %rax
    movl    $0x67452301, (%rax)      # A = 0x67452301
    movl    $0xEFCDAB89, 4(%rax)     # B = 0xEFCDAB89
    movl    $0x98BADCFE, 8(%rax)     # C = 0x98BADCFE
    movl    $0x10325476, 12(%rax)    # D = 0x10325476

    # Initialize SHA-1 context (RFC 3174)
    leaq    sha1_state(%rip), %rax
    movl    $0x67452301, (%rax)      # H0 = 0x67452301
    movl    $0xEFCDAB89, 4(%rax)     # H1 = 0xEFCDAB89
    movl    $0x98BADCFE, 8(%rax)     # H2 = 0x98BADCFE
    movl    $0x10325476, 12(%rax)    # H3 = 0x10325476
    movl    $0xC3D2E1F0, 16(%rax)    # H4 = 0xC3D2E1F0

    # Initialize bit counters
    movq    $0, md5_bit_count(%rip)
    movq    $0, sha1_bit_count(%rip)

    popq    %rbp
    ret

.LFE1:
    .size   initialize_hash_contexts, .-initialize_hash_contexts

# MD5 Hash Computation
.globl  md5_hash_computation
.type   md5_hash_computation, @function
md5_hash_computation:
.LFB2:
    pushq   %rbp
    movq    %rsp, %rbp

    # Process message in 512-bit (64-byte) blocks
    movq    -8(%rbp), %rsi       # Message pointer
    movq    -16(%rbp), %rcx      # Message length

md5_block_loop:
    cmpq    $64, %rcx            # Check if full block available
    jl      md5_final_block

    # Process 64-byte block
    call    md5_process_block
    addq    $64, %rsi            # Next block
    subq    $64, %rcx            # Remaining length
    jmp     md5_block_loop

md5_final_block:
    # Handle final block with padding
    call    md5_padding_and_final
    popq    %rbp
    ret

.LFE2:
    .size   md5_hash_computation, .-md5_hash_computation

# MD5 Block Processing (64 bytes)
.globl  md5_process_block
.type   md5_process_block, @function
md5_process_block:
.LFB3:
    pushq   %rbp
    movq    %rsp, %rbp
    pushq   %rbx
    pushq   %r12
    pushq   %r13
    pushq   %r14

    # Load current MD5 state
    leaq    md5_state(%rip), %rax
    movl    (%rax), %r8d         # A
    movl    4(%rax), %r9d        # B
    movl    8(%rax), %r10d       # C
    movl    12(%rax), %r11d      # D

    # MD5 has 64 operations in 4 rounds (16 operations each)
    movq    $0, %r12             # Operation counter

md5_operation_loop:
    cmpq    $64, %r12
    jge     md5_round_complete

    # Determine round and apply appropriate function
    movq    %r12, %rax
    shrq    $4, %rax             # Round = operation / 16

    cmpq    $0, %rax
    je      md5_round_f
    cmpq    $1, %rax
    je      md5_round_g
    cmpq    $2, %rax
    je      md5_round_h
    jmp     md5_round_i

md5_round_f:
    # F(B,C,D) = (B & C) | (~B & D)
    movl    %r9d, %eax           # B
    andl    %r10d, %eax          # B & C
    movl    %r9d, %ebx           # B
    notl    %ebx                 # ~B
    andl    %r11d, %ebx          # ~B & D
    orl     %ebx, %eax           # (B & C) | (~B & D)
    jmp     md5_apply_operation

md5_round_g:
    # G(B,C,D) = (B & D) | (C & ~D)
    movl    %r9d, %eax           # B
    andl    %r11d, %eax          # B & D
    movl    %r10d, %ebx          # C
    movl    %r11d, %ecx          # D
    notl    %ecx                 # ~D
    andl    %ecx, %ebx           # C & ~D
    orl     %ebx, %eax           # (B & D) | (C & ~D)
    jmp     md5_apply_operation

md5_round_h:
    # H(B,C,D) = B ⊕ C ⊕ D
    movl    %r9d, %eax           # B
    xorl    %r10d, %eax          # B ⊕ C
    xorl    %r11d, %eax          # B ⊕ C ⊕ D
    jmp     md5_apply_operation

md5_round_i:
    # I(B,C,D) = C ⊕ (B | ~D)
    movl    %r11d, %eax          # D
    notl    %eax                 # ~D
    orl     %r9d, %eax           # B | ~D
    xorl    %r10d, %eax          # C ⊕ (B | ~D)

md5_apply_operation:
    # A = B + ROL(A + F + X[k] + T[i], s)
    addl    %r8d, %eax           # A + F(B,C,D)

    # Add message word X[k] (simplified indexing)
    movq    %r12, %rbx
    andq    $15, %rbx            # k = i mod 16
    shlq    $2, %rbx             # Convert to byte offset
    addl    (%rsi,%rbx), %eax    # Add X[k]

    # Add MD5 constant T[i] (simplified)
    addl    $0x5A827999, %eax    # Simplified constant

    # Rotate left by s bits (simplified to 7 bits)
    roll    $7, %eax

    # Add B
    addl    %r9d, %eax

    # Rotate registers: A←D, B←A, C←B, D←C
    movl    %r11d, %r13d         # Save D
    movl    %r8d, %r11d          # D = A
    movl    %eax, %r8d           # A = new value
    movl    %r10d, %eax          # Save C
    movl    %r9d, %r10d          # C = B
    movl    %eax, %r9d           # B = old C

    incq    %r12                 # Next operation
    jmp     md5_operation_loop

md5_round_complete:
    # Add original values back to state
    leaq    md5_state(%rip), %rax
    addl    %r8d, (%rax)         # A += original A
    addl    %r9d, 4(%rax)        # B += original B
    addl    %r10d, 8(%rax)       # C += original C
    addl    %r11d, 12(%rax)      # D += original D

    popq    %r14
    popq    %r13
    popq    %r12
    popq    %rbx
    popq    %rbp
    ret

.LFE3:
    .size   md5_process_block, .-md5_process_block

# SHA-1 Hash Computation
.globl  sha1_hash_computation
.type   sha1_hash_computation, @function
sha1_hash_computation:
.LFB4:
    pushq   %rbp
    movq    %rsp, %rbp

    # Process message in 512-bit (64-byte) blocks
    movq    -8(%rbp), %rsi       # Message pointer
    movq    -16(%rbp), %rcx      # Message length

sha1_block_loop:
    cmpq    $64, %rcx            # Check if full block available
    jl      sha1_final_block

    # Process 64-byte block
    call    sha1_process_block
    addq    $64, %rsi            # Next block
    subq    $64, %rcx            # Remaining length
    jmp     sha1_block_loop

sha1_final_block:
    # Handle final block with padding
    call    sha1_padding_and_final
    popq    %rbp
    ret

.LFE4:
    .size   sha1_hash_computation, .-sha1_hash_computation

# SHA-1 Block Processing
.globl  sha1_process_block
.type   sha1_process_block, @function
sha1_process_block:
.LFB5:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $320, %rsp           # Space for 80 32-bit words

    # Load SHA-1 state
    leaq    sha1_state(%rip), %rax
    movl    (%rax), %r8d         # H0
    movl    4(%rax), %r9d        # H1
    movl    8(%rax), %r10d       # H2
    movl    12(%rax), %r11d      # H3
    movl    16(%rax), %r12d      # H4

    # Prepare message schedule W[0..79]
    call    sha1_message_schedule

    # 80 operations in 4 rounds of 20 each
    movq    $0, %r13             # Operation counter

sha1_operation_loop:
    cmpq    $80, %r13
    jge     sha1_operations_complete

    # Determine function based on round
    movq    %r13, %rax
    cmpq    $20, %rax
    jl      sha1_func_f
    cmpq    $40, %rax
    jl      sha1_func_g
    cmpq    $60, %rax
    jl      sha1_func_h
    jmp     sha1_func_i

sha1_func_f:
    # f(B,C,D) = (B & C) | (~B & D)
    movl    %r9d, %eax           # B
    andl    %r10d, %eax          # B & C
    movl    %r9d, %ebx           # B
    notl    %ebx                 # ~B
    andl    %r11d, %ebx          # ~B & D
    orl     %ebx, %eax           # (B & C) | (~B & D)
    movl    $0x5A827999, %ecx    # K0
    jmp     sha1_apply_function

sha1_func_g:
    # g(B,C,D) = B ⊕ C ⊕ D
    movl    %r9d, %eax           # B
    xorl    %r10d, %eax          # B ⊕ C
    xorl    %r11d, %eax          # B ⊕ C ⊕ D
    movl    $0x6ED9EBA1, %ecx    # K1
    jmp     sha1_apply_function

sha1_func_h:
    # h(B,C,D) = (B & C) | (B & D) | (C & D)
    movl    %r9d, %eax           # B
    andl    %r10d, %eax          # B & C
    movl    %r9d, %ebx           # B
    andl    %r11d, %ebx          # B & D
    orl     %ebx, %eax           # (B & C) | (B & D)
    movl    %r10d, %ebx          # C
    andl    %r11d, %ebx          # C & D
    orl     %ebx, %eax           # | (C & D)
    movl    $0x8F1BBCDC, %ecx    # K2
    jmp     sha1_apply_function

sha1_func_i:
    # i(B,C,D) = B ⊕ C ⊕ D (same as g)
    movl    %r9d, %eax           # B
    xorl    %r10d, %eax          # B ⊕ C
    xorl    %r11d, %eax          # B ⊕ C ⊕ D
    movl    $0xCA62C1D6, %ecx    # K3

sha1_apply_function:
    # temp = ROL(A, 5) + f(B,C,D) + E + K + W[t]
    movl    %r8d, %ebx           # A
    roll    $5, %ebx             # ROL(A, 5)
    addl    %eax, %ebx           # + f(B,C,D)
    addl    %r12d, %ebx          # + E
    addl    %ecx, %ebx           # + K

    # Add W[t]
    movq    %r13, %rax
    shlq    $2, %rax             # Convert to byte offset
    addl    -320(%rbp,%rax), %ebx # + W[t]

    # Update registers: E=D, D=C, C=ROL(B,30), B=A, A=temp
    movl    %r11d, %r12d         # E = D
    movl    %r10d, %r11d         # D = C
    movl    %r9d, %r10d          # C = B
    roll    $30, %r10d           # C = ROL(B, 30)
    movl    %r8d, %r9d           # B = A
    movl    %ebx, %r8d           # A = temp

    incq    %r13                 # Next operation
    jmp     sha1_operation_loop

sha1_operations_complete:
    # Add to hash state
    leaq    sha1_state(%rip), %rax
    addl    %r8d, (%rax)         # H0 += A
    addl    %r9d, 4(%rax)        # H1 += B
    addl    %r10d, 8(%rax)       # H2 += C
    addl    %r11d, 12(%rax)      # H3 += D
    addl    %r12d, 16(%rax)      # H4 += E

    addq    $320, %rsp
    popq    %rbp
    ret

.LFE5:
    .size   sha1_process_block, .-sha1_process_block

# SHA-1 Message Schedule (expand 16 words to 80)
.globl  sha1_message_schedule
.type   sha1_message_schedule, @function
sha1_message_schedule:
.LFB6:
    pushq   %rbp
    movq    %rsp, %rbp

    # Copy first 16 words from message block
    movq    $0, %rcx
copy_initial_words:
    cmpq    $16, %rcx
    jge     expand_words

    movl    (%rsi,%rcx,4), %eax
    movl    %eax, -320(%rbp,%rcx,4)
    incq    %rcx
    jmp     copy_initial_words

expand_words:
    # Expand W[16..79] using W[t] = ROL(W[t-3]⊕W[t-8]⊕W[t-14]⊕W[t-16], 1)
    movq    $16, %rcx

expand_loop:
    cmpq    $80, %rcx
    jge     schedule_complete

    # W[t] = W[t-3] ⊕ W[t-8] ⊕ W[t-14] ⊕ W[t-16]
    movq    %rcx, %rax
    subq    $3, %rax
    movl    -320(%rbp,%rax,4), %eax   # W[t-3]

    movq    %rcx, %rbx
    subq    $8, %rbx
    xorl    -320(%rbp,%rbx,4), %eax   # ⊕ W[t-8]

    movq    %rcx, %rbx
    subq    $14, %rbx
    xorl    -320(%rbp,%rbx,4), %eax   # ⊕ W[t-14]

    movq    %rcx, %rbx
    subq    $16, %rbx
    xorl    -320(%rbp,%rbx,4), %eax   # ⊕ W[t-16]

    roll    $1, %eax                  # ROL(..., 1)
    movl    %eax, -320(%rbp,%rcx,4)   # Store W[t]

    incq    %rcx
    jmp     expand_loop

schedule_complete:
    popq    %rbp
    ret

.LFE6:
    .size   sha1_message_schedule, .-sha1_message_schedule

# Placeholder functions for padding and finalization
.globl  md5_padding_and_final
.type   md5_padding_and_final, @function
md5_padding_and_final:
    # Add padding and process final block(s)
    ret

.globl  sha1_padding_and_final
.type   sha1_padding_and_final, @function
sha1_padding_and_final:
    # Add padding and process final block(s)
    ret

.globl  copy_hash_result
.type   copy_hash_result, @function
copy_hash_result:
    # Copy hash result to output buffer
    movq    -24(%rbp), %rax      # Hash type
    movq    -32(%rbp), %rdi      # Output buffer

    testq   %rax, %rax
    jz      copy_md5_result

copy_sha1_result:
    leaq    sha1_state(%rip), %rsi
    movq    $20, %rcx            # SHA-1 = 160 bits = 20 bytes
    rep movsb
    ret

copy_md5_result:
    leaq    md5_state(%rip), %rsi
    movq    $16, %rcx            # MD5 = 128 bits = 16 bytes
    rep movsb
    ret

# Hash state storage
.section .data
    # MD5 state (4 × 32-bit words)
    md5_state:          .space 16
    md5_bit_count:      .quad 0

    # SHA-1 state (5 × 32-bit words)
    sha1_state:         .space 20
    sha1_bit_count:     .quad 0

.section .rodata
    # Algorithm identification
    hash_algorithms:    .ascii "MD5-SHA1-LEGACY-HASH-FUNCTIONS"
    security_warning:   .ascii "CRYPTOGRAPHICALLY_BROKEN"
    collision_attacks:  .ascii "VULNERABLE_TO_COLLISION_ATTACKS"
    quantum_weakness:   .ascii "GROVER_ALGORITHM_REDUCES_SECURITY"
    usage_context:      .ascii "LEGACY_COMPATIBILITY_ONLY"