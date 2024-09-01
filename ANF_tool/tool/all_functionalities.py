import numpy as np
import csv 
import math 
from sage.all import *
from sage.rings.polynomial.pbori import *
from . import settings as s
from functools import reduce

###### step 2: list of monomials in the public variables  #######
class ListMons: 
    def __init__(self, arg): 
        if isinstance(arg, sage.rings.polynomial.pbori.pbori.BooleSet):
            self.monomes = arg 
        else: 
            raise TypeError("Only BooleSet are allowed")
    
    @classmethod 
    def from_anf(cls, anf): 
        """
        Convert a BooleanPolynomial with public and private variables
        into a ListMons object containing the monomials in the public
        variables. For instance, k2 * x3 * x1 + k4 * x5 gives {x3 * x1, x5}.
        
        Parameters: 
        - anf : a BooleanPolynomial with public and private variables. 
        Hypothesis: we use a lexicographical ordering (lp) such that
        xi > kj for all i and j.    
        """
        del_key = anf.set()
        for index in range (s.SIZE_X, s.SIZE_X + s.SIZE_K): 
             del_key = del_key.subset1(index).union(del_key.subset0(index))
        return cls(del_key)
    
    def __add__(self, other): 
        return ListMons(self.monomes.union(other.monomes))
    
    def __mul__(self, other): 
         return ListMons(self.monomes.cartesian_product(other.monomes))
            
    def __repr__(self):
        return f"ListMons{{{Polynomial(self.monomes).__str__()}}}"
    
    def __len__(self): 
        return len(self.monomes)
    
###### step 3: bound on the number of monomials for each degree  #######
class BoundNrMons: 
    """
    Class to store bounds on the number of monomials of a function for 
    each degree.
    Attributes: 
    - bound (list): bound[d] is a bound on the number of monomials of degree d.
    - is_max (bool): A flag indicating whether all the bounds are maximal. 
    """
    def __init__(self, arg:list, is_max: bool) -> None: 
            self.bound = arg
            self.is_max = is_max
             
    @classmethod 
    def from_list_mons(cls, list_mons):
        if isinstance(list_mons,
                      sage.rings.polynomial.pbori.pbori.BooleSet): 
            monomes = list_mons
        elif isinstance(list_mons, ListMons):
            monomes = list_mons.monomes
        else:
            raise TypeError("Input must be a BooleSet or a ListMons object")
       
                            
        bound = [0] * (s.SIZE_X + 1)
        for monome in monomes: 
            bound[monome.deg()] += 1
        return cls(bound, False)
    
    def __add__(self, other):
        if (self.is_max or other.is_max): 
            return BoundNrMons(s.BINOMIALS[s.SIZE_X], True)
        bound = [min(s.BINOMIALS[s.SIZE_X][i],
                     self.bound[i]+other.bound[i]) 
                 for i in range(s.SIZE_X+1)]
        return BoundNrMons(bound, bound == s.BINOMIALS[s.SIZE_X]) 
    
    def __mul__(self, other): 
        if (self.is_max and other.bound[0] == 1) or \
           (other.is_max and self.bound[0] == 1):
            return BoundNrMons(s.BINOMIALS[s.SIZE_X], True)
        accumul_self   = copy(self.bound)
        accumul_other  = copy(other.bound)
        for i in range (1, s.SIZE_X + 1): 
            accumul_self[i]   += accumul_self[i-1]
            accumul_other[i]  += accumul_other[i-1]

        def bound(bound_lhs, bound_rhs, accumul_rhs, d) : 
            b = 0
            for j in range (0, d + 1): 
                if j != d: 
                    sum_rhs = accumul_rhs[d] - accumul_rhs[d-j-1] 
                else :   
                    sum_rhs = accumul_rhs[d] 
                b +=  (bound_lhs[j] 
                          * min(sum_rhs, s.BINOMIALS[s.SIZE_X-j][d-j]))
                if b >= s.BINOMIALS[s.SIZE_X][d] : 
                    return s.BINOMIALS[s.SIZE_X][d]
            return b

        res = [0] * (s.SIZE_X + 1)
        for d in range (s.SIZE_X + 1):    
            res[d] = min(bound(self.bound, other.bound, accumul_other, d), 
                         bound(other.bound, self.bound, accumul_self, d), 
                         s.BINOMIALS[s.SIZE_X][d])
        return BoundNrMons(res, res == s.BINOMIALS[s.SIZE_X]) 
    
    def get_list_to_save(self):
        """
        Information to be saved in a file. 
        Returns:
            A list of size SIZE_X + 1 whose d-th cell contains the difference
            between the trivial bound and the bound computed by the tool for
            the degree d. If the computed bound equals the trivial bound, we
            use the value np.inf instead. 
        """
        return [np.inf if (0 ==  self.bound[d]) 
                 else (s.BINOMIALS[s.SIZE_X][d] -  self.bound[d]) for d in range(s.SIZE_X + 1)]
    
    def minimum(self, other): 
        if self.is_max and other.is_max: 
            return BoundNrMons(s.BINOMIALS[s.SIZE_X], True)
        res = [min(self.bound[i], other.bound[i]) for 
               i in range(s.SIZE_X+1)]
        return BoundNrMons(res, False) 
    
    def __str__(self):
        string = ""
        for d in range (s.SIZE_X + 1): 
            if self.bound[d] != 0: 
                string += f'max nr monomes of degree {d}\t:  {self.bound[d]}\n'
        return string
     

