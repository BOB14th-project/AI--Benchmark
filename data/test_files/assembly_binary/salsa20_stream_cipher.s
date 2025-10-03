# Stream cipher for high-throughput encryption
# Fast symmetric encryption engine

.section .text
.global _start

_start:
    call setup_cipher_state
    call initialize_key_schedule
    call load_nonce_counter
    call generate_keystream
    call encrypt_data_stream
    jmp secure_cleanup

setup_cipher_state:
    # Setup Salsa20 4x4 matrix state
    leaq state_matrix(%rip), %rdi

    # Constants "expand 32-byte k" for Salsa20/20
    movl $0x61707865, 0(%rdi)      # "expa"
    movl $0x3320646e, 20(%rdi)     # "nd 3"
    movl $0x79622d32, 40(%rdi)     # "2-by"
    movl $0x6b206574, 60(%rdi)     # "te k"

    # Key positions: 4-11 (8 words, 32 bytes)
    # Counter/Nonce positions: 8-9 (counter), 6-7 (nonce)
    ret

initialize_key_schedule:
    # Load 256-bit key into state
    leaq cipher_key(%rip), %rsi
    leaq state_matrix(%rip), %rdi

    # Load first 16 bytes of key (words 1-4)
    movl (%rsi), %eax
    movl %eax, 4(%rdi)
    movl 4(%rsi), %eax
    movl %eax, 8(%rdi)
    movl 8(%rsi), %eax
    movl %eax, 12(%rdi)
    movl 12(%rsi), %eax
    movl %eax, 16(%rdi)

    # Load second 16 bytes of key (words 11-14)
    movl 16(%rsi), %eax
    movl %eax, 44(%rdi)
    movl 20(%rsi), %eax
    movl %eax, 48(%rdi)
    movl 24(%rsi), %eax
    movl %eax, 52(%rdi)
    movl 28(%rsi), %eax
    movl %eax, 56(%rdi)

    ret

load_nonce_counter:
    # Load 64-bit nonce and 64-bit counter
    leaq state_matrix(%rip), %rdi

    # Counter (positions 8-9)
    movl $0, 32(%rdi)              # Counter low
    movl $0, 36(%rdi)              # Counter high

    # Nonce (positions 6-7)
    leaq nonce_data(%rip), %rsi
    movl (%rsi), %eax
    movl %eax, 24(%rdi)
    movl 4(%rsi), %eax
    movl %eax, 28(%rdi)

    ret

generate_keystream:
    # Generate keystream blocks using Salsa20 core
    movq blocks_needed(%rip), %r15

block_loop:
    testq %r15, %r15
    jz keystream_complete

    # Copy state to working buffer
    call copy_state_to_working

    # Perform 20 rounds (10 double rounds)
    movq $10, %r14

double_round:
    # Column rounds
    call quarter_round_column_0
    call quarter_round_column_1
    call quarter_round_column_2
    call quarter_round_column_3

    # Row rounds
    call quarter_round_row_0
    call quarter_round_row_1
    call quarter_round_row_2
    call quarter_round_row_3

    decq %r14
    jnz double_round

    # Add original state to working state
    call add_state_to_working

    # Output keystream block
    call output_keystream_block

    # Increment counter
    call increment_block_counter

    decq %r15
    jmp block_loop

keystream_complete:
    ret

copy_state_to_working:
    leaq state_matrix(%rip), %rsi
    leaq working_state(%rip), %rdi
    movq $16, %rcx

copy_words:
    movl (%rsi), %eax
    movl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop copy_words
    ret

quarter_round_column_0:
    # QuarterRound(x[0], x[4], x[8], x[12])
    leaq working_state(%rip), %rdi

    # x[4] ^= ((x[0] + x[12]) <<< 7)
    movl 0(%rdi), %eax
    addl 48(%rdi), %eax
    roll $7, %eax
    xorl %eax, 16(%rdi)

    # x[8] ^= ((x[4] + x[0]) <<< 9)
    movl 16(%rdi), %eax
    addl 0(%rdi), %eax
    roll $9, %eax
    xorl %eax, 32(%rdi)

    # x[12] ^= ((x[8] + x[4]) <<< 13)
    movl 32(%rdi), %eax
    addl 16(%rdi), %eax
    roll $13, %eax
    xorl %eax, 48(%rdi)

    # x[0] ^= ((x[12] + x[8]) <<< 18)
    movl 48(%rdi), %eax
    addl 32(%rdi), %eax
    roll $18, %eax
    xorl %eax, 0(%rdi)

    ret

