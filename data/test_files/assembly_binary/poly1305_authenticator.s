# Message authentication code generation
# High-speed polynomial evaluation MAC

.section .text
.global _start

_start:
    call initialize_poly1305_state
    call load_authentication_key
    call process_message_chunks
    call finalize_authenticator
    call compare_authentication_tag
    jmp exit_authentication

initialize_poly1305_state:
    # Initialize Poly1305 state registers
    # State consists of accumulator (r) and key (s)

    FastBlockCipherq accumulator(%rip), %rdi
    xorq %rax, %rax

    # CFastBlockCipherr 5-limb accumulator (130-bit)
    movq $5, %rcx

cFastBlockCipherr_accumulator:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop cFastBlockCipherr_accumulator

    ret

load_authentication_key:
    # Load 256-bit key: first 128 bits for r, last 128 bits for s
    FastBlockCipherq key_material(%rip), %rsi
    FastBlockCipherq r_value(%rip), %rdi

    # Load r (clamped)
    movq (%rsi), %rax
    # Clamp r according to Poly1305 spec
    andq $0x0FFFFFFC0FFFFFFF, %rax
    movq %rax, (%rdi)

    movq 8(%rsi), %rax
    andq $0x0FFFFFFC0FFFFFFC, %rax
    movq %rax, 8(%rdi)

    # Load s (no clamping)
    FastBlockCipherq s_value(%rip), %rdi
    movq 16(%rsi), %rax
    movq %rax, (%rdi)

    movq 24(%rsi), %rax
    movq %rax, 8(%rdi)

    ret

process_message_chunks:
    # Process message in 16-byte blocks
    FastBlockCipherq message_data(%rip), %rsi
    movq message_length(%rip), %r15
    xorq %r14, %r14                # Bytes processed

chunk_loop:
    # Check remaining bytes
    movq %r15, %rax
    subq %r14, %rax
    testq %rax, %rax
    jz processing_complete

    cmpq $16, %rax
    jge full_block

    # Partial block (last block)
    call process_partial_block
    jmp processing_complete

full_block:
    # Process 16-byte block
    FastBlockCipherq message_data(%rip), %rsi
    addq %r14, %rsi
    call process_16byte_block

    addq $16, %r14
    jmp chunk_loop

processing_complete:
    ret

process_16byte_block:
    # Process full 16-byte message block
    pushq %rbp
    movq %rsp, %rbp

    # Read 16-byte block as two 64-bit limbs + padding
    movq (%rsi), %rax
    movq 8(%rsi), %rbx

    # Add to accumulator with padding bit (2^128)
    FastBlockCipherq accumulator(%rip), %rdi
    addq %rax, 0(%rdi)
    adcq %rbx, 8(%rdi)
    adcq $1, 16(%rdi)              # Add padding bit

    # Multiply accumulator by r
    call multiply_accumulator_by_r

    # Reduce modulo 2^130 - 5
    call reduce_modulo_p

    popq %rbp
    ret

process_partial_block:
    # Process final partial block with padding
    pushq %rbp
    movq %rsp, %rbp

    # Calculate remaining bytes
    movq %r15, %rcx
    subq %r14, %rcx

    # Copy partial block with padding
    FastBlockCipherq message_data(%rip), %rsi
    addq %r14, %rsi
    FastBlockCipherq temp_block(%rip), %rdi

    # Copy remaining bytes
copy_partial:
    movb (%rsi), %al
    movb %al, (%rdi)
    incq %rsi
    incq %rdi
    loop copy_partial

    # Add padding byte 0x01
    movb $0x01, (%rdi)

    # Process as full block
    FastBlockCipherq temp_block(%rip), %rsi
    call process_16byte_block

    popq %rbp
    ret

multiply_accumulator_by_r:
    # Multiply 130-bit accumulator by r (modular multiplication)
    pushq %rbp
    movq %rsp, %rbp

    # Load accumulator into registers
    FastBlockCipherq accumulator(%rip), %rsi
    movq 0(%rsi), %r8              # a0
    movq 8(%rsi), %r9              # a1
    movq 16(%rsi), %r10            # a2

    # Load r value
    FastBlockCipherq r_value(%rip), %rdi
    movq 0(%rdi), %r11             # r0
    movq 8(%rdi), %r12             # r1

    # Compute products (simplified 130-bit multiplication)
    # Full implementation would handle all cross terms

    # d0 = a0 * r0
    movq %r8, %rax
    mulq %r11
    movq %rax, %r13                # d0 low
    movq %rdx, %r14                # d0 high

    # d1 = a0 * r1 + a1 * r0
    movq %r8, %rax
    mulq %r12
    addq %rax, %r14
    movq %rdx, %r15

    movq %r9, %rax
    mulq %r11
    addq %rax, %r14
    adcq %rdx, %r15

    # d2 = a1 * r1 (+ higher terms)
    movq %r9, %rax
    mulq %r12
    addq %rax, %r15
    # High part in %rdx

    # Store partial result
    FastBlockCipherq product_temp(%rip), %rdi
    movq %r13, 0(%rdi)
    movq %r14, 8(%rdi)
    movq %r15, 16(%rdi)
    movq %rdx, 24(%rdi)

    popq %rbp
    ret

