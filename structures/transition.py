from box import Box

class Transition:


    def __init__(self, target: Box, guard: str='', event: str='', action: str=''):
        self.target = target
        self.guard = guard
        self.event = event
        self.action = action
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0


    @property
    def coordinates(self):
        return (self.x1, self.y1), (self.x2, self.y2)


    def update_coordinates(self, insert=(x1, y1), end=(x2, y2)):
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
