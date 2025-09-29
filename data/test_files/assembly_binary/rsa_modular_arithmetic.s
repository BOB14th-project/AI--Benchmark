# RSA Modular Arithmetic Implementation
# x86_64 Assembly for RSA encryption operations

.section .text
.global _main

_main:
    # RSA key generation and modular exponentiation
    pushq %rbp
    movq %rsp, %rbp

    # Initialize RSA parameters
    movq $61, %rax          # Small prime p for demo
    movq $53, %rbx          # Small prime q for demo
    mulq %rbx               # n = p * q
    movq %rax, %r8          # Store modulus n

    # Public exponent e = 65537
    movq $65537, %r9

    # Calculate phi(n) = (p-1)(q-1)
    movq $60, %rax          # p-1
    movq $52, %rbx          # q-1
    mulq %rbx
    movq %rax, %r10         # Store phi(n)

    # RSA encryption: c = m^e mod n
    movq $42, %rdi          # Message m
    movq %r9, %rsi          # Exponent e
    movq %r8, %rdx          # Modulus n
    call modular_exponentiation

    # Store ciphertext
    movq %rax, %r11

    # Calculate private exponent d (simplified)
    movq $2, %rcx
find_private_key:
    movq %rcx, %rax
    movq %r9, %rbx
    mulq %rbx
    xorq %rdx, %rdx
    divq %r10
    cmpq $1, %rdx
    je found_private_key
    incq %rcx
    cmpq $1000, %rcx
    jl find_private_key

found_private_key:
    movq %rcx, %r12         # Store private exponent d

    # RSA decryption: m = c^d mod n
    movq %r11, %rdi         # Ciphertext c
    movq %r12, %rsi         # Private exponent d
    movq %r8, %rdx          # Modulus n
    call modular_exponentiation

    # Exit
    movq $60, %rax          # sys_exit
    movq $0, %rdi           # Exit status
    syscall

# Modular exponentiation function
# Input: %rdi = base, %rsi = exponent, %rdx = modulus
# Output: %rax = result
modular_exponentiation:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %rcx
    pushq %r8
    pushq %r9

    movq $1, %rax           # Result = 1
    movq %rdi, %rbx         # Base
    movq %rsi, %rcx         # Exponent
    movq %rdx, %r8          # Modulus

mod_exp_loop:
    testq %rcx, %rcx        # Check if exponent is 0
    jz mod_exp_done

    testq $1, %rcx          # Check if exponent is odd
    jz mod_exp_even

    # result = (result * base) % modulus
    mulq %rbx
    xorq %rdx, %rdx
    divq %r8
    movq %rdx, %rax         # Keep remainder

mod_exp_even:
    # base = (base * base) % modulus
    movq %rbx, %r9
    movq %rbx, %rax
    mulq %r9
    xorq %rdx, %rdx
    divq %r8
    movq %rdx, %rbx         # Update base

    shrq $1, %rcx           # exponent = exponent / 2
    jmp mod_exp_loop

mod_exp_done:
    popq %r9
    popq %r8
    popq %rcx
    popq %rbx
    popq %rbp
    ret