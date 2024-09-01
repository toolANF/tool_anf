
def get_initial_ascon_state(variables):
    x = variables.gens_x()
    k = variables.gens_k()
    c = variables.gens_c()
    
    IV_ASCON_128 = 0x80400c0600000000  
    IV = []
    for i in range (64): 
        if (IV_ASCON_128 & (0x1 << i)):
            IV.append(c[1])
        else : 
            IV.append(c[0])
    return IV + [k[i] for i in range(128)] + [x[i] for i in range(128)]

def apply_ascon_add_round_constant(s, variables, index_round, index_step):
    
    c = variables.gens_c()
    ascon_round_constants = (0xf0, 0xe1, 0xd2, 0xc3,
                             0xb4, 0xa5, 0x96, 0x87, 
                             0x78, 0x69, 0x5a, 0x4b)
    for i in range(8): 
        if (ascon_round_constants[index_round] >> i) & 1: 
            s[(2 << 6) + i] = s[(2 << 6) + i] + c[1]
            
def apply_ascon_sbox_layer(s, variables, index_round, index_step):  
    
    c = variables.gens_c()
    
    for col in range(64): 
        x0 = s[(0 << 6) + col]
        x1 = s[(1 << 6) + col]
        x2 = s[(2 << 6) + col]
        x3 = s[(3 << 6) + col]
        x4 = s[(4 << 6) + col]

        s[(0 << 6) + col] = x2*(x1 + c[1]) + x0*(c[1]+x1) + x1*(x4+c[1]) + x3
        s[(1 << 6) + col] = x0 + x4 + x3*(x2+c[1]) + x2*(x1+c[1]) + x1*(x3+c[1])
        s[(2 << 6) + col] = x4*(x3+c[1]) + x2 + x1 + c[1]
        s[(3 << 6) + col] = x1 + x2 + x0*(c[1]+x4) + x3*(c[1]+x0) + x4
        s[(4 << 6) + col] = x3 + x1*(c[1]+x0) + x4*(x1+c[1])
        
def apply_ascon_linear_layer(s, variables, index_round, index_step): 
    s[0 : 1 << 6]      = [s[i] + s[(i + 19) % 64] + s[(i + 28) % 64] for i in range(64)]
    s[1 << 6 : 2 << 6] = [s[(1 << 6) + i] + s[(1 << 6) + (i + 61) % 64] + s[(1 << 6) + (i + 39) % 64] for i in range(64)] 
    s[2 << 6 : 3 << 6] = [s[(2 << 6) + i] + s[(2 << 6) + (i + 1)  % 64] + s[(2 << 6) + (i + 6)  % 64] for i in range(64)]
    s[3 << 6 : 4 << 6] = [s[(3 << 6) + i] + s[(3 << 6) + (i + 10) % 64] + s[(3 << 6) + (i + 17) % 64] for i in range(64)]
    s[4 << 6 : 5 << 6] = [s[(4 << 6) + i] + s[(4 << 6) + (i + 7)  % 64] + s[(4 << 6) + (i + 41) % 64] for i in range(64)]
    
ascon_round_function = (apply_ascon_add_round_constant,
                        apply_ascon_sbox_layer, 
                        apply_ascon_linear_layer)

param_ascon_bound = {
    'TOOL_VERSION': 'bound',
    'SIZE_X': 128,
    'SIZE_K': 128,
    'STATE_CONSTRUCTOR': get_initial_ascon_state,
    'ROUND_FUNCTION': ascon_round_function,
    'NR_ROUNDS_STEP_1': 1,
    'NR_ROUNDS_STEP_2': 1,
    'NR_ROUNDS_MAX': 4,
    'FILE_NAME': 'ascon_bound.csv',
    'BITS_TO_SAVE': range(320),
}


param_ascon_estimate = {
    'TOOL_VERSION': 'estimate',
    'SIZE_X': 128,
    'SIZE_K': 128,
    'STATE_CONSTRUCTOR': get_initial_ascon_state,
    'ROUND_FUNCTION': ascon_round_function,
    'NR_ROUNDS_STEP_1': 1,
    'NR_ROUNDS_STEP_2': 1,
    'NR_ROUNDS_MAX': 4,
    'FILE_NAME': 'ascon_estimate.csv',
    'BITS_TO_SAVE': range(320),
}

