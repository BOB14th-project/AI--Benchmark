; PKI signature hash function - 160-bit output
; 80 rounds, 5 chaining variables

section .data
    ; 160-bit hash initialization vectors
    H0: dd 0x67452301
    H1: dd 0xEFCDAB89
    H2: dd 0x98BADCFE
    H3: dd 0x10325476
    H4: dd 0xC3D2E1F0

    ; Round constants for 80 rounds
    K0: dd 0x5A827999    ; Rounds 0-19
    K1: dd 0x6ED9EBA1    ; Rounds 20-39
    K2: dd 0x8F1BBCDC    ; Rounds 40-59
    K3: dd 0xCA62C1D6    ; Rounds 60-79

    rounds: dd 80

section .text
    global hash160_compress

; F function varies by round
f_function:
    cmp ecx, 20
    jl .f1
    cmp ecx, 40
    jl .f2
    cmp ecx, 60
    jl .f3
    ; f4: b XOR c XOR d
    mov eax, esi
    xor eax, edx
    xor eax, edi
    ret
.f1:
    ; (b AND c) OR (NOT b AND d)
    mov eax, esi
    and eax, edx
    mov ebx, esi
    not ebx
    and ebx, edi
    or eax, ebx
    ret
.f2:
    ; b XOR c XOR d
    mov eax, esi
    xor eax, edx
    xor eax, edi
    ret
.f3:
    ; (b AND c) OR (b AND d) OR (c AND d)
    mov eax, esi
    and eax, edx
    mov ebx, esi
    and ebx, edi
    or eax, ebx
    mov ebx, edx
    and ebx, edi
    or eax, ebx
    ret

; 80-round compression for 160-bit hash
hash160_compress:
    push rbp
    mov rbp, rsp

    ; Load initial hash values
    mov eax, [rel H0]
    mov ebx, [rel H1]
    mov ecx, [rel H2]
    mov edx, [rel H3]
    mov r8d, [rel H4]

    xor r9d, r9d        ; round counter
.hash_loop:
    cmp r9d, 80
    jge .hash_done

    ; Determine K constant
    mov r10d, r9d
    shr r10d, 5         ; divide by 20
    lea r11, [rel K0]
    mov r11d, [r11 + r10*4]

    ; Rotate and mix
    rol eax, 5
    call f_function
    add eax, r8d
    add eax, r11d

    inc r9d
    jmp .hash_loop

.hash_done:
    ; Store final hash (160 bits = 5 x 32-bit)
    pop rbp
    ret
