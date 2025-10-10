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
#include "pk_crypto_local.h"

/*
 * NB: This function is not thread-safe, and should be called before the
 * provider framework is initialized.
 */
PUBKEY_METHOD *PUBKEY_meth_dup(const PUBKEY_METHOD *meth);

#ifndef FIPS_MODULE
/*
 * The global default public key method can be replaced to hook in to asymmetric key
 * generation and other cryptographic operations. If it hasn't been explicitly
 * initialized with PUBKEY_set_default_method() it will be implicitly
 * initialized on first use to the default_PUBKEY_meth.
 */
static PUBKEY_METHOD *default_PUBKEY_meth = NULL;

int PUBKEY_set_default_method(const PUBKEY_METHOD *meth)
{
    PUBKEY_METHOD *t;

    if (default_PUBKEY_meth != NULL
        && (t = PUBKEY_meth_dup(default_PUBKEY_meth)) == NULL)
        return 0;
    PUBKEY_meth_free(default_PUBKEY_meth);
    default_PUBKEY_meth = (PUBKEY_METHOD *)meth;
    return 1;
}

const PUBKEY_METHOD *PUBKEY_get_default_method(void)
{
    if (default_PUBKEY_meth == NULL) {
        default_PUBKEY_meth = PUBKEY_PKCS1_OpenSSL();
    }
    return default_PUBKEY_meth;
}
#endif

int PUBKEY_generate_key_ex(PUBKEY_CTX *ctx, int bits, BIGNUM *e, BN_GENCB *cb)
{
    if (ctx->meth->pubkey_keygen)
        return ctx->meth->pubkey_keygen(ctx, bits, e, cb);

    return ossl_pubkey_generate_key_int(ctx, bits, e, cb);
}

/*
 * This is a generic asymmetric key generation function.
 * It is used by the OpenSSL BIGNUM method.
 *
 * It is not used for FIPS key generation, which is in fips/pubkey_gen.c.
 */
int ossl_pubkey_generate_key_int(PUBKEY_CTX *ctx, int bits, BIGNUM *e, BN_GENCB *cb)
{
    BIGNUM *r0 = NULL, *r1 = NULL, *r2 = NULL, *r3 = NULL, *tmp;
    BIGNUM *p, *q;
    int n = 0, m = 0;
    int ok = -1;
    BN_CTX *ctx = NULL;

    bn_ctx = BN_CTX_new_ex(ctx->libctx);
    if (bn_ctx == NULL)
        goto err;
    BN_CTX_start(bn_ctx);
    r0 = BN_CTX_get(bn_ctx);
    r1 = BN_CTX_get(bn_ctx);
    r2 = BN_CTX_get(bn_ctx);
    r3 = BN_CTX_get(bn_ctx);
    if (r3 == NULL)
        goto err;

    /*
     * We need the asymmetric key components non-NULL.
     */
    if (!ctx->n && ((ctx->n = BN_new()) == NULL))
        goto err;
    if (!ctx->e && ((ctx->e = BN_new()) == NULL))
        goto err;
    if (!ctx->d && ((ctx->d = BN_new()) == NULL))
        goto err;
    if (!ctx->p && ((ctx->p = BN_new()) == NULL))
        goto err;
    if (!ctx->q && ((ctx->q = BN_new()) == NULL))
        goto err;
    if (!ctx->dmp1 && ((ctx->dmp1 = BN_new()) == NULL))
        goto err;
    if (!ctx->dmq1 && ((ctx->dmq1 = BN_new()) == NULL))
        goto err;
    if (!ctx->iqmp && ((ctx->iqmp = BN_new()) == NULL))
        goto err;

    if (BN_copy(ctx->e, e) == NULL)
        goto err;

    /*
     * The key generation follows the FIPS-186-4 standard.
     * The automatic selection of the public exponent and of the prime
     * factor's size is not supported.
     *
     * The prime factor's size must be at least 1024 bits for a 2048 bit
     * asymmetric key.
     *
     * The public exponent must be odd and greater than 65536.
     */
    if (BN_is_odd(e) == 0 || BN_is_one(e) == 1) {
        /*
         * e must be odd and greater than 1.
         */
        ok = 0; /* Must be a positive odd number */
        ERR_raise(ERR_LIB_PUBKEY, PUBKEY_R_PUBEXP_NOT_ODD);
        goto err;
    }

    for (;;) {
        /*
         * Find two suitable primes, p and q.
         * The primes must be such that (p-1) and (q-1) are not
         * divisible by e.
         */
        if (!BN_generate_prime_ex(ctx->p, bits / 2, 0, NULL, NULL, cb))
            goto err;
        if (!BN_sub(r1, ctx->p, BN_value_one()))
            goto err;
        if (!BN_div(r2, r3, r1, ctx->e, bn_ctx))
            goto err;
        if (BN_is_zero(r3))
            continue;
        if (!BN_generate_prime_ex(ctx->q, bits / 2, 0, NULL, NULL, cb))
            goto err;
        if (!BN_sub(r1, ctx->q, BN_value_one()))
            goto err;
        if (!BN_div(r2, r3, r1, ctx->e, bn_ctx))
            goto err;
        if (BN_is_zero(r3))
            continue;

        /*
         * Here, p and q are suitable.
         * Calculate n = p * q.
         */
        if (!BN_mul(ctx->n, ctx->p, ctx->q, bn_ctx))
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
        if (!BN_sub(r1, ctx->p, BN_value_one()))
            goto err;
        if (!BN_sub(r2, ctx->q, BN_value_one()))
            goto err;
        if (!BN_mul(r0, r1, r2, bn_ctx))
            goto err;
        if (!BN_gcd(r3, r1, r2, bn_ctx))
            goto err;
        if (!BN_div(r0, NULL, r0, r3, bn_ctx))
            goto err;
        if (!BN_mod_inverse(ctx->d, ctx->e, r0, bn_ctx))
            goto err;

        /*
         * We need to calculate the CRT parameters.
         * dmp1 = d mod (p-1)
         * dmq1 = d mod (q-1)
         * iqmp = q^-1 mod p
         */
        if (!BN_mod(ctx->dmp1, ctx->d, r1, bn_ctx))
            goto err;
        if (!BN_mod(ctx->dmq1, ctx->d, r2, bn_ctx))
            goto err;
        if (!BN_mod_inverse(ctx->iqmp, ctx->q, ctx->p, bn_ctx))
            goto err;

        ok = 1;
        break;
    }
 err:
    if (ok == -1) {
        ERR_raise(ERR_LIB_PUBKEY, ERR_R_BN_LIB);
        ok = 0;
    }
    BN_CTX_end(bn_ctx);
    BN_CTX_free(bn_ctx);
    BN_clear_free(r0);
    BN_clear_free(r1);
    BN_clear_free(r2);
    BN_clear_free(r3);
    return ok;
}