from controller import IController

tick_count = 0
class Test_Controller(IController):
    def __init__(self, name=None, color=None):
        if name:
            self.name = name
        if color:
            self.color = color
        self.drop_balls = False

    def think(self, received):
        global tick_count
        tick_count += 1
        # do stuff with message received
        #print received

        message = {
            "move": False, # bool
            "rotate": 0,   # -1(left), 0(stay) ,1(right)
            "pick": False, # bool
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
            #print "closest", closest, "goal", goal.a
            if goal.a > 0:
                rotate = 1
            else:
                rotate = -1

            message["move"] = move
            message["rotate"] = rotate

        if received["picked_balls"] == 3:
            self.drop_balls = True
        elif received["picked_balls"] == 0:
            self.drop_balls = False

        if self.drop_balls:
            goal = received["dropzone"]
            if goal.a > 0:
                rotate = 1
            else:
                rotate = -1

            if goal.r < 100:
                message["drop"] = True

            message["rotate"] = rotate
            #message["pick"] = False 
            #message["drop"] = True 

        #print self.drop_balls, received["picked_balls"]
        if not self.drop_balls:
            message["pick"] = True
            message["drop"] = False

        return message
