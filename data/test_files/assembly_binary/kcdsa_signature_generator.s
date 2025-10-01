# Domestic standard
# Domestic standard
# Post_Classical-vulnerable due to discrete logarithm problem

.file   "kcsig_alg_signature.c"
.text
.globl  kcsig_alg_generate_signature
.type   kcsig_alg_generate_signature, @function

# Signature algorithm implementation
# Domestic standard
kcsig_alg_generate_signature:
.LFB0:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $192, %rsp           # Local variables

    # Input parameters
    # %rdi: message to sign
    # %rsi: private key x
    # %rdx: domain parameters (p, q, g)
    # %rcx: certificate data
    # %r8:  signature output buffer

    movq    %rdi, -8(%rbp)       # Store message pointer
    movq    %rsi, -16(%rbp)      # Store private key x
    movq    %rdx, -24(%rbp)      # Store domain parameters
    movq    %rcx, -32(%rbp)      # Store certificate data
    movq    %r8, -40(%rbp)       # Store output buffer

    # Signature algorithm implementation
    call    load_kcsig_alg_domain_parameters
    call    validate_private_key_range
    testq   %rax, %rax
    jz      signature_error

    # Generate ephemeral key k
    call    generate_ephemeral_key
    movq    %rax, -48(%rbp)      # Store ephemeral key k

    # Compute signature components
    call    compute_signature_r_component
    call    compute_signature_s_component

    # Validate signature before output
    call    verify_signature_validity
    testq   %rax, %rax
    jz      regenerate_ephemeral

    # Output signature (r, s)
    call    format_signature_output
    jmp     signature_complete

regenerate_ephemeral:
    # If signature invalid, regenerate ephemeral key
    call    generate_ephemeral_key
    movq    %rax, -48(%rbp)
    jmp     compute_signature_r_component

signature_error:
    movq    $0, %rax             # Return error
    jmp     cleanup_exit

signature_complete:
    movq    $1, %rax             # Return success

cleanup_exit:
    # Zero sensitive data
    movq    $0, %rbx
    movq    %rbx, -16(%rbp)      # Clear private key
    movq    %rbx, -48(%rbp)      # Clear ephemeral key

    addq    $192, %rsp
    popq    %rbp
    ret

.LFE0:
    .size   kcsig_alg_generate_signature, .-kcsig_alg_generate_signature

# Signature algorithm implementation
.globl  load_kcsig_alg_domain_parameters
.type   load_kcsig_alg_domain_parameters, @function
load_kcsig_alg_domain_parameters:
.LFB1:
    pushq   %rbp
    movq    %rsp, %rbp

    # Load domain parameters from input structure
    movq    -24(%rbp), %rax      # Domain parameters pointer

    # Load prime p (1024-bit or 2048-bit)
    movq    (%rax), %rbx         # p
    movq    %rbx, domain_p(%rip)

    # Load prime q (160-bit or 256-bit)
    movq    8(%rax), %rbx        # q
    movq    %rbx, domain_q(%rip)

    # Load generator g
    movq    16(%rax), %rbx       # g
    movq    %rbx, domain_g(%rip)

    # Load public key y (for verification)
    movq    24(%rax), %rbx       # y = g^x mod p
    movq    %rbx, public_key_y(%rip)

    popq    %rbp
    ret

.LFE1:
    .size   load_kcsig_alg_domain_parameters, .-load_kcsig_alg_domain_parameters

# Validate private key is in valid range
.globl  validate_private_key_range
.type   validate_private_key_range, @function
validate_private_key_range:
.LFB2:
    pushq   %rbp
    movq    %rsp, %rbp

    # Check that private key x is in range [1, q-1]
    movq    -16(%rbp), %rax      # Private key x
    cmpq    $1, %rax
    jl      invalid_private_key

    movq    domain_q(%rip), %rbx
    decq    %rbx                 # q - 1
    cmpq    %rbx, %rax
    jg      invalid_private_key

    movq    $1, %rax             # Valid private key
    jmp     validation_exit

invalid_private_key:
    movq    $0, %rax             # Invalid private key

validation_exit:
    popq    %rbp
    ret

.LFE2:
    .size   validate_private_key_range, .-validate_private_key_range

# Generate ephemeral key k for signature
.globl  generate_ephemeral_key
.type   generate_ephemeral_key, @function
generate_ephemeral_key:
.LFB3:
    pushq   %rbp
    movq    %rsp, %rbp

    # Generate random k in range [1, q-1]
