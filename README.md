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

Each line like A,B,100 means value of fund B in fund A is 1000.
Optional 4th column containing end market values of funds is possible. Example:

    A,B,1000,1009
    A,C,2000,1994
    B,D,500,505
    B,E,250,253
    B,F,250,251
    C,G,1000,994
    C,H,1000,1000

Returns csv data representing weights of each base fund in each rot fund found. If end
market value is provided 4th column will contain weighted returns. Example or return data:

    A,D,0.167,2.222
    A,E,0.083,1.333
    A,F,0.083,0.444
    A,G,0.333,-3.000
    A,H,0.333,0.000 

### Usage:

    weight_calculator.py [-h] [-v] data_file
    
    positional arguments:
      data_file            A .csv file containing fund data to act on.
    
    optional arguments:
      -h, --help           show this help message and exit
      -v, --verbose        increase log verbosity
