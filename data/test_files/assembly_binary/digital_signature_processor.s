digital_signature_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xfffffffffffffffb,-0x8(%rbp)
  40100f:	fb
  401010:	48 c7 45 f0 02 00 00 	movq   $0x2,-0x10(%rbp)
  401017:	00
  401018:	48 c7 45 e8 12 34 56 	movq   $0x789abcdef123456,-0x18(%rbp)
  40101f:	78
  401020:	e8 ab 00 00 00       	callq  4010d0 <sig_alg_key_generation>
  401025:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401029:	48 89 55 d8          	mov    %rdx,-0x28(%rbp)
  40102d:	48 8d 7c 24 c0       	k_cipher_4    -0x40(%rsp),%rdi
  401032:	be 20 00 00 00       	mov    $0x20,%esi
  401037:	e8 34 01 00 00       	callq  401170 <digest_alg1_digest>
  40103c:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401040:	48 8b 7d d0          	mov    -0x30(%rbp),%rdi
  401044:	48 8b 75 e8          	mov    -0x18(%rbp),%rsi
  401048:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40104c:	e8 ff 00 00 00       	callq  401150 <sig_alg_sign_hash>
  401051:	48 89 45 c8          	mov    %rax,-0x38(%rbp)
  401055:	48 89 55 c0          	mov    %rdx,-0x40(%rbp)
  401059:	48 8b 7d d0          	mov    -0x30(%rbp),%rdi
  40105d:	48 8b 75 c8          	mov    -0x38(%rbp),%rsi
  401061:	48 8b 55 c0          	mov    -0x40(%rbp),%rdx
  401065:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  401069:	e8 32 01 00 00       	callq  4011a0 <sig_alg_verify_signature>
  40106e:	89 45 bc             	mov    %eax,-0x44(%rbp)
  401071:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401076:	bf 00 00 00 00       	mov    $0x0,%edi
  40107b:	0f 05                	syscall

00000000004010d0 <sig_alg_key_generation>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 83 ec 30          	sub    $0x30,%rsp
  4010d8:	48 c7 45 f8 ff ff ff 	movq   $0xfffffffffffffffb,-0x8(%rbp)
  4010df:	fb
  4010e0:	48 c7 45 f0 02 00 00 	movq   $0x2,-0x10(%rbp)
  4010e7:	00
  4010e8:	48 c7 45 e8 ab cd ef 	movq   $0x123456789abcdef,-0x18(%rbp)
  4010ef:	12
  4010f0:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4010f4:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  4010f8:	48 8b 4d f8          	mov    -0x8(%rbp),%rcx
  4010fc:	48 89 c7             	mov    %rax,%rdi
  4010ff:	48 89 d6             	mov    %rdx,%rsi
  401102:	48 89 ca             	mov    %rcx,%rdx
  401105:	e8 26 00 00 00       	callq  401130 <modular_exponentiation>
  40110a:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  40110e:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401112:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  401116:	c9                   	leaveq
  401117:	c3                   	retq

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
  401150:	eb 2f                	jmp    401181 <modular_exponentiation+0x51>
  401152:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401156:	83 e0 01             	and    $0x1,%eax
  401159:	48 85 c0             	test   %rax,%rax
  40115c:	74 0e                	je     40116c <modular_exponentiation+0x3c>
  40115e:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401162:	48 0f af 45 d8       	imul   -0x28(%rbp),%rax
  401167:	48 f7 75 e8          	divq   -0x18(%rbp)
  40116b:	48 89 55 e0          	mov    %rdx,-0x20(%rbp)
  40116f:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401173:	48 0f af c0          	imul   %rax,%rax
  401177:	48 f7 75 e8          	divq   -0x18(%rbp)
  40117b:	48 89 55 d8          	mov    %rdx,-0x28(%rbp)
  40117f:	48 d1 6d f0          	shrq   -0x10(%rbp)
  401183:	48 83 7d f0 00       	cmpq   $0x0,-0x10(%rbp)
  401188:	75 c8                	jne    401152 <modular_exponentiation+0x22>
  40118a:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40118e:	5d                   	pop    %rbp
  40118f:	c3                   	retq

