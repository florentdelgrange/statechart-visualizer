import sys

import svgwriter
from sismic import io, model
from structures.box_elements import RootBox

file_name = sys.argv[1]

# elevator test
with open("tests/" + file_name + ".yaml", 'r') as stream:
    statechart = io.import_from_yaml(stream)
    assert isinstance(statechart, model.Statechart)

box = RootBox(statechart=statechart)
svgwriter.export(box)

while True:
    print(box.name + ' >> give an instruction')
    instr = input(box.name + ' >> ').split()
    if instr[0] == 'exit':
        break
    elif instr[0] == 'move' and len(instr) == 6:
        box1 = next(filter(lambda x: x.name == instr[1], box.inner_states), None)
        box2 = next(filter(lambda x: x.name == instr[5], box.inner_states), None)
        if box1 is not None and box2 is not None:
            box1.move_to(instr[3] + ' ' + instr[4], box2)
            svgwriter.export(box)
        else:
            print(instr[1] + ' or ' + instr[5] + ' is not in the main Box')
    else:
        print(box.name + " >> syntax error")



# microwave test
#with open("tests/microwave.yaml", 'r') as stream:
#    statechart = io.import_from_yaml(stream)
#    assert isinstance(statechart, model.Statechart)
#
#svgwriter.export(RootBox(statechart=statechart))
