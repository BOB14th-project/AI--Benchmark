secure_matrix_transformation_unit:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:	55                   	push   %rbp
  401001:	48 89 e5             	mov    %rsp,%rbp
  401004:	48 83 ec 60          	sub    $0x60,%rsp
  401008:	48 c7 45 f8 63 7c 77 	movq   $0x7b777c63,-0x8(%rbp)
  40100f:	7b
  401010:	48 c7 45 f0 f2 6b 6f 	movq   $0xc56f6bf2,-0x10(%rbp)
  401017:	c5
  401018:	48 c7 45 e8 30 01 67 	movq   $0x2b670130,-0x18(%rbp)
  40101f:	2b
  401020:	48 c7 45 e0 fe d7 ab 	movq   $0x76abd7fe,-0x20(%rbp)
  401027:	76
  401028:	e8 43 01 00 00       	callq  401170 <matrix_state_initialization>
  40102d:	48 8d 7d d0          	k_cipher_4    -0x30(%rbp),%rdi
  401031:	48 8d 75 c0          	k_cipher_4    -0x40(%rbp),%rsi
  401035:	ba 10 00 00 00       	mov    $0x10,%edx
  40103a:	e8 71 01 00 00       	callq  4011b0 <block_substitution_layer>
  40103f:	48 8d 7d c0          	k_cipher_4    -0x40(%rbp),%rdi
  401043:	ba 04 00 00 00       	mov    $0x4,%edx
  401048:	e8 a3 01 00 00       	callq  4011f0 <linear_permutation_layer>
  40104d:	48 8d 7d b0          	k_cipher_4    -0x50(%rbp),%rdi
  401051:	48 8d 75 a0          	k_cipher_4    -0x60(%rbp),%rsi
  401055:	ba 10 00 00 00       	mov    $0x10,%edx
  40105a:	e8 d1 01 00 00       	callq  401230 <key_addition_layer>
  40105f:	48 8d 7d a0          	k_cipher_4    -0x60(%rbp),%rdi
  401063:	be 04 00 00 00       	mov    $0x4,%esi
  401068:	e8 03 02 00 00       	callq  401270 <column_mixing_transformation>
  40106d:	b8 3c 00 00 00       	mov    $0x3c,%eax
  401072:	bf 00 00 00 00       	mov    $0x0,%edi
  401077:	0f 05                	syscall

0000000000401170 <matrix_state_initialization>:
  401170:	55                   	push   %rbp
  401171:	48 89 e5             	mov    %rsp,%rbp
  401174:	48 83 ec 30          	sub    $0x30,%rsp
  401178:	48 c7 45 f8 52 09 6a 	movq   $0xd56a0952,-0x8(%rbp)
  40117f:	d5
  401180:	48 c7 45 f0 30 36 a5 	movq   $0x38a53630,-0x10(%rbp)
  401187:	38
  401188:	48 c7 45 e8 bf 40 a3 	movq   $0x9ea340bf,-0x18(%rbp)
  40118f:	9e
  401190:	48 c7 45 e0 81 f3 d7 	movq   $0xfbd7f381,-0x20(%rbp)
  401197:	fb
  401198:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  40119c:	48 33 45 f0          	xor    -0x10(%rbp),%rax
  4011a0:	48 89 45 d8          	mov    %rax,-0x28(%rbp)
  4011a4:	48 8b 45 d8          	mov    -0x28(%rbp),%rax
  4011a8:	c9                   	leaveq
  4011a9:	c3                   	retq

