from sismic.model.elements import CompoundState, OrthogonalState
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
            height = max(list(map(lambda x: x.height, self.children)) or [0]) + self.header + space
        else:
            width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space,
                        space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = sum(map(lambda x: x.height + space, self.children)) + self.header
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
                child.update_coordinates(insert=(w, h - child.height / 2))
                w += child.width
        else:
            w = self._x + self.width / 2
            h = self._y + self.header - space
            for child in self.children:
                h += space
                child.update_coordinates(insert=(w - child.width / 2, h))
                h += child.height

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
        for child in self._children:
            if child._parallel_states:
                return True

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
    def shape(self):
        return self._shape

    @property
    def parent(self):
        return self._parent

    @property
    def axis(self):
        return self._axis


class InitBox(Box):
    def __init__(self, root_state):
        super().__init__(name='', axis=None)
        self._transitions = [Transition(source=self, target=root_state)]
        self._width, self._height = self.compute_dimensions()
        self._shape = 'circle'

    def compute_dimensions(self):
        return radius * 2, radius * 2


class RootBox(Box):
    def __init__(self, statechart):
        super().__init__(name=statechart.name, axis='horizontal')

        # first initializes all the boxes
        self._inner_states = [Box(name) for name in statechart.states]

        def init(state, axis):
            # note : horizontal axis parameter allow alternating of axis for the initialization
            axis = next(filter(lambda x: x != axis, ['horizontal', 'vertical']))
            box = next(x for x in self._inner_states if x.name == state.name)
            children_statechart = statechart.children_for(state.name)
            children = []
            for child in children_statechart:
                children += [init(statechart.state_for(child), axis)]

            if isinstance(state, CompoundState) and state.initial is not None:
                root_state = next(x for x in children if x.name == state.initial)
                children = [InitBox(root_state), root_state] + list(filter(lambda x: x is not root_state, children))
            else:
                root_state = None

            entry, exit = None, None
            if state.on_entry is not None: entry = state.on_entry
            if state.on_exit is not None: exit = state.on_exit
            if isinstance(state, OrthogonalState):
                for child in children:
                    child.update(parallel_states=list(filter(lambda x: x is not child, children)))
            box.update(new_children=children, entry=entry, exit=exit, root_state=root_state, axis=axis)
            return box

        root = init(statechart.state_for(statechart.root), self._axis)
        self.update(new_children=[InitBox(root), root], entry=statechart.preamble)
        self.update_coordinates()

    @property
    def transitions(self):
        """
        Return all the transitions in this box
        """
        transitions = []  # List[Transition]

        def find_transitions(box, transitions):
            for child in box.children:
                transitions += child.transitions
                find_transitions(child)

        return find_transitions(self, transitions)
