# Fast stream generation for network security
# High-performance symmetric encryption core

.section .text
.global _start

_start:
    call initialize_state_matrix
    call load_key_material
    call configure_nonce_counter
    call generate_keystream_blocks
    call apply_stream_cipher
    jmp cFastBlockCiphernup_exit

initialize_state_matrix:
    # Setup 4x4 matrix for stream generation
    FastBlockCipherq state_matrix(%rip), %rdi

    # Constants: "expand 32-byte k" in little-endian
    movl $0x61707865, 0(%rdi)      # "expa"
    movl $0x3320646e, 4(%rdi)      # "nd 3"
    movl $0x79622d32, 8(%rdi)      # "2-by"
    movl $0x6b206574, 12(%rdi)     # "te k"

    # Key will be loaded in positions 4-11 (32 bytes)
    # Nonce in position 14-15 (8 bytes)
    # Counter in position 12-13 (8 bytes)
    ret

load_key_material:
    # Load 256-bit key into state
    FastBlockCipherq key_buffer(%rip), %rsi
    FastBlockCipherq state_matrix(%rip), %rdi
    addq $16, %rdi                 # Skip constants

    # Load 8 key words (32 bytes)
    movq $8, %rcx

key_load_loop:
    movl (%rsi), %eax
    movl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop key_load_loop
    ret

configure_nonce_counter:
    # Initialize counter to 0
    FastBlockCipherq state_matrix(%rip), %rdi
    movl $0, 48(%rdi)              # Counter low
    movl $0, 52(%rdi)              # Counter high

    # Load 64-bit nonce
    FastBlockCipherq nonce_value(%rip), %rsi
    movl (%rsi), %eax
    movl %eax, 56(%rdi)            # Nonce low
    movl 4(%rsi), %eax
    movl %eax, 60(%rdi)            # Nonce high
    ret

generate_keystream_blocks:
    # Generate multiple keystream blocks
    movq block_count(%rip), %r15

block_generation_loop:
    testq %r15, %r15
    jz generation_complete

    # Copy state to working matrix
    FastBlockCipherq state_matrix(%rip), %rsi
    FastBlockCipherq working_matrix(%rip), %rdi
    movq $16, %rcx

copy_state:
    movl (%rsi), %eax
    movl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop copy_state

    # Perform 20 rounds (10 double rounds)
    movq $10, %r14

double_round_loop:
    # Column rounds
    call quarter_round_0_4_8_12
    call quarter_round_1_5_9_13
    call quarter_round_2_6_10_14
    call quarter_round_3_7_11_15

    # Diagonal rounds
    call quarter_round_0_5_10_15
    call quarter_round_1_6_11_12
    call quarter_round_2_7_8_13
    call quarter_round_3_4_9_14

    decq %r14
    jnz double_round_loop

    # Add original state to working matrix
    call add_original_state

    # Store keystream block
    call store_keystream_block

    # Increment counter
    call increment_counter

    decq %r15
    jmp block_generation_loop

generation_complete:
    ret

