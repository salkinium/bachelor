# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os
import time

from multiprocessing import Process, Value
from threading import Timer

from periodic_timer import PeriodicTimer
from temperature_control import TemperatureControl
from mote_control import MoteControl

class Box(object):
	""" TemperatureBox
	Allows access to the controller and node in the styrofoam box.
	"""

	def __init__(self, id, mote, temperature, logPath=''):
		super(Box, self).__init__()
		
		self.logger = logging.getLogger('Box.({})'.format(id))
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		# console logging
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		
		# file logging
		fh = logging.FileHandler(os.path.join(logPath, 'box-{}.log'.format(id)))
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)
		
		self.id = int(id)
		self.moteControl = MoteControl(mote, os.path.join(logPath, 'box_raw-{}.log'.format(id)))
		self.temperatureControl = TemperatureControl(temperature, os.path.join(logPath, 'box_raw-{}.log'.format(id)))
		
		self.environmentTimer = PeriodicTimer(10, self._reportEnvironment)
		self.environmentTimer.start()
		self.temperatureTimeoutTimer = None
		self.temperatureTimeoutExpired = Value('b', False)
		
	
	def _reportEnvironment(self):
		self.logger.info("Environment: Tair={:.1f}C Tmote={:.1f}C Hmote={:.1f}%" \
							.format(self.airTemperature, self.moteTemperature, self.moteHumidity))
		return True
	
	def _temperatureTimeoutExpired(self):
		self.temperatureTimeoutExpired.value = True
	
	@property
	def airTemperature(self):
		return self.temperatureControl.temperature
	
	@property
	def moteTemperature(self):
		return self.moteControl.temperature
	
	@property
	def moteHumidity(self):
		return self.moteControl.humidity
	
	def airTemperatureTargetReached(self):
		return self.temperatureControl.targetReached() or self.temperatureTimeoutExpired.value
	
	def setAirTemperature(self, value, timeout=None):
		self.logger.info("Setting air temperature to {}C".format(value))
		self.temperatureControl.temperature = value
		# set-up the timeout
		self.temperatureTimeoutExpired.value = False
# 		if self.temperatureTimeoutTimer:
# 			self.temperatureTimeoutTimer.cancel()
# 		if timeout:
# 			self.temperatureTimeoutTimer = Timer(timeout, self._temperatureTimeoutExpired)
	
	def transmit(self, addr, amType, group, msg):
		self.moteControl.transmit(addr, amType, group, msg)
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("Box( {} )".format(self.id))