###### step 3: estimate the number of monomials for each degree  #######
def prob_degree(a: int, b:int, d:int) -> float:
    """
    Return the probability that a product between 
    a monomial of degree a and a monomial of degree b
    in size_x variables gives a monomial of degree d.
    Hypothesis: 0 <= a <= size_x
                0 <= b <= size_x 
                max(a, b) <= d <= min(size_x, a + b)
                degree_product is a global variable 
    """
    if b > a: 
        a, b = b, a 
    return s.COEFF_PROD[a][b][d-a]

def DL(x, a, n):
    # Taylor series expansion of (1 + x)^a of order n  
    #return xa + 1/2 * a(a-1) * x^2 + ... + 1/n! * a(a-1)...(a-n) * x^n 
    t = x * a 
    L = [t]
    for i in range(1, n+1):
        t *=  x * (a - i) / (i + 1)
        L.append(t)
        L.sort()
        return sum(L)
    
class EstimateNrMons:
    """
    Class to store estimates on the number of monomials of a function for 
    each degree.
    Attributes: 
    - tab (numpy array): tab[d] is a bound on the number of monomials of degree d.
    - deg (int): Maximal degree of the function.
    """
    def __init__(self, arg: np.ndarray, deg) -> None:
        self.tab = arg
        self.deg = deg
    
    @classmethod 
    def from_list_mons(cls, list_mons):
        if isinstance(list_mons,
                      sage.rings.polynomial.pbori.pbori.BooleSet): 
            monomes = list_mons
        elif isinstance(list_mons, ListMons):
            monomes = list_mons.monomes
        else:
            raise TypeError("Input must be a BooleSet or a ListMons object")
        tab = np.zeros(shape = s.SIZE_X + 1, dtype = np.float128)
        deg = -np.inf
        for monome in monomes: 
            d = monome.deg()
            if d > deg: 
                deg = d
            tab[d] += 1
        return EstimateNrMons(tab/2, deg)
    
    def __add__(self, other):
        tab = self.tab + other.tab - 2 * self.tab * other.tab / s.BINOMIALS[s.SIZE_X]
        deg = min(s.SIZE_X, max(self.deg, other.deg))
        return EstimateNrMons(tab, deg)
    
    def __mul__(self, other): 
        tab = np.zeros(shape = s.SIZE_X + 1, dtype = np.float128)
        
        deg = min(s.SIZE_X, self.deg + other.deg)
        for d in range(deg + 1): 
            somme = 0 
            k = s.BINOMIALS[s.SIZE_X][d]
            for a in range(d+1): 
                flag = False 
                for b in range(d-a, d+1): 
                    somme += (prob_degree(a, b, d) 
                              * self.tab[a] 
                              * other.tab[b])
                    if math.ceil(somme) >= int(k): 
                        flag = True 
                        break 
                if flag: 
                    break 
            if flag: 
                tab[d] = k / 2
            else: 
                tab[d] = -k / 2 * DL(-2/k, somme, 10)
        
        return EstimateNrMons(tab, deg)
    
    def get_list_to_save(self): 
        """
        Information to be saved in a file. 
        Returns:
            A list of size SIZE_X + 1 whose d-th cell contains the estimated proportion 
            for the monomials of degree d.
        """
        T = self.tab / s.BINOMIALS[s.SIZE_X]
        return T.tolist()
        
    def __str__(self): 
        string = ""
        for d in range (s.SIZE_X + 1): 
            if self.tab[d] != 0: 
                string += f'estimate for degree {d}\t:  {self.tab[d]}\n'
        return string
    
    
#########################################################################

class Variables:
    """
    A class storing different representations for public variables, secret
    variables and constants. 
    Attributes: 
    - x (tuple): Public variables. 
    - k (tuple): Secret variables.
    - c (tuple): Constants 0 and 1.
    Usage:
    Use this class to code the round function of a symmetric primitive
    in the form of `function(s, variables, index_round, index_step)` where 
    `variable` is a Variables object. Then, if you need for instance the 
    constant 1, write  
    c = variables.gens_c()
    c[1]
    """
    def __init__(self, x, k, c):
        self.x = x 
        self.k = k 
        self.c = c
        
    def gens_x(self):
        return self.x
    
    def gens_k(self):
        return self.k
        
    def gens_c(self): 
        return self.c
    
    @classmethod 
    def for_step_1(cls): 
        x = s.RING.gens()[0: s.SIZE_X]
        k = s.RING.gens()[s.SIZE_X: s.SIZE_X + s.SIZE_K]
        c = (Polynomial(0, s.RING), Polynomial(1, s.RING))
        return cls(x, k, c)
    
    @classmethod 
    def for_step_2(cls): 
        var = Variables.for_step_1()
        x = tuple(ListMons.from_anf(anf) for anf in var.x)
        k = tuple(ListMons.from_anf(anf) for anf in var.k)
        c = tuple(ListMons.from_anf(anf) for anf in var.c)
        return cls(x, k, c)
    
    @classmethod
    def for_step_3_bound(cls): 
        var = Variables.for_step_2()
        x = tuple(BoundNrMons.from_list_mons(a) for a in var.x)
        k = tuple(BoundNrMons.from_list_mons(a) for a in var.k)
        c = tuple(BoundNrMons.from_list_mons(a) for a in var.c)
        return cls(x, k, c)
    
    # step 3   
    @classmethod 
    def for_step_3_estimate(cls):  
        var = Variables.for_step_2()
        x = tuple(EstimateNrMons.from_list_mons(a) for a in var.x)
        k = tuple(EstimateNrMons.from_list_mons(a) for a in var.k)
        c = tuple(EstimateNrMons.from_list_mons(a) for a in var.c)
        x = tuple(EstimateNrMons(2*a.tab, a.deg) for a in x)
        c = tuple(EstimateNrMons(2*a.tab, a.deg) for a in c)
        return cls(x, k, c)