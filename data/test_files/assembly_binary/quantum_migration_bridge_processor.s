quantum_migration_bridge_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 90          	sub    $0x90,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ff ff ff 	movq   $0x1fffffffffffff,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 ac ed ba 	movq   $0xbebaedac,-0x18(%rbp)
  40101f:	be
  401020:	48 c7 45 e0 de ad be 	movq   $0xefbeadde,-0x20(%rbp)
  401027:	ef
  401028:	e8 f3 02 00 00       	callq  401320 <legacy_algorithm_detector>
  40102d:	89 45 dc             	mov    %eax,-0x24(%rbp)
  401030:	83 7d dc 01          	cmpl   $0x1,-0x24(%rbp)
  401034:	75 0c                	jne    401042 <_start+0x42>
  401036:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  40103a:	e8 f1 02 00 00       	callq  401330 <quantum_safe_replacement>
  40103f:	48 89 45 c8          	mov    %rax,-0x38(%rbp)
  401043:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401047:	48 8d 75 b0          	lea    -0x50(%rbp),%rsi
  40104b:	ba 20 00 00 00       	mov    $0x20,%edx
  401050:	e8 fb 02 00 00       	callq  401350 <hybrid_transition_protocol>
  401055:	48 8d 7d a0          	lea    -0x60(%rbp),%rdi
  401059:	48 8d 75 90          	lea    -0x70(%rbp),%rsi
  40105d:	ba 10 00 00 00       	mov    $0x10,%edx
  401062:	e8 29 03 00 00       	callq  401390 <korean_legacy_handler>
  401067:	48 8d 7d 80          	lea    -0x80(%rbp),%rdi
  40106b:	be 40 00 00 00       	mov    $0x40,%esi
  401070:	e8 5b 03 00 00       	callq  4013d0 <migration_integrity_check>
  401075:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40107a:	bf 00 00 00 00       	mov    $0x0,%edi
  40107f:	0f 05                	syscall

0000000000401320 <legacy_algorithm_detector>:
  401320:	55                   	push   %rbp
  401321:	48 89 e5             	mov    %rsp,%rbp
  401324:	48 83 ec 20          	sub    $0x20,%rsp
  401328:	48 c7 45 f8 d1 00 00 	movq   $0xd1,-0x8(%rbp)
  40132f:	00
  401330:	48 c7 45 f0 02 00 00 	movq   $0x2,-0x10(%rbp)
  401337:	00
  401338:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40133c:	48 39 45 f0          	cmp    %rax,-0x10(%rbp)
  401340:	0f 92 c0             	setb   %al
  401343:	0f b6 c0             	movzbl %al,%eax
  401346:	89 45 fc             	mov    %eax,-0x4(%rbp)
  401349:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40134c:	c9                   	leaveq
  40134d:	c3                   	retq

0000000000401330 <quantum_safe_replacement>:
  401330:	55                   	push   %rbp
  401331:	48 89 e5             	mov    %rsp,%rbp
  401334:	48 83 ec 30          	sub    $0x30,%rsp
  401338:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40133c:	48 c7 45 f8 c3 2d 4a 	movq   $0x164a2dc3,-0x8(%rbp)
  401343:	16
  401344:	48 c7 45 f0 67 95 b3 	movq   $0x29b39567,-0x10(%rbp)
  40134b:	29
  40134c:	48 c7 45 e8 8a f4 c1 	movq   $0x7ec1f48a,-0x18(%rbp)
  401353:	7e
  401354:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401358:	48 33 45 f0          	xor    -0x10(%rbp),%rax
  40135c:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  401360:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401364:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401368:	c9                   	leaveq
  401369:	c3                   	retq

0000000000401350 <hybrid_transition_protocol>:
  401350:	55                   	push   %rbp
  401351:	48 89 e5             	mov    %rsp,%rbp
  401354:	48 83 ec 30          	sub    $0x30,%rsp
  401358:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40135c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401360:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401363:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40136a:	eb 40                	jmp    4013ac <hybrid_transition_protocol+0x5c>
  40136c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40136f:	48 63 d0             	movslq %eax,%rdx
  401372:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401376:	48 01 d0             	add    %rdx,%rax
  401379:	0f b6 08             	movzbl (%rax),%ecx
  40137c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40137f:	83 e0 07             	and    $0x7,%eax
  401382:	83 c0 01             	add    $0x1,%eax
  401385:	d3 e1                	shl    %cl,%ecx
  401387:	89 c8                	mov    %ecx,%eax
  401389:	8b 55 fc             	mov    -0x4(%rbp),%edx
  40138c:	48 63 d2             	movslq %edx,%rdx
  40138f:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  401393:	48 01 ca             	add    %rcx,%rdx
  401396:	88 02                	mov    %al,(%rdx)
  401398:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  40139c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40139f:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4013a2:	7c c8                	jl     40136c <hybrid_transition_protocol+0x1c>
  4013a4:	90                   	nop
  4013a5:	c9                   	leaveq
  4013a6:	c3                   	retq

