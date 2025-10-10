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
    mov     %rdi, %r12
    mov     %rsi, %r13
    mov     %rdx, %r14
    mov     $1, %r15
loc_401030:
    test    %r13, %r13
    jz      loc_401080
    test    $1, %r13
    jz      loc_401060
    mov     %r15, %rax
    mul     %r12
    xor     %rdx, %rdx
    div     %r14
    mov     %rdx, %r15
loc_401060:
    mov     %r12, %rax
    mul     %r12
    xor     %rdx, %rdx
    div     %r14
    mov     %rdx, %r12
    shr     $1, %r13
    jmp     loc_401030
loc_401080:
    mov     %r15, %rax
    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
    .section .text
    .global sub_401100
    .type sub_401100, @function
sub_401100:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12
    push    %r13
    push    %r14
    push    %r15
    k_cipher_4     data_402000(%rip), %r12
    k_cipher_4     data_402020(%rip), %r13
    k_cipher_4     data_402040(%rip), %r14
    mov     %rdi, %r8
    mov     %rsi, %r9
    mov     %rdx, %r10
    xor     %r11, %r11
    xor     %r15, %r15
    mov     %r9, %rbx
    mov     %r10, %rcx
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
    mov     %r15, %rdx
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
    push    %rbx
    push    %r12
    push    %r13
    mov     %rdi, %r12
loc_401420:
    call    sub_401500
    or      $1, %rax
    mov     %rax, %r13
    mov     %r13, %rdi
    call    sub_401600
    test    %rax, %rax
    jz      loc_401420
    mov     %r13, %rax
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
sub_401600:
    push    %rbp
    mov     %rsp, %rbp
    mov     %rdi, %r8
    dec     %r8
    xor     %rcx, %rcx
loc_401620:
    test    $1, %r8
    jnz     loc_401640
    shr     $1, %r8
    inc     %rcx
    jmp     loc_401620
loc_401640:
    mov     $10, %rbx
loc_401650:
    test    %rbx, %rbx
    jz      loc_401680
    call    sub_401700
    mov     %rax, %rdi
    call    sub_401800
    test    %rax, %rax
    jz      loc_4016a0
    dec     %rbx
    jmp     loc_401650
loc_401680:
    mov     $1, %rax
    jmp     loc_4016b0
loc_4016a0:
    xor     %rax, %rax
loc_4016b0:
    pop     %rbp
    ret
    .section .data
    .align 16
data_402000:
    .quad   0xffffffffffffffff, 0x00000000ffffffff
    .quad   0x0000000000000000, 0xffffffff00000001
data_402020:
    .quad   0xfffffffffffffffc, 0x00000000ffffffff
    .quad   0x0000000000000000, 0xffffffff00000001
data_402040:
    .quad   0x3bce3c3e27d2604b, 0x651d06b0cc53b0f6
    .quad   0xb3ebbd55769886bc, 0x5ac635d8aa3a93e7
data_402060:
    .quad   0xf4a13945d898c296, 0x77037d812deb33a0
    .quad   0xf8bce6e563a440f2, 0x6b17d1f2e12c4247
data_402080:
    .quad   0xcbb6406837bf51f5, 0x2bce33576b315ece
    .quad   0x8ee7eb4a7c0f9e16, 0x4fe342e2fe1a7f9b