# Software

The software has been written in an object-oriented style because I am a Java guy
and this is how I code. Feel free to change this though.  

## Finite State Machine
All the components have what are called state-machines. This eliminates the need for small loops and allows
for constant checking of each object. Every state in the state machine has three components:  

#### Do something  
This happens on the first time the state is called and is the main portion of the state.  
After this state is hit, a newState flag is set to false and the rest of the times this state is reached
it will

#### Wait for something
This is pretty self-explanatory. It waits for a set amount of time or until some condition is reached.

#### Set a new state
The state machine moves onto a different state and the newState flag is reset to True because 
we are in a new state.

There are four main objects that talk to each other.

## Robot Arm
Controls the robot arm and holds the state machine for the robot.
Also has helper methods as a layer of abstraction above the DPi_Robot

## Robot Manager
The robot manager isn't actually a physical part, it is just there to tell the robot what it should be doing.  
This is the most complicated part of the project and is the overarching controller of the robot.

## Clock
This isn't really a clock, just a thing that points to where the next block is going and knocks blocks over

## Block Feeder
This holds the state machine for the block feeder, it constantly cycles blocks to the top of the feeder.

## Build Site
Holds all the information to build blocks such as placement, number of blocks, and a representation of the tower for the robot to dodge.

## Constants
All the constants are stored here. I tried to make it so there are no "magic numbers" but some still exist.