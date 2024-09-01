import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import os

def read_csv_file(filename):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            return df
        except Exception as e:
            print(f"Error reading the file '{filename}': {e}")
    else:
        print(f"The file '{filename}' does not exist.")
        return None

def check_bounds(df): 
    """
    Checks whether the values in the specified DataFrame columns follow the expected order: 
    first zeros (representing the trivial bound 'n choose d'), then non-zero values 
    (representing a non-trival bound), and finally np.inf (representing the bound 0).
    Prints 
    Args: 
        df (DataFrame) : The input DataFrame with columns named 'round', 'bit', '0', '1', '2', etc. 
                         These numbered columns represent bounds computed by a tool for different 
                         degrees. The column 'd' (degree) contains the difference between the 
                         trivial bound and the bound computed by the tool. If the computed 
                         bound equals the trivial bound, the value np.inf is used to represent it.
    Returns: 
        (DataFrame, DataFrame): A pair of DataFrame objects containing rows of the DataFrame df. 
                                The first DataFrame contains the rows with unexpected behavior in the
                                computed bounds. The second DataFrame includes rows with the expected
                                behavior.
    """
 
    df = df.apply(pd.to_numeric, errors='coerce')
    columns_degree    = [col for col in df.columns if col not in ['round', 'bit']]
    columns_round_bit = [col for col in df.columns if col in ['round', 'bit']]

    
    def check_order(row):
        zero_found = False
        non_zero_found = False
        inf_found = False

        for value in row:

            if value == 0:
                if non_zero_found or inf_found:
                    return False 
                zero_found = True
            elif value != np.inf:
                if inf_found:
                    return False 
                non_zero_found = True
            elif value == np.inf:
                inf_found = True
            else:
                return False
        return True
        
    def get_non_zero_columns(row):
        non_zero_cols = row[(row != 0) & (row != np.inf)].index
        if len(non_zero_cols) > 0:
            first_non_zero = non_zero_cols[0]
            last_non_zero = non_zero_cols[-1]
        else:
            first_non_zero = last_non_zero = None
        return pd.Series([first_non_zero, last_non_zero], index=['first_non_full', 'last_non_full'])
    
    results = df[columns_degree].apply(check_order, axis=1)
    false_indices = results.index[~results]
    right_indices = results.index[results]
    incorrect_df = df.loc[false_indices]
    correct_df = df.loc[right_indices]
   
    round_bit_df = correct_df[columns_round_bit]
    non_zero_df = correct_df[columns_degree].apply(get_non_zero_columns, axis=1)
    correct_df = pd.concat([round_bit_df, non_zero_df], axis=1)
    correct_df = correct_df.dropna()
    
    return incorrect_df, correct_df

def print_trivium_bound(): 
    file_path   = '../ANF_tool/trivium_bound.csv'
    df = read_csv_file(file_path)
    if df is None: 
        return 
    
    incorrect_df, correct_df = check_bounds(df)
    if not incorrect_df.empty: 
        print('Unexpected behavior')
        print(incorrect_df.to_string(index=False))
    rounds = correct_df['round'].to_numpy()
    first_non_full = correct_df['first_non_full'].to_numpy()
    last_non_full = correct_df['last_non_full'].to_numpy()
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, first_non_full, color='blue', label='First degree non-full')
    plt.plot(rounds, last_non_full, color='red', label='Last degree non-full')
    plt.xlabel('Rounds (numbered from 1)')
    plt.ylabel('Degree')
    plt.title('First variant of the tool applied to Trivium')
    plt.ylim(0, 80)
    plt.yticks(range(0, 81, 10))
    plt.legend()
    plt.savefig('trivium_bound.png')
    
    pd.set_option('display.max_rows', None) 
    print(correct_df.to_string(index=False))
   
if __name__ == "__main__":
    print_trivium_bound()