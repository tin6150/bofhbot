import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *

# global parameters; paths to files used in reboot
SINFO = f'/global/home/users/{getpass.getuser()}/bofhbot/data/gpuNodes.txt'
CHECKGPU_DISCREPANCIES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/discrepantNodes.txt'
REBOOTED_NODES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/rebooted.txt'
REPORT = f'/global/home/users/{getpass.getuser()}/bofhbot/data/errorEmail.txt'
NON_DISCREPANT_NODES = f'/global/home/users/{getpass.getuser()}/bofhbot/data/nonDiscrepantNodes.txt'

############################################################

def updateRebootRecord():
    # this function updates the list of nodes that have been rebooted
    # if a node was fixed since being rebooted, it can be removed from the reboot list
    with open(NON_DISCREPANT_NODES, 'r') as f:
        for line in f:
            os.system(f"sed -i '/{line.strip()}/d' {REBOOTED_NODES}")

def findNodeState(node):
    # this function parses output from sinfo to find the current state of the inputted node
    # this is used to determine how a reboot should take place
    with open(SINFO, 'r') as f:
        for ln in f:
            ln = ln.strip()
            fields = ln.split()
            if(fields[1] == node):
                return fields[2]
    return f'{node} not found'

def findNodePartition(node):
    # this function parses output from sinfo to find the partition association of an inputted node
    # this is used in order to properly submit an sbatch job to reboot
    with open(SINFO, 'r') as f:
        for ln in f:
            ln = ln.strip()
            fields = ln.split()
            if(fields[1] == node):
                return fields[0]
    return f'{node} not found'

def addNodeToRebootRecord(node):
    # this function adds an inputted node to a list of nodes that have been rebooted
    # this is used to keep track of nodes that have been rebooted; nodes that have been rebooted
    # and are still discrepant are not rebooted again, but instead noted in the final report
    with open(REBOOTED_NODES, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if(len(data) > 0):
            file_object.write("\n")
        file_object.write(node)

def firstReboot(node):
    # this function checks whether an inputted node has been rebooted before
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
    # remove non discrepant nodes from the reboot list
    updateRebootRecord()
    # parse discrepant nodes
    with open(CHECKGPU_DISCREPANCIES, 'r') as f:
        for line in f:
            line = line.strip()
            if(len(line) == 0):
                continue
            # find the state of the current node
            nodeState = findNodeState(line)
            # if node has not been rebooted before, reboot. Otherwise, note in report that node was not fixed by reboot
            if(firstReboot(line)):
                if(nodeState == 'idle' or nodeState == 'down' or nodeState == 'down*'):
                    # ssh node to reboot
                    os.system(f'sudo -u tin /global/home/groups/scs/tin/remote_cycle_node.sh {line}')
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
                        os.system(f'sudo -u tin /global/home/groups/scs/tin/remote_cycle_node.sh {line}')
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
