#!/usr/bin/env python
# coding=utf-8

import sys, os, subprocess
import commands

import config

pjoin = os.path.join

"""generate_pqr is an script that generates pqr files from pdb files.
 \nCoded by Natalia Jaña\nRe-written by Carlos Ríos.\n"""

class generate_pqr:
    def __init__(self, pqr_path, *pdb_files):
        self.pqr_path = pqr_path
        self.pqr_files = []
        self.pdb_files = pdb_files

        if not os.path.exists( pqr_path ):
            try:
                os.mkdir( pqr_path )
                self.pqr_path = pqr_path
            except OSError, e:
                print e

    def generate(self):
        command = config.CONFIG_PDB2PQR_COMMAND
        params = config.CONFIG_PDB2PQR_PARAMS

        for i in self.pdb_files:
            f = pjoin(self.pqr_path, i.split(os.sep)[-1][:-4] + ".pqr")
            torun = command + params + i + " " + f
            output = commands.getoutput( torun )
            self.pqr_files.append(f)
            #now save the log
            log = open(pjoin(self.pqr_path, "pqr_log.log"), "a")
            log.write("COMMAND: "+torun+'\n\n'+output+"\n"+"="*80+"\n\n")
            log.close()

    
    def generate_dx(self, infs) :
        command = config.CONFIG_APBS_COMMAND
        in_files = infs[0]
        for i in in_files:
            torun = command + " " + i
            output = commands.getoutput( torun )
            #now save the log
            log = open(pjoin(self.pqr_path, "dx_log.log"), "a")
            log.write("COMMAND: "+torun+'\n\n'+output+"\n"+"="*80+"\n\n")
            log.close()


        #take a list with the dx files
        #self.dx_files = [self.pqr_files[0]+'.78.dx', self.pqr_files[1]+'.78.dx']
        self.dx_files = infs[1]
        

    def compare_dx(self) :
        command = config.CONFIG_COMPAREDX_COMMAND
        #dxf = config.CONFIG_DX_PATH

        #self.dxs_path = pjoin(self.pqr_path, dxf)
        self.dxs_path = self.pqr_path
        if not os.path.exists( self.dxs_path ):
            try:
                os.mkdir( self.dxs_path )
            except OSError, e:
                print e


        ddx_filename = self.dx_files[0].split(os.sep)[-1][:-6] +'__'+ self.dx_files[1].split(os.sep)[-1]
        ddx = pjoin(self.dxs_path, ddx_filename)

        try:
            torun = command + " %s %s %s" % (self.dx_files[0], self.dx_files[1], ddx)
            retcode = subprocess.call( torun , shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            else:
                print >>sys.stderr, "Child returned", retcode
        except OSError, e:

            print >>sys.stderr, "Execution failed:", e

        return ddx
