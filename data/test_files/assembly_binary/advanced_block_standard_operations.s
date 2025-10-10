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

    k_cipher_4     data_402000(%rip), %r15
    mov     $10, %rbx

loc_401030:
    test    %rbx, %rbx
    jz      loc_401080

    call    sub_401100
    call    sub_401200
    call    sub_401300
    call    sub_401400

    dec     %rbx
    jmp     loc_401030

loc_401080:
    call    sub_401100
    call    sub_401200
    call    sub_401400

    mov     %r12, %rax

    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret

sub_401100:
    push    %rcx
    push    %rdx
    mov     $16, %rcx

loc_401110:
    test    %rcx, %rcx
    jz      loc_401140

    movzbl  (%r12), %edx
    movzbl  (%r15,%rdx), %edx
    movb    %dl, (%r12)

    inc     %r12
    dec     %rcx
    jmp     loc_401110

loc_401140:
    sub     $16, %r12
    pop     %rdx
    pop     %rcx
    ret

sub_401200:
    push    %rax
    push    %rbx
    push    %rcx

    mov     (%r12), %eax
    mov     4(%r12), %ebx
    mov     8(%r12), %ecx
    mov     12(%r12), %edx

    rol     $8, %ebx
    rol     $16, %ecx
    rol     $24, %edx

    mov     %eax, (%r12)
    mov     %ebx, 4(%r12)
    mov     %ecx, 8(%r12)
    mov     %edx, 12(%r12)

    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

sub_401300:
    push    %rax
    push    %rbx
    push    %rcx
    push    %rdx

    mov     $4, %rbx

loc_401320:
    test    %rbx, %rbx
    jz      loc_401370

    movzbl  (%r12), %eax
    movzbl  1(%r12), %ecx
    movzbl  2(%r12), %edx
    movzbl  3(%r12), %esi

    mov     %eax, %edi
    shl     $1, %edi
    xor     %ecx, %edi
    xor     %edx, %edi
    xor     %esi, %edi

    movb    %dil, (%r12)

    add     $4, %r12
    dec     %rbx
    jmp     loc_401320

loc_401370:
    sub     $16, %r12
    pop     %rdx
    pop     %rcx
    pop     %rbx
    pop     %rax
    ret

sub_401400:
    push    %rax
    push    %rcx
    mov     $16, %rcx

loc_401410:
    test    %rcx, %rcx
    jz      loc_401440

    movb    (%r12), %al
    xorb    (%r13), %al
    movb    %al, (%r12)

    inc     %r12
    inc     %r13
    dec     %rcx
    jmp     loc_401410

loc_401440:
    sub     $16, %r12
    sub     $16, %r13
    pop     %rcx
    pop     %rax
    ret

    .section .data
    .align 16

data_402000:
    .byte   0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5
    .byte   0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76
    .byte   0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0
    .byte   0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0
    .byte   0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc
    .byte   0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15
    .byte   0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a
    .byte   0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75
    .byte   0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0
    .byte   0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84
    .byte   0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b
    .byte   0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf
    .byte   0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85
    .byte   0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8
    .byte   0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5
    .byte   0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2

data_402100:
    .byte   0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
    .byte   0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f