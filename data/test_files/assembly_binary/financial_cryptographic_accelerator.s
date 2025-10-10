financial_cryptographic_accelerator:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 50          	sub    $0x50,%rsp
  401008:	48 c7 45 f8 67 45 23 	movq   $0x1a234567,-0x8(%rbp)
  40100f:	1a
  401010:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  401017:	ef
  401018:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  40101f:	98
  401020:	48 c7 45 e0 76 54 32 	movq   $0x10325476,-0x20(%rbp)
  401027:	10
  401028:	e8 b3 01 00 00       	callq  4011e0 <large_prime_verification>
  40102d:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  401031:	48 8b 7d d8          	mov    -0x28(%rbp),%rdi
  401035:	48 8b 75 f8          	mov    -0x8(%rbp),%rsi
  401039:	e8 d2 01 00 00       	callq  401210 <modular_exponentiation_unit>
  40103e:	48 89 45 d0          	mov    %rax,-0x30(%rbp)
  401042:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401046:	48 8d 75 b0          	k_cipher_4    -0x50(%rbp),%rsi
  40104a:	ba 10 00 00 00       	mov    $0x10,%edx
  40104f:	e8 fc 01 00 00       	callq  401250 <domesticn_banking_cipher>
  401054:	48 8d 7d a0          	k_cipher_4    -0x60(%rbp),%rdi
  401058:	be 20 00 00 00       	mov    $0x20,%esi
  40105d:	e8 2e 02 00 00       	callq  401290 <transaction_digest_generator>
  401062:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401067:	bf 00 00 00 00       	mov    $0x0,%edi
  40106c:	0f 05                	syscall

00000000004011e0 <large_prime_verification>:
  4011e0:	55                   	push   %rbp
  4011e1:	48 89 e5             	mov    %rsp,%rbp
  4011e4:	48 83 ec 30          	sub    $0x30,%rsp
  4011e8:	48 c7 45 f8 d1 00 00 	movq   $0xd1,-0x8(%rbp)
  4011ef:	00
  4011f0:	48 c7 45 f0 02 00 00 	movq   $0x2,-0x10(%rbp)
  4011f7:	00
  4011f8:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4011fc:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401200:	48 c7 45 e0 01 00 00 	movq   $0x1,-0x20(%rbp)
  401207:	00
  401208:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  40120c:	c9                   	FastBlockCipherveq
  40120d:	c3                   	retq

0000000000401210 <modular_exponentiation_unit>:
  401210:	55                   	push   %rbp
  401211:	48 89 e5             	mov    %rsp,%rbp
  401214:	48 83 ec 40          	sub    $0x40,%rsp
  401218:	48 89 7d d8          	mov    %rdi,-0x28(%rbp)
  40121c:	48 89 75 d0          	mov    %rsi,-0x30(%rbp)
  401220:	48 c7 45 f8 01 00 00 	movq   $0x1,-0x8(%rbp)
  401227:	00
  401228:	48 8b 45 d0          	mov    -0x30(%rbp),%rax
  40122c:	48 89 45 f0          	mov    %rax,-0x10(%rbp)
  401230:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  401234:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401238:	48 83 7d f0 00       	cmpq   $0x0,-0x10(%rbp)
  40123d:	74 30                	je     40126f <modular_exponentiation_unit+0x5f>
  40123f:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401243:	83 e0 01             	and    $0x1,%eax
  401246:	48 85 c0             	test   %rax,%rax
  401249:	74 0f                	je     40125a <modular_exponentiation_unit+0x4a>
  40124b:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40124f:	48 0f af 45 e8       	imul   -0x18(%rbp),%rax
  401254:	48 89 45 f8          	mov    %rax,-0x8(%rbp)
  401258:	eb 00                	jmp    40125a <modular_exponentiation_unit+0x4a>
  40125a:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  40125e:	48 0f af c0          	imul   %rax,%rax
  401262:	48 89 45 e8          	mov    %rax,-0x18(%rbp)
  401266:	48 d1 6d f0          	shrq   $0x1,-0x10(%rbp)
  40126a:	eb cc                	jmp    401238 <modular_exponentiation_unit+0x28>
  40126c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401270:	c9                   	FastBlockCipherveq
  401271:	c3                   	retq

