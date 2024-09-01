# implementation of Trivium with an alternative Boolean circuit 

# odd coordinates are used to store product of the form x_j x_{j+1}
# state[-1] is the key stream bit s

nA = 93;  rA = nA - 2
nB = 84;  rB = nB - 2
nC = 111; rC = nC - 2
len_A = nA + nB - 1
len_B = nB + nC - 1
len_C = nC + nA - 1
len_res = 1

def set_A(s, i, val): 
    s[2*i] = val
    
def set_B(s, i, val):
    s[2*(i + len_A)] = val 
    
def set_C(s, i, val):
    s[2*(i + len_A + len_B)] = val 
    
def set_prod_A(s, i, val): 
    s[2*i+ 1] = val
    
def set_prod_B(s, i, val):
    s[2*(i + len_A) + 1] = val 
    
def set_prod_C(s, i, val):
    s[2*(i + len_A + len_B) + 1] = val 
    
def get_initial_trivium_state(variables): 
    
    x = variables.gens_x()
    k = variables.gens_k()
    c = variables.gens_c()
    
    s = 2 * (len_A + len_B + len_C + len_res) * [c[0]]    
    for i in range(80):
        set_A(s, i, k[i])
    for i in range (80):
        set_B(s, i, x[i])
    for i in range(3):
        set_C(s, 111 - i - 1, c[1]) 
    return s

def get_smallest_bound(*args): 
    result = args[0]
    for arg in args[1:]:
        result = result.minimum(arg)
    return result

def trivium_round_function_bound(s, variables, index_round, index_step): 
    
    A = lambda i : s[2*i]
    B = lambda i : s[2*(i + len_A)]
    C = lambda i : s[2*(i + len_A + len_B)]
    prod_A = lambda i : s[2*i + 1]
    prod_B = lambda i : s[2*(i + len_A) + 1]
    prod_C = lambda i : s[2*(i + len_A + len_B) + 1]
    
    linear_a = lambda t : C(t + 65) + C(t + 110) + A(t + 68)
    linear_b = lambda t : A(t + 65) + A(t + 92)  + B(t + 77) 
    linear_c = lambda t : B(t + 68) + B(t + 83)  + C(t + 86)
    
    output = A(65) + A(92) + B(68) + B(83) + C(65) + C(110)
    s[-1] = output
    
    if index_round < rC+1 or index_step != 3: 
        mult_a = C(rC-1) * C(rC)
    else : 
        d1 = get_smallest_bound(B(rC+rB-1) * B(rC+rB) * B(rC+rB+1), 
                                prod_C(rC-1) * B(rC+rB+1), 
                                B(rC+rB-1) * prod_C(rC)) 
                 
        d2 = get_smallest_bound(linear_c(rC) * B(rC+rB) * B(rC+rB+1), 
                                linear_c(rC) * prod_C(rC))
                                    
        d3 = linear_c(rC+1) * C(rC-1)
                                  
        mult_a = get_smallest_bound(d1 + d2 + d3, C(rC-1) * C(rC))
    
    if index_round < rA+1 or index_step != 3: 
        mult_b = A(rA-1) * A(rA)
    else: 
        d1 = get_smallest_bound(C(rA+rC-1) * C(rA+rC) * C(rA+rC+1),
                                prod_A(rA-1) * C(rA+rC+1), 
                                C(rA+rC-1) * prod_A(rA))
                     
                     
        d2 = get_smallest_bound(linear_a(rA) * C(rA+rC) * C(rA+rC+1), 
                                linear_a(rA) * prod_A(rA))
                                    
        d3 = linear_a(rA+1) * A(rA-1)
        mult_b = get_smallest_bound(d1 + d2 + d3, A(rA-1) * A(rA))
         
    if index_round < rB+1 or index_step != 3: 
        mult_c = B(rB-1) * B(rB)
    else: 
        d1 = get_smallest_bound( A(rB+rA-1) * A(rB+rA) * A(rB+rA+1), 
                                 prod_B(rB-1) * A(rB+rA+1),
                                 A(rB+rA-1) * prod_B(rB))
                                    
        d2 = get_smallest_bound(linear_b(rB) *  A(rB+rA) * A(rB+rA+1), 
                                linear_b(rB) * prod_B(rB))
        d3 = linear_b(rB+1) * B(rB-1)
        mult_c = get_smallest_bound(d1 + d2 + d3, B(rB-1) * B(rB))
    
    tA = linear_a(0) + mult_a
    tB = linear_b(0) + mult_b
    tC = linear_c(0) + mult_c
    
    for i in range (len_A-1,0,-1): 
        set_A(s, i, A(i-1))
        set_prod_A(s, i, prod_A(i-1)) 
    set_A(s, 0, tA)
    set_prod_A(s, 0, mult_a)
    
    for i in range (len_B-1,0,-1): 
        set_B(s, i, B(i-1))
        set_prod_B(s, i, prod_B(i-1)) 
    set_B(s, 0, tB)
    set_prod_B(s, 0, mult_b)
    
    for i in range (len_C-1,0,-1): 
        set_C(s, i, C(i-1))
        set_prod_C(s, i, prod_C(i-1)) 
    set_C(s, 0, tC)
    set_prod_C(s, 0, mult_c)
    
