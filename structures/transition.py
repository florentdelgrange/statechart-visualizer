class Transition:
    def __init__(self, source: object, target: object, guard: str= '', event: str= '', action: str= ''):
        self.source = source
        self.target = target
        self.guard = guard
        self.event = event
        self.action = action
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0

    @property
    def coordinates(self):
        return (self.x1, self.y1), (self.x2, self.y2)

    def update_coordinates(self, start, end):
        (x1, y1), (x2, y2) = start, end
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2

    def __str__(self):
        return "Transition : " + self.source.name + " -> " + self.target.name

    def __repr__(self):
        return self.__str__()
