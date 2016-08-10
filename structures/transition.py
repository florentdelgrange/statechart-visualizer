import math
from structures.box import space, get_coordinates


class Transition:
    def __init__(self, source: object, target: object, guard: str = '', event: str = '', action: str = ''):
        self.source = source
        self.target = target
        self.guard = guard
        self.event = event
        self.action = action
        self._x1, self._x2, self._y1, self._y2 = 0, 0, 0, 0
        self.polyline = []

    @property
    def coordinates(self):
        if self.polyline:
            return self.polyline[0], self.polyline[len(self.polyline) - 1]
        else:
            return (self._x1, self._y1), (self._x2, self._y2)

    @property
    def is_downward_transition(self):
        return self.source in self.target.ancestors

    def update_coordinates(self, start, end):
        (x1, y1), (x2, y2) = start, end
        self._x1, self._x2, self._y1, self._y2 = x1, x2, y1, y2

    def __str__(self):
        return "Transition : " + self.source.name + " -> " + self.target.name

    def __repr__(self):
        return self.__str__()


def zone_of(box1, box2, coordinates):
    """
    box2 is ___ of box1

    :param box1: the box reference
    :param box2: the box to determine the zone
    :param coordinates: the coordinates dictionary Dict[Box: (int, int)]
    :return: the area of box number 2 relative to the box number 1
    """
    (x1, y1), (x2, y2) = get_coordinates(box1, coordinates)
    (x3, y3), (x4, y4) = get_coordinates(box2, coordinates)
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


def acceptance_zone(box1, box2, axis, coordinates):
    """
    Check and compute if it is possible to draw a transition directly to another box
    with just one line
    """
    box1_coordinates = get_coordinates(box1, coordinates)
    box2_coordinates = get_coordinates(box2, coordinates)
    if axis == 'horizontal':
        x1, x2 = box1_coordinates[0][1], box1_coordinates[1][1]
        x3, x4 = box2_coordinates[0][1], box2_coordinates[1][1]
    else:
        x1, x2 = box1_coordinates[0][0], box1_coordinates[1][0]
        x3, x4 = box2_coordinates[0][0], box2_coordinates[1][0]
    if x1 < x2 and x3 < x4:
        x = [x1, x2, x3, x4]
        x.remove(min(x))
        x.remove(max(x))
        a, b = min(x), max(x)
        if (a >= x1 and b <= x2) and (a >= x3 and b <= x4):
            return a, b


