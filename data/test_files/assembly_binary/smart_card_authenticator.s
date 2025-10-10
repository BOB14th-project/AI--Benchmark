smart_card_authenticator:     file format elf64-x86-64

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
  401028:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  40102c:	48 8d 75 f8          	k_cipher_4    -0x8(%rbp),%rsi
  401030:	e8 2b 00 00 00       	callq  401060 <transform_key_schedule>
  401035:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401039:	48 8d 75 d0          	k_cipher_4    -0x30(%rbp),%rsi
  40103d:	e8 9e 00 00 00       	callq  4010e0 <transform_encrypt_block>
  401042:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401046:	be 10 00 00 00       	mov    $0x10,%esi
  40104b:	e8 20 01 00 00       	callq  401170 <card_challenge_response>
  401050:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401055:	bf 00 00 00 00       	mov    $0x0,%edi
  40105a:	0f 05                	syscall

0000000000401060 <transform_key_schedule>:
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
  40109a:	eb 37                	jmp    4010d3 <transform_key_schedule+0x73>
  40109c:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40109f:	c1 c0 08             	rol    $0x8,%eax
  4010a2:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010a5:	8b 45 e8             	mov    -0x18(%rbp),%eax
  4010a8:	c1 c0 10             	rol    $0x10,%eax
  4010ab:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4010ae:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4010b1:	c1 c0 18             	rol    $0x18,%eax
  4010b4:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  4010b7:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4010ba:	48 98                	cltq
  4010bc:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4010c0:	48 c1 e0 04          	shl    $0x4,%rax
  4010c4:	48 01 d0             	add    %rdx,%rax
  4010c7:	8b 55 ec             	mov    -0x14(%rbp),%edx
  4010ca:	89 10                	mov    %edx,(%rax)
  4010cc:	8b 55 e8             	mov    -0x18(%rbp),%edx
  4010cf:	89 50 04             	mov    %edx,0x4(%rax)
  4010d2:	8b 55 e4             	mov    -0x1c(%rbp),%edx
  4010d5:	89 50 08             	mov    %edx,0x8(%rax)
  4010d8:	8b 55 e0             	mov    -0x20(%rbp),%edx
  4010db:	89 50 0c             	mov    %edx,0xc(%rax)
  4010de:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  4010e2:	83 7d dc 0c          	cmpl   $0xc,-0x24(%rbp)
  4010e6:	7e b4                	jle    40109c <transform_key_schedule+0x3c>
  4010e8:	90                   	nop
  4010e9:	5d                   	pop    %rbp
  4010ea:	c3                   	retq

00000000004010e0 <transform_encrypt_block>:
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
  40111a:	eb 42                	jmp    40115e <transform_encrypt_block+0x7e>
  40111c:	8b 45 dc             	mov    -0x24(%rbp),%eax
  40111f:	48 98                	cltq
  401121:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  401125:	48 c1 e0 04          	shl    $0x4,%rax
  401129:	48 01 d0             	add    %rdx,%rax
  40112c:	8b 00                	mov    (%rax),%eax
  40112e:	31 45 ec             	xor    %eax,-0x14(%rbp)
  401131:	8b 00                	mov    (%rax),%eax
  401133:	31 45 e8             	xor    %eax,-0x18(%rbp)
  401136:	8b 00                	mov    (%rax),%eax
  401138:	31 45 e4             	xor    %eax,-0x1c(%rbp)
  40113b:	8b 00                	mov    (%rax),%eax
  40113d:	31 45 e0             	xor    %eax,-0x20(%rbp)
  401140:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401143:	25 ff 00 00 00       	and    $0xff,%eax
  401148:	89 c0                	mov    %eax,%eax
  40114a:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40114d:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401150:	c1 c0 08             	rol    $0x8,%eax
  401153:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401156:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401159:	c1 c0 10             	rol    $0x10,%eax
  40115c:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  40115f:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  401163:	83 7d dc 0b          	cmpl   $0xb,-0x24(%rbp)
  401167:	7e b3                	jle    40111c <transform_encrypt_block+0x3c>
  401169:	90                   	nop
  40116a:	5d                   	pop    %rbp
  40116b:	c3                   	retq

0000000000401170 <card_challenge_response>:
  401170:	55                   	push   %rbp
  401171:	48 89 e5             	mov    %rsp,%rbp
  401174:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401178:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40117b:	48 c7 45 f0 aa bb cc 	movq   $0xddeeffaabbccdd,-0x10(%rbp)
  401182:	dd
  401183:	48 c7 45 e8 ee ff aa 	movq   $0xbbccddeeffaabb,-0x18(%rbp)
  40118a:	bb
  40118b:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%rbp)
  401192:	eb 25                	jmp    4011b9 <card_challenge_response+0x49>
  401194:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401197:	48 98                	cltq
  401199:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40119d:	48 01 d0             	add    %rdx,%rax
  4011a0:	0f b6 00             	movzbl (%rax),%eax
  4011a3:	0f b6 c0             	movzbl %al,%eax
  4011a6:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  4011aa:	48 31 d0             	xor    %rdx,%rax
  4011ad:	89 45 e0             	mov    %eax,-0x20(%rbp)
  4011b0:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4011b3:	c1 c0 05             	rol    $0x5,%eax
  4011b6:	01 45 f0             	add    %eax,-0x10(%rbp)
  4011b9:	83 45 e4 01          	addl   $0x1,-0x1c(%rbp)
  4011bd:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4011c0:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011c3:	7c cf                	jl     401194 <card_challenge_response+0x24>
  4011c5:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4011c9:	5d                   	pop    %rbp
  4011ca:	c3                   	retq