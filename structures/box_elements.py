from structures.box import Box, radius
from structures.transition import Transition, update_transitions_coordinates
from sismic.model.elements import CompoundState, OrthogonalState


class InitBox(Box):
    def __init__(self, root_state):
        super().__init__(name='', axis=None)
        self._transitions = [Transition(source=self, target=root_state)]
        self._shape = 'circle'

    @property
    def dimensions(self):
        return radius * 2, radius * 2

    def __repr__(self):
        return "InitBox to " + self.transitions[0].target.name


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

            entry, exit = None, None
            if state.on_entry is not None:
                entry = state.on_entry
            if state.on_exit is not None:
                exit = state.on_exit

            # now check the transitions
            transitions = statechart.transitions_from(state.name)
            transitions = map(
                lambda t: Transition(source=box, target=next(x for x in self._inner_states if x.name == t.target)),
                transitions)

            if isinstance(state, OrthogonalState):
                for child in children:
                    for parallel_state in filter(lambda x: x is not child, children):
                        child.add_parallel_state(parallel_state)

            for child in children:
                box.add_child(child)
            for transition in transitions:
                box.add_transition(transition)

            box.entry = entry
            box.exit = exit
            box.axis = axis
            return box

        root = init(statechart.state_for(statechart.root), self.axis)
        self.add_child(InitBox(root))
        self.add_child(root)
        self.entry = statechart.preamble

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
        update_transitions_coordinates(transitions, self.coordinates)
        return transitions

    @property
    def constraints(self):
        def find_constraints(box, constraints=[]):
            c = []
            for child in box.children:
                c += find_constraints(child, child._constraints)
            return constraints + c

        constraints = find_constraints(self)
        return constraints

    @property
    def zone(self):
        return 'all'

    @property
    def inner_states(self):
        return self._inner_states

    def __repr__(self):
        return "Root Box: " + self.name
