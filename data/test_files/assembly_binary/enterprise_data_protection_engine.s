enterprise_data_protection_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 80          	sub    $0x80,%rsp
  401008:	48 c7 45 f8 67 45 23 	movq   $0x1a234567,-0x8(%rbp)
  40100f:	1a
  401010:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  401017:	ef
  401018:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  40101f:	98
  401020:	48 c7 45 e0 76 54 32 	movq   $0x10325476,-0x20(%rbp)
  401027:	10
  401028:	e8 93 02 00 00       	callq  4012c0 <large_modular_computation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401035:	48 89 c7             	mov    %rax,%rdi
  401038:	e8 a3 02 00 00       	callq  4012e0 <inverse_transform_calculation>
  40103d:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401041:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401045:	48 8d 75 b0          	lea    -0x50(%rbp),%rsi
  401049:	ba 10 00 00 00       	mov    $0x10,%edx
  40104e:	e8 ed 02 00 00       	callq  401340 <korean_feistel_round>
  401053:	48 8d 7d a0          	lea    -0x60(%rbp),%rdi
  401057:	48 8d 75 90          	lea    -0x70(%rbp),%rsi
  40105b:	ba 80 00 00 00       	mov    $0x80,%edx
  401060:	e8 1b 03 00 00       	callq  401380 <substitution_box_transform>
  401065:	48 8d 7d 80          	lea    -0x80(%rbp),%rdi
  401069:	be 20 00 00 00       	mov    $0x20,%esi
  40106e:	e8 4d 03 00 00       	callq  4013c0 <digest_computation_engine>
  401073:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401078:	bf 00 00 00 00       	mov    $0x0,%edi
  40107d:	0f 05                	syscall

00000000004012c0 <large_modular_computation>:
  4012c0:	55                   	push   %rbp
  4012c1:	48 89 e5             	mov    %rsp,%rbp
  4012c4:	48 83 ec 40          	sub    $0x40,%rsp
  4012c8:	48 c7 45 f8 ff ff 00 	movq   $0x10000ffff,-0x8(%rbp)
  4012cf:	00
  4012d0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012d4:	48 c1 e8 10          	shr    $0x10,%rax
  4012d8:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  4012dc:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4012e0:	c9                   	leaveq
  4012e1:	c3                   	retq

00000000004012e0 <inverse_transform_calculation>:
  4012e0:	55                   	push   %rbp
  4012e1:	48 89 e5             	mov    %rsp,%rbp
  4012e4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4012e8:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012ec:	48 f7 d0             	not    %rax
  4012ef:	48 83 c0 01          	add    $0x1,%rax
  4012f3:	5d                   	pop    %rbp
  4012f4:	c3                   	retq

0000000000401340 <korean_feistel_round>:
  401340:	55                   	push   %rbp
  401341:	48 89 e5             	mov    %rsp,%rbp
  401344:	48 83 ec 30          	sub    $0x30,%rsp
  401348:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40134c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401350:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401353:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40135a:	eb 2a                	jmp    401386 <korean_feistel_round+0x46>
  40135c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40135f:	48 63 d0             	movslq %eax,%rdx
  401362:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401366:	48 01 d0             	add    %rdx,%rax
  401369:	0f b6 08             	movzbl (%rax),%ecx
  40136c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40136f:	48 63 d0             	movslq %eax,%rdx
  401372:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401376:	48 01 d0             	add    %rdx,%rax
  401379:	0f b6 00             	movzbl (%rax),%eax
  40137c:	31 c8                	xor    %ecx,%eax
  40137e:	88 02                	mov    %al,(%rdx)
  401380:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401384:	eb 00                	jmp    401386 <korean_feistel_round+0x46>
  401386:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401389:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40138c:	7c ce                	jl     40135c <korean_feistel_round+0x1c>
  40138e:	90                   	nop
  40138f:	c9                   	leaveq
  401390:	c3                   	retq

0000000000401380 <substitution_box_transform>:
  401380:	55                   	push   %rbp
  401381:	48 89 e5             	mov    %rsp,%rbp
  401384:	48 83 ec 20          	sub    $0x20,%rsp
  401388:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  40138c:	48 89 75 e8          	mov    %rsi,-0x18(%rbp)
  401390:	89 55 e4             	mov    %edx,-0x1c(%rbp)
  401393:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40139a:	eb 3c                	jmp    4013d8 <substitution_box_transform+0x58>
  40139c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40139f:	48 63 d0             	movslq %eax,%rdx
  4013a2:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4013a6:	48 01 d0             	add    %rdx,%rax
  4013a9:	0f b6 00             	movzbl (%rax),%eax
  4013ac:	0f b6 c0             	movzbl %al,%eax
  4013af:	25 0f 00 00 00       	and    $0xf,%eax
  4013b4:	48 98                	cltq
  4013b6:	48 8d 14 85 00 00 00 	lea    0x0(,%rax,4),%rdx
  4013bd:	00
  4013be:	48 8d 05 7b 0c 20 00 	lea    0x200c7b(%rip),%rax
  4013c5:	8b 04 02             	mov    (%rdx,%rax,1),%eax
  4013c8:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4013cb:	48 63 d2             	movslq %edx,%rdx
  4013ce:	48 8b 4d e8          	mov    -0x18(%rbp),%rcx
  4013d2:	48 01 ca             	add    %rcx,%rdx
  4013d5:	88 02                	mov    %al,(%rdx)
  4013d7:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4013db:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013de:	3b 45 e4             	cmp    -0x1c(%rbp),%eax
  4013e1:	7c b9                	jl     40139c <substitution_box_transform+0x1c>
  4013e3:	90                   	nop
  4013e4:	c9                   	leaveq
  4013e5:	c3                   	retq

00000000004013c0 <digest_computation_engine>:
  4013c0:	55                   	push   %rbp
  4013c1:	48 89 e5             	mov    %rsp,%rbp
  4013c4:	48 83 ec 30          	sub    $0x30,%rsp
  4013c8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4013cc:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4013cf:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  4013d6:	67
  4013d7:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  4013de:	ef
  4013df:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  4013e6:	98
  4013e7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4013ee:	eb 28                	jmp    401418 <digest_computation_engine+0x58>
  4013f0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013f3:	48 63 d0             	movslq %eax,%rdx
  4013f6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4013fa:	48 01 d0             	add    %rdx,%rax
  4013fd:	0f b6 00             	movzbl (%rax),%eax
  401400:	0f b6 c0             	movzbl %al,%eax
  401403:	01 45 f8             	add    %eax,-0x8(%rbp)
  401406:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401409:	c1 c0 07             	rol    $0x7,%eax
  40140c:	89 45 f8             	mov    %eax,-0x8(%rbp)
  40140f:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401412:	31 45 f8             	xor    %eax,-0x8(%rbp)
  401415:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401419:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40141c:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40141f:	7c cf                	jl     4013f0 <digest_computation_engine+0x30>
  401421:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401425:	c9                   	leaveq
  401426:	c3                   	retq

Disassembly of section .data:

0000000000602000 <sbox_lookup_table>:
  602000:	63 7c 77 7b 	arpl   %di,0x7b(%rax,%rsi,2)
  602004:	f2 6b 6f c5 	repnz imul $0xffffffc5,%edi,%ebp
  602008:	30 01                	xor    %al,(%rcx)
  60200a:	67 2b fe             	addr32 sub %esi,%edi
  60200d:	d7                   	xlat   %ds:(%rbx)
  60200e:	ab                   	stos   %eax,%es:(%rdi)
  60200f:	76 ca                	jbe    601fdb <sbox_lookup_table-0x25>