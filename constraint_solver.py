from cassowary import SimplexSolver, Variable, WEAK

class Constraint:
    def __init__(self, box1, direction, box2):
        self._box1 = box1
        self._box2 = box2
        self._direction = direction

    @property
    def box1(self):
        return self._box1

    @property
    def box2(self):
        return self._box2

    @property
    def direction(self):
        return self._direction

class BoxWithConstraints:
    def __init__(self, box):
        self._box = box
        self._x = Variable(box.name + ' x', 0)
        self._y = Variable(box.name + ' y', 0)

    @property
    def box(self):
        return self._box

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
