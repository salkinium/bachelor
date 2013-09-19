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
#include "leds.hpp"

using namespace xpcc::atmega;

// IO #########################################################################
// ATMEL ATMEGA328P
//                    +-v-+
//     (!RESET) PC6  1|   |28  PC5 (SCL)
//        (RXD) PD0  2|   |27  PC4 (SDA)
//        (TXD) PD1  3|   |26  PC3 (COLD_FAN)
//              PD2  4|   |25  PC2 (HEAT_FAN)
// (GREEN,OC2B) PD3  5|   |24  PC1 (COLD)
//              PD4  6|   |23  PC0 (HEAT)
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
typedef GpioOutputB2 Red;
typedef GpioOutputD3 Green;
typedef GpioOutputB1 Blue;

// Signal
typedef GpioOutputD6 WhiteLeft;
typedef GpioOutputB5 WhiteRight;

// Power
typedef GpioOutputB0 PsOn;
typedef GpioOpenDrain<GpioD7> PwrOk;

// Control
typedef xpcc::GpioInverted<GpioC0> Heater;
typedef xpcc::GpioInverted<GpioC2> HeaterFan;
typedef xpcc::GpioInverted<GpioC1> Cooler;
typedef xpcc::GpioInverted<GpioC3> CoolerFan;

// Leds
WhiteLedLeft whiteLeft;
WhiteLedRight whiteRight;
xpcc::ui::DoubleIndicator heartbeatLed(&whiteLeft);
Heartbeat heartbeat;

RedLed red;
GreenLed green;
BlueLed blue;

xpcc::ui::RgbLed rgb(&red, &green, &blue);

// COMMUNICATION ##############################################################
// Message
struct SensorData
{
	uint8_t tempData1[2];
	uint8_t tempData2[2];
}
sensorMessage __attribute__((packed));

// TMP102 driver
#include <xpcc/driver/temperature/tmp102.hpp>
typedef I2cMaster Twi;
xpcc::Tmp102<Twi> temperature1(sensorMessage.tempData1, 0x48);
xpcc::Tmp102<Twi> temperature2(sensorMessage.tempData2, 0x49);
xpcc::PeriodicTimer<> temperatureTimer(250);

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
#define	XPCC_LOG_LEVEL xpcc::log::DISABLED

#endif // THESIS_HARDWARE
