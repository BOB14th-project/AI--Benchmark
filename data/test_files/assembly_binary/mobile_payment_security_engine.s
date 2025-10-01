mobile_payment_security_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40100f:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401016:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  40101d:	c7 45 f0 6f ed 9e ba 	movl   $0xba9eed6f,-0x10(%rbp)
  401024:	e8 07 01 00 00       	callq  401130 <payment_token_generator>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	lea    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	lea    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 22 01 00 00       	callq  401160 <domesticn_mobile_cipher>
  40103e:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401042:	be 10 00 00 00       	mov    $0x10,%esi
  401047:	e8 54 01 00 00       	callq  4011a0 <transaction_authentication>
  40104c:	48 8d 7d b0          	lea    -0x50(%rbp),%rdi
  401050:	be 16 00 00 00       	mov    $0x16,%esi
  401055:	e8 86 01 00 00       	callq  4011e0 <mobile_integrity_verification>
  40105a:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40105f:	bf 00 00 00 00       	mov    $0x0,%edi
  401064:	0f 05                	syscall

0000000000401130 <payment_token_generator>:
  401130:	55                   	push   %rbp
  401131:	48 89 e5             	mov    %rsp,%rbp
  401134:	48 83 ec 20          	sub    $0x20,%rsp
  401138:	c7 45 fc a1 b2 c3 d4 	movl   $0xd4c3b2a1,-0x4(%rbp)
  40113f:	c7 45 f8 e5 f6 07 18 	movl   $0x1807f6e5,-0x8(%rbp)
  401146:	c7 45 f4 29 3a 4b 5c 	movl   $0x5c4b3a29,-0xc(%rbp)
  40114d:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401150:	33 45 f8             	xor    -0x8(%rbp),%eax
  401153:	0f af 45 f4          	imul   -0xc(%rbp),%eax
  401157:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40115a:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40115d:	c9                   	leaveq
  40115e:	c3                   	retq

0000000000401160 <domesticn_mobile_cipher>:
  401160:	55                   	push   %rbp
  401161:	48 89 e5             	mov    %rsp,%rbp
  401164:	48 83 ec 30          	sub    $0x30,%rsp
  401168:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40116c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401170:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401173:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40117a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401181:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401188:	eb 2e                	jmp    4011b8 <domesticn_mobile_cipher+0x58>
  40118a:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40118d:	48 63 d0             	movslq %eax,%rdx
  401190:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401194:	48 01 d0             	add    %rdx,%rax
  401197:	0f b6 08             	movzbl (%rax),%ecx
  40119a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40119d:	0f b6 c0             	movzbl %al,%eax
  4011a0:	31 c8                	xor    %ecx,%eax
  4011a2:	8b 55 f4             	mov    -0xc(%rbp),%edx
  4011a5:	48 63 d2             	movslq %edx,%rdx
  4011a8:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4011ac:	48 01 ca             	add    %rcx,%rdx
  4011af:	88 02                	mov    %al,(%rdx)
  4011b1:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4011b4:	c1 c0 01             	rol    $0x1,%eax
  4011b7:	89 45 fc             	mov    %eax,-0x4(%rbp)
  4011ba:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  4011be:	8b 45 f4             	mov    -0xc(%rbp),%eax
  4011c1:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4011c4:	7c c4                	jl     40118a <domesticn_mobile_cipher+0x2a>
  4011c6:	90                   	nop
  4011c7:	c9                   	leaveq
  4011c8:	c3                   	retq

00000000004011a0 <transaction_authentication>:
  4011a0:	55                   	push   %rbp
  4011a1:	48 89 e5             	mov    %rsp,%rbp
  4011a4:	48 83 ec 30          	sub    $0x30,%rsp
  4011a8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4011ac:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4011af:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4011b6:	ff
  4011b7:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4011be:	be
  4011bf:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4011c6:	ef
  4011c7:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011cb:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4011cf:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4011d3:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4011d7:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4011db:	c9                   	leaveq
  4011dc:	c3                   	retq

00000000004011e0 <mobile_integrity_verification>:
  4011e0:	55                   	push   %rbp
  4011e1:	48 89 e5             	mov    %rsp,%rbp
  4011e4:	48 83 ec 20          	sub    $0x20,%rsp
  4011e8:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  4011ec:	89 75 ec             	mov    %esi,-0x14(%rbp)
  4011ef:	c7 45 fc 01 23 45 67 	movl   $0x67452301,-0x4(%rbp)
  4011f6:	c7 45 f8 89 ab cd ef 	movl   $0xefcdab89,-0x8(%rbp)
  4011fd:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401204:	eb 1b                	jmp    401221 <mobile_integrity_verification+0x41>
  401206:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401209:	c1 c0 05             	rol    $0x5,%eax
  40120c:	89 45 fc             	mov    %eax,-0x4(%rbp)
  40120f:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401212:	31 45 fc             	xor    %eax,-0x4(%rbp)
  401215:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401218:	83 c0 01             	add    $0x1,%eax
  40121b:	89 45 fc             	mov    %eax,-0x4(%rbp)
  40121e:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401222:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401225:	3b 45 ec             	cmp    -0x14(%rbp),%eax
  401228:	7c dc                	jl     401206 <mobile_integrity_verification+0x26>
  40122a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40122d:	c9                   	leaveq
  40122e:	c3                   	retq

Disassembly of section .data:

0000000000602000 <mobile_constants>:
  602000:	84 94 62 d2 ca 37 a8 	test   %dl,-0x57c82d9e(%rdx,%riz,2)
  602007:	93
  602008:	5b                   	pop    %rbx
  602009:	9d                   	popfq
  60200a:	11 96 6f ed 9e ba    	adc    %edx,-0x45611291(%rsi)
  602010:	a1 b2 c3 d4 e5 f6 07 	movabs 0x181807f6e5d4c3b2,%eax
  602017:	18 29
  602019:	3a 4b 5c             	cmp    0x5c(%rbx),%cl
  60201c:	ff ff                	(bad)
  60201e:	ff ff                	(bad)
  602020:	ff ff                	(bad)
  602022:	ff ff                	(bad)
  602024:	ac                   	lods   %ds:(%rsi),%al
  602025:	ed                   	in     (%dx),%eax
  602026:	ba be de ad be       	mov    $0xbeaddebe,%edx
  60202b:	ef                   	out    %eax,(%dx)
  60202c:	01 23                	add    %esp,(%rbx)
  60202e:	45 67               	rex.RB addr32
  602030:	89 ab cd ef          	mov    %ebp,-0x10123(%rbx)