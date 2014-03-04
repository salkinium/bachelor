# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from base import BaseCommand


class IgnoreCommand(BaseCommand):

    def __init__(self):
        super(IgnoreCommand, self).__init__()

    def execute(self, _):
        # ignores everything and just returns True every time
        return True

    def __str__(self):
        return "IgnoreCommand()"
