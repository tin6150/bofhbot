import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

SINFO = f'/global/home/users/{getpass.getuser()}/bofhbot/data/gpuNodes.txt'
CLUSH_OUTPUT = f'/global/home/users/{getpass.getuser()}/bofhbot/data/allNodes.txt'
REACHABLE_NODES = f"/global/home/users/{getpass.getuser()}/bofhbot/data/reachableNodes.txt"
UNREACHABLE_NODES = f"/global/home/users/{getpass.getuser()}/bofhbot/data/unreachableNodes.txt"
IGNORE_LIST = f'/global/home/users/{getpass.getuser()}/bofhbot/data/.ignore.txt'

############################################################

def parseSINFO():
    nodes = set()
    with open(SINFO, 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
            with open(IGNORE_LIST, 'r') as i:
                if fields[1] not in i.read():
                    nodes.add(fields[1])
    return nodes
    
############################################################

def main():
    nodeList = ','.join(parseSINFO())
    os.system(f'clush -w {nodeList} uptime &> {CLUSH_OUTPUT}')
    with open(CLUSH_OUTPUT, 'r') as f:
        for line in f:
            if(line.startswith("clush")):
               continue
            line = line.strip()
            fields = line.split()
            if(fields[1] == "ssh:" or fields[1] == "Permission"):
                with open(UNREACHABLE_NODES, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)
                    if(len(data) > 0):
                        file_object.write("\n")
                    file_object.write(fields[0][:-1])
            else:
                with open(REACHABLE_NODES, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)                                                                            
                    file_object.write(fields[0][:-1] + ',')    

############################################################

main()
