// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_TEMPERATURE_HPP
#define TASK_TEMPERATURE_HPP

#include <xpcc/processing/protothread.hpp>
#include <xpcc/processing/periodic_timer.hpp>
#include <xpcc/debug/logger.hpp>
#include <xpcc/container.hpp>

#include "../hardware.hpp"

namespace task
{

class Temperature : private xpcc::pt::Protothread
{
public:
	Temperature();

	uint8_t
	addSensor(xpcc::Tmp102<Twi> *sensor);

	uint8_t
	getNumberOfSensors();

	bool
	configureSensors();

	/// @return	the average temperature
	float
	getAverage();

	float
	getTemperature(uint8_t sensor);

	bool
	update();

private:
	xpcc::PeriodicTimer<> readTimer;
	float temperatures[5];
	uint8_t numberOfSensors;

	xpcc::Tmp102<Twi>* sensorList[4];
};

} // namespace task

#include "task_temperature_impl.hpp"

#endif // TASK_TEMPERATURE_HPP