0000000000401390 <korean_legacy_handler>:
  401390:	55                   	push   %rbp
  401391:	48 89 e5             	mov    %rsp,%rbp
  401394:	48 83 ec 30          	sub    $0x30,%rsp
  401398:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40139c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4013a0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4013a3:	48 c7 45 f8 a5 96 30 	movq   $0x383096a5,-0x8(%rbp)
  4013aa:	38
  4013ab:	48 c7 45 f0 bf 40 a3 	movq   $0x9ea340bf,-0x10(%rbp)
  4013b2:	9e
  4013b3:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4013ba:	eb 3c                	jmp    4013f8 <korean_legacy_handler+0x68>
  4013bc:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013bf:	48 63 d0             	movslq %eax,%rdx
  4013c2:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4013c6:	48 01 d0             	add    %rdx,%rax
  4013c9:	0f b6 08             	movzbl (%rax),%ecx
  4013cc:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4013d0:	0f b6 c0             	movzbl %al,%eax
  4013d3:	31 c8                	xor    %ecx,%eax
  4013d5:	89 c1                	mov    %eax,%ecx
  4013d7:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4013db:	0f b6 c0             	movzbl %al,%eax
  4013de:	31 c8                	xor    %ecx,%eax
  4013e0:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4013e3:	48 63 d2             	movslq %edx,%rdx
  4013e6:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4013ea:	48 01 ca             	add    %rcx,%rdx
  4013ed:	88 02                	mov    %al,(%rdx)
  4013ef:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4013f3:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013f6:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4013f9:	7c c1                	jl     4013bc <korean_legacy_handler+0x2c>
  4013fb:	90                   	nop
  4013fc:	c9                   	leaveq
  4013fd:	c3                   	retq

00000000004013d0 <migration_integrity_check>:
  4013d0:	55                   	push   %rbp
  4013d1:	48 89 e5             	mov    %rsp,%rbp
  4013d4:	48 83 ec 30          	sub    $0x30,%rsp
  4013d8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4013dc:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4013df:	48 c7 45 f8 5a 82 79 	movq   $0x6479825a,-0x8(%rbp)
  4013e6:	64
  4013e7:	48 c7 45 f0 3d 1c f5 	movq   $0xe4f51c3d,-0x10(%rbp)
  4013ee:	e4
  4013ef:	48 c7 45 e8 8b 44 f7 	movq   $0x9af7448b,-0x18(%rbp)
  4013f6:	9a
  4013f7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4013fe:	eb 28                	jmp    401428 <migration_integrity_check+0x58>
  401400:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401403:	48 63 d0             	movslq %eax,%rdx
  401406:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40140a:	48 01 d0             	add    %rdx,%rax
  40140d:	0f b6 00             	movzbl (%rax),%eax
  401410:	0f b6 c0             	movzbl %al,%eax
  401413:	01 45 f8             	add    %eax,-0x8(%rbp)
  401416:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401419:	c1 c0 0d             	rol    $0xd,%eax
  40141c:	89 45 f8             	mov    %eax,-0x8(%rbp)
  40141f:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401422:	31 45 f8             	xor    %eax,-0x8(%rbp)
  401425:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401429:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40142c:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40142f:	7c cf                	jl     401400 <migration_integrity_check+0x30>
  401431:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401435:	c9                   	leaveq
  401436:	c3                   	retq

Disassembly of section .data:

0000000000602000 <quantum_parameters>:
  602000:	ff ff ff ff ff ff ff 	(bad)
  602007:	ff ff ff ff ff ff ff 	(bad)
  60200e:	1f                   	(bad)
  60200f:	ac                   	lods   %ds:(%rsi),%al
  602010:	ed                   	in     (%dx),%eax
  602011:	ba be de ad be       	mov    $0xbeaddebe,%edx
  602016:	ef                   	out    %eax,(%dx)
  602017:	c3                   	retq
  602018:	2d 4a 16 67 95       	sub    $0x9567164a,%eax
  60201d:	b3 29                	mov    $0x29,%bl
  60201f:	8a f4                	mov    %ah,%dh
  602021:	c1 7e a5 96          	sarl   $0x96,-0x5b(%rsi)
  602025:	30 38                	xor    %bh,(%rax)
  602027:	bf 40 a3 9e 5a       	mov    $0x5a9ea340,%edi
  60202c:	82 79 64 3d          	cmpb   $0x3d,0x64(%rcx)
  602030:	1c f5                	sbb    $0xf5,%al
  602032:	e4 8b                	in     $0x8b,%al
  602034:	44 f7 9a             	rex.R imul %edx