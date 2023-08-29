import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

SINFO = f'/global/home/users/{getpass.getuser()}/bofhbot/data/gpuNodes.txt'
CHECKGPU_DISCREPANCIES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/discrepantNodes.txt'
REBOOTED_NODES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/rebooted.txt'
REPORT = f'/global/home/users/{getpass.getuser()}/bofhbot/data/errorEmail.txt'
NON_DISCREPANT_NODES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/nonDiscrepantNodes.txt'

############################################################

def updateRebootRecord():
    with open(NON_DISCREPANT_NODES, 'r') as f:
        for line in f:
            os.system(f"sed -i '/{line.strip()}/d' {REBOOTED_NODES}")

def findNodeState(node):
    with open(SINFO, 'r') as f:
        for ln in f:
            ln = ln.strip()
            fields = ln.split()
            if(fields[1] == node):
                return fields[2]
    return f'{node} not found'

def findNodePartition(node):
    with open(SINFO, 'r') as f:
        for ln in f:
            ln = ln.strip()
            fields = ln.split()
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
    file1 = open(REBOOTED_NODES, 'r')
    file1.seek(0)
    while True:
        line = file1.readline()
        line = line.strip()
        if(line == node):
            file1.close()
            return False
        if not line:
            file1.close()
            return True

############################################################

def main():
    updateRebootRecord()
    with open(CHECKGPU_DISCREPANCIES, 'r') as f:
        for line in f:
            line = line.strip()
            if(len(line) == 0):
                continue
            nodeState = findNodeState(line)
            if(firstReboot(line)):
                if(nodeState == 'idle' or nodeState == 'down' or nodeState == 'down*'):
                    #ssh node to reboot
                    # os.system(f'ssh {fields[0]} reboot')
                    # add node to reboot list
                    addNodeToRebootRecord(line)
                elif(nodeState == 'alloc' or nodeState == 'mix' or nodeState == 'resv'):
                    # submit job to reboot node once exclusive access is available
                    # also add node to reboot list in job
                    partition = findNodePartition(line)
                    os.system(f'sbatch --nodelist={line} --partition={partition} ~/bofhbot/reboot.sh')
                elif(nodeState == 'drain' or nodeState == 'drng' or nodeState == 'drain*'):
                    # check if any jobs are running on node with squeue -w, if not reboot with ssh
                    if(os.popen(f'squeue -w {line} | wc -l').read().split('\n')[0] == '1'):
                        # os.system(f'ssh {line} reboot')
                        # add node to reboot list
                        addNodeToRebootRecord(line)
                elif(nodeState == f'{line} not found'):
                    # do nothing
                    pass
                else:
                    pass
            else:
                # add to report that node was not fixed by reboot
                with open(REPORT, "a+") as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)
                    if(len(data) > 0):
                        file_object.write("\n")
                    file_object.write(line)                

############################################################

main()
