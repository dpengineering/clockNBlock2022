//      ******************************************************************
//      *                                                                *
//      *              RS485 Slave (without using interrupts)            *
//      *                                                                *
//      *            Stan Reifel                     7/17/2022           *
//      *                                                                *
//      ******************************************************************

#include <Arduino.h>
#include "RS485Slave.h"

//
// Protocol for RS485 serial communication between the Master and a Slave module:
//
// Commands are sent from the Master to a Slave.  The slave on the RS485 network is
// identified by the Slave's address.  Each Slave must have a unique 6 bit SlaveAddress.
//
// Commands from the Master include a CommandByte and up to 15 bytes of additional
// data.  The Slave must acknowledge that it received the Master's command and that
// the data it received is intact.  The Master can send commands to have the Slave
// do things, or it can send commands requesting data from the Slave.
//
// When the Slave receives a command from the Master, it must acknowledge the command.
// This acknowledgement is used to let the Master know the command was received
// successfully.  When the Master sends a command requesting data from the Slave, the
// Slave sends the data by adding it to the acknowledgement (which can include up
// to 15 bytes of data from the Slave).
//
// After the Master sends a command, it waits for an acknowledgement from the Slave.
// If the Master doesn't receive the acknowledgement within a few milliseconds, it
// resends the command (up to n times).  If the Slave receives a command with corrupted
// data, the Slave simply ignores the command by not executing it or sending any
// acknowledgement (causing the Master to resend).
//
// All data transfers are initiated by the Master.  The Slave can not asynchronously
// transmit data that wasn't requested by a command from the Master.
//
// Byte format of command packets sent from the Master to Slave:
//   * HeaderByte: Always 0xaa
//   * SlaveAddress: 6 bits, note bit 7 must be 1, bit 6 must be 0.
//   * CommandByte
//   * DataCount: Count of bytes in the DataField (0 - 15):
//      - The value's low nibble = DataCount
//      - The value's high nibble = (~DataCount) << 4   (one's complment of the DataCount)
//   * DataField: Between 0 and 15 bytes of additional data sent by the Master
//   * Checksum: The 8 bit sum of all bytes in the packet including the HeaderByte,
//              DataCount value, SlaveAddress value, CommandByte, and all bytes in
//              the DataField.
//
// There are two packet formats the Slave uses when acknowledging the Master's commands.
// If the Master isn't requesting data from the Slave, the acknowledgement format is:
//   * HeaderByte: 0x77
//   * Checksum: (will always be 0x77)
// If the Master is requesting data from the Slave, the format is:
//   * HeaderByte: 0x78
//   * DataCount: Count of bytes in the DataField (1 - 15):
//      - The value's low nibble = DataCount
//      - The value's high nibble = (~DataCount) << 4   (one's complment of the DataCount)
//  * DataField: Between 1 and 15 bytes of data sent from the Slave
//  * Checksum: The 8 bit sum of all bytes in the acknowledgement packet including the
//              HeaderByte, DataCount value, and all bytes in the DataField.
//


//
// Master/Slave communication constants
//
const int RS485_BAUDRATE = 115200;
const int RS485_RETRY_ATTEMPTS = 3;
const uint8_t COMMAND_PACKET_HEADER = 0xaa;
const uint8_t ACKNOWLEDGEMENT_PACKET_HEADER_WITH_NO_DATA = 0x77;
const uint8_t ACKNOWLEDGEMENT_PACKET_HEADER_WITH_DATA = 0x78;

//
// state values for: getCommandState
//
static int getCommandState = 0;
const int GET_COMMAND_STATE__WAITING_FOR_HEADER = 0;
const int GET_COMMAND_STATE__WAITING_FOR_ADDRESS = 1;
const int GET_COMMAND_STATE__WAITING_FOR_COMMAND = 2;
const int GET_COMMAND_STATE__WAITING_FOR_DATA_SIZE = 3;
const int GET_COMMAND_STATE__WAITING_FOR_DATA = 4;
const int GET_COMMAND_STATE__WAITING_FOR_CHECKSUM = 5;

//
// vars global to this module
//
static int slaveAddress = 0;
static int TXEnablePin;
static int TXEnableDelayUS = (1000000 * 2) / RS485_BAUDRATE;   // delay 2 serial bits
static uint8_t dataReceiveBuffer[16];
static int dataReceiveIndex;
static uint8_t dataTransmitBuffer[16];
static int dataTransmitIndex;

//
// external functions
//
extern void debug(const char *s);
extern void debug(const char *s, int i);


// ---------------------------------------------------------------------------------
//                                 Public functions
// ---------------------------------------------------------------------------------


