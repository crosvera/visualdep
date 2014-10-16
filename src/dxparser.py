#!/usr/bin/env python
# coding=utf-8
#
# Carlos Ríos V. <crosvera@gmail.com>

import numpy as np
import re

import pdb

def read_dx(dxfile):
    with open(dxfile, "rb") as dxf:
        dxc = np.array(dxf.readlines())

    #Regex to detect float numbers
    float_regex = """
        [-+]? # optional sign
        (?:
            (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \./ ) # 1. 12. 123. etc 1 12 123 etc
        )
        (?: [Ee] [+-]? \d+ ) ? # followed by optional exponent part if desired
    """
    f = re.compile(float_regex, re.VERBOSE)
    f2 = re.compile("."+float_regex, re.VERBOSE)
    #Regex to get the grid spacing hx, hy, hz
    n = re.compile("object 1 class gridpositions counts (\d+) (\d+) (\d+)")
    #Regex to get the total number of points
    q = re.compile("object 3 class array type double rank 0 items (\d+) data follows")

    deltas = []
    dflag = 0
    #values = np.array([], dtype=np.dtype(float))
    values = []
    for l in dxc:
        l = l.strip()
        
        if f2.match(l): #Starts with a float? so it's a value field
            for v in l.split():
                #values = np.append(values, np.float(v))
                values.append(np.float(v))
        elif l[0] == "#": #A comment
            continue
        elif l.startswith("object 1"):
            nn = n.match(l).groups()
            nx = int(nn[0])
            ny = int(nn[1])
            nz = int(nn[2])
        elif l.startswith("origin"):
            oo = f.findall(l)
            xmin = np.float(oo[0])
            ymin = np.float(oo[1])
            zmin = np.float(oo[2])
        elif l.startswith("delta"):
            dflag += 1
            deltas.append(l)
            if dflag == 3:
                hx = np.float(deltas[0].split()[1])
                hy = np.float(deltas[1].split()[2])
                hz = np.float(deltas[2].split()[3])
        #elif l.startswith("object 2"):
        #    continue
        #elif l.startswith("object 3"):
        #    t = int(q.match(l).group(1))
        elif l.startswith("attribute"):
            break

    if len(values) != nx*ny*nz:
        raise Exception("Something went wrong, the total values captured (%d) are different from the expected one (%d)." % (len(values), nx*ny*nz))

    return {"points": (nx,ny,nz), "origin": (xmin,ymin,zmin), "spacing": (hx,hy,hz), "values": np.array(values)}


