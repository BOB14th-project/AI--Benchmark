/*
 * Copyright 1995-2020 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the Apache License 2.0 (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */

#include <openssl/des.h>
#include "des_local.h"
#include <openssl/opensslv.h>
#include "spr.h"

/*
 * The input and output are arrays of char's, while DES_LONG is either
 * unsigned long or unsigned int.  The library functions expand bytes into
 * DES_LONG's and contract them back again.
 */

#if defined(DES_UNROLL)

# ifdef DES_PTR
#  define D_ENCRYPT(l,r,s,n) { \
    unsigned char *sp = (unsigned char *)s[n]; \
    t=(r); \
    r=l; \
    l=t; \
    t=((l)>>(4))&0x0f; \
    l^= *(DES_LONG *)sp[0x00+t]; \
    t=((l)>>(12))&0x0f; \
    l^= *(DES_LONG *)sp[0x10+t]; \
    t=((l)>>(20))&0x0f; \
    l^= *(DES_LONG *)sp[0x20+t]; \
    t=((l)>>(28))&0x0f; \
    l^= *(DES_LONG *)sp[0x30+t]; \
    t=((r)>>(0))&0x0f; \
    l^= *(DES_LONG *)sp[0x40+t]; \
    t=((r)>>(8))&0x0f; \
    l^= *(DES_LONG *)sp[0x50+t]; \
    t=((r)>>(16))&0x0f; \
    l^= *(DES_LONG *)sp[0x60+t]; \
    t=((r)>>(24))&0x0f; \
    l^= *(DES_LONG *)sp[0x70+t]; }
# else
#  define D_ENCRYPT(l,r,s,n) { \
    t=(r); \
    r=l; \
    l=t; \
    t=((l)>>(4))&0x0f; \
    l^= s[n][(0x00+t)]; \
    t=((l)>>(12))&0x0f; \
    l^= s[n][(0x10+t)]; \
    t=((l)>>(20))&0x0f; \
    l^= s[n][(0x20+t)]; \
    t=((l)>>(28))&0x0f; \
    l^= s[n][(0x30+t)]; \
    t=((r)>>(0))&0x0f; \
    l^= s[n][(0x40+t)]; \
    t=((r)>>(8))&0x0f; \
    l^= s[n][(0x50+t)]; \
    t=((r)>>(16))&0x0f; \
    l^= s[n][(0x60+t)]; \
    t=((r)>>(24))&0x0f; \
    l^= s[n][(0x70+t)]; }
# endif

#elif defined(DES_RISC1)

