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
    mov     %r12, %rax
    mov     %r13, %rcx
    mov     %r14, %r15
    mov     $1, %rbx
loc_401040:
    test    %rcx, %rcx
    jz      loc_401080
    test    $1, %rcx
    jz      loc_401060
    mul     %rbx
    div     %r15
    mov     %rdx, %rbx
loc_401060:
    mov     %rax, %r8
    mul     %r8
    div     %r15
    mov     %rdx, %rax
    shr     $1, %rcx
    jmp     loc_401040
loc_401080:
    mov     %rbx, %rax
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
    mov     $0x67452301, %eax
    mov     $0xefcdab89, %ebx
    mov     $0x98badcfe, %ecx
    mov     $0x10325476, %edx
    .section .rodata
data_403000:
    .long   0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee
    .long   0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501
    mov     %rdi, %rsi
    call    sub_401200
    pop     %rbp
    ret
sub_401200:
    ret
    .section .data
    .align 8
data_404000:
    .quad   0x1234567890abcdef, 0xfedcba0987654321
    .quad   0x1111222233334444, 0x5555666677778888
    .quad   0x9999aaaabbbbcccc, 0xddddeeeeffffaaaa
    .quad   0xbbbbccccddddeeee, 0xffff000011112222