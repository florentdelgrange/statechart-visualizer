# -*- coding: utf-8 -*-
import svgwrite, yaml

char_width = 15
char_height = 20
space = 20

class Box:


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
            p_len = 13 * char_width
        else:
            p_len = 0
        if horizontal_axis:
            self.width = max(sum(map(lambda x: x.width + space, self.children)) + space, space + p_len + char_width * len(self.name) + space)
            self.height = max(list(map(lambda x: x.height, self.children)) or [0]) + 2 * space + 2 * space + char_height
        else:
            self.width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space, space + p_len + char_width * len(self.name) + space)
            self.height = sum(map(lambda x: x.height + space, self.children)) + space + 2 * space + char_height


    def render(self, dwg, insert=(0,0)):
        normal_style = "font-size:20;font-family:Arial"
        italic_style = "font-size:20;font-family:Arial;font-style:oblique"
        x, y = insert
        # First draw the main box
        rect = dwg.rect(insert=(x, y), size=(self.width, self.height), fill=svgwrite.rgb(135,206,235), stroke='black', stroke_width=1)
        dwg.add(rect)
        # Now draw the name of the box
        w = x + self.width / 2
        h = y + space + char_height
        if self.parallel_state:
            w = w - (len(self.name) * char_width + 13 * char_width) / 2
            t1 = dwg.text("<<parallel state>>", insert=(w, h), style=italic_style)
            t2 = dwg.text(self.name, insert=(w + 13 * char_width, h), style=normal_style)
            dwg.add(t1)
            dwg.add(t2)
        else:
            w = w - (len(self.name) * char_width) / 2
            dwg.add(dwg.text(self.name, insert=(w, h), style=normal_style))
        # Finnaly draw the children following the axis (horizontal or vertical)
        if self.horizontal_axis:
            w = x
            h = y + self.height/2
            for child in self.children:
                w += space
                child.render(dwg, insert=(w, h - child.height / 2))
                w += child.width
        else:
            w = x + self.width/2
            h = y
            for child in self.children:
                h += space
                child.render(dwg, insert=(w - child.width/2, h))
                h += child.height


    def export(self):
        dwg = svgwrite.Drawing(self.name + ".svg")
        self.render(dwg)
        dwg.save()


with open("tests/elevator.yaml", 'r') as stream:
    try:
        b = Box(yaml.load(stream)['statechart'])
        b.export()
    except yaml.YAMLError as exc:
        print(exc)
