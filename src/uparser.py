#!/usr/bin/env python
# config=utf-8

import shutil
from multiprocessing import Process, Queue

import Utils
from Utils import pjoin
from editinfile import editinfile
import alignment
import dbscan 
from Model import engine, Job, JobStatus

from sqlalchemy.orm import sessionmaker
import prody
import scipy


class upload_parser:
    def __init__(self):
        #Make the connection with the database
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.__Queued = self.session.query(JobStatus).filter(JobStatus.status == "Queued").one()
        self.__Started = self.session.query(JobStatus).filter(JobStatus.status == "Started").one()
        self.__Finished = self.session.query(JobStatus).filter(JobStatus.status == "Finished").one()
        self.__Error = self.session.query(JobStatus).filter(JobStatus.status == "Error").one()
        self.__Deleted = self.session.query(JobStatus).filter(JobStatus.status == "Deleted").one()

    def get_queued_job(self):
        """get_queued_job returns the first job marked as `queued' in the 
           database. It will return None if the database has not jobs queued.
        """
        self.session.commit()
        QueuedJobs = self.session.query(Job).filter(Job.status_id == JobStatus.id)
        QueuedJobs = QueuedJobs.filter(JobStatus.status=="Queued").order_by(Job.id)
        if QueuedJobs.count():
            return QueuedJobs.limit(1)[0]
        else:
            return None

    
    def do_calc(self, job=None):
        if job == None:
            job = self.get_queued_job()
            if not job: return None

        #First: Mark the job as started (JobStatus.id = 2)
        job.status = self.__Started
        job.comment = "Job Started."
        job.datetime_start = Utils.now()
        self.session.commit()

        print "*" * 80
        print "Retrieving job with id %d." % job.id
        print "Job Started."

        #Second: Get the pickled data
        #REMEMBER: data_pickle is a [pickled] tuple, has the follow format:
        #           ( tmp_path, pdb1_filename, pdb2_filename, pdb2_aligned )
        Data = job.get_unpickled_data()
        userpath = Data[0]
        pdb1 = pjoin(userpath, Data[1])
        pdb2 = pjoin(userpath, Data[2])

        #Third: Apply structural alignment to both structures.
        #       Also check the RMSD.
        rmsd, spdb, mpdb = alignment.align(pdb1, pdb2, userpath)
        if rmsd > config.CONFIG_RMSD_LIMIT:
            #If the RMSD is higher than the limit, abort.
            job.status = self.__Error #Mark the job with error.
            job.datetime_stop = Utils.now()
            job.comment = "ERROR: The RMSD value (%.2f) after the structural alignment exceed the actual limit of %.2f. Job stopped at: %s." % (rmsd, config.CONFIG_RMSD_LIMIT, str(job.datetime_stop))
            self.session.commit()

            print job.comment
            #Now we delete the data of the failed job
            shutil.rmtree(userpath)
            return None

        #Fourth: Generate the respective .pqr files
        job.comment = "Job at Electrostatic Potential Calculation."
        self.session.commit()
        print job.comment

        spqr = Utils.pdb2pqr(spdb, userpath)
        mpqr = Utils.pdb2pqr(mpdb, userpath)

        #Fifth: Generate the input files for APBS (.in)
        insfile, dxsfile = editinfile(spqr)
        inmfile, dxmfile = editinfile(mpqr)

        #Sixth: Use APBS to generate the .dx files.
        Utils.apbs(insfile, userpath)
        Utils.apbs(inmfile, userpath)

        #Seventh: Generate the differences in electrostatic potential.
        job.comment = "Job at Differences in Electrostatical Potential calculation."
        self.session.commit()

        print job.comment

        ddx = dxsfile.split(os.sep)[-1][:-3] +'_'+ dxmfile.split(os.sep)[-1]
        ddx = pjoin(userpath, ddx)
        ddx, AND, head, tail = Utils.delta_dx(dxsfile, dxmfile, ddx)

        #Eighth: Generate a new .dx file with the normalized differences
        #        Spawned in other process.
        andfile = pjoin(userpath, 'andfile.dx')
        #Utils.calc_and(AND, head, tail, andfile)
        q = Queue()
        p = Process(target=Utils.calc_and, args=(AND, q, head, tail, andfile,))
        p.start()
        p.join()

        #Ninth: Generate the .pdb files from the Delta and AND .dx files
        csv = Utils.pqr2csv(spqr)
        deltaphi = Utils.multivalue(csv, ddx)
        #get the data from the other process (Utils.calc_and)
        andfile, andvalue = q.get(True)
        andphi = Utils.multivalue(csv, andfile)

        deltapdb = Utils.phi2pdb(deltaphi, spdb)
        andpdb = Utils.phi2pdb(andphi, spdb)

        deltapqr = Utils.bfactor2charge(deltapdb, spqr)


        #Tenth: Clustering, Outlier detection.
        deltapqr_data = prody.parsePQR(deltapqr)
        atoms = [(a.getCharge(), a) for a in deltapqr_data]
        atoms = sorted(atoms, key=lambda a: a[0])
        atoms = scipy.array(atoms)
        l = range(len(atoms))
        atoms2 = scipy.array(zip(l, atoms[:,0]))

        cClass, tType, Eps, boolAns = dbscan.dbscan(atoms2, 2)
        outliers = []
        for i in l:
            if cClass[i] == -1.0:
                outliers.append(atoms[i][1])

        maxv = atoms[-1][0]

        #Eleventh: Save the changes in the database
        data = (userpath, Data[1], Data[2],                 #Basic data
                (pdb1, spdb, spqr, insfile, dxsfile),       #pdb1 related data
                (pdb2, mpdb, mpqr, inmfile, dxmfile),       #pdb2 related data
                (ddx, deltapdb, andvalue, deltapqr, andfile,
                    andpdb), #delta related data
                (outliers, maxv) #Outliers from deltapqr, max delta EP
               )

        job.set_data(data)
        job.comment = "Job finished successfully."
        job.status = self.__Finished
        job.datetime_stop = Utils.now()
        self.session.commit()
        print job.comment

        return True


if __name__ == "__main__":
    import os, time
    import config

    pidfile = open("/var/run/visualdep.pid" ,'a')
    pidfile.write("\n" + str(os.getpid()))
    pidfile.close()

    #os.chdir(config.CONFIG_VISUALDEP_PATH)
    parser = upload_parser()
    while True:
        parser.do_calc()
        time.sleep(30)
