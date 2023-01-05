#      ******************************************************************
#      *                                                                *
#      *  One time setup of constants for ClockNBlock Linear Delta Arm  *
#      *                                                                *
#      *    Stan Reifel, Arnav Wadhwa, Brian Vesper     11/4/2022       *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiRobot import DPiRobot

# Constants:
dpiRobot = DPiRobot()
robotType = dpiRobot.ROBOT_TYPE_LINEAR_DELTA
maxX = 610
minX = -610
maxY = 610
minY = -610
maxZ = -1203.8
minZ = -1480.8 # Changed from -1423
defaultAccel = 6400
defaultJunctDeviation = 32
homingSpeed = 50
maxHomingDistance = 610
homingMethod = dpiRobot.HOMING_METHOD_LIMIT_SWITCHES
stepsPerMM = 47.407
armLength = 1273.125
towerRadius = 487.6
endEffectorRadius = 73.33
maxArmPos = 610
motorDriverType = dpiRobot.MOTOR_DRIVER_TYPE_DM542T
microStepping = 32
reverseStepDirectionFlag = True


def main():
    #
    # Up to 4 DPiRobot boards can be connected to a DPiNetwork.  Each board is addressed
    # (0 - 3) by configuring its jumpers.  If no jumpers are installed, the board number
    # is 0.  Note: After changing the jumpers, the board must be power-cycled.
    #
    
    #
    # In this example, we will be using board number 0
    #
    dpiRobot.setBoardNumber(0)

    # Initalize the robot to the default values
    if dpiRobot.initialize() != True:
        print("Communication with the DPiRobot board failed.")
        return

    #Initalize the Delta Arm

    dpiRobot.setRobotType(robotType)
    print(robotType)

    dpiRobot.setRobotMinMaxX(minX, maxX)
    dpiRobot.setRobotMinMaxY(minY, maxY)
    dpiRobot.setRobotMinMaxZ(minZ, maxZ)

    dpiRobot.setRobotDefaultAcceleration(defaultAccel)
    dpiRobot.setRobotDefaultJunctionDeviation(defaultJunctDeviation)

    dpiRobot.setHomingMethod(homingMethod)
    dpiRobot.setHomingSpeed(homingSpeed)
    dpiRobot.setMaxHomingDistanceDegOrMM(maxHomingDistance)

    dpiRobot.linDelta_SetStepsPerMM(stepsPerMM)
    dpiRobot.linDelta_SetArmLength(armLength)

    dpiRobot.linDelta_SetTowerAndEndEffectorRadius(towerRadius, endEffectorRadius)
    dpiRobot.linDelta_SetMaxJointPos(maxArmPos)

    dpiRobot.motorDriver_SetDriverType(motorDriverType)
    print(motorDriverType)
    dpiRobot.motorDriver_SetDriverMicrostepping(microStepping)
    print(microStepping)
    dpiRobot.motorDriver_SetReverseStepDirectionFlag(reverseStepDirectionFlag)


# Run script
if __name__ == "__main__":
    main()
