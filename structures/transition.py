class Transition:
    def __init__(self, source: object, target: object, guard: str= '', event: str= '', action: str= ''):
        self.source = source
        self.target = target
        self.guard = guard
        self.event = event
        self.action = action
        self._x1, self._x2, self._y1, self._y2 = 0, 0, 0, 0
        self.polyline = []

    @property
    def coordinates(self):
        if self.polyline:
            return self.polyline[0], self.polyline[len(self.polyline) - 1]
        else:
            return (self._x1, self._y1), (self._x2, self._y2)

    def update_coordinates(self, start, end):
        (x1, y1), (x2, y2) = start, end
        self._x1, self._x2, self._y1, self._y2 = x1, x2, y1, y2

    def __str__(self):
        return "Transition : " + self.source.name + " -> " + self.target.name

    def __repr__(self):
        return self.__str__()
