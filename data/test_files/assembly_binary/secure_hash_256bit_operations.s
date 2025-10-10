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

    k_cipher_4     data_403000(%rip), %r14
    mov     $0x6a09e667, (%r14)
    mov     $0xbb67ae85, 4(%r14)
    mov     $0x3c6ef372, 8(%r14)
    mov     $0xa54ff53a, 12(%r14)
    mov     $0x510e527f, 16(%r14)
    mov     $0x9b05688c, 20(%r14)
    mov     $0x1f83d9ab, 24(%r14)
    mov     $0x5be0cd19, 28(%r14)

loc_401040:
    cmp     $0, %r13
    jle     loc_401080

    call    sub_401100

    add     $64, %r12
    sub     $64, %r13
    jmp     loc_401040

loc_401080:
    mov     %r14, %rax

    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401100:
    push    %rax
    push    %rbx
    push    %rcx
    push    %rdx

    mov     $64, %rbx

loc_401120:
    test    %rbx, %rbx
    jz      loc_401160

    mov     (%r12), %eax
    add     %eax, (%r14)
    mov     4(%r12), %eax
    add     %eax, 4(%r14)

    add     $8, %r12
    dec     %rbx
    jmp     loc_401120

loc_401160:
    sub     $512, %r12

    pop     %rdx
    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

    .section .data
    .align 16

data_403000:
    .long   0, 0, 0, 0, 0, 0, 0, 0

data_403100:
    .long   0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5
    .long   0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5