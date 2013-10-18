#!/usr/bin/env python

import __main__
__main__.pymol_argv = [ 'pymol', '-qc'] # Quiet and no GUI

import sys, time, os
import pymol

__about__ = "This module make the alignment of two structures. This modules was made for the ViasualDEP WEB Interface."

# we don't want write all that line =P
pjoin = os.path.join

#class alignment:
def align(pdb1, pdb2, savepath):
        pymol.finish_launching()
        pymol.cmd.delete("all") #delete everything in "cache"

        pdb1_name = pdb1.split(os.sep)[-1].strip(".pdb")
        pdb2_name = pdb2.split(os.sep)[-1].strip(".pdb")

        #load the pdb files
        pymol.cmd.load( pdb1, pdb1_name )
        pymol.cmd.load( pdb2, pdb2_name )

        #make the align
        algn = pymol.cmd.align( pdb2_name, pdb1_name )
        time.sleep(1)

        print "RMSD Align:", algn[0]

        #save the new mobile structure
        spdb = 'static_%s.pdb' % pdb1_name
        spdb = pjoin(savepath, spdb)

        mpdb = 'mobile_%s.pdb' % pdb2_name
        mpdb = pjoin(savepath, mpdb)

        pymol.cmd.save( spdb, pdb1_name, 0, 'pdb')
        pymol.cmd.save( mpdb, pdb2_name, 0, 'pdb')

        pymol.cmd.sync(10)

        return algn[0], spdb, mpdb


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Error: You must give two files as argument.")

    align(sys.argv[1], sys.argv[2], './') 
