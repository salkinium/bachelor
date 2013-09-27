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
	HeaterPin::setOutput(xpcc::Gpio::LOW);
	HeaterFanPin::setOutput(xpcc::Gpio::LOW);
	CoolerPin::setOutput(xpcc::Gpio::LOW);
	CoolerFanPin::setOutput(xpcc::Gpio::LOW);

	// set the led pins
	initializeLeds();
	RedLedPin::setOutput();
	GreenLedPin::setOutput();
	BlueLedPin::setOutput();
	WhiteLeftLedPin::setOutput();
	WhiteRightLedPin::setOutput();

	// connect the peripherals
	GpioC5::connect(Twi::Scl);
	GpioC4::connect(Twi::Sda);
	Twi::initialize<Twi::DataRate::Standard>();

	GpioD0::connect(Uart::Rx);
	GpioD1::connect(Uart::Tx);
	Uart::initialize<Uart::B115200>();

	xpcc::atmega::enableInterrupts();
	XPCC_LOG_INFO << "\n\nRESTART\n\n";

	PsOn::reset();

	temperature.configureSensors();

	uint8_t uartRead;
	uint8_t fanPower(0);
	uint8_t heatPower(0);
	xpcc::PeriodicTimer<> temperatureTimer(500);

	while (1)
	{
		rgbLed.run();
		temperature.run();
		temperatureControl.run();

		if (temperatureTimer.isExpired())
		{
			float temp = temperature.getTemperature(1);
			temp -= 20;
			temp *= 2.6;
			uint16_t raw = temp < 0 ? 0 : temp;
			uint8_t value = raw > 180 ? 180 : raw;
			rgbLed.fadeTo(480, xpcc::color::Hsv(180-value, 255, 255));
		}

		if (Uart::read(uartRead))
		{
			switch (uartRead)
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
					if (fanPower <= 90) fanPower += 10;
					heaterFan.setPower(fanPower);
					XPCC_LOG_DEBUG << "Fan++: " << fanPower << xpcc::endl;
					break;
				case 'f':
					if (fanPower >= 10) fanPower -= 10;
					heaterFan.setPower(fanPower);
					XPCC_LOG_DEBUG << "Fan--: " << fanPower << xpcc::endl;
					break;
				case 'H':
					if (heatPower <= 90) heatPower += 10;
					heater.setPower(heatPower);
					XPCC_LOG_DEBUG << "Heat++: " << heatPower << xpcc::endl;
					break;
				case 'h':
					if (heatPower >= 10) heatPower -= 10;
					heater.setPower(heatPower);
					XPCC_LOG_DEBUG << "Heat--: " << heatPower << xpcc::endl;
					break;
			}
		}
	}

	return 0;
}
