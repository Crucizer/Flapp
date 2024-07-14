import pygame as pg
import numpy as np
import sys
import random
import time
from NeuralNetwork import NeuralNetwork
import operator
import math

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

class Species:

    def __init__(self, bird):
        self.birds = []
        self.avg_fitness = 0
        self.threshold = 1.2
        self.birds.append(bird)
        self.benchmark_fitness = bird.fitness
        self.benchmark_brain = bird.brain.clone()
        self.champion = bird.clone()


    def similarity(self, brain):
        similarity = self.weight_difference(self.benchmark_brain, brain)
        return self.threshold > similarity
    
    @staticmethod # doesn't take self as an argument
    def weight_difference(brain_1, brain_2):
        total_weight_difference = 0 
        for i in range(len(brain_1.connections)):
            total_weight_difference += abs(brain_1.connections[i].weight - brain_2.connections[i].weight)
        return total_weight_difference
    
    def add_to_species(self, bird):
        self.birds.append(bird)

    def sort_players_by_fitness(self):
        self.birds.sort(key=operator.attrgetter('fitness'), reverse = True)
        
        if self.birds[0].fitness > self.benchmark_fitness:
            self.benchmark_fitness = self.birds[0].fitness
            self.champion = self.birds[0].clone()

    def calculate_avg_fitness(self):
        total_fitness = 0 
        for bird in self.birds:
            total_fitness += bird.fitness

        if self.birds:
            self.avg_fitness = int(total_fitness / len(self.birds))
        else:
            self.avg_fitness = 0 

    def offspring(self):
        if len(self.birds) > 1:
            baby = self.birds[random.randint(0, len(self.birds) - 1)].clone()
        else:
            baby = self.birds[0].clone()
            # this shouldn't really happen
            print("NOT GOOD")
        baby.brain.mutate()
        return baby


class Population:
    def __init__(self, size):
        self.birds = []
        self.start_time = time.time()
        self.action = 0
        self.size = size
        self.pipes = [Pipe(DISPLAY_WIDTH)]
        self.species = []
        self.generation = 1

        for _ in range(self.size):
            self.birds.append(Bird())

        self.work()

    def work(self):
        for pipe in self.pipes:
            pipe.draw()
            pipe.move()

        for bird in self.birds:
            # updating bird
            if not bird.dead:
                if time.time() - self.start_time > 0.25:
                    self.action = bird.brain.feed_forward(bird.get_vision(self.pipes))
                    self.action = 1 if self.action > 0.5 else 0
                    bird.update(self.action)

            # checking collision
            for pipe in self.pipes:
                collision = Collision(bird, pipe)
                if collision.checkCollison():
                    bird.dead = True

                if pipe.x < bird.x and not pipe.passed:
                    pipe.passed = True # all birds have same x axis
                    bird.score += 1
            

        # removing pipes
        self.pipes = [pipe for pipe in self.pipes if pipe.x > -pipe.width]

        # adding new pipes
        if self.pipes[-1].x < DISPLAY_HEIGHT - 500:
            self.pipes.append(Pipe(DISPLAY_WIDTH))

        if self.extinct():
            self.pipes = [Pipe(DISPLAY_WIDTH)]
            self.naturalSelection()

    def extinct(self):
        died = True
        for i in range(self.size):
            if not self.birds[i].dead:
                died = False
                break
        
        return died
    
    def naturalSelection(self):
        # make species
        self.speciate()

        # calculate fitness
        self.calculate_fitness()

        # sort by fitness
        self.sort_species_by_fitness()

        # next generation
        self.next_gen()

    def speciate(self):
        for s in self.species:
            s.players = [] # resetting

        for bird in self.birds:
            add_to_species = False

            for s in self.species:
                if s.similarity(bird.brain):
                    s.add_to_species(bird)
                    add_to_species = True
                    break

            if not add_to_species:
                self.species.append(Species(bird))

    def calculate_fitness(self):
        for bird in self.birds:
            bird.calculate_fitness()

        for s in self.species:
            s.calculate_avg_fitness()


    def sort_species_by_fitness(self):
        for s in self.species:
            s.sort_players_by_fitness()

        self.species.sort(key=operator.attrgetter('benchmark_fitness'), reverse = True)

    def next_gen(self):
        children = [] # childrens for the next generation

        # Clone of champion is added to each species

        for s in self.species:
            children.append(s.champion.clone())

        children_per_species = math.floor((self.size - len(self.species)) / len(self.species))
        for s in self.species:
            for i in range(0, children_per_species):
                children.append(s.offspring())


        while len(children) < self.size:
            children.append(self.species[0].offspring()) # rest of the childrens are offspring from the best species

        self.birds = []

        for child in children:
            self.birds.append(child)

        self.generation += 1

    
    
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

        self.pipeGap = random.randint(120, 200)
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
        self.gravity = 0.5
        self.jumpVel = -12
        self.jumping = False
        self.jump_cooldown = 0 
        self.jump_cooldown_time = 0.1
        

        self.score = 0 
        self.dead = False
        self.lifespan = 0
        self.fitness = 0

        # for AI stuff
        self.input_values = 3 
        self.brain = NeuralNetwork(self.input_values)
        self.brain.generate_net()
        self.vision = [0.5,1,0.5] # random hardcoded value for now

    def draw(self):
        pg.draw.circle(DISPLAY, self.color, (self.x,self.y), self.radius)

    def update(self, action):
        if not self.dead: # bird disappears after colliding
            self.draw()
            self.move(action)

        # update lifespan
        self.lifespan += 0.1

    def move(self,action):
        current_time = time.time()
        
        # Apply gravity
        self.vel += self.gravity
        self.y += self.vel

        # Check if cooldown has passed
        if current_time - self.start_time > self.jump_cooldown_time:
            self.jumping = False

        # Jump if action is 1 and not already jumping
        if action == 1 and not self.jumping:
            self.vel = self.jumpVel
            self.jumping = True
            self.start_time = current_time

    def calculate_fitness(self):
        self.fitness = self.score*100 + self.lifespan

    def clone(self):
        clone = Bird()
        clone.fitness = self.fitness
        clone.brain = self.brain.clone()
        clone.brain.generate_net()

        return clone 
    
    def get_vision(self, pipes):
        nearest_pipe = min(pipes, key=lambda p: p.x - self.x if p.x > self.x else float('inf'))
        return [
            self.y / DISPLAY_HEIGHT,
            (nearest_pipe.x - self.x) / DISPLAY_WIDTH,
            (nearest_pipe.topHeight - self.y) / DISPLAY_HEIGHT
        ]
    

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