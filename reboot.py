import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

SINFO = f'/global/home/users/{getpass.getuser()}/bofhbot/data/gpuNodes.txt'
REACHABLE_NODES = f"/global/home/users/{getpass.getuser()}/bofhbot/data/reachableNodes.txt"
UNREACHABLE_NODES = f"/global/home/users/{getpass.getuser()}/bofhbot/data/unreachableNodes.txt"
CHECKGPU_DISCREPANCIES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/errorEmail.txt'
REBOOTED_NODES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/rebooted.txt'

############################################################

def findNodeState(node):
    with open(SINFO, 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
            if(fields[1] == node):
                return fields[2]
    return f'{node} not found'

def findNodePartition(node):
    with open(SINFO, 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
            if(fields[1] == node):
                return fields[0]
    return f'{node} not found'

def addNodeToRebootRecord(node):
    with open(REBOOTED_NODES, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if(len(data) > 0):
            file_object.write("\n")
        file_object.write(node)

def firstReboot(node):
    with open(REBOOTED_NODES, 'r') as f:
        for line in f:
            line = line.strip()
            if(line == node):
                return False
    return True

############################################################

def main():
    with open(CHECKGPU_DISCREPANCIES, 'r') as f:
        for line in f:
            line = line.strip()
            fields = line.split()
            if(len(fields) == 0):
                continue
            if(fields[0] != 'gpuOffline'):
                continue
            nodeState = findNodeState(fields[3])
            if(firstReboot(fields[3])):
                if(nodeState == 'idle' or nodeState == 'down'):
                    #ssh node to reboot
                    # os.system(f'ssh {fields[1]} reboot')
                    # add node to reboot list
                    addNodeToRebootRecord(fields[3])
                elif(nodeState == 'alloc' or nodeState == 'mix' or nodeState == 'resv'):
                    # submit job to reboot node once exclusive access is available
                    # also add node to reboot list in job
                    partition = findNodePartition(fields[3])
                    os.system(f'sbatch --nodelist={fields[3]} --partition={partition} ~/bofhbot/reboot.sh')
                elif(nodeState == 'drain'):
                    # check if any jobs are running on node with squeue -w, if not reboot with ssh
                    if(os.popen(f'squeue -w {fields[3]} | wc -l').read().split('\n')[0] == '1'):
                        # os.system(f'ssh {fields[3]} reboot')
                        # add node to reboot list
                        addNodeToRebootRecord(fields[3])
                elif(nodeState == f'{fields[3]} not found'):
                    # do nothing
                    pass
                else:
                    pass
            else:
                # add to report that node was not fixed by reboot
                with open(CHECKGPU_DISCREPANCIES, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)
                    if(len(data) > 0):
                        file_object.write("\n")
                    file_object.write(fields[3])                

############################################################

main()
