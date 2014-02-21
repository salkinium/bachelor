# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
from multiprocessing import Process, Value, Array
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
		
		self.temperatures = Array('f', range(5))
		self.temperatureLength = Value('i', 0)
		self.heaterPower = Value('i', 0)
		self.target = 0
		self.logger.info("listening")
		self.start()
	
	@property
	def temperature(self):
		if self.temperatureLength.value > 0:
			return sum(self.temperatures) / float(self.temperatureLength.value)
		
		return 0
	
	@property
	def power(self):
		return self.heaterPower.value
	
	@temperature.setter
	def temperature(self, value):
		try:
			self.port.write("{}C".format(int(value)))
			self.target = int(value);
		except:
			self.logger.error('Unable to send value: {}'.format(value))
	
	def targetReached(self):
		if (self.target-2 <= self.temperature <= self.target+5):
			return True
		return False
	
	def run(self):
		while(True):
			line = self.port.readline().strip('\n')
			if line.startswith("T:"):
				temps = line[3:].translate(None, " C,").split('\t')
				self.temperatureLength.value = len(temps)
				for ii in range(5):
					self.temperatures[ii] = 0
				for ii in range(self.temperatureLength.value):
					self.temperatures[ii] = float(temps[ii])
				self.logger.debug("temperature={}".format([float(t) for t in temps]))
			elif line.startswith("P:"):
				self.heaterPower.value = int(line[3:])
				self.logger.debug("power={}".format(self.heaterPower.value))
			elif line.startswith("Info:"):
				continue
			elif line != "":
				self.logger.warn("unknown input '{}'".format(line))
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("TemperatureControl( %s )\n" % self.port.port)
