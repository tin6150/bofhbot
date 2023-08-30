#!/bin/bash
# load python 3.6
module load python/3.6
# clear file containing sinfo output
> ~/bofhbot/data/gpuNodes.txt
# get cluster name
CLUSTER=$(sacctmgr list cluster | tail -1 | awk '{print $1;}')
# verify clush is installed
CLUSH_INSTALLED=$((pip list | grep ClusterShell) | wc -l)
BRC="brc"
LRC="perceus-00"
# if cluster is BRC, look for savio gpu partitions
if [[ $CLUSTER = $BRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'savio2_gpu\|savio2_1080ti\|savio3_gpu\|savio4_gpu' > ~/bofhbot/data/gpuNodes.txt
# if cluster is LRC, look for es1, etna_gpu, and alice partitions
elif [[ $CLUSTER = $LRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'es1\|etna_gpu\|alice' > ~/bofhbot/data/gpuNodes.txt    
# if neither, abort
else
    echo "Unknown Cluster; can't parse sinfo"
    exit
fi
# if clush is not installed, abort
if [[ $CLUSH_INSTALLED -ne 1 ]]
then
    echo "ClusterShell not installed, try pip install --user ClusterShell"
    exit
fi
wait
# clear all temporary data files
> ~/bofhbot/data/reachableNodes.txt
> ~/bofhbot/data/unreachableNodes.txt
> ~/bofhbot/data/errorEmail.txt
> ~/bofhbot/data/fullReport.txt
> ~/bofhbot/data/discrepantNodes.txt
# check which nodes can be ssh-ed
python sshCheck.py
wait
truncate -s -1 ~/bofhbot/data/reachableNodes.txt
# run checkGpuOnNode on every reachable node
clush -w $(cat ~/bofhbot/data/reachableNodes.txt) python ~/bofhbot/checkGpuOnNode.py
wait
# sort nodes first by cluster, then by node number
~/bofhbot/sortNodes.sh
echo >> ~/bofhbot/data/errorEmail.txt
echo >> ~/bofhbot/data/errorEmail.txt
echo "Nodes still missing GPU(s) after reboot" >> ~/bofhbot/data/errorEmail.txt
# attempt to reboot discrepant nodes, add nodes that weren't fixed by reboot to report
python -u reboot.py
wait
echo >> ~/bofhbot/data/errorEmail.txt
echo >> ~/bofhbot/data/errorEmail.txt
# add nodes that could not ssh-ed to section of report
echo "Down Nodes, can't SSH" >> ~/bofhbot/data/errorEmail.txt
echo >> ~/bofhbot/data/errorEmail.txt
cat ~/bofhbot/data/errorEmail.txt ~/bofhbot/data/unreachableNodes.txt >> ~/bofhbot/data/fullReport.txt
# email report to henry and tin
python emailErrorBot.py
exit
