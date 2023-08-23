import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

SINFO = '/global/home/users/hchristopher/bofhbot/data/gpuNodes.txt'
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
    nodeList = parseSINFO()
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
                
############################################################

main()
