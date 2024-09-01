import tool
from ascon import param_ascon_bound, param_ascon_estimate 
from trivium import param_trivium_bound, param_trivium_estimate 

if __name__ == "__main__":
    
    params = [param_ascon_bound, param_ascon_estimate, param_trivium_bound, param_trivium_estimate]

    for param in params : 
        print(f"Writing {param['FILE_NAME']}")
        print(f"number of rounds for step 1: {param['NR_ROUNDS_STEP_1']}")
        print(f"number if rounds for step 2: {param['NR_ROUNDS_STEP_2']}")
        print(f"total number of rounds analyzed: {param['NR_ROUNDS_MAX']}")
        tool.config_param(param)
        state = tool.get_initial_state()
        tool.apply_step_1(state)
        tool.apply_step_2(state)
        tool.apply_step_3(state)