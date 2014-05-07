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

class LinkFile:

    def __init__(self, filename):
        self.filename = filename

        messages = []
        with open(self.filename, 'r') as linkfile:
            for line in linkfile:
                try:
                    message = StringMessage(line)
                    messages.append(message)
                except:
                    print line

        links = []
        link = None

        for msg in messages:
            try:
                if msg.is_transmission:
                    link = Link(msg)
                    links.append(link)
                elif msg.is_reception:
                    link.add_rx(msg)
            except:
                print msg

        self.id_a = links[0].tx['id']
        self.id_b = None

        for link in links:
            if link.tx['id'] == self.id_a:
                for rx in link.valid_rx:
                    self.id_b = rx['id']
                    break

        self.links_ab = []
        self.links_ba = []

        for link in links:
            if link.tx['id'] == self.id_a:
                # transmitting from 0 to 1
                self.links_ab.append(link)
            else:
                self.links_ba.append(link)

    @property
    def string_ab(self):
        return "{}-{}".format(self.id_a, self.id_b)

    @property
    def string_ba(self):
        return "{}-{}".format(self.id_b, self.id_a)

    def get_analyzer_ab(self):
        return Analyzer(self.links_ab, "{}_{}".format(self.filename, self.string_ab))

    def get_analyzer_ba(self):
        return Analyzer(self.links_ba, "{}_{}".format(self.filename, self.string_ba))

    def get_analyzers(self):
        return self.get_analyzer_ab(), self.get_analyzer_ba()


    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("LinkFile( {} )\n".format(self.filename))
