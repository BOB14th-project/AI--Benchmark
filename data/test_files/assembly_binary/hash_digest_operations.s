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

    k_cipher_4     data_403000(%rip), %r15
    mov     $0x67452301, (%r15)
    mov     $0xefcdab89, 4(%r15)
    mov     $0x98badcfe, 8(%r15)
    mov     $0x10325476, 12(%r15)

    call    sub_401200

loc_401030:
    cmp     $0, %r13
    jle     loc_401070

    call    sub_401100

    add     $64, %r12
    sub     $64, %r13
    jmp     loc_401030

loc_401070:
    mov     %r15, %rax

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

    mov     (%r15), %eax
    mov     4(%r15), %ebx
    mov     8(%r15), %ecx
    mov     12(%r15), %edx

    mov     $64, %r8

loc_401130:
    test    %r8, %r8
    jz      loc_401180

    mov     %ebx, %esi
    and     %ecx, %esi
    mov     %ebx, %edi
    not     %edi
    and     %edx, %edi
    or      %edi, %esi

    add     %esi, %eax
    add     (%r12), %eax
    add     $0xd76aa478, %eax

    rol     $7, %eax
    add     %ebx, %eax

    mov     %edx, %edi
    mov     %ecx, %edx
    mov     %ebx, %ecx
    mov     %eax, %ebx
    mov     %edi, %eax

    add     $4, %r12
    dec     %r8
    jmp     loc_401130

loc_401180:
    sub     $256, %r12

    add     %eax, (%r15)
    add     %ebx, 4(%r15)
    add     %ecx, 8(%r15)
    add     %edx, 12(%r15)

    pop     %rdx
    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

sub_401200:
    push    %rax
    push    %rbx

    mov     %r13, %rax
    shl     $3, %rax
    mov     %rax, data_403100

    movb    $0x80, (%r12,%r13)
    inc     %r13

    mov     %r13, %rax
    and     $63, %rax
    cmp     $56, %rax
    jle     loc_401250

    mov     $64, %rbx
    sub     %rax, %rbx
    add     %rbx, %r13

loc_401250:
    mov     data_403100, %rax
    mov     %rax, (%r12,%r13)

    pop     %rbx
    pop     %rax
    ret

    .section .text
    .global sub_401300
    .type sub_401300, @function

sub_401300:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12
    push    %r13
    push    %r14
    push    %r15

    mov     %rdi, %r12
    mov     %rsi, %r13

    k_cipher_4     data_403200(%rip), %r14
    mov     $0x67452301, (%r14)
    mov     $0xefcdab89, 4(%r14)
    mov     $0x98badcfe, 8(%r14)
    mov     $0x10325476, 12(%r14)
    mov     $0xc3d2e1f0, 16(%r14)

loc_401340:
    cmp     $0, %r13
    jle     loc_401380

    call    sub_401390

    add     $64, %r12
    sub     $64, %r13
    jmp     loc_401340

loc_401380:
    mov     %r14, %rax

    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401390:
    push    %rax
    push    %rbx
    push    %rcx
    push    %rdx
    push    %rsi

    mov     (%r14), %eax
    mov     4(%r14), %ebx
    mov     8(%r14), %ecx
    mov     12(%r14), %edx
    mov     16(%r14), %esi

    mov     $80, %r8

loc_4013c0:
    test    %r8, %r8
    jz      loc_401440

    mov     %eax, %edi
    rol     $5, %edi

    mov     %ebx, %r9d
    and     %ecx, %r9d
    mov     %ebx, %r10d
    not     %r10d
    and     %edx, %r10d
    or      %r10d, %r9d

    add     %edi, %r9d
    add     %esi, %r9d
    add     (%r12), %r9d
    add     $0x5a827999, %r9d

    mov     %edx, %esi
    mov     %ecx, %edx
    mov     %ebx, %ecx
    rol     $30, %ecx
    mov     %eax, %ebx
    mov     %r9d, %eax

    add     $4, %r12
    dec     %r8
    jmp     loc_4013c0

loc_401440:
    sub     $320, %r12

    add     %eax, (%r14)
    add     %ebx, 4(%r14)
    add     %ecx, 8(%r14)
    add     %edx, 12(%r14)
    add     %esi, 16(%r14)

    pop     %rsi
    pop     %rdx
    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

    .section .data
    .align 16

data_403000:
    .long   0, 0, 0, 0

data_403200:
    .long   0, 0, 0, 0, 0

data_403100:
    .quad   0

data_403300:
    .long   0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6