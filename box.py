# -*- coding: utf-8 -*-
import svgwrite, yaml

char_width = 10
char_height = 20
space = 20
radius = space

class Box:
    """
    A Box displays a state.

    :param yaml_dict: This is the data structure (Dict) obtained from a yaml statechart
    :param horizontal_axis: The inner states will be arranged on a horizontal axis if this parameter is True, on a vertical axis otherwise.
    :param parallel_state: True if the state is parralel to another
    """


    def __init__(self, yaml_dict, horizontal_axis=True, parallel_state=False, preamble=''):
        self.name = yaml_dict['name']
        self.children = []
        self.horizontal_axis = horizontal_axis
        self.parallel_state = parallel_state
        self.transitions = []
        self.preamble = preamble
        self.header = 2 * space + char_height
        if self.preamble:
            self.header += space + char_height

        if 'root state' in yaml_dict:
            child = Box(yaml_dict['root state'], not(horizontal_axis), preamble=yaml_dict.get('preamble', '').replace("\n", " ; "))
            self.children += [RootBox(child.name), child]

        if 'parallel states' in yaml_dict:
            states_dict = yaml_dict['parallel states']
            brothers = []
            brothers += [Box(x, not(horizontal_axis), parallel_state=True, preamble=x.get('on entry', '')) for x in states_dict]
            self.children += brothers
            if horizontal_axis:
                height = max(map(lambda x: x.height, brothers))
                for x in brothers:
                    x.height = height
            else:
                width = max(map(lambda x: x.width, brothers))
                for x in brothers:
                    x.width = width

        if 'states' in yaml_dict:
            self.children += [Box(x, not(horizontal_axis), preamble=x.get('on entry', '')) for x in yaml_dict['states']]

        if self.parallel_state:
            # we consider that a parallel state always have a initial state
            init = next(x for x in self.children if x.name==yaml_dict['initial'])
            self.children = [RootBox(init.name), init] + list(filter(lambda x: x is not init, self.children))

        self.width, self.height = self.compute_dimensions()


    def render(self, dwg, insert=(0,0)):
        """
        Computes the positions of the inner Boxes and their names and puts it in the Drawing object.

        :param dwg: Drawing object obtained from svgwrite
        :param insert: upper left corner position of the box
        """
        normal_style = "font-size:25;font-family:Arial"
        italic_style = "font-size:25;font-family:Arial;font-style:oblique"
        bold_style = "font-size:25;font-weight:bold;font-family:Arial"
        x, y = insert
        # First draw the main box
        g = svgwrite.container.Group()
        dwg.add(g)
        rect = svgwrite.shapes.Rect(insert=(x, y), size=(self.width, self.height), fill=svgwrite.rgb(135,206,235), stroke='black', stroke_width=1)
        g.add(rect)

        # Now draw the name of the box
        w = x + self.width / 2
        h = y + space + char_height
        if self.parallel_state:
            w = w - (len(self.name) * char_width + 13 * char_width) / 2
            t1 = svgwrite.text.Text("<<parallel>>", insert=(w, h), style=italic_style, textLength=13*char_width)
            t2 = svgwrite.text.Text(self.name, insert=(w + 14 * char_width, h), style=bold_style, textLength=len(self.name)*char_width)
            g.add(t1)
            g.add(t2)
        else:
            w = w - (len(self.name) * char_width) / 2
            g.add(svgwrite.text.Text(self.name, insert=(w, h), style=bold_style, textLength=len(self.name) * char_width))

        # This draws the 'on entry' zone
        if self.preamble != '':
            w = x + space
            h += space + char_height
            g.add(svgwrite.text.Text("entry / ", insert=(w, h), style=italic_style, textLength=8*char_width))
            g.add(svgwrite.text.Text(self.preamble, insert=(w + 9 * char_width, h), style=normal_style, textLength=len(self.preamble)*char_width))

        # Finnaly draw the children following the axis (horizontal or vertical)
        if self.horizontal_axis:
            w = x
            h = y + (self.height + self.header) / 2
            for child in self.children:
                w += space
                child.render(g, insert=(w, h - child.height/2))
                w += child.width
        else:
            w = x + self.width/2
            h = y + self.header - space
            for child in self.children:
                h += space
                child.render(g, insert=(w - child.width/2, h))
                h += child.height


    def export(self):
        """
        Creates the svg file that represents the Box.
        """
        dwg = svgwrite.Drawing(self.name + ".svg", size=(self.width, self.height))
        self.render(dwg)
        dwg.save()


    def compute_dimensions(self):
        """
        Compute the dimensions of the box.
        :return: the width and the height of the box.
        """
        if self.parallel_state:
            p_len = 14 * char_width
        else:
            p_len = 0
        if self.preamble != '':
            entry_len = (8 + len(self.preamble)) * char_width
        else:
            entry_len = 0
        if self.horizontal_axis:
            width = max(sum(map(lambda x: x.width + space, self.children)) + space, space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = max(list(map(lambda x: x.height, self.children)) or [0]) + self.header + space
        else:
            width = max(max(list(map(lambda x: x.width, self.children)) or [0]) + 2 * space, space + p_len + char_width * len(self.name) + space, 2 * space + entry_len)
            height = sum(map(lambda x: x.height + space, self.children)) + self.header
        return width, height


class RootBox(Box):


    def __init__(self, root_state):
        self.name = ''
        self.children = []
        self.horizontal_axis = False
        self.parallel_state = False
        self.transitions = [{'target': root_state, 'guard': ''}]
        self.preamble = ''
        self.header = 0
        self.width, self.height = self.compute_dimensions()


    def compute_dimensions(self):
        return radius*2, radius*2


    def render(self, dwg, insert=(0,0)):
        x, y = insert
        dwg.add(svgwrite.shapes.Circle(center=(x+radius,y+radius), r=radius))
