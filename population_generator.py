#!/usr/bin/env python3
"""
Used to create the initial agent population. Is called from experiment.py.
"""
import logging
import networkx as nx
import farmer

__author__ = "Claudius Graebner"
__email__ = "graebnerc@uni-bremen.de"


class PopulationGenerator:
    """
    This class is used only to initialize the population. All relevant properties are set via the parameter file.
    """
    def __init__(self, parameter_file, logging_filename, model_instance):
        """
        Parameters
        ----------

        parameter_file : file
            The file that contains the parametrization of the model run.

        logging_filename : file
            The file to store the logs.

        model_instance : model.Model
            The instance of the associated model.
        """
        assert type(parameter_file) == dict, "Parameters given in the wrong format!"
        self.__logging_filename = logging_filename
        self.__params = parameter_file
        self.__model = model_instance
        self.__agents = []
        """Set up the logger."""
        self.logger_pop_gen = logging.getLogger(__name__)
        self.logger_pop_gen.setLevel(logging.INFO)
        if not len(self.logger_pop_gen.handlers):
            terminal_handler = logging.StreamHandler()
            terminal_handler.setLevel(logging.INFO)
            terminal_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            terminal_handler.setFormatter(terminal_formatter)
            self.logger_pop_gen.addHandler(terminal_handler)
            file_handler = logging.FileHandler(filename=self.__logging_filename)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger_pop_gen.addHandler(file_handler)

        self.init_population()
        self.logger_pop_gen.info('Successfully initiated a population.')
        self.make_neighborhoods(self.__agents)
        assert self.__agents[0].neighborhood != [], "Function make neighborhood did not work"
        self.logger_pop_gen.info('Successfully updated the network of the population.')

    def init_population(self):
        """
        Initializes the population.
        """
        number_of_agents = self.__params['number_of_farmers']
        init_nb_P = int(self.__params['initial_share_P'] * number_of_agents)
        init_nb_NP = number_of_agents - init_nb_P
        self.logger_pop_gen.info('We have %s P and %s NP agents.', str(init_nb_P), str(init_nb_NP))
        self.__agents = [farmer.Farmer(0, self.__params, self.__model) for i in range(init_nb_P)] + \
                        [farmer.Farmer(1, self.__params, self.__model) for j in range(init_nb_NP)]
        assert isinstance(self.__agents[0], farmer.Farmer), "Not farmer, but {}".format(type(self.__agents[0]))
        assert len(self.__agents) == number_of_agents, "Nb of agents should be {} but it is {}.".format(
            number_of_agents, len(self.__agents))

    def make_neighborhoods(self, list_of_agents):
        """
        Allocates the agents on a grip. A von Neumann neighborhood is assumed so every agent has four neighbors.
        """
        assert isinstance(list_of_agents, list), "list of agents not list but {}".format(type(list_of_agents))
        assert isinstance(list_of_agents[0], farmer.Farmer), \
            "Entries of list not farmer but {}".format(type(list_of_agents[0]))

        self.logger_pop_gen.warning('Initiated a grid neighborhood.')
        graph = nx.random_regular_graph(4, self.__params['number_of_farmers'])
        neighborhood_lists = [[] for i in range(self.__params['number_of_farmers'])]
        for tup in graph.edges():
            neighborhood_lists[tup[0]].append(tup[1])
            neighborhood_lists[tup[1]].append(tup[0])
        for i in range(len(self.__agents)):
            self.__agents[i].neighborhood = [self.__agents[j] for j in neighborhood_lists[i]]
            assert isinstance(self.__agents[i], farmer.Farmer), "An error in the list of agents."
            assert isinstance(self.__agents[i].neighborhood, list), "Neighborhood not given of list."
            assert isinstance(self.__agents[i].neighborhood[0], farmer.Farmer), \
                "Elements in neighborhood not agents."

    def get_agents(self):
        return self.__agents
