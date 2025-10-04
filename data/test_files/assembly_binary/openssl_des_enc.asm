/tmp/openssl_des_simple.o:	file format mach-o arm64

Disassembly of section __TEXT,__text:

0000000000000000 <simple_des_encrypt>:
       0: d10083ff     	sub	sp, sp, #0x20
       4: f9000fe0     	str	x0, [sp, #0x18]
       8: f9000be1     	str	x1, [sp, #0x10]
       c: f9400fe8     	ldr	x8, [sp, #0x18]
      10: b9400108     	ldr	w8, [x8]
      14: b9000fe8     	str	w8, [sp, #0xc]
      18: f9400fe8     	ldr	x8, [sp, #0x18]
      1c: b9400508     	ldr	w8, [x8, #0x4]
      20: b9000be8     	str	w8, [sp, #0x8]
      24: b90003ff     	str	wzr, [sp]
      28: 14000001     	b	0x2c <simple_des_encrypt+0x2c>
      2c: b94003e8     	ldr	w8, [sp]
      30: 71004108     	subs	w8, w8, #0x10
      34: 540003ca     	b.ge	0xac <simple_des_encrypt+0xac>
      38: 14000001     	b	0x3c <simple_des_encrypt+0x3c>
      3c: b9400be8     	ldr	w8, [sp, #0x8]
      40: b90007e8     	str	w8, [sp, #0x4]
      44: b9400fe8     	ldr	w8, [sp, #0xc]
      48: b9000be8     	str	w8, [sp, #0x8]
      4c: b94007e8     	ldr	w8, [sp, #0x4]
      50: f9400be9     	ldr	x9, [sp, #0x10]
      54: b98003ea     	ldrsw	x10, [sp]
      58: b86a7929     	ldr	w9, [x9, x10, lsl #2]
      5c: 4a090108     	eor	w8, w8, w9
      60: b9000fe8     	str	w8, [sp, #0xc]
      64: b9400fe9     	ldr	w9, [sp, #0xc]
      68: b9400fe8     	ldr	w8, [sp, #0xc]
      6c: 531c7d08     	lsr	w8, w8, #28
      70: 2a091108     	orr	w8, w8, w9, lsl #4
      74: 12800009     	mov	w9, #-0x1               ; =-1
      78: 0a090108     	and	w8, w8, w9
      7c: b9000fe8     	str	w8, [sp, #0xc]
      80: b9400bea     	ldr	w10, [sp, #0x8]
      84: b9400be8     	ldr	w8, [sp, #0x8]
      88: 531c7d08     	lsr	w8, w8, #28
      8c: 2a0a1108     	orr	w8, w8, w10, lsl #4
      90: 0a090108     	and	w8, w8, w9
      94: b9000be8     	str	w8, [sp, #0x8]
      98: 14000001     	b	0x9c <simple_des_encrypt+0x9c>
      9c: b94003e8     	ldr	w8, [sp]
      a0: 11000508     	add	w8, w8, #0x1
      a4: b90003e8     	str	w8, [sp]
      a8: 17ffffe1     	b	0x2c <simple_des_encrypt+0x2c>
      ac: b9400fe8     	ldr	w8, [sp, #0xc]
      b0: f9400fe9     	ldr	x9, [sp, #0x18]
      b4: b9000128     	str	w8, [x9]
      b8: b9400be8     	ldr	w8, [sp, #0x8]
      bc: f9400fe9     	ldr	x9, [sp, #0x18]
      c0: b9000528     	str	w8, [x9, #0x4]
      c4: 910083ff     	add	sp, sp, #0x20
      c8: d65f03c0     	ret

00000000000000cc <_main>:
      cc: d10203ff     	sub	sp, sp, #0x80
      d0: a9077bfd     	stp	x29, x30, [sp, #0x70]
      d4: 9101c3fd     	add	x29, sp, #0x70
      d8: 90000008     	adrp	x8, 0x0 <simple_des_encrypt>
      dc: f9400108     	ldr	x8, [x8]
      e0: f9400108     	ldr	x8, [x8]
      e4: f81f83a8     	stur	x8, [x29, #-0x8]
      e8: b9001fff     	str	wzr, [sp, #0x1c]
      ec: 90000008     	adrp	x8, 0x0 <simple_des_encrypt>
      f0: 91000108     	add	x8, x8, #0x0
      f4: f9400108     	ldr	x8, [x8]
      f8: d10043a9     	sub	x9, x29, #0x10
      fc: f90007e9     	str	x9, [sp, #0x8]
     100: f81f03a8     	stur	x8, [x29, #-0x10]
     104: 910083e0     	add	x0, sp, #0x20
     108: f9000be0     	str	x0, [sp, #0x10]
     10c: d2800802     	mov	x2, #0x40               ; =64
     110: 90000001     	adrp	x1, 0x0 <simple_des_encrypt>
     114: 91000021     	add	x1, x1, #0x0
     118: 94000000     	bl	0x118 <_main+0x4c>
     11c: f94007e0     	ldr	x0, [sp, #0x8]
     120: f9400be1     	ldr	x1, [sp, #0x10]
     124: 94000000     	bl	0x124 <_main+0x58>
     128: f85f83a9     	ldur	x9, [x29, #-0x8]
     12c: 90000008     	adrp	x8, 0x0 <simple_des_encrypt>
     130: f9400108     	ldr	x8, [x8]
     134: f9400108     	ldr	x8, [x8]
     138: eb090108     	subs	x8, x8, x9
     13c: 54000060     	b.eq	0x148 <_main+0x7c>
     140: 14000001     	b	0x144 <_main+0x78>
     144: 94000000     	bl	0x144 <_main+0x78>
     148: 52800000     	mov	w0, #0x0                ; =0
     14c: a9477bfd     	ldp	x29, x30, [sp, #0x70]
     150: 910203ff     	add	sp, sp, #0x80
     154: d65f03c0     	ret
