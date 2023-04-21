# Setting Constants and Variables in DPi Robot board


## Constants
The constants that need to be set are listed in oneTimeSetup/LinearDeltaRobotSetup.py  
The constants are:  
robotType =  
maxX =   
minX =   
maxY =   
minY =   
maxZ =   
minZ =   
defaultAccel =   
defaultJunctDeviation =   
homingSpeed =   
maxHomingDistance =   
homingMethod =   
stepsPerMM =   
armLength =   
towerRadius =   
endEffectorRadius =   
maxArmPos =   
motorDriverType =   
microStepping =   
reverseStepDirectionFlag =  

## Deriving Constants
armLength, towerRadius, endEffectorRadius should be available in the CAD file.  

stepsPerMM is the number of steps per mm of travel. To calculate this, multiply the belt pitch by the number of teeth in the gear connected to the stepper
to get the mm per revolution. Then, divide the number of steps per revolution by the mm per revolution.

microStepping is the number of microsteps per step. This is set by the dip switches on the motor driver if using the DM542T.  

defaultAccel should be around 6000 - 7000, this number can be played around with.

defaultJunctDeviation should be around 32, this number can be played around with.

The rest of the constants should be determined experimentally.

## Configuring the motor drivers.
Configuring the motor drivers is done through the dip switches on the side of the driver.  

Set the current limit to a reasonable number where the peak current is less than the rated current on the stepper.

Microstepping can be set to whatever you want. I recommend 32. 

The switch on the top of the driver should also be set to 5V not 24V. This corresponds to the strength of the signal sent for the step and direction.