#!/usr/bin/env python

import re, datetime, os
from subprocess import check_call

from Bio import PDB
import prody
import numpy

from config import *

pjoin = os.path.join

def check_email(email):
    pattern = "(?:[a-z0-9!#$%&'*+/=?^_{|}~-]+(?:.[a-z0-9!#$%" + \
    "&'*+/=?^_{|}~-]+)*|\"(?:" + \
    "[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]" + \
    "|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9]" + \
    "(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?" + \
    "|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)" + \
    "{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?" + \
    "|[a-z0-9-]*[a-z0-9]:(?:" + \
    "[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]"  + \
    "|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"

    check = re.compile(pattern)
    if check.match(email):
        return True
    else:
        return False


def now():
    return datetime.datetime.now()


def check_residues(pdb_filepath):
    """check_residues returns True if the number of residues in pdb_filepath
       are in the range of ]0, config.CONFIG_UPLOAD_RESIDUE_LIMIT].
       Returns False in other case."""

    #When config.CONFIG_UPLOAD_RESIDUE_LIMIT == 0, means NO LIMIT!
    if CONFIG_UPLOAD_RESIDUE_LIMIT == 0: return True

    parser = PDB.PDBParser()
    pdb_name = pdb_filepath.split(os.sep)[-1].strip('.pdb')

    structure = parser.get_structure( pdb_name, pdb_filepath )
    residues = structure.get_residues()

    nres = 0
    for r in residues: nres += 1
    
    if nres > 0 and nres <= CONFIG_UPLOAD_RESIDUE_LIMIT:
        return True
    else:
        return False



class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidEmailError(Error):
    def __init__(self, expr):
        self.expr = expr
        Error.__init__(self,
             "%s it's not a valid e-mail address." % (repr(expr)))


def pdb2pqr(pdb, savepath):
    cmd = CONFIG_PDB2PQR_COMMAND
    cmd += " " + pdb
    pqr = pdb[:-4] + ".pqr"
    cmd += " " + pqr

    log = pjoin(savepath, 'pdb2pqr.log')
    log = open(log, "a+")

    check_call(cmd, shell=True, stderr=log, stdout=log)
    log.close()
    return pqr


def apbs(infile, userpath):
    os.chdir(userpath)
    cmd = CONFIG_APBS_COMMAND
    cmd += " " + infile

    check_call(cmd, shell=True)


def pqr2csv(pqr):
    cmd = CONFIG_PQR2CSV_COMMAND
    cmd += " " + pqr
    csv = pqr[:-4] + ".csv"
    cmd += " " + csv

    check_call(cmd, shell=True)
    return csv


def multivalue(csv, dx, outphi=None):
    if not outphi:
        outphi = dx[:-3] + '.phi'
    cmd = CONFIG_MULTIVALUE_COMMAND
    cmd += " " + csv + " " + dx
    cmd += " " + outphi

    check_call(cmd, shell=True)
    return outphi


def phi2pdb(phi, pdb, outpdb=None):
    pdb = prody.parsePDB(pdb)
    atoms = [a for a in pdb]
    for a in atoms:
        a.setBeta(0.0)

    phic = open(phi, 'r').readlines()
    for l in phic:
        x,y,z,t = l.strip().split(',')
        x = float(x)
        y = float(y)
        z = float(z)
        t = float(t)
        for j in xrange(len(atoms)):
            X,Y,Z = atoms[j].getCoords()
            X = float(X)
            Y = float(Y)
            Z = float(Z)
            if X == x and Y == y and Z == z:
                atoms[j].setBeta(t)
                atoms.pop(j)
                break

    if not outpdb:
        outpdb = phi[:-4] + ".pdb"

    prody.proteins.writePDB(outpdb, pdb)
    return outpdb


def bfactor2charge(dpdb, spqr, outpqr=None):
    if not outpqr:
        outpqr = dpdb[:-4] + ".pqr"

    pdb = prody.parsePDB(dpdb)
    pqr = prody.parsePQR(spqr)

    pdbatoms = [a for a in pdb]
    #pqratoms = [a for a in pqr]

    for atom in pqr:
        for i in range(len(pdbatoms)):
            if (atom.getCoords() == pdbatoms[i].getCoords()).all():
                atom.setCharge(pdbatoms[i].getBeta())
                pdbatoms.pop(i)
                break

    prody.writePQR(outpqr, pqr)
    return outpqr



def delta_dx(dx1, dx2, outdx="delta.dx"):
    sdx = open(dx1, "r")
    mdx = open(dx2, "r")
   

    # We are not going to check the number of line or
    # even the number of values that we are going to
    # process in the calculation of the difference.
    # We assume that the files has the same format
    # and all the values are in the same place in the file.

    content = zip(sdx, mdx)
    sdx.close()
    mdx.close()

    p = re.compile('[ a-z]+', re.IGNORECASE)
    q = re.compile("object 3 class array type double rank 0 items (\d+) data follows")
    float_regex = """
        [-+]? # optional sign
        (?:
            (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \./ ) # 1. 12. 123. etc 1 12 123 etc
        )
        (?: [Ee] [+-]? \d+ ) ? # followed by optional exponent part if desired
    """
    r = re.compile(float_regex, re.VERBOSE)

    buf = []
    buf2 = []
    index = 0
    for a,b in content:
        a = a.strip()
        b = b.strip()
        if a[0] == "#":
            continue
        elif a.startswith("attribute"):
            l = """attribute "dep" string "positions"
object "regular positions regular connections" class field
component "positions" value 1
component "connections" value 2
component "data" value 3"""
            break 
        elif p.match(a):
            buf.append(a + '\n')
            n = q.match(a)
            if(n):
                n = int(n.group(1))
                AND = numpy.zeros(shape=(n/3,3))
        else:
            a = r.findall(a)
            b = r.findall(b)

            d1 = abs(float(a[0]) - float(b[0]))
            m1 = max(abs(float(a[0])), abs(float(b[0])))
            #AND[index][0] = d1/max(abs(float(a[0])), abs(float(b[0])))
            AND[index][0] = numpy.divide(d1, m1)

            d2 = abs(float(a[1]) - float(b[1]))
            m2 = max(abs(float(a[1])), abs(float(b[1])))
            #AND[index][1] = d2/max(abs(float(a[1])), abs(float(b[1])))
            AND[index][1] = numpy.divide(d2, m2)

            d3 = abs(float(a[2]) - float(b[2]))
            m3 = max(abs(float(a[2])), abs(float(b[2])))
            #AND[index][2] = d3/max(abs(float(a[2])), abs(float(b[2])))
            AND[index][2] = numpy.divide(d3, m3)

            d = "%.6f %.6f %.6f\n" % (d1, d2, d3)
            buf2.append(d)
            index += 1


    outfile = open(outdx, 'w')
    outfile.writelines(buf)
    outfile.writelines(buf2)
    outfile.write(l)
    outfile.close()

    return outdx, AND, buf, l


def calc_and(AND, queue, head=None, tail=None,outfile="andfile"):
    f = open(outfile, 'w')

    if head:
        f.writelines(head)

    for i in xrange(AND.shape[0]):
        f.write("%.6f %.6f %.6f\n" % tuple(AND[i]))

    if tail:
        f.write(tail)
    f.close()

    ANDvalue = numpy.divide(numpy.sum(AND), AND.shape[0] * AND.shape[1])

    #return outfile, ANDvalue
    queue.put((outfile, ANDvalue))
