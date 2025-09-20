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

    call    sub_401100
    mov     %rax, %rbx

    mov     %rbx, %rdi
    mov     %r12, %rsi
    call    sub_401200
    mov     %rax, %r8

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

    mov     %rdi, %rax
    mov     %rsi, %rcx
    mov     %rdx, %r8

    mov     $1, %rbx

loc_401120:
    test    %rcx, %rcx
    jz      loc_401160
    test    $1, %rcx
    jz      loc_401140

    mul     %rbx
    div     %r8
    mov     %rdx, %rbx

loc_401140:
    mov     %rax, %r9
    mul     %r9
    div     %r8
    mov     %rdx, %rax
    shr     $1, %rcx
    jmp     loc_401120

loc_401160:
    mov     %rbx, %rax
    pop     %rbp
    ret

sub_401200:
    push    %rbp
    mov     %rsp, %rbp

    mov     %rdi, %rax
    add     %rsi, %rax

    pop     %rbp
    ret

    .section .data
    .align 8

data_404000:
    .quad   0xffffffffffffffffc90fdaa22168c234, 0xc4c6628b80dc1cd129024e08
    .quad   0x8a67cc74020bbea63b139b22514a08798e3404ddef9519b3
    .quad   0xcd3a431b302b0a6df25f14374fe1356d6d51c245e485b576