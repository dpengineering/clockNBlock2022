#
#
# This program runs a sample loop for the block feeders
#
#

from dpeaDPi.DPiComputer import DPiComputer
from dpeaDPi.DPiPowerDrive import DPiPowerDrive
from time import sleep

#Define constants
powerDriveBoard = 1 #PowerDrive Board (there will probably be multiple in the final project) or one solenoid board

# Create dpiComputer and solenoid objects
dpiComputer = DPiComputer()
dpiPowerDrive = DPiPowerDrive()

def main():

    # Initalize the computer
    dpiComputer.initialize()

    #Set PowerDrive board number
    dpiPowerDrive.setBoardNumber(powerDriveBoard)

    #Ensure the Power drive board has been initalized
    if dpiPowerDrive.initialize() != True:
        print("Communication with the DPiPowerDrive board failed.")
        return
    initalize()
    print("All done")


# We will set all of the block feeders to be displaying a block.

#Constants for the sensors
## Task: Rename these variables to actually make sense
display = dpiComputer.IN_CONNECTOR__IN_3
bottom = dpiComputer.IN_CONNECTOR__IN_2
blockExists = dpiComputer.IN_CONNECTOR__IN_1
isFull = dpiComputer.IN_CONNECTOR__IN_0

upPiston = 1
overPiston = 0

def initalize():
    print(dpiComputer.readDigitalIn(display))
    print(dpiComputer.readDigitalIn(bottom))
    print(dpiComputer.readDigitalIn(blockExists))
    if (dpiComputer.readDigitalIn(display) == True):
        print(dpiComputer.readDigitalIn(display))
        return
    if (dpiComputer.readDigitalIn(bottom) == True):
        dpiPowerDrive.switchDriverOnOrOff(upPiston, True)
        print(dpiComputer.readDigitalIn(bottom))
        return
    if (dpiComputer.readDigitalIn(blockExists) == True):
        print(dpiComputer.readDigitalIn(blockExists))
        dpiPowerDrive.switchDriverOnOrOff(overPiston, True)
        while (dpiComputer.readDigitalIn(bottom) != True):
            sleep(0.01)
        dpiPowerDrive.switchDriverOnOrOff(upPiston, True)
    return

def loop():
    # check if sensor 3 is on. If it is, do nothing.

    return
#Run script
if __name__ == "__main__":
    main()