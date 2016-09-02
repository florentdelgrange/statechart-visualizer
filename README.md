# Statechart Visualizer
Display statecharts properly from a yaml or a statechart object from Sismic.

## Introduction
This module is initially planned to display the statecharts from sismic but you can
easily use it to create directly your own statecharts and display them. The purpose of the
project is display statecharts properly and add constraints (like *state 1 must be left to state2*)
on the states.

You can then export your statechart as svg file.

## Requirements
You will find here the list of modules needed to use it :

- [Sismic](https://github.com/AlexandreDecan/sismic)
- [Cassowary](https://github.com/pybee/cassowary)
- [svgwrite](https://github.com/biazzotto/svgwrite)

## Interactive mode
You can test the module interactively from a simple yaml file (representing
a statechart) following this way :
```
main.py <your-file.yaml>
```

Each action will create (or update) a svg file with the name of the statechart.
For more informations about the actions you are able to do with this program, type simply `help` while 
main.py is launched.
Note that the syntax of the yaml file to represent a statechart is specified in the [sismic documentation](http://sismic.readthedocs.io/en/master/format.html#defining-statecharts-in-yaml).

## Usage

Let assume that you have created a statechart object with Sismic. You can create a svg file from this statechart.

1. Create a RootBox with this statechart.
2. Export this RootBox to a svg file.

```
from structures.box_elements import RootBox
box = RootBox(statechart)
svgwriter.export(box)
```
Using the constraint solver (using the cassowary alogorithm), the boxes representing the states will be arranged
following the text on the transtitions and alternatively following a horizontal axis and a vertical axis.
If the arrangement doesn't suit you, you can add mannualy constraint on the boxes with the method `box.add_constraint`.
If you don't want to display the entire text on transitions, you can hide a part of it, for example the action with 
`box._hide_action_on_transitions`.

## Example

Suppose we want to display the statechart in [tests/elevator.yaml](https://github.com/radioGiorgio/statechart-visualizer/blob/master/tests/elevator.yaml).
First, we do :
```
import svgwriter
from sismic import io, model
from structures.box_elements import RootBox

with open('tests/elevator.yaml', 'r') as stream:
        statechart = io.import_from_yaml(stream)
        assert isinstance(statechart, model.Statechart)

box = RootBox(statechart=statechart)
svgwriter.export(box, file_name='examples/Elevator')
```

![alt text](https://raw.githubusercontent.com/radioGiorgio/statechart-visualizer/master/examples/Elevator.svg)

But we want to have another arrangement of the boxes.
Suppose that we want that :
- movingDown at north of doorsClosed
- doorsClosed at north-east of doorsOpen
- floorListener at south of movingElevator
and we don't want to display the actions.

```
get = lambda x: box.get_box_by_name(x)
box.add_constraint(Constraint(get('moving'), 'north', get('doorsClosed')))
box.add_constraint(Constraint(get('doorsClosed'), 'north', get('doorsOpen')))
box.add_constraint(Constraint(get('doorsClosed'), 'east', get('doorsOpen')))
box.add_constraint(Constraint(get('floorListener'), 'south', get('movingElevator')))
box.hide_action_on_transitions()
svgwriter.export(box, file_name='examples/Elevator')
```

![alt text](http://radioGiorgio.github.io/statechart-visualizer/blob/master/examples/Elevator.svg)
