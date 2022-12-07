//      ******************************************************************
//      *                                                                *
//      *                      Constant declarations                     *
//      *                                                                *
//      *               Copyright (c) S. Reifel & Co,  2022              *
//      *                                                                *
//      ******************************************************************


#ifndef Constants_h
#define Constants_h

#include <Arduino.h>

//
// IO pin definitions
//
const int LED_PIN = 26;
const int TEST_PIN = 22;

const int ENTRANCE_PIN = 6;
const int FEED_1_PIN = 7;
const int FEED_2_PIN = 8;
const int EXIT_PIN = 9;
const int ARROW_PIN = 10;


const int RS486_ADDRESS_0_PIN = 27;
const int RS486_ADDRESS_1_PIN = 28;
const int RS486_TX_PIN = 16;
const int RS486_RX_PIN = 17;
const int RS485_TX_ENABLE_PIN = 18;

const int DEBUG_TX_PIN = 20;
const int DEBUG_RX_PIN = 21;

//
// other constants
//
const int NUMBER_OF_SENSORS = 4;

#endif
