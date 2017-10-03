from simulador import *
from time import sleep
import thread

# TODO Build a two-way communication so the controller can receive messages
# about the state of the world

# TODO Bug: if more than 3 balls are in the robot pick range (robot radius)
# they are all picked up.

class Controller:
    def __init__(self, color):
        self.color = color
        self.message = None

    def sendMessage(self, message):
        self.message = message

def run_world_thread(thread_name, controller):
    world = World([controller])
    world.run()

if __name__ == "__main__":
    controller = Controller((0, 137, 85))

    thread.start_new_thread(run_world_thread, ("World Thread", controller))

    while True:
        command = raw_input()
        if command == 'w':
            controller.sendMessage("move")
        elif command == 'a':
            controller.sendMessage("turnLeft")
        elif command == 'd':
            controller.sendMessage("turnRight")
        elif command == 'p':
            controller.sendMessage("pick")
        elif command == 'o':
            controller.sendMessage("drop")
