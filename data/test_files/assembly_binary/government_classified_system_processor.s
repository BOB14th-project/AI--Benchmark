government_classified_system_processor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401017:	be
  401018:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  40101f:	ef
  401020:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  401027:	fe
  401028:	e8 a3 00 00 00       	callq  4010d0 <classified_key_generation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	lea    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	lea    -0x40(%rbp),%rsi
  401039:	ba 16 00 00 00       	mov    $0x16,%edx
  40103e:	e8 bd 00 00 00       	callq  401100 <document_protection_layer>
  401043:	48 8d 7d b0          	lea    -0x50(%rbp),%rdi
  401047:	be 10 00 00 00       	mov    $0x10,%esi
  40104c:	e8 ef 00 00 00       	callq  401140 <korean_government_cipher>
  401051:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401056:	bf 00 00 00 00       	mov    $0x0,%edi
  40105b:	0f 05                	syscall

00000000004010d0 <classified_key_generation>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 83 ec 30          	sub    $0x30,%rsp
  4010d8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4010df:	ff
  4010e0:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4010e7:	be
  4010e8:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4010ef:	ef
  4010f0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010f4:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4010f8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4010fc:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401100:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401104:	c9                   	leaveq
  401105:	c3                   	retq

0000000000401100 <document_protection_layer>:
  401100:	55                   	push   %rbp
  401101:	48 89 e5             	mov    %rsp,%rbp
  401104:	48 83 ec 30          	sub    $0x30,%rsp
  401108:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40110c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401110:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401113:	48 c7 45 f8 63 7c 77 	movq   $0x7b777c63,-0x8(%rbp)
  40111a:	7b
  40111b:	48 c7 45 f0 f2 6b 6f 	movq   $0xc56f6bf2,-0x10(%rbp)
  401122:	c5
  401123:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40112a:	eb 2a                	jmp    401156 <document_protection_layer+0x56>
  40112c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40112f:	48 63 d0             	movslq %eax,%rdx
  401132:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401136:	48 01 d0             	add    %rdx,%rax
  401139:	0f b6 08             	movzbl (%rax),%ecx
  40113c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401140:	0f b6 c0             	movzbl %al,%eax
  401143:	31 c8                	xor    %ecx,%eax
  401145:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401148:	48 63 d2             	movslq %edx,%rdx
  40114b:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40114f:	48 01 ca             	add    %rcx,%rdx
  401152:	88 02                	mov    %al,(%rdx)
  401154:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401158:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40115b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40115e:	7c cc                	jl     40112c <document_protection_layer+0x2c>
  401160:	90                   	nop
  401161:	c9                   	leaveq
  401162:	c3                   	retq

0000000000401140 <korean_government_cipher>:
  401140:	55                   	push   %rbp
  401141:	48 89 e5             	mov    %rsp,%rbp
  401144:	48 83 ec 20          	sub    $0x20,%rsp
  401148:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  40114c:	89 75 ec             	mov    %esi,-0x14(%rbp)
  40114f:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  401156:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  40115d:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401160:	33 45 f8             	xor    -0x8(%rbp),%eax
  401163:	c1 c0 07             	rol    $0x7,%eax
  401166:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401169:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40116c:	c9                   	leaveq
  40116d:	c3                   	retq