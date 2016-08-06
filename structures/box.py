from structures.transition import Transition

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
        self._text_coordinates = {'name': (0, 0), 'exit': (0, 0), 'entry': (0, 0)}  # type Dict[str: (int, int)]
        self._width, self._height = 0, 0
        self._x, self._y = 0, 0
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

        self._width, self._height = self.compute_dimensions()

        if self.orthogonal_state:
            if self._axis == 'horizontal':
                height = max(map(lambda x: x.height, self.children))
                for brother in self.children:
                    brother._height = height
            else:
                width = max(map(lambda x: x.width, self.children))
                for brother in self.children:
                    brother._width = width

    def zone_of(self, box):
        """
        box is ___ of self

        :param box: the box to determine the zone compared to self
        :return: the zone of the box
        """
        if box in self.ancestors:
            return 'inside'
        elif self in box.ancestors:
            return 'a container'
        else:
            (x1, y1), (x2, y2) = self.coordinates
            (x3, y3), (x4, y4) = box.coordinates
            x1, y1 = ((x1 + x2) / 2, (y1 + y2) / 2)
            x2, y2 = ((x3 + x4) / 2, (y3 + y4) / 2)
            if x1 <= x2 and y1 >= y2:
                return 'northeast'
            elif x1 >= x2 and y1 >= y2:
                return 'northwest'
            elif x1 >= x2 and y1 <= y2:
                return 'southwest'
            else:
                return 'southeast'

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

    def get_text_position_of(self, attribute):
        """
        get the position of the attribute entered in parameter

        :param attribute: 'name' | 'entry' | 'exit'
        :return: the position of the attribute
        """
        return self._text_coordinates[attribute]

    def update_coordinates(self, insert: (int, int) = (0, 0)):
        self._x, self._y = insert

        # update text coordinates
        # name coordinates
        w = self._x + self.width / 2
        h = self._y + space + char_height
        if self._parallel_states:
            w -= (len(self.name) * char_width + 13 * char_width) / 2  # for the <<parallel>> zone left to the name
        else:
            w -= (len(self.name) * char_width) / 2
        self._text_coordinates['name'] = (w, h)

        # 'on entry' zone coordinates
        if self._entry != '':
            w = self._x + space
            h += space + char_height
            self._text_coordinates['entry'] = (w, h)

        # TODO : 'exit' zone
        # update children coordinates

        if self._axis == 'horizontal':
            w = self._x
            h = self._y + (self.height + self.header) / 2
            for child in self.children:
                w += space
                if child.has_self_transition and child.zone == 'west':
                    w += space
                child.update_coordinates(insert=(w, h - child.height / 2))
                w += child.width
                if child.has_self_transition and child.zone == 'east':
                    w += space
        else:
            w = self._x + self.width / 2
            h = self._y + self.header - space
            for child in self.children:
                h += space
                if child.has_self_transition and child.zone == 'north':
                    h += space
                child.update_coordinates(insert=(w - child.width / 2, h))
                h += child.height
                if child.has_self_transition and child.zone == 'south':
                    h += space

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

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
    def coordinates(self):
        """
        The coordinates of the Box with (insert=(x1, y1), end=(x2, y2))
        """
        return (self._x, self._y), (self._x + self.width, self._y + self.height)

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
