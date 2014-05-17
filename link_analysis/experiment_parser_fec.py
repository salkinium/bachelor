#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys
from fec_plotter import FEC_Plotter


if __name__ == "__main__":

    plotter = FEC_Plotter(sys.argv[2:], "../../hauser_data/simulation/fec_scheme_{}".format(sys.argv[1]))

    plotter.save_throughput_plot()