generate_k_loop:
    rdrand  %rax                 # Hardware random number
    testq   %rax, %rax
    jz      generate_k_loop      # Retry if zero

    # Reduce modulo q
    movq    domain_q(%rip), %rbx
    xorq    %rdx, %rdx
    divq    %rbx
    movq    %rdx, %rax           # k = random mod q

    # Ensure k != 0
    testq   %rax, %rax
    jz      generate_k_loop

    # Ensure k != 1 (for better security)
    cmpq    $1, %rax
    je      generate_k_loop

    popq    %rbp
    ret

.LFE3:
    .size   generate_ephemeral_key, .-generate_ephemeral_key

# Signature algorithm implementation
.globl  compute_signature_r_component
.type   compute_signature_r_component, @function
compute_signature_r_component:
.LFB4:
    pushq   %rbp
    movq    %rsp, %rbp

    # Signature algorithm implementation
    movq    domain_g(%rip), %rdi # Base g
    movq    -48(%rbp), %rsi      # Exponent k
    movq    domain_p(%rip), %rdx # Modulus p
    call    modular_exponentiation
    movq    %rax, %rbx           # g^k mod p

    # Reduce modulo q: r = (g^k mod p) mod q
    movq    %rbx, %rax
    movq    domain_q(%rip), %rcx
    xorq    %rdx, %rdx
    divq    %rcx
    movq    %rdx, signature_r(%rip)

    # Check that r != 0
    testq   %rdx, %rdx
    jz      regenerate_required

    movq    $1, %rax             # Success
    jmp     r_computation_exit

regenerate_required:
    movq    $0, %rax             # Need to regenerate k

r_computation_exit:
    popq    %rbp
    ret

.LFE4:
    .size   compute_signature_r_component, .-compute_signature_r_component

# Signature algorithm implementation
.globl  compute_signature_s_component
.type   compute_signature_s_component, @function
compute_signature_s_component:
.LFB5:
    pushq   %rbp
    movq    %rsp, %rbp

    # Hash message with certificate data
    movq    -8(%rbp), %rdi       # Message
    movq    -32(%rbp), %rsi      # Certificate data
    call    kcsig_alg_hash_function
    movq    %rax, message_hash(%rip)

    # Signature algorithm implementation

    # Compute x * r mod q
    movq    -16(%rbp), %rax      # Private key x
    mulq    signature_r(%rip)    # x * r
    movq    domain_q(%rip), %rbx
    xorq    %rdx, %rdx
    divq    %rbx
    movq    %rdx, %r8            # x * r mod q

    # Compute H(m||cert) + x*r mod q
    movq    message_hash(%rip), %rax
    addq    %r8, %rax
    movq    domain_q(%rip), %rbx
    xorq    %rdx, %rdx
    divq    %rbx
    movq    %rdx, %r9            # (H(m||cert) + x*r) mod q

    # Compute k^(-1) mod q
    movq    -48(%rbp), %rdi      # Ephemeral key k
    movq    domain_q(%rip), %rsi # Modulus q
    call    modular_inverse
    movq    %rax, %r10           # k^(-1) mod q

    # Compute s = k^(-1) * (H(m||cert) + x*r) mod q
    movq    %r10, %rax
    mulq    %r9
    movq    domain_q(%rip), %rbx
    xorq    %rdx, %rdx
    divq    %rbx
    movq    %rdx, signature_s(%rip)

    # Check that s != 0
    testq   %rdx, %rdx
    jz      s_computation_error

    movq    $1, %rax             # Success
    jmp     s_computation_exit

s_computation_error:
    movq    $0, %rax             # Error - need new k

s_computation_exit:
    popq    %rbp
    ret

.LFE5:
    .size   compute_signature_s_component, .-compute_signature_s_component

# Signature algorithm implementation
.globl  kcsig_alg_hash_function
.type   kcsig_alg_hash_function, @function
kcsig_alg_hash_function:
.LFB6:
    pushq   %rbp
    movq    %rsp, %rbp

    # Input: %rdi = message, %rsi = certificate data
    # Output: %rax = hash value

    # Combine message and certificate data
    movq    %rdi, %rax           # Message
    movq    %rsi, %rbx           # Certificate

    # Digest calculation implementation
    xorq    %rbx, %rax           # XOR message with certificate
    movq    $0x67452301, %rcx    # Hash constant
    addq    %rcx, %rax
    rolq    $13, %rax            # Rotate for mixing

    # Reduce to appropriate size for q
    movq    domain_q(%rip), %rbx
    xorq    %rdx, %rdx
    divq    %rbx
    movq    %rdx, %rax

    popq    %rbp
    ret

