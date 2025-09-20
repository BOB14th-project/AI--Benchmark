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

    mov     %r14, %rdi
    mov     %r12, %rsi
    mov     %r13, %rdx
    call    sub_401100
    mov     %rax, %r8

    mov     %r8, %rax
    mul     %r14
    add     %r15, %rax

    mov     %r8, %rax

    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401100:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12

    mov     %rdi, %r8
    mov     %rsi, %r9
    mov     %rdx, %r10

    xor     %r11, %r11
    mov     %r9, %rbx

loc_401140:
    test    %r8, %r8
    jz      loc_401180
    test    $1, %r8
    jz      loc_401160

    call    sub_401200

loc_401160:
    call    sub_401300
    shr     $1, %r8
    jmp     loc_401140

loc_401180:
    mov     %r11, %rax
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401200:
sub_401300:
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
    .quad   0xffffffff00000000, 0xffffffffffffffff