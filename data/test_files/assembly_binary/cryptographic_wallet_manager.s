cryptographic_wallet_manager:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	48 83 ec 28          	sub    $0x28,%rsp
  401004:	48 c7 04 24 ff ff ff 	movq   $0xffffffffffffffff,(%rsp)
  40100b:	ff
  40100c:	48 c7 44 24 08 ff ff 	movq   $0xfffffffffffffffb,0x8(%rsp)
  401013:	ff fb
  401015:	48 c7 44 24 10 ff ff 	movq   $0xfffffffffffffffc,0x10(%rsp)
  40101c:	ff fc
  40101e:	48 c7 44 24 18 ff ff 	movq   $0xfffffffffffffffd,0x18(%rsp)
  401025:	ff fd
  401027:	e8 64 00 00 00       	callq  401090 <secp256k1_point_mul>
  40102c:	48 89 04 24          	mov    %rax,(%rsp)
  401030:	48 89 54 24 08       	mov    %rdx,0x8(%rsp)
  401035:	48 8d 3c 24          	lea    (%rsp),%rdi
  401039:	be 20 00 00 00       	mov    $0x20,%esi
  40103e:	e8 7d 01 00 00       	callq  4011c0 <curve_sig_sign>
  401043:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
  401048:	48 89 54 24 18       	mov    %rdx,0x18(%rsp)
  40104d:	48 8d 7c 24 10       	lea    0x10(%rsp),%rdi
  401052:	48 8d 34 24          	lea    (%rsp),%rsi
  401056:	e8 a5 02 00 00       	callq  401300 <digest_alg256_hash>
  40105b:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401060:	bf 00 00 00 00       	mov    $0x0,%edi
  401065:	0f 05                	syscall

0000000000401090 <secp256k1_point_mul>:
  401090:	55                   	push   %rbp
  401091:	48 89 e5             	mov    %rsp,%rbp
  401094:	48 83 ec 40          	sub    $0x40,%rsp
  401098:	48 c7 45 f8 6b 17 d1 	movq   $0x96d8986b17d1f2,%rax
  40109f:	f2
  4010a0:	48 89 45 f8          	mov    %rax,-0x8(%rbp)
  4010a4:	48 c7 45 f0 e1 2c 42 	movq   $0xf263a440e12c42,%rax
  4010ab:	47
  4010ac:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  4010b0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010b4:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  4010b8:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  4010bc:	48 89 55 e0          	mov    %rdx,-0x20(%rbp)
  4010c0:	c7 45 dc 00 00 00 00 	movl   $0x0,-0x24(%rbp)
  4010c7:	eb 45                	jmp    40110e <secp256k1_point_mul+0x7e>
  4010c9:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4010cc:	83 e0 01             	and    $0x1,%eax
  4010cf:	85 c0                	test   %eax,%eax
  4010d1:	74 1e                	je     4010f1 <secp256k1_point_mul+0x61>
  4010d3:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4010d7:	48 03 45 f8          	add    -0x8(%rbp),%rax
  4010db:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  4010df:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4010e3:	48 03 45 f0          	add    -0x10(%rbp),%rax
  4010e7:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4010eb:	e8 30 00 00 00       	callq  401120 <point_double>
  4010f0:	90                   	nop
  4010f1:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010f5:	48 d1 e0             	shl    %rax
  4010f8:	48 89 45 f8          	mov    %rax,-0x8(%rbp)
  4010fc:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401100:	48 d1 e0             	shl    %rax
  401103:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  401107:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  40110b:	eb 01                	jmp    40110e <secp256k1_point_mul+0x7e>
  40110d:	90                   	nop
  40110e:	83 7d dc ff          	cmpl   $0xff,-0x24(%rbp)
  401112:	7e b5                	jle    4010c9 <secp256k1_point_mul+0x39>
  401114:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401118:	48 8b 55 e0          	mov    -0x20(%rbp),%rdx
  40111c:	c9                   	leaveq
  40111d:	c3                   	retq

