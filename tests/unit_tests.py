from sismic import io
import sismic
import unittest
from structures.segment import Segment, intersect, combined_segments
from constraint_solver import Constraint
from structures.box_elements import RootBox


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
        p = intersect(Segment((1, 3), (1, 6)), Segment((1, 4), (1, 7)))
        self.assertEqual(p, (1, (4, 6)))
        combined = combined_segments(Segment((3, 1), (6, 1)), Segment((4, 1), (7, 1)))
        self.assertEqual(combined.p1, (4, 1))
        self.assertEqual(combined.p2, (6, 1))


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


if __name__ == '__main__':
    unittest.main()
