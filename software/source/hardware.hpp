// coding: utf-8
/* Copyright (c) 2013, Niklas Hauser
* All Rights Reserved.
*
* The file is part of the my thesis and is released under the 3-clause BSD
* license. See the file `LICENSE` for the full license governing this code.
*/
// ----------------------------------------------------------------------------

#ifndef THESIS_HARDWARE
#define THESIS_HARDWARE

#include <xpcc/architecture/platform.hpp>

using namespace xpcc::atmega;

// IO #########################################################################
// ATMEL ATMEGA328P
//                    +-v-+
//     (!RESET) PC6  1|   |28  PC5 (SCL)
//        (RXD) PD0  2|   |27  PC4 (SDA)
//        (TXD) PD1  3|   |26  PC3 (HEAT_FAN)
//              PD2  4|   |25  PC2 (COLD_FAN)
// (GREEN,OC2B) PD3  5|   |24  PC1 (HEAT)
//              PD4  6|   |23  PC0 (COLD)
//              VCC  7|   |22  GND
//              GND  8|   |21  AREF
//      (XTAL1) PB6  9|   |20  AVCC
//      (XTAL2) PB7 10|   |19  PB5 (SCK)
//  (LED2,OC0B) PD5 11|   |18  PB4 (MISO)
//  (LED1,OC0A) PD6 12|   |17  PB3 (MOSI)
//     (PWR_OK) PD7 13|   |16  PB2 (RED,OC1B)
//      (PS_ON) PB0 14|   |15  PB1 (BLUE,OC1A)
//                    +---+

// Color
typedef GpioOutputB2 RedLedPin;
typedef GpioOutputD3 GreenLedPin;
typedef GpioOutputB1 BlueLedPin;

// Signal
typedef GpioOutputD6 WhiteLeftLedPin;
typedef GpioOutputD5 WhiteRightLedPin;

// Power
//typedef GpioOpenDrain<GpioB0> PsOn;
typedef GpioOutputB0 PsOn;
typedef GpioInputD7 PwrOk;

// Control
typedef GpioOutputC1 HeaterPin;
typedef GpioOutputC3 HeaterFanPin;
typedef GpioOutputC0 CoolerPin;
typedef GpioOutputC2 CoolerFanPin;

// Leds
#include "leds.hpp"
WhiteLedLeft whiteLedLeft;
WhiteLedRight whiteLedRight;
RedLed redLed;
GreenLed greenLed;
BlueLed blueLed;

xpcc::ui::RgbLed rgbLed(redLed, greenLed, blueLed);

// COMMUNICATION ##############################################################
// Message
struct
{
	uint8_t temperature0[2];
	uint8_t temperature1[2];
	uint8_t temperature2[2];
    uint8_t temperature3[2];
    uint8_t temperature4[2];
} rawSensorData;

// TMP102 and TMP175 drivers
#include <xpcc/driver/temperature/tmp102.hpp>
#include <xpcc/driver/temperature/tmp175.hpp>
/*
typedef GpioC4 Sda;
typedef GpioC5 Scl;
typedef I2cMaster Twi;
/*/
typedef GpioOpenDrain<GpioC4> Sda;
typedef GpioOpenDrain<GpioC5> Scl;
typedef xpcc::SoftwareI2cMaster<Scl, Sda> Twi;
//*/

// This sensor is always present
xpcc::Tmp175<Twi> sensor0(rawSensorData.temperature0, 0b1001111);

// these sensors are purely optional
xpcc::Tmp102<Twi> sensor1(rawSensorData.temperature1, 0b1001000);
xpcc::Tmp102<Twi> sensor2(rawSensorData.temperature2, 0b1001001);
xpcc::Tmp102<Twi> sensor3(rawSensorData.temperature3, 0b1001010);
xpcc::Tmp102<Twi> sensor4(rawSensorData.temperature4, 0b1001011);

// Serial debug
#include <xpcc/io/iodevice_wrapper.hpp>
typedef Uart0 Uart;
xpcc::IODeviceWrapper<Uart> outputDevice;

#include <xpcc/debug/logger/style_wrapper.hpp>
#include <xpcc/debug/logger/style/prefix.hpp>
#include <xpcc/debug/logger.hpp>
xpcc::log::StyleWrapper< xpcc::log::Prefix< char[10] > > loggerDeviceDebug (
		xpcc::log::Prefix< char[10] > ("Debug:   ", outputDevice ) );
xpcc::log::Logger xpcc::log::debug( loggerDeviceDebug );

xpcc::log::StyleWrapper< xpcc::log::Prefix< char[10] > > loggerDeviceInfo (
		xpcc::log::Prefix< char[10] > ("Info:    ", outputDevice ) );
xpcc::log::Logger xpcc::log::info( loggerDeviceInfo );

xpcc::log::StyleWrapper< xpcc::log::Prefix< char[10] > > loggerDeviceWarning (
		xpcc::log::Prefix< char[10] > ("Warning: ", outputDevice ) );
xpcc::log::Logger xpcc::log::warning( loggerDeviceWarning );

xpcc::log::StyleWrapper< xpcc::log::Prefix< char[10] > > loggerDeviceError (
		xpcc::log::Prefix< char[10] > ("Error    ", outputDevice ) );
xpcc::log::Logger xpcc::log::error( loggerDeviceError );

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG


// TASKS ######################################################################
#include "tasks/task_software_pwm.hpp"
task::SoftwarePwm<HeaterPin, 333> heater(whiteLedLeft);
task::SoftwarePwm<HeaterFanPin, 33> heaterFan(whiteLedRight);

#include "tasks/task_temperature.hpp"
task::Temperature temperature;

#include "tasks/task_temperature_control.hpp"
task::TemperatureControl temperatureControl;

#include "tasks/task_io.hpp"
task::IO inputOutput(temperature, temperatureControl);

#endif // THESIS_HARDWARE
