// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_TEMPERATURE_CONTROL_HPP
#	error	"Don't include this file directly, use 'task_temperature_control.hpp' instead!"
#endif

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

task::TemperatureControl::TemperatureControl()
:	targetTemperature(0), timer(250), tPid(10, 0.4, 1.0, 0.7, 100)
{
}

void
task::TemperatureControl::setTemperature(float temperature)
{
	targetTemperature = temperature;
}

float
task::TemperatureControl::getTemperature()
{
	return temperature.getTemperature(1);
}

bool
task::TemperatureControl::run()
{
	heater.run();
	heaterFan.run();

	PT_BEGIN();

	while(true)
	{
		PT_WAIT_UNTIL(timer.isExpired());

		tPid.update(targetTemperature - getTemperature(), heater.getPower() == 0 && tPid.getLastError() < 1.5);

		// this scope is needed for the local variables
		{
			float temp = temperature.getTemperature(0);
			XPCC_LOG_DEBUG << "onBoard: " << static_cast<uint8_t>(temp) << ".";
			temp = temp - static_cast<uint8_t>(temp);
			temp *= 100;
			XPCC_LOG_DEBUG << static_cast<uint8_t>(temp) << " C ";

			temp = temperature.getTemperature(1);
			XPCC_LOG_DEBUG << "temp1: " << static_cast<uint8_t>(temp) << ".";
			temp = temp - static_cast<uint8_t>(temp);
			temp *= 100;
			XPCC_LOG_DEBUG << static_cast<uint8_t>(temp) << " C ";


			int16_t value = tPid.getValue();
			XPCC_LOG_DEBUG << "lastError= " << tPid.getLastError();
			XPCC_LOG_DEBUG << " errorSum= " << tPid.getErrorSum();
			XPCC_LOG_DEBUG << " value= " << value << xpcc::endl;

			heater.setPower(value < 0 ? 0 : value);
			uint8_t fanPower = value < 40 ? 40 : value;
			if (value < -50) fanPower = 0;
			heaterFan.setPower(fanPower);
		}
	}

	// return is included in PT_END();
	PT_END();
}
