# Mathematical curve implementation
# Signature algorithm implementation
# Curve computation implementation

.file   "curve_scalar_mult.c"
.text
.globl  ec_scalar_multiplication
.type   ec_scalar_multiplication, @function

# Function: ec_scalar_multiplication
# Performs k*P on elliptic curve (scalar point multiplication)
# Signature algorithm implementation

ec_scalar_multiplication:
.LFB0:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $128, %rsp              # Local stack space

    # Input parameters (calling convention)
    # %rdi: scalar k (256-bit)
    # %rsi: point P coordinates
    # %rdx: curve parameters
    # %rcx: output buffer

    movq    %rdi, -8(%rbp)          # Store scalar k
    movq    %rsi, -16(%rbp)         # Store point P
    movq    %rdx, -24(%rbp)         # Store curve params
    movq    %rcx, -32(%rbp)         # Store output buffer

    # Initialize point at infinity (identity element)
    call    initialize_point_at_infinity
    movq    %rax, -40(%rbp)         # Store result point R

    # Binary method for scalar multiplication
    # Process each bit of scalar k from MSB to LSB
    movq    $255, -48(%rbp)         # Bit counter (256-bit scalar)

scalar_mult_loop:
    # R = 2*R (point doubling)
    movq    -40(%rbp), %rdi         # Current result point
    movq    -24(%rbp), %rsi         # Curve parameters
    call    elliptic_point_double
    movq    %rax, -40(%rbp)         # Update result

    # Check if current bit of k is set
    movq    -8(%rbp), %rax          # Scalar k
    movq    -48(%rbp), %rcx         # Bit position
    btq     %rcx, %rax              # Test bit
    jnc     skip_point_add          # Skip if bit is 0

    # R = R + P (point addition)
    movq    -40(%rbp), %rdi         # Current result
    movq    -16(%rbp), %rsi         # Base point P
    movq    -24(%rbp), %rdx         # Curve parameters
    call    elliptic_point_add
    movq    %rax, -40(%rbp)         # Update result

skip_point_add:
    decq    -48(%rbp)               # Decrement bit counter
    jns     scalar_mult_loop        # Continue if non-negative

    # Copy result to output buffer
    movq    -40(%rbp), %rsi         # Source: result point
    movq    -32(%rbp), %rdi         # Destination: output buffer
    movq    $64, %rcx               # Copy 64 bytes (2 coordinates)
    rep movsb                       # Memory copy

    movq    -40(%rbp), %rax         # Return result point
    addq    $128, %rsp              # Restore stack
    popq    %rbp
    ret

.LFE0:
    .size   ec_scalar_multiplication, .-ec_scalar_multiplication

# Mathematical curve implementation
.globl  elliptic_point_double
.type   elliptic_point_double, @function

