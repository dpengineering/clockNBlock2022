//      ******************************************************************
//      *                                                                *
//      *              Header file for CmdProcessor.c                *
//      *                                                                *
//      *              Copyright (c) S. Reifel & Co, 2022                *
//      *                                                                *
//      ******************************************************************

#ifndef CmdProcessor_h
#define CmdProcessor_h

#include <Arduino.h>

//
// function declarations
//
void cmdProcessor_Initialize(int boardNum);
void cmdProcessor_Execute(void);


// ------------------------------------ End ---------------------------------
#endif