//
// initialize the RS485 serial communication
//    Enter:  slaveAddr = the address of this slave (0 - 0x3f)
//            TXPin = pin number used to transmit the RS485 signal
//            RXPin = pin number used to receive the RS485 signal
//            txEnablePin = pin number used to enable slave's RS485 TX signal
//
void RS485Initialize(int slaveAddr, int TXPin, int RXPin, int txEnablePin)
{
    slaveAddress = slaveAddr;
    TXEnablePin = txEnablePin;
    Serial1.setRX(RXPin);
    Serial1.setTX(TXPin);
    Serial1.begin(RS485_BAUDRATE);
    getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
}



//
// get a command from the master via a RS485 network, note this function doesn't send the acknowledgement
//    Enter:  receivedCommand -> storage to return the command byte
//            receivedDataSize -> storage to return number of data bytes receive from master (0 - 15)
//    Exit:   true returned if a command was received, else false
//            command's additional data retrieved using "Pop"commands
//
boolean RS485GetCommand(int &receivedCommand, int &receivedDataSize)
{
    static uint8_t checksum;
    static int addressReceived;
    static int commandReceived;
    static int dataSizeReceived;
    static int dataCountSoFar;

    //
    // loop to read all the characters currently available from the master
    //
    while(Serial1.available() > 0)
    {
        uint8_t c = Serial1.read();
        switch(getCommandState)
        {
            case GET_COMMAND_STATE__WAITING_FOR_HEADER:
            {
                //
                // get the packet header, ignore if not correct
                //
                checksum = c;
                if (c == COMMAND_PACKET_HEADER)
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_ADDRESS;
                break;
            }


            case GET_COMMAND_STATE__WAITING_FOR_ADDRESS:
            {
                //
                // get the slave address, ignore packet if not formatted properly
                //
                checksum += c;
                addressReceived = c & 0x3f;
                if ((c & 0xc0) != 0x80)
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
                else
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_COMMAND;
                break;
            }


            case GET_COMMAND_STATE__WAITING_FOR_COMMAND:
            {
                //
                // get the command byte
                //
                checksum += c;
                commandReceived = c;
                getCommandState = GET_COMMAND_STATE__WAITING_FOR_DATA_SIZE;
                break;
            }


            case GET_COMMAND_STATE__WAITING_FOR_DATA_SIZE:
            {
                //
                // get the data count, ignore packet if not formatted properly
                //
                checksum += c;
                dataSizeReceived = c & 0x0f;
                if (dataSizeReceived != (((~c) >> 4) & 0x0f))
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
                else if (dataSizeReceived == 0)
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_CHECKSUM;
                else
                {
                    dataCountSoFar = 0;
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_DATA;
                }
                break;
            }


            case GET_COMMAND_STATE__WAITING_FOR_DATA:
            {
                //
                // get a byte of data, check if it's the last byte expected
                //
                checksum += c;
                dataReceiveBuffer[dataCountSoFar] = c;
                dataCountSoFar++;

                if (dataCountSoFar >= dataSizeReceived)
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_CHECKSUM;
                break;
            }


            case GET_COMMAND_STATE__WAITING_FOR_CHECKSUM:
            {
                //
                // if the checksum is correct and the packet is addressed to this slave, then
                // pass the command and data back to the calling function
                //
                if ((checksum == c) && (addressReceived == slaveAddress))
                {
                    //
                    // copy the command and data back to calling function
                    //
                    receivedCommand = commandReceived;
                    receivedDataSize = dataSizeReceived;
                    dataReceiveIndex = 0;
                    dataTransmitIndex = 0;
                    getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
                    return(true);
                }

                getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
                break;
            }
        }
    }

    //
    // no data available, return false indicating that a complete packet has not been received
    //
    return(false);
}



//
// get data from the receive buffer
//
uint8_t RS485PopUint8(void)
{
    uint8_t value = dataReceiveBuffer[dataReceiveIndex];
    dataReceiveIndex++;
    return(value);
}

uint8_t RS485PopInt8(void)
{
    int8_t value = dataReceiveBuffer[dataReceiveIndex];
    dataReceiveIndex++;
    return(value);
}

uint16_t RS485PopUint16(void)
{
    uint16_t value = (uint16_t) ((dataReceiveBuffer[dataReceiveIndex] << 8) + dataReceiveBuffer[dataReceiveIndex + 1]);
    dataReceiveIndex += 2;
    return(value);
}

int16_t RS485PopInt16(void)
{
    int16_t value = (int16_t) ((dataReceiveBuffer[dataReceiveIndex] << 8) + dataReceiveBuffer[dataReceiveIndex + 1]);
    dataReceiveIndex += 2;
    return(value);
}

