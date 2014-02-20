# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
from multiprocessing import Process

import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from multiprocessing import Process, Value
from threading import Timer

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *
from tinyos.packet.Serial import Serial

from messages import *
from box import Box

def enum(**enums):
    return type('Enum', (), enums)


class BoxManager(Process, object):
	""" BoxManager
	Allows dynamic addition and removal of boxes and motes and manages
	the communication between them.
	"""

	ParserLineType = enum(IGNORE='Ignore', ERROR='Error', UNKNOWN='Unknown',
						TEMPERATURE='Temperature', MESSAGE='Message')

	def __init__(self, logPath='/var/log/boxmanager'):
		super(BoxManager, self).__init__()
		
		self.logPath = logPath
		self.boxes = []
		
		self.logger = logging.getLogger('BoxManager')
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		# console logging
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		
		# file logging
		fh = logging.FileHandler(os.path.join(self.logPath,'boxmanager.log'))
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)
		self.script = None
		self.sendingTimeoutTimer = None
		self.sendingTimeoutExpired = Value('b', False)
		
# 		self.start()
	
	def addBox(self, id, mote, temperature):
		if id not in [box.id for box in self.boxes]:
			self.logger.info("Adding box: id={} mote={} temperature={}".format(id, mote, temperature))
			box = Box(id, mote, temperature, self.logPath)
			self.boxes.append(box)
		else:
			self.logger.error("Box with id={} already present!".format(id))
		
	def removeBox(self, id):
		self.logger.info("Removing box {}".format(id))
		new_boxes = []
		for box in self.boxes:
			if box.id != id:
				new_boxes.append(box)
		self.boxes = new_boxes
	
	def retrieveBox(self, id):
		for box in self.boxes:
			if box.id == id:
				return box
		return None
	
	def addScript(self, scriptFile):
		if os.path.exists(scriptFile):
			self.logger.info("Adding script file: {}".format(scriptFile))
			try:
				self.script = open(scriptFile, 'r')
			except:
				self.logger.error("Unable to open script file!")
		else:
			self.logger.error("Script file does not exist! {}".format(scriptFile))

	def terminateScript(self):
		if self.script:
			self.script.close()
		self.script = None
	
	def run(self):
		while(True):
			if self.script:
				line = self.script.readline()
				type, args = self.parseScriptLine(line)
				success = self.actionScriptLine(type, args)
				if not success:
					self.script = None
	
	def actionScriptLine(self, type, arguments):
		if type == self.ParserLineType.IGNORE:
			return True
		elif type == self.ParserLineType.UNKNOWN:
			self.logger.warn("Unknown script command: '{}'".format(arguments['line']))
			return False
		elif type == self.ParserLineType.ERROR:
			self.logger.error("Error parsing script line '{}' of action '{}'".format(arguments['line'], arguments['action']))
			return False
		
		elif type == self.ParserLineType.TEMPERATURE:
			args = {'timeout': None}
			args.update(arguments)
			
			if not all(key in args for key in ('box', 'temperature', 'timeout')):
				self.logger.error("Command '{}' is incomplete: '{}'".format(type, args))
				return False
			
			box = self.retrieveBox(args['box'])
			if not box:
				self.logger.error("Box '{}' not found!".format(args['box']))
				return False
			
			box.setAirTemperature(args['temperature'], args['timeout'])
			return True
		
		elif type == self.ParserLineType.MESSAGE:
			# wait until all boxes have reached the target temperature
			while(not all(box.airTemperatureTargetReached() for box in self.boxes)):
				pass
			
			args = {'timeout': 5, 'power': 7, 'data': [], 'repeat': 1, 'period': 1}
			args.update(arguments)
			if not all(key in args for key in ('from', 'to', 'power', 'data', 'repeat', 'period', 'timeout')):
				self.logger.error("Command '{}' is incomplete: '{}'".format(type, args))
				return False
			
			sender = self.retrieveBox(args['from'])
			if not sender:
				self.logger.error("Sender '{}' not found!".format(args['box']))
				return False
			
			receiver = self.retrieveBox(args['to'])
			if not receiver:
				self.logger.error("Receiver '{}' not found!".format(args['box']))
				return False
			
			
			tx = SerialMessage.SerialMessage()
			tx.set_header_channel(26)
			tx.set_header_type(SerialMessage.SerialMessage.get_amType())
			tx.set_header_power(args['power'])
			tx.set_header_len(len(args['data']))
			tx.set_header_nodeid(args['from'])
			tx.set_data(args['data'])
			self.logger.debug("Created message: {}".format(tx))
			
			while(args['repeat']):
				self.logger.debug("Sending message from '{}' to '{}'.".format(args['from'], args['to']))
				
				sender.moteControl.purgeReceiveBuffer()
				receiver.moteControl.purgeReceiveBuffer()
				
				sender.transmit(args['to'], tx)
				
				if self.sendingTimeoutTimer:
					self.sendingTimeoutTimer.cancel()
				self.sendingTimeoutExpired.value = False
				self.sendingTimeoutTimer = Timer(args['timeout'], self._sendingTimeoutExpired)
				
				while( (sender.moteControl.receiveBufferEmpty() or receiver.moteControl.receiveBufferEmpty() ) and \
					not self.sendingTimeoutExpired.value):
					pass
				
				txConfirmation = sender.moteControl.getReceivedMessage()
				rx = receiver.moteControl.getReceivedMessage()
				
				if self.sendingTimeoutExpired.value or not rx or not txConfirmation:
					self.logger.warning("Message reception timed out on repeat {}".format(args['repeat']))
				else:
					self.logger.debug("Received Message: {}".format(rx))
					# man are these numbers arbitrary
					txLength = txConfirmation.get_header_len()
					txData = txConfirmation.data[22:-(100-txLength)]
					rxData = rx.data[22:-(100-txLength)]
					
					if txData != rxData:
						xor = [ord(txData[ii]) ^ ord(rxData[ii]) for ii in range(len(txData))]
						self.logger.warning("Corrupted paylaod: {}".format(xor))
				
				args['repeat'] = args['repeat'] - 1
				
				if args['repeat'] > 0:
					# wait to send again
					time.sleep(args['period'])
			
			return True
		
		return False
	
	def _sendingTimeoutExpired(self):
		self.sendingTimeoutExpired.value = True
	
	def parseScriptLine(self, line):
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
				for key in args:
					if key in ['power', 'timeout', 'repeat', 'from', 'to']:
						args[key] = int(args[key])
					if key in ['period']:
						args[key] = float(args[key])
					if key in ['data']:
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
		return ("BoxManager( {} )\n".format(len(self.boxes))) \
