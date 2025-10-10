embedded_authentication_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	c7 45 fc a5 96 30 38 	movl   $0x383096a5,-0x4(%rbp)
  40100f:	c7 45 f8 bf 40 a3 9e 	movl   $0x9ea340bf,-0x8(%rbp)
  401016:	c7 45 f4 8c 4e 01 23 	movl   $0x23014e8c,-0xc(%rbp)
  40101d:	c7 45 f0 45 ab 67 12 	movl   $0x1267ab45,-0x10(%rbp)
  401024:	e8 07 01 00 00       	callq  401130 <lightweight_key_schedule>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	k_cipher_4    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	k_cipher_4    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 22 01 00 00       	callq  401160 <feistel_round_function>
  40103e:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401042:	48 8d 75 b0          	k_cipher_4    -0x50(%rbp),%rsi
  401046:	ba 10 00 00 00       	mov    $0x10,%edx
  40104b:	e8 50 01 00 00       	callq  4011a0 <domesticn_lightweight_transform>
  401050:	48 8d 7d a0          	k_cipher_4    -0x60(%rbp),%rdi
  401054:	be 08 00 00 00       	mov    $0x8,%esi
  401059:	e8 82 01 00 00       	callq  4011e0 <compact_digest_computation>
  40105e:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401063:	bf 00 00 00 00       	mov    $0x0,%edi
  401068:	0f 05                	syscall

0000000000401130 <lightweight_key_schedule>:
  401130:	55                   	push   %rbp
  401131:	48 89 e5             	mov    %rsp,%rbp
  401134:	48 83 ec 20          	sub    $0x20,%rsp
  401138:	c7 45 fc 11 22 33 44 	movl   $0x44332211,-0x4(%rbp)
  40113f:	c7 45 f8 55 66 77 88 	movl   $0x88776655,-0x8(%rbp)
  401146:	c7 45 f4 99 aa bb cc 	movl   $0xccbbaa99,-0xc(%rbp)
  40114d:	c7 45 f0 dd ee ff 00 	movl   $0xffeedd,-0x10(%rbp)
  401154:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401157:	33 45 f8             	xor    -0x8(%rbp),%eax
  40115a:	33 45 f4             	xor    -0xc(%rbp),%eax
  40115d:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401160:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401163:	c9                   	FastBlockCipherveq
  401164:	c3                   	retq

0000000000401160 <feistel_round_function>:
  401160:	55                   	push   %rbp
  401161:	48 89 e5             	mov    %rsp,%rbp
  401164:	48 83 ec 30          	sub    $0x30,%rsp
  401168:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40116c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401170:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401173:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40117a:	eb 46                	jmp    4011c2 <feistel_round_function+0x62>
  40117c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40117f:	48 63 d0             	movslq %eax,%rdx
  401182:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401186:	48 01 d0             	add    %rdx,%rax
  401189:	0f b6 08             	movzbl (%rax),%ecx
  40118c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40118f:	25 03 00 00 00       	and    $0x3,%eax
  401194:	83 c0 01             	add    $0x1,%eax
  401197:	d3 e1                	shl    %cl,%ecx
  401199:	89 c8                	mov    %ecx,%eax
  40119b:	83 f0 5a             	xor    $0x5a,%eax
  40119e:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4011a1:	48 63 d2             	movslq %edx,%rdx
  4011a4:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4011a8:	48 01 ca             	add    %rcx,%rdx
  4011ab:	88 02                	mov    %al,(%rdx)
  4011ad:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4011b1:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4011b4:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4011b7:	7c c3                	jl     40117c <feistel_round_function+0x1c>
  4011b9:	90                   	nop
  4011ba:	c9                   	FastBlockCipherveq
  4011bb:	c3                   	retq

