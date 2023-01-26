#      ******************************************************************
#      *                                                                *
#      *   This program use the DPiStepper Board to test RS-485 Cables  *
#      *                                                                *
#      *            Stan Reifel                     8/21/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiStepper import DPiStepper
from time import sleep


def main():
    #
    # create the DPiStepper object, one object should be created for each DPiStepper
    # board that you are using.
    #
    dpiStepper = DPiStepper()
    dpiStepper.setBoardNumber(0)
    if dpiStepper.initialize() != True:
        print("Communication with the DPiStepper board failed.")
        return


    #
    # Enable the stepper motors and use 8x microstepping
    #
    dpiStepper.enableMotors(True)
    microstepping = 8
    dpiStepper.setMicrostepping(microstepping)


    #
    # Set the motor speed
    #
    speed_steps_per_second = 200 * microstepping
    accel_steps_per_second_per_second = speed_steps_per_second
    dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, accel_steps_per_second_per_second)

    #
    # loop 10 times, turning the motor 3 revolutions each time
    #
    for i in range(10):
        #
        # rotate the step 3 turns
        #
        stepper_num = 0
        steps_per_rotation = 1600
        wait_to_finish_moving_flg = False
        results = dpiStepper.moveToRelativePositionInSteps(stepper_num,  3 * steps_per_rotation, wait_to_finish_moving_flg)
        if (results != True):
            print("moveToRelativePositionInSteps() failed")
            continue

        #
        # now wait for motor to stop
        #
        while dpiStepper.getAllMotorsStopped() == False:
            results = dpiStepper.getCurrentPositionInSteps(stepper_num)
            if results[0] != True:
                print("getCurrentPositionInSteps() failed")
            sleep(0.01)

        print("Completed test: " + str(i))


#
# run the example script
#
if __name__ == "__main__":
    main()

