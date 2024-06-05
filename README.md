# CheckGpu
## Synopsis
checkNodes.sh [OPTION1] [OPTION2]

## Description
The checkGpu branch is a script which checks GPU nodes in a cluster environment for discrepancies between the expected and actual amount of GPUs in a node. Nodes which contain discrepancies or cannot be accessed via SSH are automatically rebooted, and a report of the script's findings are sent to the user via email.

The first step of this process creates a list of nodes within a cluster that contain GPUs, and will be checked for discrepancies in later steps. This is done by parsing the output of an sinfo command which lists all nodes within GPU partitions. Depending on what cluster you run this script in, different partitions will be searched for in sinfo. The list of GPU nodes can be further constrained with the use of the -l option, which enables the .ignoreList.txt and .checkList.txt files. 

With a list of all GPU nodes, the script then attempts to access each node via SSH. A list of reachable and unreachable nodes is generated; the reachable nodes will be checked for GPU discrepancies, and the unreachable nodes will be listed seperately in the final report.

Reachable nodes are checked for GPU discrepancies. Three numbers are compared to determine discrepancies: the amount of GPUs listed as belonging to the node in the slurm.conf file, the amount of Nvidia devices registered to the node in the dev directory, and the amount of CUDA capable devices in the node detected by deviceQuery. If these numbers do not all match, the node is flagged as discrepant, and added to the final report. A list of serial numbers corresponding to the working GPUs on the discrepant node is provided as well.

Nodes which contain discrepancies are often fixed by simply rebooting. To do this, discrepant nodes are sent a power cycle command via warewulf IPMI. Nodes which were flagged as unreachable during the SSH check are also issued a power cycle command. Occasionally, nodes cannot be succesfully rebooted with this command, so the status of each reboot command is included in the final report.

Each time this script is run, the names of all nodes which were succesfully issued a power cycle command are recorded. The next time the script is run, this list of rebooted nodes is parsed. If a node on the reboot list is no longer discrepant, it is removed from the list. If a node on the reboot list is still discrepant, an additional section will be added to the final report listing such nodes. This reboot list record can be erased by using the -c option.

A report of the cluster's GPU nodes is generated and sent to the user via email. This report contains a list of discrepant nodes, nodes which remain discrepant after a reboot, the status of reboot commands issued by the script, and nodes which couldn't be accessed via SSH.

## Options
-h: This option enables the .ignoreList.txt and .checkList.txt files to further constrain the list of GPU nodes checked by the script. If used, .checkList.txt should contain all nodes that should be checked, and .ignoreList.txt should contain all nodes that should not be checked. Nodes can be listed in either file as one node per line, or a range of nodes can be specified like so: n[<START_RANGE>-<END_RANGE>].\<PARTITION>

-c: This option wipes the data contained on the reboot list, ie data regarding previous reboots is removed when the scipt is run with this option

## Usage
This script generates a report on GPU nodes, which can then be acted upon by the cluster engineers to fix lingering discrepancies. As such, this script should be invoked once per day at 9:00 AM, and once again at 9:30 AM. The first invocation will generate a report listing all discrepant and inaccessible nodes, and attempt to reboot such nodes. The second invocation will generate a report listing nodes that remain inaccessible or discrepant after the reboot from the previous invocation, indicating further action is needed to repair the listed nodes. 

To accomplish this, two cron jobs should be run on the head node invoking this script. The first cron job should run every day at 9:00 AM, and should be run with the -c option. The second cron job should be run every day at 9:30 AM, and should be run without the -c option. The -l option can be used in either invocation to constrain the list of nodes the script checks.