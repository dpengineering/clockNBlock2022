//      ******************************************************************
//      *                                                                *
//      *   Command Processor - Execute commands sent from the Master    *
//      *                                                                *
//      *              Copyright (c) S. Reifel & Co, 2022                *
//      *                                                                *
//      ******************************************************************

#include <Arduino.h>
#include "Constants.h"
#include "RS485Slave.h"
#include "CmdProcessor.h"

//
// this board's RS485 base address
//
const int DPi_CLOCKNBLOCK__RS485_BASE_ADDRESS = 0x3C;

//
// RS485 DPi ClockNBlock commands
//
const byte CMD_DPi_CLOCKNBLOCK__PING                  = 0x00;
const byte CMD_DPi_CLOCKNBLOCK__INITIALIZE            = 0x01;
const byte CMD_DPi_CLOCKNBLOCK__READ_ENTRANCE         = 0x02;
const byte CMD_DPi_CLOCKNBLOCK__READ_FEED_1           = 0x03;
const byte CMD_DPi_CLOCKNBLOCK__READ_FEED_2           = 0x04;
const byte CMD_DPi_CLOCKNBLOCK__READ_EXIT             = 0x05;
const byte CMD_DPi_CLOCKNBLOCK__ARROW_ON              = 0x06;
const byte CMD_DPi_CLOCKNBLOCK__ARROW_OFF             = 0x07;

//
// forward function declarations
//
void initializeBoard(void);

//
// external functions declarations
//
extern void heartBeatLED_Fast(void);
extern int getInputPin(int inputNumber);
extern void debug(const char *s);
extern void debug(const char *s, int i);
extern void debug(const char *s, float f);


// ---------------------------------------------------------------------------------

//
// initialize the command processor
//  Enter:  boardNum = the hardware selected board number for this board (0 - 3)
//
void cmdProcessor_Initialize(int boardNum)
{
    //
    // determine the slave address for this board
    //
    int slaveAddress = DPi_CLOCKNBLOCK__RS485_BASE_ADDRESS + boardNum;

    //
    // initialize RS485 communication
    //
    pinMode(RS485_TX_ENABLE_PIN, OUTPUT);
    digitalWrite(RS485_TX_ENABLE_PIN, LOW);
    RS485Initialize(slaveAddress, RS486_TX_PIN, RS486_RX_PIN, RS485_TX_ENABLE_PIN);


    //
    // initialize board to be in the default configuration
    //
    initializeBoard();
}


//
// initialize board to be in the "power on" configuration
//
void initializeBoard(void)
{
    digitalWrite(ARROW_PIN, LOW);
}

//
// check for new commands from the Master and execute them, this function returns
// immediately if no commands are available
//
void cmdProcessor_Execute(void)
{
    int commandFromMaster;
    int dataSizeFromMaster;

    //
    // check if there is a new command from the Master, return if no command available
    //
    if (RS485GetCommand(commandFromMaster, dataSizeFromMaster) != true)
        return;

    //
    // command has been received: determine which command, send Master the RS485
    // acknowledgement, then execute it
    //
    int commandFromMaster_Base = commandFromMaster & 0xfc;
    int commandFromMaster_Arg = commandFromMaster & 0x03;

    if(commandFromMaster == CMD_DPi_CLOCKNBLOCK__PING)
    {
        if (dataSizeFromMaster != 0) return;
        RS485AcknowledgeCommand();
        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__INITIALIZE)
    {
        if (dataSizeFromMaster != 0) return;
        RS485AcknowledgeCommand();
        initializeBoard();
        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__READ_ENTRANCE)
    {
        if (dataSizeFromMaster != 0) return;

//        digitalWrite(LED_PIN, digitalRead(ENTRANCE_PIN));
//        while(true);

        RS485PushUint8(digitalRead(ENTRANCE_PIN));

        RS485AcknowledgeCommand();


        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__READ_FEED_1)
    {
        if (dataSizeFromMaster != 0) return;
        RS485PushUint8(digitalRead(FEED_1_PIN));
        RS485AcknowledgeCommand();
        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__READ_FEED_2)
    {
        if (dataSizeFromMaster = 0) return;
        RS485PushUint8(digitalRead(FEED_2_PIN));
        RS485AcknowledgeCommand();
        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__READ_EXIT)
    {
        if (dataSizeFromMaster != 0) return;
        RS485PushUint8(digitalRead(EXIT_PIN));
        RS485AcknowledgeCommand();
        heartBeatLED_Fast();
        return;
    }

    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__ARROW_ON)
    {
        if (dataSizeFromMaster != 0) return;
        RS485AcknowledgeCommand();
        digitalWrite(ARROW_PIN, HIGH);
        heartBeatLED_Fast();
        return;
    }
    if (commandFromMaster == CMD_DPi_CLOCKNBLOCK__ARROW_OFF)
    {
        if (dataSizeFromMaster != 0) return;
        RS485AcknowledgeCommand();
        digitalWrite(ARROW_PIN, LOW);
        heartBeatLED_Fast();
        return;
    }
}
