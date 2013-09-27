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

#include <xpcc/architecture/platform.hpp>
#include <xpcc/processing.hpp>
#include <xpcc/ui/led.hpp>
#include <xpcc/debug/logger.hpp>

void
initializeLeds()
{
	// Timer0 is used to fade the two white LEDs
	// Fast PWM mode, non-inverting mode for both A and B compare outputs
	// Clear OC0X on Compare Match, set OC0X at Bottom
	TCCR0A = (1 << WGM01) | (1 << WGM00) |
			(1 << COM0A1) | (1 << COM0B1);
	// 14745.6kHz / 64 / 256 = 0.9kHz
	// Prescaler 64, enable Timer0
	TCCR0B = (1 << CS01) | (1 << CS00);
	// No Interrupt required
	TIMSK0 = 0;

	// Timer1 is used to fade the red and blue Leds at 10bit resolution
	// Fast PWM mode, non-inverting mode for both A and B compare outputs
	// Clear OC0X on Compare Match, set OC0X at Bottom
	TCCR1A = (1 << WGM11) | (1 << WGM10) |
			(1 << COM1A1) | (1 << COM1B1);
	// 14745.6kHz / 8 / 1024 = 1.8kHz
	// Prescaler 8, enable Timer1
	TCCR1B = (1 << WGM12) | (1 << CS11);
	// No Interrupt required
	TIMSK1 = 0;

	// Timer2 is used to fade the green Led and drive xpcc::Clock
	// Fast PWM mode, non-inverting mode for B compare outputs
	// Clear OC0X on Compare Match, set OC0X at Bottom
	TCCR2A = (1 << WGM21) | (1 << WGM20) |
			(1 << COM2B1);
	// 14745.6kHz / 64 / 256 = 0.9kHz ~ 1.1111ms
	// Prescaler 64, enable Timer2
	TCCR2B = (1 << CS22);
	// Enable Overflow Interrupt for xpcc::Clock
	TIMSK2 = (1 << TOIE2);
}

class WhiteLedLeft : public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint8_t> table;

	virtual void
	setValue(uint8_t brightness)
	{
		OCR0A = 255 - table[brightness];
	}

public:
	WhiteLedLeft(const uint8_t* table=xpcc::ui::table8_256)
	:	Led(), table(table)
	{
	}
};

class WhiteLedRight : public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint8_t> table;

	virtual void
	setValue(uint8_t brightness)
	{
		OCR0B = 255 - table[brightness];
	}

public:
	WhiteLedRight(const uint8_t* table=xpcc::ui::table8_256)
	:	Led(), table(table)
	{
	}
};

class RedLed : public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint16_t> table;

	virtual void
	setValue(uint8_t brightness)
	{
		OCR1B = 1023 - table[brightness];
	}

public:
	RedLed(const uint16_t* table=xpcc::ui::table10_256)
	:	Led(), table(table)
	{
	}
};

class GreenLed : public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint8_t> table;

	virtual void
	setValue(uint8_t brightness)
	{
		OCR2B = 255 - table[brightness];
	}

public:
	GreenLed(const uint8_t* table=xpcc::ui::table8_256)
	:	Led(), table(table)
	{
	}
};

class BlueLed : public xpcc::ui::Led
{
	xpcc::accessor::Flash<uint16_t> table;

	virtual void
	setValue(uint8_t brightness)
	{
		OCR1A = 1023 - table[brightness];
	}

public:
	BlueLed(const uint16_t* table=xpcc::ui::table10_256)
	:	Led(), table(table)
	{
	}
};



#endif // LEDS_HPP
