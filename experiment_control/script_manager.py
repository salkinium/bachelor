# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os

from commands import *


class ScriptManager(object):

    def __init__(self, boxmanager, log_path='/var/log/boxmanager'):
        super(ScriptManager, self).__init__()

        self.log_path = log_path
        self.boxmanager = boxmanager

        self.logger = logging.getLogger('ScriptManager')
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

        # results logger
        self.results = logging.getLogger('ExperimentResults')
        self.results.setLevel(logging.DEBUG)
        self.results.addHandler(self.ch)

        self.script = None
        self.scripts = []

    def add_script(self, script_file):
        if os.path.exists(script_file):
            self.logger.info("Adding script file: {}".format(script_file))
            try:
                script = open(script_file, 'r')
                self.scripts.append(script)
                if not self.script:
                    self._set_active_script(self.scripts.pop(0))
            except:
                self.logger.error("Unable to open script file!")
        else:
            self.logger.error("Script file does not exist! {}".format(script_file))

    def _set_active_script(self, script):
        self.terminate_script()
        self.script = script
        # file handler
        xh = logging.FileHandler(
            os.path.join(self.log_path, os.path.splitext(os.path.basename(self.script.name))[0] + '-experiment.log'))
        xh.setLevel(logging.INFO)
        xformatter = logging.Formatter('timestamp=%(asctime)s\t%(message)s')
        xh.setFormatter(xformatter)
        self.results.handlers = []
        self.results.addHandler(xh)
        self.results.addHandler(self.ch)

        self.logger.info("Executing script: {}".format(script.name))

    def terminate_script(self):
        if self.script:
            self.script.close()
        self.script = None

    def is_idle(self):
        return len(self.scripts) == 0 and self.script is None

    def run(self):
        while True:
            if self.script:
                line = self.script.readline()
                if line == '':
                    self.terminate_script()
                    break
                command = self.get_command(line)
                if command:
                    success = command.execute(self.boxmanager)
                if not command or not success:
                    self.terminate_script()
            elif len(self.scripts):
                self._set_active_script(self.scripts.pop(0))
            else:
                self.terminate_script()

    def get_command(self, line):
        if line.strip(' \t') == '\n' or line.startswith('#'):
            return IgnoreCommand()

        line = line.strip('\n')

        if line.startswith('set temperature:\t'):
            nline = line.replace('set temperature:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                return TemperatureCommand(args)
            except:
                self.logger.error("Error parsing script line '{}' for TemperatureCommand".format(line))
                return None

        elif line.startswith('send message:\t'):
            nline = line.replace('send message:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                return MessageCommand(args, self.results)
            except:
                self.logger.error("Error parsing script line '{}' for MessageCommand".format(line))
                return None

        elif line.startswith('wait temperature:\t'):
            nline = line.replace('wait temperature:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                return TemperatureReachedCommand(args)
            except:
                self.logger.error("Error parsing script line '{}' for TemperatureReachedCommand".format(line))
                return None

        elif line.startswith('wait:\t'):
            nline = line.replace('wait:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                return WaitCommand(args)
            except:
                self.logger.error("Error parsing script line '{}' for WaitCommand".format(line))
                return None

        else:
            self.logger.warn("Unknown script command: '{}'".format(line))
            return None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "ScriptManager( {} )\n".format(len(self.scripts))
