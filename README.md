# Statechart Visualizer
Display pretty statecharts following a description of the system under the form of a yaml file or a Sismic object.

## Introduction
This module for python 3 is initially planned to display statecharts from Sismic, but you can
easily use it to create directly your own statecharts and display them. The purpose of the
project is to display readable and understandable statecharts, and add visual constraints of some states (e.g., *state 1 must be left to state2*).

You can then export your statechart as svg file.

## Requirements
You will find here the list of modules needed.

- [Sismic](https://github.com/AlexandreDecan/sismic)
- [Cassowary](https://github.com/pybee/cassowary)
- [svgwrite](https://github.com/biazzotto/svgwrite)

## Interactive mode
You can test the module interactively from a simple yaml file (representing
a statechart) as follows:
```
python main.py <your-file.yaml>
```

Each time you run this command, it will create (or update) an svg file with the name of the statechart.
For more informations about things this program is able to do, simply type `help` while 
main.py is launched.
Note that the syntax of the yaml file to represent a statechart is specified in the [sismic documentation](http://sismic.readthedocs.io/en/master/format.html#defining-statecharts-in-yaml).

## Usage

Assuming you have created a statechart object with Sismic, you can create a svg file from this statechart as follows.

1. Create a RootBox with this statechart.
2. Export this RootBox to a svg file.

```python
from structures.box_elements import RootBox
box = RootBox(statechart)
svgwriter.export(box)
```
By using the constraint solver, the boxes representing the states will be arranged
following the text on the transtitions and alternatively following a horizontal axis and a vertical axis.
After that, the transitions will be drawn minimizing intersections with boxes, text and other transitions.

If the arrangement doesn't suit you, you can manually add constraints on the boxes with the method `box.add_constraint`.
If you don't want to display the entire text on transitions, you can hide a part of it (e.g., you can hide all the actions with 
`box._hide_action_on_transitions`).

## Example

Assuming we want to display the statechart in [tests/elevator.yaml](https://github.com/radioGiorgio/statechart-visualizer/blob/master/tests/elevator.yaml), we do:
```python
import svgwriter
from sismic import io, model
from structures.box_elements import RootBox

with open('tests/elevator.yaml', 'r') as stream:
        statechart = io.import_from_yaml(stream)
        assert isinstance(statechart, model.Statechart)

box = RootBox(statechart=statechart)
svgwriter.export(box, file_name='examples/Elevator')
```

![alt text](https://cdn.rawgit.com/radioGiorgio/statechart-visualizer/master/examples/Elevator_simple.svg)

Now, we additionally want to have another arrangement of the boxes.
Let us assume that we want:
- movingDown at north of doorsClosed,
- doorsClosed at north-east of doorsOpen,
- floorListener at south of movingElevator,

and we don't want to display the actions.

```python
get = lambda x: box.get_box_by_name(x)
box.add_constraint(Constraint(get('moving'), 'north', get('doorsClosed')))
box.add_constraint(Constraint(get('doorsClosed'), 'north', get('doorsOpen')))
box.add_constraint(Constraint(get('doorsClosed'), 'east', get('doorsOpen')))
box.add_constraint(Constraint(get('floorListener'), 'south', get('movingElevator')))
box.hide_action_on_transitions()
svgwriter.export(box, file_name='examples/Elevator')
```

![alt text](https://cdn.rawgit.com/radioGiorgio/statechart-visualizer/master/examples/Elevator.svg)

## Known issues
- Risk of text overlapping when more than 2 transitions have the same incident state and the same state of arrival.
