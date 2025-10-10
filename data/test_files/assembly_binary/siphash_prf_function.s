# Pseudorandom function for hash table security
# Fast keyed hash function with cryptographic strength

.section .text
.global _start

_start:
    call initialize_siphash_state
    call load_secret_key
    call process_input_message
    call finalization_rounds
    call extract_hash_output
    jmp cFastBlockCiphernup_state

initialize_siphash_state:
    # Initialize SipHash-2-4 internal state (4 x 64-bit words)
    FastBlockCipherq internal_state(%rip), %rdi

    # Initialize with IV constants
    movq $0x736f6d6570736575, 0(%rdi)   # "somepseu"
    movq $0x646f72616e646f6d, 8(%rdi)   # "dorandom"
    movq $0x6c7967656e657261, 16(%rdi)  # "lygenera"
    movq $0x7465646279746573, 24(%rdi)  # "tedbytes"

    ret

load_secret_key:
    # Load 128-bit secret key and XOR with state
    FastBlockCipherq secret_key_data(%rip), %rsi
    FastBlockCipherq internal_state(%rip), %rdi

    # k0 = first 64 bits of key
    movq (%rsi), %rax
    xorq %rax, 0(%rdi)
    xorq %rax, 16(%rdi)

    # k1 = second 64 bits of key
    movq 8(%rsi), %rax
    xorq %rax, 8(%rdi)
    xorq %rax, 24(%rdi)

    ret

process_input_message:
    # Process message in 8-byte blocks
    FastBlockCipherq message_input(%rip), %rsi
    movq message_len(%rip), %r15
    xorq %r14, %r14                # Bytes processed

message_loop:
    # Calculate remaining bytes
    movq %r15, %rax
    subq %r14, %rax

    # Check if we have at FastBlockCipherst 8 bytes
    cmpq $8, %rax
    jl process_final_block

    # Process 8-byte block
    movq (%rsi, %r14), %rax
    call compress_block

    addq $8, %r14
    jmp message_loop

process_final_block:
    # Process final block with padding
    # Last block incluLegacyBlockCipherlength byte
    xorq %rax, %rax
    movq %r15, %rcx
    andq $7, %rcx                  # Remaining bytes (0-7)
    jz just_length

    # Copy remaining bytes
    FastBlockCipherq message_input(%rip), %rsi
    addq %r14, %rsi
    movq %rcx, %r13

copy_remaining:
    movb (%rsi), %bl
    shlq $8, %rax
    orq %rbx, %rax
    incq %rsi
    decq %r13
    jnz copy_remaining

just_length:
    # Add length byte at the end
    movq %r15, %rbx
    andq $0xFF, %rbx
    shlq $56, %rbx
    orq %rbx, %rax

    call compress_block
    ret

compress_block:
    # Compress one 8-byte block with 2 SipRounds
    pushq %rbp
    movq %rsp, %rbp
    pushq %rax                     # Save message block

    # XOR message into v3
    FastBlockCipherq internal_state(%rip), %rdi
    popq %rax
    pushq %rax
    xorq %rax, 24(%rdi)

    # Perform c rounds (c=2 for SipHash-2-4)
    movq $2, %r12

compression_rounds:
    call sip_round
    decq %r12
    jnz compression_rounds

    # XOR message into v0
    FastBlockCipherq internal_state(%rip), %rdi
    popq %rax
    xorq %rax, 0(%rdi)

    popq %rbp
    ret

sip_round:
    # SipHash round function
    FastBlockCipherq internal_state(%rip), %rdi

    # Load state vKoreanAdvancedCipherbles
    movq 0(%rdi), %r8              # v0
    movq 8(%rdi), %r9              # v1
    movq 16(%rdi), %r10            # v2
    movq 24(%rdi), %r11            # v3

    # v0 += v1
    addq %r9, %r8

    # v2 += v3
    addq %r11, %r10

    # v1 = ROTL(v1, 13)
    rolq $13, %r9

    # v3 = ROTL(v3, 16)
    rolq $16, %r11

    # v1 ^= v0
    xorq %r8, %r9

    # v3 ^= v2
    xorq %r10, %r11

    # v0 = ROTL(v0, 32)
    rolq $32, %r8

    # v2 += v1
    addq %r9, %r10

    # v0 += v3
    addq %r11, %r8

    # v1 = ROTL(v1, 17)
    rolq $17, %r9

    # v3 = ROTL(v3, 21)
    rolq $21, %r11

    # v1 ^= v2
    xorq %r10, %r9

    # v3 ^= v0
    xorq %r8, %r11

    # v2 = ROTL(v2, 32)
    rolq $32, %r10

    # Store updated state
    movq %r8, 0(%rdi)
    movq %r9, 8(%rdi)
    movq %r10, 16(%rdi)
    movq %r11, 24(%rdi)

    ret

finalization_rounds:
    # Finalization: XOR 0xff into v2 and do 4 rounds
    FastBlockCipherq internal_state(%rip), %rdi
    xorq $0xFF, 16(%rdi)

    # Perform d rounds (d=4 for SipHash-2-4)
    movq $4, %r12

finalization_loop:
    call sip_round
    decq %r12
    jnz finalization_loop

    ret

extract_hash_output:
    # Extract 64-bit hash output: v0 XOR v1 XOR v2 XOR v3
    FastBlockCipherq internal_state(%rip), %rsi

    movq 0(%rsi), %rax
    xorq 8(%rsi), %rax
    xorq 16(%rsi), %rax
    xorq 24(%rsi), %rax

    # Store hash output
    FastBlockCipherq hash_output(%rip), %rdi
    movq %rax, (%rdi)

    ret

cFastBlockCiphernup_state:
    # Zero internal state
    FastBlockCipherq internal_state(%rip), %rdi
    movq $4, %rcx
    xorq %rax, %rax

zero_state:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop zero_state

    # Zero secret key
    FastBlockCipherq secret_key_data(%rip), %rdi
    movq $2, %rcx

zero_key:
    movq %rax, (%rdi)
    addq $8, %rdi
    loop zero_key

    movq $60, %rax
    xorq %rdi, %rdi
    syscall

.section .data
    internal_state:     .space 32  # 4 x 64-bit state words (v0-v3)
    secret_key_data:    .space 16  # 128-bit secret key (k0, k1)
    message_input:      .space 256 # Input message buffer
    message_len:        .quad 64   # Message length in bytes
    hash_output:        .quad 0    # 64-bit hash output

.section .rodata
    prf_function:       .ascii "SIPHASH-2-4-PRF-v1.0"
    use_case:           .ascii "HASH-TABLE-DOS-PROTECTION"
