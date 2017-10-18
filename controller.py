class IController:
    def __init__(self, name="Unnamed", color=(255, 255, 255)):
        self.color = color
        self.name = name
    
    def communicate(self, received):
        send = self.think(received)
        return send

    def think(self, received):
        raise NotImplementedError( "Should have implemented this" )