uint32_t RS485PopUint32(void)
{
    uint32_t value = (uint32_t) (
            (dataReceiveBuffer[dataReceiveIndex] << 24) +
            (dataReceiveBuffer[dataReceiveIndex+1] << 16) +
            (dataReceiveBuffer[dataReceiveIndex+2] << 8) +
            (dataReceiveBuffer[dataReceiveIndex+3]));
    dataReceiveIndex += 4;
    return(value);
}

int32_t RS485PopInt32(void)
{
    int32_t value = (int32_t) (
            (dataReceiveBuffer[dataReceiveIndex] << 24) +
            (dataReceiveBuffer[dataReceiveIndex+1] << 16) +
            (dataReceiveBuffer[dataReceiveIndex+2] << 8) +
            (dataReceiveBuffer[dataReceiveIndex+3]));
    dataReceiveIndex += 4;
    return(value);
}



//
// push data to the transmit buffer
//
void RS485PushUint8(uint8_t value)
{
    dataTransmitBuffer[dataTransmitIndex] = (uint8_t) value;
    dataTransmitIndex++;
}

void RS485PushInt8(int8_t value)
{
    dataTransmitBuffer[dataTransmitIndex] = (uint8_t) value;
    dataTransmitIndex++;
}

void RS485PushUint16(uint16_t value)
{
    uint8_t* dataPntr = (uint8_t*) &value;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[1];    // high byte;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[0];    // low byte;
}

void RS485PushInt16(int16_t value)
{
    uint8_t* dataPntr = (uint8_t*) &value;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[1];    // high byte;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[0];    // low byte;
}

void RS485PushUint32(uint32_t value)
{
    uint8_t* dataPntr = (uint8_t*) &value;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[3];    // high byte;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[2];
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[1];
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[0];    // low byte
}

void RS485PushInt32(int32_t value)
{
    uint8_t* dataPntr = (uint8_t*) &value;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[3];    // high byte;
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[2];
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[1];
    dataTransmitBuffer[dataTransmitIndex++] = dataPntr[0];    // low byte
}



//
// acknowledge the command, sending data to the master  Note: if there is additional data to
// sent to the Master, it must have been "Pushed" before calling
//
void RS485AcknowledgeCommand(void)
{
    volatile int j;
    uint8_t checksum = 0;

    //
    // enable the serial TX line for this slave
    //
    digitalWrite(TXEnablePin, HIGH);

    //delayMicroseconds(TXEnableDelayUS);   // REMOVED CALL TO delayMicroseconds() BECAUSE SOMETIMES IT WOULDN'T RETURN FOR A LONG TIME ???????
    for(int i = 0; i < 100; i++)            // delay replaced with a loop
        j = i * i;

    //
    // check if this packet has no additional data
    //
    if (dataTransmitIndex == 0)
    {
        Serial1.write(ACKNOWLEDGEMENT_PACKET_HEADER_WITH_NO_DATA);
        checksum += ACKNOWLEDGEMENT_PACKET_HEADER_WITH_NO_DATA;
    }

    //
    // check if this packet includes additional data
    //
    if (dataTransmitIndex > 0)
    {
        //
        // send the header byte indicating there is data
        //
        Serial1.write(ACKNOWLEDGEMENT_PACKET_HEADER_WITH_DATA);
        checksum += ACKNOWLEDGEMENT_PACKET_HEADER_WITH_DATA;

        //
        // send encoded version of number of data bytes
        //
        int sendDataSize = dataTransmitIndex;
        uint8_t sendDataCountValue = (sendDataSize & 0x0f) + (((~sendDataSize) & 0x0f) << 4);
        Serial1.write(sendDataCountValue);
        checksum += sendDataCountValue;

        //
        // send the data bytes
        //
        for(int i = 0; i < sendDataSize; i++)            // send the optional data
        {
            uint8_t c = dataTransmitBuffer[i];
            Serial1.write(c);
            checksum += c;
        }
    }

    //
    // send the checksum
    //
    Serial1.write(checksum);

    //
    // wait for the transmission to complete, then disable the TX line
    //
    Serial1.flush();

    //delayMicroseconds(TXEnableDelayUS);   // REMOVED CALL TO delayMicroseconds() BECAUSE SOMETIMES IT WOULDN'T RETURN FOR A LONG TIME ???????
    for(int i = 0; i < 100; i++)            // delay replaced with a loop
        j = i * i;

    digitalWrite(TXEnablePin, LOW);
}

// -------------------------------------- End --------------------------------------
