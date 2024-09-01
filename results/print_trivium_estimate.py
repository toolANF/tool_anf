import pandas as pd 
import numpy as np
from print_trivium_bound import  read_csv_file
import os


def print_trivium_estimate(degs_for_round): 
    
    file_path_res_tool   = '../ANF_tool/trivium_estimate.csv'
    file_path_res_exp    = '../exp_stat/trivium_stat_exp.csv'
    
    tool_df = read_csv_file(file_path_res_tool)
    exp_df = read_csv_file(file_path_res_exp)  
    if tool_df is None or exp_df is None: 
        return     
    
    # exp_df 
    exp_df = exp_df.groupby(['round', 'degree'], as_index = False).sum()
    exp_df.to_csv(file_path_res_exp, index=False) # compile experimental results
    exp_df['p_exp'] = exp_df['N_mon_found']/exp_df["N_mon_tested"]
    
    for round, degrees in degs_for_round.items(): 
        
        # results with the tool
        sub_tool_df = tool_df[['round'] + [str(c) for c in degrees]]      
        sub_tool_df = sub_tool_df[sub_tool_df['round'] == int(round)]
        sub_tool_df = sub_tool_df.drop(columns=['round'])
        sub_tool_df.index = ['p_tool']
        sub_tool_df.columns = sub_tool_df.columns.astype(int)

   
        # experimental results  
        sub_exp_df = exp_df[exp_df['round'] == int(round)] 
        sub_exp_df = sub_exp_df.set_index('degree')
        sub_exp_df = sub_exp_df.drop(columns=['round', 'N_mon_found'])
        sub_exp_df = sub_exp_df.transpose()
        sub_exp_df = sub_exp_df.reindex(columns=degrees)
        print(f"ROUND {round}:")
        combined = pd.concat([sub_tool_df, sub_exp_df])
        print(combined.to_string(float_format='%.4f'), '\n')

    
    

if __name__ == "__main__":
    
    degs_for_round = {
        425: list(range(1, 8)),
        510: list(range(3, 7)),
        550: list(range(5, 9)),
        600: list(range(7, 13)),
        650: list(range(12, 20)),
    }

    print_trivium_estimate(degs_for_round)