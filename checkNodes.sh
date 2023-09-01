#!/bin/bash
BOFH_PATH="$( dirname -- "$( readlink -f -- "$0"; )"; )"
# load python 3.6
module load python/3.6
# create temporary data files
touch "$BOFH_PATH"/data/allNodes.txt
touch "$BOFH_PATH"/data/discrepantNodes.txt
touch "$BOFH_PATH"/data/errorEmail.txt
touch "$BOFH_PATH"/data/fullReport.txt
touch "$BOFH_PATH"/data/gpuNodes.txt
touch "$BOFH_PATH"/data/nonDiscrepantNodes.txt
touch "$BOFH_PATH"/data/reachableNodes.txt
touch "$BOFH_PATH"/data/rebooted.txt
touch "$BOFH_PATH"/data/unreachableNodes.txt
touch "$BOFH_PATH"/data/failedReboot.txt
# clear file containing sinfo output
> "$BOFH_PATH"/data/gpuNodes.txt
# get cluster name
CLUSTER=$(sacctmgr list cluster | tail -1 | awk '{print $1;}')
# verify clush is installed
CLUSH_INSTALLED=$((pip list | grep ClusterShell) | wc -l)
BRC="brc"
LRC="perceus-00"
FIND_REBOOT=$(find /global/home/groups/scs/tin/remote_cycle_node.sh)
REBOOT_PATH='/global/home/groups/scs/tin/remote_cycle_node.sh'
# if cluster is BRC, look for savio gpu partitions
if [[ $CLUSTER = $BRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'savio2_gpu\|savio2_1080ti\|savio3_gpu\|savio4_gpu' > "$BOFH_PATH"/data/gpuNodes.txt
# if cluster is LRC, look for es1, etna_gpu, and alice partitions
elif [[ $CLUSTER = $LRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'es1\|etna_gpu\|alice' > "$BOFH_PATH"/data/gpuNodes.txt    
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
if [[ $FIND_REBOOT != $REBOOT_PATH ]]
then
    echo "remote_cycle_node.sh is not in expected path"
    exit
fi
wait
# clear all temporary data files
> "$BOFH_PATH"/data/allNodes.txt
> "$BOFH_PATH"/data/reachableNodes.txt
> "$BOFH_PATH"/data/unreachableNodes.txt
> "$BOFH_PATH"/data/errorEmail.txt
> "$BOFH_PATH"/data/fullReport.txt
> "$BOFH_PATH"/data/discrepantNodes.txt
> "$BOFH_PATH"/data/nonDiscrepantNodes.txt
> "$BOFH_PATH"/data/failedReboot.txt
# check which nodes can be ssh-ed
python "$BOFH_PATH"/sshCheck.py -p $BOFH_PATH
wait
truncate -s -1 "$BOFH_PATH"/data/reachableNodes.txt
# run checkGpuOnNode on every reachable node
clush -w $(cat "$BOFH_PATH"/data/reachableNodes.txt) python "$BOFH_PATH"/checkGpuOnNode.py -p $BOFH_PATH
wait
cat "$BOFH_PATH"/data/emailContent/*.txt >> "$BOFH_PATH"/data/errorEmail.txt
cat "$BOFH_PATH"/data/discrepantNodes/*.txt >> "$BOFH_PATH"/data/discrepantNodes.txt
cat "$BOFH_PATH"/data/nonDiscrepantNodes/*.txt >> "$BOFH_PATH"/data/nonDiscrepantNodes.txt
rm -r "$BOFH_PATH"/data/emailContent/*
rm -r "$BOFH_PATH"/data/discrepantNodes/*
rm -r "$BOFH_PATH"/data/nonDiscrepantNodes/*
# sort nodes first by cluster, then by node number
"$BOFH_PATH"/sortNodes.sh
echo >> "$BOFH_PATH"/data/errorEmail.txt
echo "Nodes still missing GPU(s) after reboot" >> "$BOFH_PATH"/data/errorEmail.txt
# attempt to reboot discrepant nodes, add nodes that weren't fixed by reboot to report
sed -i '/^$/d' "$BOFH_PATH"/data/rebooted.txt
python -u "$BOFH_PATH"/reboot.py -p $BOFH_PATH
wait
echo >> "$BOFH_PATH"/data/errorEmail.txt
echo >> "$BOFH_PATH"/data/errorEmail.txt
# add nodes that could not ssh-ed to section of report
echo "Down Nodes, can't SSH" >> "$BOFH_PATH"/data/errorEmail.txt
echo >> "$BOFH_PATH"/data/errorEmail.txt
cat "$BOFH_PATH"/data/errorEmail.txt "$BOFH_PATH"/data/unreachableNodes.txt >> "$BOFH_PATH"/data/fullReport.txt
# email report to henry and tin
python "$BOFH_PATH"/emailErrorBot.py -p $BOFH_PATH
exit
