// code from https://www.ecrypt.eu.org/stream/e2-trivium.html
#ifndef TRIVIUM_H_
#define TRIVIUM_H_



/* 
 * Reference implementation of the TRIVIUM stream cipher
 *
 * Author: Christophe De Canni\`ere, K.U.Leuven.
 */

/* ------------------------------------------------------------------------- */

#include "ecrypt-portable.h"
#include "ecrypt-machine.h"
#include <iostream>
#include <vector>
/* ------------------------------------------------------------------------- */

#define S00(a, b) ((S(a, 1) << ( 32 - (b))))
#define S32(a, b) ((S(a, 2) << ( 64 - (b))) | (S(a, 1) >> ((b) - 32)))
#define S64(a, b) ((S(a, 3) << ( 96 - (b))) | (S(a, 2) >> ((b) - 64)))
#define S96(a, b) ((S(a, 4) << (128 - (b))) | (S(a, 3) >> ((b) - 96)))

#define UPDATE()                                                             \
  do {                                                                       \
    T(1) = S64(1,  66) ^ S64(1,  93);                                        \
    T(2) = S64(2,  69) ^ S64(2,  84);                                        \
    T(3) = S64(3,  66) ^ S96(3, 111);                                        \
                                                                             \
    Z(T(1) ^ T(2) ^ T(3));                                                   \
    T(1) ^= (S64(1,  91) & S64(1,  92)) ^ S64(2,  78);                       \
    T(2) ^= (S64(2,  82) & S64(2,  83)) ^ S64(3,  87);                       \
    T(3) ^= (S96(3, 109) & S96(3, 110)) ^ S64(1,  69);                       \
  } while (0)

#define ROTATE()                                                             \
  do {                                                                       \
    S(1, 3) = S(1, 2); S(1, 2) = S(1, 1); S(1, 1) = T(3);                    \
    S(2, 3) = S(2, 2); S(2, 2) = S(2, 1); S(2, 1) = T(1);                    \
    S(3, 4) = S(3, 3); S(3, 3) = S(3, 2); S(3, 2) = S(3, 1); S(3, 1) = T(2); \
  } while (0)

#define LOAD(s)                                                              \
  do {                                                                       \
    S(1, 1) = U8TO32_LITTLE((s) +  0);                                       \
    S(1, 2) = U8TO32_LITTLE((s) +  4);                                       \
    S(1, 3) = U8TO32_LITTLE((s) +  8);                                       \
                                                                             \
    S(2, 1) = U8TO32_LITTLE((s) + 12);                                       \
    S(2, 2) = U8TO32_LITTLE((s) + 16);                                       \
    S(2, 3) = U8TO32_LITTLE((s) + 20);                                       \
                                                                             \
    S(3, 1) = U8TO32_LITTLE((s) + 24);                                       \
    S(3, 2) = U8TO32_LITTLE((s) + 28);                                       \
    S(3, 3) = U8TO32_LITTLE((s) + 32);                                       \
    S(3, 4) = U8TO32_LITTLE((s) + 36);                                       \
  } while (0)

#define STORE(s)                                                            \
  do {                                                                      \
    U32TO8_LITTLE((s) +  0, S(1, 1));                                       \
    U32TO8_LITTLE((s) +  4, S(1, 2));                                       \
    U32TO8_LITTLE((s) +  8, S(1, 3));                                       \
                                                                            \
    U32TO8_LITTLE((s) + 12, S(2, 1));                                       \
    U32TO8_LITTLE((s) + 16, S(2, 2));                                       \
    U32TO8_LITTLE((s) + 20, S(2, 3));                                       \
                                                                            \
    U32TO8_LITTLE((s) + 24, S(3, 1));                                       \
    U32TO8_LITTLE((s) + 28, S(3, 2));                                       \
    U32TO8_LITTLE((s) + 32, S(3, 3));                                       \
    U32TO8_LITTLE((s) + 36, S(3, 4));                                       \
  } while (0)


#define S(a, n) (s##a##n)
#define T(a) (t##a)


/*****************************************************************/
void customizedTrivium(const u8* key, const u8* iv, u8* keystream, int nrRounds); 

int getLenKeystream(int nrRounds); // in bytes

/****************************************************************/ 
// to select a particular bit of the keystream

#define Q8(x) ((x)/8) 
#define R8(x) ((x)%8)
#define Q32(x) ((x)/32) 
#define R32(x) ((x)%32)

#define TRIVIUM_BIT(ks, r) (((ks)[4*Q32(r) + 3 - Q8(R32(r))  ] >> (7 - R8(R32(r)))) & 1)

#endif