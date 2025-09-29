secure_communication_protocol:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	48 c7 45 f8 01 23 45 	movq   $0x6789abcdef234501,-0x8(%rbp)
  40100f:	67
  401010:	48 c7 45 f0 89 ab cd 	movq   $0xfedcba9876543210,-0x10(%rbp)
  401017:	ef
  401018:	48 c7 45 e8 fe dc ba 	movq   $0x98765432fedcba98,-0x18(%rbp)
  40101f:	98
  401020:	e8 ab 00 00 00       	callq  4010d0 <diffie_hellman_init>
  401025:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401029:	48 89 55 d8          	mov    %rdx,-0x28(%rbp)
  40102d:	48 8b 7d e0          	mov    -0x20(%rbp),%rdi
  401031:	48 8b 75 d8          	mov    -0x28(%rbp),%rsi
  401035:	e8 16 01 00 00       	callq  401150 <compute_shared_secret>
  40103a:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  40103e:	48 8b 7d d0          	mov    -0x30(%rbp),%rdi
  401042:	be 20 00 00 00       	mov    $0x20,%esi
  401047:	e8 64 01 00 00       	callq  4011b0 <stream_cipher_init>
  40104c:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401050:	be 10 00 00 00       	mov    $0x10,%esi
  401055:	e8 96 01 00 00       	callq  4011f0 <encrypt_message>
  40105a:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40105f:	bf 00 00 00 00       	mov    $0x0,%edi
  401064:	0f 05                	syscall

00000000004010d0 <diffie_hellman_init>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 83 ec 30          	sub    $0x30,%rsp
  4010d8:	48 c7 45 f8 ff ff ff 	movq   $0xfffffffffffffffb,-0x8(%rbp)
  4010df:	fb
  4010e0:	48 c7 45 f0 02 00 00 	movq   $0x2,-0x10(%rbp)
  4010e7:	00
  4010e8:	48 c7 45 e8 12 34 56 	movq   $0x789abcdef234567,-0x18(%rbp)
  4010ef:	78
  4010f0:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4010f4:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  4010f8:	48 8b 4d f8          	mov    -0x8(%rbp),%rcx
  4010fc:	48 89 c7             	mov    %rax,%rdi
  4010ff:	48 89 d6             	mov    %rdx,%rsi
  401102:	48 89 ca             	mov    %rcx,%rdx
  401105:	e8 26 00 00 00       	callq  401130 <modular_exponentiation>
  40110a:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  40110e:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401112:	48 c7 45 d8 ab cd ef 	movq   $0x123456789abcdef,-0x28(%rbp)
  401119:	12
  40111a:	48 8b 55 d8          	mov    -0x28(%rbp),%rdx
  40111e:	c9                   	leaveq
  40111f:	c3                   	retq

0000000000401130 <modular_exponentiation>:
  401130:	55                   	push   %rbp
  401131:	48 89 e5             	mov    %rsp,%rbp
  401134:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401138:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  40113c:	48 89 55 e8          	mov    %rdx,-0x18(%rbp)
  401140:	48 c7 45 e0 01 00 00 	movq   $0x1,-0x20(%rbp)
  401147:	00
  401148:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40114c:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401150:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401154:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401158:	eb 2f                	jmp    401189 <modular_exponentiation+0x59>
  40115a:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  40115e:	83 e0 01             	and    $0x1,%eax
  401161:	48 85 c0             	test   %rax,%rax
  401164:	74 0e                	je     401174 <modular_exponentiation+0x44>
  401166:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40116a:	48 0f af 45 d8       	imul   -0x28(%rbp),%rax
  40116f:	48 f7 75 e8          	divq   -0x18(%rbp)
  401173:	48 89 55 e0          	mov    %rdx,-0x20(%rbp)
  401177:	eb 01                	jmp    40117a <modular_exponentiation+0x4a>
  401179:	90                   	nop
  40117a:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  40117e:	48 0f af c0          	imul   %rax,%rax
  401182:	48 f7 75 e8          	divq   -0x18(%rbp)
  401186:	48 89 55 d8          	mov    %rdx,-0x28(%rbp)
  40118a:	48 d1 6d d0          	shrq   -0x30(%rbp)
  40118e:	eb 05                	jmp    401195 <modular_exponentiation+0x65>
  401190:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  401194:	90                   	nop
  401195:	48 83 7d d0 00       	cmpq   $0x0,-0x30(%rbp)
  40119a:	75 be                	jne    40115a <modular_exponentiation+0x2a>
  40119c:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4011a0:	5d                   	pop    %rbp
  4011a1:	c3                   	retq

0000000000401150 <compute_shared_secret>:
  401150:	55                   	push   %rbp
  401151:	48 89 e5             	mov    %rsp,%rbp
  401154:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401158:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  40115c:	48 c7 45 e8 ff ff ff 	movq   $0xfffffffffffffffb,-0x18(%rbp)
  401163:	fb
  401164:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401168:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  40116c:	48 8b 4d e8          	mov    -0x18(%rbp),%rcx
  401170:	48 89 c7             	mov    %rax,%rdi
  401173:	48 89 d6             	mov    %rdx,%rsi
  401176:	48 89 ca             	mov    %rcx,%rdx
  401179:	e8 b2 ff ff ff       	callq  401130 <modular_exponentiation>
  40117e:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401182:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401186:	5d                   	pop    %rbp
  401187:	c3                   	retq

00000000004011b0 <stream_cipher_init>:
  4011b0:	55                   	push   %rbp
  4011b1:	48 89 e5             	mov    %rsp,%rbp
  4011b4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011b8:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4011bb:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  4011c2:	eb 1a                	jmp    4011de <stream_cipher_init+0x2e>
  4011c4:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011c7:	48 98                	cltq
  4011c9:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4011cd:	48 01 d0             	add    %rdx,%rax
  4011d0:	8b 55 f0             	mov    -0x10(%rbp),%edx
  4011d3:	88 10                	mov    %dl,(%rax)
  4011d5:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011d8:	31 10                	xor    %edx,(%rax)
  4011da:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011de:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011e1:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011e4:	7c de                	jl     4011c4 <stream_cipher_init+0x14>
  4011e6:	90                   	nop
  4011e7:	5d                   	pop    %rbp
  4011e8:	c3                   	retq

00000000004011f0 <encrypt_message>:
  4011f0:	55                   	push   %rbp
  4011f1:	48 89 e5             	mov    %rsp,%rbp
  4011f4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011f8:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4011fb:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  401202:	eb 2a                	jmp    40122e <encrypt_message+0x3e>
  401204:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401207:	48 98                	cltq
  401209:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40120d:	48 01 d0             	add    %rdx,%rax
  401210:	0f b6 00             	movzbl (%rax),%eax
  401213:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401216:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401219:	83 e0 ff             	and    $0xff,%eax
  40121c:	31 45 ec             	xor    %eax,-0x14(%rbp)
  40121f:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401222:	48 98                	cltq
  401224:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401228:	48 01 d0             	add    %rdx,%rax
  40122b:	8b 55 ec             	mov    -0x14(%rbp),%edx
  40122e:	88 10                	mov    %dl,(%rax)
  401230:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  401234:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401237:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  40123a:	7c c8                	jl     401204 <encrypt_message+0x14>
  40123c:	90                   	nop
  40123d:	5d                   	pop    %rbp
  40123e:	c3                   	retq