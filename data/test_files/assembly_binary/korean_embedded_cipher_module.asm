; Lightweight Cipher for Embedded Systems - 64-bit block processing
; Optimized for constrained environments

section .data
    delta_const dd 0x5A827999  ; Mathematical constant for whitening
    
section .text
    global lightweight_encrypt
    global lightweight_decrypt

lightweight_encrypt:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    
    ; Load 64-bit block (2 dwords)
    mov     eax, [rdi]      ; Lower 32 bits
    mov     ebx, [rdi+4]    ; Upper 32 bits
    mov     r12, rdx        ; Key pointer
    
    ; Initial whitening
    xor     eax, [r12]
    xor     ebx, [r12+4]
    
    ; 32-round transformation
    xor     ecx, ecx        ; Round counter
.round_loop:
    ; F-function with rotation and XOR
    mov     r8d, ebx
    rol     r8d, 5
    mov     r9d, ebx
    rol     r9d, 11
    xor     r8d, r9d
    add     r8d, [rel delta_const]
    xor     eax, r8d
    
    ; Second transformation
    mov     r8d, eax
    ror     r8d, 7
    mov     r9d, eax
    ror     r9d, 13
    xor     r8d, r9d
    xor     ebx, r8d
    
    inc     ecx
    cmp     ecx, 32
    jl      .round_loop
    
    ; Final whitening
    xor     eax, [r12+8]
    xor     ebx, [r12+12]
    
    ; Store result
    mov     [rsi], eax
    mov     [rsi+4], ebx
    
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

lightweight_decrypt:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    
    mov     eax, [rdi]
    mov     ebx, [rdi+4]
    mov     r12, rdx
    
    ; Reverse whitening
    xor     eax, [r12+8]
    xor     ebx, [r12+12]
    
    ; 32 rounds in reverse
    mov     ecx, 31
.round_loop_dec:
    mov     r8d, eax
    ror     r8d, 7
    mov     r9d, eax
    ror     r9d, 13
    xor     r8d, r9d
    xor     ebx, r8d
    
    mov     r8d, ebx
    rol     r8d, 5
    mov     r9d, ebx
    rol     r9d, 11
    xor     r8d, r9d
    add     r8d, [rel delta_const]
    xor     eax, r8d
    
    dec     ecx
    cmp     ecx, 0
    jge     .round_loop_dec
    
    xor     eax, [r12]
    xor     ebx, [r12+4]
    
    mov     [rsi], eax
    mov     [rsi+4], ebx
    
    pop     r12
    pop     rbx
    pop     rbp
    ret
