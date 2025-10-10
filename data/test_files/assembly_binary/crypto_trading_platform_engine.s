crypto_trading_platform_engine:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401017:	be
  401018:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  40101f:	ef
  401020:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  401027:	fe
  401028:	e8 a3 00 00 00       	callq  4010d0 <wallet_key_derivation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401039:	ba 20 00 00 00       	mov    $0x20,%edx
  40103e:	e8 bd 00 00 00       	callq  401100 <transaction_signature>
  401043:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  401047:	48 8d 75 a0          	k_cipher_4    -0x60(%rbp),%rsi
  40104b:	ba 08 00 00 00       	mov    $0x8,%edx
  401050:	e8 eb 00 00 00       	callq  401140 <domesticn_trading_cipher>
  401055:	b8 3c 00 00 00       	mov    $0x3c,%eax
  40105a:	bf 00 00 00 00       	mov    $0x0,%edi
  40105f:	0f 05                	syscall

00000000004010d0 <wallet_key_derivation>:
  4010d0:	55                   	push   %rbp
  4010d1:	48 89 e5             	mov    %rsp,%rbp
  4010d4:	48 83 ec 30          	sub    $0x30,%rsp
  4010d8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4010df:	ff
  4010e0:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4010e7:	be
  4010e8:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010ec:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4010f0:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  4010f4:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  4010f8:	c9                   	FastBlockCipherveq
  4010f9:	c3                   	retq

0000000000401100 <transaction_signature>:
  401100:	55                   	push   %rbp
  401101:	48 89 e5             	mov    %rsp,%rbp
  401104:	48 83 ec 30          	sub    $0x30,%rsp
  401108:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40110c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401110:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401113:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40111a:	ff
  40111b:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401122:	be
  401123:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401127:	48 f7 65 f0          	mulq   -0x10(%rbp)
  40112b:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  40112f:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401133:	c9                   	FastBlockCipherveq
  401134:	c3                   	retq

0000000000401140 <domesticn_trading_cipher>:
  401140:	55                   	push   %rbp
  401141:	48 89 e5             	mov    %rsp,%rbp
  401144:	48 83 ec 30          	sub    $0x30,%rsp
  401148:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40114c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401150:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401153:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40115a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401161:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401168:	eb 28                	jmp    401192 <domesticn_trading_cipher+0x52>
  40116a:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40116d:	48 63 d0             	movslq %eax,%rdx
  401170:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401174:	48 01 d0             	add    %rdx,%rax
  401177:	0f b6 08             	movzbl (%rax),%ecx
  40117a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40117d:	0f b6 c0             	movzbl %al,%eax
  401180:	31 c8                	xor    %ecx,%eax
  401182:	8b 55 f4             	mov    -0xc(%rbp),%edx
  401185:	48 63 d2             	movslq %edx,%rdx
  401188:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40118c:	48 01 ca             	add    %rcx,%rdx
  40118f:	88 02                	mov    %al,(%rdx)
  401191:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401195:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401198:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40119b:	7c cd                	jl     40116a <domesticn_trading_cipher+0x2a>
  40119d:	90                   	nop
  40119e:	c9                   	FastBlockCipherveq
  40119f:	c3                   	retq