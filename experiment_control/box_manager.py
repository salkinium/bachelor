# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os
from multiprocessing import Process

from box import Box


class BoxManager(Process, object):
    """ BoxManager
    Allows dynamic addition and removal of boxes and motes and manages
    the communication between them.
    """

    def __init__(self, log_path='/var/log/boxmanager'):
        super(BoxManager, self).__init__()

        self.log_path = log_path
        self.boxes = []

        self.logger = logging.getLogger('BoxManager')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # console logging
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)

        # file logging
        fh = logging.FileHandler(os.path.join(self.log_path, 'boxmanager.log'))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # results logger
        self.results = logging.getLogger('ExperimentResults')
        self.results.setLevel(logging.DEBUG)
        self.results.addHandler(self.ch)

    def add_box(self, identifier, mote, temperature, correction):
        if identifier not in [box.id for box in self.boxes]:
            self.logger.info("Adding box: id={} mote={} temperature={} correction={}"
                             .format(identifier, mote, temperature, correction))
            box = Box(identifier, mote, temperature, self.log_path)
            box.mote_control.temperature_correction = correction
            self.boxes.append(box)
        else:
            self.logger.error("Box with id={} already present!".format(identifier))

    def remove_box(self, identifier):
        self.logger.info("Removing box {}".format(identifier))
        new_boxes = []
        for box in self.boxes:
            if box.id != identifier:
                new_boxes.append(box)
        self.boxes = new_boxes

    def get_box(self, identifier):
        for box in self.boxes:
            if box.id == identifier:
                return box
        return None

    def boxes_without(self, box):
        boxes = []
        for b in self.boxes:
            if b is not box:
                boxes.append(b)
        return boxes

    @property
    def identifiers(self):
        return [box.id for box in self.boxes]

    def __contains__(self, item):
        if isinstance(item, Box):
            return item in self.boxes
        return item in self.identifiers

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "BoxManager( {} )\n".format(len(self.boxes))
