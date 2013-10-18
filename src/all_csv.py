#!/usr/bin/env python
# coding=utf-8

import sys, os, subprocess
import commands

import config

from Bio import PDB
import numpy

__about__ = "Calculates the electrostatic potential for every pqr file"
__author__ = """Natalia Jaña <njana@udec.cl>, 
              \nre-written by: Carlos Ríos <crosvera@gmail.com>"""

pjoin = os.path.join




class all_csv:
    def __init__ (self, tmp_path, static_pqr, static_pdb, dx_file ):
        self.tmp_path       = tmp_path
        self.pqr2csv_cmd    = config.CONFIG_PQR2CSV_COMMAND
        self.multivalue_cmd = config.CONFIG_MULTIVALUE_COMMAND
        self.pexatom_cmd    = config.CONFIG_PEXATOM_COMMAND
        self.s_pqr          = static_pqr
        self.s_pdb          = static_pdb
        self.dx_f           = dx_file
        self.dx_path        = pjoin( tmp_path, config.CONFIG_PQR_PATH, config.CONFIG_DX_PATH )


    def pqr2csv (self):
        #create the folder to store the csv files
        csv_path = pjoin( self.tmp_path, config.CONFIG_PQR_PATH, config.CONFIG_CSV_PATH )
        if not os.path.exists( csv_path ):
            try:
                os.mkdir( csv_path )
                self.csv_path = csv_path
            except OSError, e:
                print e
        else:
            self.csv_path = csv_path
        #now run the command
        line = " %s %s" % ( self.s_pqr, pjoin(csv_path, self.s_pqr.split(os.sep)[-1]+".csv") )

        try:
            torun = self.pqr2csv_cmd + line
            retcode = subprocess.call( torun , shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            else:
                #print >>sys.stderr, "Child returned", retcode
                return pjoin(csv_path, self.s_pqr.split(os.sep)[-1]+".csv")
        except OSError, e:
            print >>sys.stderr, "Execution failed:", e

        return None
        

    def multivalue (self, csv_file, u_file):
        #create the folder to store the phi files
        phi_path = pjoin( self.tmp_path, config.CONFIG_PQR_PATH, config.CONFIG_PHI_PATH )
        if not os.path.exists( phi_path ):
            try:
                os.mkdir( phi_path)
                self.phi_path = phi_path
            except OSError, e:
                print e
        else:
            self.phi_path = phi_path

        #now run the command
        line = " %s %s %s" % ( csv_file, u_file, pjoin(phi_path, u_file.split(os.sep)[-1]+'.phi') )

        try:
            torun = self.multivalue_cmd + line
            retcode = subprocess.call( torun , shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            else:
                #print >>sys.stderr, "Child returned", retcode
                return pjoin(phi_path, u_file.split(os.sep)[-1]+'.phi')
        except OSError, e:
            print >>sys.stderr, "Execution failed:", e

        return None

    def pexatom (self, phi_file):
        dirc = pjoin( self.phi_path, "pdb/")
        if not os.path.exists( dirc ):
            try:
                os.mkdir( dirc )
                self.dirc = dirc
            except OSError, e:
                print e
        else:
            self.dirc = dirc

        f    = pjoin(dirc, phi_file.split(os.sep)[-1].strip(".phi") + ".pdb")
        line = " %s %s %s" %(self.s_pdb, phi_file, f)
        torun = self.pexatom_cmd + line
        output = commands.getoutput( torun )
        return f



#    def pex (self, phi_file):
#        dirc = pjoin( self.phi_path, "pdb/")
#        if not os.path.exists( dirc ):
#            try:
#                os.mkdir( dirc )
#                self.dirc = dirc
#            except OSError, e:
#                print e
#        else:
#            self.dirc = dirc
#
#        parser = PDB.PDBParser()
#        writer = PDB.PDBIO()
#
#        structure = parser.get_structure(self.s_pdb, self.s_pdb)
#        atoms = structure.get_atoms()
#
#        phi_f = open(phi_file, 'r')
#        f    = pjoin(dirc, phi_file.split(os.sep)[-1].strip(".phi") + ".pdb")
#
#        for atom in atoms:
#            l = phi_f.readline().strip().split(',')
#            if float(l[-1]) >= 0.0:
#                atom.set_bfactor(float(l[-1]))
#            else:
#                atom.set_bfactor(0.0)  #Fix the NaN problem
#
#        phi_f.close()
#        writer.set_structure(structure)
#        writer.save(f)
#
#        return f

    def pex (self, phi_file):
        dirc = pjoin( self.phi_path, "pdb/")
        if not os.path.exists( dirc ):
            try:
                os.mkdir( dirc )
                self.dirc = dirc
            except OSError, e:
                print e
        else:
            self.dirc = dirc

        parser = PDB.PDBParser()
        writer = PDB.PDBIO()

        structure = parser.get_structure(self.s_pdb, self.s_pdb)
        atoms = structure.get_atoms()

        phi_f = open(phi_file, 'r')
        phi = []

        output_pdb = pjoin(dirc, phi_file.split(os.sep)[-1].strip(".phi") + ".pdb")

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
                if a.get_coord().all() == p['coord'].all():
                    a.set_bfactor(p['ep'])
                    phi.remove(p)
                    break
                else:
                    a.set_bfactor(0.0)

        writer.set_structure(structure)
        writer.save(output_pdb)

        return output_pdb
