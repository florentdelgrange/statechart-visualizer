import sys

import svgwriter
from sismic import io, model
from structures.box_elements import RootBox
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

file_name = sys.argv[1]

# load the yaml file in arg
with open(file_name, 'r') as stream:
    statechart = io.import_from_yaml(stream)
    assert isinstance(statechart, model.Statechart)

box = RootBox(statechart=statechart)
svgwriter.export(box)

directions = ['north', 'south', 'east', 'west']
print("you can move boxes here, ex : ")
print("move state1 south state2")

while True:
    instr = input(box.name + ' >> ').split()
    if instr[0] == 'exit' or instr[0] == 'quit':
        break
    if instr[0] == 'move':
        i = instr.index(next(filter(lambda x: x in directions, instr)))
        instr = ['move'] + [' '.join(instr[1: i])] + [instr[i]] + [' '.join(instr[i+1:])]
    if instr[0] == 'move' and len(instr) == 4:
        box1 = next(filter(lambda x: x.name == instr[1], box.inner_states), None)
        box2 = next(filter(lambda x: x.name == instr[3], box.inner_states), None)
        if box1 is not None and box2 is not None:
            box1.move_to(instr[2] + ' of', box2)
            svgwriter.export(box)
        else:
            print(instr[1] + ' or ' + instr[3] + ' is not in the main Box')
    else:
        print(box.name + " >> syntax error")
