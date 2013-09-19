// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of the my thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------

#include <xpcc/architecture/driver.hpp>
#include <xpcc/processing.hpp>

#include "hardware.hpp"
#include "leds.hpp"

using namespace xpcc::atmega;

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

// xpcc::Clock
ISR(TIMER2_OVF_vect)
{
	/* this interrupt is called every 4.4444444ms
	 * but the clock is only incremented by 4ms
	 * After 9 interrupts, 40ms in real life has elapsed
	 * but only 36ms have been counted.
	 * therefore after 9 interrupts, the clock is incremented twice
	 */

	static uint8_t cycles(9);
	xpcc::Clock::increment(4);
	if (!cycles--) {
		xpcc::Clock::increment(4);
		cycles = 9;
	}
}

int
main(void)
{
	// set the power pins
	PsOn::setOutput(xpcc::Gpio::HIGH);
	PwrOk::setInput();

	// set the temperature pins
	Heater::setOutput(xpcc::Gpio::LOW);
	HeaterFan::setOutput(xpcc::Gpio::LOW);
	Cooler::setOutput(xpcc::Gpio::LOW);
	CoolerFan::setOutput(xpcc::Gpio::LOW);

	// set the led pins
	initializeLeds();
	RedLedPin::setOutput();
	GreenLedPin::setOutput();
	BlueLedPin::setOutput();
	WhiteLeftLedPin::setOutput();
	WhiteRightLedPin::setOutput();

	GpioC5::connect(Twi::Scl);
	GpioC4::connect(Twi::Sda);
	Twi::initialize<Twi::DataRate::Fast>();

	GpioD0::connect(Uart::Rx);
	GpioD1::connect(Uart::Tx);
	Uart::initialize<115200>();

	xpcc::atmega::enableInterrupts();
	XPCC_LOG_INFO << "\n\nRESTART\n\n";

	PsOn::reset();

	uint8_t hello;
	while (1)
	{
		rgb.run();
		whiteLeft.run();
		heartbeat.run();

		if (Uart::read(hello))
		{
			switch (hello)
			{
				case 'P':
					PsOn::reset();
					XPCC_LOG_DEBUG << "P on" << xpcc::endl;
					break;
				case 'p':
					PsOn::set();
					XPCC_LOG_DEBUG << "P off" << xpcc::endl;
					break;
				case 'F':
					HeaterFan::set();
					XPCC_LOG_DEBUG << "HF on" << xpcc::endl;
					break;
				case 'f':
					HeaterFan::reset();
					XPCC_LOG_DEBUG << "HF off" << xpcc::endl;
					break;
				case 'H':
					Heater::set();
					XPCC_LOG_DEBUG << "H on" << xpcc::endl;
					break;
				case 'h':
					Heater::reset();
					XPCC_LOG_DEBUG << "H off" << xpcc::endl;
					break;
			}
		}
	}

	return 0;
}
