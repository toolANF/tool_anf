#include <iostream>
#include <bits/stdint-uintn.h>
#include <cstdint>
#include <iostream>
#include <random>
#include <fstream>
#include <string>

#include "cube.hpp"
#include "trivium.hpp"
#include "ascon.h"

using namespace std; 

/* 
These functions randomly draw `nrKeys` keys. For each key, they randomly draw nrCubes 
monomials in dim public variables and count how many of them belong to
the ANF of the function instantiated with the key. 

For Ascon, the membership test is performed for each round 
and for each bit of the state. The results are written in the form of a 
table where the columns contain the round, the position of the analyzed 
bit, the degree of the monomials, how many of the drawn monomials belong
to the ANF, the number of drawn monomials and the number of keys used. 

For Trivium, the membership test is performed on the key stream output bit 
for each round. The results are written in the form of a 
table where the columns contain the round, the degree of the monomials,
how many of the drawn monomials belong to the ANF, the number 
of drawn monomials and the number of keys used. 
*/
void ascon_draw_cubes(int dim, int nrCubes, int nrKeys);
void trivium_draw_cubes(int dim, int nrCubes, int nrKeys); 

int main(int argc, char const *argv[]) {

    
    // for TRIVIUM 
    for (unsigned degree = 2; degree < 12; ++degree) {
        // draw 250 monomials per key and 20 keys
        trivium_draw_cubes(degree, 250, 20); 
        
    }

    // for ASCON 
    for (unsigned degree = 2; degree < 12; ++degree) {
        // draw 250 monomials per key and 20 keys
        ascon_draw_cubes(degree, 250, 20); 
        
    }
    
    return 0; 
}

void init_random_key(uint8_t* key, int size_key) 
{
    static default_random_engine generator(static_cast<long unsigned int>(time(0)));
    static uniform_int_distribution<u8> distribution(0, 255); 
    for (auto i = 0; i < size_key; i++) key[i] = distribution(generator);  
}

void print_key(uint8_t* key, int size_key) 
{
    cout << "-------------------key-------------------" << endl;
    for (auto i = 0; i < size_key; i++) cout << (int)key[i] << " ";   
    cout << endl; 
}

void ascon_draw_cubes(int dim, int nrCubesPerKey, int nrKeys) {
    const int size_key   = 16;
    const int size_state = 320; 
    const int nrRounds   = 12; 
    const int nrVars     = 128; 

    uint8_t key[size_key]; 
    ascon_state_t s;
    ascon_state_t sum[nrRounds]; 
    static auto consts = initAsconConstants();
    vector<vector<unsigned>> nrMonsFound(nrRounds, vector<unsigned> (size_state, 0));

    for (int ind_k = 0; ind_k < nrKeys; ++ind_k) {
        init_random_key(key, size_key);
        //print_key(key, size_key); 
        Cubes cubes(dim, nrVars, nrCubesPerKey);
        do {
            for (unsigned r = 0; r < nrRounds; ++r) set_null_state(&sum[r]); 

            const uint8_t* vectors = cubes.getVectorSpace(); 
            int size_v = cubes.sizeVector(); 
            for (int j = 0; j < (1 << dim); j++) {
                LOAD_STATE(&s, key, vectors + j * size_v); 
                for (unsigned r = 0; r < nrRounds; ++r) {    
                    ROUND(&s, consts[r]);
                    for (int i = 0; i < 5; i++) sum[r].x[i] ^= s.x[i]; 
                }    
            }

            for (unsigned r = 0; r < nrRounds; ++r) {
                for (unsigned p = 0; p < size_state; p++)
                    if (ASCON_BIT(sum[r], p)) nrMonsFound[r][p]++;  
            } 
        } while (cubes.nextRandomCube());

    }

    ofstream myfile;
    string filename = "ascon_stat_exp.csv"; 
    myfile.open(filename, ios::app);

    if (myfile.tellp() == 0) {
        myfile << "round,bit,degree,N_mon_found,N_mon_tested,N_keys\n";
    }

    for (unsigned r = 0; r < nrRounds; r++) {
        for (unsigned p = 0; p < size_state; ++p) {
             myfile << r + 1 << ",";  // rounds are numbered from 1
             myfile << p << ","; 
             myfile << dim << ","; 
             myfile << nrMonsFound[r][p] << ","; 
             myfile << nrCubesPerKey * nrKeys << ",";
             myfile << nrKeys << endl;
        } 
    }  
    myfile.close();
}

void trivium_draw_cubes(int dim, int nrCubesPerKey, int nrKeys) {
   
    const int size_key = 10;
    const int nrRounds = 1152; 
    const int nrVars   = 80; 

    uint8_t key[size_key]; 
    

    int len_ks = getLenKeystream(nrRounds);
    uint8_t keystream[len_ks];

    
    vector<unsigned> nrMonsFound(nrRounds, 0);
    

    for (int64_t ind_k = 0; ind_k < nrKeys; ++ind_k) {
        init_random_key(key, size_key);
        Cubes cubes(dim, nrVars, nrCubesPerKey);
        vector<uint8_t> sum(len_ks, 0); 
        do {
            for (auto i = 0; i < len_ks; i++) sum[i] = 0; 
            auto vectors = cubes.getVectorSpace();
            auto size_v = cubes.sizeVector(); 
            
            for (int j = 0; j < (1 << dim); j++) {
                customizedTrivium(key, vectors + j * size_v, keystream, nrRounds); 
                for (int i = 0; i < len_ks; i++) sum[i] ^= keystream[i]; 
            }
            for (int r = 0; r < nrRounds; ++r) {
            if (TRIVIUM_BIT(sum, r)) nrMonsFound[r]++;  
            }
        } while (cubes.nextRandomCube());
    }


    

    ofstream myfile;
    string filename = "trivium_stat_exp.csv"; 
    myfile.open(filename, ios::app);

    if (myfile.tellp() == 0) {
        myfile << "round,degree,N_mon_found,N_mon_tested,N_keys\n";
    }
    for (unsigned r = 0; r < nrRounds; r++) {
        myfile << r +1 << ","; // rounds are numbered from 1 
        myfile << dim << ","; 
        myfile << nrMonsFound[r] << ","; 
        myfile << nrCubesPerKey * nrKeys << ","; 
        myfile << nrKeys << endl;
    }  
    myfile.close();
}