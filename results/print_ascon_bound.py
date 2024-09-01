import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from print_trivium_bound import check_bounds, read_csv_file

def print_ascon_bound():
    file_path   = '../ANF_tool/ascon_bound.csv'

    df = read_csv_file(file_path)
    if df is None: 
        return
    incorrect_df, df = check_bounds(df)
    if not incorrect_df.empty: 
            print('Unexpected behavior')
            print(incorrect_df.to_string(index=False))
            
    min_round = df['round'].min()
    max_round = df['round'].max()
    for r in range(min_round, max_round+1): 
        for row in range(5): 
            round_row_df = df[(df['round'] == r) & (df['bit'] < 64*(row+1)) & (df['bit'] >= 64*row)]
            mode_first_non_full = round_row_df['first_non_full'].mode()[0]
            mode_last_non_full  = round_row_df['last_non_full'].mode()[0]
            print(f"round {r}, row {row}, for (almost) all bits [first deg not full - last deg not full] =  [{mode_first_non_full}-{mode_last_non_full}]")
            
            df_exception = round_row_df[
                (round_row_df['first_non_full'] != mode_first_non_full) |
                (round_row_df['last_non_full'] != mode_last_non_full)
            ]
            if not df_exception.empty:
                print(f'Exception for round {r}, row {row}')
                print(df_exception.to_string(index=False))
                
if __name__ == "__main__":
    print_ascon_bound()