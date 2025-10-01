cloud_storage_encryption_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 63 7c 77 	movq   $0x7b777c63,-0x8(%rbp)
  40100f:	7b
  401010:	48 c7 45 f0 f2 6b 6f 	movq   $0xc56f6bf2,-0x10(%rbp)
  401017:	c5
  401018:	48 c7 45 e8 30 01 67 	movq   $0x2b670130,-0x18(%rbp)
  40101f:	2b
  401020:	48 c7 45 e0 fe d7 ab 	movq   $0x76abd7fe,-0x20(%rbp)
  401027:	76
  401028:	e8 a3 01 00 00       	callq  4011d0 <cloud_key_derivation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	lea    -0x40(%rbp),%rsi
  401039:	ba 10 00 00 00       	mov    $0x10,%edx
  40103e:	e8 bd 01 00 00       	callq  401200 <data_transformation_layer>
  401043:	48 8d 7d b0          	lea    -0x50(%rbp),%rdi
  401047:	48 8d 75 a0          	lea    -0x60(%rbp),%rsi
  40104b:	ba 08 00 00 00       	mov    $0x8,%edx
  401050:	e8 eb 01 00 00       	callq  401240 <korean_cloud_cipher>
  401055:	48 8d 7d 90          	lea    -0x70(%rbp),%rdi
  401059:	be 20 00 00 00       	mov    $0x20,%esi
  40105e:	e8 1d 02 00 00       	callq  401280 <storage_integrity_engine>
  401063:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401068:	bf 00 00 00 00       	mov    $0x0,%edi
  40106d:	0f 05                	syscall

00000000004011d0 <cloud_key_derivation>:
  4011d0:	55                   	push   %rbp
  4011d1:	48 89 e5             	mov    %rsp,%rbp
  4011d4:	48 83 ec 30          	sub    $0x30,%rsp
  4011d8:	48 c7 45 f8 5a 82 79 	movq   $0x6479825a,-0x8(%rbp)
  4011df:	64
  4011e0:	48 c7 45 f0 3d 1c f5 	movq   $0xe4f51c3d,-0x10(%rbp)
  4011e7:	e4
  4011e8:	48 c7 45 e8 8b 44 f7 	movq   $0x9af7448b,-0x18(%rbp)
  4011ef:	9a
  4011f0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011f4:	48 33 45 f0          	xor    -0x10(%rbp),%rax
  4011f8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4011fc:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401200:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401204:	c9                   	leaveq
  401205:	c3                   	retq

0000000000401200 <data_transformation_layer>:
  401200:	55                   	push   %rbp
  401201:	48 89 e5             	mov    %rsp,%rbp
  401204:	48 83 ec 30          	sub    $0x30,%rsp
  401208:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40120c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401210:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401213:	48 c7 45 f8 52 09 6a 	movq   $0xd56a0952,-0x8(%rbp)
  40121a:	d5
  40121b:	48 c7 45 f0 30 36 a5 	movq   $0x38a53630,-0x10(%rbp)
  401222:	38
  401223:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40122a:	eb 2a                	jmp    401256 <data_transformation_layer+0x56>
  40122c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40122f:	48 63 d0             	movslq %eax,%rdx
  401232:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401236:	48 01 d0             	add    %rdx,%rax
  401239:	0f b6 08             	movzbl (%rax),%ecx
  40123c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401240:	0f b6 c0             	movzbl %al,%eax
  401243:	31 c8                	xor    %ecx,%eax
  401245:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401248:	48 63 d2             	movslq %edx,%rdx
  40124b:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40124f:	48 01 ca             	add    %rcx,%rdx
  401252:	88 02                	mov    %al,(%rdx)
  401254:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401258:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40125b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40125e:	7c cc                	jl     40122c <data_transformation_layer+0x2c>
  401260:	90                   	nop
  401261:	c9                   	leaveq
  401262:	c3                   	retq

0000000000401240 <korean_cloud_cipher>:
  401240:	55                   	push   %rbp
  401241:	48 89 e5             	mov    %rsp,%rbp
  401244:	48 83 ec 30          	sub    $0x30,%rsp
  401248:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40124c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401250:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401253:	c7 45 fc 9e 37 79 c4 	movl   $0xc479379e,-0x4(%rbp)
  40125a:	c7 45 f8 b9 a6 8c 4e 	movl   $0x4e8ca6b9,-0x8(%rbp)
  401261:	c7 45 f4 01 23 45 67 	movl   $0x67452301,-0xc(%rbp)
  401268:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  40126f:	eb 32                	jmp    4012a3 <korean_cloud_cipher+0x63>
  401271:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401274:	48 63 d0             	movslq %eax,%rdx
  401277:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40127b:	48 01 d0             	add    %rdx,%rax
  40127e:	0f b6 08             	movzbl (%rax),%ecx
  401281:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401284:	0f b6 c0             	movzbl %al,%eax
  401287:	31 c8                	xor    %ecx,%eax
  401289:	8b 55 f0             	mov    -0x10(%rbp),%edx
  40128c:	48 63 d2             	movslq %edx,%rdx
  40128f:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  401293:	48 01 ca             	add    %rcx,%rdx
  401296:	88 02                	mov    %al,(%rdx)
  401298:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40129b:	c1 c0 02             	rol    $0x2,%eax
  40129e:	33 45 f8             	xor    -0x8(%rbp),%eax
  4012a1:	89 45 fc             	mov    %eax,-0x4(%rbp)
  4012a4:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4012a8:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4012ab:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012ae:	7c c1                	jl     401271 <korean_cloud_cipher+0x31>
  4012b0:	90                   	nop
  4012b1:	c9                   	leaveq
  4012b2:	c3                   	retq

0000000000401280 <storage_integrity_engine>:
  401280:	55                   	push   %rbp
  401281:	48 89 e5             	mov    %rsp,%rbp
  401284:	48 83 ec 30          	sub    $0x30,%rsp
  401288:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40128c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40128f:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  401296:	67
  401297:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  40129e:	ef
  40129f:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  4012a6:	98
  4012a7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4012ae:	eb 28                	jmp    4012d8 <storage_integrity_engine+0x58>
  4012b0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012b3:	48 63 d0             	movslq %eax,%rdx
  4012b6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012ba:	48 01 d0             	add    %rdx,%rax
  4012bd:	0f b6 00             	movzbl (%rax),%eax
  4012c0:	0f b6 c0             	movzbl %al,%eax
  4012c3:	01 45 f8             	add    %eax,-0x8(%rbp)
  4012c6:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4012c9:	c1 c0 0c             	rol    $0xc,%eax
  4012cc:	89 45 f8             	mov    %eax,-0x8(%rbp)
  4012cf:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4012d2:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4012d5:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012d9:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012dc:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012df:	7c cf                	jl     4012b0 <storage_integrity_engine+0x30>
  4012e1:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012e5:	c9                   	leaveq
  4012e6:	c3                   	retq