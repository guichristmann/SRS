from simulator import *

class Controller:
    def __init__(self, color=WHITE):
        self.color = color
    
    def communicate(self, received):
        send = self.think(received)
        return send

    def think(self, received):
        # do stuff with message received
        #print received

        message = {
            "move": False, # bool
            "rotate": 0,   # -1(left), 0(stay) ,1(right)
            "pick": True, # bool
            "drop": False  # bool
        }

        if len(received["balls"]) > 0:
            min_distance = 1000
            closest = -1
            for i, b in enumerate(received["balls"]):
                if b.r < min_distance:
                    min_distance = b.r
                    closest = i

            goal = received["balls"][closest]
            move = True
            print "closest", closest, "goal", goal.a
            if goal.a > 0:
                rotate = 1
            else:
                rotate = -1

            message = {
                "move": move,#False, # bool
                "rotate": rotate,#-1,   # -1(left), 0(stay) ,1(right)
                "pick": True, # bool
                "drop": False  # bool
            }
        return message
