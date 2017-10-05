import random
import pygame
from point2 import Point2
from pygame.locals import *
from controller import *
from math import pi

# TODO Deal with droppping balls in the dropping ball zone and in the not dropping balls zone

# pygame constants
SCREEN_WIDTH = 1266
SCREEN_HEIGHT = 668
BALL_RADIUS = 5
ROBOT_RADIUS = 30

# colors
BACKGROUND = (30, 30, 30)
DROPZONE_COLOR = (50, 114, 50)
STRANGE_BLUE = (0, 72, 82)
RED = (255, 0, 0)
ORANGE = (244, 144, 30)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

# simulation parameters
INITIAL_BALLS = 10
MAX_CARRY_BALLS = 3 # amount of balls a robot can carry
MAX_BALLS = 100 # max spawned balls
DROPZONE_CENTER = Point2((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
DROPZONE_RADIUS = 100
MOVE_STEP = 2 
TURN_STEP = 0.025 # increment in radians to robot orientation
TICKRATE = 60 # how many ticks per second
BALL_SPAWN_RATE = TICKRATE * 0.5 # balls spawned per second


# pygame variables
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
balls_font = pygame.font.SysFont("comicsans", 30)
scoreboard_font = pygame.font.SysFont("comicsansms", 30)
name_font = pygame.font.SysFont("comicsansms", 15)

class Ball(object):
    def __init__(self, pos):
        self.pos = pos 
        self.owner = None

class Robot(object):
    def __init__(self, name, color, x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2):
        self.color = color
        self.name = name
        self.score = 0 # how many balls this robot dropped correctly
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

    # draws this robot
    def drawRobot(self):
        pygame.draw.circle(screen, self.color, self.pos.rect(asInt=True), ROBOT_RADIUS)
        end_point = Point2()
        end_point.r = ROBOT_RADIUS
        end_point.a = self.orientation
        end_point += self.pos

        pygame.draw.line(screen, RED, self.pos.rect(asInt=True), end_point.rect(asInt=True), 2)

        name_surface = name_font.render(self.name, True, WHITE)
        name_width = name_surface.get_width()
        pos = (self.pos.rect(asInt=True)[0] - name_width/2,
               self.pos.rect(asInt=True)[1] - ROBOT_RADIUS - 15)
        screen.blit(name_surface, pos)

class Communicator:
    def __init__(self, robot, controller):
        self.robot = robot
        self.controller = controller

class World(object):
    def __init__(self, controllers=[]):
        self.communicators = []
        for c in controllers:
            control = Communicator(Robot(c.name, c.color), c)
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

        if (pos - DROPZONE_CENTER).r < DROPZONE_RADIUS + 30:
            self.spawnBall()
        else:
            self.balls.append(Ball(pos))

    # checks if balls are dropped in the drop zone and spawn balls randomly
    def updateWorld(self):
        if self.tick_counter % BALL_SPAWN_RATE == 0:
            if len(self.balls) < MAX_BALLS:
                self.spawnBall()

        for c in self.communicators:
            msg_to_controller = self.generateMessage(c.robot)
            msg_from_controller = c.controller.communicate(msg_to_controller)
            c.robot.executeMessage(msg_from_controller)

            if c.robot.picking and len(self.balls):
                self.pickClosestBall(c.robot)
                c.robot.picking = False
            elif c.robot.dropping:
                self.dropBall(c.robot)
                c.robot.dropping = False

            print c.robot.name, c.robot.score

        self.checkDroppedBalls()

    # checks if any dropped balls are in the drop zone and awards points to
    # the robot that dropped it
    def checkDroppedBalls(self):
        for b in self.balls:
            if (b.pos - DROPZONE_CENTER).r < DROPZONE_RADIUS:
                b.owner.score += 1
                self.balls.remove(b) # kinda bad

    def pickClosestBall(self, robot):
        # find closest ball
        min_dist = 1000
        closest  = self.balls[0]
        for b in self.balls:
            dist = (robot.pos - b.pos).r
            if dist < min_dist:
                min_dist = dist
                closest = b

        # if closest ball is inside picking range
        #print min_dist
        if min_dist < ROBOT_RADIUS - BALL_RADIUS:
            # if robot can pick more balls
            if len(robot.picked_balls) < 3:

                # put ball in robot
                closest.owner = robot
                robot.picked_balls.append(closest)
                # remove ball from world
                self.balls.remove(closest)

    def dropBall(self, robot):
        if robot.picked_balls:
            dropped_ball = robot.picked_balls.pop()
            dropped_ball.pos = robot.pos

            self.balls.append(dropped_ball)

    def generateMessage(self, robot):
        balls_pos = []
        for b in self.balls:
            relative = b.pos - robot.pos
            relative.a -= robot.orientation
            relative.a = normalizeAngle(relative.a)

            balls_pos.append(relative)

        dropzone_relative = (DROPZONE_CENTER - robot.pos)
        dropzone_relative.a -= robot.orientation
        dropzone_relative.a = normalizeAngle(dropzone_relative.a)
            
        message = {
            "balls": balls_pos,
            "dropzone": dropzone_relative,
            "picked_balls": len(robot.picked_balls)
        }
        return message

    def drawBalls(self):
        # draws balls which are dropped on the world
        for b in self.balls:
            pygame.draw.circle(screen, ORANGE, b.pos.rect(asInt=True), BALL_RADIUS) 

        # checks if any robot is holding balls and draws that too
        for r in self.communicators:
            if len(r.robot.picked_balls):
                # draws text of how many balls the robot is carrying
                textSurface = balls_font.render(str(len(r.robot.picked_balls)), True, WHITE)
                pygame.draw.circle(screen, ORANGE, r.robot.pos.rect(asInt=True), BALL_RADIUS) 
                screen.blit(textSurface, r.robot.pos.rect(asInt=True))

    def drawRobots(self):
        for c in self.communicators:
            c.robot.drawRobot()

    def drawScoreboard(self):
        x_pos = 5
        y_pos = 5
        for c in self.communicators:
            string = c.robot.name + ": " + str(c.robot.score) + ' '
            score_surface = scoreboard_font.render(string, True, c.robot.color)
            screen.blit(score_surface, (x_pos, y_pos))
            y_pos += score_surface.get_height() + 20

    # draws everything the world contains
    def drawWorld(self):
        screen.fill(BACKGROUND)

        # draw dropzone
        pygame.draw.circle(screen, DROPZONE_COLOR, DROPZONE_CENTER.rect(asInt=True), DROPZONE_RADIUS) 

        self.drawRobots()
        self.drawBalls()
        self.drawScoreboard()

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

            clock.tick(TICKRATE)
            self.tick_counter += 1

# Used when returning state of the world for the controllers. When returning
# the orientation of the robot towards a ball this makes sure it is the smallest
# interval.
def normalizeAngle(angle):
    while angle > pi:
        angle -= 2*pi
    while angle < -pi:
        angle += 2*pi
    return angle

if __name__ == "__main__":
    c1 = Controller("Domotro", STRANGE_BLUE)
    c2 = Controller("Artorias", (200, 200, 200))
    c3 = Controller("Jao", (53, 193, 105))
    c4 = Controller("Nicholas Cage", (173, 85, 33))
    c5 = Controller("C3PO", GRAY)
    c6 = Controller("Meh", STRANGE_BLUE)
    c7 = Controller("Carlos Santana", (200, 200, 200))
    c8 = Controller("Solaire", (53, 193, 105))
    c9 = Controller("Genesio", (173, 85, 33))
    c10 = Controller("Estrume", GRAY)
    world = World([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
    world.run()
