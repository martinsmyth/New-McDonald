#!/usr/bin/env bash
"""
This script calls the model with all the .json files in a directory called 'json2go'
The main.py file must be in the same directory as the directory 'json2go'
The results will be stored in a folder 'output' which must contain a folder 'figures':
main.py
specifications/
output/figures
output/tables

The default value for the number of iterations is 50, but it can be changed through the optional first argument.

The script requires Python 3 and the package 'PyPDF2'. This can be be installed via:
pip install pypdf2

For non Mac machines the first line must probably be changed and line 34 changed into python3
"""
source activate py3k
iterations=50 # Default number of iterations

if [ $# -eq 0 ]
  then
    echo "No arguments supplied. Using default number of iterations: $iterations"
elif [ $# -eq 1 ]
  then
    iterations=$1
    echo "Number of iterations supplied: $iterations"
else
    echo "This script can handle one zero or one argument (for the number of iterations)."
    exit 1
fi

echo "Run all simulation for $iterations times with all json files in directory json2go"

for i in specifications/*.json; do python main.py $i $iterations; done

echo "Finished Script"