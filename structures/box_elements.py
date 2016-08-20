from structures.box import Box, radius
from structures.transition import Transition, update_transitions_coordinates
import sismic
from sismic.model.elements import CompoundState, OrthogonalState


class InitBox(Box):
    """
    This box is the black circle that indicate the init state.
    It always has a transition to this state.
    """

    def __init__(self, init_state):
        super().__init__(name='', axis=None)
        self._transitions = [Transition(source=self, target=init_state)]
        self._shape = 'circle'

    @property
    def dimensions(self):
        return radius * 2, radius * 2

    def __repr__(self):
        return "InitBox to " + self.transitions[0].target.name


class RootBox(Box):
    """
    This Box is the main box that will contain all the boxes.
    It intends to represent a statechart.

    :param statechart: it is an instance of a statechart object from sismic.
    """

    def __init__(self, statechart: sismic.model.Statechart):
        super().__init__(name=statechart.name, axis='horizontal')

        self._inner_states = [Box(name) for name in statechart.states]

        def init(state, axis):
            # alternate the axis for the children
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
        self.transitions  # initialize the transitions coordinates

    @property
    def transitions(self):
        """
        Compute their positions and update them.
        :return: all the transitions in the statechart.
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
        """
        :return: all the constraints on the Boxes situated in this Root Box.
        """

        def find_constraints(box, constraints=[]):
            c = []
            for child in box.children:
                c += find_constraints(child, child._constraints)
            return constraints + c

        constraints = find_constraints(self)
        return constraints

    @property
    def inner_states(self):
        """
        :return: all the Boxes that represents a state of the statechart.
        """
        return self._inner_states

    def get_box_by_name(self, state_name: str):
        """
        Get the instance of the box with the state name entered in parameter.
        :param state_name: name of the Box to find (must be in the statechart).
        :return: the instance of the box with the name entered in parameter.
        """
        return next(filter(lambda box: box.name == state_name, self._inner_states))

    def zone(self, box1, box2):
        """
        Get the zone of the box1 compared to the box2.
        example : if zone(box1, box2) returns ['south', 'east'] it means that box1 is south east of box2.
        :param box1: the first box (must be in the inner boxes)
        :param box2: the second box (must be in the inner boxes)
        :return: a list containing precisely the zone of the box1 compared to the box2.
        """
        coordinates = self.coordinates
        x1, y1, x2, y2 = coordinates[box1]
        x3, y3, x4, y4 = coordinates[box2]
        x1, y1 = (x1 + x2) / 2., (y1 + y2) / 2.
        x2, y2 = (x3 + x4) / 2., (y3 + y4) / 2.
        zone = []
        if x1 < x2:
            zone.append('west')
        elif x1 > x2:
            zone.append('east')
        if y1 < y2:
            zone.append('north')
        elif y1 > y2:
            zone.append('south')
        return zone

    def __repr__(self):
        return "Root Box: " + self.name
