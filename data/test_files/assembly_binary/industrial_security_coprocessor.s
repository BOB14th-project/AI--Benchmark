industrial_security_coprocessor:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 80          	sub    $0x80,%rsp
  401008:	48 c7 45 f8 67 45 23 	movq   $0x1a234567,-0x8(%rbp)
  40100f:	1a
  401010:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  401017:	ef
  401018:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  40101f:	98
  401020:	48 c7 45 e0 76 54 32 	movq   $0x10325476,-0x20(%rbp)
  401027:	10
  401028:	e8 c3 01 00 00       	callq  4011f0 <industrial_key_derivation>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401035:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401039:	ba 10 00 00 00       	mov    $0x10,%edx
  40103e:	e8 dd 01 00 00       	callq  401220 <block_transformation_unit>
  401043:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  401047:	48 8d 75 a0          	k_cipher_4    -0x60(%rbp),%rsi
  40104b:	ba 20 00 00 00       	mov    $0x20,%edx
  401050:	e8 0b 02 00 00       	callq  401260 <scada_authentication_module>
  401055:	48 8d 7d 90          	k_cipher_4    -0x70(%rbp),%rdi
  401059:	be 08 00 00 00       	mov    $0x8,%esi
  40105e:	e8 3d 02 00 00       	callq  4012a0 <domesticn_industrial_cipher>
  401063:	48 8d 7d 80          	k_cipher_4    -0x80(%rbp),%rdi
  401067:	be 20 00 00 00       	mov    $0x20,%esi
  40106c:	e8 6f 02 00 00       	callq  4012e0 <control_system_digest>
  401071:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401076:	bf 00 00 00 00       	mov    $0x0,%edi
  40107b:	0f 05                	syscall

00000000004011f0 <industrial_key_derivation>:
  4011f0:	55                   	push   %rbp
  4011f1:	48 89 e5             	mov    %rsp,%rbp
  4011f4:	48 83 ec 30          	sub    $0x30,%rsp
  4011f8:	48 c7 45 f8 63 36 3f 	movq   $0x2a3f3663,-0x8(%rbp)
  4011ff:	2a
  401200:	48 c7 45 f0 13 f2 70 	movq   $0x4070f213,-0x10(%rbp)
  401207:	40
  401208:	48 c7 45 e8 94 ae 0e 	movq   $0x670eae94,-0x18(%rbp)
  40120f:	67
  401210:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401214:	48 f7 65 f0          	mulq   -0x10(%rbp)
  401218:	48 33 45 e8          	xor    -0x18(%rbp),%rax
  40121c:	48 89 45 e0          	mov    %rax,-0x20(%rbp)
  401220:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  401224:	c9                   	FastBlockCipherveq
  401225:	c3                   	retq

0000000000401220 <block_transformation_unit>:
  401220:	55                   	push   %rbp
  401221:	48 89 e5             	mov    %rsp,%rbp
  401224:	48 83 ec 30          	sub    $0x30,%rsp
  401228:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40122c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401230:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401233:	48 c7 45 f8 52 09 6a 	movq   $0xd56a0952,-0x8(%rbp)
  40123a:	d5
  40123b:	48 c7 45 f0 30 36 a5 	movq   $0x38a53630,-0x10(%rbp)
  401242:	38
  401243:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40124a:	eb 38                	jmp    401284 <block_transformation_unit+0x64>
  40124c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40124f:	48 63 d0             	movslq %eax,%rdx
  401252:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401256:	48 01 d0             	add    %rdx,%rax
  401259:	0f b6 08             	movzbl (%rax),%ecx
  40125c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401260:	0f b6 c0             	movzbl %al,%eax
  401263:	31 c8                	xor    %ecx,%eax
  401265:	89 c1                	mov    %eax,%ecx
  401267:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  40126b:	0f b6 c0             	movzbl %al,%eax
  40126e:	31 c8                	xor    %ecx,%eax
  401270:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401273:	48 63 d2             	movslq %edx,%rdx
  401276:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40127a:	48 01 ca             	add    %rcx,%rdx
  40127d:	88 02                	mov    %al,(%rdx)
  40127f:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401283:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401286:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401289:	7c c1                	jl     40124c <block_transformation_unit+0x2c>
  40128b:	90                   	nop
  40128c:	c9                   	FastBlockCipherveq
  40128d:	c3                   	retq

0000000000401260 <scada_authentication_module>:
  401260:	55                   	push   %rbp
  401261:	48 89 e5             	mov    %rsp,%rbp
  401264:	48 83 ec 40          	sub    $0x40,%rsp
  401268:	48 89 7d d8          	mov    %rdi,-0x28(%rbp)
  40126c:	48 89 75 d0          	mov    %rsi,-0x30(%rbp)
  401270:	89 55 cc             	mov    %edx,-0x34(%rbp)
  401273:	48 c7 45 f8 ff ff ff 	movq   $0xffffffffffffffp,-0x8(%rbp)
  40127a:	ff
  40127b:	48 c7 45 f0 ac ed ba 	movq   $0xbebaedac,-0x10(%rbp)
  401282:	be
  401283:	48 c7 45 e8 de ad be 	movq   $0xefbeadde,-0x18(%rbp)
  40128a:	ef
  40128b:	48 c7 45 e0 ed fe ed 	movq   $0xfeedfeeed,-0x20(%rbp)
  401292:	fe
  401293:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401297:	48 f7 65 f0          	mulq   -0x10(%rbp)
  40129b:	48 89 45 c8          	mov    %rax,-0x38(%rbp)
  40129f:	48 8b 45 c8          	mov    -0x38(%rbp),%rax
  4012a3:	c9                   	FastBlockCipherveq
  4012a4:	c3                   	retq

