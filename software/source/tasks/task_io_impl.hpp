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

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::ERROR

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
			}
			stream << xpcc::endl;
		}

		if (Uart::read(uartData))
		{
			if (!updateParser(uartData))
			{
				XPCC_LOG_ERROR << XPCC_FILE_INFO;
				XPCC_LOG_ERROR << "Unable to format input." << xpcc::endl;
			}
		}

		PT_YIELD();
	}

	// return is included in PT_END();
	PT_END();
}

bool
task::IO::updateParser(uint8_t &input)
{
	return false;
}

void
task::IO::formatTemperature(float temperature)
{
	stream << static_cast<int8_t>(temperature) << ".";
	temperature = temperature - static_cast<int8_t>(temperature);
	temperature *= 100;
	stream << static_cast<uint8_t>(temperature) << " C, ";
}
