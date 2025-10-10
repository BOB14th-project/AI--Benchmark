biometric_authentication_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	c7 45 fc 5a 82 79 64 	movl   $0x6479825a,-0x4(%rbp)
  40100f:	c7 45 f8 3d 1c f5 e4 	movl   $0xe4f51c3d,-0x8(%rbp)
  401016:	c7 45 f4 8b 44 f7 9a 	movl   $0x9af7448b,-0xc(%rbp)
  40101d:	c7 45 f0 2e 93 61 07 	movl   $0x761932e,-0x10(%rbp)
  401024:	e8 87 00 00 00       	callq  4010b0 <biometric_key_extraction>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	k_cipher_4    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	k_cipher_4    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 a2 00 00 00       	callq  4010e0 <domesticn_biometric_cipher>
  40103e:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401042:	be 16 00 00 00       	mov    $0x16,%esi
  401047:	e8 d4 00 00 00       	callq  401120 <template_protection>
  40104c:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401051:	bf 00 00 00 00       	mov    $0x0,%edi
  401056:	0f 05                	syscall

00000000004010b0 <biometric_key_extraction>:
  4010b0:	55                   	push   %rbp
  4010b1:	48 89 e5             	mov    %rsp,%rbp
  4010b4:	48 83 ec 20          	sub    $0x20,%rsp
  4010b8:	c7 45 fc a9 b8 c7 d6 	movl   $0xd6c7b8a9,-0x4(%rbp)
  4010bf:	c7 45 f8 e5 f4 03 12 	movl   $0x1203f4e5,-0x8(%rbp)
  4010c6:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4010c9:	0f af 45 f8          	imul   -0x8(%rbp),%eax
  4010cd:	c1 c0 05             	rol    $0x5,%eax
  4010d0:	89 45 f4             	mov    %eax,-0xc(%rbp)
  4010d3:	8b 45 f4             	mov    -0xc(%rbp),%eax
  4010d6:	c9                   	leaveq
  4010d7:	c3                   	retq

00000000004010e0 <domesticn_biometric_cipher>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 83 ec 30          	sub    $0x30,%rsp
  4010e8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4010ec:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4010f0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4010f3:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  4010fa:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401101:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401108:	eb 28                	jmp    401132 <domesticn_biometric_cipher+0x52>
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
  40113b:	7c cd                	jl     40110a <domesticn_biometric_cipher+0x2a>
  40113d:	90                   	nop
  40113e:	c9                   	leaveq
  40113f:	c3                   	retq

0000000000401120 <template_protection>:
  401120:	55                   	push   %rbp
  401121:	48 89 e5             	mov    %rsp,%rbp
  401124:	48 83 ec 20          	sub    $0x20,%rsp
  401128:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  40112c:	89 75 ec             	mov    %esi,-0x14(%rbp)
  40112f:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  401136:	ff
  401137:	c7 45 fc ac ed ba be 	movl   $0xbebaedac,-0x4(%rbp)
  40113e:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401142:	48 f7 65 fc          	mulq   -0x4(%rbp)
  401146:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  40114a:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40114e:	c9                   	leaveq
  40114f:	c3                   	retq