#!/usr/bin/env python


import sys, time, os, re
import tempfile
import pickle
import base64

import config, Utils
import Model
import results

import web
from Bio import PDB
from sqlalchemy.orm import scoped_session, sessionmaker


__about__ = """index.py was made for the VisualDEP GUI, its function is
             make possible the upload of pdb files."""
###########################################################################
#MISC VARS
#setting the temporary path
tempfile.tempdir = config.CONFIG_TMP_PATH
#make the DB connection

pjoin = os.path.join

############################## WEBPY STUFF #######################################
render = web.template.render('templates/')

urls = ('/', 'index',
        '/whatis', 'whatis',
        '/results', results.app_results,
       )

app = web.application(urls, locals())


def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=Model.engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all()

app.add_processor(load_sqla)


class whatis:
    def GET(self):
        return render.whatis()


class index:
    def GET(self):
        return render.index(msg=None)


    def POST( self ):
        f_input = web.input(pdb1={}, pdb2={})
        if len(f_input) != 3:
            #error
            msg = "An error has occurred while the form was submited. Please try again later."
            return render.index( msg )

        #everything is ok
        #make the temporary dir
        tmp_dir = tempfile.mkdtemp()
 
        if 'pdb1' in f_input:
            pdb1 = f_input['pdb1']
            pdb1.filename = pdb1.filename.lower().replace(' ','_')
            if not pdb1.filename.endswith('.pdb'):
                #error, this is not a pdb file
                msg = "ERROR: The file [%s] is not a valid .pdb file. Please submit a valid .pdb file." % (pdb1.filename)
                return  render.index( msg )

            if pdb1.filename == 'model.pdb':
                pdb1.filename = 'model_.pdb'
            pdb1F = open( pjoin(tmp_dir, pdb1.filename), "w" )
            pdb1F.write( pdb1.value )
            pdb1F.close()
        else:
            #Error uploading the pdb file.
            msg = 'ERROR: You have to upload a valid .pdb file.'
            return render.index( msg )


        if 'pdb2' in f_input:
            pdb2 = f_input['pdb2']
            pdb2.filename = pdb2.filename.lower().replace(' ', '_')
            if not pdb2.filename.endswith('.pdb'):
                #error, this is not a pdb file
                msg = "ERROR: The file [%s] is not a valid .pdb file. Please submit a valid .pdb file." % (pdb2.filename)
                return render.index( msg )

            if pdb2.filename == 'model.pdb':
                pdb2.filename = 'model_.pdb'
            pdb2F = open( pjoin(tmp_dir, pdb2.filename), "w" )
            pdb2F.write( pdb2.value )
            pdb2F.close()
        else:
            #Error uploading the pdb file.
            msg = 'ERROR: You have to upload a valid .pdb file.'
            return render.index( msg )


        if pdb1.filename == pdb2.filename:
            msg = "ERROR: Files cannot be the same. Please submit different files."
            return render.index( msg )


        #CHECK FOR NUMBERS OF RESIDUES IN PDB FILES in pdb1
        if not Utils.check_residues( pjoin(tmp_dir, pdb1.filename) ) :
            msg = "The PDB file: %s, doesn't respect the range ]0, %d]. Please change the file." % (pdb1.filename, config.CONFIG_UPLOAD_RESIDUE_LIMIT)
            return render.index( msg )

        #CHECK FOR NUMBERS OF RESIDUES IN PDB FILES in pdb2
        if not Utils.check_residues( pjoin(tmp_dir, pdb2.filename) ) :
            msg = "The PDB file: %s, doesn't respect the range ]0, %d]. Please change the file." % (pdb2.filename, config.CONFIG_UPLOAD_RESIDUE_LIMIT)
            return render.index( msg )

        #Serialization of the data to store it into the DB
        #( pdbs_path, pdb1_name, pdb2_name, pdb2_aligned, (min_umbral, max_umbral) )
        data = (tmp_dir, pdb1.filename, pdb2.filename)
        #data = ( tmp_dir, pdb1.filename, pdb2.filename, None, None)
        #save the data into the database
        job = Model.Job(data)
        web.ctx.orm.add(job)
        job.status = web.ctx.orm.query(Model.JobStatus).filter(Model.JobStatus.status == "Queued").one()
        web.ctx.orm.commit()

        jid = job.id

        #SHOW the page. Everything is ok
        return render.index(None, jid)




if __name__ == "__main__":
#    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
