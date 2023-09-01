import socket 
import os
import argparse
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

# global parameters: paths to files used in checking whether nodes can be ssh-ed
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--path", help="path to bofhbot")
args = argParser.parse_args()
SINFO = f'{args.path}/data/gpuNodes.txt'
CLUSH_OUTPUT = f'{args.path}/data/allNodes.txt'
REACHABLE_NODES = f"{args.path}/data/reachableNodes.txt"
UNREACHABLE_NODES = f"{args.path}/data/unreachableNodes.txt"
IGNORE_LIST = f'{args.path}/.ignore.txt'

############################################################

def parseSINFO():
    # this function parses an sinfo command that lists all nodes in the cluster that contain a gpu
    # all nodes from sinfo are returned as a set. Any nodes set to be ignored in the .ignore.txt file
    # are skipped in parsing
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
    # parse sinfo, get all nodes as a single string seperated by commmas (syntax for clush call)
    nodeList = ','.join(parseSINFO())
    # attempt to ssh into all nodes, redirect output to a file which will be parsed
    os.system(f'clush -w {nodeList} uptime &> {CLUSH_OUTPUT}')
    # open the output of parallel ssh and parse
    with open(CLUSH_OUTPUT, 'r') as f:
        for line in f:
            # ignore lines that start with clush
            if(line.startswith("clush")):
               continue
            line = line.strip()
            fields = line.split()
            # if node has an ssh error, add node to list of unreachable node
            if(fields[1] == "ssh:"):
                with open(UNREACHABLE_NODES, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)
                    if(len(data) > 0):
                        file_object.write("\n")
                    file_object.write(fields[0][:-1])
            # if node is passsword locked, ignore it
            elif(fields[1] == "Permission"):
                continue
            # if node can be ssh-ed, add it to list of reachable nodes
            else:
                with open(REACHABLE_NODES, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)                                                                            
                    file_object.write(fields[0][:-1] + ',')    

############################################################

main()
