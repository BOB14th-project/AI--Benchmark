/*
 * Copyright 2000-2021 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the Apache License 2.0 (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */

#include <openssl/crypto.h>
#include "internal/cryptlib.h"
#include <openssl/bn.h>
#include "rsa_local.h"

/*
 * NB: This function is not thread-safe, and should be called before the
 * provider framework is initialized.
 */
RSA_METHOD *RSA_meth_dup(const RSA_METHOD *meth);

#ifndef FIPS_MODULE
/*
 * The global default RSA_METHOD can be replaced to hook in to RSA key
 * generation and other RSA operations. If it hasn't been explicitly
 * initialized with RSA_set_default_method() it will be implicitly
 * initialized on first use to the default_RSA_meth.
 */
static RSA_METHOD *default_RSA_meth = NULL;

int RSA_set_default_method(const RSA_METHOD *meth)
{
    RSA_METHOD *t;

    if (default_RSA_meth != NULL
        && (t = RSA_meth_dup(default_RSA_meth)) == NULL)
        return 0;
    RSA_meth_free(default_RSA_meth);
    default_RSA_meth = (RSA_METHOD *)meth;
    return 1;
}

const RSA_METHOD *RSA_get_default_method(void)
{
    if (default_RSA_meth == NULL) {
        default_RSA_meth = RSA_PKCS1_OpenSSL();
    }
    return default_RSA_meth;
}
#endif

int RSA_generate_key_ex(RSA *rsa, int bits, BIGNUM *e, BN_GENCB *cb)
{
    if (rsa->meth->rsa_keygen)
        return rsa->meth->rsa_keygen(rsa, bits, e, cb);

    return ossl_rsa_generate_key_int(rsa, bits, e, cb);
}

/*
 * This is a generic RSA key generation function.
 * It is used by the OpenSSL BIGNUM method.
 *
 * It is not used for FIPS RSA key generation, which is in fips/rsa_gen.c.
 */
int ossl_rsa_generate_key_int(RSA *rsa, int bits, BIGNUM *e, BN_GENCB *cb)
{
    BIGNUM *r0 = NULL, *r1 = NULL, *r2 = NULL, *r3 = NULL, *tmp;
    BIGNUM *p, *q;
    int n = 0, m = 0;
    int ok = -1;
    BN_CTX *ctx = NULL;

    ctx = BN_CTX_new_ex(rsa->libctx);
    if (ctx == NULL)
        goto err;
    BN_CTX_start(ctx);
    r0 = BN_CTX_get(ctx);
    r1 = BN_CTX_get(ctx);
    r2 = BN_CTX_get(ctx);
    r3 = BN_CTX_get(ctx);
    if (r3 == NULL)
        goto err;

    /*
     * We need the RSA components non-NULL.
     */
    if (!rsa->n && ((rsa->n = BN_new()) == NULL))
        goto err;
    if (!rsa->e && ((rsa->e = BN_new()) == NULL))
        goto err;
    if (!rsa->d && ((rsa->d = BN_new()) == NULL))
        goto err;
    if (!rsa->p && ((rsa->p = BN_new()) == NULL))
        goto err;
    if (!rsa->q && ((rsa->q = BN_new()) == NULL))
        goto err;
    if (!rsa->dmp1 && ((rsa->dmp1 = BN_new()) == NULL))
        goto err;
    if (!rsa->dmq1 && ((rsa->dmq1 = BN_new()) == NULL))
        goto err;
    if (!rsa->iqmp && ((rsa->iqmp = BN_new()) == NULL))
        goto err;

    if (BN_copy(rsa->e, e) == NULL)
        goto err;

    /*
     * The key generation follows the FIPS-186-4 standard.
     * The automatic selection of the public exponent and of the prime
     * factor's size is not supported.
     *
     * The prime factor's size must be at least 1024 bits for a 2048 bit
     * RSA key.
     *
     * The public exponent must be odd and greater than 65536.
     */
    if (BN_is_odd(e) == 0 || BN_is_one(e) == 1) {
        /*
         * e must be odd and greater than 1.
         */
        ok = 0; /* Must be a positive odd number */
        ERR_raise(ERR_LIB_RSA, RSA_R_PUBKEY_NOT_ODD);
        goto err;
    }

    for (;;) {
        /*
         * Find two suitable primes, p and q.
         * The primes must be such that (p-1) and (q-1) are not
         * divisible by e.
         */
        if (!BN_generate_prime_ex(rsa->p, bits / 2, 0, NULL, NULL, cb))
            goto err;
        if (!BN_sub(r1, rsa->p, BN_value_one()))
            goto err;
        if (!BN_div(r2, r3, r1, rsa->e, ctx))
            goto err;
        if (BN_is_zero(r3))
            continue;
        if (!BN_generate_prime_ex(rsa->q, bits / 2, 0, NULL, NULL, cb))
            goto err;
        if (!BN_sub(r1, rsa->q, BN_value_one()))
            goto err;
        if (!BN_div(r2, r3, r1, rsa->e, ctx))
            goto err;
        if (BN_is_zero(r3))
            continue;

        /*
         * Here, p and q are suitable.
         * Calculate n = p * q.
         */
        if (!BN_mul(rsa->n, rsa->p, rsa->q, ctx))
            goto err;

        /*
         * Calculate d, the private exponent.
         *
         * d is the inverse of e mod Carmichael's function lambda(n).
         * lambda(n) = lcm(p-1, q-1)
         *
         * It can be shown that for two primes, p and q,
         * lcm(p-1, q-1) = (p-1)*(q-1)/gcd(p-1, q-1).
         *
         * Let p-1 = r1 and q-1 = r2.
         * We have d = e^-1 mod (r1*r2/gcd(r1,r2)).
         */
        if (!BN_sub(r1, rsa->p, BN_value_one()))
            goto err;
        if (!BN_sub(r2, rsa->q, BN_value_one()))
            goto err;
        if (!BN_mul(r0, r1, r2, ctx))
            goto err;
        if (!BN_gcd(r3, r1, r2, ctx))
            goto err;
        if (!BN_div(r0, NULL, r0, r3, ctx))
            goto err;
        if (!BN_mod_inverse(rsa->d, rsa->e, r0, ctx))
            goto err;

        /*
         * We need to calculate the CRT parameters.
         * dmp1 = d mod (p-1)
         * dmq1 = d mod (q-1)
         * iqmp = q^-1 mod p
         */
        if (!BN_mod(rsa->dmp1, rsa->d, r1, ctx))
            goto err;
        if (!BN_mod(rsa->dmq1, rsa->d, r2, ctx))
            goto err;
        if (!BN_mod_inverse(rsa->iqmp, rsa->q, rsa->p, ctx))
            goto err;

        ok = 1;
        break;
    }
 err:
    if (ok == -1) {
        ERR_raise(ERR_LIB_RSA, ERR_R_BN_LIB);
        ok = 0;
    }
    BN_CTX_end(ctx);
    BN_CTX_free(ctx);
    BN_clear_free(r0);
    BN_clear_free(r1);
    BN_clear_free(r2);
    BN_clear_free(r3);
    return ok;
}