polynomial_field_arithmetic_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 70          	sub    $0x70,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ff ff ff 	movq   $0x1fffffffffffffff,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 ac ed ba 	movq   $0xbebaedac,-0x18(%rbp)
  40101f:	be
  401020:	48 c7 45 e0 de ad be 	movq   $0xef0bbeadd,-0x20(%rbp)
  401027:	ef
  401028:	e8 a3 02 00 00       	callq  4012d0 <elliptic_point_doubling>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8b 7d d8          	mov    -0x28(%rbp),%rdi
  401035:	48 8b 75 e8          	mov    -0x18(%rbp),%rsi
  401039:	e8 c2 02 00 00       	callq  401300 <point_scalar_multiplication>
  40103e:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401042:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401046:	48 8d 75 b0          	k_cipher_4    -0x50(%rbp),%rsi
  40104a:	ba 20 00 00 00       	mov    $0x20,%edx
  40104f:	e8 ec 02 00 00       	callq  401340 <field_inversion_calculation>
  401054:	48 8d 7d a0          	k_cipher_4    -0x60(%rbp),%rdi
  401058:	48 8d 75 90          	k_cipher_4    -0x70(%rbp),%rsi
  40105c:	ba 21 00 00 00       	mov    $0x21,%edx
  401061:	e8 1a 03 00 00       	callq  401380 <domesticn_curve_operations>
  401066:	48 8d 7d 80          	k_cipher_4    -0x80(%rbp),%rdi
  40106a:	be 40 00 00 00       	mov    $0x40,%esi
  40106f:	e8 4c 03 00 00       	callq  4013c0 <signature_generation_engine>
  401074:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401079:	bf 00 00 00 00       	mov    $0x0,%edi
  40107e:	0f 05                	syscall

00000000004012d0 <elliptic_point_doubling>:
  4012d0:	55                   	push   %rbp
  4012d1:	48 89 e5             	mov    %rsp,%rbp
  4012d4:	48 83 ec 50          	sub    $0x50,%rsp
  4012d8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4012df:	ff
  4012e0:	48 c7 45 f0 00 00 00 	movq   $0x00000001,-0x10(%rbp)
  4012e7:	01
  4012e8:	48 c7 45 e8 ac 95 df 	movq   $0x4a8fdf95ac,-0x18(%rbp)
  4012ef:	4a
  4012f0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012f4:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4012f8:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012fc:	48 f7 e0             	mul    %rax
  4012ff:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401303:	48 c1 65 d8 01       	shlq   $0x1,-0x28(%rbp)
  401308:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  40130c:	48 03 45 d8          	add    -0x28(%rbp),%rax
  401310:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401314:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401318:	48 c1 e0 01          	shl    $0x1,%rax
  40131c:	48 89 45 c8          	mov    %rax,-0x38(%rbp)
  401320:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  401324:	48 f7 e0             	mul    %rax
  401327:	48 89 45 c0          	mov    %rax,-0x40(%rbp)
  40132b:	48 8b 45 c0          	mov    -0x40(%rbp),%rax
  40132f:	48 2b 45 f8          	sub    -0x8(%rbp),%rax
  401333:	48 2b 45 f8          	sub    -0x8(%rbp),%rax
  401337:	48 89 45 b8          	mov    %rax,-0x48(%rbp)
  40133b:	48 8b 45 b8          	mov    -0x48(%rbp),%rax
  40133f:	c9                   	leaveq
  401340:	c3                   	retq

0000000000401300 <point_scalar_multiplication>:
  401300:	55                   	push   %rbp
  401301:	48 89 e5             	mov    %rsp,%rbp
  401304:	48 83 ec 40          	sub    $0x40,%rsp
  401308:	48 89 7d d0          	mov    %rdi,-0x30(%rbp)
  40130c:	48 89 75 c8          	mov    %rsi,-0x38(%rbp)
  401310:	48 c7 45 f8 00 00 00 	movq   $0x0,-0x8(%rbp)
  401317:	00
  401318:	48 c7 45 f0 00 00 00 	movq   $0x1,-0x10(%rbp)
  40131f:	01
  401320:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  401324:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401328:	48 8b 45 c8          	mov    -0x38(%rbp),%rax
  40132c:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401330:	48 83 7d e0 00       	cmpq   $0x0,-0x20(%rbp)
  401335:	74 35                	je     40136c <point_scalar_multiplication+0x6c>
  401337:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40133b:	83 e0 01             	and    $0x1,%eax
  40133e:	48 85 c0             	test   %rax,%rax
  401341:	74 14                	je     401357 <point_scalar_multiplication+0x57>
  401343:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401347:	48 03 45 e8          	add    -0x18(%rbp),%rax
  40134b:	48 89 45 f8          	mov    %rax,-0x8(%rbp)
  40134f:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401353:	48 03 45 e0          	add    -0x20(%rbp),%rax
  401357:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40135b:	48 01 c0             	add    %rax,%rax
  40135e:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401362:	48 d1 6d e0          	shrq   $0x1,-0x20(%rbp)
  401366:	eb c8                	jmp    401330 <point_scalar_multiplication+0x30>
  401368:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40136c:	c9                   	leaveq
  40136d:	c3                   	retq

