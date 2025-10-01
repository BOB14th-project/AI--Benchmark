vpn_tunnel_encryption_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 70          	sub    $0x70,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ff ff ff 	movq   $0x1fffffffffffff,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 ac ed ba 	movq   $0xbebaedac,-0x18(%rbp)
  40101f:	be
  401020:	48 c7 45 e0 de ad be 	movq   $0xefbeadde,-0x20(%rbp)
  401027:	ef
  401028:	e8 c3 01 00 00       	callq  4011f0 <tunnel_key_exchange>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	lea    -0x40(%rbp),%rsi
  401039:	ba 20 00 00 00       	mov    $0x20,%edx
  40103e:	e8 dd 01 00 00       	callq  401220 <packet_encryption_layer>
  401043:	48 8d 7d b0          	lea    -0x50(%rbp),%rdi
  401047:	48 8d 75 a0          	lea    -0x60(%rbp),%rsi
  40104b:	ba 10 00 00 00       	mov    $0x10,%edx
  401050:	e8 0b 02 00 00       	callq  401260 <korean_vpn_cipher>
  401055:	48 8d 7d 90          	lea    -0x70(%rbp),%rdi
  401059:	be 30 00 00 00       	mov    $0x30,%esi
  40105e:	e8 3d 02 00 00       	callq  4012a0 <tunnel_authentication>
  401063:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401068:	bf 00 00 00 00       	mov    $0x0,%edi
  40106d:	0f 05                	syscall

00000000004011f0 <tunnel_key_exchange>:
  4011f0:	55                   	push   %rbp
  4011f1:	48 89 e5             	mov    %rsp,%rbp
  4011f4:	48 83 ec 40          	sub    $0x40,%rsp
  4011f8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4011ff:	ff
  401200:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401207:	be
  401208:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  40120f:	ef
  401210:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  401217:	fe
  401218:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40121c:	48 f7 65 f0          	mulq   -0x10(%rbp)
  401220:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  401224:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401228:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  40122c:	c9                   	leaveq
  40122d:	c3                   	retq

0000000000401220 <packet_encryption_layer>:
  401220:	55                   	push   %rbp
  401221:	48 89 e5             	mov    %rsp,%rbp
  401224:	48 83 ec 30          	sub    $0x30,%rsp
  401228:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40122c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401230:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401233:	48 c7 45 f8 63 7c 77 	movq   $0x7b777c63,-0x8(%rbp)
  40123a:	7b
  40123b:	48 c7 45 f0 f2 6b 6f 	movq   $0xc56f6bf2,-0x10(%rbp)
  401242:	c5
  401243:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40124a:	eb 2a                	jmp    401276 <packet_encryption_layer+0x56>
  40124c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40124f:	48 63 d0             	movslq %eax,%rdx
  401252:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401256:	48 01 d0             	add    %rdx,%rax
  401259:	0f b6 08             	movzbl (%rax),%ecx
  40125c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401260:	0f b6 c0             	movzbl %al,%eax
  401263:	31 c8                	xor    %ecx,%eax
  401265:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401268:	48 63 d2             	movslq %edx,%rdx
  40126b:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40126f:	48 01 ca             	add    %rcx,%rdx
  401272:	88 02                	mov    %al,(%rdx)
  401274:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401278:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40127b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40127e:	7c cc                	jl     40124c <packet_encryption_layer+0x2c>
  401280:	90                   	nop
  401281:	c9                   	leaveq
  401282:	c3                   	retq

0000000000401260 <korean_vpn_cipher>:
  401260:	55                   	push   %rbp
  401261:	48 89 e5             	mov    %rsp,%rbp
  401264:	48 83 ec 30          	sub    $0x30,%rsp
  401268:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40126c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401270:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401273:	c7 45 fc 9e 37 79 c4 	movl   $0xc479379e,-0x4(%rbp)
  40127a:	c7 45 f8 b9 a6 8c 4e 	movl   $0x4e8ca6b9,-0x8(%rbp)
  401281:	c7 45 f4 01 23 45 67 	movl   $0x67452301,-0xc(%rbp)
  401288:	c7 45 f0 89 ab cd ef 	movl   $0xefcdab89,-0x10(%rbp)
  40128f:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  401296:	eb 38                	jmp    4012d0 <korean_vpn_cipher+0x70>
  401298:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40129b:	48 63 d0             	movslq %eax,%rdx
  40129e:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4012a2:	48 01 d0             	add    %rdx,%rax
  4012a5:	0f b6 08             	movzbl (%rax),%ecx
  4012a8:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012ab:	0f b6 c0             	movzbl %al,%eax
  4012ae:	31 c8                	xor    %ecx,%eax
  4012b0:	89 c1                	mov    %eax,%ecx
  4012b2:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4012b5:	0f b6 c0             	movzbl %al,%eax
  4012b8:	31 c8                	xor    %ecx,%eax
  4012ba:	8b 55 ec             	mov    -0x14(%rbp),%edx
  4012bd:	48 63 d2             	movslq %edx,%rdx
  4012c0:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4012c4:	48 01 ca             	add    %rcx,%rdx
  4012c7:	88 02                	mov    %al,(%rdx)
  4012c9:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012cc:	c1 c0 04             	rol    $0x4,%eax
  4012cf:	89 45 fc             	mov    %eax,-0x4(%rbp)
  4012d2:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  4012d6:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4012d9:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012dc:	7c ba                	jl     401298 <korean_vpn_cipher+0x38>
  4012de:	90                   	nop
  4012df:	c9                   	leaveq
  4012e0:	c3                   	retq

00000000004012a0 <tunnel_authentication>:
  4012a0:	55                   	push   %rbp
  4012a1:	48 89 e5             	mov    %rsp,%rbp
  4012a4:	48 83 ec 30          	sub    $0x30,%rsp
  4012a8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4012ac:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4012af:	48 c7 45 f8 5a 82 79 	movq   $0x6479825a,-0x8(%rbp)
  4012b6:	64
  4012b7:	48 c7 45 f0 3d 1c f5 	movq   $0xe4f51c3d,-0x10(%rbp)
  4012be:	e4
  4012bf:	48 c7 45 e8 8b 44 f7 	movq   $0x9af7448b,-0x18(%rbp)
  4012c6:	9a
  4012c7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4012ce:	eb 28                	jmp    4012f8 <tunnel_authentication+0x58>
  4012d0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012d3:	48 63 d0             	movslq %eax,%rdx
  4012d6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012da:	48 01 d0             	add    %rdx,%rax
  4012dd:	0f b6 00             	movzbl (%rax),%eax
  4012e0:	0f b6 c0             	movzbl %al,%eax
  4012e3:	01 45 f8             	add    %eax,-0x8(%rbp)
  4012e6:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4012e9:	c1 c0 09             	rol    $0x9,%eax
  4012ec:	89 45 f8             	mov    %eax,-0x8(%rbp)
  4012ef:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4012f2:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4012f5:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012f9:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012fc:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012ff:	7c cf                	jl     4012d0 <tunnel_authentication+0x30>
  401301:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401305:	c9                   	leaveq
  401306:	c3                   	retq