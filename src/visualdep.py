#!/usr/bin/env python
# coding=utf-8
#
# VisualDEP Pipeline- Command Line Version
# VisualDEP - Visualization of Diferences in Electrostatic Potentials
#
# Copyright (C) 2009-2014 Laboratorio de Biofísica Molecular - Universidad de Concepción.
# 
# José Martínez-Oyanedel <jmartine@udec.cl>
# Natalia Jaña-Perez <njana@udec.cl>
# Carlos Ríos-Vera. <crosvera@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import __main__
__main__.pymol_argv = ["pymol", "-qc"] # Quiet and no GUI

import sys, time, os, re
from subprocess import check_call
import ConfigParser

import pymol
pymol.finish_launching()
import numpy as np
import prody

import pqrparser
import dxparser



def get_config():
    conf = ConfigParser.ConfigParser()
    conf.read(os.path.expanduser("~")+"/.visualdep.conf")
    config = {}
    config["pdb2pqr_path"] = conf.get("VisualDEP", "pdb2pqr_path")
    config["psize_path"] = os.path.join(config["pdb2pqr_path"], "src")
    config["apbs_path"] = conf.get("VisualDEP", "apbs_path")
    config["apbs_bin_path"] = os.path.join(config["apbs_path"], 
                                           conf.get("VisualDEP", "apbs_bin"))
    config["multivalue_path"] = conf.get("VisualDEP", "multivalue_path")
    config["multivalue_bin_path"] = os.path.join(conf.get["VisualDEP", "multivalue_path"],
                                                 conf.get["VisualDEP", "multivalue_bin"])
    config["rmsd_constraint"] = conf.getboolean("VisualDEP", "rmsd_constraint")
    config["rmsd_limit"] = conf.getfloat("VisualDEP", "rmsd_limit")

    return config
        
# Config vars
VISUALDEP_CONFIG = get_config()


def alignment_pymol(pdb1, pdb2, save_path="./"):
    #os.environ['PYMOL_DATA'] = "/usr/share/pymol/"
    pymol.cmd.delete("all")

    p1_name = pdb1.split(os.sep)[-1][:-4]
    p2_name = pdb2.split(os.sep)[-1][:-4]

    pymol.cmd.load(pdb1, p1_name)
    pymol.cmd.load(pdb2, p2_name)
    algn = pymol.cmd.super(p1_name, p2_name)
    #algn = pymol.cmd.super(p1_name+" & alt A+''", p2_name+" & alt B+''")
    #algn = pymol.cmd.do("super %s & alt A+'', %s & alt B+''" %(p1_name, p2_name))
    #algn = pymol.cmd.do("super %s , %s" %(p1_name, p2_name))
    #algn = pymol.cmd.align(p1_name, p2_name)
    time.sleep(1)

    #print "align results:", algn
    static_pdb = os.path.join(save_path, "static_"+p1_name+".pdb")
    mobile_pdb = os.path.join(save_path, "mobile_"+p2_name+".pdb")
    pymol.cmd.save(static_pdb, p1_name, 0, "pdb")
    pymol.cmd.save(mobile_pdb, p2_name, 0, "pdb")
    
    pymol.cmd.sync(10)
    #pymol.cmd.quit()

    return static_pdb, mobile_pdb, algn[0]




def get_pqr(pdb, sdie="78.5400", save_path="./"):
    sys.path.insert(0, VISUALDEP_CONFIG["pdb2pqr_path"])
    import pdb2pqr

    pqr = os.path.join(save_path, pdb.split(os.sep)[-1][:-4] + ".pqr")

    l = "./ --ff AMBER -v --whitespace --chain %s %s" % (pdb, pqr)
    sys.argv = l.split()

    pdb2pqr.mainCommand(sys.argv)

    return pqr



