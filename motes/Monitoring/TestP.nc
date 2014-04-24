#include "Test.h"


module TestP {
  uses {
    interface Boot;
    interface Timer<TMilli> as TimerSend;
    interface AMSend as RadioSend;
    interface Receive as RadioReceive;
    interface AMSend as SerialSend;
    interface Receive as SerialReceive;
    interface Packet as SerialPacket;
    interface CC2420Packet;
    interface RadioBackoff;
    interface PacketAcknowledgements;
    interface AMPacket;
    interface SplitControl as RadioControl;
    interface SplitControl as SerialControl;
    interface CC2420Config;
    interface Leds;
    interface Queue<serial_msg_t> as SerialQueue;
    interface Check as SendCheck;
    interface Check as RecvCheck;
    interface HplMsp430Usart as Usart;

#ifdef SENSOR_READINGS
    interface Read<uint16_t> as Temp;
    interface Read<uint16_t> as Hum;
    interface AMSend as SensorSend;
    interface Timer<TMilli> as SensorTimer;
#endif
  }
}

implementation {

  message_t radio_pkt;
  serial_msg_t conf;
  message_t serial_pkt;
  bool serial_busy;

#ifdef SENSOR_READINGS
  message_t sensor_pkt;
  sensor_msg_t *sensor_data;
#endif

  task void sendRadio();
  task void sendSerial();

  event void Boot.booted(){
#ifdef SENSOR_READINGS
    sensor_data = (sensor_msg_t *) 
      call SensorSend.getPayload(&sensor_pkt,
                                 sizeof(sensor_msg_t));
    sensor_data->nodeid = TOS_NODE_ID;
    call SensorTimer.startPeriodic(SENSING_PERIOD);
#endif
    serial_busy = FALSE;
    call RadioControl.start();
    call SerialControl.start();
  }

  event void RadioControl.startDone(error_t error){
    if (error != SUCCESS)
      call RadioControl.start();
  }

  event void RadioControl.stopDone(error_t error){}

  event void SerialControl.startDone(error_t error){
    if (error != SUCCESS)
        call SerialControl.start();
  }

  event void SerialControl.stopDone(error_t error){}

  async event void RadioBackoff.requestCca(message_t *msg){
    call RadioBackoff.setCca(FALSE);
  }

  async event void RadioBackoff.requestCongestionBackoff(message_t *msg){
    call RadioBackoff.setCongestionBackoff(0);
  }

  async event void RadioBackoff.requestInitialBackoff(message_t *msg){
    call RadioBackoff.setInitialBackoff(0);
  }

  event void RadioSend.sendDone(message_t* msg,
                                error_t error){
  }

  event void SerialSend.sendDone(message_t* msg,
                                 error_t error){
    serial_busy = FALSE;
    if (!call SerialQueue.empty())
      post sendSerial();
  }

  event message_t* RadioReceive.receive(message_t *msg,
                                        void * payload,
                                        uint8_t len){
    memset(msg, 0, sizeof(message_t));
    return msg;
  }

  void processMsg(uint8_t type, message_t *msg, uint8_t *metadata){
    serial_msg_t receivedmsg;
    receivedmsg.header.type = type;
    receivedmsg.header.channel = conf.header.channel;
    receivedmsg.header.power = conf.header.power;
    receivedmsg.header.len = conf.header.len;
    receivedmsg.header.nodeid = TOS_NODE_ID;
    receivedmsg.header.seqnum = conf.header.seqnum;
    memcpy(receivedmsg.header.metadata, metadata, 2);
    memcpy(receivedmsg.data, msg, TOSH_DATA_LENGTH-sizeof(test_header_t));
    call SerialQueue.enqueue(receivedmsg);
    post sendSerial();
  }


  event void SendCheck.sent(message_t *msg, uint8_t *metadata){
    processMsg(SEND,msg,metadata);
  }

  event void RecvCheck.sent(message_t *msg, uint8_t *metadata){
    processMsg(RECEIVE,msg,metadata);
  }
  
  event message_t* SerialReceive.receive(message_t *msg,
                                        void * payload,
                                        uint8_t len){
    conf = *((serial_msg_t *) payload);
    if (conf.header.channel != call CC2420Config.getChannel()){
      call CC2420Config.setChannel(conf.header.channel);
    } else if (conf.header.nodeid == TOS_NODE_ID){
      call TimerSend.startOneShot(10);
    }
    return msg;
  }


  event void TimerSend.fired(){
    post sendRadio();
  }

  task void sendSerial(){
    if (!serial_busy && !call SerialQueue.empty()){
      serial_msg_t *tmsg = (serial_msg_t *) 
        call SerialSend.getPayload(&serial_pkt,
                                   sizeof(serial_msg_t));
      serial_msg_t temp = call SerialQueue.dequeue();
      memcpy(tmsg, &temp, sizeof(serial_msg_t));
      if (call SerialSend.send(AM_BROADCAST_ADDR, &serial_pkt,
                               sizeof(serial_msg_t))
          == SUCCESS){
        serial_busy = TRUE;
      } else {
        post sendSerial();
      }
    }
  }

  task void sendRadio(){
    radio_msg_t *tmsg = (radio_msg_t *) 
      call RadioSend.getPayload(&radio_pkt,
                                sizeof(radio_msg_t));
    memset(&radio_pkt, 0, sizeof(message_t));
    memcpy(tmsg, conf.data, conf.header.len);
    call CC2420Packet.setPower(&radio_pkt, conf.header.power);
    call PacketAcknowledgements.noAck(&radio_pkt);
    if (call RadioSend.send(AM_BROADCAST_ADDR, &radio_pkt, 
                            conf.header.len) != SUCCESS){
    }
  }

  event void CC2420Config.syncDone(error_t error) {
    if (conf.header.nodeid == TOS_NODE_ID)
      call TimerSend.startOneShot(10);
  }

#ifdef SENSOR_READINGS
  task void sendSensor(){
    if (call SensorSend.send(AM_BROADCAST_ADDR, &sensor_pkt,
                             sizeof(sensor_msg_t))
        != SUCCESS){
      post sendSensor();
    }
  }

  event void SensorTimer.fired(){
    call Temp.read(); 
  }

  event void Temp.readDone(error_t result, uint16_t val){
    if (result != SUCCESS)
      val += 0xF000;
    sensor_data->temperature = val;
    if (beginCorrection == -120) {
    	beginCorrection = ((val*0.01) - 40 - 26)*0.48 - 15;
    }
    
    //88 => 15.6
    //26 => -15
    
    call Usart.compensateTemperature115200((val*0.01) - 40 - beginCorrection);
    call Hum.read();
  }


  event void Hum.readDone(error_t result, uint16_t val){
    if (result != SUCCESS)
      val += 0xF000;
    sensor_data->humidity = val;
    post sendSensor();
  }

  event void SensorSend.sendDone(message_t* msg,
                                 error_t error){
  }
#endif
}

