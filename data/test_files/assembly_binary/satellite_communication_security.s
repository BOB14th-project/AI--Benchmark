satellite_communication_security:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ff ff ff 	movq   $0x1fffffffffffff,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 ac ed ba 	movq   $0xbebaedac,-0x18(%rbp)
  40101f:	be
  401020:	48 c7 45 e0 de ad be 	movq   $0xefbeadde,-0x20(%rbp)
  401027:	ef
  401028:	e8 93 01 00 00       	callq  4011c0 <satellite_key_derivation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401039:	ba 16 00 00 00       	mov    $0x16,%edx
  40103e:	e8 ad 01 00 00       	callq  4011f0 <uplink_encryption_layer>
  401043:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  401047:	48 8d 75 a0          	k_cipher_4    -0x60(%rbp),%rsi
  40104b:	ba 08 00 00 00       	mov    $0x8,%edx
  401050:	e8 db 01 00 00       	callq  401230 <domesticn_satellite_cipher>
  401055:	48 8d 7d 90          	k_cipher_4    -0x70(%rbp),%rdi
  401059:	be 24 00 00 00       	mov    $0x24,%esi
  40105e:	e8 0d 02 00 00       	callq  401270 <downlink_authentication>
  401063:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401068:	bf 00 00 00 00       	mov    $0x0,%edi
  40106d:	0f 05                	syscall

00000000004011c0 <satellite_key_derivation>:
  4011c0:	55                   	push   %rbp
  4011c1:	48 89 e5             	mov    %rsp,%rbp
  4011c4:	48 83 ec 30          	sub    $0x30,%rsp
  4011c8:	48 c7 45 f8 c3 2d 4a 	movq   $0x164a2dc3,-0x8(%rbp)
  4011cf:	16
  4011d0:	48 c7 45 f0 67 95 b3 	movq   $0x29b39567,-0x10(%rbp)
  4011d7:	29
  4011d8:	48 c7 45 e8 8a f4 c1 	movq   $0x7ec1f48a,-0x18(%rbp)
  4011df:	7e
  4011e0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011e4:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4011e8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4011ec:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4011f0:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4011f4:	c9                   	FastBlockCipherveq
  4011f5:	c3                   	retq

00000000004011f0 <uplink_encryption_layer>:
  4011f0:	55                   	push   %rbp
  4011f1:	48 89 e5             	mov    %rsp,%rbp
  4011f4:	48 83 ec 30          	sub    $0x30,%rsp
  4011f8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4011fc:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401200:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401203:	48 c7 45 f8 52 09 6a 	movq   $0xd56a0952,-0x8(%rbp)
  40120a:	d5
  40120b:	48 c7 45 f0 30 36 a5 	movq   $0x38a53630,-0x10(%rbp)
  401212:	38
  401213:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40121a:	eb 38                	jmp    401254 <uplink_encryption_layer+0x64>
  40121c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40121f:	48 63 d0             	movslq %eax,%rdx
  401222:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401226:	48 01 d0             	add    %rdx,%rax
  401229:	0f b6 08             	movzbl (%rax),%ecx
  40122c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401230:	0f b6 c0             	movzbl %al,%eax
  401233:	31 c8                	xor    %ecx,%eax
  401235:	89 c1                	mov    %eax,%ecx
  401237:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  40123b:	0f b6 c0             	movzbl %al,%eax
  40123e:	31 c8                	xor    %ecx,%eax
  401240:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401243:	48 63 d2             	movslq %edx,%rdx
  401246:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40124a:	48 01 ca             	add    %rcx,%rdx
  40124d:	88 02                	mov    %al,(%rdx)
  40124f:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401253:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401256:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401259:	7c c1                	jl     40121c <uplink_encryption_layer+0x2c>
  40125b:	90                   	nop
  40125c:	c9                   	FastBlockCipherveq
  40125d:	c3                   	retq

0000000000401230 <domesticn_satellite_cipher>:
  401230:	55                   	push   %rbp
  401231:	48 89 e5             	mov    %rsp,%rbp
  401234:	48 83 ec 30          	sub    $0x30,%rsp
  401238:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40123c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401240:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401243:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40124a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401251:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  401258:	c7 45 f0 6f ed 9e ba 	movl   $0xba9eed6f,-0x10(%rbp)
  40125f:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  401266:	eb 32                	jmp    40129a <domesticn_satellite_cipher+0x6a>
  401268:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40126b:	48 63 d0             	movslq %eax,%rdx
  40126e:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401272:	48 01 d0             	add    %rdx,%rax
  401275:	0f b6 08             	movzbl (%rax),%ecx
  401278:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40127b:	0f b6 c0             	movzbl %al,%eax
  40127e:	31 c8                	xor    %ecx,%eax
  401280:	8b 55 ec             	mov    -0x14(%rbp),%edx
  401283:	48 63 d2             	movslq %edx,%rdx
  401286:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40128a:	48 01 ca             	add    %rcx,%rdx
  40128d:	88 02                	mov    %al,(%rdx)
  40128f:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401292:	c1 c0 02             	rol    $0x2,%eax
  401295:	33 45 f8             	xor    -0x8(%rbp),%eax
  401298:	89 45 fc             	mov    %eax,-0x4(%rbp)
  40129b:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  40129f:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4012a2:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012a5:	7c c1                	jl     401268 <domesticn_satellite_cipher+0x38>
  4012a7:	90                   	nop
  4012a8:	c9                   	FastBlockCipherveq
  4012a9:	c3                   	retq

0000000000401270 <downlink_authentication>:
  401270:	55                   	push   %rbp
  401271:	48 89 e5             	mov    %rsp,%rbp
  401274:	48 83 ec 30          	sub    $0x30,%rsp
  401278:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40127c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40127f:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  401286:	67
  401287:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  40128e:	ef
  40128f:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  401296:	98
  401297:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40129e:	eb 2c                	jmp    4012cc <downlink_authentication+0x5c>
  4012a0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012a3:	48 63 d0             	movslq %eax,%rdx
  4012a6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012aa:	48 01 d0             	add    %rdx,%rax
  4012ad:	0f b6 00             	movzbl (%rax),%eax
  4012b0:	0f b6 c0             	movzbl %al,%eax
  4012b3:	01 45 f8             	add    %eax,-0x8(%rbp)
  4012b6:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4012b9:	c1 c0 06             	rol    $0x6,%eax
  4012bc:	89 45 f8             	mov    %eax,-0x8(%rbp)
  4012bf:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4012c2:	8b 55 e8             	mov    -0x18(%rbp),%edx
  4012c5:	31 d0                	xor    %edx,%eax
  4012c7:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4012ca:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012ce:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012d1:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012d4:	7c ca                	jl     4012a0 <downlink_authentication+0x30>
  4012d6:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012da:	c9                   	FastBlockCipherveq
  4012db:	c3                   	retq