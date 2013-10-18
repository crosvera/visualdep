#!/usr/bin/env python

import argparse, getpass

from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from Model import *
from config import *


engine = create_engine('%s://%s:%s@%s/%s' %(CONFIG_DB_DBMS,
                    CONFIG_DB_USER, CONFIG_DB_PASSWORD, CONFIG_DB_HOST,
                    CONFIG_DB_DATABASE), echo=True)

Session = sessionmaker(bind=engine)
session = Session()



def add_admin():
    print "Adding a new Administrator user:"
    print "================================\n"

    name = raw_input("Full name: ")
    email = raw_input("E-mail address: ")
    username = raw_input("Username: ")
    password = getpass.getpass()
    return Admin(name, email, username, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--install', 
        help="Create all the tables needed and its initial values.",
        action='store_true')
    parser.add_argument('--new-admin', 
        help="Launch a wizard to create a new admin user.",
        action='store_true')
    parser.add_argument('--drop-all', 
        help="Drop all the tables in the database.",
        action='store_true')

    opts =  parser.parse_args()
    
    if opts.drop_all:
        print "THIS WILL DROP ALL THE TABLES IN THE DATABASE\n"
        drop = raw_input("ARE YOU SURE? [NO]: ")
        if drop == "YES":
            metadata = MetaData(engine)
            metadata.reflect()
            metadata.drop_all()
            print "\n** ALL DROPED =( **"


    if opts.install: #make tables and its initial values
        print "\nVisualDEP Installation [Control+C for cancel]\n",\
              "Add an administrator user for basic tasks.\n"

        admin = add_admin()
        opts.new_admin = False

        Base.metadata.create_all(engine)

        session.add_all(InitialData())
        session.add(admin)

        session.commit()
        print "\n** Congrats, VisualDEP is installed! **"


    if opts.new_admin:
        admin = add_admin()
        Base.metadata.create_all(engine)

        session.add(admin)
        session.commit()
        print "\n** Congrats, new user added! **"
