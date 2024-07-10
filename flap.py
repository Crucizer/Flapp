import pygame as pg
import numpy as np
import sys
import random
import time

#initializing pygame
pg.init()

DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 600
DISPLAY = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pg.display.set_caption("Flapp")

# Clock
clock = pg.time.Clock()
FPS = 60

# COLORS
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
WHITE = (255,255,255)

class Pipe:
    # provide an additonal paramter isTop
    def __init__(self,x):
        self.x = x
        self.width = 75

        self.pipeGap = random.randint(70, 150)
        self.topHeight = random.randint(50, DISPLAY_HEIGHT - self.pipeGap)
        self.bottomHeight = DISPLAY_HEIGHT - self.topHeight;


    def draw(self):
        pg.draw.rect(DISPLAY, WHITE, (self.x, 0, self.width, self.topHeight))
        pg.draw.rect(DISPLAY, WHITE, (self.x, self.topHeight+self.pipeGap, self.width, self.bottomHeight))

    def move(self):
        self.x -= 5;

class Bird:
    def __init__(self):
        self.y= DISPLAY_HEIGHT//2
        self.action = 0
        self.start_time = round((time.time()),2)

    def draw(self):
        pg.draw.circle(DISPLAY, WHITE, (100,self.y), 15)
        self.jump()

    def move(self):
        pass

    def jump(self):
        self.keys = pg.key.get_pressed()
        if self.keys[pg.K_SPACE]:
            self.y -= 8
            self.start_time = time.time()
        else:
            # add gravity
            t = time.time()- self.start_time
            self.y += 1+ 4*t + 0.5*t**2



# Game loop
def main():
    pipes = [Pipe(DISPLAY_WIDTH)]
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        DISPLAY.fill(BLACK)

        # do stuff
        birdie.draw()

        for pipe in pipes:
            pipe.draw()
            pipe.move()
        # remove out of screen pipes
        pipes = [pipe for pipe in pipes if pipe.x > -pipe.width]
        # add pipes
        if pipes[-1].x < DISPLAY_WIDTH - 500:
                    pipes.append(Pipe(DISPLAY_WIDTH))

        # frame rate
        clock.tick(FPS)

        #update the display
        pg.display.flip()

    pg.quit()
    sys.exit()

birdie = Bird()
pipe = Pipe(DISPLAY_WIDTH)
main()
