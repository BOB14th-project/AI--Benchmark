automotive_ecu_cryptographic_unit:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40100f:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401016:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  40101d:	c7 45 f0 6f ed 9e ba 	movl   $0xba9eed6f,-0x10(%rbp)
  401024:	e8 c7 00 00 00       	callq  4010f0 <can_bus_authentication>
  401029:	89 45 ec             	mov    %eax,-0x14(%rbp)
  40102c:	48 8d 7d e0          	lea    -0x20(%rbp),%rdi
  401030:	48 8d 75 d0          	lea    -0x30(%rbp),%rsi
  401034:	ba 08 00 00 00       	mov    $0x8,%edx
  401039:	e8 e2 00 00 00       	callq  401120 <domesticn_automotive_cipher>
  40103e:	48 8d 7d c0          	lea    -0x40(%rbp),%rdi
  401042:	48 8d 75 b0          	lea    -0x50(%rbp),%rsi
  401046:	ba 16 00 00 00       	mov    $0x16,%edx
  40104b:	e8 10 01 00 00       	callq  401160 <vehicle_security_protocol>
  401050:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401055:	bf 00 00 00 00       	mov    $0x0,%edi
  40105a:	0f 05                	syscall

00000000004010f0 <can_bus_authentication>:
  4010f0:	55                   	push   %rbp
  4010f1:	48 89 e5             	mov    %rsp,%rbp
  4010f4:	48 83 ec 20          	sub    $0x20,%rsp
  4010f8:	c7 45 fc ab cd ef 01 	movl   $0x1efcdab,-0x4(%rbp)
  4010ff:	c7 45 f8 23 45 67 89 	movl   $0x89674523,-0x8(%rbp)
  401106:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401109:	0f af 45 f8          	imul   -0x8(%rbp),%eax
  40110d:	c1 c0 04             	rol    $0x4,%eax
  401110:	89 45 f4             	mov    %eax,-0xc(%rbp)
  401113:	8b 45 f4             	mov    -0xc(%rbp),%eax
  401116:	c9                   	leaveq
  401117:	c3                   	retq

0000000000401120 <domesticn_automotive_cipher>:
  401120:	55                   	push   %rbp
  401121:	48 89 e5             	mov    %rsp,%rbp
  401124:	48 83 ec 30          	sub    $0x30,%rsp
  401128:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40112c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401130:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401133:	c7 45 fc 84 94 62 d2 	movl   $0xd2629484,-0x4(%rbp)
  40113a:	c7 45 f8 ca 37 a8 93 	movl   $0x93a837ca,-0x8(%rbp)
  401141:	c7 45 f4 5b 9d 11 96 	movl   $0x96119d5b,-0xc(%rbp)
  401148:	c7 45 f0 00 00 00 00 	movl   $0x0,-0x10(%rbp)
  40114f:	eb 32                	jmp    401183 <domesticn_automotive_cipher+0x63>
  401151:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401154:	48 63 d0             	movslq %eax,%rdx
  401157:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40115b:	48 01 d0             	add    %rdx,%rax
  40115e:	0f b6 08             	movzbl (%rax),%ecx
  401161:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401164:	0f b6 c0             	movzbl %al,%eax
  401167:	31 c8                	xor    %ecx,%eax
  401169:	8b 55 f0             	mov    -0x10(%rbp),%edx
  40116c:	48 63 d2             	movslq %edx,%rdx
  40116f:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  401173:	48 01 ca             	add    %rcx,%rdx
  401176:	88 02                	mov    %al,(%rdx)
  401178:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40117b:	c1 c0 05             	rol    $0x5,%eax
  40117e:	33 45 f8             	xor    -0x8(%rbp),%eax
  401181:	89 45 fc             	mov    %eax,-0x4(%rbp)
  401184:	83 45 f0 01          	addl   $0x1,-0x10(%rbp)
  401188:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40118b:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40118e:	7c c1                	jl     401151 <domesticn_automotive_cipher+0x31>
  401190:	90                   	nop
  401191:	c9                   	leaveq
  401192:	c3                   	retq

0000000000401160 <vehicle_security_protocol>:
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
  401193:	c9                   	leaveq
  401194:	c3                   	retq