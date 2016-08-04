class Transition:
    def __init__(self, source: object, target: object, guard: object = '', event: object = '', action: object = ''):
        self.source = source
        self.target = target
        self.guard = guard
        self.event = event
        self.action = action
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0

    @property
    def coordinates(self):
        return (self.x1, self.y1), (self.x2, self.y2)

    def update_coordinates(self, insert: (int, int), end=(int, int)):
        x1, y1, x2, y2 = insert, end
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
