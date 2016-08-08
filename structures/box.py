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
        self._root_state = None  # type: Box ; Initial inner state in this Box
        self._parent = None  # type: Box
        self._shape = 'rectangle'

    def update(self, new_children=None, new_transitions=None, entry=None,
               exit=None,
               root_state=None,
               axis='', parallel_states=None):
        """
        Update the dimensions of the box. Some optional parameters can be added
        so that they are updated at the same time.
        Note that the Box dimensions depend on these parameters.

        :param new_children: list of Boxes to add to the children list of this Box
        :param new_transitions: list of Transitions to add to the transitions list of this Box
        :param entry: entry text of this Box
        :param exit: exit text of this Box
        :param root_state: initial state of this Box
        :param axis: the axis of the box; must be vertical or horizontal
        :param parallel_states: the list of parallel Boxes
        """
        if new_children is not None:
            self._children += new_children
            for child in new_children:
                child._parent = self
        if new_transitions is not None:
            self._transitions += new_transitions
        if entry is not None:
            self._entry = entry
        if exit is not None:
            self._exit = exit
        if root_state is not None:
            self._root_state = root_state
        if axis == 'vertical' or axis == 'horizontal':
            self._axis = axis
        if parallel_states is not None:
            self._parallel_states = parallel_states

    @property
    def dimensions(self):
        width, height = self.compute_dimensions()
        if self.parallel_states:
            if self.parent.axis == 'horizontal':
                height = max(map(lambda x: x.compute_dimensions()[1], self.parent.children))
            else:
                width = max(map(lambda x: x.compute_dimensions()[0], self.parent.children))
        return width, height

    def compute_dimensions(self):
        """
        Compute the dimensions of the box.

        :return: the width and the height of the box.
        """
        if self._parallel_states:
            p_len = 14 * char_width
        else:
            p_len = 0
        if self.entry != '':
            entry_len = (8 + len(self._entry)) * char_width
        else:
            entry_len = 0
        if self.axis == 'horizontal':
            width = max(sum(map(lambda x: x.width + space, self.children)) + space,
                        space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = max(list(map(lambda x: x.height, self.children)) or [0]) + self.header + 2 * space
            # self transitions
            width += sum(map(lambda x: space, filter(lambda child: child.has_self_transition, self.children)))
            height += next(map(lambda x: space,
                               filter(lambda child: child.has_self_transition and child.zone == 'west', self.children)),
                           0)
            height += next(map(lambda x: space,
                               filter(lambda child: child.has_self_transition and child.zone == 'east', self.children)),
                           0)
        else:
            width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space,
                        space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = sum(map(lambda x: x.height + space, self.children)) + self.header
            # self transitions
            width += next(map(lambda x: space,
                              filter(lambda child: child.has_self_transition and child.zone == 'north', self.children)),
                          0)
            width += next(map(lambda x: space,
                              filter(lambda child: child.has_self_transition and child.zone == 'south', self.children)),
                          0)
            height += sum(map(lambda x: space, filter(lambda child: child.has_self_transition, self.children)))

        return width, height

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

    def coordinates(self, insert=(0, 0)):
        """
        Computes the coordinates of all the Boxes in this Box and returns a dict
        whose key is a box and the value is the insert of the Box.

        :param insert: (optional) the insert of the box - initially (0,0)
        :return: the dictionary linking the boxes with their insert
        """
        x, y = insert
        coordinates = {self: insert}

        if self._axis == 'horizontal':
            w = x
            h = y + (self.height + self.header) / 2
            for child in self.children:
                w += space
                if child.has_self_transition and child.zone == 'west':
                    w += space
                coordinates.update(child.coordinates(insert=(w, h - child.height / 2)))
                w += child.width
                if child.has_self_transition and child.zone == 'east':
                    w += space
        else:
            w = x + self.width / 2
            h = y + self.header - space
            for child in self.children:
                h += space
                if child.has_self_transition and child.zone == 'north':
                    h += space
                coordinates.update(child.coordinates(insert=(w - child.width / 2, h)))
                h += child.height
                if child.has_self_transition and child.zone == 'south':
                    h += space
        return coordinates

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

    @property
    def transitions(self):
        return self._transitions

    @property
    def entry(self):
        return self._entry

    @property
    def parallel_states(self):
        return self._parallel_states

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
            h += space + char_height
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
