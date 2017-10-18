from controller import IController

PICK_BALLS = 0
DROP_BALLS = 1

tick_count = 0
class Christmann_Controller(IController):
    def __init__(self):
        self.color = (84, 22, 180)
        self.name = "ChristBot" 

    def dropBalls(self):
        print "I'm going to drop my balls"
        if self.dropzone_pos.a > 0:
            rotate = 1
        elif self.dropzone_pos.a < 0:
            rotate = -1
        else:
            rotate = 0

        self.message['move'] = True
        self.message['rotate'] = rotate
        
        if self.dropzone_pos.r < 100: # robot is inside dropzone
            self.message['drop'] = True

    def pickBall(self, ball):
        print "I'm going to pick a ball."
        if ball.a > 0.1:
            rotate = 1
            move = False
        elif ball.a < -0.1:
            rotate = -1
            move = False
        else:
            rotate = 0
            move = True

        self.message['move'] = move
        self.message['rotate'] = rotate
        self.message['pick'] = True

        return self.message

    def think(self, received):
        global tick_count
        tick_count += 1

        self.message = {
            "move": False, # bool
            "rotate": 0,   # -1(left), 0(stay) ,1(right)
            "pick": False, # bool
            "drop": False  # bool
        }

        picked_balls = received['picked_balls']
        self.dropzone_pos = received['dropzone']
        balls = sorted(received['balls'], key=lambda x : x.r) # orders ball by closest

        if picked_balls == 3:
            self.dropBalls()
        elif picked_balls == 0:
            self.pickBall(balls[0])
        else:
            if self.dropzone_pos.r < balls[0].r + 100: # dropzone is closer than closest ball
                self.dropBalls()
            else:
                self.pickBall(balls[0])

        return self.message
