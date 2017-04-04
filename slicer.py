#!/usr/bin/env python3
"""
Slicer for 3D object stored in a STL binary file, slices are saved on svg files
"""

from struct import unpack
from os import system

from itertools import compress, cycle
from bisect import bisect_left

from math import pi, cos

import argparse

from utils import grouper, cosangle, get_contours, intersection

def main():
    """
    Main function, get arguments and call the slice function
    """

    parser = argparse.ArgumentParser(description="slice an STL binary file",\
        epilog=("slice given stl file into SLICES horizontal slices. writes"+\
                " a numbered output svg file for each slice (bottom to top)."))

    parser.add_argument("stl_file", help="name of stl file to slice (a binary stl file)")

    parser.add_argument("-s", "--slices", help="how many slices you want (default 10)", \
        type=int, default=10)

    parser.add_argument("-a", "--axe", help="change the direction of slices: Z:0, Y:1, X:2 "+\
        "(defult Z)", type=int, choices=[0, 1, 2], default=0)

    parser.add_argument("--simplify", \
        help="simplify the figure by removing points forming more than angle (in deg)", \
        type=float, default=None)

    args = parser.parse_args()

    if not args.simplify:
        args.simplify = 180

    slicer(args.stl_file, args.slices, args.simplify, args.axe)


def slicer(filename, slices, max_angle=None, axe=0):
    """
    Call functions to get the 3D model and call the slicer on this model
    `filename` is the STR binary filename
    `slices` is the number of level to make
    `max_angle` is the amgle (in degree) for simplification, None is no simplification
    """

    model = stl_file_reader(filename, axe)

    slice_3d_model(model, slices, max_angle)

def stl_file_reader(name, axe=0):
    """
    Return a 3D model from the stl file `filename`
    This file needs to be in binary stl format
    The `axe` argument is for the direction of slicing (Z: 0, Y: 1, X: 2)

    The return model is composed of 3 list of X, Y and Z coordinates
    """
    model = [None]*3
    with open(name, 'rb') as fichier:
        # Header
        header = fichier.read(80)
        print("Header file : ", header)

        # number of faces
        nombre_faces = int.from_bytes(fichier.read(4), byteorder='little')
        print("The model contains", nombre_faces, "faces")

        # get all faces data
        face_data = fichier.read(50*nombre_faces)
        valeurs = unpack("=" + "12fh"*nombre_faces, face_data)

        # filter only useful values
        valeurs = tuple(compress(valeurs, cycle([0, 0, 0, # normal veector
                                                 1, 1, 1, # point 1
                                                 1, 1, 1, # point 2
                                                 1, 1, 1, # point 3
                                                 0])))    # unspecified unsigned int
        model[(0+axe)%3] = valeurs[0::3]
        model[(1+axe)%3] = valeurs[1::3]
        model[(2+axe)%3] = valeurs[2::3]

        return model

def generate_tranches(model, zlist):
    """
    Return a list of slice on level into `zlist`
    `zlist` needs to be sorted
    """
    slices = [[] for _ in zlist]

    # pylint: disable=C0103
    # p1, p2, p3 are points
    for p1, p2, p3 in grouper(zip(*model), 3):
        minz, maxz = min(p1[2], p2[2], p3[2]), max(p1[2], p2[2], p3[2])
        start, end = bisect_left(zlist, minz), bisect_left(zlist, maxz)
        for level in range(start, end):
            Z = zlist[level]
            segment = intersection(p1, p2, p3, Z)
            if segment:
                slices[level].append(segment)
    return slices

def slice_3d_model(model, slices, max_angle=180):
    """
    Cut the 3D model in slices
    This function generate output files with create_svg
    """
    xmin, xmax, ymin, ymax, zmin, zmax = min(model[0]), max(model[0]),\
                                         min(model[1]), max(model[1]),\
                                         min(model[2]), max(model[2])
    pas = (zmax-zmin)/(slices+1)
    zstart = zmin+pas/2
    zlist = [zstart + a*pas for a in range(slices)]

    for index, segments in enumerate(generate_tranches(model, zlist)):
        if max_angle != 180:
            segments = simplifier_tranche(segments, max_angle)

        create_svg("couche_%s.svg"%(index), segments, [xmin, ymin, xmax-xmin, ymax-ymin])

        system("tycat couche_%s.svg"%(index))


def simplifier_tranche(tranche, angle_max=180):
    """
    Makes simplification on a slice
    It is done by removing points making an angle more important than `angle_max`
    """
    contours = get_contours(tranche)
    new_contours = []
    angle_max = angle_max*pi/180
    cos_angle_max = cos(angle_max)
    # pylint: disable=C0103
    # i1, i2, p1, p2, p0 are points and indexes
    for contour in contours:
        a_supprimer = [False]*len(contour)
        iter_contour = enumerate(contour)
        _, p0 = next(iter_contour)
        i1, p1 = next(iter_contour)
        for i2, p2 in iter_contour:
            if cosangle(p0, p1, p2) < cos_angle_max:
                a_supprimer[i1] = True
                p1, i1 = p2, i2
            else:
                p0, _, p1, i1 = p1, i1, p2, i2
        new_contours.append([pt for i, pt in enumerate(contour) if not a_supprimer[i]])

    segments = []
    for contour in new_contours:
        for p1, p2 in zip(contour, contour[1:]):
            segments.append((p1, p2))

    print('réduction de du nombre de traits de',\
          int(100*(1-len(segments)/len(tranche))), '%')

    return segments


def create_svg(filename, segments, rect):
    """
    Create an svg file `filename` with the `segments` given, `rect` is the area where all segments are
    """
    with open(filename, "w") as fichier:
        fichier.write(("<svg height=\"500\" width=\"500\" viewBox=\"%s %s %s %s\" " + \
                       "xmlns=\"http://www.w3.org/2000/svg\">\n") % \
                       (rect[0], rect[1], rect[2], rect[3]))
        # pylint: disable=C0103
        # p1, p2 are points
        for p1, p2 in segments:
            fichier.write(('<line x1="%s" y1="%s" x2="%s" y2="%s"' +
                           ' style="stroke:#F00;stroke-width:%s" />\n') % \
                           (p1[0], p1[1], p2[0], p2[1], rect[2]/500))

        fichier.write("</svg>\n")

if __name__ == "__main__":
    main()
