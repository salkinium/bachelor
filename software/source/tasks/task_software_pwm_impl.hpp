// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------
#ifndef TASK_SOFTWARE_PWM_HPP
#	error	"Don't include this file directly, use 'task_software_pwm.hpp' instead!"
#endif

template< typename Pin, uint16_t Period >
task::SoftwarePwm<Pin, Period>::SoftwarePwm(xpcc::ui::Led& led)
:	Protothread(), led(led), percent(0), setTime(0), periodTimer(Period), setTimeout(0)
{
}

template< typename Pin, uint16_t Period >
void
task::SoftwarePwm<Pin, Period>::setPower(uint8_t power)
{
	if (power > 99)
		power = 99;
	percent = power;
	float timeout = static_cast<float>(power) * Period / 100.f;
	setTime = static_cast<uint16_t>(timeout);
}

template< typename Pin, uint16_t Period >
uint8_t
task::SoftwarePwm<Pin, Period>::getPower()
{
	return percent;
}

template< typename Pin, uint16_t Period >
bool
task::SoftwarePwm<Pin, Period>::update()
{
	led.update();

	PT_BEGIN();

	while(true)
	{
		if (percent > 0) {
			Pin::set();
			led.setBrightness(150);
		}

		if (percent < 99) {
			PT_WAIT_UNTIL(setTimeout.isExpired() || periodTimer.isExpired());

			Pin::reset();
			led.setBrightness(0);
		}

		PT_WAIT_UNTIL(periodTimer.isExpired());

		setTimeout.restart(setTime);
	}

	// return is included in PT_END();
	PT_END();
}
