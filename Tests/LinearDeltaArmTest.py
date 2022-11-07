#      ******************************************************************
#      *                                                                *
#      *      This program tests the ClockNBlock Linear Delta Arm       *
#      *                                                                *
#      *            Arnav Wadhwa                     11/7/2022          *
#      *                                                                *
#      ******************************************************************


from dpeaDPi.DPiRobot import DPiRobot
from time import sleep
import math

#Constants

LinearRobotBoardNumber = 0                # Sets the board number for the delta arm


def main():

    # Create Delta Arm Object
    dpiRobot = DPiRobot()


    # Sets the board number for the delta arm
    dpiRobot.setBoardNumber(LinearRobotBoardNumber)

    #Initalize the robot to the default values
    if dpiRobot.initialize() != True:
        print("Communication with the DPiRobot board failed.")
        return


    #
    # When the robot is first turned on, it doesn't know where it is.  The robot determines
    # where it is by "Homing".  Homing is the process of slowly moving each actuator until
    # it makes contact with its homing sensor.
    #

    #
    # Move the robot to its home position.  The robot will first enable its motors, then
    # start moving up toward "Home".  Setting "alwaysHomeFlg = True" will cause the robot
    # to always run the homing procedure, even if it already knows where it is.
    #
    sleep(1)
    alwaysHomeFlg = True
    if dpiRobot.homeRobot(alwaysHomeFlg) != True:
        print("Homing failed.")
        return

    #
    # At all times the robot has a "Status" value that you can get by calling getRobotStatus().
    # Two values are return and assigned to the variables "success_flg" and "status".
    # "success_flg" will be "True" if the command executed successfully or "False" if it
    # failed while trying to get the status.  "status" can have many values depending on what
    # the robot is doing.
    #
    _success_flg, status = dpiRobot.getRobotStatus()

    if status == dpiRobot.STATE_NOT_READY:
        print("Status: Robot is not ready.")
    elif status == dpiRobot.STATE_MOTORS_DISABLED:
        print("Status: Motors are disabled.")
    elif status == dpiRobot.STATE_NOT_HOMED:
        print("Status: Motors enabled but robot not homed.")
    elif status == dpiRobot.STATE_HOMING:
        print("Status: Robot is running the homing procedure.")
    elif status == dpiRobot.STATE_STOPPED:
        print("Status: Robot is stopped.")
    elif status == dpiRobot.STATE_PREPARING_TO_MOVE:
        print("Status: Robot received 1 or more waypoints but hasn't started moving.")
    elif status == dpiRobot.STATE_MOVING:
        print("Status: Robot is moving.")
    else:
        print("Unknown status.")


    # Ask the robot where it is in Robot Coordinates (the Z will be a wacky negative number)

    _success_flg, X, Y, Z = dpiRobot.getCurrentPosition_RobotCoords()
    print(f"Robot's position in 'Robot Coordinates':  X:{X}, Y:{Y}, Z:{Z}")

    # Ask where the robot is in User Coordinates
    _success_flg, X, Y, Z = dpiRobot.getCurrentPosition()
    print(f"Robot's position in 'User Coordinates':  X:{X}, Y:{Y}, Z:{Z}")


    # Comment this out when you would like to make the robot move
    # return

    # All units are in mm/sec
    speed = 35.0
    acceleration = 35.0

    # Move to 0, 0, -1300 (Ask Stan about user coords to robot coords)

    X = 0.0
    Y = 0.0
    Z = 100
    _success_flg = dpiRobot.addWaypoint(X, Y, Z, speed)
    dpiRobot.waitWhileRobotIsMoving()
    print("Move to (0, 0, 100) complete")

    # Move in Square
    sleep(2)
    speed = 100.0
    dpiRobot.addWaypoint(250, 250, Z, speed)
    dpiRobot.addWaypoint(-250, 250, Z, speed)
    dpiRobot.addWaypoint(-250, -250, Z, speed)
    dpiRobot.addWaypoint(250, -250, Z, speed)
    dpiRobot.addWaypoint(250, 250, Z, speed)
    dpiRobot.waitWhileRobotIsMoving()
    print("Move to in a square complete")


    # Move in circle
    sleep(2)
    Z = 100
    radius = 200.0
    speed = 200

    dpiRobot.addWaypoint(radius, 0, Z, speed)
    dpiRobot.waitWhileRobotIsMoving()
    sleep(1)

    degreesToRadians = 3.14159 / 180.0
    dpiRobot.bufferWaypointsBeforeStartingToMove(True)
    for robotTheta in range(0, 360, 2):
        X = radius * math.cos(robotTheta * degreesToRadians)
        Y = radius * math.sin(robotTheta * degreesToRadians)
        dpiRobot.addWaypoint(X, Y, Z, speed)
    dpiRobot.bufferWaypointsBeforeStartingToMove(False)
    print("Move to in a circle complete")

    # # Move back to origin
    # sleep(2)
    # speed = 75
    # dpiRobot.addWaypoint(0, 0, 0, speed)
    # dpiRobot.waitWhileRobotIsMoving()
    # print("All done")

# Run script
if __name__ == "__main__":
    main()


