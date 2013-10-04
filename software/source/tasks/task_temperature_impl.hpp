// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_TEMPERATURE_HPP
#	error	"Don't include this file directly, use 'task_temperature.hpp' instead!"
#endif

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::ERROR

task::Temperature::Temperature()
:	readTimer(250), temperatures{0,0,0,0,0}
{
}

bool
task::Temperature::configureSensors()
{
	xpcc::Timeout<> configTimeout(1000);
	bool success(true);

	while(!(success = sensor0.configure()) && !configTimeout.isExpired())
		;
	if (!success) {
		XPCC_LOG_ERROR << "On Board Sensor config timed out!" << xpcc::endl;
		return false;
	}
	configTimeout.restart(1000);
	while(!(success = sensor1.configure()) && !configTimeout.isExpired())
		;
	if (!success) {
		XPCC_LOG_ERROR << "Temp1 Sensor config timed out!" << xpcc::endl;
		return false;
	}

	return true;
}

float
task::Temperature::getAverage()
{
	float sum = temperatures[0] + temperatures[1];
	return (sum / 2.0f);
}

float
task::Temperature::getTemperature(uint8_t sensor)
{
	if (sensor > 1) return 0;
	return temperatures[sensor];
}

bool
task::Temperature::run()
{
	sensor0.update();
	sensor1.update();

	PT_BEGIN();

	while(true)
	{
		if (readTimer.isExpired())
		{
			sensor0.readTemperature();
			sensor1.readTemperature();

			float temp = getTemperature(1);
			temp -= 20;
			temp *= 2.65;
			uint16_t raw = temp < 0 ? 0 : temp;
			uint8_t value = raw > 180 ? 180 : raw;
			rgbLed.fadeTo(250, xpcc::color::Hsv(180-value, 255, 255));
		}

		if (sensor0.isNewDataAvailable())
		{
			XPCC_LOG_DEBUG << XPCC_FILE_INFO;
			XPCC_LOG_DEBUG << "sensor0 new data" << xpcc::endl;
			sensor0.getData();
			temperatures[0] = sensor0.getTemperature();
		}

		if (sensor1.isNewDataAvailable())
		{
			sensor1.getData();
			temperatures[1] = sensor1.getTemperature();
		}

		PT_YIELD();
	}

	// return is included in PT_END();
	PT_END();
}
