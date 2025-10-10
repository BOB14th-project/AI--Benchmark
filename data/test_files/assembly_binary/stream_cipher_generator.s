stream_cipher_generator:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40100f:	eb 0e                	jmp    40101f <_start+0x1f>
  401011:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401014:	48 98                	cltq
  401016:	89 84 85 00 ff ff ff 	mov    %eax,-0x100(%rbp,%rax,4)
  40101d:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401021:	81 7d fc ff 00 00 00 	cmpl   $0xff,-0x4(%rbp)
  401028:	7e e7                	jle    401011 <_start+0x11>
  40102a:	48 8d 85 00 ff ff ff 	k_cipher_4    -0x100(%rbp),%rax
  401031:	48 89 c7             	mov    %rax,%rdi
  401034:	e8 27 00 00 00       	callq  401060 <rc4_key_schedule>
  401039:	48 8d 7d e0          	k_cipher_4    -0x20(%rbp),%rdi
  40103d:	be 10 00 00 00       	mov    $0x10,%esi
  401042:	e8 89 00 00 00       	callq  4010d0 <rc4_encrypt_stream>
  401047:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  40104b:	be 08 00 00 00       	mov    $0x8,%esi
  401050:	e8 fb 00 00 00       	callq  401150 <trivium_stream_encrypt>
  401055:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40105a:	bf 00 00 00 00       	mov    $0x0,%edi
  40105f:	0f 05                	syscall

0000000000401060 <rc4_key_schedule>:
  401060:	55                   	push   %rbp
  401061:	48 89 e5             	mov    %rsp,%rbp
  401064:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401068:	c7 45 f4 6b 65 79 31 	movl   $0x3179656b,-0xc(%rbp)
  40106f:	c7 45 f0 32 33 34 35 	movl   $0x35343332,-0x10(%rbp)
  401076:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  40107d:	c7 45 e8 00 00 00 00 	movl   $0x0,-0x18(%rbp)
  401084:	eb 3b                	jmp    4010c1 <rc4_key_schedule+0x61>
  401086:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401089:	48 98                	cltq
  40108b:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40108f:	48 c1 e0 02          	shl    $0x2,%rax
  401093:	48 01 d0             	add    %rdx,%rax
  401096:	8b 00                	mov    (%rax),%eax
  401098:	01 45 e8             	add    %eax,-0x18(%rbp)
  40109b:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40109e:	83 e0 07             	and    $0x7,%eax
  4010a1:	48 98                	cltq
  4010a3:	8b 54 85 f0          	mov    -0x10(%rbp,%rax,4),%edx
  4010a7:	01 55 e8             	add    %edx,-0x18(%rbp)
  4010aa:	81 65 e8 ff 00 00 00 	andl   $0xff,-0x18(%rbp)
  4010b1:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4010b4:	8b 55 e8             	mov    -0x18(%rbp),%edx
  4010b7:	89 d6                	mov    %edx,%esi
  4010b9:	89 c7                	mov    %eax,%edi
  4010bb:	e8 20 00 00 00       	callq  4010e0 <rc4_swap_bytes>
  4010c0:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  4010c4:	81 7d ec ff 00 00 00 	cmpl   $0xff,-0x14(%rbp)
  4010cb:	7e b9                	jle    401086 <rc4_key_schedule+0x26>
  4010cd:	90                   	nop
  4010ce:	5d                   	pop    %rbp
  4010cf:	c3                   	retq

