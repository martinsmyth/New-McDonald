#!/usr/bin/env python3
"""
The farmer class. It only provides the code for the farmers and contains methods for strategy switching and payoff.
"""
import copy
import numpy as np
from scipy.stats import truncnorm

__author__ = "Claudius Graebner"
__email__ = "graebnerc@uni-bremen.de"


class Farmer:
    """
    The farmer class.
    """
    def __init__(self, initial_seed, parameter_file, model_instance):
        """
        Assume that seed=0 means the use of the P seeds and seed=1 means the use of the NP seed.
        Parameters
        -----------
        initial_seed : int (0 or 1)
            The type of seed the farmer starts with. 0 stands for the proprietary and 1 for the non-proprietary seed.

        parameter_file : file
            The file containing the parameter setting for the model.

        model_instance : model.Model
            The instance of the associated model.
        """
        self.__wealth = [0.0]
        assert initial_seed in (0, 1), "Initial seed should be either 0 or one but is {}.".format(initial_seed)
        self.__seed = initial_seed
        self.__parameters = parameter_file
        self.__model = model_instance
        self.__neighborhood = None

    def choose_seed(self, mean_NP, firstround=0):
        """
        Parameters
        ----------
        mean_NP : float
            The average yield of the agents that use the NP seed.

        firstround : bool
            Is set to 1 if we are in the first time step in which farmers always decide at random.

        Description
        ------------
        Depending on the model type, one of the following procedure is implemented:
            Baseline model (model_0):
                Agents choose a type of seed at random.
            Extension 1: Here we distinguish three cases:
                A : The agents compare the fixed return of the proprietary seed with the average yield of all agents
                    that have used the non-proprietary alternative in the last k rounds (k is a parameter).
                B: The agents are located on a grid (with a von Neumann neighborhood) and compare the P payoff with
                    the average payoffs of their neighbors using the NP seed (again considering the previous k rounds).
                C: This case does not differ to case B, but agents put more weight on their own payoff in the previous
                    round (with a 50 per cent) weight.
            Extension 2 works as the first extension but this time the payoff of the NP seed is a function of the users.
        """
        if self.__parameters["model"] == "model_0":
            self.__seed = np.random.choice((0, 1), p=(self.__parameters["p_P"], 1-self.__parameters["p_P"]))
        elif self.__parameters["model"] in ("model_1", "model_2"):
            if firstround == 1:
                self.__seed = np.random.choice((0, 1), p=(self.__parameters["p_P"], 1 - self.__parameters["p_P"]))
            elif self.__parameters["model_1_case"] == "A":
                if (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) > mean_NP:
                    self.__seed = 0
                elif (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) < mean_NP:
                    self.__seed = 1
                else:
                    self.__seed = np.random.choice((0, 1), p=(0.5, 0.5))
            elif self.__parameters["model_1_case"] == "B":
                mean_NP = np.mean([np.mean(f.get_wealth()[self.__parameters["retrospective_memory"]:]) for f in self.__neighborhood if f.seed == 1])
                if (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) > mean_NP:
                    self.__seed = 0
                elif (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) < mean_NP:
                    self.__seed = 1
                else:
                    self.__seed = np.random.choice((0, 1), p=(0.5, 0.5))
            elif self.__parameters["model_1_case"] == "C":
                mean_NP = np.mean([np.mean(f.get_wealth()[self.__parameters["retrospective_memory"]:]) for f in self.__neighborhood if f.seed == 1])
                mean_NP = np.mean([mean_NP + self.__wealth[self.__parameters["retrospective_memory"]:]])
                #  TODO Maybe do this more rigorous
                if (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) > mean_NP:
                    self.__seed = 0
                elif (float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]) < mean_NP:
                    self.__seed = 1
                else:
                    self.__seed = np.random.choice((0, 1), p=(0.5, 0.5))
            elif self.__parameters["model_1_case"] == "D":
                raise Exception("Case D not yet implemented.")
                exit(1)
            else:
                raise Exception("No correct case specified.")
                exit(1)

    def receive_income(self, n):
        """
        Gives the agents their income.

        Parameters
        -----------

        n : int
            The number of agents using the NP seeds at the beginning of the time period considered. Needed to calculate
            the return in model extension 3.

        Description
        -----------

        In the baseline model or the first extension, the yield of the P value is fixed, and the NP value follows a
        truncated normal distribution (over positive reals) with given mean and variance.
        In the third extension (model_2) the return depends on the number of users:
            $$P = R_P * (n / N)$$
        This function entails that the P seed is better if only few agents are using the NP seed, but after a number
        of people decided to use the NP seed, this type of seed becomes better.
        """
        if self.__parameters["model"] == "model_0" or "model_1":
            if self.__seed == 0:
                self.__wealth.append(float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"])
            else:  # TODO: Due to the fact that P has a fixed cost every year, its mean is de facto lower than NP
                self.__wealth.append(self.positive_normal(self.__parameters["mean_return_NP"],
                                                          self.__parameters["var_return_NP"]))
        elif self.__parameters["model"] == "model_2":
            if self.__seed == 0:
                self.__wealth.append(float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"])
            else:
                self.__wealth.append((2*(float(self.__parameters["fix_return_P"]) - self.__parameters["yearly_cost_P"]))
                                     * (n / self.__parameters["number_of_farmers"]))

    @property
    def neighborhood(self):
        """getter of neighborhood"""
        return self.__neighborhood

    @neighborhood.setter
    def neighborhood(self, new_neighborhood):
        add_agents = copy.copy(new_neighborhood)
        #  TODO Should the agent herself be part of neighborhood
        #try:
        #    add_agents.remove(self)
        #except ValueError:
        #    pass
        assert isinstance(add_agents[0], Farmer)
        self.__neighborhood = add_agents
        assert self.__neighborhood is not None, "Neighborhood has not changed!"

    @staticmethod
    def positive_normal(mean, var):
        """
        A normal distribution of which negative values are censored.
        """
        a, b = -mean, mean
        x = truncnorm.rvs(a, b, loc=0, scale=var)
        x += mean
        return x

    @property
    def seed(self):
        return self.__seed

    def get_wealth(self):
        return self.__wealth

