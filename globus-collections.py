#!/usr/bin/python
### Globus-collections.py
### Code for creating globus collections via automation of globus command line.
### Copyright 2024-2025 University of Pittsburgh
### Harry Hochheiser, harryh@pitt.edu


import sys
import argparse
import os
import subprocess
import re
from pathlib import Path
import json


def run_command(cstring):
    """ Run a Globus command
    cstring is a fully formed Globus command. This routine will use sub.process.run() to make a shell
    call and return the result code.
    """
    process_output=subprocess.run(cstring,shell=True,capture_output=True)
    print("trying command..."+cstring)
    out = process_output.stdout.decode("utf-8")
    retcode = process_output.returncode    
    print("...result is "+str(retcode)+"\n")
    print(".."+out)
    return (retcode,out)



 
def login(gcs_endpoint_id):
    """ Globus login
    runs a login for the appropriate  endpoint
    this forces the login through the web broser
    """
    login_string = "globus login --gcs "+gcs_endpoint_id
    return run_command(login_string)


def create_collection(newpath,collection_id,new_coll_name):
    """ Creating the collection
    newpath  new directory locally being shared
    collection_id  containing collection
    new_coll_name  the new collection name
    """ 
    create_command = "globus collection create guest "+collection_id+" '"+str(newpath)+"' "+new_coll_name
    (retcode,out) = run_command(create_command)
    if not retcode == 0:
        return (-1,"")
    regexp="ID:\s+(.*)\n"
    pat=re.compile(regexp)
    ma = re.search(pat,out)   
    if ma is None:
        return (-2,"")
    if len(ma.groups()) < 1:
        return (-3,"")
    return (0,ma.group(1))


def create_new_dir_collection(basedir,share_dir,newdir,collection_id):
    """ create the directory and the collection
    basedir    base under which we will be putting the new directory
    share_dir  the share directory
    newdir     the new directory under base
    collection_id the collection
    """ 
    p = Path(basedir,newdir)
    if not os.path.exists(p):
        os.makedirs(p)
    new_share_dir = share_dir+"/"+newdir
    
    return create_collection(new_share_dir,collection_id,newdir)

def get_email(globus_id):
    """   gets the email for a user
      globus_id  the globus Id for which we want to get an email
      the "globus get-identities call returns
      something of the following form:

            ID                                   | Username            | Full Name        | Organization             | Email Address   
           ------------------------------------ | ------------------- | ---------------- | ------------------------ | ----------------
            83b35b59-d648-4c62-a843-ceebed336627 | hshoch@globusid.org | Harry Hochheiser | University of Pittsburgh | hshoch@gmail.com
        This routine parses out the last line to grab  the email at the end.
    """
    command = "globus get-identities -v "+globus_id
    (r,o) = run_command(command)
    if not r == 0:
        return (r,o)

    lines = o.split('\n')
    pinfo = lines[2]
    pfields = pinfo.split('|')
    return (0,pfields[-1].strip())

def assign_privileges(id,person):
    """    assign privileges
    id       the collection for which privileges are being assigned
    person   person id - the "globusid" or other globus email
    """ 
    (r,email) = get_email(person)
    if not r ==0:
        return (r,email)
    
    com_string ="globus endpoint permission create --permissions rw --provision-identity '"+person+"' --notify-email '"+email+"' "+id+":/"
    return run_command(com_string)


# add code to do it all iterate over config..
def process_collections(colls,cdir,sdir,collection_id):
    """  Process a set of collection requests
    colls is a set of pairs of collection names and globus names.
    cdir is the base local directory that will be shared
    sdir is the "share directory" as seen by globus
    collection_id is the collection in which files will be shared.

    iterates through and tries to create a collection for each, 
    """ 
    results = []
    for (colname,contact) in colls.items():
        res = process_collection(colname,contact,cdir,sdir,collection_id)
        results.append(res)
    return results


def process_collection(colname,contact,cdir,sdir,collection_id):
    """ create a single collection and assign permissions.
    colname is the name of the collection
    contact is the globus id of the contact
    cdir is the base local directory that will be shared
    sdir is the "share directory" as seen by globus
    collection_id is the collection in which files will be shared.

    creates a single collection
    """ 
    (res,out) = create_new_dir_collection(cdir,sdir,colname,collection_id)
    if res == 0:
        return assign_privileges(out,contact)
    else:
        print("Cannot create collection "+colname)
        return (res,out)
    
def process_permissions(colls,collection_id):
    """
    colls is a set of pairs of collection names and globus names.
    collection_id is the collection  for which we are assigning privileges.
    """
    print("Processing permissions..."+str(len(colls)))
    results = []
    for (_,contact) in colls.items():
        print("processing..."+contact)
        res = assign_privileges(collection_id,contact)
        results.append(res)
    return results


def main():

    # get the directory
    parser = argparse.ArgumentParser("Glous data processing")
    parser.add_argument("-d",default=".",help="Base local directory for collections")
    parser.add_argument("-s",default=".",help="Base share directory")
    parser.add_argument("-g",help="Globus endpoint ID that will be shared")
    parser.add_argument("-c",help="Collection ID to be shared")
    parser.add_argument("-f",help="JSON file containing pairs of group names and globus ids. Group names will be names of new subdirectories, assigned to users associated with the globus ids.",default="collections.json")
    parser.add_argument("-p",help="Set permissions only - do not create files ",action='store_true')
    
    args = parser.parse_args()
    cdir = args.d
    cfile = args.f
    gcs_endpoint_id=args.g
    sdir = args.s
    permissions = args.p
    collection_id = args.c
    print("collection id is..."+collection_id)
    

    # read config file
    with open(cfile,"r") as cj:
        colls= json.load(cj)
    (res,out) = login(gcs_endpoint_id)
    
    if not res == 0:
        print("login error")

    if args.p == True:
        results = process_permissions(colls,collection_id)
    else:
        results =  process_collections(colls,cdir,sdir,collection_id)
    print(results)
    

if __name__ =="__main__":
    main()
