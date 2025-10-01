secure_boot_verification_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401017:	be
  401018:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  40101f:	ef
  401020:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  401027:	fe
  401028:	e8 83 00 00 00       	callq  4010b0 <boot_signature_verification>
  40102d:	89 45 dc             	mov    %eax,-0x24(%rbp)
  401030:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401034:	48 8d 75 c0          	lea    -0x40(%rbp),%rsi
  401038:	ba 08 00 00 00       	mov    $0x8,%edx
  40103d:	e8 9e 00 00 00       	callq  4010e0 <korean_secure_boot_cipher>
  401042:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401047:	bf 00 00 00 00       	mov    $0x0,%edi
  40104c:	0f 05                	syscall

00000000004010b0 <boot_signature_verification>:
  4010b0:	55                   	push   %rbp
  4010b1:	48 89 e5             	mov    %rsp,%rbp
  4010b4:	48 83 ec 30          	sub    $0x30,%rsp
  4010b8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4010bf:	ff
  4010c0:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4010c7:	be
  4010c8:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4010cf:	ef
  4010d0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010d4:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4010d8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4010dc:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4010e0:	b8 01 00 00 00       	mov    $0x1,%eax
  4010e5:	c9                   	leaveq
  4010e6:	c3                   	retq

00000000004010e0 <korean_secure_boot_cipher>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 83 ec 30          	sub    $0x30,%rsp
  4010e8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4010ec:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4010f0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4010f3:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  4010fa:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401101:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401108:	eb 28                	jmp    401132 <korean_secure_boot_cipher+0x52>
  40110a:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40110d:	48 63 d0             	movslq %eax,%rdx
  401110:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401114:	48 01 d0             	add    %rdx,%rax
  401117:	0f b6 08             	movzbl (%rax),%ecx
  40111a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40111d:	0f b6 c0             	movzbl %al,%eax
  401120:	31 c8                	xor    %ecx,%eax
  401122:	8b 55 f4             	mov    -0xc(%rbp),%edx
  401125:	48 63 d2             	movslq %edx,%rdx
  401128:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40112c:	48 01 ca             	add    %rcx,%rdx
  40112f:	88 02                	mov    %al,(%rdx)
  401131:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401135:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401138:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40113b:	7c cd                	jl     40110a <korean_secure_boot_cipher+0x2a>
  40113d:	90                   	nop
  40113e:	c9                   	leaveq
  40113f:	c3                   	retq