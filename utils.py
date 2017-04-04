"""
Utilities functions
"""

from itertools import zip_longest
from math import sqrt


def grouper(iterable, size, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    ex: grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)] * size
    return zip_longest(*args, fillvalue=fillvalue)


def intersection(p1, p2, p3, Z):
    # pylint: disable=C0103
    # p1, p2, p3 are points
    """
    Return the intersection between the triangle (p1, p2, p3) and the level `Z`
    None if no intersection
    """
    d1, d2, d3 = p1[2]-Z, p2[2]-Z, p3[2]-Z
    s1, s2, s3 = d1 < 0, d2 < 0, d3 < 0
    U = [None]*6

    if s1 != s2:
        U[:3] = [(d2*c1 - d1*c2)/(d2-d1) for c1, c2 in zip(p1, p2)]
        if s1 != s3:
            U[3:6] = [(d1*c3 - d3*c1)/(d1-d3) for c3, c1 in zip(p3, p1)]
        else:
            U[3:6] = [(d2*c3 - d3*c2)/(d2-d3) for c3, c2 in zip(p3, p2)]
    elif s3 != s1:
        U[:3] = [(d3*c1 - d1*c3)/(d3-d1) for c1, c3 in zip(p1, p3)]

        U[3:6] = [(d2*c3 - d3*c2)/(d2-d3) for c3, c2 in zip(p3, p2)]
    else:
        return None
    return [tuple(U[:3]), tuple(U[3:6])]


def cosangle(p0, p1, p2):
    # pylint: disable=C0103
    # p0, p1, p2 are points, tuples of 3 coordonate
    """
    Return the cosinus of the angle between p0, p1, p2 
    """
    if not(p0 and p1 and p2):
        return 0

    a2 = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    b2 = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    c2 = (p0[0]-p2[0])**2 + (p0[1]-p2[1])**2

    num = (a2 + b2 - c2)
    det = (2*sqrt(a2*b2))

    if det == 0:
        return 0

    cosa = num/det
    # print(cosa)
    if abs(cosa) > 1:
        return 1
    return cosa


def get_contours(segments):
    """
    Return the points paths of contours of the figure
    points needs to be compared with == operator
    ex: segments = [(p0, p1), (p2, p1), (p3, p4)]
        contours => [(p0, p1, p2), (p3, p4)]
    """
    def fusionner_contour(contour1, contour2):
        """
        Make the fusion between paths `contour1` and `contour2`
        """
        contour = []
        ch2_traites = [False]*len(contour2)
        for ch1 in contour1:
            chemin = ch1
            for index, ch2 in enumerate(contour2):
                if ch2_traites[index]:
                    continue
                if ch1[-1] == ch2[0]:
                    chemin.extend(ch2[1:])
                    ch2_traites[index] = True
                    break
                elif ch1[-1] == ch2[-1]:
                    ch2.reverse()
                    chemin.extend(ch2[1:])
                    ch2_traites[index] = True
                    break
                elif ch1[0] == ch2[0]:
                    chemin = ch2[:]
                    chemin.reverse()
                    chemin.extend(ch1[1:])
                    ch2_traites[index] = True
                    break
                elif ch1[0] == ch2[-1]:
                    chemin = ch2[:]
                    chemin.extend(ch1[1:])
                    ch2_traites[index] = True
                    break
            contour.append(chemin)

        for index, ch2 in enumerate(contour2):
            if not ch2_traites[index]:
                contour.append(ch2)
        return contour

    def decoupage_rec(_segments):
        """
        Recursive function for create a path from all segments
        """
        len_s = len(_segments)
        if len_s <= 1:
            return _segments
        milieu = len_s // 2
        ch1 = decoupage_rec(_segments[:milieu])
        ch2 = decoupage_rec(_segments[milieu:])

        return fusionner_contour(ch1, ch2)

    return decoupage_rec(segments)
