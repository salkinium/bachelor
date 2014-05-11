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
import time

if __name__ == "__main__":

    properties = {'payload': None,
                  'input': None,
                  'output': None,
                  'window': 1}

    parsed = {}
    for arg in sys.argv[1:]:
        try:
            prop, value = arg.split("=")
            parsed[prop] = value
        except:
            print "Invalid argument: '{}'".format(arg)
            exit(-1)

    properties.update(parsed)

    if properties['payload'] == None:
        print "You need to specify a new payload using 'payload='"
        exit(-1)

    if properties['input'] == None:
        print "You need to specify an input log using 'input='"
        exit(-1)

    try:
        properties['window'] = int(properties['window'])
    except:
        print "Invalid window argument: '{}'".format(properties['window'])
        exit(-1)

    if properties['output'] == None:
        properties['output'] = "{}-simulation-{}-{}.log".format(properties['input'], properties['payload'][:15], properties['window']).replace(",", "_").replace("(", "_")
        print "Output file not specified, will use '{}".format(properties['output'])

    start = time.time()

    link_file = LinkFile(properties['input'])

    simulator_ab = Simulator(link_file.links_ab, properties['output'], properties['window'])
    simulator_ba = Simulator(link_file.links_ba, properties['output'], properties['window'])

    print "\nsimulating A->B"
    simulator_ab.simulate(properties['payload'])

    print "\nsimulating B->A"
    simulator_ba.simulate(properties['payload'])

    print "Done in {}s.".format(time.time() - start)






