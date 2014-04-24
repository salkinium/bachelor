#ifndef TEST_H
#define TEST_H

enum {
  AM_SERIAL_MSG = 12,
  AM_RADIO_MSG = 13,
  AM_SENSOR_MSG = 14
};

enum {
  DELAY_SEND = 250,
  SENSING_PERIOD = 5*1024
};

enum {
  NONE = 0,
  SEND = 1,
  RECEIVE = 2,
  INVALID = 0xFF
};

int8_t beginCorrection = -120;

#ifndef TOSH_DATA_LENGTH
#define TOSH_DATA_LENGTH 110
#endif

typedef nx_struct test_header {
  nx_uint8_t type;
  nx_uint8_t channel;
  nx_uint8_t power;
  nx_uint8_t len;
  nx_uint16_t nodeid;
  nx_uint16_t seqnum;
  nx_uint8_t metadata[2];
} test_header_t;

typedef nx_struct radio_msg {
  nx_uint8_t data[TOSH_DATA_LENGTH-sizeof(test_header_t)];
} radio_msg_t;

typedef nx_struct serial_msg {
  test_header_t header;
  nx_uint8_t data[TOSH_DATA_LENGTH-sizeof(test_header_t)];
} serial_msg_t;

#ifdef SENSOR_READINGS
typedef nx_struct sensor_msg {
  nx_uint16_t nodeid;
  nx_uint16_t temperature;
  nx_uint16_t humidity;
} sensor_msg_t;
#endif

#endif
