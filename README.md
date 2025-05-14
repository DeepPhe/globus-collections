# globus-collections
A Script for creating Globus Collections for shared tasks

Background
=========
This script is designed to automate the creation of Globus collections
and the creation of appropriate permissions, allowing the
specification of multiple collections through a permissions
file. There are several assumptions:

1. All collections will be created relative to a common endpoint and
shared mapped collection. Note that this be a mapped collection, not a
Globus gues tcollection.

2. There is a local (to the machine where this script is being run)
file space that can be exposed to the globus services (through that
endpoint)

3. New collections are specificed by pairings of names of the new
collection and a corresponding globus id - as specified in the
collections.json file.

4. The specified name(s) of the new collection(s) will be instantiated
as directories on the local share of the same name


Usage
======

This script takes several necessary arguments:

1. -f: the json file containing collection name, globus id pairs.
2. -d  the local directory where files will be held.
3. -s the mapped share directory on Globus
4 - g the globus endpoint ID
5. -c the globus collection ID.
6. -p permissions only if true. Requires that the given collections
have already been created. 

An Example:

```python
python globus-collections.py -d  “/Users/harry/OneDrive - University of Pittsburgh/Documents - ChemoTimelines/upload” -f collections.json -g ff4297b5-e45b-48f9-877e-5943d1f1a090 -s”/Shared\ libraries/ChemoTimelines/Documents/upload/” -c 9f3f8b64-2d67-4cad-829e-d0715dab7cdd
```
