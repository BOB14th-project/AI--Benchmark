; Public Key Digital Signature Implementation
; Based on discrete logarithm problem

section .data
    prime_p: times 32 dq 0      ; Large prime modulus
    generator_g: times 32 dq 0   ; Generator element
    subgroup_q: times 32 dq 0    ; Prime order of subgroup
    
section .text
    global signature_generation
    global signature_verification
    global modular_exponentiation

; Signature generation function
; Arguments: rdi = message_hash, rsi = private_key, rdx = signature_output
signature_generation:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 512            ; Stack space for temporaries
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15
    
    mov     r12, rdi            ; Message hash pointer
    mov     r13, rsi            ; Private key pointer
    mov     r14, rdx            ; Signature output pointer
    
    ; Generate random ephemeral key k
    lea     rdi, [rbp-256]
    call    generate_random_nonce
    
    ; Compute r = g^k mod p
    mov     rdi, [rel generator_g]
    lea     rsi, [rbp-256]      ; k
    mov     rdx, [rel prime_p]
    lea     rcx, [rbp-128]      ; result r
    call    modular_exponentiation
    
    ; r = r mod q
    lea     rdi, [rbp-128]
    mov     rsi, [rel subgroup_q]
    call    modular_reduction
    
    ; Store r as first signature component
    mov     rax, [rbp-128]
    mov     [r14], rax
    
    ; Compute e = H(z || M) where z is deterministic value
    mov     rdi, r12            ; Message hash
    lea     rsi, [rbp-128]      ; r value
    lea     rdx, [rbp-64]       ; Output e
    call    compute_hash_combination
    
    ; Compute s = x * (k - e) mod q
    ; First: k - e
    lea     rdi, [rbp-256]      ; k
    lea     rsi, [rbp-64]       ; e
    mov     rdx, [rel subgroup_q]
    call    modular_subtraction
    mov     r15, rax            ; k - e
    
    ; Second: x * (k - e)
    mov     rdi, r13            ; Private key x
    mov     rsi, r15            ; k - e
    mov     rdx, [rel subgroup_q]
    call    modular_multiplication
    
    ; Store s as second signature component
    mov     [r14+8], rax
    
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    add     rsp, 512
    pop     rbp
    ret

; Modular exponentiation using square-and-multiply
; Arguments: rdi = base, rsi = exponent, rdx = modulus, rcx = result
modular_exponentiation:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    
    mov     r12, rdi            ; base
    mov     r13, rsi            ; exponent
    mov     r14, rdx            ; modulus
    mov     r15, rcx            ; result pointer
    
    ; Initialize result = 1
    mov     qword [r15], 1
    
.exp_loop:
    ; Test if exponent bit 0 is set
    test    r13, 1
    jz      .skip_multiply
    
    ; result = (result * base) mod modulus
    mov     rdi, r15
    mov     rsi, r12
    mov     rdx, r14
    call    montgomery_multiply
    mov     [r15], rax
    
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
    
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

; Montgomery multiplication for efficient modular arithmetic
montgomery_multiply:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    
    ; Load operands
    mov     rax, [rdi]
    mov     rbx, [rsi]
    mov     r12, [rdx]          ; modulus
    
    ; Multiply: rdx:rax = rax * rbx
    mul     rbx
    
    ; Montgomery reduction
    mov     rcx, rax
    mov     r13, rdx
    
    ; m = (T mod R) * N' mod R
    mov     r8, rcx
    imul    r8, qword [rel montgomery_constant]
    
    ; t = (T + m * N) / R
    mov     rax, r8
    mul     r12
    add     rax, rcx
    adc     rdx, r13
    
    ; Conditional subtraction
    cmp     rdx, r12
    jb      .no_sub
    sub     rdx, r12
    
.no_sub:
    mov     rax, rdx
    
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

signature_verification:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 256
    
    ; rdi = message_hash, rsi = signature, rdx = public_key
    mov     r12, rdi
    mov     r13, rsi
    mov     r14, rdx
    
    ; Extract r, s from signature
    mov     r8, [r13]           ; r
    mov     r9, [r13+8]         ; s
    
    ; Compute e = H(z || M)
    mov     rdi, r12
    mov     rsi, r8
    lea     rdx, [rbp-64]
    call    compute_hash_combination
    
    ; Compute y^s mod p
    mov     rdi, r14            ; public key y
    mov     rsi, r9             ; s
    mov     rdx, [rel prime_p]
    lea     rcx, [rbp-128]
    call    modular_exponentiation
    
    ; Compute g^e mod p
    mov     rdi, [rel generator_g]
    lea     rsi, [rbp-64]       ; e
    mov     rdx, [rel prime_p]
    lea     rcx, [rbp-192]
    call    modular_exponentiation
    
    ; v = (y^s * g^e) mod p mod q
    lea     rdi, [rbp-128]
    lea     rsi, [rbp-192]
    mov     rdx, [rel prime_p]
    call    modular_multiplication
    
    mov     rsi, [rel subgroup_q]
    call    modular_reduction
    
    ; Compare v with r
    cmp     rax, r8
    sete    al
    
    add     rsp, 256
    pop     rbp
    ret

section .data
    montgomery_constant: dq 0xFFFFFFFFFFFFFFFF
