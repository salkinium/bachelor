# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


from link import Link
import dateutil.parser

class StringLink(Link):
	""" StringLink
	Parses a string and generates a link class 
	"""

	def __init__(self, string=None):
		Link.__init__(self, None)
		
		if string:
			self['string'] = string
			for item in string.split('\t'):
				items = item.split('=')
				self.properties[items[0]] = items[1]
		
		for p in self.properties:
			if p in ['power', 'lqi', 'crc', 'rssi', 'errors']:
				self[p] = int(self[p])
			elif p in ['timestamp']:
				self[p] = dateutil.parser.parse(self[p])
			elif p in ['orgdata', 'xor']:
				self[p] = bytearray( [int(ii) for ii in self[p].split(' ')] )

	def __str__(self):
		return "String" + Link.__str__(self)