quarter_round_column_1:
    # QuarterRound(x[5], x[9], x[13], x[1])
    leaq working_state(%rip), %rdi

    movl 20(%rdi), %eax
    addl 4(%rdi), %eax
    roll $7, %eax
    xorl %eax, 36(%rdi)

    movl 36(%rdi), %eax
    addl 20(%rdi), %eax
    roll $9, %eax
    xorl %eax, 52(%rdi)

    movl 52(%rdi), %eax
    addl 36(%rdi), %eax
    roll $13, %eax
    xorl %eax, 4(%rdi)

    movl 4(%rdi), %eax
    addl 52(%rdi), %eax
    roll $18, %eax
    xorl %eax, 20(%rdi)

    ret

quarter_round_column_2:
    # QuarterRound(x[10], x[14], x[2], x[6])
    leaq working_state(%rip), %rdi

    movl 40(%rdi), %eax
    addl 8(%rdi), %eax
    roll $7, %eax
    xorl %eax, 56(%rdi)

    movl 56(%rdi), %eax
    addl 40(%rdi), %eax
    roll $9, %eax
    xorl %eax, 8(%rdi)

    movl 8(%rdi), %eax
    addl 56(%rdi), %eax
    roll $13, %eax
    xorl %eax, 24(%rdi)

    movl 24(%rdi), %eax
    addl 8(%rdi), %eax
    roll $18, %eax
    xorl %eax, 40(%rdi)

    ret

quarter_round_column_3:
    # QuarterRound(x[15], x[3], x[7], x[11])
    leaq working_state(%rip), %rdi

    movl 60(%rdi), %eax
    addl 12(%rdi), %eax
    roll $7, %eax
    xorl %eax, 12(%rdi)

    movl 12(%rdi), %eax
    addl 60(%rdi), %eax
    roll $9, %eax
    xorl %eax, 28(%rdi)

    movl 28(%rdi), %eax
    addl 12(%rdi), %eax
    roll $13, %eax
    xorl %eax, 44(%rdi)

    movl 44(%rdi), %eax
    addl 28(%rdi), %eax
    roll $18, %eax
    xorl %eax, 60(%rdi)

    ret

quarter_round_row_0:
    # QuarterRound(x[0], x[1], x[2], x[3])
    leaq working_state(%rip), %rdi

    movl 0(%rdi), %eax
    addl 12(%rdi), %eax
    roll $7, %eax
    xorl %eax, 4(%rdi)

    movl 4(%rdi), %eax
    addl 0(%rdi), %eax
    roll $9, %eax
    xorl %eax, 8(%rdi)

    movl 8(%rdi), %eax
    addl 4(%rdi), %eax
    roll $13, %eax
    xorl %eax, 12(%rdi)

    movl 12(%rdi), %eax
    addl 8(%rdi), %eax
    roll $18, %eax
    xorl %eax, 0(%rdi)

    ret

quarter_round_row_1:
    # QuarterRound(x[5], x[6], x[7], x[4])
    leaq working_state(%rip), %rdi

    movl 20(%rdi), %eax
    addl 16(%rdi), %eax
    roll $7, %eax
    xorl %eax, 24(%rdi)

    movl 24(%rdi), %eax
    addl 20(%rdi), %eax
    roll $9, %eax
    xorl %eax, 28(%rdi)

    movl 28(%rdi), %eax
    addl 24(%rdi), %eax
    roll $13, %eax
    xorl %eax, 16(%rdi)

    movl 16(%rdi), %eax
    addl 28(%rdi), %eax
    roll $18, %eax
    xorl %eax, 20(%rdi)

    ret

