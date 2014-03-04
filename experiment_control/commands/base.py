# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os


class BaseCommand(object):

    def __init__(self, arguments=None, log_path='/var/log/boxmanager'):
        super(BaseCommand, self).__init__()

        self.arguments = arguments if arguments else []

        self.log_path = log_path
        self.logger = logging.getLogger('Command')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # console logging
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)

        # file logging
        fh = logging.FileHandler(os.path.join(self.log_path, 'scriptmanager.log'))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def execute(self, _):
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "BaseCommand()"