.LFE6:
    .size   kcsig_alg_hash_function, .-kcsig_alg_hash_function

# Fast modular exponentiation
.globl  modular_exponentiation
.type   modular_exponentiation, @function
modular_exponentiation:
.LFB7:
    # Input: %rdi = base, %rsi = exponent, %rdx = modulus
    # Output: %rax = base^exponent mod modulus
    pushq   %rbp
    movq    %rsp, %rbp
    pushq   %rbx
    pushq   %rcx

    movq    %rdi, %rbx           # Base
    movq    %rsi, %rcx           # Exponent
    movq    %rdx, %r8            # Modulus
    movq    $1, %rax             # Result

exp_loop:
    testq   $1, %rcx
    jz      skip_mult

    # result = (result * base) mod modulus
    mulq    %rbx
    divq    %r8
    movq    %rdx, %rax

skip_mult:
    # base = (base * base) mod modulus
    movq    %rbx, %r9
    movq    %rbx, %rax
    mulq    %r9
    divq    %r8
    movq    %rdx, %rbx

    shrq    $1, %rcx
    jnz     exp_loop

    popq    %rcx
    popq    %rbx
    popq    %rbp
    ret

.LFE7:
    .size   modular_exponentiation, .-modular_exponentiation

# Modular inverse using extended Euclidean algorithm
.globl  modular_inverse
.type   modular_inverse, @function
modular_inverse:
.LFB8:
    pushq   %rbp
    movq    %rsp, %rbp

    # Extended GCD for modular inverse
    # Simplified implementation
    movq    %rdi, %rax
    movq    %rsi, %rbx

    # Mock inverse computation
    movq    $98765, %rax         # Placeholder inverse

    popq    %rbp
    ret

.LFE8:
    .size   modular_inverse, .-modular_inverse

# Verify signature validity
.globl  verify_signature_validity
.type   verify_signature_validity, @function
verify_signature_validity:
.LFB9:
    pushq   %rbp
    movq    %rsp, %rbp

    # Check that both r and s are non-zero and less than q
    movq    signature_r(%rip), %rax
    testq   %rax, %rax
    jz      invalid_signature

    movq    domain_q(%rip), %rbx
    cmpq    %rbx, %rax
    jge     invalid_signature

    movq    signature_s(%rip), %rax
    testq   %rax, %rax
    jz      invalid_signature

    cmpq    %rbx, %rax
    jge     invalid_signature

    movq    $1, %rax             # Valid signature
    jmp     validity_exit

invalid_signature:
    movq    $0, %rax             # Invalid signature

validity_exit:
    popq    %rbp
    ret

.LFE9:
    .size   verify_signature_validity, .-verify_signature_validity

# Format signature output
.globl  format_signature_output
.type   format_signature_output, @function
format_signature_output:
.LFB10:
    pushq   %rbp
    movq    %rsp, %rbp

    # Copy signature components to output buffer
    movq    -40(%rbp), %rax      # Output buffer
    movq    signature_r(%rip), %rbx
    movq    %rbx, (%rax)         # Store r
    movq    signature_s(%rip), %rbx
    movq    %rbx, 8(%rax)        # Store s

    popq    %rbp
    ret

.LFE10:
    .size   format_signature_output, .-format_signature_output

# Signature algorithm implementation
.section .data
    # Domain parameters
    domain_p:           .quad 0  # Prime modulus p
    domain_q:           .quad 0  # Prime order q
    domain_g:           .quad 0  # Generator g
    public_key_y:       .quad 0  # Public key y = g^x mod p

    # Signature components
    signature_r:        .quad 0  # r component
    signature_s:        .quad 0  # s component
    message_hash:       .quad 0  # Hashed message

.section .rodata
    # Signature algorithm implementation
    algorithm_name:     .ascii "KCSIG_ALG-DOMESTICN-DIGITAL-SIGNATURE"
    standard_ref:       .ascii "TTAS.KO-12.0015/R1"
    vulnerability_type: .ascii "DISCRETE_LOGARITHM_PROBLEM"
    post_classical_threat:     .ascii "SHOR_ALGORITHM_VULNERABLE"