#!/usr/bin/env python
# coding=utf-8

import os, sys

from Bio import PDB
import numpy

from config import *

pjoin = os.path.join

def pexatom(tmp_path, pdb_in, phi_in):
    phi_path = pjoin(tmp_path, CONFIG_PQR_PATH, CONFIG_PHI_PATH)
    dirc = pjoin(phi_path, "pdb/")
    if not os.path.exists( dirc ):
        os.mkdir( dirc )

    parser = PDB.PDBParser()
    writer = PDB.PDBIO()

    structure = parser.get_structure(pdb_in, pdb_in)
    atoms = structure.get_atoms()

    phi_f = open(phi_in, 'r')
    phi = []

    output_pdb = pjoin(dirc, phi_in.split(os.sep)[-1].strip(".phi") + ".pdb")

    for l in phi_f:
        l = l.strip().split(',')
        if float(l[3]) >= 0.0:
            data = dict(coord=numpy.array([l[0], l[1], l[2]], dtype=numpy.float32),
                        ep=float(l[3]))
        else:
            data = dict(coord=numpy.array([l[0], l[1], l[2]], dtype=numpy.float32),
                        ep=0.0)

        phi.append(data)

    phi_f.close()

    for a in atoms:
        for p in phi:
            if (a.get_coord()[0] == p['coord'][0] and a.get_coord()[1] == p['coord'][1] and a.get_coord()[2] == p['coord'][2]):
                a.set_bfactor(p['ep'])
                phi.remove(p)
                break
            else:
                a.set_bfactor(0.0)

    writer.set_structure(structure)
    writer.save(output_pdb)

    return output_pdb

