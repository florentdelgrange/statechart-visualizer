import svgwrite
from structures.box import Box, radius, char_width, char_height
from structures.box_elements import RootBox

normal_style = "font-size:25;font-family:Arial"
italic_style = "font-size:25;font-family:Arial;font-style:oblique"
bold_style = "font-size:25;font-weight:bold;font-family:Arial"


def get_shape(box: Box, insert):
    """
    get the svg object associated with the shape of the Box

    :param insert: the top left corner coordinates of the box
    :param box: the box to render
    :return: the svg object related
    """
    x, y = insert
    if box.shape == 'rectangle':
        return svgwrite.shapes.Rect(insert=(x, y), rx=15, ry=15, size=(box.width, box.height),
                                    fill=svgwrite.rgb(135, 206, 235),
                                    stroke='black', stroke_width=2)
    elif box.shape == 'circle':
        return svgwrite.shapes.Circle(center=(x + radius, y + radius), r=radius)


def render_box(box: Box, coordinates):
    """
    creates the shapes of the boxes and puts it in a svg group

    :param coordinates: the coordinates dict of all boxes
    :param box: the box to render
    :return: the group that contains the box and their inner boxes
    """
    g = svgwrite.container.Group()

    # First draw the main box
    x1, y1, x2, y2 = coordinates[box]
    insert = x1, y1
    shape = get_shape(box, insert)
    if shape is not None:
        g.add(shape)

    # Now draw the name of the box
    w, h = box.name_position(insert)
    if box.parallel_states:
        t1 = svgwrite.text.Text("<<parallel>>", insert=(w, h), style=italic_style, textLength=13 * char_width)
        t2 = svgwrite.text.Text(box.name, insert=(w + 14 * char_width, h), style=bold_style,
                                textLength=len(box.name) * char_width)
        g.add(t1)
        g.add(t2)
    else:
        g.add(svgwrite.text.Text(box.name, insert=(w, h), style=bold_style, textLength=len(box.name) * char_width))

    # This draws the 'on entry' zone
    w, h = box.entry_position(insert)
    if box.entry != '':
        if not isinstance(box, RootBox):
            g.add(svgwrite.text.Text("entry / ", insert=(w, h), style=italic_style, textLength=8 * char_width))
            init_len = 9 * char_width
        else:
            init_len = 0
        i = 0
        for entry in box.entry.split('\n'):
            g.add(svgwrite.text.Text(entry, insert=(w + init_len, h + char_height * i), style=normal_style,
                                     textLength=len(entry) * char_width))
            i += 1

    w, h = box.exit_position(insert)
    if box.exit != '':
        g.add(svgwrite.text.Text("exit / ", insert=(w, h), style=italic_style, textLength=8 * char_width))
        i = 0
        for exit in box.exit.split('\n'):
            g.add(svgwrite.text.Text(exit, insert=(w + 9 * char_width, h + char_height * i), style=normal_style,
                                     textLength=len(exit) * char_width))
            i += 1
    # TODO : do zone

    # Finally draw the children following the axis (horizontal or vertical)
    for child in box.children:
        g.add(render_box(child, coordinates))

    return g


def render_transitions(transitions):
    lines = []
    for t in transitions:
        if t.polyline:
            lines += [
                svgwrite.shapes.Polyline(points=t.polyline, stroke='black', stroke_width=1, fill="none",
                                         marker_end="url(#arrow)")]
        else:
            (x1, y1), (x2, y2) = t.coordinates
            lines += [svgwrite.shapes.Line(start=(x1, y1), end=(x2, y2), stroke='black', stroke_width=1,
                                           marker_end="url(#arrow)")]
    return lines


def export(box: Box):
    """
    Creates the svg file that represents the Box

    :param box: the box that will be on the svg file
    """
    dwg = svgwrite.Drawing(box.name + ".svg", size=(box.width, box.height))
    dwg.add(render_box(box, box.coordinates))
    marker = svgwrite.container.Marker(insert=(8, 3), orient='auto', markerWidth=30, markerHeight=20,
                                       id="arrow")
    path = svgwrite.path.Path(d="M0,0 L0,6 L9,3 z")
    marker.add(path)
    dwg.defs.add(marker)
    for transition in render_transitions(box.transitions):
        dwg.add(transition)
    dwg.save()
