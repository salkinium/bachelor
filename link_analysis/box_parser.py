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

import pandas as pd
import seaborn as sns
sns.set_style("whitegrid")
sns.set_style("ticks")

from matplotlib import rc
rc('mathtext', default='regular')

if __name__ == "__main__":

    for arg in sys.argv[1:]:

        values = {'date': [], 'tmote': [], 'tair': [], 'power': [], 'target': []}
        target = 30
        first_date = None
        # first_date = dateutil.parser.parse("2014-05-01 14:09:08.231")
        first_date = dateutil.parser.parse("2014-04-26 09:11:05.108")

        with open(arg, 'r') as linkfile:
            for line in linkfile:
                line = line.replace("\n", "")

                date = dateutil.parser.parse(line[:23].replace(',', '.'))
                if first_date == None:
                    first_date = date
                date = datetime(2014, 5, 1, 0)+(date - first_date)

                if "Setting air temperature" in line:
                    target = int(line[70:-1])
                elif "Environment" in line:
                    line_values = line[56:].split(" ")
                    values['date'].append(date)
                    values['target'].append(target)
                    # values['tair'].append(float(line_values[0][5:-1]))
                    # values['tmote'].append(float(line_values[1][6:-1]))
                    values['tair'].append(float(line_values[0][5:-1])*0.94+1.75)
                    values['tmote'].append(float(line_values[1][6:-1])*0.92+3.0)
                    values['power'].append(int(line_values[3][7:-1]))

        fig, ax = plt.subplots(1)
        ax.set_ylim(ymin=20, ymax=95)
        fig.set_size_inches(8 * 0.625, 0.625 * 1 * 5.5)

        ax2 = ax.twinx()

        ax2.set_ylim(ymin=0, ymax=100)
        ax2.set_ylabel("Power (%)", fontsize=18)
        ax.set_xlabel("Running time (hours)")
        ax.set_ylabel("Temperature ($^\circ$C)", fontsize=18)
        ax2.grid(b=False)
        ax.patch.set_visible(False)
        ax2.set_zorder(ax.get_zorder()-1)
        # ax.set_axisbelow(True)
        # ax.grid(b=False)
        # ax3.set_zorder(ax2.get_zorder() - 1)
        # ax3.patch.set_visible(False)
        # ax3.grid(b=False)

        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%-H'))

        power, = ax2.plot_date(values['date'], values['power'], 'b-')
        pylab.setp(power, alpha=1, linewidth=0.8)


        target, = ax.plot_date(values['date'], values['target'], 'k-')
        pylab.setp(target, alpha=0.9, linewidth=1)
        tair, = ax.plot_date(values['date'], values['tair'], 'g-')
        pylab.setp(tair, linewidth=1.75)
        tmote, = ax.plot_date(values['date'], values['tmote'], 'r-')
        pylab.setp(tmote, linewidth=2)


        # l = pylab.legend([power, target, tair, tmote],
        #              ["Heating Power", "Target Temperature", "Air Temperature", "Mote Temperature"],
        #              # loc=4,
        #              prop = {'size': 12})

        pylab.savefig(os.path.join(os.path.dirname(__file__), "{}_plot.pdf".format(arg)), bbox_inches='tight', pad_inches=0.1)
        # pylab.show()