00000000004011b0 <block_substitution_layer>:
  4011b0:	55                   	push   %rbp
  4011b1:	48 89 e5             	mov    %rsp,%rbp
  4011b4:	48 83 ec 20          	sub    $0x20,%rsp
  4011b8:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  4011bc:	48 89 75 e8          	mov    %rsi,-0x18(%rbp)
  4011c0:	89 55 e4             	mov    %edx,-0x1c(%rbp)
  4011c3:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  4011ca:	eb 3e                	jmp    40120a <block_substitution_layer+0x5a>
  4011cc:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4011cf:	48 63 d0             	movslq %eax,%rdx
  4011d2:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  4011d6:	48 01 d0             	add    %rdx,%rax
  4011d9:	0f b6 00             	movzbl (%rax),%eax
  4011dc:	0f b6 c0             	movzbl %al,%eax
  4011df:	48 8d 14 85 00 00 00 	k_cipher_4    0x0(,%rax,4),%rdx
  4011e6:	00
  4011e7:	48 8d 05 12 0e 20 00 	k_cipher_4    0x200e12(%rip),%rax        # 602000 <transformation_sbox>
  4011ee:	8b 04 02             	mov    (%rdx,%rax,1),%eax
  4011f1:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4011f4:	48 63 d2             	movslq %edx,%rdx
  4011f7:	48 8b 4d e8          	mov    -0x18(%rbp),%rcx
  4011fb:	48 01 ca             	add    %rcx,%rdx
  4011fe:	88 02                	mov    %al,(%rdx)
  401200:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401204:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401207:	3b 45 e4             	cmp    -0x1c(%rbp),%eax
  40120a:	7c c0                	jl     4011cc <block_substitution_layer+0x1c>
  40120c:	90                   	nop
  40120d:	c9                   	leaveq
  40120e:	c3                   	retq

00000000004011f0 <linear_permutation_layer>:
  4011f0:	55                   	push   %rbp
  4011f1:	48 89 e5             	mov    %rsp,%rbp
  4011f4:	48 83 ec 20          	sub    $0x20,%rsp
  4011f8:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  4011fc:	89 55 ec             	mov    %edx,-0x14(%rbp)
  4011ff:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  401206:	c7 45 f8 00 00 00 00 	movl   $0x0,-0x8(%rbp)
  40120d:	eb 4a                	jmp    401259 <linear_permutation_layer+0x69>
  40120f:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  401216:	eb 32                	jmp    40124a <linear_permutation_layer+0x5a>
  401218:	8b 45 f8             	mov    -0x8(%rbp),%eax
  40121b:	c1 e0 02             	shl    $0x2,%eax
  40121e:	89 c2                	mov    %eax,%edx
  401220:	03 55 fc             	add    -0x4(%rbp),%edx
  401223:	48 63 d2             	movslq %edx,%rdx
  401226:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  40122a:	48 01 d0             	add    %rdx,%rax
  40122d:	0f b6 08             	movzbl (%rax),%ecx
  401230:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401233:	c1 e0 02             	shl    $0x2,%eax
  401236:	89 c2                	mov    %eax,%edx
  401238:	03 55 f8             	add    -0x8(%rbp),%edx
  40123b:	48 63 d2             	movslq %edx,%rdx
  40123e:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401242:	48 01 d0             	add    %rdx,%rax
  401245:	88 08                	mov    %cl,(%rax)
  401247:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  40124b:	83 7d fc 03          	cmpl   $0x3,-0x4(%rbp)
  40124f:	7e c7                	jle    401218 <linear_permutation_layer+0x28>
  401251:	83 45 f8 01          	addl   $0x1,-0x8(%rbp)
  401255:	83 7d f8 03          	cmpl   $0x3,-0x8(%rbp)
  401259:	7e b4                	jle    40120f <linear_permutation_layer+0x1f>
  40125b:	90                   	nop
  40125c:	c9                   	leaveq
  40125d:	c3                   	retq