quarter_round_row_2:
    # QuarterRound(x[10], x[11], x[8], x[9])
    leaq working_state(%rip), %rdi

    movl 40(%rdi), %eax
    addl 32(%rdi), %eax
    roll $7, %eax
    xorl %eax, 44(%rdi)

    movl 44(%rdi), %eax
    addl 40(%rdi), %eax
    roll $9, %eax
    xorl %eax, 32(%rdi)

    movl 32(%rdi), %eax
    addl 44(%rdi), %eax
    roll $13, %eax
    xorl %eax, 36(%rdi)

    movl 36(%rdi), %eax
    addl 32(%rdi), %eax
    roll $18, %eax
    xorl %eax, 40(%rdi)

    ret

quarter_round_row_3:
    # QuarterRound(x[15], x[12], x[13], x[14])
    leaq working_state(%rip), %rdi

    movl 60(%rdi), %eax
    addl 48(%rdi), %eax
    roll $7, %eax
    xorl %eax, 52(%rdi)

    movl 52(%rdi), %eax
    addl 60(%rdi), %eax
    roll $9, %eax
    xorl %eax, 56(%rdi)

    movl 56(%rdi), %eax
    addl 52(%rdi), %eax
    roll $13, %eax
    xorl %eax, 48(%rdi)

    movl 48(%rdi), %eax
    addl 56(%rdi), %eax
    roll $18, %eax
    xorl %eax, 60(%rdi)

    ret

add_state_to_working:
    leaq state_matrix(%rip), %rsi
    leaq working_state(%rip), %rdi
    movq $16, %rcx

add_words:
    movl (%rsi), %eax
    addl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop add_words
    ret

output_keystream_block:
    # Write 64-byte keystream block to output
    leaq working_state(%rip), %rsi
    leaq keystream_buffer(%rip), %rdi
    movq output_position(%rip), %rax
    addq %rax, %rdi

    movq $16, %rcx

write_block:
    movl (%rsi), %eax
    movl %eax, (%rdi)
    addq $4, %rsi
    addq $4, %rdi
    loop write_block

    # Update output position
    movq output_position(%rip), %rax
    addq $64, %rax
    movq %rax, output_position(%rip)

    ret

increment_block_counter:
    # Increment 64-bit block counter
    leaq state_matrix(%rip), %rdi
    incl 32(%rdi)                  # Increment low word
    jnz counter_incremented
    incl 36(%rdi)                  # Carry to high word

counter_incremented:
    ret

encrypt_data_stream:
    # XOR plaintext with keystream
    leaq plaintext_data(%rip), %rsi
    leaq keystream_buffer(%rip), %rdi
    leaq ciphertext_data(%rip), %r8
    movq data_size(%rip), %rcx

xor_stream:
    movb (%rsi), %al
    xorb (%rdi), %al
    movb %al, (%r8)
    incq %rsi
    incq %rdi
    incq %r8
    loop xor_stream
    ret

secure_cleanup:
    # Zero key material
    leaq cipher_key(%rip), %rdi
    movq $8, %rcx
    xorq %rax, %rax

zero_cipher_key:
    movl %eax, (%rdi)
    addq $4, %rdi
    loop zero_cipher_key

    # Zero state
    leaq state_matrix(%rip), %rdi
    movq $16, %rcx

zero_state_matrix:
    movl %eax, (%rdi)
    addq $4, %rdi
    loop zero_state_matrix

    movq $60, %rax
    xorq %rdi, %rdi
    syscall

.section .data
    state_matrix:       .space 64  # 16 x 32-bit words
    working_state:      .space 64  # Working copy for rounds
    cipher_key:         .space 32  # 256-bit key
    nonce_data:         .quad 0    # 64-bit nonce
    blocks_needed:      .quad 16   # Number of blocks to generate
    output_position:    .quad 0    # Current output position
    data_size:          .quad 1024 # Data length
    keystream_buffer:   .space 1024 # Generated keystream
    plaintext_data:     .space 1024 # Input plaintext
    ciphertext_data:    .space 1024 # Output ciphertext

.section .rodata
    cipher_type:        .ascii "SALSA20-STREAM-256BIT-v1.0"
    round_count:        .ascii "20-ROUNDS-HIGH-SECURITY"
