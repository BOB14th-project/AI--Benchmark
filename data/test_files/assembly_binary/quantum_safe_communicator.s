post_classical_safe_communicator:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 81 ec 00 02 00 00 	sub    $0x200,%rsp
  40100b:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  401012:	eb 1b                	jmp    40102f <_start+0x2f>
  401014:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401017:	48 98                	cltq
  401019:	c7 84 85 00 fe ff ff 	movl   $0x1,-0x200(%rbp,%rax,4)
  401020:	01 00 00 00
  401024:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401028:	81 7d fc ff 01 00 00 	cmpl   $0x1ff,-0x4(%rbp)
  40102f:	7e e3                	jle    401014 <_start+0x14>
  401031:	48 8d 85 00 fe ff ff 	k_cipher_4    -0x200(%rbp),%rax
  401038:	48 89 c7             	mov    %rax,%rdi
  40103b:	e8 20 00 00 00       	callq  401060 <ntru_key_generation>
  401040:	48 8d 7d f0          	k_cipher_4    -0x10(%rbp),%rdi
  401044:	be 10 00 00 00       	mov    $0x10,%esi
  401049:	e8 82 00 00 00       	callq  4010d0 <ntru_encrypt_message>
  40104e:	48 8d 7d e0          	k_cipher_4    -0x20(%rbp),%rdi
  401052:	be 20 00 00 00       	mov    $0x20,%esi
  401057:	e8 14 01 00 00       	callq  401170 <merkle_tree_signature>
  40105c:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401061:	bf 00 00 00 00       	mov    $0x0,%edi
  401066:	0f 05                	syscall

0000000000401060 <ntru_key_generation>:
  401060:	55                   	push   %rbp
  401061:	48 89 e5             	mov    %rsp,%rbp
  401064:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401068:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  40106f:	eb 29                	jmp    40109a <ntru_key_generation+0x3a>
  401071:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401074:	48 98                	cltq
  401076:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  40107a:	48 c1 e0 02          	shl    $0x2,%rax
  40107e:	48 01 d0             	add    %rdx,%rax
  401081:	8b 00                	mov    (%rax),%eax
  401083:	0f af 45 f4          	imul   -0xc(%rbp),%eax
  401087:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40108a:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40108d:	25 ff 07 00 00       	and    $0x7ff,%eax
  401092:	89 45 f0             	mov    %eax,-0x10(%rbp)
  401095:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401099:	81 7d f4 ff 01 00 00 	cmpl   $0x1ff,-0xc(%rbp)
  4010a0:	7e cf                	jle    401071 <ntru_key_generation+0x11>
  4010a2:	90                   	nop
  4010a3:	5d                   	pop    %rbp
  4010a4:	c3                   	retq

00000000004010d0 <ntru_encrypt_message>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4010d8:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4010db:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  4010e2:	eb 3c                	jmp    401120 <ntru_encrypt_message+0x50>
  4010e4:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4010e7:	48 98                	cltq
  4010e9:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4010ed:	48 01 d0             	add    %rdx,%rax
  4010f0:	0f b6 00             	movzbl (%rax),%eax
  4010f3:	0f b6 c0             	movzbl %al,%eax
  4010f6:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010f9:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4010fc:	0f af 45 f0          	imul   -0x10(%rbp),%eax
  401100:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401103:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401106:	25 ff 07 00 00       	and    $0x7ff,%eax
  40110b:	89 45 e4             	mov    %eax,-0x1c(%rbp)
  40110e:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401111:	48 98                	cltq
  401113:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  401117:	48 01 d0             	add    %rdx,%rax
  40111a:	8b 55 e4             	mov    -0x1c(%rbp),%edx
  40111d:	88 10                	mov    %dl,(%rax)
  40111f:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  401123:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401126:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  401129:	7c b9                	jl     4010e4 <ntru_encrypt_message+0x14>
  40112b:	90                   	nop
  40112c:	5d                   	pop    %rbp
  40112d:	c3                   	retq

0000000000401170 <merkle_tree_signature>:
  401170:	55                   	push   %rbp
  401171:	48 89 e5             	mov    %rsp,%rbp
  401174:	48 83 ec 40          	sub    $0x40,%rsp
  401178:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  40117c:	89 75 f4             	mov    %esi,-0xc(%rbp)
  40117f:	c7 45 f0 aa bb cc dd 	movl   $0xddccbbaa,-0x10(%rbp)
  401186:	c7 45 ec ee ff 00 11 	movl   $0x1100ffee,-0x14(%rbp)
  40118d:	c7 45 e8 22 33 44 55 	movl   $0x55443322,-0x18(%rbp)
  401194:	c7 45 e4 66 77 88 99 	movl   $0x99887766,-0x1c(%rbp)
  40119b:	c7 45 e0 00 00 00 00 	movl   $0x0,-0x20(%rbp)
  4011a2:	eb 2f                	jmp    4011d3 <merkle_tree_signature+0x63>
  4011a4:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4011a7:	48 98                	cltq
  4011a9:	48 8b 55 f8          	mov    -0x8(%rbp),%rdx
  4011ad:	48 01 d0             	add    %rdx,%rax
  4011b0:	0f b6 00             	movzbl (%rax),%eax
  4011b3:	0f b6 c0             	movzbl %al,%eax
  4011b6:	33 45 f0             	xor    -0x10(%rbp),%eax
  4011b9:	89 45 dc             	mov    %eax,-0x24(%rbp)
  4011bc:	8b 45 dc             	mov    -0x24(%rbp),%eax
  4011bf:	c1 c0 03             	rol    $0x3,%eax
  4011c2:	01 45 ec             	add    %eax,-0x14(%rbp)
  4011c5:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4011c8:	33 45 e8             	xor    -0x18(%rbp),%eax
  4011cb:	01 45 e4             	add    %eax,-0x1c(%rbp)
  4011ce:	d1 65 f0             	shll   -0x10(%rbp)
  4011d1:	83 45 e0 01          	addl   $0x1,-0x20(%rbp)
  4011d5:	8b 45 e0             	mov    -0x20(%rbp),%eax
  4011d8:	3b 45 f4             	cmp    -0xc(%rbp),%eax
  4011db:	7c c7                	jl     4011a4 <merkle_tree_signature+0x34>
  4011dd:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011e0:	33 45 ec             	xor    -0x14(%rbp),%eax
  4011e3:	33 45 e8             	xor    -0x18(%rbp),%eax
  4011e6:	33 45 e4             	xor    -0x1c(%rbp),%eax
  4011e9:	89 45 d8             	mov    %eax,-0x28(%rbp)
  4011ec:	8b 45 d8             	mov    -0x28(%rbp),%eax
  4011ef:	c9                   	leaveq
  4011f0:	c3                   	retq