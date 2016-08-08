from structures.box import Box, radius
from structures.transition import Transition, update_transitions_coordinates
from sismic.model.elements import CompoundState, OrthogonalState


class InitBox(Box):
    def __init__(self, root_state):
        super().__init__(name='', axis=None)
        self._transitions = [Transition(source=self, target=root_state)]
        self._width, self._height = self.dimensions
        self._shape = 'circle'

    @property
    def dimensions(self):
        return radius * 2, radius * 2


class RootBox(Box):
    def __init__(self, statechart):
        super().__init__(name=statechart.name, axis='vertical')

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

            # now check the transitions
            transitions = statechart.transitions_from(state.name)
            if transitions:
                transitions = map(
                    lambda t: Transition(source=box, target=next(x for x in self._inner_states if x.name == t.target)),
                    transitions)
            else:
                transitions = None

            if isinstance(state, OrthogonalState):
                for child in children:
                    child.update(parallel_states=list(filter(lambda x: x is not child, children)))
            box.update(new_children=children, new_transitions=transitions, entry=entry, exit=exit,
                       root_state=root_state, axis=axis)
            return box

        root = init(statechart.state_for(statechart.root), self.axis)
        self.update(new_children=[InitBox(root), root], entry=statechart.preamble)

    def update(self, new_children=None, new_transitions=None, entry=None,
               exit=None,
               root_state=None,
               axis='', parallel_states=None):
        super().update(new_children, new_transitions, entry, exit, root_state, axis, parallel_states)
        update_transitions_coordinates(self.transitions, self.coordinates())

    @property
    def transitions(self):
        """
        Return all the transitions in this box
        Compute their positions and update them
        """

        def find_transitions(box, transitions=[]):
            t = []
            for child in box.children:
                t += find_transitions(child, child.transitions)
            return transitions + t

        transitions = find_transitions(self)
        return transitions

    @property
    def zone(self):
        return 'all'
