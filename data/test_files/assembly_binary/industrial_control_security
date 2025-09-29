industrial_control_security:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	48 c7 45 f8 01 23 45 	movq   $0x6789abcdef234501,-0x8(%rbp)
  40100f:	67
  401010:	48 c7 45 f0 89 ab cd 	movq   $0xfedcba9876543210,-0x10(%rbp)
  401017:	ef
  401018:	48 c7 45 e8 fe dc ba 	movq   $0x98765432fedcba98,-0x18(%rbp)
  40101f:	98
  401020:	48 c7 45 e0 76 54 32 	movq   $0x1032547698765432,-0x20(%rbp)
  401027:	10
  401028:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  40102c:	48 8d 75 f8          	lea    -0x8(%rbp),%rsi
  401030:	e8 2b 00 00 00       	callq  401060 <lea_key_schedule>
  401035:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401039:	48 8d 75 d0          	lea    -0x30(%rbp),%rsi
  40103d:	e8 9e 00 00 00       	callq  4010e0 <lea_encrypt_block>
  401042:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401046:	be 10 00 00 00       	mov    $0x10,%esi
  40104b:	e8 20 01 00 00       	callq  401170 <scada_protocol_auth>
  401050:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401055:	bf 00 00 00 00       	mov    $0x0,%edi
  40105a:	0f 05                	syscall

0000000000401060 <lea_key_schedule>:
  401060:	55                   	push   %rbp
  401061:	48 89 e5             	mov    %rsp,%rbp
  401064:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401068:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  40106c:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401070:	8b 00                	mov    (%rax),%eax
  401072:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401075:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401079:	8b 40 04             	mov    0x4(%rax),%eax
  40107c:	89 45 e8             	mov    %eax,-0x18(%rbp)
  40107f:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401083:	8b 40 08             	mov    0x8(%rax),%eax
  401086:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  401089:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  40108d:	8b 40 0c             	mov    0xc(%rax),%eax
  401090:	89 45 e0             	mov    %eax,-0x20(%rbp)
  401093:	c7 45 dc 00 00 00 00 	movl   $0x0,-0x24(%rbp)
  40109a:	eb 37                	jmp    4010d3 <lea_key_schedule+0x73>
  40109c:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40109f:	c1 c0 01             	rol    $0x1,%eax
  4010a2:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010a5:	8b 45 e8             	mov    -0x18(%rbp),%eax
  4010a8:	c1 c0 03             	rol    $0x3,%eax
  4010ab:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4010ae:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4010b1:	c1 c0 06             	rol    $0x6,%eax
  4010b4:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  4010b7:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4010ba:	c1 c0 0b             	rol    $0xb,%eax
  4010bd:	89 45 e0             	mov    %eax,-0x20(%rbp)
  4010c0:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4010c3:	48 98                	cltq
  4010c5:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4010c9:	48 c1 e0 04          	shl    $0x4,%rax
  4010cd:	48 01 d0             	add    %rdx,%rax
  4010d0:	8b 55 ec             	mov    -0x14(%rbp),%edx
  4010d3:	89 10                	mov    %edx,(%rax)
  4010d5:	8b 55 e8             	mov    -0x18(%rbp),%edx
  4010d8:	89 50 04             	mov    %edx,0x4(%rax)
  4010db:	8b 55 e4             	mov    -0x1c(%rbp),%edx
  4010de:	89 50 08             	mov    %edx,0x8(%rax)
  4010e1:	8b 55 e0             	mov    -0x20(%rbp),%edx
  4010e4:	89 50 0c             	mov    %edx,0xc(%rax)
  4010e7:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  4010eb:	83 7d dc 17          	cmpl   $0x17,-0x24(%rbp)
  4010ef:	7e ab                	jle    40109c <lea_key_schedule+0x3c>
  4010f1:	90                   	nop
  4010f2:	5d                   	pop    %rbp
  4010f3:	c3                   	retq

