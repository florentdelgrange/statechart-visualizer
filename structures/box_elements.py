from structures.box import Box, radius, space
from structures.transition import Transition
from sismic.model.elements import CompoundState, OrthogonalState


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

        root = init(statechart.state_for(statechart.root), self._axis)
        self.update(new_children=[InitBox(root), root], entry=statechart.preamble)

    def update(self, new_children=None, new_transitions=None, entry=None,
               exit=None,
               root_state=None,
               axis='', parallel_states=None):
        super().update(new_children, new_transitions, entry, exit, root_state, axis, parallel_states)
        self.update_coordinates()

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

    def update_coordinates(self):
        super().update_coordinates()

        # now update the transitions coordinates
        def acceptance_zone(box1, box2, axis):
            """
            Check and compute if it is possible to draw a transition directly to another box
            with just one line
            """
            if axis == 'horizontal':
                x1, x2 = box1.coordinates[0][1], box1.coordinates[1][1]
                x3, x4 = box2.coordinates[0][1], box2.coordinates[1][1]
            else:
                x1, x2 = box1.coordinates[0][0], box1.coordinates[1][0]
                x3, x4 = box2.coordinates[0][0], box2.coordinates[1][0]
            if x1 < x2 and x3 < x4:
                x = [x1, x2, x3, x4]
                x.remove(min(x))
                x.remove(max(x))
                a, b = min(x), max(x)
                if (a >= x1 and b <= x2) and (a >= x3 and b <= x4):
                    return a, b

        for transition in self.transitions:
            # First check if it is possible to draw directly a transition in with one line.
            source = transition.source
            target = transition.target
            (x1, y1), (x2, y2) = source.coordinates
            (x3, y3), (x4, y4) = target.coordinates
            if source != target:
                direction = source.zone_of(target)
                acc = acceptance_zone(source, target, 'horizontal')
                if acc is not None:
                    y = (acc[0] + acc[1]) / 2
                    if direction == 'southwest' or direction == 'northwest':
                        transition.update_coordinates(start=(x1, y), end=(x4, y))
                    else:
                        transition.update_coordinates(start=(x2, y), end=(x3, y))
                # vertical test
                else:
                    acc = acceptance_zone(source, target, 'vertical')
                    if acc is not None:
                        x = (acc[0] + acc[1]) / 2
                        if direction == 'northeast' or direction == 'northwest':
                            transition.update_coordinates(start=(x, y1), end=(x, y4))
                        else:
                            transition.update_coordinates(start=(x, y2), end=(x, y3))
            else:
                if source.zone == 'north':
                    transition.polyline = [((x1 + x2) / 2, y1), ((x1 + x2) / 2, y1 - space),
                                           (x1 - space, y1 - space), (x1 - space, (y1 + y2) / 2),
                                           (x1, (y1 + y2) / 2)]
                elif source.zone == 'south':
                    transition.polyline = [((x1 + x2) / 2, y2), ((x1 + x2) / 2, y2 + space),
                                           (x2 + space, y2 + space),
                                           (x2 + space, (y1 + y2) / 2), (x2, (y1 + y2) / 2)]
                elif source.zone == 'west':
                    transition.polyline = [(x1, (y1 + y2) / 2), (x1 - space, (y1 + y2) / 2),
                                           (x1 - space, y1 - space), ((x1 + x2) / 2, y1 - space), ((x1 + x2) / 2, y1)]
                else:
                    transition.polyline = [(x2, (y1 + y2) / 2), (x2 + space, (y1 + y2) / 2),
                                           (x2 + space, y2 + space), ((x1 + x2) / 2, y2 + space),
                                           ((x1 + x2) / 2, y2)]

    @property
    def zone(self):
        return 'all'
