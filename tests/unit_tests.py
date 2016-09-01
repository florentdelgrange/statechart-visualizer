from sismic import io
import sismic
import unittest

from structures.segment import Segment, intersect, combined_segments, get_box_segments
from constraint_solver import Constraint
from structures.box import Box
from structures.box_elements import RootBox, InitBox
from structures.transition import Transition


class TestSegment(unittest.TestCase):
    def test_simple_intersection(self):
        s1 = Segment((0, 2), (4, 2))
        s2 = Segment((0, 0), (4, 4))
        self.assertEqual(intersect(s1, s2), (2, 2))

    def test_orthogonal_intersection(self):
        s1 = Segment((0, 2), (4, 2))
        s2 = Segment((2, 4), (2, 0))
        self.assertEqual(intersect(s1, s2), (2, 2))

    def test_combined_segments(self):
        combined = combined_segments(Segment((1, 3), (1, 6)), Segment((1, 4), (1, 7)))
        p1, p2 = combined.p1, combined.p2
        self.assertEqual(p1, (1, 4))
        self.assertEqual(p2, (1, 6))
        combined = combined_segments(Segment((3, 1), (6, 1)), Segment((4, 1), (7, 1)))
        self.assertEqual(combined.p1, (4, 1))
        self.assertEqual(combined.p2, (6, 1))

    def test_Box(self):
        box = Box('random')
        coordinates = {box: (10, 10, 30, 40)}
        s1, s2, s3, s4 = get_box_segments(box, coordinates)
        self.assertEqual((s1.p1, s1.p2), ((10, 10), (10, 40)))
        self.assertEqual((s2.p1, s2.p2), ((10, 10), (30, 10)))
        self.assertEqual((s3.p1, s3.p2), ((30, 10), (30, 40)))
        self.assertEqual((s4.p1, s4.p2), ((10, 40), (30, 40)))


class TestTransitions(unittest.TestCase):
    def setUp(self):
        # The tests will be applied on the yaml file microwave
        with open("tests/microwave.yaml", 'r') as stream:
            statechart = io.import_from_yaml(stream)
            assert isinstance(statechart, sismic.model.Statechart)
        self.root_box = RootBox(statechart)
        self.states = {}
        for box in self.root_box.inner_states:
            self.states[box.name] = box

    def test_segment(self):
        for transition in self.root_box.transitions:
            segments = transition.segments
            for i in range(len(segments)):
                segment = segments[i]
                if transition.polyline:
                    self.assertEqual((segment.p1, segment.p2), (transition.polyline[i], transition.polyline[i + 1]))
                else:
                    self.assertEqual((segment.p1, segment.p2), transition.coordinates)

    def test_conflict(self):
        t1 = Transition(Box('b1'), Box('b2'))
        t2 = Transition(Box('b3'), Box('b4'))
        t3 = Transition(Box('b4'), Box('b5'))

        t1.polyline = [(0, 3), (6, 3), (6, 10)]
        t2.polyline = [(3, 8), (3, 5), (5, 5), (5, 0)]
        t3.update_coordinates(start=(6, 2), end=(6, 5))
        self.assertEqual(intersect(Segment((0, 3), (6, 3)), Segment((5, 0), (5, 5))), (5, 3))
        self.assertEqual([t2, t3], t1.conflicts_with_transitions([t2, t3]))


class TestBoxElements(unittest.TestCase):
    def setUp(self):
        # The tests will be applied on the yaml file microwave
        with open("tests/elevator.yaml", 'r') as stream:
            statechart = io.import_from_yaml(stream)
            assert isinstance(statechart, sismic.model.Statechart)
        self.root_box = RootBox(statechart)
        self.states = {}
        for box in self.root_box.inner_states:
            self.states[box.name] = box

    def test_zone(self):
        self.assertIn('south', self.root_box.zone(self.states['doorsOpen'], self.states['floorListener']))
        self.assertIn('east', self.root_box.zone(self.states['doorsClosed'], self.states['movingDown']))


class TestConstraints(unittest.TestCase):
    def setUp(self):
        # The tests will be applied on the yaml file microwave
        with open("tests/microwave.yaml", 'r') as stream:
            statechart = io.import_from_yaml(stream)
            assert isinstance(statechart, sismic.model.Statechart)
        self.root_box = RootBox(statechart)
        self.states = {}
        for box in self.root_box.inner_states:
            self.states[box.name] = box

    def test_random_constraints1(self):
        self.root_box.add_constraint(Constraint(self.states['program mode'], 'south', self.states['cooking mode']))
        self.root_box.add_constraint(Constraint(self.states['program mode'], 'west', self.states['cooking mode']))
        self.assertEqual({'south', 'west'},
                         set(self.root_box.zone(self.states['program mode'], self.states['cooking mode'])))

    def test_random_constraints2(self):
        self.root_box.add_constraint(
            Constraint(self.states['closed without item'], 'south', self.states['program mode']))
        self.assertIn('south', self.root_box.zone(self.states['closed without item'], self.states['closed with item']))

    def test_random_constraints3(self):
        self.root_box.add_constraint(Constraint(self.states['door opened'], 'south', self.states['door closed']))
        self.root_box.add_constraint(Constraint(self.states['door opened'], 'east', self.states['door closed']))
        self.assertEqual(
            {'south', 'east'}, set(self.root_box.zone(self.states['door opened'], self.states['door closed'])))

    def test_order_constraints(self):
        """
        test if the adding order of the constraints influences the coordinates of the statechart.
        """
        with open("tests/elevator.yaml", 'r') as stream:
            statechart = io.import_from_yaml(stream)
            assert isinstance(statechart, sismic.model.Statechart)
        root_box = RootBox(statechart)
        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'south', root_box.get_box_by_name('doorsOpen')))
        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'west', root_box.get_box_by_name('moving')))
        root_box.transitions
        coordinates1 = root_box.coordinates
        set1 = root_box.constraints.copy()

        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'north', root_box.get_box_by_name('doorsOpen')))
        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'east', root_box.get_box_by_name('moving')))
        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'west', root_box.get_box_by_name('moving')))
        root_box.add_constraint(
            Constraint(root_box.get_box_by_name('doorsClosed'), 'south', root_box.get_box_by_name('doorsOpen')))
        root_box.transitions
        coordinates2 = root_box.coordinates
        set2 = root_box.constraints.copy()

        self.assertEqual(set1, set2)
        for key in coordinates1.keys():
            self.assertEqual(coordinates1[key], coordinates2[key],
                             msg='the positions of ' + str(key) + ' are not equals')


if __name__ == '__main__':
    unittest.main()
