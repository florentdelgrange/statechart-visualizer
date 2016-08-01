# -*- coding: utf-8 -*-
import svgwrite, yaml

char_width = 15
char_height = 20
space = 20

class Box:
    """
    A Box displays a state.

    :param yaml_dict: This is the data structure (Dict) obtained from a yaml statechart
    :param horizontal_axis: The inner states will be arranged on a horizontal axis if this parameter is True, on a vertical axis otherwise.
    :param parallel_state: True if the state is parralel to another
    """


    def __init__(self, yaml_dict, horizontal_axis=True, parallel_state=False):
        self.name = yaml_dict['name']
        self.children = []
        self.horizontal_axis = horizontal_axis
        self.parallel_state = parallel_state

        self.preamble = yaml_dict.get('preamble', '')
        if 'root state' in yaml_dict:
            self.children += [Box(yaml_dict['root state'], not(horizontal_axis))]
        if 'parallel states' in yaml_dict:
            self.children += [Box(x, not(horizontal_axis), parallel_state=True) for x in yaml_dict['parallel states']]
        if 'states' in yaml_dict:
            self.children += [Box(x, not(horizontal_axis)) for x in yaml_dict['states']]
        if parallel_state:
            p_len = 14 * char_width
        else:
            p_len = 0
        if horizontal_axis:
            self.width = max(sum(map(lambda x: x.width + space, self.children)) + space, space + p_len + char_width * len(self.name) + space)
            self.height = max(list(map(lambda x: x.height, self.children)) or [0]) + 3 * space + char_height
        else:
            self.width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space, space + p_len + char_width * len(self.name) + space)
            self.height = sum(map(lambda x: x.height + space, self.children)) + space + 2 * space + char_height


    def render(self, dwg, insert=(0,0)):
        """
        Computes the positions of the inner Boxes and their names and puts it in the Drawing object.

        :param dwg: Drawing object obtained from svgwrite
        :param insert: upper left corner position of the box
        """
        normal_style = "font-size:25;font-family:Arial"
        italic_style = "font-size:25;font-family:Arial;font-style:oblique"
        x, y = insert
        # First draw the main box
        rect = dwg.rect(insert=(x, y), size=(self.width, self.height), fill=svgwrite.rgb(135,206,235), stroke='black', stroke_width=1)
        dwg.add(rect)
        # Now draw the name of the box
        w = x + self.width / 2
        h = y + space + char_height
        if self.parallel_state:
            w = w - (len(self.name) * char_width + 13 * char_width) / 2
            t1 = dwg.text("<<parallel>>", insert=(w, h), style=italic_style, textLength=13*char_width)
            t2 = dwg.text(self.name, insert=(w + 14 * char_width, h), style=normal_style, textLength=len(self.name)*char_width)
            dwg.add(t1)
            dwg.add(t2)
        else:
            w = w - (len(self.name) * char_width) / 2
            dwg.add(dwg.text(self.name, insert=(w, h), style=normal_style, textLength=len(self.name) * char_width))
        # Finnaly draw the children following the axis (horizontal or vertical)
        if self.horizontal_axis:
            w = x
            h = y + 2 * space + char_height + (self.height - 2 * space - char_height) / 2
            for child in self.children:
                w += space
                child.render(dwg, insert=(w, h - child.height/2))
                w += child.width
        else:
            w = x + self.width/2
            h = y + space + char_height
            for child in self.children:
                h += space
                child.render(dwg, insert=(w - child.width/2, h))
                h += child.height 


    def export(self):
        """
        Creates the svg file that represents the Box.
        """
        dwg = svgwrite.Drawing(self.name + ".svg")
        self.render(dwg)
        dwg.save()


#test
with open("tests/elevator.yaml", 'r') as stream:
    try:
        b = Box(yaml.load(stream)['statechart'])
        b.export()
    except yaml.YAMLError as exc:
        print(exc)
