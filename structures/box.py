from sismic.model import Statechart
from sismic.model.elements import CompoundState, OrthogonalState
from transition import Transition

char_width, char_height, space, radius = 10, 20, 20, 20


class Box:
    """
    A box intends to represent a state and has its own dimensions.

    :param name: the state name
    :param axis: 'vertical' | 'horizontal': the inner boxes will be positioned on this axis
    """


    def __init__(self, name: str, axis: str='horizontal'):
        self._name = name
        self._axis = axis
        self._parallel_states = [] # type: List[Box]
        self._children = [] # type: List[Box]
        self._transitions = [] # type: List[Transition]
        self._entry = '' # type: str
        self._exit = '' # type: str
        self._root_state = None # type : Box ; Initial inner state in this Box
        self._width, self._height = 0, 0
        self._x, self._y = 0, 0
        self._shape = 'rectangle'


    def update(new_children: List[Box]=None, new_transitions: List[Transition]=None, entry: str=None, exit: str=None root_state: Box=None, insert=None, axis='', parallel_states=None):
        """
        Update the dimensions of the box. Some optional parameters can be added
        so that they are updated at the same time.
        Note that that the Box dimensions depend on these parameters.

        :param new_children: list of Boxes to add to the children list of this Box
        :param new_transitions: list of Transitions to add to the transitions list of this Box
        :param entry: entry text of this Box
        :param exit: exit text of this Box
        :param root_state: initial state of this Box
        :param insert: coordinates of the top left corner of this Box
        :param axis: the axis of the box; must be vertical or horizontal
        :param parallel_states: the list of parralel Boxes
        """
        if children != None: self._children += new_children
        if transitions != None: self._transitions += new_transitions
        if entry != None: self._entry = entry
        if exit != None: self._exit = exit
        if root_state != None: self._root_state = root_state
        if insert != None: self._x, self._y = insert
        if axis == 'vertical' or axis == 'horizontal': self._axis = axis
        if parallel_states != None: self._parallel_states = parallel_states

        self._width, self._height = compute_dimensions()


    def compute_dimensions(self):
        """
        Compute the dimensions of the box.

        :return: the width and the height of the box.
        """
        if self._parallel_states != []:
            p_len = 14 * char_width
        else:
            p_len = 0
        if self.entry != '':
            entry_len = (8 + len(self._entry)) * char_width
        else:
            entry_len = 0
        if axis == 'horizontal':
            width = max(sum(map(lambda x: x.width + space, self.children)) + space, space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = max(list(map(lambda x: x.height, self.children)) or [0]) + self.header + space
        else:
            width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space, space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = sum(map(lambda x: x.height + space, self.children)) + self.header
        return width, height


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
        return (self._x1, self._y1), (self._x1 + width, self._y2 + height)


    @property
    def shape(self):
        return self._shape



class InitBox(Box):


    def __init__(self, root_state):
        self._name = ''
        self._axis = None
        self._parallel_state = []
        self._children = []
        self._transitions = [Transition(source=self, target=root_state)]
        self._entry = ''
        self._exit = ''
        self._width, self._height = self.compute_dimensions()
        self._x, self._y = 0, 0
        self._shape = 'circle'


    def compute_dimensions(self):
        return radius*2, radius*2

class RootBox(Box):


    def __init__(self, statechart):
        self._name = statechart.name
        # first initializes all the boxes
        self._inner_states = [Boxes(name) for name in statechart.states()]
        self._statechart = statechart

        def init(state, horizontal_axis=True):
            # note : horizontal axis parameter allow the alternance of axis for the initialization
            if horizontal_axis:
                axis = 'horizontal'
            else:
                axis = 'vertical'
            box = next(x for x in self._inner_states if x.name==state.name)
            children_statechart = statechart.children_for(state.name)
            children = []
            for child in children_statechart:
                children += [init(statechart.state_for(child), not(horizontal_axis))]

            if isinstance(state, CompoundState) and state.initial is not None:
                root_state = next(x for x in children if x.name==state.initial)
                children = [InitBox(root_state), root_state] + list(filter(lambda x: x is not root_state, children))

            entry, exit = None, None
            if state.on_entry is not None: entry=state.on_entry
            if state.on_exit is not None: exit=state.on_exit
            if isinstance(state, OrthogonalState):
                for child in children:
                    child.update(parallel_states=list(filter(lambda x: x is not child, children)))
            box.update(children=children, entry=entry, exit=exit, root_state=root_state, axis=axis)

        root = init(statechart.root)
        self.children = [InitBox(root), root]