def classic_arrow(transition, coordinates):
    """
    gives the polyline list for a classic transition arrow

    :param transition: the transition to determines the polyline
    :param coordinates: the coordinates of the boxes ; Dict[Box: (int, int)]
    :return: a list containing the points of the polyline
    """
    source = transition.source
    target = transition.target
    (x1, y1), (x2, y2) = get_coordinates(source, coordinates)
    (x3, y3), (x4, y4) = get_coordinates(target, coordinates)

    generate_list = lambda zone: list(
        filter(lambda t: zone_of(source, t.target, coordinates) == zone, source.transitions))

    if source.parent.axis == 'horizontal' and zone_of(source, target, coordinates) == 'northwest':
        l = generate_list('northwest')
        l.sort(key=lambda t: math.sqrt((x1 - get_coordinates(t.target, coordinates)[1][0]) ** 2 +
                                       (y1 - (
                                           get_coordinates(t.target, coordinates)[1][1] +
                                           get_coordinates(t.target, coordinates)[0][1]) / 2) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        w = x2 - x1
        x = x1 + w / (target_counter + 1) + target_index * w / (target_counter + 1)
        y = (y3 + y4) / 2
        return [(x, y1), (x, y), (x4, y)]
    elif source.parent.axis == 'horizontal' and zone_of(source, target, coordinates) == 'northeast':
        l = generate_list('northeast')
        l.sort(key=lambda t: math.sqrt((x2 - get_coordinates(t.target, coordinates)[0][0]) ** 2 +
                                       (y1 - (
                                           get_coordinates(t.target, coordinates)[1][1] +
                                           get_coordinates(t.target, coordinates)[0][1]) / 2) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        w = x2 - x1
        x = x2 - w / (target_counter + 1) - target_index * w / (target_counter + 1)
        y = (y3 + y4) / 2
        return [(x, y1), (x, y), (x3, y)]
    elif source.parent.axis == 'horizontal' and zone_of(source, target, coordinates) == 'southwest':
        l = generate_list('southwest')
        l.sort(key=lambda t: math.sqrt((x1 - get_coordinates(t.target, coordinates)[1][0]) ** 2 +
                                       (y2 - (
                                           get_coordinates(t.target, coordinates)[1][1] +
                                           get_coordinates(t.target, coordinates)[0][1]) / 2) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        w = x2 - x1
        x = x1 + w / (target_counter + 1) + target_index * w / (target_counter + 1)
        y = (y3 + y4) / 2
        return [(x, y2), (x, y), (x4, y)]
    elif source.parent.axis == 'horizontal' and zone_of(source, target, coordinates) == 'southeast':
        l = generate_list('southeast')
        l.sort(key=lambda t: math.sqrt((x2 - get_coordinates(t.target, coordinates)[0][0]) ** 2 +
                                       (y2 - (
                                           get_coordinates(t.target, coordinates)[1][1] +
                                           get_coordinates(t.target, coordinates)[0][1]) / 2) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        w = x2 - x1
        x = x2 - w / (target_counter + 1) - target_index * w / (target_counter + 1)
        y = (y3 + y4) / 2
        return [(x, y2), (x, y), (x3, y)]
    elif source.parent.axis == 'vertical' and zone_of(source, target, coordinates) == 'northwest':
        l = generate_list('northwest')
        l.sort(
            key=lambda t: math.sqrt((x1 - (
                get_coordinates(t.target, coordinates)[0][0] + get_coordinates(t.target, coordinates)[1][0]) / 2) ** 2 +
                                    (y1 - get_coordinates(t.target, coordinates)[1][1]) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        h = y2 - y1
        x = (x3 + x4) / 2
        y = y1 + h / (target_counter + 1) + target_index * h / (target_counter + 1)
        return [(x1, y), (x, y), (x, y4)]
    elif source.parent.axis == 'vertical' and zone_of(source, target, coordinates) == 'northeast':
        l = generate_list('northeast')
        l.sort(
            key=lambda t: math.sqrt((x2 - (
                get_coordinates(t.target, coordinates)[0][0] + get_coordinates(t.target, coordinates)[1][0]) / 2) ** 2 +
                                    (y1 - get_coordinates(t.target, coordinates)[1][1]) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        h = y2 - y1
        x = (x3 + x4) / 2
        y = y1 + h / (target_counter + 1) + target_index * h / (target_counter + 1)
        return [(x2, y), (x, y), (x, y4)]
    elif source.parent.axis == 'vertical' and zone_of(source, target, coordinates) == 'southwest':
        l = generate_list('southwest')
        l.sort(
            key=lambda t: math.sqrt((x1 - (
                get_coordinates(t.target, coordinates)[0][0] + get_coordinates(t.target, coordinates)[1][0]) / 2) ** 2 +
                                    (y2 - get_coordinates(t.target, coordinates)[0][1]) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        h = y2 - y1
        x = (x3 + x4) / 2
        y = y2 - h / (target_counter + 1) - target_index * h / (target_counter + 1)
        return [(x1, y), (x, y), (x, y3)]
    else:
        l = generate_list('southeast')
        l.sort(
            key=lambda t: math.sqrt((x2 - (
                get_coordinates(t.target, coordinates)[0][0] + get_coordinates(t.target, coordinates)[1][0]) / 2) ** 2 +
                                    (y2 - get_coordinates(t.target, coordinates)[0][1]) ** 2))
        target_counter = len(l)
        target_index = l.index(transition)
        h = y2 - y1
        x = (x3 + x4) / 2
        y = y2 - h / (target_counter + 1) - target_index * h / (target_counter + 1)
        return [(x2, y), (x, y), (x, y3)]


def update_transitions_coordinates(transitions, coordinates):
    for transition in transitions:
        # First check if it is possible to draw directly a transition in with one line.
        source = transition.source
        target = transition.target
        (x1, y1), (x2, y2) = get_coordinates(source, coordinates)
        (x3, y3), (x4, y4) = get_coordinates(target, coordinates)
        if source != target:
            def generate_list():
                l = list(filter(lambda t: t.target == target, source.transitions)) + list(
                    filter(lambda t: t.target == source, target.transitions))
                l.sort(key=lambda t: t.source.name + t.target.name)
                return l

            same_target_counter = len(generate_list())
            same_target_index = generate_list().index(transition)
            direction = zone_of(source, target, coordinates)
            acc = acceptance_zone(source, target, 'horizontal', coordinates)
            # check if it is possible to join directly the target with one line
            if acc is not None:
                transition.polyline = []
                h = acc[1] - acc[0]
                y = acc[0] + h / (same_target_counter + 1) + same_target_index * h / (same_target_counter + 1)
                if direction == 'southwest' or direction == 'northwest':
                    transition.update_coordinates(start=(x1, y), end=(x4, y))
                else:
                    transition.update_coordinates(start=(x2, y), end=(x3, y))
            # vertical test
            else:
                acc = acceptance_zone(source, target, 'vertical', coordinates)
                if acc is not None:
                    transition.polyline = []
                    w = acc[1] - acc[0]
                    x = acc[0] + w / (same_target_counter + 1) + same_target_index * w / (same_target_counter + 1)
                    if direction == 'northeast' or direction == 'northwest':
                        transition.update_coordinates(start=(x, y1), end=(x, y4))
                    else:
                        transition.update_coordinates(start=(x, y2), end=(x, y3))
                elif source in target.ancestors:
                    # inner transition
                    transition.polyline = []
                    if source.axis == 'horizontal':
                        if target.parent.children.index(target) == 0:
                            transition.update_coordinates(start=(x1, (y3 + y4) / 2), end=(x3, (y3 + y4) / 2))
                        elif target.parent.childrent.index(target) == len(target.parent.children) - 1:
                            transition.update_coordinates(start=(x2, (y3 + y4) / 2), end=(x4, (y3 + y4) / 2))
                        elif zone_of(source, target, coordinates) == 'northeast' or zone_of(source, target,
                                                                                            coordinates) == 'northwest':
                            transition.update_coordinates(start=((x3 + x4) / 2, y1), end=((x3 + x4) / 2, y3))
                        else:
                            transition.update_coordinates(start=((x3 + x4) / 2, y2), end=((x3 + x4) / 2, y4))
                    else:
                        if target.parent.children.index(target) == 0:
                            transition.update_coordinates(start=((x3 + x4) / 2, y1), end=((x3 + x4) / 2, y3))
                        elif target.parent.childrent.index(target) == len(target.parent.children) - 1:
                            transition.update_coordinates(start=((x3 + x4) / 2, y2), end=((x3 + x4) / 2, y4))
                        elif zone_of(source, target, coordinates) == 'northwest' or zone_of(source, target,
                                                                                            coordinates) == 'southwest':
                            transition.update_coordinates(start=(x1, (y3 + y4) / 2), end=(x3, (y3 + y4) / 2))
                        else:
                            transition.update_coordinates(start=(x2, (y3 + y4) / 2), end=(x4, (y3 + y4) / 2))
                else:
                    # classic arrow
                    transition.polyline = classic_arrow(transition, coordinates)
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