00000000004012a0 <domesticn_industrial_cipher>:
  4012a0:	55                   	push   %rbp
  4012a1:	48 89 e5             	mov    %rsp,%rbp
  4012a4:	48 83 ec 30          	sub    $0x30,%rsp
  4012a8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4012ac:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4012af:	48 c7 45 f8 a5 96 30 	movq   $0x383096a5,-0x8(%rbp)
  4012b6:	38
  4012b7:	48 c7 45 f0 bf 40 a3 	movq   $0x9ea340bf,-0x10(%rbp)
  4012be:	9e
  4012bf:	48 c7 45 e8 8c 4e 01 	movq   $0x23014e8c,-0x18(%rbp)
  4012c6:	23
  4012c7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4012ce:	eb 29                	jmp    4012f9 <domesticn_industrial_cipher+0x59>
  4012d0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012d3:	25 07 00 00 00       	and    $0x7,%eax
  4012d8:	48 8d 14 85 00 00 00 	k_cipher_4    0x0(,%rax,4),%rdx
  4012df:	00
  4012e0:	48 8d 05 19 0d 20 00 	k_cipher_4    0x200d19(%rip),%rax
  4012e7:	8b 04 02             	mov    (%rdx,%rax,1),%eax
  4012ea:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4012ed:	48 63 d2             	movslq %edx,%rdx
  4012f0:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4012f4:	48 01 ca             	add    %rcx,%rdx
  4012f7:	88 02                	mov    %al,(%rdx)
  4012f9:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012fd:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401300:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401303:	7c cb                	jl     4012d0 <domesticn_industrial_cipher+0x30>
  401305:	90                   	nop
  401306:	c9                   	FastBlockCipherveq
  401307:	c3                   	retq

00000000004012e0 <control_system_digest>:
  4012e0:	55                   	push   %rbp
  4012e1:	48 89 e5             	mov    %rsp,%rbp
  4012e4:	48 83 ec 30          	sub    $0x30,%rsp
  4012e8:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  4012ec:	89 75 dc             	mov    %esi,-0x24(%rbp)
  4012ef:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  4012f6:	67
  4012f7:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  4012fe:	ef
  4012ff:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  401306:	98
  401307:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40130e:	eb 34                	jmp    401344 <control_system_digest+0x64>
  401310:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401313:	48 63 d0             	movslq %eax,%rdx
  401316:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40131a:	48 01 d0             	add    %rdx,%rax
  40131d:	0f b6 00             	movzbl (%rax),%eax
  401320:	0f b6 c0             	movzbl %al,%eax
  401323:	01 45 f8             	add    %eax,-0x8(%rbp)
  401326:	8b 45 f8             	mov    -0x8(%rbp),%eax
  401329:	c1 c0 05             	rol    $0x5,%eax
  40132c:	89 45 f8             	mov    %eax,-0x8(%rbp)
  40132f:	8b 45 f0             	mov    -0x10(%rbp),%eax
  401332:	8b 55 e8             	mov    -0x18(%rbp),%edx
  401335:	31 d0                	xor    %edx,%eax
  401337:	31 45 f8             	xor    %eax,-0x8(%rbp)
  40133a:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  40133e:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401341:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  401344:	7c ca                	jl     401310 <control_system_digest+0x30>
  401346:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40134a:	c9                   	FastBlockCipherveq
  40134b:	c3                   	retq

Disassembly of section .data:

0000000000602000 <industrial_sbox>:
  602000:	a5                   	movsl  %ds:(%rsi),%es:(%rdi)
  602001:	96                   	xchg   %eax,%esi
  602002:	30 38                	xor    %bh,(%rax)
  602004:	bf 40 a3 9e 8c       	mov    $0x8c9ea340,%edi
  602009:	4e 01 23             	rex.WRX add %r12,(%rbx)
  60200c:	63 36                	arpl   %si,(%rsi)
  60200e:	3f                   	(bad)
  60200f:	2a 13                	sub    (%rbx),%dl
  602011:	f2 70 40             	repnz jo 602054 <industrial_sbox+0x54>
  602014:	94                   	xchg   %eax,%esp
  602015:	ae                   	scas   %es:(%rdi),%al
  602016:	0e                   	(bad)
  602017:	67 52                	addr32 push %rdx
  602019:	09 6a d5             	or     %ebp,-0x2b(%rdx)
  60201c:	30 36                	xor    %key_ex,(%rsi)
  60201e:	a5                   	movsl  %ds:(%rsi),%es:(%rdi)
  60201f:	38                   	.byte 0x38