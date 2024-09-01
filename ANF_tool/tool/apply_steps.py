import os
from .all_functionalities import *
from . import settings as s

def get_initial_state(): 
    variables = Variables.for_step_1()
    return s.STATE_CONSTRUCTOR(variables)

def apply_step_1(state): 
    variables = Variables.for_step_1()
    for r in range(s.NR_ROUNDS_STEP_1):
        for f in s.ROUND_FUNCTION: 
            f(state, variables, r, 1)
            
def apply_step_2(state):
    variables  = Variables.for_step_2() 
    state[:] = [ListMons.from_anf(p) for p in state]
    for r in range(s.NR_ROUNDS_STEP_1, 
                   s.NR_ROUNDS_STEP_1 + s.NR_ROUNDS_STEP_2):
        for f in s.ROUND_FUNCTION: 
            f(state, variables, r, 2)
            
def use_writer(state, r, writer): 
    for bit_index in s.BITS_TO_SAVE: 
        row = [r, bit_index] if len(s.BITS_TO_SAVE) > 1 else [r]
        row += state[bit_index].get_list_to_save()
        writer.writerow(row) 
    
 
def apply_step_3(state):
    
    if s.TOOL_VERSION == 'bound': 
        variables = Variables.for_step_3_bound()
        state[:] = [BoundNrMons.from_list_mons(p) for p in state]

    elif s.TOOL_VERSION =='estimate': 
        variables = Variables.for_step_3_estimate()
        state[:] = [EstimateNrMons.from_list_mons(p) for p in state]     
    else: 
        raise ValueError('Not the right name for tool_version.')

    s.config_auxiliary_arrays()
    
    with open(s.FILE_NAME, "w") as file:
        writer = csv.writer(file)
        labels = ["round", 'bit']  if len(s.BITS_TO_SAVE) > 1 else ["round"]
        labels += [f"{i}" for i in range(s.SIZE_X+1)]
        writer.writerow(labels)
        for r in range(s.NR_ROUNDS_STEP_1 + s.NR_ROUNDS_STEP_2, 
                    s.NR_ROUNDS_MAX): 
            use_writer(state, r, writer)
            for f in s.ROUND_FUNCTION: 
                f(state, variables, r, 3)
        use_writer(state, s.NR_ROUNDS_MAX, writer)