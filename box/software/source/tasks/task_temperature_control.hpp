// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_TEMPERATURE_CONTROL_HPP
#define TASK_TEMPERATURE_CONTROL_HPP

#include <xpcc/processing/protothread.hpp>
#include <xpcc/processing/periodic_timer.hpp>
#include <xpcc/math/filter/pid.hpp>

#include "../hardware.hpp"

namespace task
{

class TemperatureControl : private xpcc::pt::Protothread
{
public:
	TemperatureControl();

	/// sets a new target temperature
	void
	setTemperature(float temperature);

	/// @return	the current temperature
	float
	getTemperature();

	/// @return	remaining time in seconds, that it will take to reach target temperature
	uint16_t
	getEstimatedRemainingTime();

	bool
	update();

private:
	float targetTemperature;
	xpcc::PeriodicTimer<> timer;
	xpcc::Pid<float, 100> tPid;
};

} // namespace task

#include "task_temperature_control_impl.hpp"

#endif // TASK_TEMPERATURE_CONTROL_HPP
