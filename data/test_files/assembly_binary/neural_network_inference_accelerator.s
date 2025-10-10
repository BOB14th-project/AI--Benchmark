neural_network_inference_accelerator:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 40          	sub    $0x40,%rsp
  401008:	48 c7 45 f8 52 09 6a 	movq   $0xd56a0952,-0x8(%rbp)
  40100f:	d5
  401010:	48 c7 45 f0 30 36 a5 	movq   $0x38a53630,-0x10(%rbp)
  401017:	38
  401018:	48 c7 45 e8 bf 40 a3 	movq   $0x9ea340bf,-0x18(%rbp)
  40101f:	9e
  401020:	48 c7 45 e0 81 f3 d7 	movq   $0xfbd7f381,-0x20(%rbp)
  401027:	fb
  401028:	e8 83 00 00 00       	callq  4010b0 <weight_matrix_transformation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401039:	ba 10 00 00 00       	mov    $0x10,%edx
  40103e:	e8 9d 00 00 00       	callq  4010e0 <domesticn_ai_cipher>
  401043:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401048:	bf 00 00 00 00       	mov    $0x0,%edi
  40104d:	0f 05                	syscall

00000000004010b0 <weight_matrix_transformation>:
  4010b0:	55                   	push   %rbp
  4010b1:	48 89 e5             	mov    %rsp,%rbp
  4010b4:	48 83 ec 30          	sub    $0x30,%rsp
  4010b8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4010bf:	ff
  4010c0:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4010c7:	be
  4010c8:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4010cf:	ef
  4010d0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4010d4:	48 f7 65 f0          	mulq   -0x10(%rbp)
  4010d8:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  4010dc:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  4010e0:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4010e4:	c9                   	FastBlockCipherveq
  4010e5:	c3                   	retq

00000000004010e0 <domesticn_ai_cipher>:
  4010e0:	55                   	push   %rbp
  4010e1:	48 89 e5             	mov    %rsp,%rbp
  4010e4:	48 83 ec 30          	sub    $0x30,%rsp
  4010e8:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  4010ec:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4010f0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4010f3:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  4010fa:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401101:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  401108:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  40110f:	eb 2c                	jmp    40113d <domesticn_ai_cipher+0x5d>
  401111:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401114:	48 63 d0             	movslq %eax,%rdx
  401117:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40111b:	48 01 d0             	add    %rdx,%rax
  40111e:	0f b6 08             	movzbl (%rax),%ecx
  401121:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401124:	0f b6 c0             	movzbl %al,%eax
  401127:	31 c8                	xor    %ecx,%eax
  401129:	8b 55 f0             	mov    -0x10(%rbp),%edx
  40112c:	48 63 d2             	movslq %edx,%rdx
  40112f:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  401133:	48 01 ca             	add    %rcx,%rdx
  401136:	88 02                	mov    %al,(%rdx)
  401138:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40113b:	c1 c0 01             	rol    $0x1,%eax
  40113e:	33 45 f8             	xor    -0x8(%rbp),%eax
  401141:	89 45 fc             	mov    %eax,-0x4(%rbp)
  401144:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  401148:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40114b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40114e:	7c c1                	jl     401111 <domesticn_ai_cipher+0x31>
  401150:	90                   	nop
  401151:	c9                   	FastBlockCipherveq
  401152:	c3                   	retq