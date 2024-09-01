import pandas as pd 
import numpy as np
from print_trivium_bound import  read_csv_file
import os

def print_ascon_estimate(degs_for_round):
  
    file_path_res_tool   = '../ANF_tool/ascon_estimate.csv'
    file_path_res_exp    = '../exp_stat/ascon_stat_exp.csv'

    tool_df = read_csv_file(file_path_res_tool)
    exp_df = read_csv_file(file_path_res_exp)  
    if tool_df is None or exp_df is None: 
        return 
    
    exp_df = exp_df.groupby(['round', 'bit', 'degree'], as_index=False).sum()
    exp_df['p_exp'] = exp_df["N_mon_found"]/ exp_df["N_mon_tested"]
    
    tool_df = pd.melt(tool_df, id_vars=['round', 'bit'], var_name='degree', value_name='p_tool')
    tool_df['degree'] = tool_df['degree'].astype(int)
    merged_df = pd.merge(tool_df, exp_df, on=['round', 'bit', 'degree'], how='outer')

    data = []
    columns = ['round', 'row', 'd', 'p_min', 'p_mean','p_max', 'p_exp_min', 'p_exp_mean', 'p_exp_max', 'N_mon', 'N_keys']

    for round, degrees in degs_for_round.items(): 
        for row in range(5):
            for d in degrees: 
                
                sub_df = merged_df[  (merged_df['degree'] == d) 
                                & (merged_df['round'] == round)
                                & (merged_df['bit'] < 64 * (row +1))
                                & (merged_df['bit'] >=  64 * row)]
                data.append([round,
                            row,
                            d, 
                            sub_df['p_tool'].min(),
                            sub_df['p_tool'].mean(),
                            sub_df['p_tool'].max(), 
                            sub_df['p_exp'].min(), 
                            sub_df['p_exp'].mean(),
                            sub_df['p_exp'].max(),
                            sub_df['N_mon_tested'].max(),
                            sub_df['N_keys'].max()]) 
    pd.set_option('display.max_rows', None) 
    print(pd.DataFrame(data, columns = columns).to_string(index=False, float_format='%.4f'))
    
    
if __name__ == "__main__":
    
    degs_for_round = {
        3: list(range(2, 7)),
        4: list(range(4, 12)),
        5: list(range(16, 23)),
        6: list(range(41, 45)), 
    }
    
    print_ascon_estimate(degs_for_round)

    