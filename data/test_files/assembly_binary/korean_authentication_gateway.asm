; Authentication Gateway - Hash-based Message Authentication
; Combined lightweight cipher with secure hash function

section .data
    hash_iv: dq 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    hash_iv_ext: dq 0xC3D2E1F0, 0x76543210, 0xFEDCBA98, 0x89ABCDEF

section .text
    global authenticate_message
    global compute_secure_hash
    global verify_signature

; Main authentication function combining cipher and hash
authenticate_message:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 256
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15
    
    mov     r12, rdi            ; Message pointer
    mov     r13, rsi            ; Message length
    mov     r14, rdx            ; Key pointer
    mov     r15, rcx            ; Output MAC
    
    ; Step 1: Apply lightweight cipher for confidentiality
    lea     rdi, [rbp-128]      ; Intermediate buffer
    mov     rsi, r12            ; Message
    mov     rdx, r14            ; Key
    call    lightweight_cipher_64bit
    
    ; Step 2: Compute secure hash for integrity
    lea     rdi, [rbp-128]      ; Encrypted message
    mov     rsi, r13            ; Length
    mov     rdx, r15            ; Output
    call    compute_secure_hash
    
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    add     rsp, 256
    pop     rbp
    ret

; 64-bit lightweight block cipher (HIGHT-like structure)
lightweight_cipher_64bit:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    
    ; Load 64-bit block
    mov     eax, [rsi]          ; X0
    mov     ebx, [rsi+4]        ; X1
    
    ; Initial whitening
    xor     eax, [rdx]
    xor     ebx, [rdx+4]
    
    xor     ecx, ecx            ; Round counter

.cipher_rounds:
    ; F0 transformation
    mov     r8d, ebx
    rol     r8d, 1              ; Rotation 1
    mov     r9d, ebx
    rol     r9d, 2              ; Rotation 2
    xor     r8d, r9d
    mov     r9d, ebx
    rol     r9d, 7              ; Rotation 7
    xor     r8d, r9d
    
    ; Add round constant
    mov     r10d, 0x5A827999
    add     r8d, r10d
    
    ; XOR with left half
    xor     eax, r8d
    
    ; F1 transformation
    mov     r8d, eax
    rol     r8d, 3              ; Rotation 3
    mov     r9d, eax
    rol     r9d, 4              ; Rotation 4
    xor     r8d, r9d
    mov     r9d, eax
    rol     r9d, 6              ; Rotation 6
    xor     r8d, r9d
    xor     ebx, r8d
    
    inc     ecx
    cmp     ecx, 32             ; 32 rounds
    jl      .cipher_rounds
    
    ; Final whitening
    xor     eax, [rdx+8]
    xor     ebx, [rdx+12]
    
    ; Store result
    mov     [rdi], eax
    mov     [rdi+4], ebx
    
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

; Secure hash function (LSH-like structure) - 512-bit output
compute_secure_hash:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 256
    push    rbx
    push    r12
    push    r13
    push    r14
    
    mov     r12, rdi            ; Message
    mov     r13, rsi            ; Length
    mov     r14, rdx            ; Output
    
    ; Initialize 512-bit state (8 x 64-bit words)
    mov     rax, [rel hash_iv]
    mov     [rbp-64], rax
    mov     rax, [rel hash_iv + 8]
    mov     [rbp-56], rax
    mov     rax, [rel hash_iv + 16]
    mov     [rbp-48], rax
    mov     rax, [rel hash_iv + 24]
    mov     [rbp-40], rax
    
    mov     rax, [rel hash_iv_ext]
    mov     [rbp-32], rax
    mov     rax, [rel hash_iv_ext + 8]
    mov     [rbp-24], rax
    mov     rax, [rel hash_iv_ext + 16]
    mov     [rbp-16], rax
    mov     rax, [rel hash_iv_ext + 24]
    mov     [rbp-8], rax
    
    xor     ecx, ecx            ; Step counter

.compression_rounds:
    ; Load message word
    mov     eax, [r12 + rcx*4]
    mov     [rbp-128], eax
    
    ; Step function with rotations
    mov     eax, [rbp-64]
    rol     eax, 5              ; Rotate state[0]
    add     eax, [rbp-56]
    xor     eax, [rbp-48]
    add     eax, [rbp-128]      ; Add message word
    mov     [rbp-192], eax      ; Temporary
    
    ; Update state with mixing
    mov     eax, [rbp-56]
    ror     eax, 8
    mov     [rbp-64], eax
    
    mov     eax, [rbp-48]
    ror     eax, 8
    mov     [rbp-56], eax
    
    mov     eax, [rbp-40]
    ror     eax, 8
    mov     [rbp-48], eax
    
    mov     eax, [rbp-192]
    mov     [rbp-40], eax
    
    ; Second half of state
    mov     eax, [rbp-32]
    rol     eax, 7
    xor     eax, [rbp-24]
    add     eax, [rbp-128]
    mov     [rbp-32], eax
    
    inc     ecx
    cmp     ecx, 32             ; 32 steps
    jl      .compression_rounds
    
    ; Finalization and output
    mov     rax, [rbp-64]
    mov     [r14], rax
    mov     rax, [rbp-56]
    mov     [r14+8], rax
    mov     rax, [rbp-48]
    mov     [r14+16], rax
    mov     rax, [rbp-40]
    mov     [r14+24], rax
    mov     rax, [rbp-32]
    mov     [r14+32], rax
    mov     rax, [rbp-24]
    mov     [r14+40], rax
    mov     rax, [rbp-16]
    mov     [r14+48], rax
    mov     rax, [rbp-8]
    mov     [r14+56], rax
    
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    add     rsp, 256
    pop     rbp
    ret

verify_signature:
    push    rbp
    mov     rbp, rsp
    
    ; Recompute MAC and compare
    ; rdi = message, rsi = length, rdx = key, rcx = signature
    mov     r12, rcx            ; Save signature
    
    sub     rsp, 64
    mov     rcx, rsp            ; Computed MAC buffer
    
    call    authenticate_message
    
    ; Compare computed vs provided
    mov     rdi, rsp
    mov     rsi, r12
    mov     rcx, 64
    repe    cmpsb
    
    sete    al                  ; Return 1 if equal, 0 otherwise
    
    add     rsp, 64
    pop     rbp
    ret
