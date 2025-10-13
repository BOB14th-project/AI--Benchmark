; Financial Transaction Security Module
; High-performance block cipher implementation for x86-64

section .data
    ; Mathematical constants for round operations
    round_constants: dd 0x9E3779B9, 0x3C6EF372, 0xDAA66D2B, 0x78DDE6E4

section .text
    global transform_block_encrypt
    global transform_block_decrypt
    global initialize_round_keys

; Block transformation encryption function
; Arguments: rdi = input_buffer, rsi = output_buffer, rdx = key_schedule
transform_block_encrypt:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15

    ; Load 128-bit data block (4 dwords)
    mov     eax, [rdi]          ; Load word 0
    mov     ebx, [rdi+4]        ; Load word 1
    mov     ecx, [rdi+8]        ; Load word 2
    mov     r8d, [rdi+12]       ; Load word 3

    mov     r12, rdx            ; Key schedule pointer
    xor     r14d, r14d          ; Round counter

.round_loop:
    ; Extract round key
    mov     r9d, [r12 + r14*4]
    mov     r10d, [r12 + r14*4 + 16]

    ; G-function with rotations (characteristic pattern)
    mov     r11d, eax
    rol     r11d, 8             ; Rotate left 8
    xor     r11d, r9d

    mov     r13d, ebx
    rol     r13d, 1
    xor     r13d, r10d

    ; F-function - Feistel structure
    mov     r15d, ecx
    xor     r15d, r11d
    add     r15d, r13d

    ; XOR with rotation
    xor     r8d, r15d

    ; Apply S-box-like transformation
    mov     r11d, r8d
    and     r11d, 0xFF
    shl     r11d, 8
    xor     r8d, r11d

    ; Second half of Feistel round
    mov     r11d, ebx
    rol     r11d, 8
    mov     r13d, ecx
    xor     r13d, r11d
    add     r13d, r8d
    xor     eax, r13d

    ; Rotate state words
    mov     r11d, eax
    mov     eax, ebx
    mov     ebx, ecx
    mov     ecx, r8d
    mov     r8d, r11d

    inc     r14d
    cmp     r14d, 16            ; 16 rounds total
    jl      .round_loop

    ; Final word swap
    mov     r11d, eax
    mov     eax, ecx
    mov     ecx, r11d

    ; Store result
    mov     [rsi], eax
    mov     [rsi+4], ebx
    mov     [rsi+8], ecx
    mov     [rsi+12], r8d

    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

transform_block_decrypt:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14

    mov     eax, [rdi]
    mov     ebx, [rdi+4]
    mov     ecx, [rdi+8]
    mov     r8d, [rdi+12]

    ; Reverse initial swap
    mov     r11d, eax
    mov     eax, ecx
    mov     ecx, r11d

    mov     r12, rdx
    mov     r14d, 15            ; Start from last round

.dec_round_loop:
    ; Reverse rotation
    mov     r11d, r8d
    mov     r8d, ecx
    mov     ecx, ebx
    mov     ebx, eax
    mov     eax, r11d

    ; Reverse round operations
    mov     r9d, [r12 + r14*4]
    mov     r10d, [r12 + r14*4 + 16]

    mov     r11d, ebx
    rol     r11d, 8
    mov     r13d, ecx
    xor     r13d, r11d
    add     r13d, r8d
    xor     eax, r13d

    ; Reverse S-box transform
    mov     r11d, r8d
    and     r11d, 0xFF
    shl     r11d, 8
    xor     r8d, r11d

    ; Reverse F-function
    mov     r11d, eax
    rol     r11d, 8
    xor     r11d, r9d

    mov     r13d, ebx
    rol     r13d, 1
    xor     r13d, r10d

    mov     r15d, ecx
    xor     r15d, r11d
    add     r15d, r13d
    xor     r8d, r15d

    dec     r14d
    cmp     r14d, 0
    jge     .dec_round_loop

    mov     [rsi], eax
    mov     [rsi+4], ebx
    mov     [rsi+8], ecx
    mov     [rsi+12], r8d

    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

initialize_round_keys:
    push    rbp
    mov     rbp, rsp

    ; Key expansion using mathematical constants
    mov     rcx, 16
    xor     r8, r8

.key_expand_loop:
    mov     eax, [rdi + r8*4]
    mov     r9d, [rel round_constants + r8*4]
    xor     eax, r9d
    rol     eax, 7
    mov     [rsi + r8*4], eax

    inc     r8
    loop    .key_expand_loop

    pop     rbp
    ret
