#ifndef ASCON_H_
#define ASCON_H_

#include <stdint.h>
#include <vector>
#include <bits/stdint-uintn.h>

#define ASCON_128_KEYBYTES 16
#define ASCON_128_RATE 8
#define ASCON_128_PA_ROUNDS 12
#define ASCON_128_PB_ROUNDS 6

#define ASCON_128_IV                            \
  (((uint64_t)(ASCON_128_KEYBYTES * 8) << 56) | \
   ((uint64_t)(ASCON_128_RATE * 8) << 48) |     \
   ((uint64_t)(ASCON_128_PA_ROUNDS) << 40) |    \
   ((uint64_t)(ASCON_128_PB_ROUNDS) << 32))

typedef struct {
  uint64_t x[5];
} ascon_state_t;

static inline std::vector<uint8_t> initAsconConstants() {
    return std::vector<uint8_t> {0xf0, 0xe1, 0xd2, 0xc3, 0xb4,0xa5, 
                            0x96, 0x87, 0x78, 0x69, 0x5a, 0x4b};
}

static inline uint64_t ROR(uint64_t x, int n) {
  return x >> n | x << (-n & 63);
}


static inline void ROUND(ascon_state_t* s, uint8_t C) {
  ascon_state_t t;
  /* addition of round constant */
  s->x[2] ^= C;
  /* substitution layer */
  s->x[0] ^= s->x[4];
  s->x[4] ^= s->x[3];
  s->x[2] ^= s->x[1];
  /* start of keccak s-box */
  t.x[0] = s->x[0] ^ (~s->x[1] & s->x[2]);
  t.x[1] = s->x[1] ^ (~s->x[2] & s->x[3]);
  t.x[2] = s->x[2] ^ (~s->x[3] & s->x[4]);
  t.x[3] = s->x[3] ^ (~s->x[4] & s->x[0]);
  t.x[4] = s->x[4] ^ (~s->x[0] & s->x[1]);
  /* end of keccak s-box */
  t.x[1] ^= t.x[0];
  t.x[0] ^= t.x[4];
  t.x[3] ^= t.x[2];
  t.x[2] = ~t.x[2];
  /* linear diffusion layer */
  s->x[0] = t.x[0] ^ ROR(t.x[0], 19) ^ ROR(t.x[0], 28);
  s->x[1] = t.x[1] ^ ROR(t.x[1], 61) ^ ROR(t.x[1], 39);
  s->x[2] = t.x[2] ^ ROR(t.x[2], 1) ^ ROR(t.x[2], 6);
  s->x[3] = t.x[3] ^ ROR(t.x[3], 10) ^ ROR(t.x[3], 17);
  s->x[4] = t.x[4] ^ ROR(t.x[4], 7) ^ ROR(t.x[4], 41);
}

/* set byte in 64-bit Ascon word */
#define SETBYTE(b, i) ((uint64_t)(b) << (56 - 8 * (i)))  

/* load bytes into 64-bit Ascon word */
static inline uint64_t LOADBYTES(const uint8_t* bytes, int n) {
  int i;
  uint64_t x = 0;
  for (i = 0; i < n; ++i) x |= SETBYTE(bytes[i], i);
  return x;
}

static inline void LOAD_STATE(ascon_state_t* s, const uint8_t* key, const uint8_t* npub) { 

    /* load key */
    const uint64_t K0 = LOADBYTES(key, 8);
    const uint64_t K1 = LOADBYTES(key + 8, 8);
    const uint64_t N0 = LOADBYTES(npub, 8);
    const uint64_t N1 = LOADBYTES(npub + 8, 8);

    /* initialize */ 
    s->x[0] = ASCON_128_IV;
    s->x[1] = K0;
    s->x[2] = K1;
    s->x[3] = N0;
    s->x[4] = N1;
}

static inline void set_null_state(ascon_state_t* s) {
    s->x[0] = 0;
    s->x[1] = 0; 
    s->x[2] = 0;
    s->x[3] = 0; 
    s->x[4] = 0; 
}

/******************************************************************************************/
// to select a particular bit of the state 

#define Q64(i) ((i)/64) 
#define R64(i) ((i)%64)
#define ASCON_BIT(s, i) ((((s).x[Q64(i)]) >> R64(i)) & 1 ) 

#endif 