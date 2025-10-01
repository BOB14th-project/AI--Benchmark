quantum_communication_relay:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	48 c7 45 f8 c3 2d 4a 	movq   $0x164a2dc3,-0x8(%rbp)
  40100f:	16
  401010:	48 c7 45 f0 67 95 b3 	movq   $0x29b39567,-0x10(%rbp)
  401017:	29
  401018:	48 c7 45 e8 8a f4 c1 	movq   $0x7ec1f48a,-0x18(%rbp)
  40101f:	7e
  401020:	48 c7 45 e0 b2 e6 53 	movq   $0x4453e6b2,-0x20(%rbp)
  401027:	44
  401028:	e8 93 00 00 00       	callq  4010c0 <quantum_key_distribution>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	lea    -0x40(%rbp),%rsi
  401039:	ba 16 00 00 00       	mov    $0x16,%edx
  40103e:	e8 ad 00 00 00       	callq  4010f0 <entanglement_protection>
  401043:	48 8d 7d b0          	lea    -0x50(%rbp),%rdi
  401047:	be 08 00 00 00       	mov    $0x8,%esi
  40104c:	e8 df 00 00 00       	callq  401130 <korean_quantum_cipher>
  401051:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401056:	bf 00 00 00 00       	mov    $0x0,%edi
  40105b:	0f 05                	syscall

00000000004010c0 <quantum_key_distribution>:
  4010c0:	55                   	push   %rbp
  4010c1:	48 89 e5             	mov    %rsp,%rbp
  4010c4:	48 83 ec 30          	sub    $0x30,%rsp
  4010c8:	48 c7 45 f8 c3 2d 4a 	movq   $0x164a2dc3,-0x8(%rbp)
  4010cf:	16
  4010d0:	48 c7 45 f0 67 95 b3 	movq   $0x29b39567,-0x10(%rbp)
  4010d7:	29
  4010d8:	48 c7 45 e8 8a f4 c1 	movq   $0x7ec1f48a,-0x18(%rbp)
  4010df:	7e
  4010e0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010e4:	48 33 45 f0          	xor    -0x10(%rbp),%rax
  4010e8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4010ec:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4010f0:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4010f4:	c9                   	leaveq
  4010f5:	c3                   	retq

00000000004010f0 <entanglement_protection>:
  4010f0:	55                   	push   %rbp
  4010f1:	48 89 e5             	mov    %rsp,%rbp
  4010f4:	48 83 ec 30          	sub    $0x30,%rsp
  4010f8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4010fc:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401100:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401103:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  40110a:	67
  40110b:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  401112:	ef
  401113:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40111a:	eb 2a                	jmp    401146 <entanglement_protection+0x56>
  40111c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40111f:	48 63 d0             	movslq %eax,%rdx
  401122:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401126:	48 01 d0             	add    %rdx,%rax
  401129:	0f b6 08             	movzbl (%rax),%ecx
  40112c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401130:	0f b6 c0             	movzbl %al,%eax
  401133:	31 c8                	xor    %ecx,%eax
  401135:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401138:	48 63 d2             	movslq %edx,%rdx
  40113b:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40113f:	48 01 ca             	add    %rcx,%rdx
  401142:	88 02                	mov    %al,(%rdx)
  401144:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401148:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40114b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40114e:	7c cc                	jl     40111c <entanglement_protection+0x2c>
  401150:	90                   	nop
  401151:	c9                   	leaveq
  401152:	c3                   	retq

0000000000401130 <korean_quantum_cipher>:
  401130:	55                   	push   %rbp
  401131:	48 89 e5             	mov    %rsp,%rbp
  401134:	48 83 ec 20          	sub    $0x20,%rsp
  401138:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  40113c:	89 75 ec             	mov    %esi,-0x14(%rbp)
  40113f:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  401146:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  40114d:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401150:	33 45 f8             	xor    -0x8(%rbp),%eax
  401153:	c1 c0 08             	rol    $0x8,%eax
  401156:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401159:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40115c:	c9                   	leaveq
  40115d:	c3                   	retq