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

class gameEnv:
    def __init__(self):
        self.reset()
        # pass

    def reset(self):
        self.bird = Bird()
        self.pipes = [Pipe(DISPLAY_WIDTH)]
        self.score = 0
        self.game_over = False
        collided = False

    def step(self, action):
        global collided
        reward = 0

        # update game state
        self.bird.update(action)

        for pipe in self.pipes:
            pipe.draw()
            pipe.move()

            collission = Collision(self.bird, pipe)
            if collission.checkCollison():
                self.game_over = True
                collided = True
                self.bird.color = RED

            if pipe.x < self.bird.x and pipe.passed == False:
                pipe.passed = True
                self.score += 1

        if self.game_over:
            reward = -1
        else:
            reward = 0.1 # small reward for just surviving

        # updating score
        for pipe in self.pipes:
            if pipe.x < self.bird.x and not pipe.passed:
                pipe.passed = True
                self.score +=1
                reward = 1 # Large reward for passing a pipe

        # removing pipe if out of screen
        self.pipes = [pipe for pipe in self.pipes if pipe.x > -pipe.width]

        # adding new pipe
        if self.pipes[-1].x < DISPLAY_WIDTH - 500:
            self.pipes.append(Pipe(DISPLAY_WIDTH))

    def render(self):
        print_stuff(36,str(self.score), GREEN, DISPLAY_WIDTH -50, DISPLAY_HEIGHT-50)

        # frame rate
        clock.tick(FPS)
        pg.display.flip()

    def get_state(self):
        if self.pipes[0].x > self.bird.x:
            pipe = self.pipes[0]
        else:
            pipe = self.pipes[1]

        state = [self.bird.y/DISPLAY_HEIGHT, self.bird.vel/10, (pipe.x - self.bird.x) / DISPLAY_WIDTH, (pipe.topHeight - self.bird.y)/ DISPLAY_HEIGHT, (pipe.bottomY - self.bird.y)/ DISPLAY_HEIGHT]

        return np.array(state)

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # initializing random weights
        self.weights_input_hidden = np.random.rand(input_size, hidden_size)
        self.weights_hidden_output = np.random.rand(hidden_size, output_size)
        self.learning_rate = 0.01

    # activation function
    def sigmoid(self, x):
        return 1/(1+np.exp(-x))

    def sigmoid_derivative(self,x):
        return x*(1-x)

    def forward_prop(self, inputs):
        self.hidden = self.sigmoid(np.dot(inputs, self.weights_input_hidden))
        self.output = self.sigmoid(np.dot(self.hidden, self.weights_hidden_output))

    # backpropagation
    def train(self, inputs, expected_output):
        output = self.forward_prop(inputs)
        error = expected_output - output
        d_output = error * self.sigmoid_derivative(output)
        error_hidden = d_output.dot(self.weights_hidden_output.T)
        d_hidden = error_hidden * self.sigmoid_derivative(self.hidden)

        # updating the weights
        self.weights_hidden_output += self.hidden.T.dot(d_output) * self.learning_rate
        self.weights_input_hidden += np.array(inputs).T.dot(d_hidden) * self.learning_rate


# Input Layer -> Bird's Y coordinate, Bird's Velocity, Horizontal distance to the Pipe, vertical distance to the bottom of the top pipe, vertical distance to the top of the bottom pipe

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
        if not collided:
            self.x -= 5;

class Bird:
    def __init__(self):
        self.x = 100 # fixed
        self.y= DISPLAY_HEIGHT//2
        self.radius = 15
        self.color = WHITE
        self.start_time = (time.time())
        self.vel = 4
        self.jumpVel = -12

    def draw(self):
        pg.draw.circle(DISPLAY, self.color, (self.x,self.y), self.radius)

    def update(self, action):
        self.draw()
        if not collided:
            self.move(action)

    def move(self,action):
        self.y += self.vel
        if action == 1: #jump
            self.y += self.jumpVel
            self.start_time = time.time()
        else:
            t = round(time.time() - self.start_time,2)
            self.y += self.vel*t + 0.5*t**2;

class Collision:
    def __init__(self, Bird, Pipe):
        self.bird = Bird;
        self.pipe = Pipe;

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
    font = pg.font.SysFont("Arial", Font_Size)
    text_render = font.render(text, 1, color)
    DISPLAY.blit(text_render, (x, y))

# Game loop
def main():
    running = True
    game = gameEnv()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        keys = pg.key.get_pressed()
        action = 1 if keys[pg.K_SPACE] else 0

        DISPLAY.fill(BLACK)
        game.step(action)
        game.render()

    pg.quit()
    sys.exit()

main()
