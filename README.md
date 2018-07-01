# Portfolio weight calculator assignment

##### Author: Yaroslav Hovorunov
##### License: MIT

Calculates weights of base funds (assets) in portfolio(s). Supports graphs
when base fund is included in root fund through through complex path. Detects
loops in data to prevent infinite looping or incorrect calculations.

Expects CSV file for input of the following format:

    A,B,1000
    A,C,2000
    B,D,500
    B,E,250
    B,F,250
    C,G,1000
    C,H,1000

###Usage:
    weight_calculator.py [-h] [-v] data_file
    
    positional arguments:
      data_file            A .csv file containing fund data to act on.
    
    optional arguments:
      -h, --help           show this help message and exit
      -v, --verbose        increase log verbosity
