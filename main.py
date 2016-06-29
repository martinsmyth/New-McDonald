#!/usr/bin/env python3
"""
A computational experiment that is used to derive an algorithmic definition of an institution.
This file is the meta-function that implements the computational model by running several instances of the model
"""
import json
import logging
import model
import os
import shutil
import subprocess
import sys


__author__ = "Claudius Graebner"
__email__ = "graebnerc@uni-bremen.de"


def main():

    if len(sys.argv) < 3:
        print('Arguments missing! Usage: python main.py [parameterfile] [nb_iterations]')
        exit(1)
    parameter_filename = sys.argv[1]
    assert parameter_filename[:15] == 'specifications/', "Called jsons must be in directory specifications/"
    parameters = json.load(open(parameter_filename))
    """Initialize loggers to keep track of what happens in the model."""
    logging_filename = 'output/' + parameter_filename[15:-5] + '.log'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.WARNING)
    file_handler = logging.FileHandler(filename=logging_filename)
    file_handler.setLevel(logging.WARNING)
    standard_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    terminal_handler.setFormatter(standard_formatter)
    file_handler.setFormatter(standard_formatter)
    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)
    logger.info("Parameters loaded successfully from parameter file: {}".format(str(parameter_filename)))
    """Specify output directory."""
    output_filename = 'output/' + parameter_filename[15:-5]
    data_name = output_filename + "_data.h5"
    if os.path.isfile(data_name):
        os.rename(data_name, data_name + "_old")
    """Conduct the computational experiment."""
    iteration = int(sys.argv[2]) + 1
    for i in range(1, iteration):
        m = model.Model(parameters, output_filename, i)
        m.run()
    """Save the results."""
    logger.info('Successfully finished simulation. Copy %s ...', str(parameter_filename))
    src_param = parameter_filename
    dst_param = 'output/' + parameter_filename[15:]
    shutil.copy(src_param, dst_param)
    """Analyze the results."""
    logger.info('completed. Now calling analyze file...')
    analyze_call = 'python analyze.py ' + str(iteration) + ' ' + str(output_filename) + ' ' + str(dst_param) + ' ' + str(1)
    print(analyze_call)
    subprocess.call(analyze_call, shell=True)
    logger.info('Completed. Find the results in %s and the figures in the corresp sub-folder.', str(output_filename))

if __name__ == '__main__':
    main()
