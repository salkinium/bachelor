// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of my bachelor thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------

#include <xpcc/architecture/driver.hpp>
#include <xpcc/processing.hpp>

#include "hardware.hpp"
#include <stdlib.h>

using namespace xpcc::atmega;

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

// xpcc::Clock
ISR(TIMER2_OVF_vect)
{
	/* this interrupt is called every 1.111111111ms
	 * but the clock is only incremented by 1ms
	 * After 9 interrupts, 10ms in real life has elapsed
	 * but only 9ms have been counted.
	 * therefore after 9 interrupts, the clock is incremented twice
	 */

	static uint8_t cycles(9);
	xpcc::Clock::increment(1);
	if (!cycles--) {
		xpcc::Clock::increment(1);
		cycles = 9;
	}
}

int
main(void)
{
	// set the power pins
	PsOn::setOutput(xpcc::Gpio::High);
	PwrOk::setInput();

	// set the temperature pins
	HeaterPin::setOutput(xpcc::Gpio::Low);
	HeaterFanPin::setOutput(xpcc::Gpio::Low);
	CoolerPin::setOutput(xpcc::Gpio::Low);
	CoolerFanPin::setOutput(xpcc::Gpio::Low);

	// set the led pins
	initializeLeds();
	RedLedPin::setOutput();
	GreenLedPin::setOutput();
	BlueLedPin::setOutput();
	WhiteLeftLedPin::setOutput();
	WhiteRightLedPin::setOutput();

	// connect the peripherals
	Scl::connect(Twi::Scl);
	Sda::connect(Twi::Sda);
	Twi::initialize<Twi::DataRate::Standard>();

	GpioD0::connect(Uart::Rx);
	GpioD1::connect(Uart::Tx);
	Uart::initialize<Uart::B115200>();

	enableInterrupts();
	XPCC_LOG_INFO << "\n\nRESTART\n" << xpcc::endl;

//	temperature.addSensor(&sensor1);
	temperature.addSensor(&sensor2);
//	temperature.addSensor(&sensor3);
//	temperature.addSensor(&sensor4);

	inputOutput.setOutputFrequency(task::OutputFrequency::Seconds5);

	PsOn::reset();
	// wait for power supply to settle
	xpcc::delay_ms(500);

	temperature.configureSensors();

	while (1)
	{
		rgbLed.update();
		temperature.update();
		temperatureControl.update();
		inputOutput.update();
	}

	return 0;
}
