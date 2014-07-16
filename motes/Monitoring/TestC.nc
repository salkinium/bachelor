#include "Test.h"

configuration TestC {
}


implementation {
  components MainC;
  components ActiveMessageC;
  components SerialActiveMessageC;
  components new AMSenderC(AM_RADIO_MSG) as RadioSend;
  components new AMReceiverC(AM_RADIO_MSG) as RadioReceive;
  components new SerialAMSenderC(AM_SERIAL_MSG) as SerialSend;
  components new SerialAMReceiverC(AM_SERIAL_MSG) as SerialReceive;
  components CC2420ControlC;
  components CC2420PacketC;
  components CC2420CsmaC;
  components CC2420ReceiveC;
  components LedsC;
  components new TimerMilliC() as TimerSend;
  components new QueueC(serial_msg_t, 5) as SerialQueue;
  components new Msp430Usart1C() as MyUsart1C;

  components TestP;

  TestP.Boot -> MainC;
  TestP.TimerSend -> TimerSend;
  TestP.RadioControl -> ActiveMessageC;
  TestP.RadioSend -> RadioSend;
  TestP.RadioReceive -> RadioReceive;
  TestP.SerialControl -> SerialActiveMessageC;
  TestP.SerialSend -> SerialSend;
  TestP.SerialReceive -> SerialReceive;
  TestP.CC2420Config -> CC2420ControlC;
  TestP.RadioBackoff -> CC2420CsmaC;
  TestP.CC2420Packet -> CC2420PacketC;
  TestP.PacketAcknowledgements -> ActiveMessageC;
  TestP.AMPacket -> ActiveMessageC;
  TestP.SerialPacket -> SerialActiveMessageC;
  TestP.Leds -> LedsC;
  TestP.SerialQueue -> SerialQueue;
  TestP.Usart -> MyUsart1C;

  TestP.SendCheck->CC2420CsmaC.Check;
  TestP.RecvCheck->CC2420ReceiveC.Check;

#ifdef NOISE_READING
  // Wiring for Noise Reading
  TestP.Noise -> CC2420ControlC;
#endif

#ifdef SENSOR_READINGS
  components new SerialAMSenderC(AM_SENSOR_MSG) as SerialSensorSend;
  components new TimerMilliC() as SensorTimer;
  components new SensirionSht11C() as TempHum;

  TestP.Temp -> TempHum.Temperature;
  TestP.Hum -> TempHum.Humidity;
  TestP.SensorSend -> SerialSensorSend;
  TestP.SensorTimer -> SensorTimer;
#endif
}
