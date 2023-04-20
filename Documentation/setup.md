# Setup

This project has 3 main components: the robot arm, the cloc, and the feeders.  
  
### Robot Arm
The robot arm has the most moving parts and has the most setup required for it.  
The robot is a delta arm which is controlled by the [DPi_Robot](https://github.com/dpengineering/DPi_Robot) board.  
  
The first thing that needs to be set up are the constants held in the robot board itself.  
To do this, connect your computer to the raspberry pi and run a program such as the LinearDeltaRobotSetup.py. Our constants are all held
in that file and on the DPi_Robot board itself through its menus. Use the touchscreen on the board to access those.  
Also, go through and test each motor, limit switch, homing method, driver type, and the dip switches on the motor drivers.  
Dip switches set current limits and microstepping. Switches **a, b, c, d** should be down

    
Next, important points need to be set up on the robot arm. These points are the home position, the position where the arm is ready to pick up a block, and the position where the arm is ready to place a block.  
The home is already set as it is just where the robot goes to hit the limit switches. And the coordinate system we use is the Robot Coordinates. 
The robot can speak in 2 different coordinate systems: Robot Coordinates and Human Coordinates. 
Robot coordinates are the coordinates that the robot actually uses to move places. The Human Coordinates can be configured 
to have (0, 0, 0) to be wherever you want it to be. Currently, the Human Coordinates are the exact same as the robot coordinates.  
  
Next you will have to train all the points. There is a program, trainRobotJoystick.py that will allow you to use one of the DPEA's joysticks
Then, drive the robot around to the pick-up locations and verify that the robot can actually pick up the block and save that location. 
Next, drive the robot to the place locations (the spot where the robot will place the block that is closest to the center of the machine) verify that the hour hand cannot hit the 
arm or the block when the robot is in that position. Rember that the robot head has a width and can hit the hour hand. In this case, the robot will not lose steps but the hour hand will.  
The button controls are outlined in the check_other_buttons() method in the trainRobotJoystick.py file.   

Finally verify which solenoid controlls the magnet and which one controls the rotation.

### Clock
The clock doesn't require too much setup. The only thing that needs to be setup is the 12:00 position.  
To do this, home the clock which will have the hands at some random position, then drive the clock hands to the 12:00 position (wherever you choose that to be preferably over one of the build locations).  
  
The minute hand has about a 204:1 gear reduction. This is not exact so find how many steps are needed for one full rotation  
The hour hand has a 5:1 gear reduction. This should be exact, but is a good idea to verify that.

### Feeders

The feeders are a pain.  
To start, find which solenoid corresponds to the piston that pushes to the side or up for each feeder.  
Hopefully this has not changed. Then, check how fast each piston pushes the block.  
For the side pistons, this should be fairly fast, but not too fast as the piston will just destroy itself.  
The up pistons should be as fast as possible such that the block does not 'jump' when it stops at the top. The block should not leave the 
detection of the sensor at the top.  
Next, calibrate each sensor with the potentiometer screw at the bottom of the sensor. Place a block in a place where the sensor should trigger,
then make sure the sensor is triggered, the light at the bottom should show that. And make sure the sensor is not too sensitive to where it gives false positives.  
You will need to pull each feeder out to adjust some of the sensors. This is outlined in the Hardware portion of the docs.