#!/usr/bin/env python

import web, os

pjoin = os.path.join

# Config parameters for initialize the data base 
CONFIG_DB_HOST      = "localhost"
CONFIG_DB_DBMS      = "postgresql"
CONFIG_DB_USER      = "dbuser"
CONFIG_DB_PASSWORD  = "dbpass"
CONFIG_DB_DATABASE  = "visualdepdb"

# user id of the httpdaemon
CONFIG_UDI = 33

CONFIG_ERROR_LOG    = "/var/www/visualdep_errors.log"

# Config parameters for some directories and for certain files
CONFIG_VISUALDEP_PATH = "/home/lbfm/www/visualdep_web/src/"
CONFIG_TMP_PATH = "/home/lbfm/www/visualdep_web/jobs/" #Here is where all the jobs will be stored

# pdb2pqr config
CONFIG_PDB2PQR_COMMAND      = "/home/lbfm/shared/pdb2pqr/pdb2pqr.py --ff=AMBER -v --chain"

# apbs config
CONFIG_APBS_COMMAND         =  "/home/lbfm/downloads/apbs-1.3-amd64/bin/apbs"

# pqr2csv config
CONFIG_PQR2CSV_COMMAND      = pjoin( CONFIG_VISUALDEP_PATH + "/scripts/pqr2csv")

# multivalue config
CONFIG_MULTIVALUE_COMMAND   = "/home/lbfm/downloads/apbs-1.3-amd64/share/tools/mesh/multivalue"

# settings for the default .dx file 
# if no dx is setted in the kclustel, umbral scripts...
# This option only set the "ends with" part of the .dx filename
CONFIG_DEFAULT_DX           = ".78"
CONFIG_DEFAULT_DX_EXTENSION = CONFIG_DEFAULT_DX + ".dx"
CONFIG_DEFAULT_SDIE         = "78.5400" #water enviroment


# settings for the upload module:
#   value: 0 -> means NO LIMIT
CONFIG_UPLOAD_RESIDUE_LIMIT   = 0

# The limit for RMSD value
CONFIG_RMSD_LIMIT        = 3.0

# number of days which a job is accessible
CONFIG_EXPIRED_DAYS     = 7


CONFIG_JMOL_VISUALIZATION   = "load pqr::/jobs/%s; select all; labels off; spacefill off; color cpk; wireframe off; ribbons off; cartoons off; backbone on; select protein; backbone off; wireframe on; spacefill 30; set propertyColorScheme 'high'; color property partialCharge;"