0000000000401120 <point_double>:
  401120:	55                   	push   %rbp
  401121:	48 89 e5             	mov    %rsp,%rbp
  401124:	48 83 ec 20          	sub    $0x20,%rsp
  401128:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40112c:	48 0f af c0          	imul   %rax,%rax
  401130:	48 6b c0 03          	imul   $0x3,%rax
  401134:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  401138:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40113c:	48 d1 e0             	shl    %rax
  40113f:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401143:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401147:	48 0f af c0          	imul   %rax,%rax
  40114b:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40114f:	48 d1 e2             	shl    %rdx
  401152:	48 29 d0             	sub    %rdx,%rax
  401155:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401159:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  40115d:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401161:	48 2b 55 e0          	sub    -0x20(%rbp),%rdx
  401165:	48 0f af c2          	imul   %rdx,%rax
  401169:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  40116d:	48 29 d0             	sub    %rdx,%rax
  401170:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401174:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401178:	48 89 45 f8          	mov    %rax,-0x8(%rbp)
  40117c:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401180:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401184:	90                   	nop
  401185:	c9                   	leaveq
  401186:	c3                   	retq

00000000004011c0 <curve_sig_sign>:
  4011c0:	55                   	push   %rbp
  4011c1:	48 89 e5             	mov    %rsp,%rbp
  4011c4:	48 83 ec 50          	sub    $0x50,%rsp
  4011c8:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011cc:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4011cf:	48 c7 45 f0 01 23 45 	movq   $0x6789abcdef234501,-0x10(%rbp)
  4011d6:	67
  4011d7:	48 c7 45 e8 89 ab cd 	movq   $0xfedcba9876543210,-0x18(%rbp)
  4011de:	ef
  4011df:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4011e3:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4011e7:	e8 a4 fe ff ff       	callq  401090 <secp256k1_point_mul>
  4011ec:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4011f0:	48 89 55 d0          	mov    %rdx,-0x30(%rbp)
  4011f4:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4011f8:	48 ba ff ff ff ff ff 	movabs $0xfffffffffffffffb,%rdx
  4011ff:	ff ff ff
  401202:	48 f7 ea             	imul   %rdx
  401205:	48 89 45 c8          	mov    %rax,-0x38(%rbp)
  401209:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40120d:	48 89 c7             	mov    %rax,%rdi
  401210:	e8 eb 00 00 00       	callq  401300 <digest_alg256_hash>
  401215:	48 89 45 c0          	mov    %rax,-0x40(%rbp)
  401219:	48 8b 45 c0          	mov    -0x40(%rbp),%rax
  40121d:	48 03 45 c8          	add    -0x38(%rbp),%rax
  401221:	48 03 45 e8          	add    -0x18(%rbp),%rax
  401225:	48 0f af 45 e0       	imul   -0x20(%rbp),%rax
  40122a:	48 89 45 b8          	mov    %rax,-0x48(%rbp)
  40122e:	48 8b 45 c8          	mov    -0x38(%rbp),%rax
  401232:	48 8b 55 b8          	mov    -0x48(%rbp),%rdx
  401236:	c9                   	leaveq
  401237:	c3                   	retq

