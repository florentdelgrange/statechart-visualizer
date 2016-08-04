import svgwrite
from structures.box import Box, radius, char_width

normal_style = "font-size:25;font-family:Arial"
italic_style = "font-size:25;font-family:Arial;font-style:oblique"
bold_style = "font-size:25;font-weight:bold;font-family:Arial"


def get_shape(box: Box):
    """
    get the svg object associated with the shape of the Box

    :param box: the box to render
    :return: the svg object related
    """
    x, y = box.coordinates
    if box.shape == 'rectangle':
        return svgwrite.shapes.Rect(insert=(x, y), size=(box.width, box.height),
                                    fill=svgwrite.rgb(135, 206, 235),
                                    stroke='black', stroke_width=1)
    elif box.shape == 'circle':
        return svgwrite.shapes.Circle(center=(x+radius, y+radius), r=radius)
    else:
        return svgwrite.shapes.Rect(insert=(x, y), size=(box.width, box.height),
                                    fill="#044B94", fill_opacity="0.4")


def render(box: Box):
    """
    creates the shapes of the boxes and puts it in a svg group

    :param box: the box to render
    :return: the group that contains the box and their inner boxes
    """
    g = svgwrite.container.Group()

    # First draw the main box
    shape = get_shape(box)
    g.add(shape)

    # Now draw the name of the box
    w, h = box.get_text_position_of('name')
    if box.parallel_state:
        t1 = svgwrite.text.Text("<<parallel>>", insert=(w, h), style=italic_style, textLength=13 * char_width)
        t2 = svgwrite.text.Text(box.name, insert=(w + 14 * char_width, h), style=bold_style,
                                textLength=len(box.name) * char_width)
        g.add(t1)
        g.add(t2)
    else:
        g.add(svgwrite.text.Text(box.name, insert=(w, h), style=bold_style, textLength=len(box.name) * char_width))

    # This draws the 'on entry' zone
    w, h = box.get_text_position_of('entry')
    if box.entry != '':
        g.add(svgwrite.text.Text("entry / ", insert=(w, h), style=italic_style, textLength=8 * char_width))
        g.add(svgwrite.text.Text(box.preamble, insert=(w + 9 * char_width, h), style=normal_style,
                                 textLength=len(box.preamble) * char_width))

    # TODO: exit zone

    # Finally draw the children following the axis (horizontal or vertical)
    for child in box.children:
        g.add(render(child))

    return g


def export(box: Box):
    """
    Creates the svg file that represents the Box

    :param box: the box that will be on the svg file
    """
    dwg = svgwrite.Drawing(box.name + ".svg", size=(box.width, box.height))
    dwg.add(render(box))
    dwg.save()
