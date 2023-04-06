import numpy as np


def cartesianToPolar(position: tuple):
    """Helper function to change cartesian coordinates to polar
    Args:
        position (tuple): Current robot position in cartesian plane
    Returns:
        r, theta, z (tuple (float)): Returns the polar coordinates that correspond to the cartesian coordinates
    """
    x, y, z = position
    # Convert to Polar Coords
    r = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(y, x)
    print(theta)
    theta = np.rad2deg(theta)
    print(theta)

    # Adjust for negative values
    if x < 0 < y:
        theta += 180
    elif x < 0 and y < 0:
        theta += 360
    elif y < 0 < x:
        theta += 360

    return r, theta, z


if __name__ == '__main__':
    position = (-50, -100, 100)
    print(position)
    print(cartesianToPolar(position))

