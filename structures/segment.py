from structures.box import Box, distance
from typing import Dict, Tuple


class Segment:
    def __init__(self, point1: Tuple[float, float], point2: Tuple[float, float]):
        self._p1 = point1
        self._p2 = point2

    @property
    def p1(self):
        return self._p1

    @property
    def p2(self):
        return self._p2

    @property
    def slope(self):
        """
        :return: the slope of the segment
        """
        x1, y1 = self._p1
        x2, y2 = self._p2
        if x1 == x2:
            return float('inf')
        else:
            return (y2 - y1) / (x2 - x1)

    @property
    def is_horizontal(self):
        x1, y1 = self._p1
        x2, y2 = self._p2
        return y1 == y2

    @property
    def is_vertical(self):
        x1, y1 = self._p1
        x2, y2 = self._p2
        return x1 == x2

    @property
    def line(self):
        """
        warning : convention : if slope is inf then return the abscissa
        :return: the line on which is the segment.
        """
        x1, y1 = self._p1
        if self.slope != float('inf'):
            return lambda x: self.slope * x + (y1 - self.slope * x1)
        else:
            return x1

    @property
    def length(self):
        return distance(self.p1, self.p2)

    def __repr__(self):
        return 'Segment ' + self._p1.__repr__() + ", " + self._p2.__repr__()


def combined_segments(segment1: Segment, segment2: Segment):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = segment1.p1, segment1.p2, segment2.p1, segment2.p2
    if x1 == x2 == x3 == x4:
        ya, yb = tuple(sorted([y1, y2, y3, y4])[1:3])
        if (min(y1, y2) <= ya <= yb <= max(y1, y2)) or (min(y3, y4) <= ya <= yb <= max(y3, y4)):
            return Segment((x1, ya), (x2, yb))
    elif y1 == y2 == y3 == y4:
        xa, xb = tuple(sorted([x1, x2, x3, x4])[1:3])
        if (min(x1, x2) <= xa <= xb <= max(x1, x2)) or (min(x3, x4) <= xa <= xb <= max(x3, x4)):
            return Segment((xa, y1), (xb, y2))
    else:
        return False


def intersect(segment1: Segment, segment2: Segment):
    a = segment1.slope
    m = segment2.slope
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = segment1.p1, segment1.p2, segment2.p1, segment2.p2
    if (a == float('inf') and m == float('inf')) or (a == 0 and m == 0):
        return combined_segments(segment1, segment2)
    elif a == float('inf'):
        x, y = x1, segment2.line(x1)
        if ((y1 <= y <= y2) or (y2 <= y <= y1)) and ((x3 <= x1 <= x4) or (x3 >= x1 >= x4)):
            return x, y
        else:
            return False
    elif m == float('inf'):
        x, y = x3, segment1.line(x3)
        if ((y3 <= y <= y4) or (y4 <= y <= y3)) and ((x1 <= x3 <= x2) or (x1 >= x3 >= x2)):
            return x, y
        else:
            return False
    else:
        x = ((y3 - m * x3) - (y1 - a * x1)) / (a - m)
        y = segment1.line(x)
        if (min(x1, x2, x3, x4) <= x <= max(x1, x2, x3, x4)) and (min(y1, y2, y3, y4) <= y <= max(y1, y2, y3, y4)):
            return x, y
        else:
            return False


def get_box_segments(box: Box, coordinates: Dict[Box, Tuple[float, float, float, float]]) -> \
        (Segment, Segment, Segment, Segment):
    x1, y1, x2, y2 = coordinates[box]
    return Segment((x1, y1), (x1, y2)), Segment((x1, y1), (x2, y1)), \
           Segment((x2, y1), (x2, y2)), Segment((x1, y2), (x2, y2))