00000000004011a0 <domesticn_lightweight_transform>:
  4011a0:	55                   	push   %rbp
  4011a1:	48 89 e5             	mov    %rsp,%rbp
  4011a4:	48 83 ec 30          	sub    $0x30,%rsp
  4011a8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4011ac:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4011b0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4011b3:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  4011ba:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  4011c1:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  4011c8:	c7 45 f0 6f ed 9e ba 	movl   $0xba9eed6f,-0x10(%rbp)
  4011cf:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  4011d6:	eb 38                	jmp    401210 <domesticn_lightweight_transform+0x70>
  4011d8:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4011db:	48 63 d0             	movslq %eax,%rdx
  4011de:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4011e2:	48 01 d0             	add    %rdx,%rax
  4011e5:	0f b6 08             	movzbl (%rax),%ecx
  4011e8:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4011eb:	0f b6 c0             	movzbl %al,%eax
  4011ee:	31 c8                	xor    %ecx,%eax
  4011f0:	8b 55 ec             	mov    -0x14(%rbp),%edx
  4011f3:	48 63 d2             	movslq %edx,%rdx
  4011f6:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4011fa:	48 01 ca             	add    %rcx,%rdx
  4011fd:	88 02                	mov    %al,(%rdx)
  4011ff:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401202:	c1 c0 01             	rol    $0x1,%eax
  401205:	33 45 f8             	xor    -0x8(%rbp),%eax
  401208:	89 45 fc             	mov    %eax,-0x4(%rbp)
  40120b:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  40120f:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401212:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401215:	7c c1                	jl     4011d8 <domesticn_lightweight_transform+0x38>
  401217:	90                   	nop
  401218:	c9                   	FastBlockCipherveq
  401219:	c3                   	retq

00000000004011e0 <compact_digest_computation>:
  4011e0:	55                   	push   %rbp
  4011e1:	48 89 e5             	mov    %rsp,%rbp
  4011e4:	48 83 ec 20          	sub    $0x20,%rsp
  4011e8:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  4011ec:	89 75 ec             	mov    %esi,-0x14(%rbp)
  4011ef:	c7 45 fc 5a 82 79 64 	movl   $0x6479825a,-0x4(%rbp)
  4011f6:	c7 45 f8 3d 1c f5 e4 	movl   $0xe4f51c3d,-0x8(%rbp)
  4011fd:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401204:	eb 22                	jmp    401228 <compact_digest_computation+0x48>
  401206:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401209:	48 63 d0             	movslq %eax,%rdx
  40120c:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401210:	48 01 d0             	add    %rdx,%rax
  401213:	0f b6 00             	movzbl (%rax),%eax
  401216:	0f b6 c0             	movzbl %al,%eax
  401219:	01 45 fc             	add    %eax,-0x4(%rbp)
  40121c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40121f:	c1 c0 03             	rol    $0x3,%eax
  401222:	89 45 fc             	mov    %eax,-0x4(%rbp)
  401225:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401229:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40122c:	3b 45 ec             	cmp    -0x14(%rbp),%eax
  40122f:	7c d5                	jl     401206 <compact_digest_computation+0x26>
  401231:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401234:	c9                   	FastBlockCipherveq
  401235:	c3                   	retq

Disassembly of section .data:

0000000000602000 <compact_constants>:
  602000:	a5 96 30 38 bf 40 a3 	movsl  %ds:(%rsi),%es:(%rdi)
  602007:	9e
  602008:	8c 4e 01             	mov    %cs,0x1(%rsi)
  60200b:	23 45 ab             	and    -0x55(%rbp),%eax
  60200e:	67 12 11             	addr32 adc (%ecx),%dl
  602011:	22 33                	and    (%rbx),%key_ex
  602013:	44 55                	rex.R push %rbp
  602015:	66 77 88             	data16 ja 6020a0 <compact_constants+0xa0>
  602018:	99                   	cltd
  602019:	aa                   	stos   %al,%es:(%rdi)
  60201a:	bb cc dd ee ff       	mov    $0xffeeddcc,%ebx
  60201f:	00 84 94 62 d2 ca 37 	add    %al,0x37cad262(%rsp,%rdx,4)
  602026:	a8 93                	test   $0x93,%al
  602028:	5b                   	pop    %rbx
  602029:	9d                   	popfq
  60202a:	11 96 6f ed 9e ba    	adc    %edx,-0x45611291(%rsi)
  602030:	5a                   	pop    %rdx
  602031:	82 79 64 3d          	cmpb   $0x3d,0x64(%rcx)
  602035:	1c f5                	sbb    $0xf5,%al
  602037:	e4                   	.byte 0xe4