def set_grid(pqr1, pqr2, sdie=78.5400, save_path="./"):
    sys.path.insert(0, VISUALDEP_CONFIG["psize_path"])
    import psize
    
    s1 = psize.Psize()
    s2 = psize.Psize()

    s1.runPsize(pqr1)
    s2.runPsize(pqr2)

    #cglen
    c1 = s1.getCoarseGridDims()
    c2 = s2.getCoarseGridDims()
    cglen = (max(c1[0], c2[0]), max(c1[1], c2[1]), max(c1[2], c2[2]))

    #fglen
    f1 = s1.getFineGridDims()
    f2 = s2.getFineGridDims()
    fglen = (max(f1[0], f2[0]), max(f1[1], f2[1]), max(f1[2], f2[2]))

    #dime
    d1 = s1.getFineGridPoints()
    d2 = s2.getFineGridPoints()
    dime = (max(d1[0], d2[0]), max(d1[1], d2[1]), max(d1[2], d2[2]))
   
    #create apbs input
    in_content = """
read
    mol pqr %s
end
elec 
    mg-auto
    dime %d %d %d
    cglen %.4f %.4f %.4f
    fglen %.4f %.4f %.4f
    cgcent mol 1
    fgcent mol 1
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie %.4f
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    write pot dx %s
end
quit
"""

    infile1 = os.path.join(save_path, pqr1.split(os.sep)[-1][:-4] + ".in")
    dxfile1 = infile1[:-3]
    cnt1 = in_content % (pqr1, dime[0], dime[1], dime[2], cglen[0], cglen[1], cglen[2], fglen[0], fglen[1], fglen[2], sdie, dxfile1)

    infile2 = os.path.join(save_path, pqr2.split(os.sep)[-1][:-4] + ".in")
    dxfile2 = infile2[:-3]
    cnt2 = in_content % (pqr2, dime[0], dime[1], dime[2], cglen[0], cglen[1], cglen[2], fglen[0], fglen[1], fglen[2], sdie, dxfile2)

    f = open(infile1, "w")
    f.write(cnt1)
    f.close()

    f = open(infile2, "w")
    f.write(cnt2)
    f.close()

    return infile1, infile2, dxfile1+".dx", dxfile2+".dx"





def apbs(infile):
    cmd = "%s %s" % (VISUALDEP_CONFIG["apbs_bin_path"], infile)
    check_call(cmd, shell=True)



def get_delta_dx_and(dx1, dx2, save_path="./"):
    dx1v = dxparser.read_dx(dx1)
    dx2v = dxparser.read_dx(dx2)

    diff = dx1v["values"] - dx2v["values"]
    anddiff = np.abs(diff) / np.maximum(np.abs(dx1v["values"]), np.abs(dx2v["values"]))
    and_value = np.average(anddiff)

    buff1 = []
    buff2 = []

    o = dx1v["origin"]
    n = dx1v["points"]
    s = dx1v["spacing"]
    t = n[0] * n[1] * n[2]
    if t%3 == 0:
        offset = 0
        while offset < t:
            buff1.append("%f %f %f\n" % tuple(diff[offset:offset+3]))
            buff2.append("%f %f %f\n" % tuple(anddiff[offset:offset+3]))
            offset += 3
    else:
        raise Exception("Something went wrong, the total values (%d) cannot be divisible by 3." % (t))


    head = """
object 1 class gridpositions counts %d %d %d
origin %f %f %f
delta %f 0.000000e+00 0.000000e+00
delta 0.000000e+00 %f 0.000000e+00
delta 0.000000e+00 0.000000e+00 %f
object 2 class gridconnections counts %d %d %d
object 3 class array type double rank 0 items %d data follows
""" % (n[0],n[1],n[2],  o[0],o[1],o[2],  s[0],s[1],s[2],  n[0],n[1],n[2],  t)


    tail = """attribute "dep" string "positions"
object "regular positions regular connections" class field
component "positions" value 1
component "connections" value 2
component "data" value 3
"""

    diff_file = os.path.join(save_path, dx1.split(os.sep)[-1][:-3] +"_"+ dx2.split(os.sep)[-1])
    and_file = diff_file[:-3] + ".and.dx"

    f1 = open(diff_file, "w")
    f2 = open(and_file, "w")

    f1.write(head)
    f1.writelines(buff1)
    f1.write(tail)
    
    f2.write(head)
    f2.writelines(buff2)
    f2.write(tail)

    f1.close()
    f2.close()

    return diff_file, and_file, and_value



