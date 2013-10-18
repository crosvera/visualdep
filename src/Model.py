#!/usr/bin/env python

import hashlib
import cPickle
import base64

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import Sequence, ForeignKey, Numeric, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.sql import expression


from config import *
import Utils


engine = create_engine('%s://%s:%s@%s/%s' %(CONFIG_DB_DBMS, CONFIG_DB_USER,
        CONFIG_DB_PASSWORD, CONFIG_DB_HOST, CONFIG_DB_DATABASE) )

Base = declarative_base()



class JobStatus(Base):
    __tablename__ = 'job_status'

    id = Column(Integer, Sequence('jobstatus_id_seq'), primary_key=True)
    status = Column(String(16), unique=True)

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return "<JobStatus('%s')>" % (self.status)


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, Sequence('jobs_id_seq'), primary_key=True)
    datetime_upload = Column(DateTime, default=Utils.now)
    datetime_start = Column(DateTime)
    datetime_stop = Column(DateTime)
    data_pickled = Column(Text)
    status_id = Column(Integer, ForeignKey('job_status.id'))
    comment = Column(Text, default="Job waiting to start.")
    permanent = Column(Boolean, default=False)

    status = relationship("JobStatus", backref=backref('jobs', order_by=id))

    def __init__(self, data):
        #pickling the data (serialization)
        self.data_pickled = base64.b64encode(cPickle.dumps(data,2))

    def set_data(self, data):
        #NOTE: WE NEED ENCODE WITH BASE64, BECAUSE POSTGRESQL DOESN'T 
        #      ACCEPT THE PICKLE CHARACTERS
        self.data_pickled = base64.b64encode(cPickle.dumps(data,2))

    def get_unpickled_data(self):
        return cPickle.loads(base64.b64decode(self.data_pickled))

    def __repr__(self):
        return "<Job('%d', '%s')>" % (self.id, self.status.status)



class Admin(Base):
    '''
        This Table will be used to manage visualdep's admins.
        These admins are used to list and handle the jobs submited to
        visualdep.
    '''

    __tablename__ = 'admins'

    id = Column(Integer, Sequence('admins_id_seq'), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String(64), nullable=False)

    def __init__(self, name, email, username, password):
        if not Utils.check_email(email):
            raise Utils.InvalidEmailError(email)

        self.name = name
        self.email = email
        self.username = username
        self.password = hashlib.sha256(password).hexdigest()

    def __repr__(self):
        return "<Admin('%s', '%s', '%s')>" % (self.username, self.name,
            self.email)


def InitialData():
    """
    In this function we add the initial data that will be introduced in the
    database's tables when this is installed.
    """
    
    data = [
        JobStatus("Queued"),
        JobStatus("Started"),
        JobStatus("Finished"),
        JobStatus("Error"),
        JobStatus("Deleted")
    ]

    return data
