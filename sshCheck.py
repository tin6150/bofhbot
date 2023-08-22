import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

############################################################

def parseSINFO():
    nodes = set()
    with open('/global/home/users/hchristopher/bofhbot/data/gpuNodes.txt', 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
            nodes.add(fields[1])
    return nodes

def isNodeReachable(node):
    exitCode = os.system(f'/global/home/users/hchristopher/bofhbot/nodeCheck.sh {node}')
    if(exitCode == 0):
        return True
    else:
        return False
    
############################################################

def main():
    nodeList = parseSINFO()
    for n in nodeList:
        if(isNodeReachable(n)):
            with open("/global/home/users/hchristopher/bofhbot/data/reachableNodes.txt", "a+") as file_object:
                file_object.seek(0)
                # If file is not empty then append '\n
                data = file_object.read(100)
                if len(data) > 0 :
                    file_object.write("\n")
                # Append text at the end of file
                file_object.write(n)
        else:
            with open("/global/home/users/hchristopher/bofhbot/data/unreachableNodes.txt", "a+") as file_object:
                file_object.seek(0)
                # If file is not empty then append '\n
                data = file_object.read(100)
                if len(data) > 0 :
                    file_object.write("\n")
                # Append text at the end of file
                file_object.write(n)
                
############################################################

main()
