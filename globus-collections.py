#!/usr/bin/python

import sys
import argparse
import os
import subprocess
import re
from pathlib import Path
import json


def run_command(cstring):
    process_output=subprocess.run(cstring,shell=True,capture_output=True)
    print("trying command..."+cstring)
    out = process_output.stdout.decode("utf-8")
    retcode = process_output.returncode    
    print("...result is "+str(retcode)+"\n")
    print(".."+out)
    return (retcode,out)

def login(gcs_endpoint_id):
    login_string = "globus login --gcs "+gcs_endpoint_id
    return run_command(login_string)


def create_collection(newpath,collection_id,new_coll_name):
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
    p = Path(basedir,newdir)
    if not os.path.exists(p):
        os.makedirs(p)
    new_share_dir = share_dir+"/"+newdir
    
    return create_collection(new_share_dir,collection_id,newdir)

def get_email(globus_id):
    command = "globus get-identities -v "+globus_id
    (r,o) = run_command(command)
    if not r == 0:
        return (r,o)

    lines = o.split('\n')
    pinfo = lines[2]
    pfields = pinfo.split('|')
    return (0,pfields[-1].strip())

def assign_privileges(id,person):
    (r,email) = get_email(person)
    if not r ==0:
        return (r,email)
    
    com_string ="globus endpoint permission create --permissions rw --provision-identity '"+person+"' --notify-email '"+email+"' "+id+":/"
    return run_command(com_string)


# add code to do it all iterate over config..
def process_collections(colls,cdir,sdir,collection_id):
    results = []
    for (colname,contact) in colls.items():
        res = process_collection(colname,contact,cdir,sdir,collection_id)
        results.append(res)
    return results



# create a single collection and assign permissions.
def process_collection(colname,contact,cdir,sdir,collection_id):
    (res,out) = create_new_dir_collection(cdir,sdir,colname,collection_id)
    if res == 0:
        return assign_privileges(out,contact)
    else:
        print("Cannot create collection "+colname)
        return (res,out)
    
def process_permissions(colls,collection_id):
    print("Processing permissions..."+str(len(colls)))
    results = []
    for (_,contact) in colls.items():
        print("processing..."+contact)
        res = assign_privileges(collection_id,contact)
        results.append(res)
    return results


def main():
    gcs_endpoint_id='ff4297b5-e45b-48f9-877e-5943d1f1a090'
    collection_id='9f3f8b64-2d67-4cad-829e-d0715dab7cdd'

    # get the directory
    parser = argparse.ArgumentParser("Glous data processing")
    parser.add_argument("-d",default=".",help="Base local directory for collections")
    parser.add_argument("-s",default=".",help="Base share directory")
    parser.add_argument("-g",help="GCS Endpoint ID",default=gcs_endpoint_id)
    parser.add_argument("-c",help="Collection ID",default=collection_id)
    parser.add_argument("-f",help="filespec.json file containing data file names to be read..",default="collections.json")
    parser.add_argument("-p",help="permissions only.",action='store_true')
    
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
