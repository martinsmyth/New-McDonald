#!/usr/bin/env python3
"""
Analysis of the simulation output. Is called via the main procedure, but can also be called individually.
"""
import matplotlib.pyplot as plt
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
import sys

import analysis_class

__author__ = "Claudius Graebner"
__email__ = "graebnerc@uni-bremen.de"


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Arguments missing! '
              'Usage: python analyze.py [nb_iterations] [path to outputfile] [parameter_file] [run_id]')
        exit(1)
    nb_of_runs = sys.argv[1]
    output = sys.argv[2]
    parameter_file = sys.argv[3]
    id_run_ident = sys.argv[4]


def analyze(nb_of_runs, id_run=id_run_ident):
    figures = []
    merger = PdfFileMerger()

    print("output: ", output)
    output_title = str(output[7:])
    print("output title: ", output_title)
    results = analysis_class.Results(nb_of_runs, parameter_file, output_title)
    results.provide_plot(id_run=id_run, spec=1)
    path_res_1 = 'output/figures/' + output_title + '_results_1.pdf'
    plt.savefig(path_res_1, format='pdf')
    figures.append(path_res_1)
    plt.clf()
    results.provide_plot(id_run=id_run, spec=2)
    path_res_2 = 'output/figures/' + output_title + '_results_2.pdf'
    plt.savefig(path_res_2, format='pdf')
    figures.append(path_res_2)
    plt.clf()
    results.provide_plot(id_run=id_run, spec=3)
    path_res_3 = 'output/figures/' + output_title + '_results_3.pdf'
    plt.savefig(path_res_3, format='pdf')
    figures.append(path_res_3)
    plt.clf()
    results.provide_plot(id_run=id_run, spec=4)
    path_res_4 = 'output/figures/' + output_title + '_results_4.pdf'
    plt.savefig(path_res_4, format='pdf')
    figures.append(path_res_4)
    plt.clf()

    for filename in figures:
        merger.append(PdfFileReader(open(filename, 'rb')))
    name = 'output/figures/' + str(output[7:]) + '_results.pdf'
    merger.write(name)
    for filename in figures:
        os.remove(filename)
    #print("Start making table..."),
    #df = results.provide_statistics()
    #path_table = 'output/tables/' + output_title + '_table.tex'
    #with open(path_table, "w") as f:
    #    f.write(df.to_latex(column_format="lcccc"))
    #print("...finished.")

    # results.save_data()
    print("Success!")

if __name__ == '__main__':
    print('Start analysis')
    analyze(sys.argv[1])