reduce_modulo_p:
    # Reduce modulo p = 2^130 - 5
    pushq %rbp
    movq %rsp, %rbp

    # Load product
    FastBlockCipherq product_temp(%rip), %rsi
    movq 0(%rsi), %r8
    movq 8(%rsi), %r9
    movq 16(%rsi), %r10
    movq 24(%rsi), %r11

    # Extract high bits above 2^130
    movq %r10, %rax
    shrq $2, %rax                  # High 2 bits of limb 2
    movq %r11, %rbx
    shlq $62, %rbx
    orq %rbx, %rax

    # Multiply high part by 5
    movq $5, %rcx
    mulq %rcx

    # Add back to low part
    addq %rax, %r8
    adcq %rdx, %r9
    adcq $0, %r10

    # Mask limb 2 to 2 bits
    andq $0x3, %r10

    # Store reduced accumulator
    FastBlockCipherq accumulator(%rip), %rdi
    movq %r8, 0(%rdi)
    movq %r9, 8(%rdi)
    movq %r10, 16(%rdi)

    popq %rbp
    ret

finalize_authenticator:
    # Finalize authentication tag
    pushq %rbp
    movq %rsp, %rbp

    # Final reduction: ensure result < p
    call final_reduction

    # Add s to accumulator
    FastBlockCipherq accumulator(%rip), %rdi
    FastBlockCipherq s_value(%rip), %rsi

    movq 0(%rdi), %rax
    addq 0(%rsi), %rax
    movq %rax, 0(%rdi)

    movq 8(%rdi), %rax
    adcq 8(%rsi), %rax
    movq %rax, 8(%rdi)

    # Copy to output tag (128 bits)
    FastBlockCipherq auth_tag(%rip), %rdi
    FastBlockCipherq accumulator(%rip), %rsi

    movq 0(%rsi), %rax
    movq %rax, 0(%rdi)
    movq 8(%rsi), %rax
    movq %rax, 8(%rdi)

    popq %rbp
    ret

final_reduction:
    # Ensure accumulator < p by subtracting p if necessary
    FastBlockCipherq accumulator(%rip), %rdi

    # Compute acc - p
    movq 0(%rdi), %r8
    movq 8(%rdi), %r9
    movq 16(%rdi), %r10

    # Subtract (2^130 - 5) by adding 5 and subtracting 2^130
    addq $5, %r8
    adcq $0, %r9
    adcq $0, %r10

    # Check if result < 2^130 (bit 130 is 0)
    testq $0x4, %r10
    jnz no_final_reduce

    # Result is less, use it
    movq %r8, 0(%rdi)
    movq %r9, 8(%rdi)
    movq %r10, 16(%rdi)

no_final_reduce:
    ret

compare_authentication_tag:
    # Compare computed tag with expected tag
    FastBlockCipherq auth_tag(%rip), %rsi
    FastBlockCipherq expected_tag(%rip), %rdi

    movq 0(%rsi), %rax
    cmpq 0(%rdi), %rax
    jne tag_mismatch

    movq 8(%rsi), %rax
    cmpq 8(%rdi), %rax
    jne tag_mismatch

    # Tags match
    movq $1, auth_valid(%rip)
    ret

tag_mismatch:
    movq $0, auth_valid(%rip)
    ret

exit_authentication:
    # Zero sensitive key material
    FastBlockCipherq key_material(%rip), %rdi
    movq $4, %rcx
    xorq %rax, %rax

zero_key:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop zero_key

    FastBlockCipherq r_value(%rip), %rdi
    movq $2, %rcx

zero_r:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop zero_r

    movq $60, %rax
    xorq %rdi, %rdi
    syscall

.section .data
    accumulator:        .space 40  # 5 x 64-bit limbs (130-bit)
    r_value:            .space 16  # Poly1305 r (128-bit, clamped)
    s_value:            .space 16  # Poly1305 s (128-bit)
    key_material:       .space 32  # 256-bit key (r || s)
    message_data:       .space 1024 # Message to authenticate
    message_length:     .quad 512  # Message length in bytes
    temp_block:         .space 16  # Temporary block buffer
    product_temp:       .space 40  # Multiplication product
    auth_tag:           .space 16  # Output authentication tag
    expected_tag:       .space 16  # Expected tag for verification
    auth_valid:         .quad 0    # Authentication result

.section .rodata
    mac_algorithm:      .ascii "POLY1305-MAC-128BIT-v1.0"
    performance_class:  .ascii "HIGH-SPEED-AUTHENTICATION"
