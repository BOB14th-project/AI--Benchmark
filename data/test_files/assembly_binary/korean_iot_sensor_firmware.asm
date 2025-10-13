; Lightweight Cipher for Resource-Constrained Devices
; Optimized for 8-bit/16-bit microcontrollers

section .data
    ; Transformation constants
    transform_delta dd 0x5A827999
    
section .text
    global lightweight_transform
    global lightweight_inverse

; 64-bit block cipher with 32 rounds
; Arguments: rdi = plaintext, rsi = ciphertext, rdx = master_key
lightweight_transform:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15
    
    ; Load 64-bit block as two 32-bit words
    mov     eax, [rdi]          ; X0
    mov     ebx, [rdi+4]        ; X1
    
    ; Load key material
    mov     r12, rdx            ; Master key pointer
    
    ; Initial whitening with key
    xor     eax, [r12]
    xor     ebx, [r12+4]
    
    ; Round counter
    xor     ecx, ecx

.transformation_rounds:
    ; Round function F0: X0 ^ (X1 <<< 1) ^ (X1 <<< 2) ^ (X1 <<< 7)
    mov     r8d, ebx
    rol     r8d, 1              ; Rotation by 1
    mov     r9d, ebx
    rol     r9d, 2              ; Rotation by 2
    xor     r8d, r9d
    mov     r9d, ebx
    rol     r9d, 7              ; Rotation by 7
    xor     r8d, r9d
    
    ; Add round key
    mov     r10d, ecx
    and     r10d, 7
    mov     r9d, [r12 + r10*4]
    add     r8d, r9d
    
    ; Add delta constant
    mov     r9d, [rel transform_delta]
    add     r8d, r9d
    
    ; XOR with X0
    xor     eax, r8d
    
    ; Round function F1: X1 ^ (X0 <<< 3) ^ (X0 <<< 4) ^ (X0 <<< 6)
    mov     r8d, eax
    rol     r8d, 3
    mov     r9d, eax
    rol     r9d, 4
    xor     r8d, r9d
    mov     r9d, eax
    rol     r9d, 6
    xor     r8d, r9d
    
    ; Add round key
    mov     r10d, ecx
    add     r10d, 1
    and     r10d, 7
    mov     r9d, [r12 + r10*4]
    add     r8d, r9d
    
    ; XOR with X1
    xor     ebx, r8d
    
    ; Increment round counter
    inc     ecx
    cmp     ecx, 32             ; 32 rounds total
    jl      .transformation_rounds
    
    ; Final whitening
    xor     eax, [r12+8]
    xor     ebx, [r12+12]
    
    ; Store ciphertext
    mov     [rsi], eax
    mov     [rsi+4], ebx
    
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

lightweight_inverse:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    
    ; Load 64-bit ciphertext
    mov     eax, [rdi]
    mov     ebx, [rdi+4]
    
    mov     r12, rdx
    
    ; Reverse final whitening
    xor     eax, [r12+8]
    xor     ebx, [r12+12]
    
    ; Reverse transformation (31 down to 0)
    mov     ecx, 31

.inverse_rounds:
    ; Reverse F1 operation
    mov     r8d, eax
    rol     r8d, 3
    mov     r9d, eax
    rol     r9d, 4
    xor     r8d, r9d
    mov     r9d, eax
    rol     r9d, 6
    xor     r8d, r9d
    
    mov     r10d, ecx
    add     r10d, 1
    and     r10d, 7
    mov     r9d, [r12 + r10*4]
    add     r8d, r9d
    xor     ebx, r8d
    
    ; Reverse F0 operation
    mov     r8d, ebx
    rol     r8d, 1
    mov     r9d, ebx
    rol     r9d, 2
    xor     r8d, r9d
    mov     r9d, ebx
    rol     r9d, 7
    xor     r8d, r9d
    
    mov     r10d, ecx
    and     r10d, 7
    mov     r9d, [r12 + r10*4]
    add     r8d, r9d
    mov     r9d, [rel transform_delta]
    add     r8d, r9d
    xor     eax, r8d
    
    dec     ecx
    cmp     ecx, 0
    jge     .inverse_rounds
    
    ; Reverse initial whitening
    xor     eax, [r12]
    xor     ebx, [r12+4]
    
    ; Store plaintext
    mov     [rsi], eax
    mov     [rsi+4], ebx
    
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret
