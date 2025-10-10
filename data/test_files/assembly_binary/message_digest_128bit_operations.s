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

    k_cipher_4     data_403000(%rip), %r14
    mov     $0x67452301, (%r14)
    mov     $0xefcdab89, 4(%r14)
    mov     $0x98badcfe, 8(%r14)
    mov     $0x10325476, 12(%r14)

loc_401030:
    cmp     $0, %r13
    jle     loc_401070

    call    sub_401100

    add     $64, %r12
    sub     $64, %r13
    jmp     loc_401030

loc_401070:
    mov     %r14, %rax

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
    add     $0xd76aa478, %eax

    add     $4, %r12
    dec     %rbx
    jmp     loc_401120

loc_401160:
    sub     $256, %r12

    pop     %rdx
    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

    .section .data
    .align 16

data_403000:
    .long   0, 0, 0, 0