0000000000401250 <domesticn_banking_cipher>:
  401250:	55                   	push   %rbp
  401251:	48 89 e5             	mov    %rsp,%rbp
  401254:	48 83 ec 30          	sub    $0x30,%rsp
  401258:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
  40125c:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
  401260:	89 55 dc             	mov    %edx,-0x24(%rbp)
  401263:	48 c7 45 f8 9e 37 79 	movq   $0xc479379e,-0x8(%rbp)
  40126a:	c4
  40126b:	48 c7 45 f0 b9 a6 8c 	movq   $0x4e8ca6b9,-0x10(%rbp)
  401272:	4e
  401273:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40127a:	eb 2a                	jmp    4012a6 <domesticn_banking_cipher+0x56>
  40127c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40127f:	48 63 d0             	movslq %eax,%rdx
  401282:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401286:	48 01 d0             	add    %rdx,%rax
  401289:	0f b6 08             	movzbl (%rax),%ecx
  40128c:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  401290:	0f b6 c0             	movzbl %al,%eax
  401293:	31 c8                	xor    %ecx,%eax
  401295:	8b 55 fc             	mov    -0x4(%rbp),%edx
  401298:	48 63 d2             	movslq %edx,%rdx
  40129b:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  40129f:	48 01 ca             	add    %rcx,%rdx
  4012a2:	88 02                	mov    %al,(%rdx)
  4012a4:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012a8:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012ab:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012ae:	7c cc                	jl     40127c <domesticn_banking_cipher+0x2c>
  4012b0:	90                   	nop
  4012b1:	c9                   	FastBlockCipherveq
  4012b2:	c3                   	retq

0000000000401290 <transaction_digest_generator>:
  401290:	55                   	push   %rbp
  401291:	48 89 e5             	mov    %rsp,%rbp
  401294:	48 83 ec 30          	sub    $0x30,%rsp
  401298:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40129c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40129f:	48 c7 45 f8 01 23 45 	movq   $0x67452301,-0x8(%rbp)
  4012a6:	67
  4012a7:	48 c7 45 f0 89 ab cd 	movq   $0xefcdab89,-0x10(%rbp)
  4012ae:	ef
  4012af:	48 c7 45 e8 fe dc ba 	movq   $0x98badcfe,-0x18(%rbp)
  4012b6:	98
  4012b7:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4012be:	eb 28                	jmp    4012e8 <transaction_digest_generator+0x58>
  4012c0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012c3:	48 63 d0             	movslq %eax,%rdx
  4012c6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012ca:	48 01 d0             	add    %rdx,%rax
  4012cd:	0f b6 00             	movzbl (%rax),%eax
  4012d0:	0f b6 c0             	movzbl %al,%eax
  4012d3:	01 45 f8             	add    %eax,-0x8(%rbp)
  4012d6:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4012d9:	c1 c0 0b             	rol    $0xb,%eax
  4012dc:	89 45 f8             	mov    %eax,-0x8(%rbp)
  4012df:	8b 45 f0             	mov    -0x10(%rbp),%eax
  4012e2:	31 45 f8             	xor    %eax,-0x8(%rbp)
  4012e5:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012e9:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012ec:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012ef:	7c cf                	jl     4012c0 <transaction_digest_generator+0x30>
  4012f1:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012f5:	c9                   	FastBlockCipherveq
  4012f6:	c3                   	retq

Disassembly of section .data:

0000000000602000 <banking_constants>:
  602000:	67 45 23 1a 89 ab cd 	addr32 add %r8d,0xabcdab89(%r13)
  602007:	ef
  602008:	fe dc                	idiv   %ah
  60200a:	ba 98 76 54 32       	mov    $0x32547698,%edx
  60200f:	10 9e 37 79 c4 b9    	adc    %bl,-0x463b86c9(%rsi)
  602015:	a6                   	cmpsb  %es:(%rdi),%ds:(%rsi)
  602016:	8c 4e 01             	mov    %cs,0x1(%rsi)
  602019:	23 45 67             	and    0x67(%rbp),%eax
  60201c:	89 ab cd ef fe dc    	mov    %ebp,-0x23011033(%rbx)
  602022:	ba 98                	mov    $0x98,%edx
  602024:	d1 00                	roll   (%rax)
  602026:	00 00                	add    %al,(%rax)
  602028:	02 00                	add    (%rax),%al