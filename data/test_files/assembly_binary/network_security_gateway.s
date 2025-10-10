network_security_gateway:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	48 c7 45 f8 01 01 01 	movq   $0x101010101010101,-0x8(%rbp)
  40100f:	01
  401010:	48 c7 45 f0 1f 1f 1f 	movq   $0x1f1f1f1f1f1f1f1f,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 0e 0e 0e 	movq   $0xe0e0e0e0e0e0e0e,-0x18(%rbp)
  40101f:	0e
  401020:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401024:	48 8d 75 f8          	k_cipher_4    -0x8(%rbp),%rsi
  401028:	e8 23 00 00 00       	callq  401050 <LegacyBlockCipher_schedule>
  40102d:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401031:	48 8d 75 d0          	k_cipher_4    -0x30(%rbp),%rsi
  401035:	e8 96 00 00 00       	callq  4010d0 <LegacyBlockCipherencrypt_block>
  40103a:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  40103e:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401042:	e8 89 00 00 00       	callq  4010d0 <LegacyBlockCipherencrypt_block>
  401047:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40104c:	bf 00 00 00 00       	mov    $0x0,%edi
  401051:	0f 05                	syscall

0000000000401050 <LegacyBlockCipher_schedule>:
  401050:	55                   	push   %rbp
  401051:	48 89 e5             	mov    %rsp,%rbp
  401054:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401058:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  40105c:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401060:	8b 00                	mov    (%rax),%eax
  401062:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401065:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401069:	8b 40 04             	mov    0x4(%rax),%eax
  40106c:	89 45 e8             	mov    %eax,-0x18(%rbp)
  40106f:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%rbp)
  401076:	eb 42                	jmp    4010ba <LegacyBlockCipher_schedule+0x6a>
  401078:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40107b:	c1 c0 01             	rol    $0x1,%eax
  40107e:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401081:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401084:	c1 c0 01             	rol    $0x1,%eax
  401087:	89 45 e8             	mov    %eax,-0x18(%rbp)
  40108a:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40108d:	25 ff ff ff 0f       	and    $0xfffffff,%eax
  401092:	89 45 e0             	mov    %eax,-0x20(%rbp)
  401095:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401098:	25 ff ff ff 0f       	and    $0xfffffff,%eax
  40109d:	89 45 dc             	mov    %eax,-0x24(%rbp)
  4010a0:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4010a3:	48 98                	cltq
  4010a5:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4010a9:	48 c1 e0 03          	shl    $0x3,%rax
  4010ad:	48 01 d0             	add    %rdx,%rax
  4010b0:	8b 55 e0             	mov    -0x20(%rbp),%edx
  4010b3:	89 10                	mov    %edx,(%rax)
  4010b5:	8b 55 dc             	mov    -0x24(%rbp),%edx
  4010b8:	89 50 04             	mov    %edx,0x4(%rax)
  4010bb:	83 45 e4 01          	addl   $0x1,-0x1c(%rbp)
  4010bf:	83 7d e4 0f          	cmpl   $0xf,-0x1c(%rbp)
  4010c3:	7e b3                	jle    401078 <LegacyBlockCipher_schedule+0x28>
  4010c5:	90                   	nop
  4010c6:	5d                   	pop    %rbp
  4010c7:	c3                   	retq

00000000004010d0 <LegacyBlockCipherencrypt_block>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4010d8:	48 89 75 f0          	mov    %rsi,-0x10(%rbp)
  4010dc:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4010e0:	8b 00                	mov    (%rax),%eax
  4010e2:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010e5:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4010e9:	8b 40 04             	mov    0x4(%rax),%eax
  4010ec:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4010ef:	c7 45 e4 00 00 00 00 	movl   $0x0,-0x1c(%rbp)
  4010f6:	eb 3b                	jmp    401133 <LegacyBlockCipherencrypt_block+0x63>
  4010f8:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4010fb:	48 98                	cltq
  4010fd:	48 8b 55 f0          	mov    -0x10(%rbp),%rdx
  401101:	48 c1 e0 03          	shl    $0x3,%rax
  401105:	48 01 d0             	add    %rdx,%rax
  401108:	8b 00                	mov    (%rax),%eax
  40110a:	89 45 e0             	mov    %eax,-0x20(%rbp)
  40110d:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401110:	8b 55 e0             	mov    -0x20(%rbp),%edx
  401113:	89 d6                	mov    %edx,%esi
  401115:	89 c7                	mov    %eax,%edi
  401117:	e8 24 00 00 00       	callq  401140 <LegacyBlockCipherf_function>
  40111c:	89 45 dc             	mov    %eax,-0x24(%rbp)
  40111f:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401122:	33 45 dc             	xor    -0x24(%rbp),%eax
  401125:	89 45 d8             	mov    %eax,-0x28(%rbp)
  401128:	8b 45 e8             	mov    -0x18(%rbp),%eax
  40112b:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40112e:	8b 45 d8             	mov    -0x28(%rbp),%eax
  401131:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401134:	83 45 e4 01          	addl   $0x1,-0x1c(%rbp)
  401138:	83 7d e4 0f          	cmpl   $0xf,-0x1c(%rbp)
  40113c:	7e ba                	jle    4010f8 <LegacyBlockCipherencrypt_block+0x28>
  40113e:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401142:	8b 55 e8             	mov    -0x18(%rbp),%edx
  401145:	89 10                	mov    %edx,(%rax)
  401147:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40114b:	8b 55 ec             	mov    -0x14(%rbp),%edx
  40114e:	89 50 04             	mov    %edx,0x4(%rax)
  401151:	90                   	nop
  401152:	5d                   	pop    %rbp
  401153:	c3                   	retq

0000000000401140 <LegacyBlockCipherf_function>:
  401140:	55                   	push   %rbp
  401141:	48 89 e5             	mov    %rsp,%rbp
  401144:	89 7d fc             	mov    %edi,-0x4(%rbp)
  401147:	89 75 f8             	mov    %esi,-0x8(%rbp)
  40114a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40114d:	33 45 f8             	xor    -0x8(%rbp),%eax
  401150:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401153:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401156:	25 3f 00 00 00       	and    $0x3f,%eax
  40115b:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40115e:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401161:	83 e0 0f             	and    $0xf,%eax
  401164:	89 45 ec             	mov    %eax,-0x14(%rbp)
  401167:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40116a:	c1 e8 04             	shr    $0x4,%eax
  40116d:	83 e0 03             	and    $0x3,%eax
  401170:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401173:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401176:	c1 e0 02             	shl    $0x2,%eax
  401179:	03 45 e8             	add    -0x18(%rbp),%eax
  40117c:	83 e0 3f             	and    $0x3f,%eax
  40117f:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  401182:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401185:	5d                   	pop    %rbp
  401186:	c3                   	retq