import structures.box
from structures.box import space, distance, zone


def compute_attraction_points(box, coordinates):
    x1, y1, x2, y2 = coordinates[box]
    y1 += box.header
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    return (mid_x, y1 + space / 2), (x2 - space / 2, mid_y), (mid_x, y2 - space / 2), (x1 + space / 2, mid_y)


def transitions_local_search(transitions, coordinates):
    nb_conflicts = lambda transition: len(transition.conflicts_with_boxes(coordinates)) + \
                                      len(transition.conflicts_with_transitions(transitions))

    for t in transitions:
        if (t.conflicts_with_transitions(transitions) \
                    or t.conflicts_with_boxes(coordinates)) \
                and t.source != t.target:
            lower_common_ancestor = structures.box.lower_common_ancestor(t.source, t.target)
            n, e, s, w = compute_attraction_points(lower_common_ancestor, coordinates)
            transition = t.copy()

            if zone(t.source, t.target, coordinates) == 'west':

                def finalization(points, transition):
                    x1, y1, x2, y2 = coordinates[transition.target]
                    mid = (x1 + x2) / 2
                    a1, a2 = points[-1]
                    b1, b2 = min([(mid, y1), (mid, y2)], key=lambda x: distance(points[-1], x))
                    points.pop()
                    points += [(b1, a2), (b1, b2)]
                    transition.polyline = points
                    if nb_conflicts(t) > nb_conflicts(transition):
                        t.polyline = points

                x1, y1, x2, y2 = coordinates[t.source]
                if x1 < n[0]:
                    for points in [[n], [s], [w]]:

                        if points[-1] == w:
                            points = [(x1, (y1 + y2) / 2)]
                            w1, w2 = w
                            points += [(w1, (y1 + y2) / 2)]
                            # points += [w]
                            old_points = points
                            for p in [n, s]:
                                points = old_points[:] + [p]
                                if points[-1] == n:
                                    if len(points) == 1:
                                        points = [((x1 + x2) / 2, y1)]
                                    else:
                                        points.pop()
                                    n1, n2 = n
                                    points += [(points[-1][0], n2)]
                                    points += [n]
                                elif points[-1] == s:
                                    if len(points) == 1:
                                        points = [((x1 + x2) / 2, y2)]
                                    else:
                                        points.pop()
                                    s1, s2 = s
                                    points += [(points[-1][0], s2)]
                                    points += [s]
                                finalization(points, transition)

                        elif points[-1] == n:
                            if len(points) == 1:
                                points = [((x1 + x2) / 2, y1)]
                            else:
                                points.pop()
                            n1, n2 = n
                            points += [(points[-1][0], n2)]
                            points += [n]

                        elif points[-1] == s:
                            if len(points) == 1:
                                points = [((x1 + x2) / 2, y2)]
                            else:
                                points.pop()
                            s1, s2 = s
                            points += [(points[-1][0], s2)]
                            points += [s]
                        finalization(points, transition)
                else:
                    for points in [[n], [s]]:
                        transition = t.copy()
                        if points[-1] == n:
                            points = [(x1, (y1 + y2) / 2)]
                            n1, n2 = n
                            points += [(x1, n2)]
                            points += [n]
                        elif points[-1] == s:
                            points = [(x2, (y1 + y2) / 2)]
                            s1, s2 = s
                            points += [(x2, s2)]
                            points += [s]
                        finalization(points, transition)

            elif zone(transition.source, transition.target, coordinates) == 'east':

                def finalization(points, transition):
                    x1, y1, x2, y2 = coordinates[transition.target]
                    mid = (x1 + x2) / 2
                    a1, a2 = points[-1]
                    b1, b2 = min([(mid, y1), (mid, y2)], key=lambda x: distance(points[-1], x))
                    points.pop()
                    points += [(b1, a2), (b1, b2)]
                    transition.polyline = points
                    if nb_conflicts(t) > nb_conflicts(transition):
                        t.polyline = points

                x1, y1, x2, y2 = coordinates[transition.source]
                if x1 > n[0]:
                    for points in [[n], [s], [e]]:
                        if points[-1] == e:
                            points = [(x2, (y1 + y2) / 2)]
                            e1, e2 = e
                            points += [(e1, (y1 + y2) / 2)]
                            # points += [e]
                            old_points = points
                            for p in [n, s]:
                                points = old_points[:] + [p]
                                if points[-1] == n:
                                    if len(points) == 1:
                                        points = [((x1 + x2) / 2, y1)]
                                    else:
                                        points.pop()
                                    n1, n2 = n
                                    points += [(points[-1][0], n2)]
                                    points += [n]
                                elif points[-1] == s:
                                    if len(points) == 1:
                                        points = [((x1 + x2) / 2, y2)]
                                    else:
                                        points.pop()
                                    s1, s2 = s
                                    points += [(points[-1][0], s2)]
                                    points += [s]
                                finalization(points, transition)

                        elif points[-1] == n:
                            if len(points) == 1:
                                points = [((x1 + x2) / 2, y1)]
                            else:
                                points.pop()
                            n1, n2 = n
                            points += [(points[-1][0], n2)]
                            points += [n]
                        elif points[-1] == s:
                            if len(points) == 1:
                                points = [((x1 + x2) / 2, y2)]
                            else:
                                points.pop()
                            s1, s2 = s
                            points += [(points[-1][0], s2)]
                            points += [s]
                        finalization(points, transition)

                else:
                    for points in [[n], [s]]:
                        if points[-1] == n:
                            points = [((x1 + x2) / 2, y1)]
                            n1, n2 = n
                            points += [((x1 + x2) / 2, n2)]
                            points += [n]
                        elif points[-1] == s:
                            points = [((x1 + x2) / 2, y2)]
                            s1, s2 = s
                            points += [((x1 + x2) / 2, s2)]
                            points += [s]
                        finalization(points, transition)

            elif zone(transition.source, transition.target, coordinates) == 'north':
                x1, y1, x2, y2 = coordinates[transition.source]

                def finalization(points, transition):
                    x1, y1, x2, y2 = coordinates[transition.target]
                    mid = (y1 + y2) / 2
                    a1, a2 = points[-1]
                    b1, b2 = min([(x1, mid), (x2, mid)], key=lambda x: distance(points[-1], x))
                    points.pop()
                    points += [(a1, b2), (b1, b2)]
                    transition.polyline = points
                    if nb_conflicts(t) > nb_conflicts(transition):
                        t.polyline = points

                if y1 < w[1]:
                    for points in [[n], [w], [e]]:
                        if points[-1] == n:
                            points = [((x1 + x2) / 2, y1)]
                            n1, n2 = n
                            points += [((x1 + x2) / 2, n2)]
                            # points += [n]
                            old_points = points
                            for p in [e, w]:
                                points = old_points[:] + [p]
                                if points[-1] == w:
                                    if len(points) == 1:
                                        points = [(x1, (y1 + y2) / 2)]
                                    else:
                                        points.pop()
                                    w1, w2 = w
                                    points += [(w1, points[-1][1])]
                                    points += [w]
                                elif points[-1] == e:
                                    if len(points) == 1:
                                        points = [(x2, (y1 + y2) / 2)]
                                    else:
                                        points.pop()
                                    e1, e2 = e
                                    points += [(e1, points[-1][1])]
                                    points += [e]
                                finalization(points, transition)

                        elif points[-1] == w:
                            if len(points) == 1:
                                points = [(x1, (y1 + y2) / 2)]
                            else:
                                points.pop()
                            w1, w2 = w
                            points += [(w1, points[-1][1])]
                            points += [w]
                        elif points[-1] == e:
                            if len(points) == 1:
                                points = [(x2, (y1 + y2) / 2)]
                            else:
                                points.pop()
                            e1, e2 = e
                            points += [(e1, points[-1][1])]
                            points += [e]
                        finalization(points, transition)

                else:
                    for points in [[w], [e]]:
                        if points[-1] == w:
                            points = [(x1, (y1 + y2) / 2)]
                            w1, w2 = w
                            points += [(w1, (y1 + y2) / 2)]
                            points += [w]
                        elif points[-1] == e:
                            points = [(x2, (y1 + y2) / 2)]
                            e1, e2 = e
                            points += [(e1, (y1 + y2) / 2)]
                            points += [e]
                        finalization(points, transition)

            else:
                x1, y1, x2, y2 = coordinates[transition.source]

                def finalization(points, transition):
                    x1, y1, x2, y2 = coordinates[transition.target]
                    mid = (y1 + y2) / 2
                    a1, a2 = points[-1]
                    b1, b2 = min([(x1, mid), (x2, mid)], key=lambda x: distance(points[-1], x))
                    points.pop()
                    points += [(a1, b2), (b1, b2)]
                    transition.polyline = points
                    if nb_conflicts(t) > nb_conflicts(transition):
                        t.polyline = points

                if y1 > w[1]:
                    for points in [[s], [w], [e]]:
                        if points[-1] == s:
                            points = [((x1 + x2) / 2, y2)]
                            s1, s2 = s
                            points += [((x1 + x2) / 2, s2)]
                            # points += [s]
                            old_points = points
                            for p in [e, w]:
                                points = old_points[:] + [p]
                                if points[-1] == w:
                                    if len(points) == 1:
                                        points = [(x1, (y1 + y2) / 2)]
                                    else:
                                        points.pop()
                                    w1, w2 = w
                                    points += [(w1, points[-1][1])]
                                    points += [w]
                                elif points[-1] == e:
                                    if len(points) == 1:
                                        points = [(x2, (y1 + y2) / 2)]
                                    else:
                                        points.pop()
                                    e1, e2 = e
                                    points += [(e1, points[-1][1])]
                                    points += [e]
                                finalization(points, transition)

                        elif points[-1] == w:
                            if len(points) == 1:
                                points = [(x1, (y1 + y2) / 2)]
                            else:
                                points.pop()
                            w1, w2 = w
                            points += [(w1, points[-1][1])]
                            points += [w]
                        elif points[-1] == e:
                            if len(points) == 1:
                                points = [(x2, (y1 + y2) / 2)]
                            else:
                                points.pop()
                            e1, e2 = e
                            points += [(e1, points[-1][1])]
                            points += [e]
                        finalization(points, transition)

                else:
                    for points in [[w], [e]]:
                        if points[-1] == w:
                            points = [(x1, (y1 + y2) / 2)]
                            w1, w2 = w
                            points += [(w1, (y1 + y2) / 2)]
                            points += [w]
                        elif points[-1] == e:
                            points = [(x2, (y1 + y2) / 2)]
                            e1, e2 = e
                            points += [(e1, (y1 + y2) / 2)]
                            points += [e]
                        finalization(points, transition)
