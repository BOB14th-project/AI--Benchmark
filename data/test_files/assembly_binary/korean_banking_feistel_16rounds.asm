; Banking-grade 16-round Feistel cipher implementation
; Used in Korean financial institutions
; Assembly optimized for x86-64 architecture

section .data
    ; S-box tables for banking cipher
    align 16
    banking_ss0:
        dd 0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0
        dd 0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0

    banking_ss1:
        dd 0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3
        dd 0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd

    banking_ss2:
        dd 0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0
        dd 0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0

    banking_ss3:
        dd 0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3
        dd 0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd

    ; Key constants for 16-round schedule
    key_constants:
        dd 0x9e3779b9, 0x3c6ef373, 0x78dde6e6, 0xf1bbcdcc
        dd 0xe3779b99, 0xc6ef3733, 0x8dde6e67, 0x1bbcdccf

    round_count: dd 16

section .text
    global banking_encrypt_block
    global banking_f_function
    global generate_round_keys

; Banking F-function with S-box substitution
; Input: EDI = right_half, ESI = round_key
; Output: EAX = f_output
banking_f_function:
    push rbx
    push r12
    push r13

    ; XOR right half with round key
    mov eax, edi
    xor eax, esi        ; temp = right ^ round_key

    ; Extract bytes for S-box lookups
    mov ebx, eax
    and ebx, 0xff       ; b0 = temp & 0xff

    mov ecx, eax
    shr ecx, 8
    and ecx, 0xff       ; b1 = (temp >> 8) & 0xff

    mov edx, eax
    shr edx, 16
    and edx, 0xff       ; b2 = (temp >> 16) & 0xff

    mov r12d, eax
    shr r12d, 24        ; b3 = (temp >> 24) & 0xff

    ; S-box lookups
    lea r13, [rel banking_ss0]
    and ebx, 0x7        ; Mask to valid range
    mov r8d, [r13 + rbx*4]  ; s0 = ss0[b0]

    lea r13, [rel banking_ss1]
    and ecx, 0x7
    mov r9d, [r13 + rcx*4]  ; s1 = ss1[b1]

    lea r13, [rel banking_ss2]
    and edx, 0x7
    mov r10d, [r13 + rdx*4] ; s2 = ss2[b2]

    lea r13, [rel banking_ss3]
    and r12d, 0x7
    mov r11d, [r13 + r12*4] ; s3 = ss3[b3]

    ; Combine S-box outputs
    mov eax, r8d
    xor eax, r9d
    xor eax, r10d
    xor eax, r11d

    ; Additional mixing
    mov ebx, eax
    shl ebx, 8
    mov ecx, eax
    shr ecx, 24
    or ebx, ecx
    xor eax, ebx

    pop r13
    pop r12
    pop rbx
    ret

; Generate 16 round keys from master key
; Input: RDI = pointer to master_key (16 bytes)
;        RSI = pointer to round_keys output (64 bytes)
generate_round_keys:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Load master key into 4 words
    mov r12d, [rdi]         ; key_words[0]
    mov r13d, [rdi + 4]     ; key_words[1]
    mov r14d, [rdi + 8]     ; key_words[2]
    mov r15d, [rdi + 12]    ; key_words[3]

    lea rbx, [rel key_constants]
    xor ecx, ecx            ; round counter

.round_loop:
    cmp ecx, 16
    jge .done

    ; Generate round key
    cmp ecx, 4
    jl .use_direct_key

    ; Complex key schedule for rounds >= 4
    mov eax, r13d           ; key_words[(rn-1)%4]
    xor eax, r12d           ; XOR with key_words[(rn-4)%4]

    mov edx, ecx
    and edx, 0x3
    mov edi, [rbx + rdx*4]  ; Load key constant
    xor eax, edi

    ; Rotate left by 1
    rol eax, 1

    ; Update key word
    mov r12d, eax
    jmp .store_key

.use_direct_key:
    ; For first 4 rounds, use key directly
    mov eax, r12d

.store_key:
    mov [rsi + rcx*4], eax

    ; Rotate key words
    mov edi, r12d
    mov r12d, r13d
    mov r13d, r14d
    mov r14d, r15d
    mov r15d, edi

    inc ecx
    jmp .round_loop

.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; Encrypt 128-bit block using 16-round Feistel
; Input: RDI = pointer to plaintext (16 bytes)
;        RSI = pointer to key (16 bytes)
;        RDX = pointer to ciphertext output (16 bytes)
banking_encrypt_block:
    push rbp
    mov rbp, rsp
    sub rsp, 80             ; Space for round keys (64) + temps (16)
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Generate round keys
    mov r14, rdi            ; Save plaintext pointer
    mov r15, rdx            ; Save ciphertext pointer
    lea rdi, [rsi]          ; Key pointer
    lea rsi, [rbp - 64]     ; Round keys destination
    call generate_round_keys

    ; Load plaintext into left and right halves
    mov r12, [r14]          ; left = first 8 bytes
    mov r13, [r14 + 8]      ; right = second 8 bytes

    ; 16 Feistel rounds
    xor ecx, ecx

.feistel_loop:
    cmp ecx, 16
    jge .feistel_done

    ; Call F-function
    mov edi, r13d           ; right half (32-bit for F-function)
    lea rbx, [rbp - 64]
    mov esi, [rbx + rcx*4]  ; round_key[i]
    call banking_f_function

    ; Feistel structure: new_left = right, new_right = left XOR f_output
    mov rbx, r13
    xor r12, rax            ; left XOR f_output
    mov r13, rbx            ; new_left = old_right
    xchg r12, r13           ; Swap for next round

    inc ecx
    jmp .feistel_loop

.feistel_done:
    ; Write ciphertext
    mov [r15], r12
    mov [r15 + 8], r13

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    add rsp, 80
    pop rbp
    ret

section .note.GNU-stack noalloc noexec nowrite progbits
