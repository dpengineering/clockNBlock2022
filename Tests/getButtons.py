import pygame
import os

os.environ['SDL_VIDEODRIVER'] = "dummy"

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)


def main():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.JOYBUTTONDOWN:
            print(event)


if __name__ == "__main":
    main()
