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
