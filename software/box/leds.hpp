// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of the my thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------


#ifndef LEDS_HPP
#define LEDS_HPP

#include "hardware.hpp"
#include <xpcc/ui/led.hpp>

void
initializeTimers()
{
	// Timer0 is used to fade the two white LEDs
	// Fast PWM mode, interting mode for both A and B compare outputs
	// Set OC0X on Compare Match, clear OC0X at Bottom
	TCCR0A = (1 << WGM01) | (1 << WGM00) | \
			(1 << COM0A1) | (1 << COM0A0) | \
			(1 << COM0B1) | (1 << COM0B0);
	// 14745.6kHz / 64 / 256 = 0.9kHz
	// Prescaler 64, enable Timer0
	TCCR0B = (1 << CS01) | (1 << CS00);
	// No Interrupt required
	TIMSK0 = 0;

	// Timer1 is used to fade the red and blue Leds at 10bit resolution
	// Fast PWM mode, interting mode for A and B compare outputs
	// Set OC0X on Compare Match, clear OC0X at Bottom
	TCCR1A = (1 << WGM11) | (1 << WGM10) | \
			(1 << COM1A1) | (1 << COM1A0) | \
			(1 << COM1B1) | (1 << COM1B0);
	// 14745.6kHz / 8 / 1024 = 1.8kHz
	// Prescaler 8, enable Timer1
	TCCR1B = (1 << WGM11) | (1 << CS12);
	// No Interrupt required
	TIMSK1 = 0;

	// Timer2 is used to fade the green Led and drive xpcc::Clock
	// Fast PWM mode, interting mode for A compare outputs
	// Set OC0X on Compare Match, clear OC0X at Bottom
	TCCR2A = (1 << WGM01) | (1 << WGM00) | \
			(1 << COM0A1) | (1 << COM0A0) | \
			(1 << COM0B1) | (1 << COM0B0);
	// 14745.6kHz / 256 / 256 = 0.225kHz ~ 4.444444ms
	// Prescaler 256, enable Timer2
	TCCR2B = (1 << CS22);
	// Enable Overflow Interrupt for xpcc::Clock
	TIMSK2 = (1 << TOIE2);
}

class WhiteLedLeft : virtual public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint8_t> table;

	virtual void
	setValue(uint16_t brightness)
	{
		OCR0A = 255-table[brightness];
	}

public:
	WhiteLedLeft(const uint8_t* table=xpcc::ui::table8_256, std::size_t const tableSize=256)
	:	Led(tableSize), table(table)
	{
	}
};

class WhiteLedRight : virtual public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint8_t> table;

	virtual void
	setValue(uint16_t brightness)
	{
		OCR0B = 255-table[brightness];
	}

public:
	WhiteLedRight(const uint8_t* table=xpcc::ui::table8_256, std::size_t const tableSize=256)
	:	Led(tableSize), table(table)
	{
	}
};


#endif // LEDS_HPP
