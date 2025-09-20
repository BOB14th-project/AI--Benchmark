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
    mov     $1024, %r12
    mov     $12289, %r13
    mov     $2, %r14
    mov     %rdi, %r15
    mov     %rsi, %rbx
    call    sub_401300
    mov     %rax, %rcx
    call    sub_401400
    mov     %rax, %r8
    mov     %r8, %rdi
    mov     %rbx, %rsi
    call    sub_401500
    mov     %rax, %r9
    mov     %rcx, %rdi
    mov     %r9, %rsi
    mov     %r15, %rdx
    call    sub_401600
    mov     %rax, %r10
    call    sub_401700
    test    %rax, %rax
    jz      sub_401000
    mov     %r9, %rax
    mov     %r10, %rdx
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
    lea     data_402000(%rip), %r12
    lea     data_402020(%rip), %r13
    mov     %rdi, %r14
    mov     %rsi, %rbx
    mov     %r14, %rdi
    mov     %r13, %rsi
    call    sub_401800
    mov     %rax, %rcx
    mov     %rbx, %rdi
    mov     %rcx, %rsi
    call    sub_401900
    mov     %rax, %rdx
    call    sub_401a00
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
    .section .text
    .global sub_401200
    .type sub_401200, @function
sub_401200:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12
    push    %r13
    mov     $503, %r12
    mov     $256, %r13
    mov     $3, %rbx
    mov     %rdi, %r8
    mov     %rsi, %r9
    call    sub_401b00
    mov     %rax, %r10
    mov     %r10, %rdi
    mov     %r8, %rsi
    call    sub_401c00
    mov     %rax, %rcx
    mov     %rcx, %rdi
    mov     %r9, %rsi
    call    sub_401d00
    mov     %rax, %rdx
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
    .section .text
    .global sub_401250
    .type sub_401250, @function
sub_401250:
    push    %rbp
    mov     %rsp, %rbp
    push    %rbx
    push    %r12
    push    %r13
    push    %r14
    mov     $1024, %r12
    mov     $524, %r13
    mov     $101, %r14
    mov     %rdi, %r8
    mov     %rsi, %r9
    call    sub_401e00
    mov     %rax, %r10
    mov     %r9, %rdi
    mov     %r8, %rsi
    call    sub_401f00
    mov     %rax, %rbx
    mov     %rbx, %rdi
    mov     %r10, %rsi
    call    sub_402000
    mov     %rax, %rdx
    pop     %r14
    pop     %r13
    pop     %r12
    pop     %rbx
    pop     %rbp
    ret
sub_401300:
    push    %rbp
    mov     %rsp, %rbp
    call    sub_402100
    mov     %rax, %rbx
    call    sub_402100
    mov     %rax, %rcx
    call    sub_402200
    pop     %rbp
    ret
sub_401800:
    push    %rbp
    mov     %rsp, %rbp
    call    sub_402300
    pop     %rbp
    ret
sub_401c00:
    push    %rbp
    mov     %rsp, %rbp
    call    sub_402400
    call    sub_402500
    call    sub_402600
    pop     %rbp
    ret
    .section .data
    .align 16
data_402000:
    .quad   0x1fffffffffffff, 0xffffffffffffffff
    .quad   0x7bc65c783158ae, 0xaed1a3c3156ee3d4
    .quad   0x6d95afb2fc7f12, 0xf5b254bb0feb4c5a
    .quad   0x1c3ac3ceff0ccd, 0x97eb406c77fe1c83
data_402020:
    .quad   0x0000000000000001, 0x0000000000000000
    .quad   0x0000000000000000, 0x0000000000000000
data_402040:
    .byte   1
    .fill   501, 1, 0
    .byte   1
data_402100:
    .quad   0x1c5, 0x0, 0x0, 0x0