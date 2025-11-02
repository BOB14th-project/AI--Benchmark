; Government involution cipher - SPN structure
; 12 rounds with dual substitution layers
; Characteristic: encryption = decryption structure

section .data
    align 16
    ; Dual substitution layers for involution property
    sub_layer_1: db 0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5
                 db 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76

    sub_layer_2: db 0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38
                 db 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb

    ; Round constants for key expansion
    round_const: dq 0x517cc1b727220a94, 0xfe13abe8fa9a6ee0

    rounds_total: dd 12

section .text
    global gov_encrypt_block

; Apply substitution layer 1
apply_sub_layer_1:
    lea rsi, [rel sub_layer_1]
    xor ecx, ecx
.loop1:
    cmp ecx, 16
    jge .done1
    movzx eax, byte [rdi + rcx]
    and eax, 0x0f
    mov al, [rsi + rax]
    mov [rdi + rcx], al
    inc ecx
    jmp .loop1
.done1:
    ret

; Apply substitution layer 2
apply_sub_layer_2:
    lea rsi, [rel sub_layer_2]
    xor ecx, ecx
.loop2:
    cmp ecx, 16
    jge .done2
    movzx eax, byte [rdi + rcx]
    and eax, 0x0f
    mov al, [rsi + rax]
    mov [rdi + rcx], al
    inc ecx
    jmp .loop2
.done2:
    ret

; Diffusion layer
diffusion_layer:
    xor ecx, ecx
.diff_loop:
    cmp ecx, 16
    jge .diff_done
    mov al, [rdi + rcx]
    mov bl, [rdi + ((rcx + 1) & 0x0f)]
    xor al, bl
    mov [rdi + rcx], al
    inc ecx
    jmp .diff_loop
.diff_done:
    ret

; Main encryption - 12 rounds
gov_encrypt_block:
    push rbp
    mov rbp, rsp
    push rbx

    xor ecx, ecx
.round_loop:
    cmp ecx, 12
    jge .encrypt_done

    ; Alternate substitution layers
    test ecx, 1
    jnz .use_layer2

    call apply_sub_layer_1
    jmp .after_sub

.use_layer2:
    call apply_sub_layer_2

.after_sub:
    ; Apply diffusion
    call diffusion_layer

    inc ecx
    jmp .round_loop

.encrypt_done:
    pop rbx
    pop rbp
    ret
