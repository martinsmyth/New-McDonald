import copy
import numpy as np
from scipy.stats import truncnorm


class Farmer:
    """
    The farmer class.
    """
    def __init__(self, initial_seed, parameter_file, model_instance):
        """
        Assume that seed=0 means the use of the P seeds and seed=1 means the use of the NP seed.
        """
        self.__wealth = [0.0]
        assert initial_seed in (0, 1), "Initial seed should be either 0 or one but is {}.".format(initial_seed)
        self.__seed = initial_seed
        self.__parameters = parameter_file
        self.__model = model_instance
        self.__neighborhood = None

    def choose_seed(self, mean_NP, firstround=0):
        if self.__parameters["model"] == "model_0":
            self.__seed = np.random.choice((0, 1), p=(self.__parameters["p_P"], 1-self.__parameters["p_P"]))
        elif self.__parameters["model"] == "model_1":
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
            The number of agents using the NP seeds at the beginning of the time period considered.
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

