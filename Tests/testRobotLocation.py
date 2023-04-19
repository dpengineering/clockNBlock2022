from Objects.robotArm import RobotArm
from dpeaDPi.DPiSolenoid import DPiSolenoid
import Objects.constants as constants
from Objects.clock import Clock

# Constants for setup
dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

robotArm = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid)
speed = 100

clock = Clock()




def main():
    robotArm.setup()
    clock.setup()
    positionPolar = (100.6, 90, -1300)
    print(f'moving to {positionPolar}')
    print(f'converted to {constants.polarToCartesian(positionPolar)}')
    robotArm.movePolar(positionPolar, speed)
    print(f'clockPos {clock.getPositionDegrees()[0]}')
    print(f'Actual Pos in steps {clock.dpiStepper.getCurrentPositionInSteps(0)}')
    clock.moveToPositionDegrees(hourDegrees=positionPolar[1])
    print(f'Moving {positionPolar[1]} degrees')
    print(f'clockPos {clock.getPositionDegrees()[0]}')
    print(f'Actual Pos in steps {clock.dpiStepper.getCurrentPositionInSteps(0)}')

    # clock.dpiStepper.moveToRelativePositionInSteps(0, 1000, True)
    # print(f'Moving 1000 steps')
    # print(f'clockPos {clock.getPositionDegrees()[0]}')
    # print(f'Actual Pos in steps {clock.dpiStepper.getCurrentPositionInSteps(0)}')

if __name__ == '__main__':
    main()