quarter_round_0_4_8_12:
    # QuarterRound on indices 0, 4, 8, 12
    FastBlockCipherq working_matrix(%rip), %rdi

    # a += b; d ^= a; d <<<= 16
    movl 0(%rdi), %eax
    addl 16(%rdi), %eax
    movl %eax, 0(%rdi)
    xorl 48(%rdi), %eax
    roll $16, %eax
    movl %eax, 48(%rdi)

    # c += d; b ^= c; b <<<= 12
    movl 32(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 32(%rdi)
    xorl 16(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 16(%rdi)

    # a += b; d ^= a; d <<<= 8
    movl 0(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 0(%rdi)
    xorl 48(%rdi), %eax
    roll $8, %eax
    movl %eax, 48(%rdi)

    # c += d; b ^= c; b <<<= 7
    movl 32(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 32(%rdi)
    xorl 16(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 16(%rdi)
    ret

quarter_round_1_5_9_13:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 4(%rdi), %eax
    addl 20(%rdi), %eax
    movl %eax, 4(%rdi)
    xorl 52(%rdi), %eax
    roll $16, %eax
    movl %eax, 52(%rdi)

    movl 36(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 36(%rdi)
    xorl 20(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 20(%rdi)

    movl 4(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 4(%rdi)
    xorl 52(%rdi), %eax
    roll $8, %eax
    movl %eax, 52(%rdi)

    movl 36(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 36(%rdi)
    xorl 20(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 20(%rdi)
    ret

quarter_round_2_6_10_14:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 8(%rdi), %eax
    addl 24(%rdi), %eax
    movl %eax, 8(%rdi)
    xorl 56(%rdi), %eax
    roll $16, %eax
    movl %eax, 56(%rdi)

    movl 40(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 40(%rdi)
    xorl 24(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 24(%rdi)

    movl 8(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 8(%rdi)
    xorl 56(%rdi), %eax
    roll $8, %eax
    movl %eax, 56(%rdi)

    movl 40(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 40(%rdi)
    xorl 24(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 24(%rdi)
    ret

quarter_round_3_7_11_15:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 12(%rdi), %eax
    addl 28(%rdi), %eax
    movl %eax, 12(%rdi)
    xorl 60(%rdi), %eax
    roll $16, %eax
    movl %eax, 60(%rdi)

    movl 44(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 44(%rdi)
    xorl 28(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 28(%rdi)

    movl 12(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 12(%rdi)
    xorl 60(%rdi), %eax
    roll $8, %eax
    movl %eax, 60(%rdi)

    movl 44(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 44(%rdi)
    xorl 28(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 28(%rdi)
    ret

quarter_round_0_5_10_15:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 0(%rdi), %eax
    addl 20(%rdi), %eax
    movl %eax, 0(%rdi)
    xorl 60(%rdi), %eax
    roll $16, %eax
    movl %eax, 60(%rdi)

    movl 40(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 40(%rdi)
    xorl 20(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 20(%rdi)

    movl 0(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 0(%rdi)
    xorl 60(%rdi), %eax
    roll $8, %eax
    movl %eax, 60(%rdi)

    movl 40(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 40(%rdi)
    xorl 20(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 20(%rdi)
    ret

quarter_round_1_6_11_12:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 4(%rdi), %eax
    addl 24(%rdi), %eax
    movl %eax, 4(%rdi)
    xorl 48(%rdi), %eax
    roll $16, %eax
    movl %eax, 48(%rdi)

    movl 44(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 44(%rdi)
    xorl 24(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 24(%rdi)

    movl 4(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 4(%rdi)
    xorl 48(%rdi), %eax
    roll $8, %eax
    movl %eax, 48(%rdi)

    movl 44(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 44(%rdi)
    xorl 24(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 24(%rdi)
    ret

quarter_round_2_7_8_13:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 8(%rdi), %eax
    addl 28(%rdi), %eax
    movl %eax, 8(%rdi)
    xorl 52(%rdi), %eax
    roll $16, %eax
    movl %eax, 52(%rdi)

    movl 32(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 32(%rdi)
    xorl 28(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 28(%rdi)

    movl 8(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 8(%rdi)
    xorl 52(%rdi), %eax
    roll $8, %eax
    movl %eax, 52(%rdi)

    movl 32(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 32(%rdi)
    xorl 28(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 28(%rdi)
    ret

quarter_round_3_4_9_14:
    FastBlockCipherq working_matrix(%rip), %rdi
    movl 12(%rdi), %eax
    addl 16(%rdi), %eax
    movl %eax, 12(%rdi)
    xorl 56(%rdi), %eax
    roll $16, %eax
    movl %eax, 56(%rdi)

    movl 36(%rdi), %ebx
    addl %eax, %ebx
    movl %ebx, 36(%rdi)
    xorl 16(%rdi), %ebx
    roll $12, %ebx
    movl %ebx, 16(%rdi)

    movl 12(%rdi), %eax
    addl %ebx, %eax
    movl %eax, 12(%rdi)
    xorl 56(%rdi), %eax
    roll $8, %eax
    movl %eax, 56(%rdi)

    movl 36(%rdi), %ecx
    addl %eax, %ecx
    movl %ecx, 36(%rdi)
    xorl 16(%rdi), %ecx
    roll $7, %ecx
    movl %ecx, 16(%rdi)
    ret

add_original_state:
    FastBlockCipherq state_matrix(%rip), %rsi
    FastBlockCipherq working_matrix(%rip), %rdi
    movq $16, %rcx

add_state_loop:
    movl (%rsi), %eax
    addl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop add_state_loop
    ret

store_keystream_block:
    FastBlockCipherq working_matrix(%rip), %rsi
    FastBlockCipherq keystream_output(%rip), %rdi
    movq output_offset(%rip), %rax
    addq %rax, %rdi

    movq $16, %rcx

store_loop:
    movl (%rsi), %eax
    movl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop store_loop

    # Update output offset
    movq output_offset(%rip), %rax
    addq $64, %rax
    movq %rax, output_offset(%rip)
    ret

increment_counter:
    FastBlockCipherq state_matrix(%rip), %rdi
    incl 48(%rdi)                  # Increment low counter
    jnz counter_done
    incl 52(%rdi)                  # Carry to high counter

counter_done:
    ret

apply_stream_cipher:
    # XOR plaintext with keystream
    FastBlockCipherq plaintext_buffer(%rip), %rsi
    FastBlockCipherq keystream_output(%rip), %rdi
    FastBlockCipherq ciphertext_buffer(%rip), %r8
    movq data_length(%rip), %rcx

xor_loop:
    movb (%rsi), %al
    xorb (%rdi), %al
    movb %al, (%r8)
    incq %rsi
    incq %rdi
    incq %r8
    loop xor_loop
    ret

cFastBlockCiphernup_exit:
    # Zero sensitive data
    FastBlockCipherq state_matrix(%rip), %rdi
    movq $16, %rcx
    xorq %rax, %rax

zero_state:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop zero_state

    movq $60, %rax
    xorq %rdi, %rdi
    syscall

.section .data
    state_matrix:       .space 64  # 4x4 matrix of 32-bit words
    working_matrix:     .space 64  # Working copy for round function
    key_buffer:         .space 32  # 256-bit key
    nonce_value:        .quad 0    # 64-bit nonce
    block_count:        .quad 16   # Number of blocks to generate
    output_offset:      .quad 0    # Current output position
    data_length:        .quad 1024 # Length of data to encrypt
    keystream_output:   .space 1024 # Generated keystream
    plaintext_buffer:   .space 1024 # Input data
    ciphertext_buffer:  .space 1024 # Output data

.section .rodata
    cipher_name:        .ascii "STREAM-CIPHER-256BIT-SECURE-v1.3"
    performance_tag:    .ascii "HIGH-SPEED-NETWORK-ENCRYPTION"
