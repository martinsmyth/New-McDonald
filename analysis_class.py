#!/usr/bin/env python3
"""
Part of the analysis of the simulation output. Is called from analyze.py.
"""
import collections
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.style.use('ggplot')

__author__ = "Claudius Graebner"
__email__ = "graebnerc@uni-bremen.de"


class Results:
    """
    Provides the relevant plots. Should be called with the imported module that contains the output.
    Call "instance.provide_plot()" to get fig and axis specified. Then either save or do plt.show().
    Requires numpy as np, pyplot as plt and json.

    A nice possibility to plot results: x_axis: a parameter; y_axis the average result of this parameter setting.
    """
    def __init__(self, number_of_runs, parameter_file, output_title):
        self.parameters = json.load(open(parameter_file))
        self.name_of_run = str(output_title)
        self.name_of_datafile = output_title + "_data.h5"
        self.data_file = pd.HDFStore("output/" + self.name_of_datafile)
        names = self.get_data_names(len(self.data_file.keys()))
        self.variables_of_interest = self.data_file[names[0]].keys()
        self.stats_of_interest = ["mean", "sd", "10% quant", "90% quant"]
        results = collections.OrderedDict()
        for name in self.variables_of_interest:
            results[name] = self.make_zips([self.data_file[i][name] for i in names])

        self.dynamics_vars_interest_dict = dict()
        print("Variables considered: "),
        for name in self.variables_of_interest:
            print(name),
            intermediate_dict = collections.OrderedDict()
            intermediate_dict[self.stats_of_interest[0]] = pd.Series([np.mean(i) for i in results[name]])
            intermediate_dict[self.stats_of_interest[1]] = pd.Series([np.std(i) for i in results[name]])
            intermediate_dict[self.stats_of_interest[2]] = pd.Series([np.percentile(i, 10) for i in results[name]])
            intermediate_dict[self.stats_of_interest[3]] = pd.Series([np.percentile(i, 90) for i in results[name]])
            self.dynamics_vars_interest_dict[name] = pd.DataFrame(intermediate_dict)
        self.data_file.close()

    def provide_plot(self, id_run=1, spec=1):
        """
        Provides a visualization of the experimental results.

        Parameters
        ----------

        id_run : str, default: "001"
            Id of the run considered if function is called with spec=1. Indexing starts with 001.

        spec: int in (1,2)
            Specifies the kind of plot to be drawn:
                1 : An illustration of a single iteration.
                2 : Illustration of the dynamics and variability among several iterations.

        Returns
        -------
        Figure and axis instances
        """
        if spec == 1:
            """Returns one figure that summarizes the results of one single iteration."""
            data_ident = "data_" + format(int(id_run), '03d')
            print("Run considered: ", data_ident)
            self.data = pd.read_hdf("output/" + self.name_of_datafile, data_ident)
            cols = ["green", "red"]
            time = range(0, self.parameters['number_of_timesteps'] + 1)
            print(time, self.parameters['number_of_timesteps'] + 1, len(self.data["Total_return"]))
            time_longer = range(0, self.parameters['number_of_timesteps'] + 1)
            fig = plt.figure(figsize=(16, 9))
            ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
            ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
            title = "Identifier: " + self.name_of_run + " on " + str(datetime.datetime.now())
            fig.suptitle(title, verticalalignment='bottom', fontsize=12, fontweight='bold')
            
            print("Building figure 1.1/1.2"),
            ax1.plot(time, self.data["Total_return"], label='Total return', color='green')
            ax1.plot(time, self.data["Returns_P"], label='Returns for P', color='blue')
            ax1.plot(time, self.data["Returns_NP"], label='Returns for NP', color='red')
            ax1.legend(loc='best')
            ax1.set_title('Total returns', fontsize=16, alpha=0.7, ha='left', loc='left')
            ax1.set_xlabel('time')
            ax1.set_xticks(np.arange(0, len(time_longer), 10))
            ax1.set_ylabel('Total return')
            ax1.axhline(y=0.0, color='black', alpha=0.2)
            ax1.grid(True)

            print("Building figure 1.2/1.2"),
            ax3.plot(time, self.data["Share_P"], label='P', linewidth=1.5, alpha=0.8, color=cols[0])
            ax3.plot(time, self.data["Share_NP"], label='NP', linewidth=1.5, alpha=0.8, color=cols[1])
            ax3.legend(loc='best', ncol=7)
            ax3.set_title('Shares of seeds', fontsize=16, alpha=0.7, ha='left', loc='left')
            ax3.set_xlabel('time')
            ax3.set_xticks(np.arange(0, len(time_longer), int(0.2 * len(time))))
            ax3.set_ylabel('Shares')
            ax3.set_ylim(-0.05, 1.05)
            ax3.set_yticks(np.arange(0, 1.1, 0.1))
            ax3.axhline(y=1.0, color='black', alpha=0.2)
            ax3.axhline(y=0.0, color='black', alpha=0.2)
            ax3.grid(True)

            plt.grid(True)
            fig.set_tight_layout(True)
            return fig, ax1, ax3

        elif spec == 2:
            """
            Returns a plot illustrating average dynamics and variability of the strategy shares through all iterations.
            """
            print("Building figure 2.1/2.1..."),
            fig, ax = plt.subplots(figsize=(16, 9))
            x_axis = range(0, len(self.data['Share_P']))
            strategies = ['Share_P', 'Share_NP']
            cols = ["green", "red"]
            for i in range(len(strategies)):
                self.dynamics_vars_interest_dict[strategies[i]]['mean'].plot(label=str(strategies[i]), color=cols[i],
                                                                             linewidth=1.5, alpha=0.8)
                ax.fill_between(x_axis, self.dynamics_vars_interest_dict[strategies[i]]['10% quant'],
                                self.dynamics_vars_interest_dict[strategies[i]]['90% quant'],
                                facecolor=cols[i], alpha=0.1)
            ax.legend(loc='best')
            ax.set_title(' Shares of seed types', fontsize=16, alpha=0.7, ha='left', loc='left')
            ax.set_xlabel('time')
            ax.set_xticks(np.arange(0, len(x_axis), 5))
            ax.set_ylabel('share of strategies')
            ax.set_ylim(-0.05, 1.05)
            ax.set_yticks(np.arange(0, 1.1, 0.1))
            ax.axhline(y=1.0, color='black', alpha=0.2)
            ax.axhline(y=0.0, color='black', alpha=0.2)
            ax.grid(True)
            fig.set_tight_layout(True)
            print("...finished.")
            return fig, ax

        elif spec == 3:
            """
            Returns a plot illustrating average wealth and interaction dynamics and variability through all iterations.
            """
            print("Building figure 3.1/3.1..."),
            fig, ax = plt.subplots(figsize=(16, 9))
            x_axis = range(0, len(self.data['Returns_P']))
            strategies = ['Returns_P', 'Returns_NP']
            cols = ["green", "red"]
            for i in range(len(strategies)):
                self.dynamics_vars_interest_dict[strategies[i]]['mean'].plot(label=str(strategies[i]), color=cols[i],
                                                                             linewidth=1.5, alpha=0.8)
                ax.fill_between(x_axis, self.dynamics_vars_interest_dict[strategies[i]]['10% quant'],
                                self.dynamics_vars_interest_dict[strategies[i]]['90% quant'],
                                facecolor=cols[i], alpha=0.1)
            ax.legend(loc='best')
            ax.set_title(' Returns for the two groups', fontsize=16, alpha=0.7, ha='left', loc='left')
            ax.set_xlabel('time')
            ax.set_xticks(np.arange(0, len(x_axis), 5))
            ax.set_ylabel('returns')
            # ax.set_ylim(-0.05, 1.05)
            # ax.set_yticks(np.arange(0, 1.1, 0.1))
            # ax.axhline(y=1.0, color='black', alpha=0.2)
            ax.axhline(y=0.0, color='black', alpha=0.2)
            ax.grid(True)
            fig.set_tight_layout(True)
            print("...finished.")
            return fig, ax

        elif spec == 4:
            """
            Returns a plot illustrating average wealth and interaction dynamics and variability through all iterations.
            """
            print("Building figure 4.1/4.1..."),
            fig, ax = plt.subplots(figsize=(16, 9))
            x_axis = range(0, len(self.data['Returns_P_pc']))
            strategies = ['Returns_P_pc', 'Returns_NP_pc']
            cols = ["green", "red"]
            for i in range(len(strategies)):
                self.dynamics_vars_interest_dict[strategies[i]]['mean'].plot(label=str(strategies[i]), color=cols[i],
                                                                             linewidth=1.5, alpha=0.8)
                ax.fill_between(x_axis, self.dynamics_vars_interest_dict[strategies[i]]['10% quant'],
                                self.dynamics_vars_interest_dict[strategies[i]]['90% quant'],
                                facecolor=cols[i], alpha=0.1)
            ax.legend(loc='best')
            ax.set_title(' Returns for the two groups (per capita)', fontsize=16, alpha=0.7, ha='left', loc='left')
            ax.set_xlabel('time')
            ax.set_xticks(np.arange(0, len(x_axis), 5))
            ax.set_ylabel('returns')
            # ax.set_ylim(-0.05, 1.05)
            # ax.set_yticks(np.arange(0, 1.1, 0.1))
            # ax.axhline(y=1.0, color='black', alpha=0.2)
            ax.axhline(y=0.0, color='black', alpha=0.2)
            ax.grid(True)
            fig.set_tight_layout(True)
            print("...finished.")
            return fig, ax

        else:
            assert 3 > 4, 'Wrong input given!'

    def provide_statistics(self):
        """
        Provides summary statistics of the results. Returns pd.DataFrame
        """
        final_vars_of_interest = collections.OrderedDict()
        for var in self.stats_of_interest:
            final_vars_of_interest[var] = pd.Series(
                [round(self.dynamics_vars_interest_dict[name][var][199], 2) for name in self.variables_of_interest],
                index=self.variables_of_interest)
        final_vars_of_interest_df = pd.DataFrame(final_vars_of_interest)
        return final_vars_of_interest_df

    @staticmethod
    def give_runs(nb_of_runs, index='run', leading_zero=False):
        """
        :param nb_of_runs:
        :return: returns a list with the names of the runs as strings.
        """
        nb_of_runs = int(nb_of_runs)
        assert isinstance(nb_of_runs, int), "Nb of runs not provided and int, but as %s" % str(type(nb_of_runs))
        assert nb_of_runs >= 0, 'Number of runs must be positive.'
        if leading_zero == 0:
            runns = [index + '_' + str(i) for i in range(nb_of_runs)]
            return runns
        else:
            if nb_of_runs <= 10:
                runns = [index + '_0' + str(i) for i in range(nb_of_runs)]
                return runns
            else:
                nb_of_runs_0 = range(10)
                runns_0 = [index + '_0' + str(i) for i in nb_of_runs_0]
                runns_1 = [index + '_' + str(i) for i in range(10, nb_of_runs)]
                print('nb_of runs: %s; nb_of_runs_0: %s' % (str(nb_of_runs), str(nb_of_runs_0)))
                return runns_0 + runns_1

    @staticmethod
    def make_zips(liste):
        """
        Takes a list of lists as input and returns the zips of the lists.

        Parameters
        ----------
        liste : list
            List of of lists (or tuples).

        Returns
        -------
        fuck : list of tuples
            Equivalent to zip(liste), but returns list instead of zip, and works for list of lists as input.
            zip requires the lists as singular objects.
        """
        index = range(len(liste[0]))
        fuck = []
        for j in index:
            fucker = tuple(liste[i][j] for i in range((len(liste))))
            fuck.append(fucker)
        return fuck

    @staticmethod
    def get_data_names(n):
        """Returns a list of data names with len n, starting with data_001."""
        names = ["data_" + format(i, '03d') for i in range(1, n + 1)]
        assert len(names) == n, "Error in function, len should be {} but is {}.".format(n, len(names))
        return names
