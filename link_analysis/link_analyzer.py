#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.

import os, sys
import glob
from logger import Logger
from string_link import StringLink

import matplotlib.pyplot as plt
import pylab as P

if __name__ == "__main__":
	"""
	Some test code
	"""
	level = 'info'
	logger = Logger(level)
	links = []
	
	for arg in sys.argv[1:]:
		if arg in ['error', 'warn', 'info', 'debug', 'disabled']:
			level = arg
			logger.setLogLevel(level)
			continue
		xml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data_senserr', 'logs', 'senserr-randommessages', arg)
		files = glob.glob(xml_path)
		for file in files:
			with open(file, 'r') as linkfile:
				logger.info("Parsing links of file: '%s'" % file)
				for line in linkfile:
					if 'crc=0' in line:
						link = StringLink(line, logger)
						links.append(link)
# 						if len(links) > 20000:
# 							break
	
	logger.info("%s links parsed" % len(links))
	
	rssi_array = [p['rssi'] for p in links]
	rssi_min = min(rssi_array)
	rssi_max = max(rssi_array)
	logger.info("RSSI in range [%s, %s]" % (rssi_min, rssi_max))
	
	
	lqi_array = [p['lqi'] for p in links]
	lqi_min = min(lqi_array)
	lqi_max = max(lqi_array)
	logger.info("LQI in range [%s, %s]" % (lqi_min, lqi_max))
	
	
	power_array = [p['power'] for p in links]
	power_min = min(power_array)
	power_max = max(power_array)
	logger.info("Power in range [%s, %s]" % (power_min, power_max))
	
	
	errors_array = [p['errors'] for p in links]
	errors_min = min(errors_array)
	errors_max = max(errors_array)
	logger.info("Errors in range [%s, %s]" % (errors_min, errors_max))
	
 	
 	P.figure()
	n, bins, patches = P.hist(rssi_array, range(rssi_min, rssi_max+1), normed=True, histtype='stepfilled', rwidth=0.8)
	P.setp(patches, 'facecolor', 'r', 'alpha', 0.75)
 	P.ylabel("occurances")
 	P.xlabel("RSSI")
 	
 	
 	P.figure()
	n, bins, patches = P.hist(lqi_array, range(lqi_min, lqi_max+1), normed=True, histtype='stepfilled', rwidth=0.8)
	P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
 	P.ylabel("occurances")
 	P.xlabel("LQI")
 	
 	P.figure()
	n, bins, patches = P.hist(power_array, range(power_min, power_max+1), normed=True, histtype='stepfilled', rwidth=0.8)
	P.setp(patches, 'facecolor', 'b', 'alpha', 0.75)
 	P.ylabel("occurances")
 	P.xlabel("Power")
 	
 	
 	P.figure()
	n, bins, patches = P.hist(errors_array, range(errors_min, 100), normed=True, histtype='stepfilled', rwidth=0.8)
	P.setp(patches, 'facecolor', 'y', 'alpha', 0.75)
 	P.ylabel("occurances")
 	P.xlabel("Errors")
 	
 	
	P.show()
	
	

