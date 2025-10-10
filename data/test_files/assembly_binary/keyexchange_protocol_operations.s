    .section .text
    .global sub_401000
    .type sub_401000, @function

sub_401000:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12
    push    %r13
    push    %r14

    mov     %rdi, %r12
    mov     %rsi, %r13
    mov     %rdx, %r14

    k_cipher_4     data_404000(%rip), %rbx
    mov     (%rbx), %r8
    mov     8(%rbx), %r9

    mov     %r12, %rax
    mov     %r13, %rcx
    mov     %r8, %r10

loc_401040:
    test    %rcx, %rcx
    jz      loc_401080
    test    $1, %rcx
    jz      loc_401060

    mul     %r10
    div     %r9
    mov     %rdx, %r10

loc_401060:
    mov     %rax, %r11
    mul     %r11
    div     %r9
    mov     %rdx, %rax
    shr     $1, %rcx
    jmp     loc_401040

loc_401080:
    mov     %r10, %rax
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

    .section .data
    .align 8

data_404000:
    .quad   0x7fffffffffffffff, 0x8000000000000000
    .quad   0x123456789abcdef0, 0xfedcba0987654321