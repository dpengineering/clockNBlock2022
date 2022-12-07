//      ******************************************************************
//      *                                                                *
//      *                 Header file for RS485Slave.cpp                 *
//      *                                                                *
//      *              Copyright (c) S. Reifel & Co, 2022                *
//      *                                                                *
//      ******************************************************************


#ifndef RS485Slave_h
#define RS485Slave_h


void RS485Initialize(int slaveAddr, int TXPin, int RXPin, int txEnablePin);
boolean RS485GetCommand(int &receivedCommand, int &receivedDataSize);
uint8_t RS485PopUint8(void);
uint8_t RS485PopInt8(void);
uint16_t RS485PopUint16(void);
int16_t RS485PopInt16(void);
uint32_t RS485PopUint32(void);
int32_t RS485PopInt32(void);
void RS485PushUint8(uint8_t value);
void RS485PushInt8(int8_t value);
void RS485PushUint16(uint16_t value);
void RS485PushInt16(int16_t value);
void RS485PushUint32(uint32_t value);
void RS485PushInt32(int32_t value);
void RS485AcknowledgeCommand(void);


// ------------------------------------ End ---------------------------------
#endif
