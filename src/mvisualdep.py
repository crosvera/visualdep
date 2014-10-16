#!/usr/bin/env python
# coding=utf-8
#
# mVisualDEP - VisualDEP Command Line Version for multiple comparisons
#
# Carlos Ríos V. <crosvera@gmail.com>
#

import __main__
__main__.pymol_argv = ["pymol", "-qc"] # Quiet and no GUI

import sys, os

import pymol
pymol.finish_launching()
import numpy as np

from visualdep import *



if __name__ == "__main__":
    #structures = sys.argv[1:]
    #pdb_dir = "/home/crosvera/projects/Mlike/visualdep/pdbs/domains"
    pdb_dir = "/home/crosvera/projects/Mlike/visualdep/pdbs"
    structures = ["2VQP_A.pdb", "1ES6_A.pdb", "2YKD_A.pdb", "3TCQ_A.pdb", 
                  "4G1G_B.pdb", "4G1L_B.pdb", "4G1O_B.pdb", "4LD8_A.pdb", 
                  "4LDD_B.pdb", "4LDI_A.pdb", "4LP7_D.pdb", "4LDB_C.pdb"]


    matrix = np.zeros([len(structures), len(structures)])

    for i in range(len(structures)):
        for j in range(len(structures))[i+1:]:

            pair = structures[i].split(os.sep)[-1][:-4] +"_"+ structures[j].split(os.sep)[-1][:-4]
            print "Pair:", pair

            spath = os.path.join("./", pair)
            try:
                os.mkdir(spath)
            except OSError as e:
                if e.errno == 17: # Directory exits
                    print e.strerror
                else: raise

            pdb1 = del_hetatoms(os.path.join(pdb_dir, structures[i]), save_path=spath)
            pdb2 = del_hetatoms(os.path.join(pdb_dir, structures[j]), save_path=spath)
            
            p1, p2, rmsd = alignment_pymol(pdb1, pdb2, save_path=spath)

            pqr1 = get_pqr(p1, save_path=spath)
            pqr2 = get_pqr(p2, save_path=spath)

            in1, in2, dx1, dx2 = set_grid(pqr1, pqr2, save_path=spath)

            apbs(in1)
            apbs(in2)

            #diff_file, and_file, and_value = get_delta_dx_and(dx1, dx2, save_path=spath)
            diff_file, and_file, and_value = get_delta_dx_and2(dx1, dx2, save_path=spath)
            csv = pqr2csv(pqr1, save_path=spath)

            diff_phi = multivalue(csv, diff_file, save_path=spath)
            and_phi = multivalue(csv, and_file, save_path=spath)

            diff_pdb = phi2pdb(p1, diff_phi, save_path=spath)
            and_pdb = phi2pdb(p1, and_phi, save_path=spath)

            matrix[i][j] = and_value
            print "END pair", pair



    print ""
    print "# MVisualDEP Similarity Matrix:"
    print ""

    sys.stdout.write("      ")
    for s in structures:
        sys.stdout.write("  "+s.split(os.sep)[-1][:-4]+" ")
    print ""

    for i in range(len(structures)):
        sys.stdout.write(" "+structures[i].split(os.sep)[-1][:-4] + "       "*i + "       ")
        for j in range(len(structures))[i+1:]:
            sys.stdout.write("   "+"%1.2f" % matrix[i][j])
        print ""



