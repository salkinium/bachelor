# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from string_message import StringMessage
from link import Link
from link_analyzer import Analyzer
import sys
import time
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'experiment_control', 'rs'))
from rs import RSCoder


def enum(**enums):
    return type('Enum', (), enums)


class LinkFile:

    Selector = enum(AB=0, BA=1)

    def __init__(self, filename, coder_required=False):
        self.filename = filename

        self.id_a = "A"
        self.id_b = "B"

        self._links_ab = None
        self._links_ba = None
        self._coder = None
        self._coder_required = (coder_required == True)

    def _create_coder_from_message(self, msg):
        if self._coder_required and 'coder' in msg:
            coder_info = msg['coder'].split(",")
            if coder_info[0] == "rs":
                n, k = int(coder_info[1]), int(coder_info[2])
                print "Creating RSCoder({}, {})".format(n,k)
                return RSCoder(n, k)

    def read_all(self):
        print "Reading entire LinkFile, please wait..."

        messages = []
        print "Parsing messages..."
        start1 = time.time()
        with open(self.filename, 'r') as linkfile:
            for i, line in enumerate(linkfile):
                try:
                    message = StringMessage(line)
                    messages.append(message)
                except:
                    print i + 1,
                if (i + 1) % 1000 == 0:
                    print i + 1
                elif (i + 1) % 10 == 0:
                    sys.stdout.write('.')
        print "\nDone in {}s".format(time.time() - start1)

        links = []
        link = None
        print "Linking messages..."
        start = time.time()
        for i, msg in enumerate(messages):
            try:
                if msg.is_transmission:
                    if self._coder == None:
                        self._coder = self._create_coder_from_message(msg)

                    link = Link(msg, self._coder)
                    links.append(link)
                elif msg.is_reception:
                    if link != None:
                        link.add_rx(msg)
            except:
                print i+1,
            if (i + 1) % 100 == 0:
                print i + 1
            else:
                sys.stdout.write('.')
        print "\nDone in {}s".format(time.time() - start)

        self.id_a = links[0].tx['id']
        print "Separating links by ids..."
        start = time.time()
        for link in links:
            if link.tx['id'] == self.id_a:
                for rx in link.valid_rx:
                    self.id_b = rx['id']
                    break

        self._links_ab = []
        self._links_ba = []

        for link in links:
            if link.tx['id'] == self.id_a:
                # transmitting from 0 to 1
                self._links_ab.append(link)
            else:
                self._links_ba.append(link)
        print "Done in {}s".format(time.time() - start)

        print "Done reading LinkFile in {}s".format(time.time() - start1)

    @property
    def links_ab(self):
        if self._links_ab == None:
            self.read_all()
        return self._links_ab

    @property
    def links_ba(self):
        if self._links_ba == None:
            self.read_all()
        return self._links_ba

    def get_links_for_selector(self, selector):
        if selector == LinkFile.Selector.AB:
            return self.links_ab
        elif selector == LinkFile.Selector.BA:
            return self.links_ba

    def get_string_for_selector(self, selector):
        if selector == LinkFile.Selector.AB:
            return self.string_ab
        elif selector == LinkFile.Selector.BA:
            return self.string_ba

    @property
    def string_ab(self):
        return "{}-{}".format(self.id_a, self.id_b)

    @property
    def string_ba(self):
        return "{}-{}".format(self.id_b, self.id_a)

    def get_analyzer_ab(self):
        return Analyzer(self, LinkFile.Selector.AB, self.filename)

    def get_analyzer_ba(self):
        return Analyzer(self, LinkFile.Selector.BA, self.filename)

    def get_analyzers(self):
        return self.get_analyzer_ab(), self.get_analyzer_ba()


    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("LinkFile( {} )\n".format(self.filename))
