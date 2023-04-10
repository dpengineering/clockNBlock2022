from main.buildSite import BuildSite
import main.constants as constants
import numpy as np
from sympy import Point3D, Polygon, Plane

# Tests functions in buildSite.py
# to be run with debugger to see how the functions work and store data


def main():
    blockPlacementArr = constants.placementArrays[0]
    location = constants.buildLocations[0][0]
    location1 = constants.buildLocations[0][1]
    BuildSite0 = BuildSite(0, location, location1)

    # Setup buildSite
    BuildSite0.setup()
    print(f'block Placements: {BuildSite0.blockPlacements}')
    print(f'current block: {BuildSite0.currentBlock}')
    print(f'intersection plane: {BuildSite0.intersectionPlane}')


if __name__ == '__main__':
    main()


