#!/usr/bin/env python3
"""
The file with the main experiment instance. It is called from the main file for every overall iteration of the model.
"""

import json
import logging
import numpy as np
import pandas as pd

import population_generator


class Model:
    def __init__(self, parameters, output_filename, ident):
        """
        Initiates a model instance..

        Parameters
        ----------
        parameters : json file
            The file with the relevant parameters for the model.

        output_filename : str
            Provide the path to the file in which output should be stored excluding ending.

        ident : int
            Number of the iteration.

        Timing
        ------
        1. Set the loggers for the experiment.
        2. Read in the parameter file.
        3. Set up the experiment specification.
        4. Set up the state variables for tracking simulation results.
        """

        """Set loggers."""
        logging_filename = output_filename + '.log'
        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)
        logger.handlers = []
        terminal_handler = logging.StreamHandler()
        terminal_handler.setLevel(logging.WARNING)
        file_handler = logging.FileHandler(filename=logging_filename)
        file_handler.setLevel(logging.WARNING)
        standard_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        terminal_handler.setFormatter(standard_formatter)
        file_handler.setFormatter(standard_formatter)
        logger.addHandler(terminal_handler)
        logger.addHandler(file_handler)

        """Read in parameter file"""
        if type(parameters) == dict:
            self.__parameters = parameters
            logger.info('Imported parameters via dict')
        elif type(parameters) == str:
            f = open(parameters)
            if not f:
                logger.critical('Error, could not open parameter file:', parameters)
            self.__parameters = json.load(f)
            logger.warning('Imported parameters via str')
        else:
            logger.critical("ERROR: parameter file given in wrong form!")
            exit(1)

        """Set particular specification."""
        self.__ident = ident
        self.__outputfile_name = output_filename
        self.__timestep = 0
        self.__pop_generator = population_generator.PopulationGenerator(self.__parameters, logging_filename, self)
        self.__agents = self.__pop_generator.get_agents()

        """State variables for tracking results."""
        self.__total_return = []
        self.__returns_P = []
        self.__returns_NP = []
        self.__share_P =[]
        self.__share_NP = []
        self.__returns_NP_pc = []
        self.__returns_P_pc = []

    def run(self):
        """
        Runs the model.
        """
        params = self.__parameters
        self.record()
        for i in range(0, params["number_of_timesteps"]):
            self.__timestep = i
            logger.warning('Iteration %s: round %s of %s for file %s.',
                           str(self.__ident), str(self.__timestep), str(params['number_of_timesteps'] - 1),
                           self.__outputfile_name)
            self.update(i)
        self.save_data()

    def update(self, i):
        """
        The update procedure implemented at any time step.
        """
        agents_NP = [f for f in self.__agents if f.seed == 1]
        if i == 0:
            mean_NP = self.__parameters["fix_return_P"] - self.__parameters["yearly_cost_P"]
        else:
            mean_NP = np.mean([np.mean(f.get_wealth()[self.__parameters["retrospective_memory"]:]) for f in agents_NP])
        for f in self.__agents:
            f.choose_seed(mean_NP)  # TODO might be effect of activation sequence
            f.receive_income(len(agents_NP))
        self.record()

    def record(self):
        """
        Records the state variables of interest at the end of each time step.
        """
        self.__total_return.append(sum([f.get_wealth()[-1] for f in self.__agents]))
        agents_P = [f for f in self.__agents if f.seed == 0]
        agents_NP = [f for f in self.__agents if f.seed == 1]
        assert len(agents_P) + len(agents_NP) == len(self.__agents), \
            "Sum of different agent types should be {} but is {}.".format(
                len(self.__agents), (len(agents_P) + len(agents_NP)))
        self.__returns_P.append(sum([f.get_wealth()[-1] for f in agents_P]))
        self.__returns_NP.append(sum([f.get_wealth()[-1] for f in agents_NP]))
        self.__share_P.append(float(len(agents_P)) / len(self.__agents))
        self.__share_NP.append(1.0 - self.__share_P[-1])
        if len(agents_P) > 0:
            self.__returns_P_pc.append(self.__returns_P[-1] / len(agents_P))
        else:
            self.__returns_P_pc.append(0.0)
        if len(agents_NP) > 0:
            self.__returns_NP_pc.append(self.__returns_NP[-1] / len(agents_NP))
        else:
            self.__returns_NP_pc.append(0.0)

    def save_data(self):
        """
        Saves the results in a pandas data frame and stores data in hd5 format.
        """
        results_data = pd.DataFrame.from_items((["Total_return", self.__total_return],
                                                ["Returns_P", self.__returns_P],
                                                ["Returns_NP", self.__returns_NP],
                                                ["Returns_P_pc", self.__returns_P_pc],
                                                ["Returns_NP_pc", self.__returns_NP_pc],
                                                ["Share_P", self.__share_P],
                                                ["Share_NP", self.__share_NP]))
        data_name = self.__outputfile_name + "_data.h5"
        data_identification = "data_" + format(self.__ident, '03d')
        store = pd.HDFStore(data_name)
        store[data_identification] = results_data
        store.close()

    def get_agents(self):
        return self.__agents
