; IoT Lightweight cipher - 32 rounds, 64-bit blocks
; Generalized Feistel for resource-constrained devices

section .data
    rounds: dd 32
    block_size: dd 8

section .text
    global iot_encrypt

; Whitening operation
whitening_keys:
    xor ecx, ecx
.wk_loop:
    cmp ecx, 8
    jge .wk_done
    mov al, [rsi + rcx]         ; master_key[i]
    xor al, [rsi + rcx + 8]     ; XOR with master_key[i+8]
    mov [rdi + rcx], al         ; store whitening key
    inc ecx
    jmp .wk_loop
.wk_done:
    ret

; F0 function - rotation and XOR
f0_function:
    rol al, 1
    xor al, 0x5A
    ret

; F1 function - rotation and XOR
f1_function:
    rol al, 3
    xor al, 0xA5
    ret

; 32-round lightweight encryption
iot_encrypt:
    push rbp
    mov rbp, rsp

    xor r10d, r10d      ; round counter
.round_loop:
    cmp r10d, 32
    jge .done

    ; Simple whitening and F-functions
    mov al, [rdi]       ; x0
    xor al, [rsi]       ; subkey[0]
    mov [rdi], al

    mov al, [rdi + 1]   ; x1
    call f0_function
    mov [rdi + 1], al

    mov al, [rdi + 3]   ; x3
    call f1_function
    mov [rdi + 3], al

    ; Rotate state
    mov al, [rdi]
    mov bl, [rdi + 7]
    mov [rdi + 7], al
    mov [rdi], bl

    inc r10d
    jmp .round_loop

.done:
    pop rbp
    ret