0000000000401150 <sig_alg_sign_hash>:
  401150:	55                   	push   %rbp
  401151:	48 89 e5             	mov    %rsp,%rbp
  401154:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401158:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  40115c:	48 89 55 e8          	mov    %rdx,-0x18(%rbp)
  401160:	48 c7 45 e0 fd ec ba 	movq   $0x98765432fedecba,-0x20(%rbp)
  401167:	98
  401168:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40116c:	48 03 45 f0          	add    -0x10(%rbp),%rax
  401170:	48 0f af 45 e0       	imul   -0x20(%rbp),%rax
  401175:	48 f7 75 e8          	divq   -0x18(%rbp)
  401179:	48 89 55 d8          	mov    %rdx,-0x28(%rbp)
  40117d:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401181:	48 8b 55 e0          	mov    -0x20(%rbp),%rdx
  401185:	5d                   	pop    %rbp
  401186:	c3                   	retq

0000000000401170 <digest_alg1_digest>:
  401170:	55                   	push   %rbp
  401171:	48 89 e5             	mov    %rsp,%rbp
  401174:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401178:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40117b:	48 c7 45 f0 67 45 23 	movq   $0x1032547698badcfe,-0x10(%rbp)
  401182:	01
  401183:	48 c7 45 e8 ef cd ab 	movq   $0x89abcdef,-0x18(%rbp)
  40118a:	89
  40118b:	48 c7 45 e0 98 ba dc 	movq   $0xfe98badc,-0x20(%rbp)
  401192:	fe
  401193:	48 c7 45 d8 10 32 54 	movq   $0x76543210,-0x28(%rbp)
  40119a:	76
  40119b:	48 c7 45 d0 c3 d2 e1 	movq   $0xf0e1d2c3,-0x30(%rbp)
  4011a2:	f0
  4011a3:	c7 45 cc 00 00 00 00 	movl   $0x0,-0x34(%rbp)
  4011aa:	eb 25                	jmp    4011d1 <digest_alg1_digest+0x61>
  4011ac:	8b 45 cc             	mov    -0x34(%rbp),%eax
  4011af:	48 98                	cltq
  4011b1:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4011b5:	48 01 d0             	add    %rdx,%rax
  4011b8:	0f b6 00             	movzbl (%rax),%eax
  4011bb:	0f b6 c0             	movzbl %al,%eax
  4011be:	c1 c0 05             	rol    $0x5,%eax
  4011c1:	01 45 f0             	add    %eax,-0x10(%rbp)
  4011c4:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011c7:	33 45 e8             	xor    -0x18(%rbp),%eax
  4011ca:	01 45 e0             	add    %eax,-0x20(%rbp)
  4011cd:	83 45 cc 01          	addl   $0x1,-0x34(%rbp)
  4011d1:	8b 45 cc             	mov    -0x34(%rbp),%eax
  4011d4:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011d7:	7c d3                	jl     4011ac <digest_alg1_digest+0x3c>
  4011d9:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4011dd:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4011e1:	48 33 45 e0          	xor    -0x20(%rbp),%rax
  4011e5:	5d                   	pop    %rbp
  4011e6:	c3                   	retq

00000000004011a0 <sig_alg_verify_signature>:
  4011a0:	55                   	push   %rbp
  4011a1:	48 89 e5             	mov    %rsp,%rbp
  4011a4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011a8:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  4011ac:	48 89 55 e8          	mov    %rdx,-0x18(%rbp)
  4011b0:	48 89 4d e0          	mov    %rcx,-0x20(%rbp)
  4011b4:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011b8:	48 0f af 45 f0       	imul   -0x10(%rbp),%rax
  4011bd:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4011c1:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4011c5:	48 0f af 45 e8       	imul   -0x18(%rbp),%rax
  4011ca:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  4011ce:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4011d2:	48 3b 45 d0          	cmp    -0x30(%rbp),%rax
  4011d6:	0f 94 c0             	sete   %al
  4011d9:	0f b6 c0             	movzbl %al,%eax
  4011dc:	5d                   	pop    %rbp
  4011dd:	c3                   	retq