#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys
import os
import pylab
import dateutil
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib import rc
import csv

rc('mathtext', default='regular')

# ./baudrate_parser.py ../../hauser_data/clock_drift/reboot_drift.csv ../../hauser_data/clock_drift/Baudrate_Error.csv ../../hauser_data/clock_drift/correction_error.csv

def get_values(file, start_row, rows, temperature_column, value_column):
    values = {'temperature': [], 'values': []}

    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        index = 0
        for row in reader:
            index += 1
            if index <= start_row:
                continue
            if index > start_row + rows:
                break

            print row
            values['temperature'].append(row[temperature_column])
            values['values'].append(row[value_column])

    values['temperature'] = map(float, values['temperature'])
    values['values'] = map(float, values['values'])

    return values

def plot_values(ax, values, color='k'):
    plot = ax.plot(values['temperature'], values['values'], '{}-'.format(color),
                   values['temperature'], values['values'], '{}o'.format(color))
    pylab.setp(plot[0], linewidth=2)

    return plot


def plot_table_values(ax, values, color='k', pol=1):
    fit = pylab.polyfit(values['temperature'], values['values'], pol)
    fit_fn = pylab.poly1d(fit)
    plot = ax.plot(values['temperature'], fit_fn(values['temperature']), '{}-'.format(color),
                   values['temperature'], values['values'], '{}o'.format(color))
    pylab.setp(plot[0], linewidth=2)

    return plot

def plot_dco_values(ax, values, color='k'):
    interpol1 = {'temperature': values['temperature'][0:7], 'values': values['values'][0:7]}
    fit1 = pylab.polyfit(interpol1['temperature'], interpol1['values'], 1)
    print 'm={} b={}'.format(fit1[0], fit1[1])
    fit_fn1 = pylab.poly1d(fit1)

    interpol2 = {'temperature': values['temperature'][6:14], 'values': values['values'][6:14]}
    fit2 = pylab.polyfit(interpol2['temperature'], interpol2['values'], 1)
    print 'm={} b={}'.format(fit2[0], fit2[1])
    fit_fn2 = pylab.poly1d(fit2)

    plot = ax.plot(interpol1['temperature'], fit_fn1(interpol1['temperature']), 'k-',
                   interpol2['temperature'], fit_fn2(interpol2['temperature']), 'k-',
                    # values['temperature'], values['values'], '{}-'.format(color),
                   values['temperature'], values['values'], '{}o'.format(color))
    pylab.setp(plot[0], linewidth=2)
    pylab.setp(plot[1], linewidth=2)

    return plot

def plot_linear_regression_values(ax, values, color='k'):
    fit = pylab.polyfit(values['temperature'], values['values'], 1)
    print 'm={} b={}'.format(fit[0], fit[1])
    fit_fn = pylab.poly1d(fit)
    plot = ax.plot(values['temperature'], fit_fn(values['temperature']), '{}-'.format(color),
                   values['temperature'], values['values'], '{}o'.format(color))
    pylab.setp(plot[0], linewidth=2)

    return plot

