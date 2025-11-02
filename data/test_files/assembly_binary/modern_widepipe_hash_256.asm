; Modern wide-pipe hash - 256-bit output
; Wide internal state, novel compression

section .data
    output_size: dd 256
    state_size: dd 16       ; 512-bit internal state
    step_constants: dd 0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5

section .text
    global widepipe_hash

; Novel mixing function
mix_function:
    xor eax, ebx
    add eax, ecx
    shr eax, 16
    xor eax, eax
    imul eax, 0x85ebca6b
    shr eax, 13
    xor eax, eax
    imul eax, 0xc2b2ae35
    shr eax, 16
    xor eax, eax
    ret

; Step function - different from SHA-2/SHA-3
step_function:
    push rbx
    mov eax, [rdi]          ; state[i]
    xor eax, esi            ; XOR with message word
    mov ebx, [rel step_constants]
    mov ecx, edx            ; index
    call mix_function
    ; Mix with neighbors
    mov ebx, [rdi - 4]
    xor eax, ebx
    mov ebx, [rdi + 4]
    add eax, ebx
    pop rbx
    ret

; Wide-pipe compression
widepipe_hash:
    push rbp
    mov rbp, rsp

    xor ecx, ecx
.compress_loop:
    cmp ecx, 48
    jge .compress_done

    call step_function

    inc ecx
    jmp .compress_loop

.compress_done:
    pop rbp
    ret