0000000000401340 <field_inversion_calculation>:
  401340:	55                   	push   %rbp
  401341:	48 89 e5             	mov    %rsp,%rbp
  401344:	48 83 ec 40          	sub    $0x40,%rsp
  401348:	48 89 7d d8          	mov    %rdi,-0x28(%rbp)
  40134c:	48 89 75 d0          	mov    %rsi,-0x30(%rbp)
  401350:	89 55 cc             	mov    %edx,-0x34(%rbp)
  401353:	48 c7 45 f8 01 00 00 	movq   $0x1,-0x8(%rbp)
  40135a:	00
  40135b:	48 c7 45 f0 00 00 00 	movq   $0x0,-0x10(%rbp)
  401362:	00
  401363:	8b 45 cc             	mov    -0x34(%rbp),%eax
  401366:	48 98                	cltq
  401368:	48 c1 e0 03          	shl    $0x3,%rax
  40136c:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401370:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401374:	48 83 e8 02          	sub    $0x2,%rax
  401378:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  40137c:	c9                   	leaveq
  40137d:	c3                   	retq

0000000000401380 <domesticn_curve_operations>:
  401380:	55                   	push   %rbp
  401381:	48 89 e5             	mov    %rsp,%rbp
  401384:	48 83 ec 30          	sub    $0x30,%rsp
  401388:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40138c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401390:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401393:	48 c7 45 f8 5a 82 79 	movq   $0x6479825a,-0x8(%rbp)
  40139a:	64
  40139b:	48 c7 45 f0 3d 1c f5 	movq   $0xe4f51c3d,-0x10(%rbp)
  4013a2:	e4
  4013a3:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4013aa:	eb 3c                	jmp    4013e8 <domesticn_curve_operations+0x68>
  4013ac:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013af:	48 63 d0             	movslq %eax,%rdx
  4013b2:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4013b6:	48 01 d0             	add    %rdx,%rax
  4013b9:	0f b6 08             	movzbl (%rax),%ecx
  4013bc:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4013c0:	0f b6 c0             	movzbl %al,%eax
  4013c3:	31 c8                	xor    %ecx,%eax
  4013c5:	89 c1                	mov    %eax,%ecx
  4013c7:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4013cb:	0f b6 c0             	movzbl %al,%eax
  4013ce:	31 c8                	xor    %ecx,%eax
  4013d0:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4013d3:	48 63 d2             	movslq %edx,%rdx
  4013d6:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4013da:	48 01 ca             	add    %rcx,%rdx
  4013dd:	88 02                	mov    %al,(%rdx)
  4013df:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4013e3:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4013e6:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4013e9:	7c c1                	jl     4013ac <domesticn_curve_operations+0x2c>
  4013eb:	90                   	nop
  4013ec:	c9                   	leaveq
  4013ed:	c3                   	retq

00000000004013c0 <signature_generation_engine>:
  4013c0:	55                   	push   %rbp
  4013c1:	48 89 e5             	mov    %rsp,%rbp
  4013c4:	48 83 ec 40          	sub    $0x40,%rsp
  4013c8:	48 89 7d d0          	mov    %rdi,-0x30(%rbp)
  4013cc:	89 75 cc             	mov    %esi,-0x34(%rbp)
  4013cf:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4013d6:	ff
  4013d7:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4013de:	be
  4013df:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4013e6:	ef
  4013e7:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  4013ee:	fe
  4013ef:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4013f3:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4013f7:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4013fb:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4013ff:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  401403:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401407:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  40140b:	c9                   	leaveq
  40140c:	c3                   	retq

Disassembly of section .data:

0000000000602000 <curve_parameter_table>:
  602000:	ff ff ff ff ff ff ff 	(bad)
  602007:	ff ff ff ff ff ff ff 	(bad)
  60200e:	ff 00                	incl   (%rax)
  602010:	00 00                	add    %al,(%rax)
  602012:	00 00                	add    %al,(%rax)
  602014:	00 00                	add    %al,(%rax)
  602016:	00 01                	add    %al,(%rcx)
  602018:	ac                   	lods   %ds:(%rsi),%al
  602019:	ed                   	in     (%dx),%eax
  60201a:	ba be de ad          	mov    $0xaddebeee,%edx
  60201f:	be ef 5a 82 79       	mov    $0x79825aef,%esi
  602024:	64 3d 1c f5 e4 00    	fs cmp $0xe4f51c,%eax