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

    .section .data
    .align 16

data_403000:
    .fill   256, 1, 0