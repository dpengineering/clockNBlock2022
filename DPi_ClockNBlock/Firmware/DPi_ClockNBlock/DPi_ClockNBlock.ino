//      ******************************************************************
//      *                                                                *
//      *                       DPi - ClockNBlock                        *
//      *                                                                *
//      *            Arnav Wadhwa                  11/25/2022            *
//      *                                                                *
//      ******************************************************************

#include <Arduino.h>
#include "Constants.h"
#include "RS485Slave.h"
#include "CmdProcessor.h"

//
// variables global to this file
//
int boardNumber;


// ---------------------------------------------------------------------------------
//                              Hardware and software setup
// ---------------------------------------------------------------------------------

//
// top level setup function
//
void setup()
{
    debug_Initialize();
    debug("Starting...");

    //
    // initialize the all the inputs
    //
    pinMode(ENTRANCE_PIN, INPUT);
    pinMode(FEED_1_PIN, INPUT);
    pinMode(FEED_2_PIN, INPUT);
    pinMode(EXIT_PIN, INPUT);
 
    pinMode(ARROW_PIN, OUTPUT);
    digitalWrite(ARROW_PIN, LOW);

    //
    // determine the board number (as configured by jumps) for this board (0 - 3)
    //
    pinMode(RS486_ADDRESS_0_PIN, INPUT_PULLDOWN);
    pinMode(RS486_ADDRESS_1_PIN, INPUT_PULLDOWN);
    boardNumber = 0;
    if (digitalRead(RS486_ADDRESS_0_PIN)) boardNumber += 1;
    if (digitalRead(RS486_ADDRESS_1_PIN)) boardNumber += 2;

    //
    // initialize other IO lines
    //
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    pinMode(TEST_PIN, OUTPUT);

    //
    // initialize the software modules
    //
    cmdProcessor_Initialize(boardNumber);
    heartbeatLED_Initialize();
}


// ---------------------------------------------------------------------------------
//                      The Main Loop and Top Level Functions
// ---------------------------------------------------------------------------------


//
// main loop - execute commands from the Master
//
void loop()
{
    while(true)
    {
        //
        // check for and process commands from the Master
        //
        cmdProcessor_Execute();

        //
        // update the "heartbeat" LED
        //
        heartbeatLED_Update();
    }
}



// ---------------------------------------------------------------------------------
//                      Functions for the Heart Beat LED
// ---------------------------------------------------------------------------------

static int heartbeatState;
static int fastHeartbeatCount;
static unsigned long heartbeatStartTime;

//
// initialize the heart beat LED
//
void heartbeatLED_Initialize(void)
{
    heartbeatState = 0;
    fastHeartbeatCount = 0;
    heartbeatStartTime = millis();
}



//
// update the heartbeat
//
void heartbeatLED_Update(void)
{
    switch(heartbeatState)
    {
        case 0:
            if ((millis() - heartbeatStartTime) < 200) return;
            digitalWrite(LED_PIN, LOW);
            heartbeatStartTime = millis();
            heartbeatState = 1;
            return;
        case 1:
            if ((millis() - heartbeatStartTime) < 200) return;
            digitalWrite(LED_PIN, HIGH);
            heartbeatStartTime = millis();
            heartbeatState = 2;
            return;
        case 2:
            if ((millis() - heartbeatStartTime) < 200) return;
            digitalWrite(LED_PIN, LOW);
            heartbeatStartTime = millis();
            heartbeatState = 3;
            return;
        case 3:
            if ((millis() - heartbeatStartTime) < 430) return;
            digitalWrite(LED_PIN, HIGH);
            heartbeatStartTime = millis();
            heartbeatState = 0;
            return;

        case 10:
            if ((millis() - heartbeatStartTime) < 40) return;
            digitalWrite(LED_PIN, HIGH);
            heartbeatStartTime = millis();
            heartbeatState = 11;
            return;
        case 11:
            if ((millis() - heartbeatStartTime) < 40) return;
            digitalWrite(LED_PIN, LOW);
            heartbeatStartTime = millis();
            fastHeartbeatCount--;
            if (fastHeartbeatCount > 0)
                heartbeatState = 10;
            else
                heartbeatState = 3;
            return;
        default:
            heartbeatState = 0;
    }
}



//
// start the heart beating fast for a few cycles
//
void heartBeatLED_Fast(void)
{
    if (heartbeatState < 10)
        heartbeatState = 11;
    fastHeartbeatCount = 7;
}


// ---------------------------------------------------------------------------------
//                      Functions for debugging with serial
// ---------------------------------------------------------------------------------

//
// initialize debugging using print statements
//
void debug_Initialize(void)
{
    Serial2.setRX(DEBUG_RX_PIN);
    Serial2.setTX(DEBUG_TX_PIN);
    Serial2.begin(115200);
}



//
// debug using print statements
//
void debug(const char *s)
{
    Serial2.println(s);
}

void debug(const char *s, int i)
{
    Serial2.print(s);
    Serial2.print(": ");
    Serial2.println(i);
}

void debug(const char *s, float f)
{
    Serial2.print(s);
    Serial2.print(": ");
    Serial2.println(f);
}

// -------------------------------------- End --------------------------------------
