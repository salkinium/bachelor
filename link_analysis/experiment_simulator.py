#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys
from link_file import LinkFile
from simulator import Simulator

if __name__ == "__main__":

    payload_string = sys.argv[1]
    link_file = LinkFile(sys.argv[2])
    log_file = sys.argv[2] + ".simulation.log"

    print "\nsimulating A->B"
    simulator_ab = Simulator(link_file.links_ab, log_file, 10)
    simulator_ab.simulate(payload_string)

    print "\nsimulating B->A"
    simulator_ba = Simulator(link_file.links_ba, log_file, 10)
    simulator_ba.simulate(payload_string)