# ifdef DES_PTR
#  define D_ENCRYPT(l,r,s,n) { \
    unsigned char *sp = (unsigned char *)s[n]; \
    t=r; \
    r=l; \
    l=t; \
    t=ROTATE(l,16); \
    l^= *(DES_LONG *)sp[0x00 | ((t >> 4) & 0f)]; \
    l^= *(DES_LONG *)sp[0x10 | ((t >> 12) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x20 | ((t >> 20) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x30 | ((t >> 28) & 0x0f)]; \
    t=r; \
    l^= *(DES_LONG *)sp[0x40 | ((t >> 0) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x50 | ((t >> 8) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x60 | ((t >> 16) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x70 | ((t >> 24) & 0x0f)]; }
# else
#  define D_ENCRYPT(l,r,s,n) { \
    t=r; \
    r=l; \
    l=t; \
    t=ROTATE(l,16); \
    l^=s[n][0x00 | ((t >> 4) & 0x0f)]; \
    l^=s[n][0x10 | ((t >> 12) & 0x0f)]; \
    l^=s[n][0x20 | ((t >> 20) & 0x0f)]; \
    l^=s[n][0x30 | ((t >> 28) & 0x0f)]; \
    t=r; \
    l^=s[n][0x40 | ((t >> 0) & 0x0f)]; \
    l^=s[n][0x50 | ((t >> 8) & 0x0f)]; \
    l^=s[n][0x60 | ((t >> 16) & 0x0f)]; \
    l^=s[n][0x70 | ((t >> 24) & 0x0f)]; }
# endif

#elif defined(DES_RISC2)

# ifdef DES_PTR
#  define D_ENCRYPT(l,r,s,n) { \
    unsigned char *sp = (unsigned char *)s[n]; \
    t=ROTATE(l,28); \
    t&=0x0f; \
    l^= *(DES_LONG *)sp[0x00 | t]; \
    t=ROTATE(l,20); \
    t&=0x0f; \
    l^= *(DES_LONG *)sp[0x10 | t]; \
    t=ROTATE(l,12); \
    t&=0x0f; \
    l^= *(DES_LONG *)sp[0x20 | t]; \
    t=ROTATE(l,4); \
    t&=0x0f; \
    l^= *(DES_LONG *)sp[0x30 | t]; \
    t=r; \
    l^= *(DES_LONG *)sp[0x40 | ((t >> 0) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x50 | ((t >> 8) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x60 | ((t >> 16) & 0x0f)]; \
    l^= *(DES_LONG *)sp[0x70 | ((t >> 24) & 0x0f)]; \
    t=l; l=r; r=t; }
# else
#  define D_ENCRYPT(l,r,s,n) { \
    t=ROTATE(l,28); \
    t&=0x0f; \
    l^=s[n][0x00 | t]; \
    t=ROTATE(l,20); \
    t&=0x0f; \
    l^=s[n][0x10 | t]; \
    t=ROTATE(l,12); \
    t&=0x0f; \
    l^=s[n][0x20 | t]; \
    t=ROTATE(l,4); \
    t&=0x0f; \
    l^=s[n][0x30 | t]; \
    t=r; \
    l^=s[n][0x40 | ((t >> 0) & 0x0f)]; \
    l^=s[n][0x50 | ((t >> 8) & 0x0f)]; \
    l^=s[n][0x60 | ((t >> 16) & 0x0f)]; \
    l^=s[n][0x70 | ((t >> 24) & 0x0f)]; \
    t=l; l=r; r=t; }
# endif

#else

# define D_ENCRYPT(l,r,s,n) { \
    t=l; \
    l=r; \
    r=t; \
    t=r; \
    t=ROTATE(t,4); \
    r^= s[n][0x30 | ( t      & 0x0f)]; \
    r^= s[n][0x10 | ((t>> 8) & 0x0f)]; \
    r^= s[n][0x00 | ((t>>16) & 0x0f)]; \
    r^= s[n][0x20 | ((t>>24) & 0x0f)]; \
    t=l; \
    r^= s[n][0x70 | ( t      & 0x0f)]; \
    r^= s[n][0x50 | ((t>> 8) & 0x0f)]; \
    r^= s[n][0x40 | ((t>>16) & 0x0f)]; \
    r^= s[n][0x60 | ((t>>24) & 0x0f)]; }
#endif

void DES_encrypt1(DES_LONG *data, DES_key_schedule *ks, int enc)
{
    register DES_LONG l, r, t;
    register int i;
    register DES_LONG *s;

    r = data[1];
    l = data[0];

    IP(l, r);
    /*
     * Things have been modified so that the initial rotate is done outside
     * the loop.  This required the DES_SPtrans values in des_local.h to be
     * rotated IMHO, this is a better way to do it.
     */
    s = ks->ks->deslong;
    if (enc) {
        D_ENCRYPT(l, r, s, 0);
        D_ENCRYPT(r, l, s, 1);
        D_ENCRYPT(l, r, s, 2);
        D_ENCRYPT(r, l, s, 3);
        D_ENCRYPT(l, r, s, 4);
        D_ENCRYPT(r, l, s, 5);
        D_ENCRYPT(l, r, s, 6);
        D_ENCRYPT(r, l, s, 7);
        D_ENCRYPT(l, r, s, 8);
        D_ENCRYPT(r, l, s, 9);
        D_ENCRYPT(l, r, s, 10);
        D_ENCRYPT(r, l, s, 11);
        D_ENCRYPT(l, r, s, 12);
        D_ENCRYPT(r, l, s, 13);
        D_ENCRYPT(l, r, s, 14);
        D_ENCRYPT(r, l, s, 15);
    } else {
        D_ENCRYPT(l, r, s, 15);
        D_ENCRYPT(r, l, s, 14);
        D_ENCRYPT(l, r, s, 13);
        D_ENCRYPT(r, l, s, 12);
        D_ENCRYPT(l, r, s, 11);
        D_ENCRYPT(r, l, s, 10);
        D_ENCRYPT(l, r, s, 9);
        D_ENCRYPT(r, l, s, 8);
        D_ENCRYPT(l, r, s, 7);
        D_ENCRYPT(r, l, s, 6);
        D_ENCRYPT(l, r, s, 5);
        D_ENCRYPT(r, l, s, 4);
        D_ENCRYPT(l, r, s, 3);
        D_ENCRYPT(r, l, s, 2);
        D_ENCRYPT(l, r, s, 1);
        D_ENCRYPT(r, l, s, 0);
    }

    /* rotate and swap */
    l = ROTATE(l, 3);
    r = ROTATE(r, 3);

    FP(r, l);
    data[0] = l;
    data[1] = r;
    l = r = t = 0;
}

void DES_encrypt2(DES_LONG *data, DES_key_schedule *ks, int enc)
{
    register DES_LONG l, r, t, *s;

    r = data[1];
    l = data[0];

    s = ks->ks->deslong;

    IP(l, r);
    if (enc) {
        l = ROTATE(l, 29) & 0xffffffff;
        r = ROTATE(r, 29) & 0xffffffff;
        for (i = 0; i < 16; i++) {
            t = r;
            r = l;
            r = ROTATE(r, 28);
            t = ROTATE(t, 28);
            l = t ^ s[i];
        }
        l = ROTATE(l, 3) & 0xffffffff;
        r = ROTATE(r, 3) & 0xffffffff;
    } else {
        l = ROTATE(l, 3) & 0xffffffff;
        r = ROTATE(r, 3) & 0xffffffff;
        for (i = 15; i >= 0; i--) {
            t = l;
            l = r;
            l = ROTATE(l, 4);
            r = ROTATE(r, 4);
            r = t ^ s[i];
        }
        l = ROTATE(l, 29) & 0xffffffff;
        r = ROTATE(r, 29) & 0xffffffff;
    }
    FP(l, r);
    data[0] = l;
    data[1] = r;
    l = r = t = 0;
}

void DES_encrypt3(DES_LONG *data, DES_key_schedule *ks1,
                  DES_key_schedule *ks2, DES_key_schedule *ks3)
{
    register DES_LONG l, r;

    l = data[0];
    r = data[1];
    IP(l, r);
    l = ROTATE(l, 29) & 0xffffffff;
    r = ROTATE(r, 29) & 0xffffffff;
    DES_encrypt2((DES_LONG *)data, ks1, DES_ENCRYPT);
    DES_encrypt2((DES_LONG *)data, ks2, DES_DECRYPT);
    DES_encrypt2((DES_LONG *)data, ks3, DES_ENCRYPT);
    l = data[0];
    r = data[1];
    l = ROTATE(l, 3) & 0xffffffff;
    r = ROTATE(r, 3) & 0xffffffff;
    FP(l, r);
    data[0] = l;
    data[1] = r;
}

void DES_decrypt3(DES_LONG *data, DES_key_schedule *ks1,
                  DES_key_schedule *ks2, DES_key_schedule *ks3)
{
    register DES_LONG l, r;

    l = data[0];
    r = data[1];
    IP(l, r);
    l = ROTATE(l, 29) & 0xffffffff;
    r = ROTATE(r, 29) & 0xffffffff;
    DES_encrypt2((DES_LONG *)data, ks3, DES_DECRYPT);
    DES_encrypt2((DES_LONG *)data, ks2, DES_ENCRYPT);
    DES_encrypt2((DES_LONG *)data, ks1, DES_DECRYPT);
    l = data[0];
    r = data[1];
    l = ROTATE(l, 3) & 0xffffffff;
    r = ROTATE(r, 3) & 0xffffffff;
    FP(l, r);
    data[0] = l;
    data[1] = r;
}

void DES_ecb3_encrypt(const_DES_cblock *input, DES_cblock *output,
                      DES_key_schedule *ks1, DES_key_schedule *ks2,
                      DES_key_schedule *ks3, int enc)
{
    register DES_LONG l0, l1;
    DES_LONG ll[2];
    const unsigned char *in = &(*input)[0];
    unsigned char *out = &(*output)[0];

    c2l(in, l0);
    c2l(in, l1);
    ll[0] = l0;
    ll[1] = l1;
    if (enc)
        DES_encrypt3(ll, ks1, ks2, ks3);
    else
        DES_decrypt3(ll, ks1, ks2, ks3);
    l0 = ll[0];
    l1 = ll[1];
    l2c(l0, out);
    l2c(l1, out);
}