00000000004010e0 <lea_encrypt_block>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4010e8:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  4010ec:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010f0:	8b 00                	mov    (%rax),%eax
  4010f2:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010f5:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010f9:	8b 40 04             	mov    0x4(%rax),%eax
  4010fc:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4010ff:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401103:	8b 40 08             	mov    0x8(%rax),%eax
  401106:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  401109:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40110d:	8b 40 0c             	mov    0xc(%rax),%eax
  401110:	89 45 e0             	mov    %eax,-0x20(%rbp)
  401113:	c7 45 dc 00 00 00 00 	movl   $0x0,-0x24(%rbp)
  40111a:	eb 42                	jmp    40115e <lea_encrypt_block+0x7e>
  40111c:	8b 45 dc             	mov    -0x24(%rbp),%eax
  40111f:	48 98                	cltq
  401121:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  401125:	48 c1 e0 04          	shl    $0x4,%rax
  401129:	48 01 d0             	add    %rdx,%rax
  40112c:	8b 00                	mov    (%rax),%eax
  40112e:	01 45 ec             	add    %eax,-0x14(%rbp)
  401131:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401134:	c1 c0 09             	rol    $0x9,%eax
  401137:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40113a:	8b 45 e8             	mov    -0x18(%rbp),%eax
  40113d:	33 45 ec             	xor    -0x14(%rbp),%eax
  401140:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401143:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401146:	03 45 e8             	add    -0x18(%rbp),%eax
  401149:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  40114c:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  40114f:	c1 c0 05             	rol    $0x5,%eax
  401152:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  401155:	8b 45 e0             	mov    -0x20(%rbp),%eax
  401158:	33 45 e4             	xor    -0x1c(%rbp),%eax
  40115b:	89 45 e0             	mov    %eax,-0x20(%rbp)
  40115e:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  401162:	83 7d dc 17          	cmpl   $0x17,-0x24(%rbp)
  401166:	7e b4                	jle    40111c <lea_encrypt_block+0x3c>
  401168:	90                   	nop
  401169:	5d                   	pop    %rbp
  40116a:	c3                   	retq

0000000000401170 <scada_protocol_auth>:
  401170:	55                   	push   %rbp
  401171:	48 89 e5             	mov    %rsp,%rbp
  401174:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401178:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40117b:	48 c7 45 f0 5a 5a 5a 	movq   $0x5a5a5a5a5a5a5a5a,-0x10(%rbp)
  401182:	5a
  401183:	48 c7 45 e8 a5 a5 a5 	movq   $0xa5a5a5a5a5a5a5a5,-0x18(%rbp)
  40118a:	a5
  40118b:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%rbp)
  401192:	eb 3a                	jmp    4011ce <scada_protocol_auth+0x5e>
  401194:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401197:	48 98                	cltq
  401199:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40119d:	48 01 d0             	add    %rdx,%rax
  4011a0:	0f b6 00             	movzbl (%rax),%eax
  4011a3:	0f b6 c0             	movzbl %al,%eax
  4011a6:	89 45 e0             	mov    %eax,-0x20(%rbp)
  4011a9:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4011ac:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  4011b0:	48 31 d0             	xor    %rdx,%rax
  4011b3:	89 45 dc             	mov    %eax,-0x24(%rbp)
  4011b6:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4011b9:	c1 c0 07             	rol    $0x7,%eax
  4011bc:	89 45 dc             	mov    %eax,-0x24(%rbp)
  4011bf:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4011c2:	48 8b 55 e8          	mov    -0x18(%rbp),%rdx
  4011c6:	48 31 d0             	xor    %rdx,%rax
  4011c9:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  4011cd:	83 45 e4 01          	addl   $0x1,-0x1c(%rbp)
  4011d1:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4011d4:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011d7:	7c bb                	jl     401194 <scada_protocol_auth+0x24>
  4011d9:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4011dd:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4011e1:	89 45 d8             	mov    %eax,-0x28(%rbp)
  4011e4:	8b 45 d8             	mov    -0x28(%rbp),%eax
  4011e7:	5d                   	pop    %rbp
  4011e8:	c3                   	retq