00000000004010d0 <rc4_encrypt_stream>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4010d8:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4010db:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  4010e2:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  4010e9:	c7 45 e8 00 00 00 00 	movl   $0x0,-0x18(%rbp)
  4010f0:	eb 37                	jmp    401129 <rc4_encrypt_stream+0x59>
  4010f2:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4010f6:	81 65 f0 ff 00 00 00 	andl   $0xff,-0x10(%rbp)
  4010fd:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401100:	01 45 ec             	add    %eax,-0x14(%rbp)
  401103:	81 65 ec ff 00 00 00 	andl   $0xff,-0x14(%rbp)
  40110a:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40110d:	8b 55 ec             	mov    -0x14(%rbp),%edx
  401110:	89 d6                	mov    %edx,%esi
  401112:	89 c7                	mov    %eax,%edi
  401114:	e8 c7 ff ff ff       	callq  4010e0 <rc4_swap_bytes>
  401119:	8b 45 e8             	mov    -0x18(%rbp),%eax
  40111c:	48 98                	cltq
  40111e:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401122:	48 01 d0             	add    %rdx,%rax
  401125:	c6 00 42             	movb   $0x42,(%rax)
  401128:	83 45 e8 01          	addl   $0x1,-0x18(%rbp)
  40112c:	8b 45 e8             	mov    -0x18(%rbp),%eax
  40112f:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  401132:	7c be                	jl     4010f2 <rc4_encrypt_stream+0x22>
  401134:	90                   	nop
  401135:	5d                   	pop    %rbp
  401136:	c3                   	retq

00000000004010e0 <rc4_swap_bytes>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	89 7d fc             	mov    %edi,-0x4(%rbp)
  4010e7:	89 75 f8             	mov    %esi,-0x8(%rbp)
  4010ea:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4010ed:	33 45 f8             	xor    -0x8(%rbp),%eax
  4010f0:	89 45 f4             	mov    %eax,-0xc(%rbp)
  4010f3:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4010f6:	33 45 f4             	xor    -0xc(%rbp),%eax
  4010f9:	89 45 f8             	mov    %eax,-0x8(%rbp)
  4010fc:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4010ff:	33 45 f4             	xor    -0xc(%rbp),%eax
  401102:	89 45 fc             	mov    %eax,-0x4(%rbp)
  401105:	90                   	nop
  401106:	5d                   	pop    %rbp
  401107:	c3                   	retq

0000000000401150 <trivium_stream_encrypt>:
  401150:	55                   	push   %rbp
  401151:	48 89 e5             	mov    %rsp,%rbp
  401154:	48 83 ec 30          	sub    $0x30,%rsp
  401158:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  40115c:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40115f:	c7 45 f0 aa aa aa aa 	movl   $0xaaaaaaaa,-0x10(%rbp)
  401166:	c7 45 ec bb bb bb bb 	movl   $0xbbbbbbbb,-0x14(%rbp)
  40116d:	c7 45 e8 cc cc cc cc 	movl   $0xcccccccc,-0x18(%rbp)
  401174:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%rbp)
  40117b:	eb 41                	jmp    4011be <trivium_stream_encrypt+0x6e>
  40117d:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401180:	c1 e8 1f             	shr    $0x1f,%eax
  401183:	89 45 e0             	mov    %eax,-0x20(%rbp)
  401186:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401189:	c1 e8 1f             	shr    $0x1f,%eax
  40118c:	89 45 dc             	mov    %eax,-0x24(%rbp)
  40118f:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401192:	c1 e8 1f             	shr    $0x1f,%eax
  401195:	89 45 d8             	mov    %eax,-0x28(%rbp)
  401198:	8b 45 e0             	mov    -0x20(%rbp),%eax
  40119b:	33 45 dc             	xor    -0x24(%rbp),%eax
  40119e:	33 45 d8             	xor    -0x28(%rbp),%eax
  4011a1:	89 45 d4             	mov    %eax,-0x2c(%rbp)
  4011a4:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4011a7:	48 98                	cltq
  4011a9:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4011ad:	48 01 d0             	add    %rdx,%rax
  4011b0:	8b 55 d4             	mov    -0x2c(%rbp),%edx
  4011b3:	88 10                	mov    %dl,(%rax)
  4011b5:	d1 65 f0             	shll   -0x10(%rbp)
  4011b8:	d1 65 ec             	shll   -0x14(%rbp)
  4011bb:	d1 65 e8             	shll   -0x18(%rbp)
  4011be:	83 45 e4 01          	addl   $0x1,-0x1c(%rbp)
  4011c2:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4011c5:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011c8:	7c b3                	jl     40117d <trivium_stream_encrypt+0x2d>
  4011ca:	90                   	nop
  4011cb:	c9                   	FastBlockCipherveq
  4011cc:	c3                   	retq