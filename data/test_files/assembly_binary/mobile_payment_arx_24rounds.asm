; Mobile payment ARX cipher - 24 rounds
; Add-Rotate-XOR design, no S-boxes

section .data
    rounds: dd 24
    rot_alpha: dd 9
    rot_beta: dd 5
    rot_gamma: dd 3
    delta: dd 0xc3efe9db, 0x44626b02, 0x79e27c8a, 0x78df30ec

section .text
    global arx_encrypt

; ARX round function - Add, Rotate, XOR only
arx_round:
    ; Add round key
    mov eax, [rdi]
    add eax, [rsi]
    mov [rdi], eax

    ; Rotate left by alpha (9 bits)
    rol eax, 9
    mov [rdi], eax

    ; XOR with key
    xor eax, [rsi + 4]
    mov [rdi], eax

    ; More rotations
    mov eax, [rdi + 4]
    rol eax, 5
    mov [rdi + 4], eax

    mov eax, [rdi + 8]
    rol eax, 3
    mov [rdi + 8], eax

    ret

; 24-round ARX encryption
arx_encrypt:
    push rbp
    mov rbp, rsp
    push rbx

    xor ecx, ecx
.arx_loop:
    cmp ecx, 24
    jge .arx_done

    call arx_round

    inc ecx
    jmp .arx_loop

.arx_done:
    pop rbx
    pop rbp
    ret
