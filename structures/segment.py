class Segment:
    def __init__(self, point1: float, point2: float):
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


def combined_segments(segment1: Segment, segment2: Segment):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = segment1.p1, segment1.p2, segment2.p1, segment2.p2
    if x1 == x2 == x3 == x4:
        y1, y2 = tuple(sorted([y1, y2, y3, y4])[1:3])
        return Segment((x1, y1), (x2, y2))
    elif y1 == y2 == y3 == y4:
        x1, x2 = tuple(sorted([x1, x2, x3, x4])[1:3])
        return Segment((x1, y1), (x2, y2))
    else:
        return False


def intersect(segment1: Segment, segment2: Segment):
    a = segment1.slope
    m = segment2.slope
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = segment1.p1, segment1.p2, segment2.p1, segment2.p2
    if a == float('inf') and m == float('inf'):
        if segment1.line == segment2.line:
            return segment1.line, tuple(sorted([y1, y2, y3, y4])[1:3])
        else:
            return -float('inf'), float('inf')
    elif a == float('inf'):
        x, y = x1, segment2.line(x1)
        if (y1 <= y <= y2) or (y2 <= y <= y1):
            return x, y
        else:
            return -float('inf'), float('inf')
    elif m == float('inf'):
        x, y = x3, segment1.line(x3)
        if (y3 <= y <= y4) or (y4 <= y <= y3):
            return x, y
        else:
            return -float('inf'), float('inf')
    elif a == 0 and m == 0:
        combined = combined_segments(segment1, segment2)
        if combined:
            return (combined.p1, combined.p2), y1
        else:
            return -float('inf'), float('inf')
    else:
        x = ((y3 - m * x3) - (y1 - a * x1)) / (a - m)
        y = segment1.line(x)
        if (min(x1, x2, x3, x4) <= x <= max(x1, x2, x3, x4)) and (min(y1, y2, y3, y4) <= y <= max(y1, y2, y3, y4)):
            return x, y
        else:
            return -float('inf'), float('inf')
