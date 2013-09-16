// coding: utf-8
#include <xpcc/architecture/platform.hpp>
#include <xpcc/architecture/driver.hpp>
#include <xpcc/processing.hpp>

using namespace xpcc::atmega;

// IO #########################################################################
// ATMEL ATMEGA328P
//                  +-v-+
//   (!RESET) PC6  1|   |28  PC5 (SCL)
//      (RXD) PD0  2|   |27  PC4 (SDA)
//      (TXD) PD1  3|   |26  PC3
//     (INT0) PD2  4|   |25  PC2
//     (OC2B) PD3  5|   |24  PC1
//            PD4  6|   |23  PC0
//            VCC  7|   |22  GND
//            GND  8|   |21  AREF
//    (XTAL1) PB6  9|   |20  AVCC
//    (XTAL2) PB7 10|   |19  PB5 (SCK)
//     (OC0B) PD5 11|   |18  PB4 (MISO)
//     (OC0A) PD6 12|   |17  PB3 (MOSI)
//            PD7 13|   |16  PB2 (!SS)
//            PB0 14|   |15  PB1 (OC1A)
//                  +---+

// communication message
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
//#define	XPCC_LOG_LEVEL xpcc::log::DEBUG
#define	XPCC_LOG_LEVEL xpcc::log::DISABLED

// xpcc::Clock
ISR(TIMER0_COMPA_vect)
{
	xpcc::Clock::increment();
}

int
main(void)
{
	// Initiate 1kHz interrupt for clock using timer0
	// Clear Timer on Compare Match (CTC) Mode
	TCCR0A = (1 << WGM01);
	// 1kHz (= 20000kHz / 256 / 78)
	OCR0A = 78;
	// Prescaler 256, enable Timer0
	TCCR0B = (1 << CS02);
	// Enable Overflow Interrupt
	TIMSK0 = (1 << OCIE0A);

	GpioC5::connect(Twi::Scl);
	GpioC4::connect(Twi::Sda);
	Twi::initialize<Twi::DataRate::Fast>();

	GpioD0::connect(Uart::Rx);
	GpioD1::connect(Uart::Tx);
	Uart::initialize<38400>();

	XPCC_LOG_INFO << "\n\nRESTART\n\n";
	xpcc::atmega::enableInterrupts();

	while (1)
	{
		if (temperatureTimer.isExpired())
		{
			temperature1.readTemperature();
			temperature2.readTemperature();
		}

		if (temperature1.isNewDataAvailable())
		{
			XPCC_LOG_DEBUG << "Temp1: " << temperature1.getTemperature() << xpcc::endl;
		}

		if (temperature2.isNewDataAvailable())
		{
			float temp = temperature2.getTemperature();
			if (temp > 70) {
				XPCC_LOG_WARNING << "Temp2 is too high!!: " << (uint8_t)temp << xpcc::endl;
			} else {
				XPCC_LOG_DEBUG << "Temp2: " << (uint8_t)temp << xpcc::endl;
			}
		}

		temperature1.update();
		temperature2.update();
	}

	return 0;
}
