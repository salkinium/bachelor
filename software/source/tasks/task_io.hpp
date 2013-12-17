// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_IO_HPP
#define TASK_IO_HPP

#include <xpcc/processing/protothread.hpp>
#include <xpcc/processing/periodic_timer.hpp>
#include <xpcc/io/iostream.hpp>
#include "task_temperature.hpp"

#include "../hardware.hpp"

namespace task
{

enum class
OutputFrequency
{
	Seconds10 = 10000,
	Seconds5 = 5000,
	Seconds2 = 2000,
	Seconds1 = 1000,
	Hz2 = 500,
	Hz3 = 333,
	Hz4 = 250,
};

class IO : private xpcc::pt::Protothread
{
public:
	IO(Temperature &sensors, TemperatureControl &control);

	void
	setOutputFrequency(OutputFrequency frequency);

	float
	getDesiredTemperature();

	bool
	update();

private:
	bool
	updateParser(uint8_t &input);

	void
	formatTemperature(float temperature);

private:
	xpcc::IOStream stream;
	xpcc::PeriodicTimer<> outputTimer;

	Temperature &sensors;
	TemperatureControl &control;

	uint8_t uartData;
	int8_t desiredTemperature;

	char buffer[20];
	uint8_t index;
};

} // namespace task

#include "task_io_impl.hpp"

#endif // TASK_IO_HPP
