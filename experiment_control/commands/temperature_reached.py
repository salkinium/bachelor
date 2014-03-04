# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from base import BaseCommand


class TemperatureReachedCommand(BaseCommand):

    def __init__(self):
        super(TemperatureReachedCommand, self).__init__()

    def execute(self, boxmanager):
        while not all(box.temperature_target_reached() for box in boxmanager.boxes):
            pass

        return True

    def __str__(self):
        return "TemperatureReachedCommand()"
