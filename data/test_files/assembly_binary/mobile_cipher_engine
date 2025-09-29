mobile_cipher_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 ab cd ef 	movq   $0x123456789abcdef,-0x8(%rbp)
  40100f:	12
  401010:	48 c7 45 f0 34 56 78 	movq   $0x9abcdef012345678,-0x10(%rbp)
  401017:	9a
  401018:	48 c7 45 e8 01 02 03 	movq   $0x404030201,-0x18(%rbp)
  40101f:	04
  401020:	e8 bb 00 00 00       	callq  4010e0 <a5_1_init>
  401025:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401029:	be 08 00 00 00       	mov    $0x8,%esi
  40102e:	e8 1d 01 00 00       	callq  401150 <a5_1_encrypt_frame>
  401033:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401037:	be 10 00 00 00       	mov    $0x10,%esi
  40103c:	e8 8f 01 00 00       	callq  4011d0 <tea_encrypt_block>
  401041:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401046:	bf 00 00 00 00       	mov    $0x0,%edi
  40104b:	0f 05                	syscall

00000000004010e0 <a5_1_init>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 83 ec 40          	sub    $0x40,%rsp
  4010e8:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4010ef:	eb 17                	jmp    401108 <a5_1_init+0x28>
  4010f1:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4010f4:	48 98                	cltq
  4010f6:	c7 84 85 e0 ff ff ff 	movl   $0x0,-0x20(%rbp,%rax,4)
  4010fd:	00 00 00 00
  401101:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401105:	eb 01                	jmp    401108 <a5_1_init+0x28>
  401107:	90                   	nop
  401108:	83 7d fc 12          	cmpl   $0x12,-0x4(%rbp)
  40110c:	7e e3                	jle    4010f1 <a5_1_init+0x11>
  40110e:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  401115:	eb 17                	jmp    40112e <a5_1_init+0x4e>
  401117:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40111a:	48 98                	cltq
  40111c:	c7 84 85 b8 ff ff ff 	movl   $0x0,-0x48(%rbp,%rax,4)
  401123:	00 00 00 00
  401127:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  40112b:	eb 01                	jmp    40112e <a5_1_init+0x4e>
  40112d:	90                   	nop
  40112e:	83 7d fc 15          	cmpl   $0x15,-0x4(%rbp)
  401132:	7e e3                	jle    401117 <a5_1_init+0x37>
  401134:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40113b:	eb 17                	jmp    401154 <a5_1_init+0x74>
  40113d:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401140:	48 98                	cltq
  401142:	c7 84 85 88 ff ff ff 	movl   $0x0,-0x78(%rbp,%rax,4)
  401149:	00 00 00 00
  40114d:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401151:	eb 01                	jmp    401154 <a5_1_init+0x74>
  401153:	90                   	nop
  401154:	83 7d fc 16          	cmpl   $0x16,-0x4(%rbp)
  401158:	7e e3                	jle    40113d <a5_1_init+0x5d>
  40115a:	90                   	nop
  40115b:	c9                   	leaveq
  40115c:	c3                   	retq

0000000000401150 <a5_1_encrypt_frame>:
  401150:	55                   	push   %rbp
  401151:	48 89 e5             	mov    %rsp,%rbp
  401154:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401158:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40115b:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  401162:	eb 5c                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  401164:	e8 e7 00 00 00       	callq  401250 <a5_1_clock_all>
  401169:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40116c:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40116f:	48 98                	cltq
  401171:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401175:	48 01 d0             	add    %rdx,%rax
  401178:	0f b6 00             	movzbl (%rax),%eax
  40117b:	0f b6 c0             	movzbl %al,%eax
  40117e:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401181:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401184:	33 45 ec             	xor    -0x14(%rbp),%eax
  401187:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  40118a:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40118d:	48 98                	cltq
  40118f:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401193:	48 01 d0             	add    %rdx,%rax
  401196:	8b 55 e4             	mov    -0x1c(%rbp),%edx
  401199:	88 10                	mov    %dl,(%rax)
  40119b:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  40119f:	eb 1f                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  4011a1:	90                   	nop
  4011a2:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011a6:	eb 18                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  4011a8:	90                   	nop
  4011a9:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011ad:	eb 11                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  4011af:	90                   	nop
  4011b0:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011b4:	eb 0a                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  4011b6:	90                   	nop
  4011b7:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011bb:	eb 03                	jmp    4011c0 <a5_1_encrypt_frame+0x70>
  4011bd:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  4011c1:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011c4:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011c7:	7c 9b                	jl     401164 <a5_1_encrypt_frame+0x14>
  4011c9:	90                   	nop
  4011ca:	5d                   	pop    %rbp
  4011cb:	c3                   	retq

