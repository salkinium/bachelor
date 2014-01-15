# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'logger'))
from logger import Logger
from multiprocessing import Process
import time
import serial

class TemperatureControl(Process):
	""" TemperatureControl
	Enables communication with the controller which manages temperature inside
	a TemperatureBox. 
	"""

	def __init__(self, portName=None, logger=None):
		super(TemperatureControl, self).__init__()
		if logger == None:
			self.log = Logger()
		else:
			self.log = logger
		
		self.port = serial.Serial(port=portName, baudrate=115200, timeout=5)
		self.port.open()
		
		self.temperatures = []
		self.start()
		self.log.info("TemperatureControl: starting thread")
	
	def getTemperature(self):
		if len(self.temperatures):
			return sum(self.temperatures) / float(len(self.temperatures))
		
		return 0
	
	def setTemperature(self, temperature):
		self.port.write("%sC" % str(int(temperature)))
	
	def run(self):
		while(True):
			line = self.port.readline()
			line = line.translate(None, '\n')
			if line.startswith('T:'):
				temps = line[3:].translate(None, ' C,').split('\t')
				self.temperatures = [float(t) for t in temps]
				self.log.debug("TemperatureControl(%s): temperature=%s" % (self.port.port, self.getTemperature()))
			elif line.startswith('Info:'):
				self.log.info("TemperatureControl(%s): %s" % (self.port.port, line.replace('Info:', ''))) 
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("TemperatureControl(\t%s )\n" % self.port.port) \
			.replace("\n", "\n\t")