0000000000401230 <key_addition_layer>:
  401230:	55                   	push   %rbp
  401231:	48 89 e5             	mov    %rsp,%rbp
  401234:	48 83 ec 20          	sub    $0x20,%rsp
  401238:	48 89 7d f0          	mov    %rdi,-0x10(%rbp)
  40123c:	48 89 75 e8          	mov    %rsi,-0x18(%rbp)
  401240:	89 55 e4             	mov    %edx,-0x1c(%rbp)
  401243:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40124a:	eb 2a                	jmp    401276 <key_addition_layer+0x46>
  40124c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40124f:	48 63 d0             	movslq %eax,%rdx
  401252:	48 8b 45 f0          	mov    -0x10(%rbp),%rax
  401256:	48 01 d0             	add    %rdx,%rax
  401259:	0f b6 08             	movzbl (%rax),%ecx
  40125c:	8b 45 fc             	mov    -0x4(%rbp),%eax
  40125f:	48 63 d0             	movslq %eax,%rdx
  401262:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  401266:	48 01 d0             	add    %rdx,%rax
  401269:	0f b6 00             	movzbl (%rax),%eax
  40126c:	31 c8                	xor    %ecx,%eax
  40126e:	88 02                	mov    %al,(%rdx)
  401270:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  401274:	eb 00                	jmp    401276 <key_addition_layer+0x46>
  401276:	8b 45 fc             	mov    -0x4(%rbp),%eax
  401279:	3b 45 e4             	cmp    -0x1c(%rbp),%eax
  40127c:	7c ce                	jl     40124c <key_addition_layer+0x1c>
  40127e:	90                   	nop
  40127f:	c9                   	leaveq
  401280:	c3                   	retq

0000000000401270 <column_mixing_transformation>:
  401270:	55                   	push   %rbp
  401271:	48 89 e5             	mov    %rsp,%rbp
  401274:	48 83 ec 30          	sub    $0x30,%rsp
  401278:	48 89 7d e0          	mov    %rdi,-0x20(%rbp)
  40127c:	89 75 dc             	mov    %esi,-0x24(%rbp)
  40127f:	48 c7 45 f8 02 03 01 	movq   $0x1010302,-0x8(%rbp)
  401286:	01
  401287:	48 c7 45 f0 01 02 03 	movq   $0x1030201,-0x10(%rbp)
  40128e:	01
  40128f:	48 c7 45 e8 01 01 02 	movq   $0x3020101,-0x18(%rbp)
  401296:	03
  401297:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  40129e:	eb 32                	jmp    4012d2 <column_mixing_transformation+0x62>
  4012a0:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012a3:	48 63 d0             	movslq %eax,%rdx
  4012a6:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  4012aa:	48 01 d0             	add    %rdx,%rax
  4012ad:	0f b6 08             	movzbl (%rax),%ecx
  4012b0:	48 8b 45 f8          	mov    -0x8(%rbp),%rax
  4012b4:	0f b6 c0             	movzbl %al,%eax
  4012b7:	0f af c1             	imul   %ecx,%eax
  4012ba:	25 ff 00 00 00       	and    $0xff,%eax
  4012bf:	8b 55 fc             	mov    -0x4(%rbp),%edx
  4012c2:	48 63 d2             	movslq %edx,%rdx
  4012c5:	48 8b 4d e0          	mov    -0x20(%rbp),%rcx
  4012c9:	48 01 ca             	add    %rcx,%rdx
  4012cc:	88 02                	mov    %al,(%rdx)
  4012ce:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  4012d2:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4012d5:	3b 45 dc             	cmp    -0x24(%rbp),%eax
  4012d8:	7c c6                	jl     4012a0 <column_mixing_transformation+0x30>
  4012da:	90                   	nop
  4012db:	c9                   	leaveq
  4012dc:	c3                   	retq

Disassembly of section .data:

0000000000602000 <transformation_sbox>:
  602000:	63 7c 77 7b 	arpl   %di,0x7b(%rax,%rsi,2)
  602004:	f2 6b 6f c5 	repnz imul $0xffffffc5,%edi,%ebp
  602008:	30 01                	xor    %al,(%rcx)
  60200a:	67 2b fe             	addr32 sub %esi,%edi
  60200d:	d7                   	xlat   %ds:(%rbx)
  60200e:	ab                   	stos   %eax,%es:(%rdi)
  60200f:	76 ca                	jbe    601fdb <transformation_sbox-0x25>
  602011:	82 c9 7d             	or     $0x7d,%cl
  602014:	fa                   	cli
  602015:	59                   	pop    %rcx
  602016:	47 f0 ad             	rex.RXB lock lods %ds:(%rsi),%eax