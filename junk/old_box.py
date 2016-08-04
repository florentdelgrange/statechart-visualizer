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
        self.transitions = yaml_dict.get('transitions', [])
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
        self.coordinates = (0, 0, self.width, self.height) # render() will update the children coordinates


    def render(self, insert=(0,0)):
        """
        Computes the positions of the inner Boxes and their names and puts it in the Drawing object.

        :param insert: upper left corner position of the box
        :return: the box as a group of svg shapes
        """
        normal_style = "font-size:25;font-family:Arial"
        italic_style = "font-size:25;font-family:Arial;font-style:oblique"
        bold_style = "font-size:25;font-weight:bold;font-family:Arial"
        x, y = insert
        # update the coordinates following the insert position /!\ side effect
        self.coordinates = (x, y, x+self.width, y+self.height)
        g = svgwrite.container.Group()

        # First draw the main box
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
                g.add(child.render(insert=(w, h - child.height/2)))
                w += child.width
        else:
            w = x + self.width/2
            h = y + self.header - space
            for child in self.children:
                h += space
                g.add(child.render(insert=(w - child.width/2, h)))
                h += child.height

        return g


    def export(self):
        """
        Creates the svg file that represents the Box.
        """
        dwg = svgwrite.Drawing(self.name + ".svg", size=(self.width, self.height))
        dwg.add(self.render())
        self.draw_transitions(dwg, self)
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


    def draw_transitions(self, dwg, main_box):
        def acceptance_zone(x1, x2, x3, x4):
            if x1 < x2 and x3 < x4:
                x = [x1, x2, x3, x4]
                x.remove(min(x))
                x.remove(max(x))
                a, b = min(x), max(x)
                if (a >= x1 and b <= x2) and (a >= x3 and b <= x4):
                    return a, b

        def zone(box1, box2):
            """box2 is ___ of the box1"""
            x1, y1, x2, y2 = box1.coordinates
            x3, y3, x4, y4 = box2.coordinates
            x1, y1 = ((x1 + x2) / 2, (y1 + y2) / 2)
            x2, y2 = ((x3 + x4) / 2, (y3 + y4) / 2)
            if x1 <= x2 and y1 >= y2:
                return 'northeast'
            elif x1 >= x2 and y1 >= y2:
                return 'northwest'
            elif x1 >= x2 and y1 <= y2:
                return 'southwest'
            else:
                return 'southeast'

        for t in self.transitions:
            targeted_box = main_box.find(t['target'])
            if targeted_box != self:
                x1, y1, x2, y2 = self.coordinates
                x3, y3, x4, y4 = targeted_box.coordinates
                direction = zone(self, targeted_box)
                acc = acceptance_zone(y1, y2, y3, y4)
                # horizontal test
                if acc is not None:
                    y = (acc[0] + acc[1])/2
                    #draw the arrow
                    if direction=='southwest' or direction=='northwest':
                        dwg.add(dwg.line(start=(x1, y), end=(x4, y), stroke='black', stroke_width=1))
                    else:
                        dwg.add(dwg.line(start=(x2, y), end=(x3, y), stroke='black', stroke_width=1))
                # vertical test
                else:
                    acc = acceptance_zone(x1, x2, x3, x4)
                    if acc is not None:
                        print(self.name, targeted_box.name)
                        x = (acc[0] + acc[1])/2
                        #draw the arrow
                        if direction=='northeast' or direction=='northwest':
                            dwg.add(dwg.line(start=(x, y1), end=(x, y4), stroke='black', stroke_width=1))
                        else:
                            dwg.add(dwg.line(start=(x, y2), end=(x, y3), stroke='black', stroke_width=1))
        for child in self.children:
            child.draw_transitions(dwg, self)


    def find(self, state_name):
        """
        Finds a Box with the name in parameter in this Box and returns it.

        :param state_name: the name of the wanted state Box.
        :return: The Box with this name.
        """
        if self.name == state_name:
            return self
        else:
            for child in self.children:
                x = child.find(state_name)
                if x != None:
                    return x
            return None


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
        self.coordinates = (0, 0, self.height, self.width)


    def compute_dimensions(self):
        return radius*2, radius*2


    def render(self, insert=(0,0)):
        x, y = insert
        return svgwrite.shapes.Circle(center=(x+radius,y+radius), r=radius)

    def draw_transitions(self, dwg, main_box):
        super().draw_transitions(dwg, main_box)
