# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from temperature_control import TemperatureControl
from mote_control import MoteControl
import logging

from multiprocessing import Process

class Box(Process, object):
	""" TemperatureBox
	Allows access to the controller and node in the styrofoam box.
	"""

	def __init__(self, id, mote, temperature, moteLogFile=None, temperatureLogFile=None):
		super(Box, self).__init__()
		
		self.id = id
		self.moteControl = MoteControl(mote, moteLogFile)
		self.temperatureControl = TemperatureControl(temperature, temperatureLogFile)
# 		self.start()
	
	def run(self):
		pass
	
	@property
	def airTemperature(self):
		return temperatureControl.temperature
	
	@property
	def moteTemperature(self):
		return moteControl.temperature
	
	def setAirTemperature(self, value):
		temperatureControl.temperature = value
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("Box( %s )" % self.id) \
