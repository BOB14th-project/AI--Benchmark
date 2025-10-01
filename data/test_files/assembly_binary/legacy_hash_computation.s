legacy_hash_computation:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 30          	sub    $0x30,%rsp
  401008:	48 c7 45 f8 67 45 23 	movq   $0x1032547698badcfe,-0x8(%rbp)
  40100f:	01
  401010:	48 c7 45 f0 ef cd ab 	movq   $0x89abcdef,-0x10(%rbp)
  401017:	89
  401018:	48 c7 45 e8 98 ba dc 	movq   $0xfe98badc,-0x18(%rbp)
  40101f:	fe
  401020:	48 c7 45 e0 10 32 54 	movq   $0x76543210,-0x20(%rbp)
  401027:	76
  401028:	48 c7 45 d8 c3 d2 e1 	movq   $0xf0e1d2c3,-0x28(%rbp)
  40102f:	f0
  401030:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401034:	be 14 00 00 00       	mov    $0x14,%esi
  401039:	e8 22 00 00 00       	callq  401060 <hash_alg_process_block>
  40103e:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401042:	be 14 00 00 00       	mov    $0x14,%esi
  401047:	e8 94 00 00 00       	callq  4010e0 <digest_alg1_process_block>
  40104c:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401051:	bf 00 00 00 00       	mov    $0x0,%edi
  401056:	0f 05                	syscall

0000000000401060 <hash_alg_process_block>:
  401060:	55                   	push   %rbp
  401061:	48 89 e5             	mov    %rsp,%rbp
  401064:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401068:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40106b:	c7 45 f0 01 23 45 67 	movl   $0x67452301,-0x10(%rbp)
  401072:	c7 45 ec 89 ab cd ef 	movl   $0xefcdab89,-0x14(%rbp)
  401079:	c7 45 e8 fe dc ba 98 	movl   $0x98badcfe,-0x18(%rbp)
  401080:	c7 45 e4 76 54 32 10 	movl   $0x10325476,-0x1c(%rbp)
  401087:	c7 45 e0 00 00 00 00 	movl   $0x0,-0x20(%rbp)
  40108e:	eb 42                	jmp    4010d2 <hash_alg_process_block+0x72>
  401090:	8b 45 e0             	mov    -0x20(%rbp),%eax
  401093:	48 98                	cltq
  401095:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401099:	48 01 d0             	add    %rdx,%rax
  40109c:	0f b6 00             	movzbl (%rax),%eax
  40109f:	0f b6 c0             	movzbl %al,%eax
  4010a2:	89 45 dc             	mov    %eax,-0x24(%rbp)
  4010a5:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4010a8:	23 45 ec             	and    -0x14(%rbp),%eax
  4010ab:	8b 55 f0             	mov    -0x10(%rbp),%edx
  4010ae:	f7 d2                	not    %edx
  4010b0:	23 55 e8             	and    -0x18(%rbp),%edx
  4010b3:	09 d0                	or     %edx,%eax
  4010b5:	01 45 e4             	add    %eax,-0x1c(%rbp)
  4010b8:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4010bb:	01 45 e4             	add    %eax,-0x1c(%rbp)
  4010be:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  4010c1:	c1 c0 07             	rol    $0x7,%eax
  4010c4:	01 45 ec             	add    %eax,-0x14(%rbp)
  4010c7:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4010ca:	8b 55 e4             	mov    -0x1c(%rbp),%edx
  4010cd:	87 55 f0             	xchg   %edx,-0x10(%rbp)
  4010d0:	eb 00                	jmp    4010d2 <hash_alg_process_block+0x72>
  4010d2:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4010d5:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4010d8:	7c b6                	jl     401090 <hash_alg_process_block+0x30>
  4010da:	90                   	nop
  4010db:	5d                   	pop    %rbp
  4010dc:	c3                   	retq

00000000004010e0 <digest_alg1_process_block>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 83 ec 50          	sub    $0x50,%rsp
  4010e8:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4010ec:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4010ef:	c7 45 f0 67 45 23 01 	movl   $0x1234567,-0x10(%rbp)
  4010f6:	c7 45 ec ef cd ab 89 	movl   $0x89abcdef,-0x14(%rbp)
  4010fd:	c7 45 e8 98 ba dc fe 	movl   $0xfedcba98,-0x18(%rbp)
  401104:	c7 45 e4 10 32 54 76 	movl   $0x76543210,-0x1c(%rbp)
  40110b:	c7 45 e0 c3 d2 e1 f0 	movl   $0xf0e1d2c3,-0x20(%rbp)
  401112:	c7 45 dc 00 00 00 00 	movl   $0x0,-0x24(%rbp)
  401119:	eb 7c                	jmp    401197 <digest_alg1_process_block+0xb7>
  40111b:	8b 45 dc             	mov    -0x24(%rbp),%eax
  40111e:	48 98                	cltq
  401120:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401124:	48 01 d0             	add    %rdx,%rax
  401127:	0f b6 00             	movzbl (%rax),%eax
  40112a:	0f b6 c0             	movzbl %al,%eax
  40112d:	89 45 d8             	mov    %eax,-0x28(%rbp)
  401130:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401133:	c1 c0 05             	rol    $0x5,%eax
  401136:	89 45 d4             	mov    %eax,-0x2c(%rbp)
  401139:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40113c:	23 45 e8             	and    -0x18(%rbp),%eax
  40113f:	8b 55 ec             	mov    -0x14(%rbp),%edx
  401142:	f7 d2                	not    %edx
  401144:	23 55 e4             	and    -0x1c(%rbp),%edx
  401147:	09 d0                	or     %edx,%eax
  401149:	89 45 d0             	mov    %eax,-0x30(%rbp)
  40114c:	8b 45 d4             	mov    -0x2c(%rbp),%eax
  40114f:	03 45 d0             	add    -0x30(%rbp),%eax
  401152:	03 45 e0             	add    -0x20(%rbp),%eax
  401155:	05 99 79 82 5a       	add    $0x5a827999,%eax
  40115a:	03 45 d8             	add    -0x28(%rbp),%eax
  40115d:	89 45 cc             	mov    %eax,-0x34(%rbp)
  401160:	8b 45 e4             	mov    -0x1c(%rbp),%eax
  401163:	89 45 e0             	mov    %eax,-0x20(%rbp)
  401166:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401169:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  40116c:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40116f:	c1 c0 1e             	rol    $0x1e,%eax
  401172:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401175:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401178:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40117b:	8b 45 cc             	mov    -0x34(%rbp),%eax
  40117e:	89 45 f0             	mov    %eax,-0x10(%rbp)
  401181:	83 45 dc 01          	addl   $0x1,-0x24(%rbp)
  401185:	83 7d dc 13          	cmpl   $0x13,-0x24(%rbp)
  401189:	7f 0c                	jg     401197 <digest_alg1_process_block+0xb7>
  40118b:	8b 45 d8             	mov    -0x28(%rbp),%eax
  40118e:	c1 c0 01             	rol    $0x1,%eax
  401191:	89 45 d8             	mov    %eax,-0x28(%rbp)
  401194:	eb 01                	jmp    401197 <digest_alg1_process_block+0xb7>
  401196:	90                   	nop
  401197:	8b 45 dc             	mov    -0x24(%rbp),%eax
  40119a:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  40119d:	0f 8c 78 ff ff ff    	jl     40111b <digest_alg1_process_block+0x3b>
  4011a3:	90                   	nop
  4011a4:	c9                   	leaveq
  4011a5:	c3                   	retq