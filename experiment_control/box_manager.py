# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
from multiprocessing import Process

import os, sys, time, random

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from multiprocessing import Process, Value
from threading import Timer

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *
from tinyos.packet.Serial import Serial

from messages import *
from box import Box
from evaluator import Evaluator


def enum(**enums):
    return type('Enum', (), enums)


class BoxManager(Process, object):
    """ BoxManager
    Allows dynamic addition and removal of boxes and motes and manages
    the communication between them.
    """

    ParserLineType = enum(IGNORE='Ignore', ERROR='Error', UNKNOWN='Unknown',
                          TEMPERATURE='Temperature', MESSAGE='Message')

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

        self.script = None
        self.scripts = []
        self.sending_timeout_timer = None
        self.sending_timeout_expired = Value('b', False)

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

    def retrieve_box(self, identifier):
        for box in self.boxes:
            if box.id == identifier:
                return box
        return None

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
                line_type, args = self.parse_script_line(line)
                success = self.action_script_line(line_type, args)
                if not success:
                    self.terminate_script()
            elif len(self.scripts):
                self._set_active_script(self.scripts.pop(0))
            else:
                self.terminate_script()

    def action_script_line(self, line_type, arguments):
        if line_type == self.ParserLineType.IGNORE:
            return True
        elif line_type == self.ParserLineType.UNKNOWN:
            self.logger.warn("Unknown script command: '{}'".format(arguments['line']))
            return False
        elif line_type == self.ParserLineType.ERROR:
            self.logger.error(
                "Error parsing script line '{}' of action '{}'".format(arguments['line'], arguments['action']))
            return False

        elif line_type == self.ParserLineType.TEMPERATURE:
            args = {'timeout': None}
            args.update(arguments)

            if not all(key in args for key in ('box', 'temperature', 'timeout')):
                self.logger.error("Command '{}' is incomplete: '{}'".format(line_type, args))
                return False

            box = self.retrieve_box(args['box'])
            if not box:
                self.logger.error("Box '{}' not found!".format(args['box']))
                return False

            box.set_air_temperature(args['temperature'], args['timeout'])
            return True

        elif line_type == self.ParserLineType.MESSAGE:
            # wait until all boxes have reached the target temperature
            while not all(box.temperature_target_reached() for box in self.boxes):
                pass

            args = {'timeout': 1, 'power': 7, 'data': [], 'repeat': 1, 'period': 1, 'bursts': None, 'randomize': False}
            args.update(arguments)
            if not all(key in args for key in ('from', 'to', 'power', 'data', 'repeat', 'period', 'timeout', 'bursts')):
                self.logger.error("Command '{}' is incomplete: '{}'".format(line_type, args))
                return False

            from_id = args['from']
            to_id = args['to']

            sender = sender_orig = self.retrieve_box(from_id)
            if not sender:
                self.logger.error("Sender '{}' not found!".format(from_id))
                return False

            receiver = receiver_orig = self.retrieve_box(to_id)
            if not receiver:
                self.logger.error("Receiver '{}' not found!".format(to_id))
                return False

            tx = SerialMessage.SerialMessage()
            tx.set_header_channel(26)
            tx.set_header_type(SerialMessage.SerialMessage.get_amType())
            tx.set_header_power(args['power'])
            tx.set_header_len(len(args['data']))
            tx.set_data(args['data'])
            self.logger.debug("Created message: {}".format(tx))

            reversed_message_flow = False
            bursts = args['bursts']
            bursts = bursts - 1 if (bursts and bursts > 0) else None
            repeats = args['repeat']

            while repeats:

                if args['bursts'] and reversed_message_flow:
                    sender = receiver_orig
                    receiver = sender_orig
                else:
                    sender = sender_orig
                    receiver = receiver_orig

                sender.mote_control.purge_receive_buffer()
                receiver.mote_control.purge_receive_buffer()

                tx.set_header_nodeid(sender.id)
                #self.logger.debug("Sending message from '{}' to '{}'.".format(sender.id, receiver.id))
                sender.transmit(receiver.id, tx)

                if self.sending_timeout_timer:
                    self.sending_timeout_timer.cancel()
                self.sending_timeout_expired.value = False
                self.sending_timeout_timer = Timer(args['timeout'], self._sending_timeout_expired)
                self.sending_timeout_timer.start()

                while not self.sending_timeout_expired.value and \
                        (sender.mote_control.receive_buffer_empty() or receiver.mote_control.receive_buffer_empty()):
                    pass

                tx_confirmation = sender.mote_control.get_received_message()
                rx = receiver.mote_control.get_received_message()

                if self.sending_timeout_expired.value or not rx or not tx_confirmation:
                    self.logger.warning("Message reception timed out on repeat {}".format(args['repeat'] - repeats))
                else:
                    values = Evaluator.evaluate_messages(tx_confirmation, rx)
                    values.update({'temperatureFrom': sender.mote_temperature,
                                   'temperatureTo': receiver.mote_temperature})

                    result_string = Evaluator.format_values(values)
                    self.results.info(result_string)

                if args['bursts']:
                    if bursts > 0:
                        bursts -= 1
                    else:
                        reversed_message_flow = not reversed_message_flow
                        bursts = args['bursts'] - 1

                repeats -= 1

                if repeats:
                    if args['randomize']:
                        # randomize payload
                        tx.set_data([random.randint(0, 255) for _ in xrange(len(args['data']))])
                    # wait to send again
                    time.sleep(args['period'])

            return True

        return False

    def _sending_timeout_expired(self):
        self.sending_timeout_expired.value = True

    def parse_script_line(self, line):
        if line.strip(' \t') == '\n' or line.startswith('#'):
            return self.ParserLineType.IGNORE, {'line': line}

        line = line.strip('\n')

        if line.startswith('set temperature:\t'):
            nline = line.replace('set temperature:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                for key in args:
                    if key in ['temperature', 'timeout', 'box']:
                        args[key] = int(args[key])

                return self.ParserLineType.TEMPERATURE, args
            except:
                return self.ParserLineType.ERROR, {'action': self.ParserLineType.TEMPERATURE, 'line': line}

        elif line.startswith('send message:\t'):
            nline = line.replace('send message:\t', '')
            try:
                args = {arg.split('=')[0]: arg.split('=')[1] for arg in nline.split('\t')}
                args['randomize'] = False
                for key in args:
                    if key in ['power', 'timeout', 'repeat', 'from', 'to', 'bursts']:
                        args[key] = int(args[key])
                    if key in ['period']:
                        args[key] = float(args[key])
                    if key in ['data']:
                        if args[key].startswith("random("):
                            number = int(args[key][7:-1])
                            args[key] = [random.randint(0, 255) for _ in xrange(number)]
                            args['randomize'] = True
                        else:
                            string = args[key].decode("hex")
                            args[key] = map(ord, string)

                return self.ParserLineType.MESSAGE, args
            except:
                return self.ParserLineType.ERROR, {'action': self.ParserLineType.MESSAGE, 'line': line}

        else:
            return self.ParserLineType.UNKNOWN, {'line': line}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "BoxManager( {} )\n".format(len(self.boxes))
