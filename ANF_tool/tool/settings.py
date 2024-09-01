import numpy as np
from sage.all import *
from sage.rings.polynomial.pbori import *

""" 
This file contains configuration settings for the tool. 
We use the variables 
- TOOL_VERSION
- SIZE_X
- SIZE_K
- STATE_CONSTRUCTOR
- ROUND_FUNCTION
- NR_ROUNDS_STEP_1 
- NR_ROUNDS_STEP_2
- NR_ROUNDS_MAX
- FILE_NAME
- BITS_TO_SAVE
- BINOMIALS
- COEFF_PROD
- RING
"""

BINOMIALS   = []
COEFF_PROD  = []

def config_param(param) -> None: 
    wanted_param = {'TOOL_VERSION',
                    'SIZE_X', 
                    'SIZE_K',
                    'STATE_CONSTRUCTOR',
                    'ROUND_FUNCTION',
                    'NR_ROUNDS_STEP_1', 
                    'NR_ROUNDS_STEP_2',
                    'NR_ROUNDS_MAX',
                    'FILE_NAME', 
                    'BITS_TO_SAVE', 
                     }
    if set(param.keys()) != wanted_param: 
        raise ValueError(
            f"Not the right parameters.\n"
            f"Received parameters: {set(param.keys())}\n"
            f"Expected parameters: {wanted_param}"
        )
    globals().update(param)
    globals()["RING"] = declare_ring([Block("x", SIZE_X), 
                                 Block("k", SIZE_K)])
    if TOOL_VERSION not in ['bound', 'estimate']: 
        raise ValueError(
            f"Invalid TOOL_VERSION: {TOOL_VERSION}. "
            f"Expected 'bound' or 'estimate'."
        )
    
    global ROUND_FUNCTION
    if not isinstance(ROUND_FUNCTION, tuple):
        ROUND_FUNCTION = (ROUND_FUNCTION,)
    global BITS_TO_SAVE
    if isinstance(BITS_TO_SAVE, int):
        BITS_TO_SAVE = (BITS_TO_SAVE,)
        
    
    
def get_binomials(size: int, use_numpy: bool) -> list: 
    """
    Return an array binomials such that 
    for 0 <= n <= size and 0 <= k <= n
    binomials[n][k] = n! / (k ! (n - k)!)
    """
    if use_numpy: 
        binomials = [np.zeros(shape = (i+1), dtype = np.float128)
                     for i in range(size+1)]
    else: 
        binomials = [(i+1) * [0] for i in range(size+1)]
    
    for i in range(size+1): 
        binomials[i][0] = 1
        binomials[i][i] = 1
    for i in range (1, size+1): 
        for j in range (1, i): 
            binomials[i][j] = binomials[i-1][j-1] + binomials[i-1][j] 
    return binomials

def get_coeff_prod(size: int) -> list: 
    """
    Return an array degree_product such that for
    - 0 <= a <= size
    - 0 <= b <= a
    - 0 <= b_diff_a <= min(size - a, b) 
    coeff_prod[a][b][b_diff_a] is the probability that a 
    product between a monomial of degree a and a monomial
    of degree b in size variables gives a monomial of 
    degree a + b_diff_a.
    """
    coeff_prod = [[[None 
                         for b_diff_a in range(min(size - a, b) + 1)]
                         for b in range(a + 1)]
                         for a in range(size + 1)]
    
    for a in range(size + 1): 
        for b in range(a + 1): 
            for b_diff_a in range(min(size - a, b) + 1): 
                k = a + b_diff_a 
                coeff_prod[a][b][b_diff_a] = ( BINOMIALS[size][k] 
                        * BINOMIALS[k][a]  
                        * BINOMIALS[a][a + b - k] 
                        /(BINOMIALS[size][a] * BINOMIALS[size][b]))
    return coeff_prod

def config_auxiliary_arrays():
    global BINOMIALS 
    global COEFF_PROD
    if TOOL_VERSION == 'bound':
        BINOMIALS[:] = get_binomials(SIZE_X, False)
        COEFF_PROD[:] = [] 
    elif TOOL_VERSION == 'estimate':
        BINOMIALS[:] = get_binomials(SIZE_X, True)
        COEFF_PROD[:] = get_coeff_prod(SIZE_X)