00000000004011d0 <tea_encrypt_block>:
  4011d0:	55                   	push   %rbp
  4011d1:	48 89 e5             	mov    %rsp,%rbp
  4011d4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011d8:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4011db:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011df:	8b 00                	mov    (%rax),%eax
  4011e1:	89 45 f0             	mov    %eax,-0x10(%rbp)
  4011e4:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011e8:	8b 40 04             	mov    0x4(%rax),%eax
  4011eb:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4011ee:	c7 45 e8 00 00 00 00 	movl   $0x0,-0x18(%rbp)
  4011f5:	c7 45 e4 b9 79 37 9e 	movl   $0x9e3779b9,-0x1c(%rbp)
  4011fc:	c7 45 e0 00 00 00 00 	movl   $0x0,-0x20(%rbp)
  401203:	eb 39                	jmp    40123e <tea_encrypt_block+0x6e>
  401205:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401208:	03 45 e4             	add    -0x1c(%rbp),%eax
  40120b:	89 45 e8             	mov    %eax,-0x18(%rbp)
  40120e:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401211:	c1 e0 04             	shl    $0x4,%eax
  401214:	89 45 dc             	mov    %eax,-0x24(%rbp)
  401217:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40121a:	03 45 e8             	add    -0x18(%rbp),%eax
  40121d:	89 45 d8             	mov    %eax,-0x28(%rbp)
  401220:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401223:	c1 e8 05             	shr    $0x5,%eax
  401226:	89 45 d4             	mov    %eax,-0x2c(%rbp)
  401229:	8b 45 dc             	mov    -0x24(%rbp),%eax
  40122c:	33 45 d4             	xor    -0x2c(%rbp),%eax
  40122f:	03 45 d8             	add    -0x28(%rbp),%eax
  401232:	01 45 f0             	add    %eax,-0x10(%rbp)
  401235:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401238:	87 45 ec             	xchg   %eax,-0x14(%rbp)
  40123b:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40123e:	83 45 e0 01          	addl   $0x1,-0x20(%rbp)
  401242:	83 7d e0 20          	cmpl   $0x20,-0x20(%rbp)
  401246:	7c bd                	jl     401205 <tea_encrypt_block+0x35>
  401248:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40124c:	8b 55 f0             	mov    -0x10(%rbp),%edx
  40124f:	89 10                	mov    %edx,(%rax)
  401251:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401255:	8b 55 ec             	mov    -0x14(%rbp),%edx
  401258:	89 50 04             	mov    %edx,0x4(%rax)
  40125b:	90                   	nop
  40125c:	5d                   	pop    %rbp
  40125d:	c3                   	retq

0000000000401250 <a5_1_clock_all>:
  401250:	55                   	push   %rbp
  401251:	48 89 e5             	mov    %rsp,%rbp
  401254:	c7 45 fc 01 00 00 00 	movl   $0x1,-0x4(%rbp)
  40125b:	c7 45 f8 01 00 00 00 	movl   $0x1,-0x8(%rbp)
  401262:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401269:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40126c:	03 45 f8             	add    -0x8(%rbp),%eax
  40126f:	03 45 f4             	add    -0xc(%rbp),%eax
  401272:	89 45 f0             	mov    %eax,-0x10(%rbp)
  401275:	83 7d f0 01          	cmpl   $0x1,-0x10(%rbp)
  401279:	7f 05                	jg     401280 <a5_1_clock_all+0x30>
  40127b:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  401282:	eb 05                	jmp    401289 <a5_1_clock_all+0x39>
  401284:	c7 45 ec 01 00 00 00 	movl   $0x1,-0x14(%rbp)
  40128b:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40128e:	33 45 f8             	xor    -0x8(%rbp),%eax
  401291:	33 45 f4             	xor    -0xc(%rbp),%eax
  401294:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401297:	8b 45 e8             	mov    -0x18(%rbp),%eax
  40129a:	5d                   	pop    %rbp
  40129b:	c3                   	retq