elliptic_point_double:
.LFB1:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $96, %rsp

    movq    %rdi, -8(%rbp)          # Point P
    movq    %rsi, -16(%rbp)         # Curve parameters

    # Check if point is at infinity
    movq    -8(%rbp), %rax
    cmpq    $0, 32(%rax)            # Check infinity flag
    jne     return_infinity

    # Load point coordinates
    movq    -8(%rbp), %rax
    movq    (%rax), %rbx            # P.x
    movq    8(%rax), %rcx           # P.y
    movq    -16(%rbp), %rdx
    movq    (%rdx), %r8             # curve.a parameter
    movq    8(%rdx), %r9            # curve.p (prime modulus)

    # Compute slope λ = (3*x^2 + a) / (2*y) mod p
    # First: 3*x^2 mod p
    movq    %rbx, %rax              # x
    mulq    %rbx                    # x^2
    movq    %r9, %rdi               # modulus p
    call    mod_reduce              # x^2 mod p
    movq    %rax, %r10              # Store x^2 mod p

    movq    $3, %rax
    mulq    %r10                    # 3*x^2
    movq    %r9, %rdi
    call    mod_reduce              # 3*x^2 mod p
    addq    %r8, %rax               # 3*x^2 + a
    movq    %r9, %rdi
    call    mod_reduce              # (3*x^2 + a) mod p
    movq    %rax, -24(%rbp)         # Store numerator

    # Compute 2*y mod p
    movq    $2, %rax
    mulq    %rcx                    # 2*y
    movq    %r9, %rdi
    call    mod_reduce              # 2*y mod p
    movq    %rax, %rdi

    # Compute modular inverse of 2*y
    movq    %r9, %rsi               # modulus
    call    mod_inverse             # (2*y)^(-1) mod p
    movq    %rax, %rdi

    # Compute slope λ = numerator * inverse
    movq    -24(%rbp), %rax         # numerator
    mulq    %rdi                    # numerator * inverse
    movq    %r9, %rdi
    call    mod_reduce              # λ mod p
    movq    %rax, -32(%rbp)         # Store slope λ

    # Compute new x coordinate: x3 = λ^2 - 2*x mod p
    movq    -32(%rbp), %rax         # λ
    mulq    %rax                    # λ^2
    movq    %r9, %rdi
    call    mod_reduce              # λ^2 mod p

    movq    $2, %rdx
    mulq    %rbx                    # 2*x
    movq    %r9, %rdi
    call    mod_reduce              # 2*x mod p
    movq    %rax, %rdi

    movq    -32(%rbp), %rax         # λ^2 mod p (recompute)
    movq    -32(%rbp), %rdx
    mulq    %rdx
    movq    %r9, %rdx
    call    mod_reduce

    subq    %rdi, %rax              # λ^2 - 2*x
    movq    %r9, %rdi
    call    mod_reduce              # x3 mod p
    movq    %rax, -40(%rbp)         # Store x3

    # Compute new y coordinate: y3 = λ*(x - x3) - y mod p
    movq    %rbx, %rax              # x
    subq    -40(%rbp), %rax         # x - x3
    movq    %r9, %rdi
    call    mod_reduce              # (x - x3) mod p

    movq    -32(%rbp), %rdx         # λ
    mulq    %rdx                    # λ*(x - x3)
    movq    %r9, %rdi
    call    mod_reduce              # λ*(x - x3) mod p

    subq    %rcx, %rax              # λ*(x - x3) - y
    movq    %r9, %rdi
    call    mod_reduce              # y3 mod p
    movq    %rax, -48(%rbp)         # Store y3

    # Allocate result point structure
    movq    $40, %rdi               # Size of point structure
    call    malloc
    movq    %rax, -56(%rbp)         # Store result pointer

    # Fill result point
    movq    -56(%rbp), %rax
    movq    -40(%rbp), %rbx         # x3
    movq    %rbx, (%rax)            # result.x = x3
    movq    -48(%rbp), %rbx         # y3
    movq    %rbx, 8(%rax)           # result.y = y3
    movq    $0, 16(%rax)            # result.z = 1 (affine coordinates)
    movq    $0, 32(%rax)            # result.infinity = false

    movq    -56(%rbp), %rax         # Return result
    jmp     double_exit

return_infinity:
    call    create_point_at_infinity
    # %rax already contains infinity point

double_exit:
    addq    $96, %rsp
    popq    %rbp
    ret

.LFE1:
    .size   elliptic_point_double, .-elliptic_point_double

# Mathematical curve implementation
.globl  elliptic_point_add
.type   elliptic_point_add, @function

elliptic_point_add:
.LFB2:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $80, %rsp

    movq    %rdi, -8(%rbp)          # Point P
    movq    %rsi, -16(%rbp)         # Point Q
    movq    %rdx, -24(%rbp)         # Curve parameters

    # Special cases: check for point at infinity
    movq    -8(%rbp), %rax
    cmpq    $0, 32(%rax)            # P.infinity?
    jne     return_q

    movq    -16(%rbp), %rax
    cmpq    $0, 32(%rax)            # Q.infinity?
    jne     return_p

    # Load coordinates
    movq    -8(%rbp), %rax
    movq    (%rax), %rbx            # P.x
    movq    8(%rax), %rcx           # P.y

    movq    -16(%rbp), %rax
    movq    (%rax), %r8             # Q.x
    movq    8(%rax), %r9            # Q.y

    # Check if points are equal
    cmpq    %rbx, %r8               # P.x == Q.x?
    jne     different_x

    cmpq    %rcx, %r9               # P.y == Q.y?
    je      call_point_double       # P == Q, use doubling

    # P.x == Q.x but P.y != Q.y => P + Q = O (infinity)
    call    create_point_at_infinity
    jmp     add_exit

