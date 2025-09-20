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
    mov     $data_402000, %r12
    mov     $data_402020, %r13
    mov     %rdi, %r14
    mov     %rsi, %r15
    lea     data_402040(%rip), %rax
    lea     data_402060(%rip), %rbx
    lea     data_402080(%rip), %rcx
    call    sub_401200
    mov     $12, %r8
loc_401050:
    test    %r8, %r8
    jz      loc_4010c0
    test    $1, %r8
    jz      loc_401080
    call    sub_401300
    jmp     loc_401090
loc_401080:
    call    sub_401400
loc_401090:
    cmp     $1, %r8
    je      loc_4010b0
    call    sub_401500
loc_4010b0:
    call    sub_401600
    dec     %r8
    jmp     loc_401050
loc_4010c0:
    mov     %r14, %rax
    pop     %r15
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
    .section .text
    .global sub_401700
    .type sub_401700, @function
sub_401700:
    push    %rbp
    mov     %rsp, %rbp
    mov     $data_402100, %rax
    mov     $data_402120, %rbx
    mov     %rdi, %rcx
    mov     %rsi, %rdx
    mov     $16, %r8
loc_401730:
    test    %r8, %r8
    jz      loc_401750
    call    sub_401800
    dec     %r8
    jmp     loc_401730
loc_401750:
    pop     %rbp
    ret
    .section .data
    .align 16
data_402000:
    .byte   0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5
    .byte   0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76
data_402020:
    .byte   0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38
    .byte   0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb
data_402040:
    .quad   0x517cc1b727220a94, 0xfe13abe8fa9a6ee0
    .quad   0x6db14acc9e21c820, 0xff28b1d5ef5de2b0
data_402060:
    .quad   0xdb92371d2126e970, 0x03249775c7d98e73
    .quad   0x5e85c1fb8f7c2e4a, 0x9fc12b3df7e18529
data_402080:
    .quad   0xa7ca823095d1ba52, 0x5c9f4d103b8fe421
    .quad   0x76c53d08f6be7a91, 0x3e4d2c567f8a1b0e
data_402100:
    .long   0x2989a1a8, 0x05858184, 0x16c6d2d4, 0x13c3d3d0
    .long   0x14445054, 0x1bcccddc, 0x0fcfcfc8, 0x11cdcdc0
data_402120:
    .long   0x29aa8181, 0x0505a8a8, 0x16d4c6c6, 0x13d0c3c3
    .long   0x14504545, 0x1bdccccc, 0x0fc8cfcf, 0x11c0cdcd