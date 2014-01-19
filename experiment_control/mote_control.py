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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))
from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *
from tinyos.packet.Serial import Serial

from messages import *

from multiprocessing import Process
import time

class MoteControl:
	""" MoteControl
	Enables communication with the WSN mote in the box.
	"""

	def __init__(self, device=None, logger=None):
		#super(MoteControl, self).__init__()
		self.log = logger if logger else Logger()
		
		self.mif = MoteIF.MoteIF()
		self.device = device
		self.tos_source = self.mif.addSource("serial@" + device)
		self.mif.addListener(self, SerialMessage.SerialMessage)
		self.mif.addListener(self, RadioMessage.RadioMessage)
		self.mif.addListener(self, SensorMessage.SensorMessage)
		self.log.info("MoteControl(%s): listening" % (self.device))
		
		self.temperature = 0
		self.humidity = 0
	
	def receive(self, src, msg):
		if msg.get_amType() == SerialMessage.AM_TYPE:
			m = SerialMessage.SerialMessage(msg.dataGet())
			self.log.debug("MoteControl(%s): SerialMessage: %s" % (self.device, str(m)))
		elif msg.get_amType() == SensorMessage.AM_TYPE:
			m = SensorMessage.SensorMessage(msg.dataGet())
			self.temperature = m.get_temperature()*0.01 - 40.1
			linear_humidity = -2.0468 + 0.0367 * m.get_humidity() + (-1.5955e-6 * m.get_humidity())**2
			self.humidity = (self.temperature - 25) * (0.01 + 0.00008 * m.get_humidity()) + linear_humidity
			
			self.log.debug("MoteControl(%s): SensorMessage: NodeId=%s, Temp=%.1fC, Hum=%.1f%%" % (self.device, m.get_nodeid(), self.temperature, self.humidity))
			
		elif msg.get_amType() == RadioMessage.AM_TYPE:
			m = RadioMessage.RadioMessage(msg.dataGet())
			self.log.debug("MoteControl(%s): RadioMessage: %s" % (self.device, str(m)))
	
	def run(self):
		pass
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("MoteControl( %s )\n" % self.device) \
