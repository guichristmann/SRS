import random
import pygame
from point2 import Point2
from pygame.locals import *
from controller import *
from math import pi


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
WHITE = (255, 255, 255)

# simulation parameters
INITIAL_BALLS = 10
MAX_CARRY_BALLS = 3 # amount of balls a robot can carry
MAX_BALLS = 100 # max spawned balls
DROPZONE_CENTER = Point2((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
DROPZONE_RADIUS = 100
MOVE_STEP = 2 
TURN_STEP = 0.025 # increment in radians to robot orientation


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
        self.picking = False
        self.dropping = False

    def executeMessage(self, message):
        if message["move"]:
            self.move()

        if message["rotate"] == -1:
            self.turn(False)
        elif message["rotate"] == 1:
            self.turn(True)

        if message["pick"]:
            self.picking = True

        if message["drop"]:
            self.dropping = True

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
                if (b.pos - self.pos).r < ROBOT_RADIUS - BALL_RADIUS and not b.owner:
                    b.owner = self
                    self.picked_balls.append(b)
                    break

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

class Communicator:
    def __init__(self, robot, controller):
        self.robot = robot
        self.controller = controller

class World(object):
    def __init__(self, controllers=[]):
        self.communicators = []
        for c in controllers:
            control = Communicator(Robot(c.color), c)
            self.communicators.append(control)

        self.balls = []
        self.state = True

        # spawn x balls, x being the parameter of the range function
        for i in range(INITIAL_BALLS):
            self.spawnBall()

    # spawn a ball
    def spawnBall(self):
        pos = Point2(random.randint(10, SCREEN_WIDTH - 10),
                     random.randint(10, SCREEN_HEIGHT - 10))

        # creates a ball in front of the initial position of the robot
        # for debugging
        # pos = Point2(SCREEN_WIDTH/2 + DROPZONE_RADIUS*2, SCREEN_HEIGHT/2)

        if (pos - DROPZONE_CENTER).r < DROPZONE_RADIUS:
            self.spawnBall()
        else:
            self.balls.append(Ball(pos))

    # checks if balls are dropped in the drop zone and spawn balls randomly
    def updateWorld(self):
        if self.tick_counter % 120.0 == 0:
            if len(self.balls) < MAX_BALLS:
                self.spawnBall()

        for c in self.communicators:
            msg_to_controller = self.generateMessage(c.robot)
            msg_from_controller = c.controller.communicate(msg_to_controller)
            c.robot.executeMessage(msg_from_controller)

            if c.robot.picking and len(self.balls):
                self.pickClosestBall(c.robot)
                c.robot.picking = False

        # atualizar posicapo da bolas

    def pickClosestBall(self, robot):
        # find closest ball
        min_dist = 1000
        closest  = self.balls[0]
        for b in self.balls:
            dist = (robot.pos - b.pos).r
            if dist < min_dist:
                min_dist = dist
                closest = b
        # if closest ball is inside picking range]
        print min_dist
        if min_dist < ROBOT_RADIUS - BALL_RADIUS:
            # if robot can pick more balls
            if len(robot.picked_balls) < 3:
                # put ball in robot
                robot.picked_balls.append(closest)
            # remove ball from world
            self.balls.remove(closest)



    def generateMessage(self, robot):
        balls_pos = []
        for b in self.balls:
            relative = b.pos - robot.pos
            relative.a -= robot.orientation
            relative.a = normalizeAngle(relative.a)

            balls_pos.append(relative)
            
        message = {
            "balls": balls_pos,
            "dropzone": (robot.pos - DROPZONE_CENTER),
            "picked_balls": len(robot.picked_balls)
        }
        return message

    def drawBalls(self):
        for b in self.balls:
            pygame.draw.circle(screen, GREEN, b.pos.rect(asInt=True), BALL_RADIUS) 

    def drawRobots(self):
        for c in self.communicators:
            c.robot.drawRobot()

    # draws everything the world contains
    def drawWorld(self):
        screen.fill(BACKGROUND)

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

def normalizeAngle(angle):
    while angle > pi:
        angle -= 2*pi
    while angle < -pi:
        angle += 2*pi
    return angle

if __name__ == "__main__":
    c = Controller()
    world = World([c])
    world.run()