different_x:
    # Compute slope λ = (Q.y - P.y) / (Q.x - P.x) mod p
    movq    %r9, %rax               # Q.y
    subq    %rcx, %rax              # Q.y - P.y
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi           # curve.p
    call    mod_reduce              # (Q.y - P.y) mod p
    movq    %rax, -32(%rbp)         # Store numerator

    movq    %r8, %rax               # Q.x
    subq    %rbx, %rax              # Q.x - P.x
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi           # curve.p
    call    mod_reduce              # (Q.x - P.x) mod p

    # Compute modular inverse
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rsi           # modulus p
    movq    %rax, %rdi              # (Q.x - P.x) mod p
    call    mod_inverse             # inverse

    # Compute slope
    movq    -32(%rbp), %rdx         # numerator
    mulq    %rdx                    # slope λ
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi           # curve.p
    call    mod_reduce
    movq    %rax, -40(%rbp)         # Store slope λ

    # Compute result coordinates (similar to doubling but different formula)
    # x3 = λ^2 - P.x - Q.x mod p
    movq    -40(%rbp), %rax         # λ
    mulq    %rax                    # λ^2
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi
    call    mod_reduce              # λ^2 mod p

    subq    %rbx, %rax              # λ^2 - P.x
    subq    %r8, %rax               # λ^2 - P.x - Q.x
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi
    call    mod_reduce              # x3 mod p
    movq    %rax, -48(%rbp)         # Store x3

    # y3 = λ*(P.x - x3) - P.y mod p
    movq    %rbx, %rax              # P.x
    subq    -48(%rbp), %rax         # P.x - x3
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi
    call    mod_reduce

    movq    -40(%rbp), %rdx         # λ
    mulq    %rdx                    # λ*(P.x - x3)
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi
    call    mod_reduce

    subq    %rcx, %rax              # λ*(P.x - x3) - P.y
    movq    -24(%rbp), %rdi
    movq    8(%rdi), %rdi
    call    mod_reduce              # y3 mod p
    movq    %rax, -56(%rbp)         # Store y3

    # Create result point
    movq    $40, %rdi
    call    malloc
    movq    %rax, -64(%rbp)

    movq    -64(%rbp), %rax
    movq    -48(%rbp), %rbx         # x3
    movq    %rbx, (%rax)
    movq    -56(%rbp), %rbx         # y3
    movq    %rbx, 8(%rax)
    movq    $1, 16(%rax)            # z = 1
    movq    $0, 32(%rax)            # infinity = false

    movq    -64(%rbp), %rax
    jmp     add_exit

call_point_double:
    movq    -8(%rbp), %rdi          # Point P
    movq    -24(%rbp), %rsi         # Curve parameters
    call    elliptic_point_double
    jmp     add_exit

return_p:
    movq    -8(%rbp), %rax
    jmp     add_exit

return_q:
    movq    -16(%rbp), %rax

add_exit:
    addq    $80, %rsp
    popq    %rbp
    ret

.LFE2:
    .size   elliptic_point_add, .-elliptic_point_add

# Utility functions
.globl  mod_reduce
.type   mod_reduce, @function
mod_reduce:
    # Input: %rax = value, %rdi = modulus
    # Output: %rax = value mod modulus
    xorq    %rdx, %rdx
    divq    %rdi
    movq    %rdx, %rax
    ret

.globl  mod_inverse
.type   mod_inverse, @function
mod_inverse:
    # Extended Euclidean algorithm for modular inverse
    # Simplified implementation
    pushq   %rbp
    movq    %rsp, %rbp
    # ... implementation details ...
    # Returns multiplicative inverse
    popq    %rbp
    ret

.globl  initialize_point_at_infinity
.type   initialize_point_at_infinity, @function
initialize_point_at_infinity:
    movq    $40, %rdi
    call    malloc
    movq    $0, (%rax)              # x = 0
    movq    $0, 8(%rax)             # y = 0
    movq    $0, 16(%rax)            # z = 0
    movq    $1, 32(%rax)            # infinity = true
    ret

.globl  create_point_at_infinity
.type   create_point_at_infinity, @function
create_point_at_infinity:
    jmp     initialize_point_at_infinity

# Curve computation implementation
.section .rodata
    .align 8
curve_secp256r1_p:      .quad 0xFFFFFFFFFFFFFFFF, 0x00000000FFFFFFFF, 0x0000000000000000, 0xFFFFFFFF00000001
curve_secp256r1_a:      .quad 0xFFFFFFFFFFFFFFFC, 0x00000000FFFFFFFF, 0x0000000000000000, 0xFFFFFFFF00000001
curve_secp256r1_b:      .quad 0x3BCE3C3E27D2604B, 0x651D06B0CC53B0F6, 0xB3EBBD55769886BC, 0x5AC635D8AA3A93E7

algorithm_identifier:   .ascii "CURVE-P256-SCALAR-MULTIPLICATION"
operation_type:         .ascii "ELLIPTIC_CURVE_POINT_OPS"