import sys

import svgwriter
from sismic import io, model
from structures.box_elements import RootBox
from constraint_solver import Constraint
import readline
import rlcompleter
import atexit
import os

# tab completion
readline.parse_and_bind('tab: complete')
# history file
histfile = os.path.join(os.environ['HOME'], '.pythonhistory')
try:
    readline.read_history_file(histfile)
except IOError:
    pass
atexit.register(readline.write_history_file, histfile)
del os, histfile, readline, rlcompleter

# example of use : python main.py tests/elevator.yaml
file_name = sys.argv[1]

# load the yaml file in arg
with open(file_name, 'r') as stream:
    statechart = io.import_from_yaml(stream)
    assert isinstance(statechart, model.Statechart)

box = RootBox(statechart=statechart)
svgwriter.export(box)

directions = ['north', 'south', 'east', 'west']
print("type help to display the commands")

while True:
    instr = input(box.name + ' >> ').split()
    if instr:
        if instr[0] == 'exit' or instr[0] == 'quit':
            break
        if instr[0] == 'move' or instr[0] == 'constraint':
            i = instr.index(next(filter(lambda x: x in directions, instr), instr[0]))
            if i != 0:
                instr = [instr[0]] + [' '.join(instr[1: i])] + [instr[i]] + [' '.join(instr[i + 1:])]
            else:
                instr = ['error']
        if instr[0] == 'move' and len(instr) == 4:
            box1 = next(filter(lambda x: x.name == instr[1], box.inner_states), None)
            box2 = next(filter(lambda x: x.name == instr[3], box.inner_states), None)
            if box1 is not None and box2 is not None:
                box1.move_to(instr[2] + ' of', box2)
                svgwriter.export(box)
            else:
                print(instr[1] + ' or ' + instr[3] + ' is not in the main Box')
        elif instr[0] == 'constraint' and len(instr) == 4:
            box1 = next(filter(lambda x: x.name == instr[1], box.inner_states), None)
            box2 = next(filter(lambda x: x.name == instr[3], box.inner_states), None)
            if box1 is not None and box2 is not None:
                box.add_constraint(Constraint(box1, instr[2], box2))
                svgwriter.export(box)
                print("Constraints : ", box.constraints)
            else:
                print(instr[1] + ' or ' + instr[3] + ' is not in the main Box')

        elif instr[0] == 'hide' and len(instr) == 2:
            {
                'guard': box.hide_guard_on_transitions,
                'event': box.hide_event_on_transitions,
                'action': box.hide_action_on_transitions
            }.get(instr[1], lambda: print('Syntax error : you must specify event, guard or action to hide'))()
            svgwriter.export(box)

        elif instr[0] == 'show' and len(instr) == 2:
            {
                'guard': box.show_guard_on_transitions,
                'event': box.show_event_on_transitions,
                'action': box.show_action_on_transitions
            }.get(instr[1], lambda: print('Syntax error : you must specify event, guard or action to show'))()
            svgwriter.export(box)

        elif instr[0] == 'help':
            print("1. move box1 direction box2")
            print("    - box1 : the name of the box to move")
            print("    - direction : the direction of the box1 compared to the box2")
            print("      values : {'north' | 'south' | 'east' | 'west'}")
            print("    - box2 : the name of the reference box")
            print("The box1 will be moved at the direction of the box2")
            print("Example : move state1 north state2")
            print()
            print("2. constraint box1 direction box2")
            print("    - box1 : the name of the box1")
            print("    - direction : the direction of the box1 compared to the box2")
            print("      values : {'north' | 'south' | 'east' | 'west'}")
            print("    - box2 : the name of the box2")
            print("The constraint Constraint(box1, direction, box2) will be added")
            print("Example : constraint state1 east state2")
            print()
            print("3. hide transition_text")
            print("    - transition_text: the part of the transition text to hide")
            print("      values : {'guard', 'event', 'action'}")
            print("The part of the transition text in parameter will be hidden.")
            print("Example : hide event")
            print()
            print("4. show transition_text")
            print("    - transition_text: the part of the transition text to display")
            print("      values : {'guard', 'event', 'action'}")
            print("The part of the previously hidden transition text in parameter will be displayed")
            print("Example : show event")
            print()
            print("5. quit | exit")
            print("leave the program")
        else:
            print(box.name + " >> syntax error")
