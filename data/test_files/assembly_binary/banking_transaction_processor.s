banking_transaction_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	48 c7 45 f8 2b 7e 15 	movq   $0x16157e2b,-0x8(%rbp)
  40100f:	16
  401010:	48 c7 45 f0 28 ae d2 	movq   $0xa6d2ae28,-0x10(%rbp)
  401017:	a6
  401018:	48 c7 45 e8 ab f7 15 	movq   $0x8815f7ab,-0x18(%rbp)
  40101f:	88
  401020:	48 c7 45 e0 09 cf 4f 	movq   $0x3c4fcf09,-0x20(%rbp)
  401027:	3c
  401028:	e8 23 01 00 00       	callq  401150 <block_key_schedule>
  40102d:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401031:	48 c7 06 41 43 43 54 	movq   $0x54434341,(%rsi)
  401038:	48 c7 46 08 3a 31 32 	movq   $0x3433323a,0x8(%rsi)
  40103f:	33
  401040:	48 c7 46 10 35 36 37 	movq   $0x3a373635,0x10(%rsi)
  401047:	3a
  401048:	e8 33 01 00 00       	callq  401180 <block_encrypt_block>
  40104d:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401051:	be 10 00 00 00       	mov    $0x10,%esi
  401056:	e8 45 01 00 00       	callq  4011a0 <banking_hmac>
  40105b:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401060:	bf 00 00 00 00       	mov    $0x0,%edi
  401065:	0f 05                	syscall

0000000000401070 <feistel_function>:
  401070:	55                   	push   %rbp
  401071:	48 89 e5             	mov    %rsp,%rbp
  401074:	89 7d fc             	mov    %edi,-0x4(%rbp)
  401077:	89 75 f8             	mov    %esi,-0x8(%rbp)
  40107a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40107d:	31 45 f8             	xor    %eax,-0x8(%rbp)
  401080:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401083:	c1 c0 05             	rol    $0x5,%eax
  401086:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401089:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40108c:	25 ff 00 00 00       	and    $0xff,%eax
  401091:	05 9e 37 79 b9       	add    $0xb97937e9,%eax
  401096:	31 45 f8             	xor    %eax,-0x8(%rbp)
  401099:	8b 45 f8             	mov    -0x8(%rbp),%eax
  40109c:	c1 c0 07             	rol    $0x7,%eax
  40109f:	89 45 f0             	mov    %eax,-0x10(%rbp)
  4010a2:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4010a5:	25 ff ff 00 00       	and    $0xffff,%eax
  4010aa:	05 3c 6e f3 72       	add    $0x72f36e3c,%eax
  4010af:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4010b2:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4010b5:	c1 c0 0c             	rol    $0xc,%eax
  4010b8:	89 45 ec             	mov    %eax,-0x14(%rbp)
  4010bb:	8b 45 ec             	mov    -0x14(%rbp),%eax
  4010be:	25 ff ff ff 00       	and    $0xffffff,%eax
  4010c3:	05 78 dd e6 e4       	add    $0xe4e6dd78,%eax
  4010c8:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4010cb:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4010ce:	c1 c0 12             	rol    $0x12,%eax
  4010d1:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4010d4:	8b 45 e8             	mov    -0x18(%rbp),%eax
  4010d7:	05 f1 bb cd cc       	add    $0xcccdbbf1,%eax
  4010dc:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4010df:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4010e2:	5d                   	pop    %rbp
  4010e3:	c3                   	retq

0000000000401150 <block_key_schedule>:
  401150:	55                   	push   %rbp
  401151:	48 89 e5             	mov    %rsp,%rbp
  401154:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  401158:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40115c:	8b 00                	mov    (%rax),%eax
  40115e:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401161:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401165:	8b 40 04             	mov    0x4(%rax),%eax
  401168:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40116b:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  401172:	eb 2a                	jmp    40119e <block_key_schedule+0x4e>
  401174:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401177:	8b 55 ec             	mov    -0x14(%rbp),%edx
  40117a:	89 d6                	mov    %edx,%esi
  40117c:	89 c7                	mov    %eax,%edi
  40117e:	e8 ed fe ff ff       	callq  401070 <feistel_function>
  401183:	89 45 e8             	mov    %eax,-0x18(%rbp)
  401186:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401189:	31 45 e8             	xor    %eax,-0x18(%rbp)
  40118c:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40118f:	89 45 f0             	mov    %eax,-0x10(%rbp)
  401192:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401195:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401198:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  40119c:	eb 00                	jmp    40119e <block_key_schedule+0x4e>
  40119e:	83 7d ec 0f          	cmpl   $0xf,-0x14(%rbp)
  4011a2:	7e d0                	jle    401174 <block_key_schedule+0x24>
  4011a4:	90                   	nop
  4011a5:	5d                   	pop    %rbp
  4011a6:	c3                   	retq

