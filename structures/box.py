import constraint_solver
from constraint_solver import Constraint

char_width, char_height, space, radius = 10, 20, 20, 20


class Box:
    """
    A box intends to represent a state and has its own dimensions.

    :param name: the state name
    :param axis: 'vertical' | 'horizontal': the inner boxes will be positioned on this axis
    """

    def __init__(self, name: str, axis: str = 'horizontal'):
        self._name = name
        self._axis = axis
        self._parallel_states = []  # type: list[Box]
        self._children = []  # type: list[Box]
        self._transitions = []  # type: list[Transition]
        self._entry = ''  # type: str
        self._exit = ''  # type: str
        self._parent = None  # type: Box
        self._shape = 'rectangle'
        self._constraints = []
        self._width, self._height = -1, -1

    @property
    def dimensions(self):
        # leaf box
        if not self.children:
            if self._parallel_states:
                p_len = 14 * char_width
            else:
                p_len = 0
            if self.entry != '':
                entry_len = max(map(lambda x: (8 + len(x)) * char_width, self._entry.split('\n')))
            else:
                entry_len = 0
            if self.exit != '':
                exit_len = max(map(lambda x: (8 + len(x)) * char_width, self._exit.split('\n')))
            else:
                exit_len = 0
            return max(p_len + len(self.name) * char_width, entry_len, exit_len) + 2 * space, self.header + 2 * space
        else:
            x1, y1, x2, y2 = self.coordinates[self]
            if self.parallel_states:
                if self.parent.axis == 'horizontal':
                    y2 = max(map(lambda child: child.coordinates[child][3], self.parent.children))
                else:
                    x2 = max(map(lambda child: child.coordinates[child][2], self.parent.children))
            return x2, y2

    def name_position(self, insert=(0, 0)):
        """
        gives the insert coordinates of the name following the insert coordinates of the Box (given in parameter)
        :return: the coordinates of the name text
        """
        x, y = insert
        w = x + self.width / 2
        h = y + space + char_height
        if self.parallel_states:
            w -= (len(self.name) * char_width + 13 * char_width) / 2  # for the <<parallel>> zone left to the name
        else:
            w -= (len(self.name) * char_width) / 2
        return w, h

    def entry_position(self, insert=(0, 0)):
        """
        gives the coordinates of the entry zone insert position
        """
        w, h = self.name_position(insert)
        if self._entry != '':
            w = insert[0] + space
            h += space + char_height
        return w, h

    def exit_position(self, insert=(0, 0)):
        """
        gives the coordinates of the exit zone insert position
        """
        w, h = self.entry_position(insert)
        if self._exit != '':
            w = insert[0] + space
            h += len(self.entry.split('\n')) * char_height
        return w, h

    @property
    def coordinates(self):
        """
        Computes the coordinates of all the Boxes in this Box and returns a dict
        whose key is a box and the value is the insert of the Box.

        :return: the dictionary linking the boxes with their insert
            format : {Box : (x1, y1, x2, y2)} where insert=(x1, y1) and end=(x2, y2)
        """
        if not self.children:
            return {self: (0, 0, self.width, self.height)}
        else:
            coordinates = {}
            for child in self.children:
                coordinates.update(child.coordinates)

            new_coordinates = constraint_solver.resolve(self, coordinates, self.children, self._constraints)

            def update_coordinates(box1, box2):
                x1, y1, x2, y2 = new_coordinates[box1]
                for child in box2.children:
                    x3, y3, x4, y4 = coordinates[child]
                    new_coordinates[child] = (x1 + x3, y1 + y3, x1 + x4, y1 + y4)
                    update_coordinates(box, child)

            for box in self.children:
                update_coordinates(box, box)

            return new_coordinates

    def move_to(self, direction, box):
        """
        move the box (self) following the direction of this box with the box in parameter
        :param direction: direction of self with the box in parameter ; type : str
        :param box: this box will not move : self will be moved following the direction of this box
        """

        # base case : self and box are brothers
        def smooth(box):
            for i in range(len(box.children)):
                child = box.children[i]
                if isinstance(child, GroupBox) and child.axis == box.axis:
                    box.remove_child(child)
                    for j in range(len(child.children)):
                        new_child = child.children[j]
                        box.add_child(new_child, i + j)

        if self == box:
            return
        if self in box.parent.children:
            parent = box.parent
            i_self = parent.children.index(self)
            i_box = parent.children.index(box)
            if direction == 'west of':
                if len(parent.children) == 2:
                    parent.axis = 'horizontal'
                if parent.axis == 'horizontal' and i_self > i_box:
                    parent._children = parent.children[:i_box] + [
                        self] + parent.children[i_box:i_self] + parent.children[i_self + 1:]
                elif parent.axis == 'vertical':
                    parent.remove_child(self)
                    parent.remove_child(box)
                    container = GroupBox('horizontal')
                    container.add_child(self)
                    container.add_child(box)
                    parent.add_child(container, index=i_box)
            elif direction == 'east of':
                if len(parent.children) == 2:
                    parent.axis = 'horizontal'
                if parent.axis == 'horizontal' and i_self < i_box:
                    parent._children = parent.children[:i_self] + parent.children[i_self + 1:i_box] + [
                        box, self] + parent.children[i_box + 1:]
                elif parent.axis == 'vertical':
                    parent.remove_child(self)
                    parent.remove_child(box)
                    container = GroupBox('horizontal')
                    container.add_child(box)
                    container.add_child(self)
                    parent.add_child(container, index=i_box)
            elif direction == 'north of':
                if len(parent.children) == 2:
                    parent.axis = 'vertical'
                if parent.axis == 'vertical' and i_self > i_box:
                    parent._children = parent.children[:i_box] + [
                        self] + parent.children[i_box:i_self] + parent.children[i_self + 1:]
                elif parent.axis == 'horizontal':
                    parent.remove_child(self)
                    parent.remove_child(box)
                    container = GroupBox('vertical')
                    container.add_child(self)
                    container.add_child(box)
                    parent.add_child(container, index=i_box)
            else:
                if len(parent.children) == 2:
                    parent.axis = 'vertical'
                if parent.axis == 'vertical' and i_self < i_box:
                    parent._children = parent.children[:i_self] + parent.children[i_self + 1:i_box] + [
                        box, self] + parent.children[i_box + 1:]
                elif parent.axis == 'horizontal':
                    parent.remove_child(self)
                    parent.remove_child(box)
                    container = GroupBox('vertical')
                    container.add_child(box)
                    container.add_child(self)
                    parent.add_child(container, index=i_box)
            smooth(closest_common_ancestor(self, box))
        else:
            ancestors_box1 = [self] + self.ancestors
            ancestors_box2 = [box] + box.ancestors
            parent = next(filter(lambda x: x in ancestors_box2, ancestors_box1))
            ancestors_box1[ancestors_box1.index(parent) - 1].move_to(direction, ancestors_box2[
                ancestors_box2.index(parent) - 1])

    def add_constraint(self, constraint):
        """
        Add the constraint in the right Box.
        If the parent of the two Boxes of the constraint is self, the constraint is added to self.
        Otherwise, find the common ancestor and add the constraint in this ancestor.
        """
        if constraint.box1.parent == constraint.box2.parent == self:
            # contradiction checking
            opposite = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
            opposite_constraints = list(
                filter(lambda c: (c.box1 == constraint.box1 and c.box2 == constraint.box2 and opposite[
                    c.direction] == constraint.direction) or (
                                     c.box1 == constraint.box2 and c.box2 == constraint.box1 and c.direction == constraint.direction),
                       self._constraints))
            if opposite_constraints:
                for x in opposite_constraints:
                    self._constraints.remove(x)
            else:
                self._constraints += [constraint]
        else:
            ancestors_box1 = [constraint.box1] + constraint.box1.ancestors
            ancestors_box2 = [constraint.box2] + constraint.box2.ancestors
            closest_ancestor = next(filter(lambda x: x in ancestors_box2, ancestors_box1))
            # find the first child of the ancestor that is an ancestor of the box
            box1 = ancestors_box1[ancestors_box1.index(closest_ancestor) - 1]
            box2 = ancestors_box2[ancestors_box2.index(closest_ancestor) - 1]
            closest_ancestor.add_constraint(Constraint(box1, constraint.direction, box2))

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self.dimensions[0]

    @property
    def height(self):
        return self.dimensions[1]

    @property
    def children(self):
        return self._children

    def add_child(self, box, index=-1, constraint=None):
        """
        Add a box as a child of this Box
        :param box: the child
        :param index: (optional) the child will be the ith son of this Box.
            If this parameter is missing, the child will be added as last son.
        :param constraint: (optional) It is a tuple that defines a constraint on the child.
            Example : box.add_child(state1, constraint=('south', state2))
            means that the state1 will be added to box with the constraint that state1 has to be south of state 2.
        :return: True if the child is added correctly to the box
        """
        if isinstance(box, Box):
            if index >= 0:
                self._children = self.children[:index] + [box] + self.children[index:]
            else:
                self._children.append(box)
            box._parent = self
            if constraint is not None:
                constraint = Constraint(box, constraint[0], constraint[1])
                self.add_constraint(constraint)
            return True
        return False

    def remove_child(self, box):
        if box in self.children:
            self.children.remove(box)
            box._parent = None
            return True
        else:
            return False

    @property
    def transitions(self):
        return self._transitions

    def add_transition(self, transition):
        if transition is not None and transition.source == self:
            self._transitions.append(transition)
            return True
        return False

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, entry):
        if type(entry) is str:
            self._entry = entry

    @property
    def exit(self):
        return self._exit

    @exit.setter
    def exit(self, exit):
        if type(exit) is str:
            self._exit = exit

    @property
    def parallel_states(self):
        return self._parallel_states

    def add_parallel_state(self, parallel_state):
        if type(parallel_state) is Box:
            self._parallel_states.append(parallel_state)
            return True
        return False

    @property
    def orthogonal_state(self):
        """
        return True if this state is an orthogonal state ie their
        children have parallel_states.
        """
        return next((True for child in self.children if child.parallel_states), False)

    @property
    def header(self):
        """
        Height of the header (name + entry)

        :return: the height of the header
        """
        h = 2 * space + char_height
        if self._entry != '':
            n = len(self._entry.split('\n'))
            h += space + n * char_height
        if self._exit != '':
            n = len(self._exit.split('\n'))
            h += space + n * char_height
        return h

    @property
    def ancestors(self):
        if self.parent is not None:
            return [self.parent] + self.parent.ancestors
        else:
            return []

    @property
    def shape(self):
        return self._shape

    @property
    def parent(self):
        return self._parent

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, axis):
        if axis == 'horizontal' or axis == 'vertical':
            self._axis = axis

    @property
    def zone(self):
        """
        :return: the zone of the box following its parent
        """
        if self.parent.children.index(self) <= len(self.parent.children) / 2 - 1:
            if self.parent.axis == 'horizontal':
                return 'west'
            else:
                return 'north'
        else:
            if self.parent.axis == 'horizontal':
                return 'east'
            else:
                return 'south'

    @property
    def has_self_transition(self):
        return next((True for t in self.transitions if t.target == self), False)

    def __repr__(self):
        return "State box : " + self.name


def closest_common_ancestor(box1, box2):
    ancestors_box1 = [box1] + box1.ancestors
    ancestors_box2 = [box2] + box2.ancestors
    return next(filter(lambda x: x in ancestors_box2, ancestors_box1))


class GroupBox(Box):
    def __init__(self, axis):
        super().__init__('', axis=axis)
        self._shape = "invisible"

    @property
    def header(self):
        return 0

    def __repr__(self):
        return "GroupBox : " + self.children.__str__()
