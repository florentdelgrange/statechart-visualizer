from cassowary import SimplexSolver, Variable, WEAK

space = 20


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

        def additional_space():
            x1, y1, x2, y2 = 0, 0, 0, 0
            if self.box.has_self_transition:
                if self.box.zone == 'north' or 'west':
                    x1 += space
                    y1 += space
                else:
                    x2 += space
                    y2 += space
            return x1, y1, x2, y2

        self._space = additional_space()

    @property
    def box(self):
        return self._box

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        self.box.width

    @property
    def height(self):
        self.box.height

    @property
    def space(self):
        return self._space


def resolve(parent, children, constraint_list, insert=(0, 0)):
    x, y = insert
    boxes = map(lambda child: BoxWithConstraints(child), children)
    constraints = map(lambda constraint: Constraint(next(filter(lambda x: x.box == constraint.box1, boxes),
                                                         BoxWithConstraints(constraint.box1)),
                                                    constraint.direction,
                                                    next(filter(lambda x: x.box == constraint.box2, boxes),
                                                         BoxWithConstraints(constraint.box2))),
                      constraint_list)

    def add_constraint(solver, constraint):
        box1 = constraint.box1
        box2 = constraint.box2
        x1, y1, x2, y2 = box1.space
        x3, y3, x4, y4 = box2.space
        {
            'north': lambda: solver.add_constraint(box1.y + box1.height + y2 + space + box2.y < y3),
            'east': lambda: solver.add_constraint(box1.x > box2.x + box2.width + x4 + space + x1),
            'south': lambda: solver.add_constraint(box1.y > box2.y + box2.height + y4 + space + y1),
            'west': lambda: solver.add_constraint(box1.x + box1.width + x2 + space + x3 < box2.x)
        }[constraint.direction]()

    solver = SimplexSolver()

    # dimension of the frame
    width, height = parent.dimensions
    left_limit = Variable('left', x)
    top_limit = Variable('top', y + parent.header)
    right_limit = Variable('right', x + width)
    bot_limit = Variable('bottom', y + height)

    # define the base constraints (stay)
    solver.add_stay(left_limit)
    solver.add_stay(top_limit)
    solver.add_stay(right_limit)
    solver.add_stay(bot_limit)

    for i in range(len(boxes)):
        b1 = boxes[i]
        x1, y1, x2, y2 = b1.space
        solver.add_constraint(b1.x > left_limit + space + x1)
        solver.add_constraint(b1.y > top_limit + space + y1)
        solver.add_constraint(b1.x + b1.width + x2 + space < right_limit)
        solver.add_constraint(b1.y + b1.height + y2 + space < bot_limit)
        for b2 in boxes[i + 1:]:
            x3, y3, x4, y4 = b2.space
            if parent.axis == 'horizontal':
                solver.add_constraint(b2.x > b1.x + b1.width + space + x2 + x3, strength=WEAK)
            else:
                solver.add_constraint(b2.y > b1.y + b1.height + space + y2 + y3, strength=WEAK)

    for constraint in constraints:
        add_constraint(solver, constraint)

    coordinates = {}
    for box in boxes:
        coordinates[box.box] = (box.x.value, box.y.value)
    return coordinates