0000000000401180 <block_encrypt_block>:
  401180:	55                   	push   %rbp
  401181:	48 89 e5             	mov    %rsp,%rbp
  401184:	48 83 ec 20          	sub    $0x20,%rsp
  401188:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  40118c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401190:	8b 00                	mov    (%rax),%eax
  401192:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401195:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401199:	8b 40 04             	mov    0x4(%rax),%eax
  40119c:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40119f:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  4011a6:	eb 28                	jmp    4011d0 <block_encrypt_block+0x50>
  4011a8:	8b 45 f4             	mov    -0xc(%rbp),%eax
  4011ab:	8b 55 ec             	mov    -0x14(%rbp),%edx
  4011ae:	89 d6                	mov    %edx,%esi
  4011b0:	89 c7                	mov    %eax,%edi
  4011b2:	e8 b9 fe ff ff       	callq  401070 <feistel_function>
  4011b7:	89 45 e8             	mov    %eax,-0x18(%rbp)
  4011ba:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4011bd:	31 45 e8             	xor    %eax,-0x18(%rbp)
  4011c0:	8b 45 f4             	mov    -0xc(%rbp),%eax
  4011c3:	89 45 f0             	mov    %eax,-0x10(%rbp)
  4011c6:	8b 45 e8             	mov    -0x18(%rbp),%eax
  4011c9:	89 45 f4             	mov    %eax,-0xc(%rbp)
  4011cc:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  4011d0:	83 7d ec 0f          	cmpl   $0xf,-0x14(%rbp)
  4011d4:	7e d2                	jle    4011a8 <block_encrypt_block+0x28>
  4011d6:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011da:	8b 55 f0             	mov    -0x10(%rbp),%edx
  4011dd:	89 10                	mov    %edx,(%rax)
  4011df:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011e3:	8b 55 f4             	mov    -0xc(%rbp),%edx
  4011e6:	89 50 04             	mov    %edx,0x4(%rax)
  4011e9:	90                   	nop
  4011ea:	c9                   	leaveq
  4011eb:	c3                   	retq

00000000004011a0 <banking_hmac>:
  4011a0:	55                   	push   %rbp
  4011a1:	48 89 e5             	mov    %rsp,%rbp
  4011a4:	48 83 ec 60          	sub    $0x60,%rsp
  4011a8:	48 89 7d f8          	mov    %rdi,-0x8(%rbp)
  4011ac:	89 75 f4             	mov    %esi,-0xc(%rbp)
  4011af:	c7 45 f0 36 36 36 36 	movl   $0x36363636,-0x10(%rbp)
  4011b6:	c7 45 ec 5c 5c 5c 5c 	movl   $0x5c5c5c5c,-0x14(%rbp)
  4011bd:	48 8d 45 e0          	lea    -0x20(%rbp),%rax
  4011c1:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4011c5:	48 8d 45 c0          	lea    -0x40(%rbp),%rax
  4011c9:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  4011cd:	c7 45 cc 00 00 00 00 	movl   $0x0,-0x34(%rbp)
  4011d4:	eb 24                	jmp    4011fa <banking_hmac+0x5a>
  4011d6:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4011da:	8b 55 cc             	mov    -0x34(%rbp),%edx
  4011dd:	48 63 d2             	movslq %edx,%rdx
  4011e0:	8b 4d f0             	mov    -0x10(%rbp),%ecx
  4011e3:	89 0c 90             	mov    %ecx,(%rax,%rdx,4)
  4011e6:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  4011ea:	8b 55 cc             	mov    -0x34(%rbp),%edx
  4011ed:	48 63 d2             	movslq %edx,%rdx
  4011f0:	8b 4d ec             	mov    -0x14(%rbp),%ecx
  4011f3:	89 0c 90             	mov    %ecx,(%rax,%rdx,4)
  4011f6:	83 45 cc 01          	addl   $0x1,-0x34(%rbp)
  4011fa:	83 7d cc 0f          	cmpl   $0xf,-0x34(%rbp)
  4011fe:	7e d6                	jle    4011d6 <banking_hmac+0x36>
  401200:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401204:	48 89 c7             	mov    %rax,%rdi
  401207:	e8 74 ff ff ff       	callq  401180 <block_encrypt_block>
  40120c:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  401210:	48 89 c7             	mov    %rax,%rdi
  401213:	e8 68 ff ff ff       	callq  401180 <block_encrypt_block>
  401218:	90                   	nop
  401219:	c9                   	leaveq
  40121a:	c3                   	retq