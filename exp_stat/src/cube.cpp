#include "cube.hpp"
#include <algorithm>
#include <bits/stdint-uintn.h>
#include <random>

using namespace std;


Cubes::Cubes(unsigned dim, unsigned nrVars, unsigned nrCubesMax)
    : dim(dim), 
      nrVars(nrVars),
      nrCubesMax(nrCubesMax), 
      size_vect(ceil(nrVars/ 8.))
{
    first(); 
    vectors = new uint8_t[(1 << dim) * size_vect];
}

Cubes::~Cubes() {delete[] vectors; }

void Cubes::first()
{
    indCube = 1; 
    currCube = vector<bool> (nrVars, 0); 
    for (unsigned i = 0; i < dim; i++) currCube[nrVars - 1 - i] = true;
}

bool Cubes::next()
{
    if (indCube == nrCubesMax) return false;
    if  (next_permutation(begin(currCube), end(currCube))) {
        indCube += 1; 
        return true; 
    }
    return false; 
}

bool Cubes::nextRandomCube()
{
    static random_device rd;
    static mt19937 g(rd());
    indCube += 1; 
    shuffle(currCube.begin(), currCube.end(), g);
    return nrCubesMax >= indCube; 
}

const uint8_t* Cubes::getVectorSpace()
{
    // init first vector 
   for (int j = 0; j < size_vect; j++) vectors[j] = 0;
   int nr_init = 1;

    // init other vectors
    for (unsigned i = 0; i < nrVars; i++) {
        if (currCube[i]) {
            auto q = i / 8; 
            auto r = i % 8;
            uint8_t* v = vectors + nr_init * size_vect; 
            for (int j = 0; j < nr_init * size_vect; j++) v[j] = vectors[j]; 
            for (; v < vectors + 2 * nr_init * size_vect; v += size_vect) v[q] ^= 1 << r; 
            nr_init *= 2; 
        }
    }
    return vectors; 
}

std::ostream & operator<<(std::ostream &os, const Cubes& c)
{
    os << "cube " << c.indCube << " : "; 
    for (unsigned i = 0; i < c.nrVars; ++i) {
        if (c.currCube[i]) os << "x" << i ; 
    }
    os << endl; 
    return os; 
}
