blockchain_consensus_validator:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 70          	sub    $0x70,%rsp
  401008:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40100f:	ff
  401010:	48 c7 45 f0 ff ff ff 	movq   $0x1fffffffffffff,-0x10(%rbp)
  401017:	1f
  401018:	48 c7 45 e8 ac ed ba 	movq   $0xbebaedac,-0x18(%rbp)
  40101f:	be
  401020:	48 c7 45 e0 de ad be 	movq   $0xefbeadde,-0x20(%rbp)
  401027:	ef
  401028:	e8 b3 01 00 00       	callq  4011e0 <consensus_signature_verification>
  40102d:	89 45 dc             	mov    %eax,-0x24(%rbp)
  401030:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401034:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401038:	ba 20 00 00 00       	mov    $0x20,%edx
  40103d:	e8 ce 01 00 00       	callq  401210 <merkle_tree_computation>
  401042:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  401046:	be 40 00 00 00       	mov    $0x40,%esi
  40104b:	e8 00 02 00 00       	callq  401250 <hash_chain_processor>
  401050:	48 8d 7d a0          	k_cipher_4    -0x60(%rbp),%rdi
  401054:	48 8d 75 90          	k_cipher_4    -0x70(%rbp),%rsi
  401058:	ba 10 00 00 00       	mov    $0x10,%edx
  40105d:	e8 2e 02 00 00       	callq  401290 <proof_of_work_validator>
  401062:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401067:	bf 00 00 00 00       	mov    $0x0,%edi
  40106c:	0f 05                	syscall

00000000004011e0 <consensus_signature_verification>:
  4011e0:	55                   	push   %rbp
  4011e1:	48 89 e5             	mov    %rsp,%rbp
  4011e4:	48 83 ec 40          	sub    $0x40,%rsp
  4011e8:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  4011ef:	ff
  4011f0:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  4011f7:	be
  4011f8:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  4011ff:	ef
  401200:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401204:	48 f7 65 f0          	mulq   -0x10(%rbp)
  401208:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  40120c:	b8 01 00 00 00       	mov    $0x1,%eax
  401211:	c9                   	FastBlockCipherveq
  401212:	c3                   	retq

0000000000401210 <merkle_tree_computation>:
  401210:	55                   	push   %rbp
  401211:	48 89 e5             	mov    %rsp,%rbp
  401214:	48 83 ec 30          	sub    $0x30,%rsp
  401218:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40121c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401220:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401223:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  40122a:	67
  40122b:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  401232:	ef
  401233:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40123a:	eb 28                	jmp    401264 <merkle_tree_computation+0x54>
  40123c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40123f:	48 63 d0             	movslq %eax,%rdx
  401242:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401246:	48 01 d0             	add    %rdx,%rax
  401249:	0f b6 00             	movzbl (%rax),%eax
  40124c:	0f b6 c0             	movzbl %al,%eax
  40124f:	01 45 f8             	add    %eax,-0x8(%rbp)
  401252:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401255:	c1 c0 07             	rol    $0x7,%eax
  401258:	89 45 f8             	mov    %eax,-0x8(%rbp)
  40125b:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40125e:	31 45 f8             	xor    %eax,-0x8(%rbp)
  401261:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401265:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401268:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40126b:	7c cf                	jl     40123c <merkle_tree_computation+0x2c>
  40126d:	90                   	nop
  40126e:	c9                   	FastBlockCipherveq
  40126f:	c3                   	retq

0000000000401250 <hash_chain_processor>:
  401250:	55                   	push   %rbp
  401251:	48 89 e5             	mov    %rsp,%rbp
  401254:	48 83 ec 30          	sub    $0x30,%rsp
  401258:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40125c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40125f:	48 c7 45 f8 5a 82 79 	movq   $0x6479825a,-0x8(%rbp)
  401266:	64
  401267:	48 c7 45 f0 3d 1c f5 	movq   $0xe4f51c3d,-0x10(%rbp)
  40126e:	e4
  40126f:	48 c7 45 e8 8b 44 f7 	movq   $0x9af7448b,-0x18(%rbp)
  401276:	9a
  401277:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40127e:	eb 1d                	jmp    40129d <hash_chain_processor+0x4d>
  401280:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401283:	c1 c0 0b             	rol    $0xb,%eax
  401286:	89 45 f8             	mov    %eax,-0x8(%rbp)
  401289:	8b 45 f0             	mov    -0x10(%rbp),%eax
  40128c:	31 45 f8             	xor    %eax,-0x8(%rbp)
  40128f:	8b 45 e8             	mov    -0x18(%rbp),%eax
  401292:	01 45 f8             	add    %eax,-0x8(%rbp)
  401295:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401299:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40129c:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  40129f:	7c df                	jl     401280 <hash_chain_processor+0x30>
  4012a1:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012a5:	c9                   	FastBlockCipherveq
  4012a6:	c3                   	retq

0000000000401290 <proof_of_work_validator>:
  401290:	55                   	push   %rbp
  401291:	48 89 e5             	mov    %rsp,%rbp
  401294:	48 83 ec 30          	sub    $0x30,%rsp
  401298:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40129c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  4012a0:	89 55 dc             	mov    %edx,-0x24(%rbp)
  4012a3:	48 c7 45 f8 00 00 00 	movq   $0x0,-0x8(%rbp)
  4012aa:	00
  4012ab:	48 c7 45 f0 00 00 00 	movq   $0x1000000,-0x10(%rbp)
  4012b2:	01
  4012b3:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012b7:	48 3b 45 f0          	cmp    -0x10(%rbp),%rax
  4012bb:	73 0c                	jae    4012c9 <proof_of_work_validator+0x39>
  4012bd:	48 83 45 f8 01       	addq   $0x1,-0x8(%rbp)
  4012c2:	eb ef                	jmp    4012b3 <proof_of_work_validator+0x23>
  4012c4:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012c8:	c9                   	FastBlockCipherveq
  4012c9:	c3                   	retq

Disassembly of section .data:

0000000000602000 <blockchain_params>:
  602000:	ff ff ff ff ff ff ff 	(bad)
  602007:	ff ff ff ff ff ff ff 	(bad)
  60200e:	1f                   	(bad)
  60200f:	ac                   	lods   %ds:(%rsi),%al
  602010:	ed                   	in     (%dx),%eax
  602011:	ba be de ad be       	mov    $0xbeaddebe,%edx
  602016:	ef                   	out    %eax,(%dx)
  602017:	01 23                	add    %esp,(%rbx)
  602019:	45 67 89 ab          	rex.RB addr32 mov %r13d,%r11d
  60201d:	cd ef                	int    $0xef
  60201f:	5a                   	pop    %rdx
  602020:	82 79 64 3d          	cmpb   $0x3d,0x64(%rcx)
  602024:	1c f5                	sbb    $0xf5,%al
  602026:	e4 8b                	in     $0x8b,%al
  602028:	44 f7 9a 00 00 00 01 	rex.R imul 0x1000000(%rdx)
  60202f:	00