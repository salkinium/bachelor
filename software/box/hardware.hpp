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
struct SensorData
{
	uint8_t tempData0[2];
	uint8_t tempData1[2];
	uint8_t tempData2[2];
}
sensorMessage __attribute__((packed));

// TMP102 and TMP175 drivers
#include <xpcc/driver/temperature/tmp102.hpp>
#include <xpcc/driver/temperature/tmp175.hpp>
typedef I2cMaster Twi;
xpcc::Tmp102<Twi> temperature1(sensorMessage.tempData1, 0x48);
//xpcc::Tmp102<Twi> temperature2(sensorMessage.tempData2, 0x49);
xpcc::Tmp175<Twi> temperatureOnBoard(sensorMessage.tempData0, 0b1001111);
xpcc::PeriodicTimer<> temperatureTimer(500);

// Serial debug
#include <xpcc/io/iodevice_wrapper.hpp>
typedef Uart0 Uart;
xpcc::IODeviceWrapper<Uart> logger;

#include <xpcc/debug/logger.hpp>
xpcc::log::Logger xpcc::log::debug(logger);
xpcc::log::Logger xpcc::log::info(logger);
xpcc::log::Logger xpcc::log::warning(logger);
xpcc::log::Logger xpcc::log::error(logger);

#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG


// TASKS ######################################################################
#include "tasks/task_software_pwm.hpp"
task::SoftwarePwm<HeaterPin, 333> heater(whiteLedLeft);
task::SoftwarePwm<HeaterFanPin, 50> heaterFan(whiteLedRight);

#endif // THESIS_HARDWARE
