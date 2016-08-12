from cassowary import STRONG
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

    def __repr__(self):
        return self.box1.__repr__() + ' ' + self.direction + ' ' + self.box2.__repr__()


class BoxWithConstraints:
    """
    Box decorator for the resolution of constraints
    """
    def __init__(self, box, coordinates):
        x1, y1, x2, y2 = coordinates[box]
        self._box = box
        self._x = Variable(box.name + ' x', x1)
        self._y = Variable(box.name + ' y', y1)
        self._width, self._height = x2 - x1, y2 - y1

        def additional_space():
            x1, y1, x2, y2 = 0, 0, 0, 0
            if self.box.has_self_transition:
                if self.box.zone == 'north' or self.box.zone == 'west':
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
    def space(self):
        return self._space

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __repr__(self):
        return 'decorator<' + self.box.__repr__() + '>'


def resolve(parent, coordinates, children, constraint_list):
    """
    Resolve a coordinates problem. The coordinates of the children entered in parameter will be computed.
    :param parent: the main box that contains the children entered in parameter
    :param coordinates: the dict of children's boxes coordinates (can be obtained by child.coordinates)
    :param children: the children to dispose in the parent's box
    :param constraint_list: the list of constraints
    :return: the dict that contains the coordinates of the children in parameter
    """

    if parent.orthogonal_state:
        if parent.axis == 'horizontal':
            height = max(map(lambda child: coordinates[child][3] - coordinates[child][1], parent.children))
            for child in parent.children:
                x1, y1, x2, y2 = coordinates[child]
                coordinates[child] = (x1, y1, x2, y1 + height)
        else:
            width = max(map(lambda child: coordinates[child][2] - coordinates[child][0], parent.children))
            for child in parent.children:
                x1, y1, x2, y2 = coordinates[child]
                coordinates[child] = (x1, y1, x1 + width, y2)

    boxes = list(map(lambda child: BoxWithConstraints(child, coordinates), children))
    constraints = list(map(lambda constraint: Constraint(next(filter(lambda x: x.box == constraint.box1, boxes),
                                                              BoxWithConstraints(constraint.box1, coordinates)),
                                                         constraint.direction,
                                                         next(filter(lambda x: x.box == constraint.box2, boxes),
                                                              BoxWithConstraints(constraint.box2, coordinates))),
                           constraint_list))

    def add_constraint(solver, constraint):
        box1 = constraint.box1
        box2 = constraint.box2
        x1, y1, x2, y2 = box1.space
        x3, y3, x4, y4 = box2.space
        {
            'north': lambda: solver.add_constraint(box1.y + box1.height + y2 + space + y3 < box2.y, strength=STRONG),
            'east': lambda: solver.add_constraint(box1.x > box2.x + box2.width + x4 + space + x1, strength=STRONG),
            'south': lambda: solver.add_constraint(box1.y > box2.y + box2.height + y4 + space + y1, strength=STRONG),
            'west': lambda: solver.add_constraint(box1.x + box1.width + x2 + space + x3 < box2.x, strength=STRONG)
        }[constraint.direction]()

    solver = SimplexSolver()

    # dimension of the frame
    left_limit = Variable('left', 0)
    top_limit = Variable('top', parent.header)
    right_limit = Variable('right', 0)
    bot_limit = Variable('bottom', 0)

    # define the base constraints (stay)
    solver.add_stay(left_limit)
    solver.add_stay(top_limit)

    for i in range(len(boxes)):
        b1 = boxes[i]
        x1, y1, x2, y2 = b1.space
        solver.add_constraint(b1.x > left_limit + space + x1)
        solver.add_constraint(b1.y > top_limit + space + y1)
        solver.add_constraint(b1.x + b1.width + x2 + space < right_limit)
        solver.add_constraint(b1.y + b1.height + y2 + space < bot_limit)
        if parent.axis == 'horizontal':
            solver.add_constraint(b1.y + y1 - top_limit == bot_limit - b1.y - b1.height - y2, strength=WEAK)
        else:
            solver.add_constraint(b1.x + x1 - left_limit == right_limit - b1.x - b1.width - x2, strength=WEAK)
        for b2 in boxes[i + 1:]:
            x3, y3, x4, y4 = b2.space
            if parent.axis == 'horizontal':
                solver.add_constraint(b2.x > b1.x + b1.width + space + x2 + x3, strength=WEAK)
            else:
                solver.add_constraint(b2.y > b1.y + b1.height + space + y2 + y3, strength=WEAK)

    for constraint in constraints:
        add_constraint(solver, constraint)

    new_coordinates = {parent: (0, 0, right_limit.value, bot_limit.value)}
    for box in boxes:
        new_coordinates[box.box] = (box.x.value, box.y.value, box.x.value + box.width, box.y.value + box.height)
    return new_coordinates
