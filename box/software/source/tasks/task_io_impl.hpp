// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_IO_HPP
#	error	"Don't include this file directly, use 'task_io.hpp' instead!"
#endif

#include <errno.h>

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::INFO

task::IO::IO(Temperature &sensors, TemperatureControl &control)
:	stream(outputDevice), outputTimer(10000), sensors(sensors), control(control),
 	uartData(0), desiredTemperature(20)
{
}

void
task::IO::setOutputFrequency(OutputFrequency frequency)
{
	outputTimer.restart(static_cast<uint16_t>(frequency));
}

float
task::IO::getDesiredTemperature()
{
	return static_cast<float>(desiredTemperature);
}

bool
task::IO::update()
{
	PT_BEGIN();

	while(true)
	{
		if (outputTimer.isExpired())
		{
			stream << "T: ";
			for (uint8_t ii=0; ii < sensors.getNumberOfSensors(); ii++)
			{
				formatTemperature(sensors.getTemperature(ii));
				if (ii + 2 <= sensors.getNumberOfSensors()) {
					stream << ",\t";
				}
			}
			stream << xpcc::endl;

			stream << "P: " << heater.getPower() << xpcc::endl;
		}

		if (Uart::read(uartData))
		{
			updateParser(uartData);
		}

		PT_YIELD();
	}

	// return is included in PT_END();
	PT_END();
}

bool
task::IO::updateParser(uint8_t &input)
{
	switch (input)
	{
		case 'P':
			PsOn::reset();
			XPCC_LOG_INFO << "Power on" << xpcc::endl;
			index = 0;
			break;
		case 'p':
			PsOn::set();
			XPCC_LOG_INFO << "Power off" << xpcc::endl;
			index = 0;
			break;

		case '0':
		case '1':
		case '2':
		case '3':
		case '4':
		case '5':
		case '6':
		case '7':
		case '8':
		case '9':
			buffer[index++] = input;
			break;

		case 'C':
		{
			char *point = buffer + index;
			int16_t num = strtol(buffer, &point, 10);
			if (num == 0 && errno != 0)
			{
				XPCC_LOG_ERROR << "Failed to parse integer!" << xpcc::endl;
				return false;
			} else {
				XPCC_LOG_INFO << "Desired Temperature set = " << num << " C" << xpcc::endl;
			}
			control.setTemperature(num);
			desiredTemperature = num;
		}
			// break;

		case '\n':
			index = 0;
			for (uint8_t ii=0; ii < 20; ++ii)
			{
				buffer[ii] = ' ';
			}
			break;
	}

	return true;
}

void
task::IO::formatTemperature(float temperature)
{
	stream << static_cast<int8_t>(temperature) << ".";
	temperature = temperature - static_cast<int8_t>(temperature);
	temperature *= 100;
	if (temperature < 10)
		stream << "0";
	stream << static_cast<uint8_t>(temperature) << " C";
}
