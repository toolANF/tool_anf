This repository contains a tool for analyzing the polynomial representations of symmetric cryptographic primitives. It also includes experiments on the initialization phases of TRIVIUM and ASCON-128.

The code is divided into three parts:

1. **ANF_tool**: Implementation of the tool using Python and Sagemath.
2. **exp_stat**: Code for randomly drawing monomials and testing whether they belong to a specific algebraic normal form.
2. **results**: Output tables comparing the tool's estimated average number of monomials (see **ANF_tool**) with experimental values calculated from a sample of monomials (see **exp_stat**).

## Tool 
The folder `ANF_tool` contains an implementation of the tool in Python using Numpy and SageMath. To test it on TRIVIUM and ASCON, run the Python script `test.py`.  Results are written in the files `ascon_bound.csv`, `ascon_estimate.csv`, `trivium_bound.csv` and `trivium_estimate.csv`, 

## Experimental statistics 
The folder `exp_stat` contains a program to randomly draw monomials and to test whether they belong to the algebraic normal forms associated to TRIVIUM or ASCON-128. To run this code, type `make run`. You can modify the function calls to `ascon_draw_cubes` and `trivium_draw_cubes` in the file `experiments.cpp` to change the number of monomials to be drawn and their degree. Each call uses one random key. Results are written in the files `ascon_stat_exp.csv` and `trivium_stat_exp.csv`.

## Results
The folder `results` contains Python scripts using Pandas to better visualize the results on TRIVIUM and ASCON.

## How to analyze a new cipher
To analyze a new cipher, write a Python script with the  cipher's parameters stored in a dictionary. The dictionary entries should be : 
- `TOOL_VERSION` (string): 'estimate' or 'bound', depending on the variant of the tool. 
- `SIZE_X` (int): Number of public variables
- `SIZE_K` (int): Number of secret variables
- `STATE_CONSTRUCTOR` (function) : See below for the required function format.
- `ROUND_FUNCTION` (function or tuple of functions): See below for the required function format.
- `NR_ROUNDS_STEP_1` (int): Number of rounds for the first step, which computes the algebraic normal forms.
- `NR_ROUNDS_STEP_2` (int): Number of rounds for the second step, which computes the lists of monomials. 
- `NR_ROUNDS_MAX` (int): Total number of rounds to be analyzed.
- `FILE_NAME` (string): Name of the file to store the results. 
- `BITS_TO_SAVE` (int,range, or tuple of int): Indexes of the bits to be analysed at each round. 
### Warning 
1. The function associated with the key `STATE_CONSTRUCTOR` must always follow this format: 
```python 
def get_cipher_initial_state(variables)->list: 
    """
    Initialize a state with public and secret variables. 
    Args:
        variables (Variables object): Used to access public variables, secret variables and constants. 
    Returns:
        list : Represents the state.
    """
    x = variables.gens_x() # tuple storing the public variables
    k = variables.gens_k() # tuple storing the secret variables
    c = variables.gens_c() # tuple storing the constants 0 and 1
    # Add your code here, e.g.:
    state = [x[i] for i in range(128)] + [k[i] for i in range(128)]
    return state
```
2. The function(s) associated with the key `ROUND_FUNCTION` must always follow this format: 
```python 
def function(state, variables, index_round, index_step)->None:
    """ Update the state. 
    Args:
        state (list): Internal state. Add bits if you also want to store output bits.
        variables (Variables object): See above.
        index_round (int): Round index, numbered from 0. 
        index_step (int): Current step of the tool (1, 2 or 3).
    """  
    # Code to update the state
``` 