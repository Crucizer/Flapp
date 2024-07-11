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

collided = False

class forEachBird:
    def __init__(self, bird, pipes):
        self.bird = bird
        self.pipes = pipes
        self.dead = False
        self.score = 0

    def step(self, action):
        if not self.dead:
            self.bird.update(action)

        # Check if collision
        for pipe in self.pipes:
            collision = Collision(self.bird, pipe)

            if collision.checkCollison():
                self.dead = True
                self.bird.color = RED

            if pipe.x < self.bird.x and not pipe.passed:
                pipe.passed = True # all birds have x axis
                self.score +=1 

# move and draw the pipes and remove the pipes
# reset function
# extinct function
# constructor function

class Population:
    def __init__(self, size):
        self.birds = []
        self.start_time = time.time()
        self.action = 0
        self.size = size
        self.pipes = [Pipe(DISPLAY_WIDTH)]

        for _ in range(self.size):
            self.birds.append(forEachBird(Bird(), self.pipes))

        self.work()

    def work(self):
        for pipe in self.pipes:
            pipe.draw()
            pipe.move()

        # for each bird

        for i in range(self.size):
            if time.time() - self.start_time > 0.25:
                self.action = random.randint(0,1)
            self.birds[i].step(self.action)

        # removing pipes
        self.pipes = [pipe for pipe in self.pipes if pipe.x > -pipe.width]

        # adding new pipes
        if self.pipes[-1].x < DISPLAY_HEIGHT - 500:
            self.pipes.append(Pipe(DISPLAY_WIDTH))



    def extinct(self):
        died = True
        for i in range(self.size):
            if not self.birds[i].dead:
                died = False
                break
        
        return died
    
    def render(self):
        # print score maybe

        # frame rate
        clock.tick(FPS)
        pg.display.flip()


# Input Layer -> Bird's Y coordinate, Bird's Velocity, Horizontal distance to the Pipe, vertical distance to the bottom of the top pipe, vertical distance to the top of the bottom pipe

class Pipe:
    def __init__(self,x):
        self.x = x
        self.width = 75

        self.pipeGap = random.randint(70, 150)
        self.topHeight = random.randint(50, DISPLAY_HEIGHT - self.pipeGap)
        self.bottomHeight = DISPLAY_HEIGHT - self.topHeight
        self.bottomY = self.topHeight + self.pipeGap

        self.passed = False


    def draw(self):
        # top pipe
        pg.draw.rect(DISPLAY, WHITE, (self.x, 0, self.width, self.topHeight))
        # bottom pipe
        pg.draw.rect(DISPLAY, WHITE, (self.x, self.bottomY, self.width, self.bottomHeight))

    def move(self):
        # if not collided:
        self.x -= 5

class Bird:
    def __init__(self):
        self.x = 100 # fixed
        self.y= DISPLAY_HEIGHT//2
        self.radius = 15
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.start_time = (time.time())
        self.vel = 4
        self.jumpVel = -12

    def draw(self):
        pg.draw.circle(DISPLAY, self.color, (self.x,self.y), self.radius)

    def update(self, action):
        if not collided: # bird disappears after colliding
            self.draw()
            self.move(action)

    def move(self,action):
        self.y += self.vel
        if action == 1: #jump
            self.y += self.jumpVel
            self.start_time = time.time()
        else:
            t = round(time.time() - self.start_time,2)
            self.y += self.vel*t + 0.5*t**2
        

class Collision:
    def __init__(self, Bird, Pipe):
        self.bird = Bird
        self.pipe = Pipe

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
        elif (self.bird.y - self.bird.radius < 5):
            return True
        elif (self.bird.y + self.bird.radius > DISPLAY_HEIGHT -5):
            return True
        else:
            return False

def print_stuff(Font_Size, text, color, x, y):
    font = pg.font.SysFont("Arial", Font_Size)
    text_render = font.render(text, 1, color)
    DISPLAY.blit(text_render, (x, y))

# Game loop
def main():
    running = True
    game= Population(100)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        DISPLAY.fill(BLACK)
        game.work()
        game.render()

    pg.quit()
    sys.exit()

main()