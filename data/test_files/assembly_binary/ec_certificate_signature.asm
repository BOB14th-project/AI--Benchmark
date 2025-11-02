; Elliptic Curve Certificate Signature
; EC variant with certificate support

section .data
    ; EC curve parameters
    curve_prime: dq 0xFFFFFFFF00000001, 0x0000000000000000
    curve_a: dq 0xFFFFFFFF00000001, 0x00000000FFFFFFFC
    curve_b: dq 0x5AC635D8AA3A93E7, 0xB3EBBD55769886BC
    base_point_x: dq 0x6B17D1F2E12C4247, 0xF8BCE6E563A440F2
    base_point_y: dq 0x4FE342E2FE1A7F9B, 0x8EE7EB4A7C0F9E16
    curve_order: dq 0xFFFFFFFF00000000, 0xFFFFFFFFFFFFFFFF

section .text
    global ec_sign_cert
    global ec_point_add
    global ec_scalar_mult

; EC point addition
ec_point_add:
    push rbp
    mov rbp, rsp

    ; Load points P and Q
    mov rax, [rdi]          ; P.x
    mov rbx, [rdi + 8]      ; P.y
    mov rcx, [rsi]          ; Q.x
    mov rdx, [rsi + 8]      ; Q.y

    ; Compute slope
    sub rdx, rbx            ; y2 - y1
    sub rcx, rax            ; x2 - x1
    ; s = (y2-y1)/(x2-x1) mod p
    call ec_field_div

    ; x3 = s^2 - x1 - x2
    imul rax, rax
    sub rax, [rdi]
    sub rax, [rsi]

    ; y3 = s(x1 - x3) - y1
    mov rbx, [rdi]
    sub rbx, rax
    imul rbx, rdx

    pop rbp
    ret

; EC scalar multiplication
ec_scalar_mult:
    push rbp
    mov rbp, rsp

    xor r10, r10            ; result = point at infinity

.scalar_loop:
    test rsi, 1
    jz .skip_add

    ; Add point to result
    mov rdi, r10
    call ec_point_add
    mov r10, rax

.skip_add:
    ; Double the point
    mov rdi, rdi
    call ec_point_add

    shr rsi, 1
    test rsi, rsi
    jnz .scalar_loop

    mov rax, r10
    pop rbp
    ret

; Sign certificate with EC
ec_sign_cert:
    push rbp
    mov rbp, rsp

    ; Hash certificate
    call hash_cert_160bit

    ; Generate random k
    rdrand r8

    ; Compute k*G
    lea rdi, [rel base_point_x]
    mov rsi, r8
    call ec_scalar_mult

    ; r = x1 mod n
    mov rbx, rax
    mov rsi, [rel curve_order]
    call mod_reduce
    mov [rbp - 8], rax      ; signature r

    ; s = k^-1(H(m) + dr) mod n
    mov rdi, r8
    mov rsi, [rel curve_order]
    call mod_inverse
    ; ... compute s

    pop rbp
    ret

ec_field_div:
    ret
