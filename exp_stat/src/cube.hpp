#ifndef CUBE_H_ 
#define CUBE_H_

#include <bits/stdint-uintn.h>
#include <cstddef>
#include <limits.h>
#include <vector> 
#include <iostream>
#include <cstdint>
#include <bitset>
#include <algorithm>
#include <math.h>
#include <random>

class Cubes {
    public: 
        Cubes(unsigned dim, unsigned nrVars, unsigned nrCubesMax);
        ~ Cubes(); 
        void first(); 
        bool next();
        bool nextRandomCube(); 
        const uint8_t* getVectorSpace(); // array of size 2**dim * size_vect
        int sizeVector() const {return size_vect; }
        friend std::ostream & operator<<(std::ostream &os, const Cubes& c);

    private:
        const unsigned dim;     // dimension of the cube e.g. 10 
        const unsigned nrVars;  // number of variables e.g. 128 
        const unsigned long long nrCubesMax; 
        unsigned indCube;
        std::vector<bool> currCube; 
        uint8_t *vectors;
        const int size_vect; 
};


#endif 