0000000000401300 <digest_alg256_hash>:
  401300:	55                   	push   %rbp
  401301:	48 89 e5             	mov    %rsp,%rbp
  401304:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401308:	48 c7 45 f0 67 45 23 	movq   $0x1032547698badcfe,-0x10(%rbp)
  40130f:	01
  401310:	48 c7 45 e8 ef cd ab 	movq   $0x67452301efcdab89,-0x18(%rbp)
  401317:	89
  401318:	48 c7 45 e0 98 ba dc 	movq   $0x543210fe98badcfe,-0x20(%rbp)
  40131f:	fe
  401320:	48 c7 45 d8 10 32 54 	movq   $0x76543210,-0x28(%rbp)
  401327:	76
  401328:	48 c7 45 d0 c3 d2 e1 	movq   $0xf0e1d2c3,-0x30(%rbp)
  40132f:	f0
  401330:	48 c7 45 c8 5b e0 cd 	movq   $0x195be0cd19137e21,-0x38(%rbp)
  401337:	19
  401338:	48 c7 45 c0 13 7e 21 	movq   $0x19137e21,-0x40(%rbp)
  40133f:	19
  401340:	48 c7 45 b8 1f 83 d9 	movq   $0xabfb41bd1f83d9ab,-0x48(%rbp)
  401347:	ab
  401348:	c7 45 b4 00 00 00 00 	movl   $0x0,-0x4c(%rbp)
  40134f:	eb 75                	jmp    4013c6 <digest_alg256_hash+0xc6>
  401351:	8b 45 b4             	mov    -0x4c(%rbp),%eax
  401354:	83 e0 3f             	and    $0x3f,%eax
  401357:	48 98                	cltq
  401359:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40135d:	48 01 d0             	add    %rdx,%rax
  401360:	0f b6 00             	movzbl (%rax),%eax
  401363:	0f b6 c0             	movzbl %al,%eax
  401366:	89 45 b0             	mov    %eax,-0x50(%rbp)
  401369:	8b 45 b0             	mov    -0x50(%rbp),%eax
  40136c:	c1 c0 05             	rol    $0x5,%eax
  40136f:	01 45 f0             	add    %eax,-0x10(%rbp)
  401372:	8b 45 b0             	mov    -0x50(%rbp),%eax
  401375:	c1 c0 0a             	rol    $0xa,%eax
  401378:	01 45 e8             	add    %eax,-0x18(%rbp)
  40137b:	8b 45 b0             	mov    -0x50(%rbp),%eax
  40137e:	c1 c0 0f             	rol    $0xf,%eax
  401381:	01 45 e0             	add    %eax,-0x20(%rbp)
  401384:	8b 45 b0             	mov    -0x50(%rbp),%eax
  401387:	c1 c0 14             	rol    $0x14,%eax
  40138a:	01 45 d8             	add    %eax,-0x28(%rbp)
  40138d:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401390:	23 45 e8             	and    -0x18(%rbp),%eax
  401393:	8b 55 f0             	mov    -0x10(%rbp),%edx
  401396:	f7 d2                	not    %edx
  401398:	23 55 e0             	and    -0x20(%rbp),%edx
  40139b:	09 d0                	or     %edx,%eax
  40139d:	01 45 d0             	add    %eax,-0x30(%rbp)
  4013a0:	8b 45 e8             	mov    -0x18(%rbp),%eax
  4013a3:	89 45 ac             	mov    %eax,-0x54(%rbp)
  4013a6:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4013a9:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4013ac:	8b 45 d0             	mov    -0x30(%rbp),%eax
  4013af:	89 45 f0             	mov    %eax,-0x10(%rbp)
  4013b2:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4013b5:	89 45 d0             	mov    %eax,-0x30(%rbp)
  4013b8:	8b 45 d8             	mov    -0x28(%rbp),%eax
  4013bb:	89 45 e0             	mov    %eax,-0x20(%rbp)
  4013be:	8b 45 ac             	mov    -0x54(%rbp),%eax
  4013c1:	89 45 d8             	mov    %eax,-0x28(%rbp)
  4013c4:	eb 00                	jmp    4013c6 <digest_alg256_hash+0xc6>
  4013c6:	83 7d b4 3f          	cmpl   $0x3f,-0x4c(%rbp)
  4013ca:	7e 85                	jle    401351 <digest_alg256_hash+0x51>
  4013cc:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4013d0:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  4013d4:	48 09 d0             	or     %rdx,%rax
  4013d7:	48 8b 55 e0          	mov    -0x20(%rbp),%rdx
  4013db:	48 09 d0             	or     %rdx,%rax
  4013de:	48 8b 55 d8          	mov    -0x28(%rbp),%rdx
  4013e2:	48 09 d0             	or     %rdx,%rax
  4013e5:	c9                   	leaveq
  4013e6:	c3                   	retq