#!/usr/bin/env python

import web
from web import form

#import base64, pickle, os
import re, sys, time,os

import Model, Utils
from Utils import pjoin
from config import *
#import dbscan

from Bio import PDB
import scipy
import prody


#pjoin = os.path.join

################## WEBPY STUFF ####################
render = web.template.render('templates/')

urls = (
        '/(\d+)*'  , 'results'
       )

app_results = web.application(urls, globals())

#DB = connect_db.connect_db()

dx_ext = CONFIG_DEFAULT_DX_EXTENSION
pqr_dx_ext = '.pqr' + dx_ext

class results:
    def GET (self, jobid=None):
        if jobid is None or not jobid.isdigit():
            return web.seeother('../')

        #Now check if the jobid exists :)
        job = web.ctx.orm.query(Model.Job).get(jobid)
        if job == None:
            #ERROR wrong id
            msg = "Wrong job identificator."
            return render.results(msg)

        if job.status.status == "Deleted":
            msg = "The job was deleted."
            return render.results(msg)
        elif job.status.status != "Finished":
            msg = "The job (id=%d) is not done yet. <br />Status: " + job.comment
            return render.results(msg %job.id)

        #Now seems you can see the results =)
        Data = job.get_unpickled_data()
        userpath = Data[0]
        sysdir = CONFIG_TMP_PATH

        pdb1 = pjoin(userpath, Data[1])
        pdb2 = pjoin(userpath, Data[2])

        stuff1 = Data[3] #pdb1 related data (pdb1, spdb, spqr, insfile, dxsfile)
        stuff2 = Data[4] #pdb2 related data (pdb2, mpdb, mpqr, inmfile, dxmfile)
        stuff3 = Data[5] #delta related data (ddx, deltapdb, andvalue, deltapqr, andfile, andpdb)
        stuff4 = Data[6] #Outliers, max delta EP
        pqrlog = pjoin(userpath, "pdb2pqr.log")
        apbslog = pjoin(userpath, "io.mc")

        outliers = stuff4[0]
        maxv = stuff4[1] #max(outliers, key=lambda a: a.getCharge()).getCharge() if len(outliers) else None

        #now we create the jmol inline-script
        script_line = CONFIG_JMOL_VISUALIZATION % (stuff3[3].split(sysdir)[-1])

        files = dict(pdb1=stuff1[0], pdb2=stuff2[0], spdb=stuff1[1], mpdb=stuff2[1], spqr=stuff1[2], 
                    mpqr=stuff2[2], dxsfile=stuff1[4], dxmfile=stuff2[4], ddx=stuff3[0], deltapdb=stuff3[1], 
                    andvalue=stuff3[2], deltapqr=stuff3[3], andfile=stuff3[4], andpdb=stuff3[5], pqrlog=pqrlog, 
                    apbslog=apbslog, script=script_line)

        return render.results( None, files=files, jobid=jobid, atoms=outliers, maxv=maxv)



