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
    push    %r15

    lea     data_402000, %r12
    lea     data_402020, %r13

    mov     %rdi, %r14

    mov     %rsi, %r15

    call    sub_401100
    mov     %rax, %rbx

    mov     %rbx, %rdi
    mov     %r12, %rsi
    mov     %r13, %rdx
    call    sub_401200
    mov     %rax, %r8

    mov     %rbx, %rdi
    call    sub_401300
    mov     %rax, %rcx

    mov     %r8, %rax
    mul     %r14
    add     %r15, %rax
    mul     %rcx

    mov     %r8, %rax
    mov     %rdx, %rbx

    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

    .section .text
    .global sub_401400
    .type sub_401400, @function

sub_401400:
    push    %rbp
    mov     %rsp, %rbp

    mov     $0x67452301, %eax
    mov     $0xEFCDAB89, %ebx
    mov     $0x98BADCFE, %ecx
    mov     $0x10325476, %edx
    mov     $0xC3D2E1F0, %r8d

    mov     %rdi, %rsi
    call    sub_401500

    pop     %rbp
    ret

sub_401500:
    mov     $0x5A827999, %r9d
    mov     $0x6ED9EBA1, %r10d
    mov     $0x8F1BBCDC, %r11d
    mov     $0xCA62C1D6, %r12d

    mov     $0, %r13d

loc_401520:
    cmp     $80, %r13d
    jge     loc_401540

    inc     %r13d
    jmp     loc_401520

loc_401540:
    ret

    .section .data
    .align 8
data_402000:
    .quad   0x6b17d1f2e12c4247, 0xf8bce6e563a440f2
    .quad   0x77037d812deb33a0, 0xf4a13945d898c296

data_402020:
    .quad   0x4fe342e2fe1a7f9b, 0x8ee7eb4a7c0f9e16
    .quad   0x2bce33576b315ece, 0xcbb6406837bf51f5

data_402040:
    .quad   0xffffffff00000000, 0xffffffffffffffffbce6faada7179e84, 0xf3b9cac2fc632551