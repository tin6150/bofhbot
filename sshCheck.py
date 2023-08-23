import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

SINFO = '/global/home/users/hchristopher/bofhbot/data/gpuNodes.txt'
CLUSH_OUTPUT = '/global/home/users/hchristopher/bofhbot/data/allNodes.txt'
REACHABLE_NODES = "/global/home/users/hchristopher/bofhbot/data/reachableNodes.txt"
UNREACHABLE_NODES = "/global/home/users/hchristopher/bofhbot/data/unreachableNodes.txt"

############################################################

def parseSINFO():
    nodes = set()
    with open(SINFO, 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
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
    """
    for n in nodeList:
        if(checkSsh(n) == 'up'):
            with open(REACHABLE_NODES, "a+") as file_object:
                file_object.seek(0)
                # If file is not empty then append '\n
                data = file_object.read(100)
                #if len(data) > 0 :
                    #file_object.write("\n")
                # Append text at the end of file
                file_object.write(n + ',')
        else:
            with open(UNREACHABLE_NODES, "a+") as file_object:
                file_object.seek(0)
                # If file is not empty then append '\n
                data = file_object.read(100)
                if len(data) > 0 :
                    file_object.write("\n")
                # Append text at the end of file
                file_object.write(n)
"""                
############################################################

main()