def pdb2csv(pdb, save_path="./"):
    """Extracts the atoms coordinates from a pqr file and store it into a csv file."""

    s = prody.parsePDB(pdb)
    #s = pqrparser.parsePQR(pqr)
    content = []
    for a in s:
        l = "%f,%f,%f\n" % tuple(a.getCoords())
        #l = "%f,%f,%f\n" % tuple(a.coords)
        content.append(l)

    csv = os.path.join(save_path, pdb.split(os.sep)[-1][:-4]+".csv")
    f = open(csv, "w")
    f.writelines(content)
    f.close()

    return csv





def pqr2csv(pqr, save_path="./"):
    """Extracts the atoms coordinates from a pqr file and store it into a csv file."""

    #s = prody.parsePQR(pqr)
    s = pqrparser.parsePQR(pqr)
    content = []
    for a in s:
        #l = "%f,%f,%f\n" % tuple(a.getCoords())
        l = "%f,%f,%f\n" % tuple(a.coords)
        content.append(l)

    csv = os.path.join(save_path, pqr.split(os.sep)[-1][:-4]+".csv")
    f = open(csv, "w")
    f.writelines(content)
    f.close()

    return csv


def multivalue(csv, dx, save_path="./"):
    phi = os.path.join(save_path, dx.split(os.sep)[-1][:-3]+".phi")
    cmd = "%s %s %s %s" % (VISUALDEP_CONFIG["multivalue_bin_path"], csv, dx, phi)
    check_call(cmd, shell=True)

    return phi



def phi2pdb(base_pdb, phi, save_path="./"):
    pdb = prody.parsePDB(base_pdb)
    atoms = [a for a in pdb]
    for a in pdb:
        a.setBeta(0.0)

    phif = open(phi, "r")
    phic = phif.readlines()
    phif.close()

    for l in phic:
        x,y,z,k = l.strip().split(",")
        x = np.float(x)
        y = np.float(y)
        z = np.float(z)
        k = np.float(k)
        
        for a in xrange(len(atoms)):
            X,Y,Z = atoms[a].getCoords()
            if X==x and Y==y and Z==z:
                atoms[a].setBeta(k)
                atoms.pop(a)
                break

    out_pdb = os.path.join(save_path, phi.split(os.sep)[-1][:-4]+".pdb")
    prody.writePDB(out_pdb, pdb)

    return out_pdb


def del_hetatoms(pdb, save_path="./"):
    f = open(pdb, "r")
    content = f.readlines()
    f.close()

    cnt = [l for l in content if not l.startswith("HETATM")]

    out_pdb = os.path.join(save_path, pdb.split(os.sep)[-1])
    f = open(out_pdb, "w")
    f.writelines(cnt)
    f.close()

    return out_pdb





#if __name__ == "__main__":
#    diff_file, and_file, and_value = get_delta_dx_and(sys.argv[1], sys.argv[2])
#    print diff_file, and_file, and_value



if __name__ == "__main__":
    pdb1 = sys.argv[1]
    pdb2 = sys.argv[2]

    p1, p2, rmsd = alignment_pymol(pdb1, pdb2)
   

    if VISUALDEP_CONFIG["rmsd_constraint"] and rmsd <= VISUALDEP_CONFIG["rmsd_limit"]:
        print "RMSD:", rmsd, "too high, aborting..."
        exit(1)

    pqr1 = get_pqr(p1)
    pqr2 = get_pqr(p2)
    
    in1, in2, dx1, dx2 = set_grid(pqr1, pqr2)

    apbs(in1)
    apbs(in2)
   
    diff_file, and_file, and_value = get_delta_dx_and(dx1, dx2)
    csv = pqr2csv(pqr1)
    #csv = pdb2csv(pdb1)

    diff_phi = multivalue(csv, diff_file)
    and_phi = multivalue(csv, and_file)

    diff_pdb = phi2pdb(p1, diff_phi)
    and_pdb = phi2pdb(p1, and_phi)

    #print p1, p2, rmsd, and_value
    print "VisualDEP Summary:"
    print "RMSD:", rmsd
    print "AND value:", and_value
