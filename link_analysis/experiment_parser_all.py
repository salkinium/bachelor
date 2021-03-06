#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys
from link_analyzer import Analyzer
from link_file import LinkFile


if __name__ == "__main__":

    for arg in sys.argv[1:]:
        file = arg.split(",")
        decode = True if (len(file) > 1) else False
        print "Parsing file '{}' with decoder '{}'".format(file[0], decode)

        link_file = LinkFile(file[0], decode)

        analyzer_ab, analyzer_ba = link_file.get_analyzers()

        analyzer_ab.save_all_plots()
        analyzer_ba.save_all_plots()


