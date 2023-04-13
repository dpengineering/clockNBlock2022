from Objects.robotArm import RobotArm
from dpeaDPi.DPiSolenoid import DPiSolenoid
import Objects.constants as constants


# Constants for setup
dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

robotArm = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid)
speed = 100


def main():
    # robotArm.setup()
    positionPolar = (325.59941646139356, 307.96449858774173, -1416.5)
    print(f'moving to {positionPolar}')
    print(f'converted to {robotArm.polarToCartesian(positionPolar)}')
    robotArm.movePolar(positionPolar, speed)


if __name__ == '__main__':
    main()
