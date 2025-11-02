; Smart device ultra-lightweight crypto
; 32 rounds, 8-bit optimized

section .data
    rounds: dd 32
    block_bytes: dd 8

section .text
    global smart_device_encrypt

; Ultra-lightweight round
light_round:
    ; XOR with subkey
    mov al, [rdi]
    xor al, [rsi]
    mov [rdi], al

    ; Simple rotation (8-bit)
    mov al, [rdi + 1]
    rol al, 1
    add al, [rdi]
    mov [rdi + 1], al

    ; More XOR mixing
    mov al, [rdi + 3]
    rol al, 3
    xor al, [rdi + 2]
    mov [rdi + 3], al

    ret

; 32-round encryption
smart_device_encrypt:
    push rbp
    mov rbp, rsp

    xor r10d, r10d
.device_loop:
    cmp r10d, 32
    jge .device_done

    call light_round

    ; Rotate state bytes
    mov al, [rdi]
    mov bl, [rdi + 7]
    mov [rdi + 7], al
    mov [rdi], bl

    inc r10d
    jmp .device_loop

.device_done:
    pop rbp
    ret
