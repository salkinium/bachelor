#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import os, sys, time
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *
from tinyos.packet.Serial import Serial

from messages import *

class Connection(object):

	def __init__(self, device=None):
		super(Connection, self).__init__()
		
		self.logger = logging.getLogger('Connection.({})'.format(device))
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		# console logging
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(formatter)
		self.logger.addHandler(ch)
		
		self.mif = MoteIF.MoteIF()
		self.device = device
		self.tos_source = self.mif.addSource("serial@" + device)
		self.mif.addListener(self, SerialMessage.SerialMessage)
		self.mif.addListener(self, RadioMessage.RadioMessage)
		self.mif.addListener(self, SensorMessage.SensorMessage)
		self.logger.info("listening")
		
		self.temperature = 0
		self.humidity = 0

	def receive(self, src, msg):
		if msg.get_amType() == SensorMessage.AM_TYPE:
			m = SensorMessage.SensorMessage(msg.dataGet())
			self.temperature = m.get_temperature()*0.01 - 40.1
			linear_humidity = -2.0468 + 0.0367 * m.get_humidity() + (-1.5955e-6 * m.get_humidity())**2
			self.humidity = (self.temperature - 25) * (0.01 + 0.00008 * m.get_humidity()) + linear_humidity
			
			self.logger.debug("SensorMessage: NodeId={}, Temp={:.1f}C, Hum={:.1f}%" \
							.format(m.get_nodeid(), self.temperature, self.humidity))
						
		elif msg.get_amType() == SerialMessage.AM_TYPE:
			m = SerialMessage.SerialMessage(msg.dataGet())
			self.logger.info("SerialMessage: {}".format(str(m)))

		elif msg.get_amType() == RadioMessage.AM_TYPE:
			m = RadioMessage.RadioMessage(msg.dataGet())
			self.logger.info("RadioMessage: {}".format(str(m)))
			
		else:
			self.logger.warn("Unknown Message: {}".format(str(msg)))

	def transmit(self, addr, msg):
		self.logger.info("Transmitting: addr={} {}".format(addr, msg))
		self.mif.sendMsg(self.tos_source, addr, msg.get_amType(), 0, msg)


if __name__ == "__main__":
	
	sender = Connection("/dev/ttyUSB3:telos")
	receiver = Connection("/dev/ttyUSB1:telos")
	
	data = [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,
			0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,
			0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9]
	
# 	data = [0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,
# 			0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,
# 			0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88]
	
	rawData = chr(0)*20 + "".join(map(chr, data))
	
	tx = SerialMessage.SerialMessage()
	tx.set_header_channel(26)
	tx.set_header_type(SerialMessage.SerialMessage.get_amType())
	tx.set_header_power(3)
	tx.set_header_len(len(data))
	tx.set_header_nodeid(0)
	tx.set_data(data)
	
	print tx.data
	
	time.sleep(1)
	
	sender.transmit(1, tx)
	
	while(1):
		pass
