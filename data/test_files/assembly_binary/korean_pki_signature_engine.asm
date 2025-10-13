; Digital Signature Engine - Modular Arithmetic Implementation
; Uses Montgomery multiplication for efficiency

section .data
    prime_modulus: times 32 dq 0
    montgomery_r: times 32 dq 0

section .text
    global signature_generate
    global signature_verify
    global modular_exp

; Modular exponentiation using square-and-multiply
modular_exp:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15
    
    ; Arguments: rdi=base, rsi=exponent, rdx=modulus, rcx=result
    mov     r12, rdi    ; base
    mov     r13, rsi    ; exponent
    mov     r14, rdx    ; modulus
    mov     r15, rcx    ; result pointer
    
    ; Initialize result = 1
    mov     qword [r15], 1
    
.exp_loop:
    ; Check if exponent bit is set
    bt      r13, 0
    jnc     .skip_multiply
    
    ; result = (result * base) mod modulus
    mov     rdi, r15
    mov     rsi, r12
    mov     rdx, r14
    call    montgomery_multiply
    
.skip_multiply:
    ; base = (base * base) mod modulus
    mov     rdi, r12
    mov     rsi, r12
    mov     rdx, r14
    call    montgomery_multiply
    mov     r12, rax
    
    ; exponent >>= 1
    shr     r13, 1
    jnz     .exp_loop
    
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

; Montgomery multiplication
montgomery_multiply:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    
    ; rdi = a, rsi = b, rdx = modulus
    mov     rax, rdi
    mul     rsi         ; rdx:rax = a * b
    
    ; Montgomery reduction
    mov     rcx, [rel montgomery_r]
    mul     rcx
    add     rax, rdx
    mov     rbx, rax
    
    ; Conditional subtraction
    mov     rax, [rel prime_modulus]
    cmp     rbx, rax
    jl      .no_sub
    sub     rbx, rax
    
.no_sub:
    mov     rax, rbx
    
    pop     r12
    pop     rbx
    pop     rbp
    ret

signature_generate:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 256
    
    ; rdi = message_hash, rsi = private_key, rdx = signature_out
    mov     r12, rdi
    mov     r13, rsi
    mov     r14, rdx
    
    ; Generate random k
    lea     rdi, [rbp-128]
    call    generate_random_k
    
    ; Compute r = g^k mod p
    mov     rdi, [rel prime_modulus]
    lea     rsi, [rbp-128]
    mov     rdx, [rel prime_modulus]
    lea     rcx, [rbp-64]
    call    modular_exp
    
    ; Store r in signature
    mov     rax, [rbp-64]
    mov     [r14], rax
    
    ; Compute s = k^-1 * (H(m) + x*r) mod q
    mov     rdi, r12
    mov     rsi, r13
    mov     rdx, rax
    call    compute_s_value
    
    mov     [r14+8], rax
    
    add     rsp, 256
    pop     rbp
    ret

signature_verify:
    push    rbp
    mov     rbp, rsp
    
    ; Verification logic
    ; w = s^-1 mod q
    ; u1 = H(m)*w mod q
    ; u2 = r*w mod q
    ; v = (g^u1 * y^u2 mod p) mod q
    ; return v == r
    
    pop     rbp
    ret