def trivium_round_function_estimate(s, variables, index_round, index_step): 
    
    A = lambda i : s[2*i]
    B = lambda i : s[2*(i + len_A)]
    C = lambda i : s[2*(i + len_A + len_B)]
    prod_A = lambda i : s[2*i + 1]
    prod_B = lambda i : s[2*(i + len_A) + 1]
    prod_C = lambda i : s[2*(i + len_A + len_B) + 1]
    
    linear_a = lambda t : C(t + 65) + C(t + 110) + A(t + 68)
    linear_b = lambda t : A(t + 65) + A(t + 92)  + B(t + 77) 
    linear_c = lambda t : B(t + 68) + B(t + 83)  + C(t + 86)
    
    output = A(65) + A(92) + B(68) + B(83) + C(65) + C(110)
    s[-1] = output
    
    if index_round < rC+1 or index_step != 3: 
        mult_a = C(rC-1) * C(rC)
    else : 
        d1 = prod_C(rC-1) * B(rC+rB+1)    
        d2 = linear_c(rC) * prod_C(rC)
        d3 = linear_c(rC+1) * C(rC-1)
                                  
        mult_a = d1 + d2 + d3
    
    if index_round < rA+1 or index_step != 3: 
        mult_b = A(rA-1) * A(rA)
    else: 
        d1 = prod_A(rA-1) * C(rA+rC+1)       
        d2 = linear_a(rA) * prod_A(rA)                      
        d3 = linear_a(rA+1) * A(rA-1)
        mult_b = d1 + d2 + d3
         
    if index_round < rB+1 or index_step != 3: 
        mult_c = B(rB-1) * B(rB)
    else: 
        d1 = prod_B(rB-1) * A(rB+rA+1)                         
        d2 = linear_b(rB) * prod_B(rB)
        d3 = linear_b(rB+1) * B(rB-1)
        mult_c = d1 + d2 + d3
    
    tA = linear_a(0) + mult_a
    tB = linear_b(0) + mult_b
    tC = linear_c(0) + mult_c
    
    for i in range (len_A-1,0,-1): 
        set_A(s, i, A(i-1))
        set_prod_A(s, i, prod_A(i-1)) 
    set_A(s, 0, tA)
    set_prod_A(s, 0, mult_a)
    
    for i in range (len_B-1,0,-1): 
        set_B(s, i, B(i-1))
        set_prod_B(s, i, prod_B(i-1)) 
    set_B(s, 0, tB)
    set_prod_B(s, 0, mult_b)
    
    for i in range (len_C-1,0,-1): 
        set_C(s, i, C(i-1))
        set_prod_C(s, i, prod_C(i-1)) 
    set_C(s, 0, tC)
    set_prod_C(s, 0, mult_c)
    
param_trivium_bound = {
    'TOOL_VERSION': 'bound',
    'SIZE_X': 80,
    'SIZE_K': 80,
    'STATE_CONSTRUCTOR': get_initial_trivium_state,
    'ROUND_FUNCTION': trivium_round_function_bound,
    'NR_ROUNDS_STEP_1': 300,
    'NR_ROUNDS_STEP_2': 40,
    'NR_ROUNDS_MAX': 1152,
    'FILE_NAME': 'trivium_bound.csv',
    'BITS_TO_SAVE': -1,
}


param_trivium_estimate = {
    'TOOL_VERSION': 'estimate',
    'SIZE_X': 80,
    'SIZE_K': 80,
    'STATE_CONSTRUCTOR': get_initial_trivium_state,
    'ROUND_FUNCTION': trivium_round_function_estimate,
    'NR_ROUNDS_STEP_1': 300,
    'NR_ROUNDS_STEP_2': 40,
    'NR_ROUNDS_MAX': 1152,
    'FILE_NAME': 'trivium_estimate.csv',
    'BITS_TO_SAVE': -1,
}