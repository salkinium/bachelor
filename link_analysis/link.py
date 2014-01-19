# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging

class Link:
	""" Link
	Represents a link in a non-platform specific format.
	This encapsulates payload, errors, qualitiy quantifiers like signal strength,
	and power settings.
	"""

	def __init__(self, properties=None):
		self.properties = {}
		
		if properties:
			self.properties = properties
	
	def __iter__(self):
		for key in self.properties:
			yield key
	
	def __setitem__(self, key, value):
		self.properties[key] = value
	
	def __getitem__(self, key):
		return self.properties[key]
	
	def __len__(self):
		return len(self.properties)
	
	def __hash__(self):
		return str(self)
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("Link(\t%s )\n" %
			",\n".join(["'%s': '%s'" % (p, self.properties[p]) for p in self.properties])) \
			.replace("\n", "\n\t")
