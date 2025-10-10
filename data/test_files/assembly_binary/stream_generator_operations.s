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

    call    sub_401200

    mov     $0, %r8
    mov     $0, %r9

loc_401030:
    cmp     %r14, %rbx
    jge     loc_401090

    inc     %r8
    and     $255, %r8

    movzbl  data_403000(%r8), %eax
    add     %eax, %r9
    and     $255, %r9

    movzbl  data_403000(%r8), %ecx
    movzbl  data_403000(%r9), %edx
    movb    %dl, data_403000(%r8)
    movb    %cl, data_403000(%r9)

    add     %ecx, %edx
    and     $255, %edx
    movzbl  data_403000(%rdx), %esi

    movb    (%r12,%rbx), %al
    xorb    %sil, %al
    movb    %al, (%r13,%rbx)

    inc     %rbx
    jmp     loc_401030

loc_401090:
    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401200:
    push    %rax
    push    %rbx
    push    %rcx
    push    %rdx

    mov     $0, %rbx

loc_401220:
    cmp     $256, %rbx
    jge     loc_401260

    movb    %bl, data_403000(%rbx)
    inc     %rbx
    jmp     loc_401220

loc_401260:
    mov     $0, %rbx
    mov     $0, %rcx

loc_401270:
    cmp     $256, %rbx
    jge     loc_4012e0

    movzbl  data_403000(%rbx), %eax
    add     %eax, %rcx

    mov     %rbx, %rdx
    xor     %rdx, %rdx
    mov     %rbx, %rax
    div     %r15
    movzbl  (%r14,%rdx), %eax
    add     %eax, %rcx

    and     $255, %rcx

    movzbl  data_403000(%rbx), %eax
    movzbl  data_403000(%rcx), %edx
    movb    %dl, data_403000(%rbx)
    movb    %al, data_403000(%rcx)

    inc     %rbx
    jmp     loc_401270

loc_4012e0:
    pop     %rdx
    pop     %rcx
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

    mov     (%rdi), %r8d
    mov     4(%rdi), %r9d
    mov     8(%rdi), %r10d
    mov     12(%rdi), %r11d

    add     %r9d, %r8d
    xor     %r8d, %r11d
    rol     $16, %r11d

    add     %r11d, %r10d
    xor     %r10d, %r9d
    rol     $12, %r9d

    add     %r9d, %r8d
    xor     %r8d, %r11d
    rol     $8, %r11d

    add     %r11d, %r10d
    xor     %r10d, %r9d
    rol     $7, %r9d

    mov     %r8d, (%rdi)
    mov     %r9d, 4(%rdi)
    mov     %r10d, 8(%rdi)
    mov     %r11d, 12(%rdi)

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
    push    %r14

    mov     %rdi, %r12
    mov     %rsi, %r13
    mov     %rdx, %r14

    k_cipher_4     data_403400(%rip), %rbx
    mov     (%rbx), %r8d
    mov     4(%rbx), %r9d
    mov     8(%rbx), %r10d
    mov     12(%rbx), %r11d

    mov     $20, %rcx

loc_401440:
    test    %rcx, %rcx
    jz      loc_401490

    call    sub_401300

    k_cipher_4     4(%rdi), %rdi
    call    sub_401300

    k_cipher_4     4(%rdi), %rdi
    call    sub_401300

    k_cipher_4     4(%rdi), %rdi
    call    sub_401300

    sub     $12, %rdi

    dec     %rcx
    jmp     loc_401440

loc_401490:
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

    .section .data
    .align 16

data_403000:
    .fill   256, 1, 0

data_403400:
    .long   0x61707865, 0x3320646e, 0x79622d32, 0x6b206574

data_403500:
    .quad   0x123456789abcdef0, 0xfedcba9876543210