smart_card_security_module:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	c7 45 fc a5 96 30 38 	movl   $0x383096a5,-0x4(%rbp)
  40100f:	c7 45 f8 bf 40 a3 9e 	movl   $0x9ea340bf,-0x8(%rbp)
  401016:	c7 45 f4 8c 4e 01 23 	movl   $0x23014e8c,-0xc(%rbp)
  40101d:	c7 45 f0 45 ab 67 12 	movl   $0x1267ab45,-0x10(%rbp)
  401024:	e8 c7 00 00 00       	callq  4010f0 <smart_card_authentication>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	lea    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	lea    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 e2 00 00 00       	callq  401120 <domesticn_smartcard_cipher>
  40103e:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401042:	be 10 00 00 00       	mov    $0x10,%esi
  401047:	e8 14 01 00 00       	callq  401160 <card_challenge_response>
  40104c:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401051:	bf 00 00 00 00       	mov    $0x0,%edi
  401056:	0f 05                	syscall

00000000004010f0 <smart_card_authentication>:
  4010f0:	55                   	push   %rbp
  4010f1:	48 89 e5             	mov    %rsp,%rbp
  4010f4:	48 83 ec 20          	sub    $0x20,%rsp
  4010f8:	c7 45 fc ff 00 ff 00 	movl   $0xff00ff,-0x4(%rbp)
  4010ff:	c7 45 f8 00 ff 00 ff 	movl   $0xff00ff00,-0x8(%rbp)
  401106:	c7 45 f4 a5 a5 a5 a5 	movl   $0xa5a5a5a5,-0xc(%rbp)
  40110d:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401110:	33 45 f8             	xor    -0x8(%rbp),%eax
  401113:	0f af 45 f4          	imul   -0xc(%rbp),%eax
  401117:	89 45 f0             	mov    %eax,-0x10(%rbp)
  40111a:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40111d:	c9                   	leaveq
  40111e:	c3                   	retq

0000000000401120 <domesticn_smartcard_cipher>:
  401120:	55                   	push   %rbp
  401121:	48 89 e5             	mov    %rsp,%rbp
  401124:	48 83 ec 30          	sub    $0x30,%rsp
  401128:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40112c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401130:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401133:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40113a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401141:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  401148:	c7 45 f0 6f ed 9e ba 	movl   $0xba9eed6f,-0x10(%rbp)
  40114f:	c7 45 ec 00 00 00 00 	movl   $0x0,-0x14(%rbp)
  401156:	eb 2c                	jmp    401184 <domesticn_smartcard_cipher+0x64>
  401158:	8b 45 ec             	mov    -0x14(%rbp),%eax
  40115b:	48 63 d0             	movslq %eax,%rdx
  40115e:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401162:	48 01 d0             	add    %rdx,%rax
  401165:	0f b6 08             	movzbl (%rax),%ecx
  401168:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40116b:	0f b6 c0             	movzbl %al,%eax
  40116e:	31 c8                	xor    %ecx,%eax
  401170:	8b 55 ec             	mov    -0x14(%rbp),%edx
  401173:	48 63 d2             	movslq %edx,%rdx
  401176:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40117a:	48 01 ca             	add    %rcx,%rdx
  40117d:	88 02                	mov    %al,(%rdx)
  40117f:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401182:	c1 c0 03             	rol    $0x3,%eax
  401185:	33 45 f8             	xor    -0x8(%rbp),%eax
  401188:	89 45 fc             	mov    %eax,-0x4(%rbp)
  40118b:	83 45 ec 01          	addl   $0x1,-0x14(%rbp)
  40118f:	8b 45 ec             	mov    -0x14(%rbp),%eax
  401192:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401195:	7c c1                	jl     401158 <domesticn_smartcard_cipher+0x38>
  401197:	90                   	nop
  401198:	c9                   	leaveq
  401199:	c3                   	retq

0000000000401160 <card_challenge_response>:
  401160:	55                   	push   %rbp
  401161:	48 89 e5             	mov    %rsp,%rbp
  401164:	48 83 ec 30          	sub    $0x30,%rsp
  401168:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40116c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40116f:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  401176:	ff
  401177:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  40117e:	be
  40117f:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  401186:	ef
  401187:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40118b:	48 f7 65 f0          	mulq   -0x10(%rbp)
  40118f:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  401193:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401197:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  40119b:	c9                   	leaveq
  40119c:	c3                   	retq