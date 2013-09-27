// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_SOFTWARE_PWM_HPP
#define TASK_SOFTWARE_PWM_HPP

#include <xpcc/processing/protothread.hpp>
#include <xpcc/ui/led.hpp>

namespace task
{

template< typename Pin, uint16_t Period=500 >
class SoftwarePwm : private xpcc::pt::Protothread
{
public:
	SoftwarePwm(xpcc::ui::Led& led);

	/// sets percentage value from 0 to 99.
	void
	setPower(uint8_t power);

	uint8_t
	getPower();

	bool
	run();

private:
	xpcc::ui::Led& led;
	uint8_t percent;
	uint16_t setTime;
	xpcc::PeriodicTimer<> periodTimer;
	xpcc::Timeout<> setTimeout;
};

} // namespace task

#include "task_software_pwm_impl.hpp"

#endif // TASK_SOFTWARE_PWM_HPP
