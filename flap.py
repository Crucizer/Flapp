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
    def __init__(self,x):
        self.x = x
        self.width = 75

        self.pipeGap = random.randint(70, 150)
        self.topHeight = random.randint(50, DISPLAY_HEIGHT - self.pipeGap)
        self.bottomHeight = DISPLAY_HEIGHT - self.topHeight;
        self.bottomY = self.topHeight + self.pipeGap

        self.passed = False


    def draw(self):
        # top pipe
        pg.draw.rect(DISPLAY, WHITE, (self.x, 0, self.width, self.topHeight))
        # bottom pipe
        pg.draw.rect(DISPLAY, WHITE, (self.x, self.bottomY, self.width, self.bottomHeight))

    def move(self):
        self.x -= 5;

class Bird:
    def __init__(self):
        self.x = 100 # fixed
        self.y= DISPLAY_HEIGHT//2
        self.radius = 15
        self.action = 0
        self.color = WHITE
        self.start_time = (time.time())
        self.birdVel = 4

    def draw(self):
        pg.draw.circle(DISPLAY, self.color, (self.x,self.y), self.radius)
        self.jump()

    def move(self):
        pass

    def jump(self):
        self.keys = pg.key.get_pressed()
        if self.keys[pg.K_SPACE]:
            self.y -= self.birdVel*2
            self.start_time = time.time()
        else:
            # add gravity
            t = time.time()- self.start_time
            self.y += 1+ self.birdVel*t + 0.5*t**2

class Collision:
    def __init__(self, Bird, Pipe):
        self.bird = Bird;
        self.pipe = Pipe;

        collided = (self.checkCollison())
        if (collided):
            self.bird.color = RED
            self.bird.collided = True


    def nearest(self):
        # nearest y point
        if self.bird.y > self.pipe.topHeight and self.bird.y < self.pipe.bottomY:
            if(self.bird.y - self.pipe.topHeight > self.pipe.bottomY - self.bird.y):
                nearestY = self.pipe.bottomY
            else:
                nearestY = self.pipe.topHeight
        else:
            nearestY = self.bird.y

        # nearest x point

        if self.bird.x < self.pipe.x:
            nearestX = self.pipe.x
        elif self.bird.x > self.pipe.x + self.pipe.width:
            nearestX = self.pipe.x + self.pipe.width
        else:
            nearestX = self.bird.x

        return (nearestX, nearestY)

    def checkCollison(self):
        pointX, pointY = self.nearest()

        if ((self.bird.x - pointX)**2 + (self.bird.y - pointY)**2)**0.5 < self.bird.radius:
            return True
        else:
            return False

def print_stuff(Font_Size, text, color, x, y):
    font = pg.font.SysFont("Arial", 36)
    text = text
    text_render = font.render(text, 1, color)
    DISPLAY.blit(text_render, (x, y))

# Game loop
def main():
    pipes = [Pipe(DISPLAY_WIDTH)]
    running = True
    score = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        DISPLAY.fill(BLACK)

        for pipe in pipes:
            collided = Collision(birdie, pipe)
            if pipe.x < birdie.x and pipe.passed == False:
                pipe.passed = True
                score +=1
            pipe.draw()
            pipe.move()

        print_stuff(10, str(score), GREEN, DISPLAY_WIDTH - 50, DISPLAY_HEIGHT - 50)

        # do stuff
        birdie.draw()

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
