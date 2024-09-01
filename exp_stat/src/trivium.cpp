#include "trivium.hpp"

void customizedTrivium(const u8* key, const u8* iv, u8* keystream, int nrRounds)
{
  u8 s[39]; 
  
  int i;

  u32 s11, s12, s13;
  u32 s21, s22, s23;
  u32 s31, s32, s33, s34;

  for (i = 0; i < 10; ++i)
    s[i] = key[i];

  for (i = 10; i < 12; ++i)
    s[i] = 0;

  for (i = 0; i < 10; ++i)
    s[i + 12] = iv[i];

  for (i = 10; i < 12; ++i)
    s[i + 12] = 0;

  for (i = 0; i < 13; ++i)
    s[i + 24] = 0;

  s[13 + 24] = 0x70;

  LOAD(s);


#define Z(w) (U32TO8_LITTLE(keystream + 4 * i, w))

  for (i = 0; i < (nrRounds-1)/32 + 1; ++i)
    {
      u32 t1, t2, t3;
      
      UPDATE();
      ROTATE();
    }

  STORE(s);
}

int getLenKeystream(int nrRounds)
{
    return ((nrRounds-1)/32 + 1) * 4; 
}