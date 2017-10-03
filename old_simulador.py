import os
import random
import sys
import pygame
from point2 import Point2
from time import sleep
from pygame.locals import *
from collections import namedtuple
from copy import copy

# pygame constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_RADIUS = 5
ROBOT_RADIUS = 30

# colors
BACKGROUND = (30, 30, 30)
DROPZONE_COLOR = (244, 144, 30)
STRANGE_BLUE = (0, 72, 82)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# simulation parameters
MAX_CARRY_BALLS = 3 # amount of balls a robot can carry
MAX_BALLS = 100 # max spawned balls
DROPZONE_CENTER = Point2((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
DROPZONE_RADIUS = 100
MOVE_STEP = 2 
TURN_STEP = 0.02 # increment in radians to robot orientation

#CRTuple = namedtuple("Robot", "controller robot")

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class Ball(object):
    def __init__(self, pos):
        self.pos = pos 
        self.owner = None

class Robot(object):
    def __init__(self, color=STRANGE_BLUE, x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2):
        self.color = color
        self.pos = Point2(x, y)

        self.orientation = 0.0

        self.picked_balls = []

    def move(self):
        goal_position = Point2()
        goal_position.r = MOVE_STEP
        goal_position.a = self.orientation
        self.pos += goal_position

    def turn(self, direction):
        if direction:
            self.orientation += TURN_STEP
        else:
            self.orientation -= TURN_STEP

    # picks a ball up
    def pickBall(self, balls):
        if len(self.picked_balls) < MAX_CARRY_BALLS:
            for b in balls:
                if (b.pos - self.pos).r < ROBOT_RADIUS and not b.owner:
                    b.owner = self
                    self.picked_balls.append(b)

    # drops ball
    def dropBall(self):
        if self.picked_balls:
            self.picked_balls[-1].owner = None
            self.picked_balls.pop()

    # draws this robot
    def drawRobot(self):
        pygame.draw.circle(screen, self.color, self.pos.rect(asInt=True), ROBOT_RADIUS)
        end_point = Point2()
        end_point.r = ROBOT_RADIUS
        end_point.a = self.orientation
        end_point += self.pos

        pygame.draw.line(screen, RED, self.pos.rect(asInt=True), end_point.rect(asInt=True), 2)

class World(object):
    def __init__(self, controllers=[]):
        self.robots = []
        for c in controllers:
            self.robots.append((c, Robot(c.color)))

        self.balls = []
        self.state = True

        #self.background = pygame.image.load(os.path.join('bg', 'bg1.jpg'))

        # spawn x balls, x being the parameter of the range function
        for i in range(10):
            self.spawnBall()

    # spawn a ball
    def spawnBall(self):
        pos = Point2(random.randint(10, SCREEN_WIDTH - 10),
                     random.randint(10, SCREEN_HEIGHT - 10))

        if (pos - DROPZONE_CENTER).r < DROPZONE_RADIUS:
            self.spawnBall()
        else:
            self.balls.append(Ball(pos))

    # checks if balls are dropped in the drop zone and spawn balls randomly
    def updateWorld(self):
        if self.tick_counter % 120.0 == 0:
            if len(self.balls) < MAX_BALLS:
                self.spawnBall()

        for r in self.robots:
            i = 0
            # checks messages in robots
            if r[0].message == "hello":
                print "olar"

            elif r[0].message == "turnLeft":
                r[1].turn(False) 

            elif r[0].message == "turnRight":
                r[1].turn(True)

            elif r[0].message == "move":
                r[1].move()

            elif r[0].message == "pick":
                r[1].pickBall(self.balls)

            elif r[0].message == "drop":
                r[1].dropBall()

            # updates carried balls positions
            #print "i[" + str(i) + "]: ", len(r[1].picked_balls)
            offset = -3 * BALL_RADIUS
            for b in r[1].picked_balls:
                b.pos = copy(r[1].pos)
                b.pos.x += offset
                offset += 3 * BALL_RADIUS

            i += 1

    def drawBalls(self):
        for b in self.balls:
            pygame.draw.circle(screen, GREEN, b.pos.rect(asInt=True), BALL_RADIUS) 

    def drawRobots(self):
        for r in self.robots:
            r[1].drawRobot()

    # draws everything the world contains
    def drawWorld(self):
        screen.fill(BACKGROUND)

        # draws background
        #screen.blit(self.background, (0, 0))

        # draw dropzone
        pygame.draw.circle(screen, DROPZONE_COLOR, DROPZONE_CENTER.rect(asInt=True), DROPZONE_RADIUS) 

        self.drawRobots()
        self.drawBalls()

        pygame.display.flip()

    # main loop
    def run(self):
        self.tick_counter = 0

        while self.state:
            self.drawWorld()
            self.updateWorld()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.state = False

                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        self.state = False

            clock.tick(60)
            self.tick_counter += 1

if __name__ == "__main__":
    c = meh()
    c.color = STRANGE_BLUE
    c2 = meh()
    c2.color = (120, 0, 255)
    world = World([c, c2])
    world.run()
