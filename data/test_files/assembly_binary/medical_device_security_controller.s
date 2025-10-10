medical_device_security_controller:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	c7 45 fc a5 96 30 38 	movl   $0x383096a5,-0x4(%rbp)
  40100f:	c7 45 f8 bf 40 a3 9e 	movl   $0x9ea340bf,-0x8(%rbp)
  401016:	c7 45 f4 8c 4e 01 23 	movl   $0x23014e8c,-0xc(%rbp)
  40101d:	c7 45 f0 45 ab 67 12 	movl   $0x1267ab45,-0x10(%rbp)
  401024:	e8 c7 00 00 00       	callq  4010f0 <medical_key_generation>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	k_cipher_4    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	k_cipher_4    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 e2 00 00 00       	callq  401120 <domesticn_medical_cipher>
  40103e:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401042:	48 8d 75 b0          	k_cipher_4    -0x50(%rbp),%rsi
  401046:	ba 10 00 00 00       	mov    $0x10,%edx
  40104b:	e8 10 01 00 00       	callq  401160 <patient_data_protection>
  401050:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401055:	bf 00 00 00 00       	mov    $0x0,%edi
  40105a:	0f 05                	syscall

00000000004010f0 <medical_key_generation>:
  4010f0:	55                   	push   %rbp
  4010f1:	48 89 e5             	mov    %rsp,%rbp
  4010f4:	48 83 ec 20          	sub    $0x20,%rsp
  4010f8:	c7 45 fc 7a 69 de 4b 	movl   $0x4bde697a,-0x4(%rbp)
  4010ff:	c7 45 f8 e8 f7 a6 c5 	movl   $0xc5a6f7e8,-0x8(%rbp)
  401106:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401109:	33 45 f8             	xor    -0x8(%rbp),%eax
  40110c:	c1 c0 08             	rol    $0x8,%eax
  40110f:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401112:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401115:	c9                   	FastBlockCipherveq
  401116:	c3                   	retq

0000000000401120 <domesticn_medical_cipher>:
  401120:	55                   	push   %rbp
  401121:	48 89 e5             	mov    %rsp,%rbp
  401124:	48 83 ec 30          	sub    $0x30,%rsp
  401128:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40112c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401130:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401133:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40113a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401141:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  401148:	eb 28                	jmp    401172 <domesticn_medical_cipher+0x52>
  40114a:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40114d:	48 63 d0             	movslq %eax,%rdx
  401150:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401154:	48 01 d0             	add    %rdx,%rax
  401157:	0f b6 08             	movzbl (%rax),%ecx
  40115a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40115d:	0f b6 c0             	movzbl %al,%eax
  401160:	31 c8                	xor    %ecx,%eax
  401162:	8b 55 f4             	mov    -0xc(%rbp),%edx
  401165:	48 63 d2             	movslq %edx,%rdx
  401168:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40116c:	48 01 ca             	add    %rcx,%rdx
  40116f:	88 02                	mov    %al,(%rdx)
  401171:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  401175:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401178:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40117b:	7c cd                	jl     40114a <domesticn_medical_cipher+0x2a>
  40117d:	90                   	nop
  40117e:	c9                   	FastBlockCipherveq
  40117f:	c3                   	retq

0000000000401160 <patient_data_protection>:
  401160:	55                   	push   %rbp
  401161:	48 89 e5             	mov    %rsp,%rbp
  401164:	48 83 ec 30          	sub    $0x30,%rsp
  401168:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40116c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401170:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401173:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40117a:	ff
  40117b:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401182:	be
  401183:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401187:	48 f7 65 f0          	mulq   -0x10(%rbp)
  40118b:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  40118f:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401193:	c9                   	FastBlockCipherveq
  401194:	c3                   	retq