if __name__ == "__main__":

    reboot_file = sys.argv[1]
    reboot_dco_error = get_values(reboot_file, 11, 14, 3, 6)

    print reboot_dco_error

    baudrate_file = sys.argv[2]
    baudrate_115200_error = get_values(baudrate_file, 10, 15, 3, 6)
    baudrate_57600_error = get_values(baudrate_file, 32, 15, 3, 6)
    baudrate_19200_error = get_values(baudrate_file, 48, 15, 3, 6)
    baudrate_4800_error = get_values(baudrate_file, 64, 15, 3, 6)

    print baudrate_115200_error
    print baudrate_57600_error
    print baudrate_19200_error
    print baudrate_4800_error

    baudrate_115200_expected_inverse = get_values(baudrate_file, 5, 26, 3, 8)
    baudrate_115200_real_inverse = get_values(baudrate_file, 5, 26, 3, 13)

    print baudrate_115200_expected_inverse
    print baudrate_115200_real_inverse

    correction_file = sys.argv[3]
    correction_115200_low_start_error = get_values(correction_file, 7, 33, 3, 6)
    correction_115200_high_start_error = get_values(correction_file, 42, 33, 3, 6)

    print correction_115200_low_start_error
    print correction_115200_high_start_error

    # plot four baudrate errors
    fig, ax = plt.subplots(1)
    ax.set_xlim(xmin=15, xmax=95)

    b115200_line, b115200_dot = plot_linear_regression_values(ax, baudrate_115200_error, 'k')
    b57600_line, b57600_dot = plot_linear_regression_values(ax, baudrate_57600_error, 'b')
    b19200_line, b19200_dot = plot_linear_regression_values(ax, baudrate_19200_error, 'r')
    b4800_line, b4800_dot = plot_linear_regression_values(ax, baudrate_4800_error, 'g')

    ax.set_ylabel("Relative Error (%)", fontsize=16)
    ax.set_xlabel("Temperature ($^\circ$C)", fontsize=16)
    ax.grid(b=True, which='major', color='0.66', linestyle='-')
    ax.axhline(5, linestyle='--', color='0.33', linewidth=2)
    ax.axhline(-5, linestyle='--', color='0.33', linewidth=2)
    ax.set_axisbelow(True)

    pylab.legend([b4800_line, b19200_line, b115200_line, b57600_line],
                 ["4800 Baud", "19200 Baud", "115200 Baud", "57600 Baud"],
                 prop = {'size': 16})

    pylab.savefig(os.path.join(os.path.dirname(__file__), "{}_baudrate_error.pdf".format(baudrate_file)))
    print (-0.364828571429 - 0.36455 - 0.361257142857 - 0.378014285714) / 4.0

    # plot dco error
    fig2, ax2 = plt.subplots(1)
    ax2.set_ylim(ymin=-25, ymax=15)
    ax2.set_xlim(xmin=20, xmax=95)
    dco_error_line= plot_dco_values(ax2, reboot_dco_error, 'k')

    ax2.set_ylabel("Relative Error (%)", fontsize=16)
    ax2.set_xlabel("Temperature ($^\circ$C)", fontsize=16)
    ax2.grid(b=True, which='major', color='0.66', linestyle='-')
    ax2.axhline(5, linestyle='--', color='0.33', linewidth=2)
    ax2.axhline(-5, linestyle='--', color='0.33', linewidth=2)
    ax2.set_axisbelow(True)

    pylab.savefig(os.path.join(os.path.dirname(__file__), "{}_dco_error.pdf".format(reboot_file)))

    # plot inverse table
    fig3, ax3 = plt.subplots(1)
    # ax3.set_ylim(ymin=-25, ymax=15)
    ax3.set_xlim(xmin=-10, xmax=125)
    # baudrate_table_line = plot_table_values(ax3, baudrate_115200_expected_inverse, 'b', 2)
    baudrate_table_line = plot_table_values(ax3, baudrate_115200_real_inverse, 'k', 1)

    ax3.set_ylabel("Baudrate (kbps)", fontsize=16)
    ax3.set_xlabel("Temperature ($^\circ$C)", fontsize=16)
    ax3.grid(b=True, which='major', color='0.66', linestyle='-')
    ax3.axhline(115.200, linestyle='-', color='0.33', linewidth=1.5, zorder=1)
    ax3.set_axisbelow(True)

    pylab.savefig(os.path.join(os.path.dirname(__file__), "{}_table.pdf".format(baudrate_file)))

    # plot correction error
    fig4, ax4 = plt.subplots(1)
    ax4.set_ylim(ymin=-25, ymax=15)
    ax4.set_xlim(xmin=20, xmax=95)
    correction_high = plot_values(ax4, correction_115200_high_start_error, 'b')
    correction_low = plot_values(ax4, correction_115200_low_start_error, 'k')

    ax4.set_ylabel("Relative Error (%)", fontsize=16)
    ax4.set_xlabel("Temperature ($^\circ$C)", fontsize=16)
    ax4.grid(b=True, which='major', color='0.66', linestyle='-')
    ax4.axhline(5, linestyle='--', color='0.33', linewidth=2)
    ax4.axhline(0, linestyle='-', color='0.33', linewidth=1, zorder=1)
    ax4.axhline(-5, linestyle='--', color='0.33', linewidth=2)
    ax4.set_axisbelow(True)

    pylab.legend([correction_low[0], correction_high[0]],
                 ["Reboot at $24^{\circ}$C", "Reboot at $88^{\circ}$C"],
                 prop={'size': 16})

    pylab.savefig(os.path.join(os.path.dirname(__file__), "{}_correction_error.pdf".format(correction_file)))


