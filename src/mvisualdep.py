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
from multiprocessing import Pool, Lock, Process

import pymol
pymol.finish_launching()
import numpy as np

import visualdep


def _unwrap_self__diff_calc(arg, **kwarg):
    return MVisualdep._diff_calc(*arg, **kwarg)

class MVisualdep():
    def __init__(self, structures, save_path="./", keep_hetatoms=False):
        visualdep.VISUALDEP_CONFIG = visualdep.get_config()
        self.structures = structures
        self.save_path = save_path
        self.keep_hetatoms = keep_hetatoms
        self.structures_name = []
        for s in structures:
            self.structures_name.append(s.split(os.path.sep)[-1][:-4])

        #Make directory where the calculations will be stored
        self.save_path_grid_calc = os.path.join(self.save_path, "grid_calc")
        try:
            os.mkdir(self.save_path_grid_calc)
        except OSError as e:
            if e.errno == 17:
                print e.strerror
            else: raise

        self.save_path_diffs = os.path.join(self.save_path, "diffs")
        try:
            os.mkdir(self.save_path_diffs)
        except OSError as e:
            if e.errno == 17:
                print e.strerror
            else: raise

#    def grid_calc(self):
#        structures = []
#        pqrs = []
#        #Alignments
#        for s in self.structures[1:]:
#            pdb1, pdb2, rmsd = visualdep.alignment_pymol2(self.structures[0], s, self.save_path_grid_calc)
#        for s in self.structures:
#            structures.append(os.path.join(self.save_path_grid_calc, self.structures_name+".pdb"))
#        for s in structures:
#            pqr = visualdep.get_pqr(s, save_path=self.save_path_grid_calc)
#            pqrs.append(pqr)


    def _diff_calc(self, pair):
        pdb1 = pair[0]
        pdb2 = pair[1]

        diff = pdb1.split(os.sep)[-1][:-4]+"_"+pdb2.split(os.sep)[-1][:-4]
        diff_path = os.path.join(self.save_path_diffs, diff)
        try:
            os.mkdir(diff_path)
        except OSError as e:
            if e.errno == 17:
                print e.strerror
            else: raise

        if not self.keep_hetatoms:
            pdb1 = visualdep.del_hetatoms(pdb1, diff_path)
            pdb2 = visualdep.del_hetatoms(pdb2, diff_path)

        print "Alignment"
        p1, p2, rmsd = visualdep.alignment_pymol(pdb1, pdb2, diff_path)
        print "PQR"
        pqr1 = visualdep.get_pqr(p1, save_path=diff_path)
        pqr2 = visualdep.get_pqr(p2, save_path=diff_path)

        in1, in2, dx1, dx2 = visualdep.set_grid(pqr1, pqr2, save_path=diff_path)
        print "APBS"
        visualdep.apbs(in1)
        visualdep.apbs(in2)

        diff_file, and_file, and_value = visualdep.get_delta_dx_and(dx1, dx2, save_path=diff_path)
        csv = visualdep.pqr2csv(pqr1, save_path=diff_path)

        diff_phi = visualdep.multivalue(csv, diff_file, save_path=diff_path)
        and_phi = visualdep.multivalue(csv, and_file, save_path=diff_path)

        diff_pdb = visualdep.phi2pdb(p1, diff_phi, save_path=diff_path)
        and_pdb = visualdep.phi2pdb(p1, and_phi, save_path=diff_path)

        with open(os.path.join(diff_path, "visualdep.out"), "w") as resultfile:
            resultfile.write("Pair: "+ diff+"\n")
            resultfile.write("rmsd: "+str(rmsd)+" \n")
            resultfile.write("and: " + str(and_value) +" \n")
            resultfile.close()

    def mp_calc(self, n_procs):
        pairs = []
        for i in range(len(self.structures)):
            for j in range(len(self.structures))[i+1:]:
                pairs.append((self.structures[i], self.structures[j]))

        pool = Pool(processes=n_procs)
        pool.map(_unwrap_self__diff_calc, zip([self]*len(pairs), pairs))




if __name__ == "__main__":
    structures = sys.argv[2:]
    #pdb_dir = "/home/crosvera/projects/Mlike/visualdep/pdbs/domains"

    vd = MVisualdep(structures)
    vd.mp_calc(int(sys.argv[1]))
