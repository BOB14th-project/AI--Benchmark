; Mobile wallet ARX - ultra fast
; 24 rounds, pure ARX operations

section .data
    wallet_rounds: dd 24
    alpha_rot: dd 9
    beta_rot: dd 5
    gamma_rot: dd 3
    wallet_delta: dd 0xc3efe9db, 0x44626b02

section .text
    global wallet_arx_encrypt

; Pure ARX round - no table lookups
arx_wallet_round:
    ; Add
    mov eax, [rdi]
    add eax, [rsi]
    mov [rdi], eax

    ; Rotate (9 bits)
    rol eax, 9
    mov [rdi], eax

    ; XOR
    xor eax, [rsi + 4]
    mov [rdi], eax

    ; Second word
    mov eax, [rdi + 4]
    add eax, [rdi]
    rol eax, 5
    xor eax, [rsi + 8]
    mov [rdi + 4], eax

    ; Third word
    mov eax, [rdi + 8]
    rol eax, 3
    xor eax, [rdi + 4]
    mov [rdi + 8], eax

    ret

; 24-round ARX encryption
wallet_arx_encrypt:
    push rbp
    mov rbp, rsp

    xor r9d, r9d
.wallet_loop:
    cmp r9d, 24
    jge .wallet_done

    call arx_wallet_round

    inc r9d
    jmp .wallet_loop

.wallet_done:
    pop rbp
    ret
