# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'link_analysis'))
from logger import Logger

from multiprocessing import Process
import time
import serial

class TemperatureControl(Process, object):
	""" TemperatureControl
	Enables communication with the controller which manages temperature inside
	a TemperatureBox. 
	"""

	def __init__(self, device=None, logger=None):
		super(TemperatureControl, self).__init__()
		self.log = logger if logger else Logger()
		
		try:
			self.port = serial.Serial(port=device, baudrate=115200, timeout=5)
		except:
			self.log.error("TemperatureControl(%s): unable to open port" % self.port.port)
		
		self.temperatures = []
		self.log.info("TemperatureControl(%s): starting thread" % self.port.port)
		self.start()
	
	@property
	def temperature(self):
		if len(self.temperatures):
			return sum(self.temperatures) / float(len(self.temperatures))
		
		return 0
	
	@temperature.setter
	def temperature(self, value):
		try:
			self.port.write("%sC" % str(int(value)))
		except:
			self.log.error('TemperatureControl(%s): unable to send temperature', self.port.port)
	
	def run(self):
		while(True):
			line = self.port.readline()[:-1]
			if line.startswith("T:"):
				temps = line[3:].translate(None, " C,").split('\t')
				self.temperatures = [float(t) for t in temps]
				self.log.debug("TemperatureControl(%s): temperature=%s" % (self.port.port, self.temperature))
			elif line.startswith('Info:'):
				self.log.info("TemperatureControl(%s): %s" % (self.port.port, line.replace('Info:', '')))
			else:
				self.log.warn("TemperatureControl(%s): Unknown input '%s'" % (self.port.port, line))
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("TemperatureControl(\t%s )\n" % self.port.port) \
			.replace("\n", "\n\t")
