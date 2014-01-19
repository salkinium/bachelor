# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
from multiprocessing import Process
import serial

class TemperatureControl(Process, object):
	""" TemperatureControl
	Enables communication with the controller which manages temperature inside
	a TemperatureBox. 
	"""

	def __init__(self, device, logFile=None):
		super(TemperatureControl, self).__init__()
		
		self.logger = logging.getLogger('TemperatureControl.({})'.format(device))
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		# console logging
		ch = logging.StreamHandler()
		ch.setLevel(logging.WARN if logFile else logging.DEBUG)
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		
		# file logging
		if logFile:
			fh = logging.FileHandler(logFile)
			fh.setLevel(logging.DEBUG)
			fh.setFormatter(formatter)
			self.logger.addHandler(fh)
		
		try:
			self.port = serial.Serial(port=device, baudrate=115200, timeout=5)
		except:
			self.logger.critical("unable to open device '{}'".format(device))
		
		self.temperatures = []
		self.logger.info("listening")
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
			self.logger.error('unable to send temperature')
	
	def run(self):
		while(True):
			line = self.port.readline()[:-1]
			if line.startswith("T:"):
				temps = line[3:].translate(None, " C,").split('\t')
				self.temperatures = [float(t) for t in temps]
				self.logger.debug("temperature={}".format(self.temperature))
			elif line.startswith('Info:'):
				self.logger.info(line.replace('Info:  ', ''))
			else:
				self.logger.warn("unknown input '{}'".format(line))
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("TemperatureControl( %s )\n" % self.port.port)
