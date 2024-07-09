import pygame as pg
import numpy as np
import sys
import random

#initializing pygame
pg.init()

width, height = 800, 600
screen = pg.display.set_mode((width, height))
pg.display.set_caption("Flapp")

# Clock
clock = pg.time.Clock()
fps = 30

# Game loop
def main():
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((0,0,225))

        #update the display
        pg.display.flip()

        # frame rate
        clock.tick(fps)

    pg.quit()
    sys.exit()

main()
