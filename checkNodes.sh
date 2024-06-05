#!/bin/bash
echo ==== CheckGpu Begin ====
BOFH_PATH="$( dirname -- "$( readlink -f -- "$0"; )"; )"
CLEAN=0
LISTS=0
while getopts ":c:l" option; do
  case $option in
    c)
      # code to execute when flag1 is provided
      echo Running clean
      CLEAN=1
      ;;
    l)
      # code to execute when flag2 is provided
      echo Running with list constraints
      LISTS=1
      ;;
    *)
      # code to execute when an unknown flag is provided
      echo "Usage: $0 [-c run without previous reboot data] [-l run with allow and ignore list constraints]"
      exit 1
      ;;
  esac
done
# load python 3.6
echo Using python 3.6
module load python/3.6
# create temporary data files
echo Touching data files
touch "$BOFH_PATH"/data/allNodes.txt
touch "$BOFH_PATH"/data/discrepantNodes.txt
touch "$BOFH_PATH"/data/errorEmail.txt
touch "$BOFH_PATH"/data/fullReport.txt
touch "$BOFH_PATH"/data/gpuNodes.txt
touch "$BOFH_PATH"/data/nonDiscrepantNodes.txt
touch "$BOFH_PATH"/data/reachableNodes.txt
touch "$BOFH_PATH"/data/rebooted.txt
touch "$BOFH_PATH"/data/unreachableNodes.txt
touch "$BOFH_PATH"/data/currentReboot.txt
# clear file containing sinfo output
> "$BOFH_PATH"/data/gpuNodes.txt
# get cluster name
CLUSTER=$(sacctmgr list cluster | tail -1 | awk '{print $1;}')
echo Cluster: $CLUSTER
# verify clush is installed
CLUSH_INSTALLED=$((pip list | grep ClusterShell) | wc -l)
BRC="brc"
LRC="perceus-00"
# FIND_REBOOT=$(find /global/home/groups/scs/tin/remote_cycle_node.sh)
# REBOOT_PATH='/global/home/groups/scs/tin/remote_cycle_node.sh'
# if cluster is BRC, look for savio gpu partitions
echo Getting GPU nodes from sinfo
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
# if [[ $FIND_REBOOT != $REBOOT_PATH ]]
# then
    # echo "remote_cycle_node.sh is not in expected path"
    # exit
# fi
wait
# clear all temporary data files
echo Wiping data files from previous invocation
> "$BOFH_PATH"/data/allNodes.txt
> "$BOFH_PATH"/data/reachableNodes.txt
> "$BOFH_PATH"/data/unreachableNodes.txt
> "$BOFH_PATH"/data/errorEmail.txt
> "$BOFH_PATH"/data/fullReport.txt
> "$BOFH_PATH"/data/discrepantNodes.txt
> "$BOFH_PATH"/data/nonDiscrepantNodes.txt
> "$BOFH_PATH"/data/currentReboot.txt
if [[ $CLEAN -eq 1 ]]
then
    echo Wiping reboot data
    > "$BOFH_PATH"/data/rebooted.txt
fi
# check which nodes can be ssh-ed
echo Checking which nodes can be accessed via SSH
python "$BOFH_PATH"/sshCheck.py -p $BOFH_PATH -l $LISTS
wait
truncate -s -1 "$BOFH_PATH"/data/reachableNodes.txt
REACHABLE=$(grep -o '\.' "$BOFH_PATH"/data/reachableNodes.txt | wc -l )
UNREACHABLE=$(grep -o '\.' "$BOFH_PATH"/data/unreachableNodes.txt | wc -l)
echo $REACHABLE nodes reachable
echo $UNREACHABLE nodes unreachable
# run checkGpuOnNode on every reachable node
echo Running checkGpu on reachable nodes
clush -w $(cat "$BOFH_PATH"/data/reachableNodes.txt) python "$BOFH_PATH"/checkGpuOnNode.py -p $BOFH_PATH
wait
cat "$BOFH_PATH"/data/emailContent/*.txt >> "$BOFH_PATH"/data/errorEmail.txt
cat "$BOFH_PATH"/data/discrepantNodes/*.txt >> "$BOFH_PATH"/data/discrepantNodes.txt
cat "$BOFH_PATH"/data/nonDiscrepantNodes/*.txt >> "$BOFH_PATH"/data/nonDiscrepantNodes.txt
rm -r "$BOFH_PATH"/data/emailContent/*
rm -r "$BOFH_PATH"/data/discrepantNodes/*
rm -r "$BOFH_PATH"/data/nonDiscrepantNodes/*
# sort nodes first by cluster, then by node number
echo Sorting output
"$BOFH_PATH"/sortNodes.sh
echo >> "$BOFH_PATH"/data/errorEmail.txt
# echo "Nodes still missing GPU(s) after reboot" >> "$BOFH_PATH"/data/errorEmail.txt
# attempt to reboot discrepant nodes, add nodes that weren't fixed by reboot to report
sed -i '/^$/d' "$BOFH_PATH"/data/rebooted.txt
# python -u "$BOFH_PATH"/reboot.py -p $BOFH_PATH
# wait
# echo >> "$BOFH_PATH"/data/errorEmail.txt
# echo >> "$BOFH_PATH"/data/errorEmail.txt
# add nodes that could not ssh-ed to section of report
echo "Down Nodes, can't SSH" >> "$BOFH_PATH"/data/errorEmail.txt
echo >> "$BOFH_PATH"/data/errorEmail.txt
cat "$BOFH_PATH"/data/errorEmail.txt "$BOFH_PATH"/data/unreachableNodes.txt >> "$BOFH_PATH"/data/fullReport.txt
# email report to henry and tin
echo Sending email
python "$BOFH_PATH"/emailErrorBot.py -p $BOFH_PATH
cp "$BOFH_PATH"/data/fullReport.txt "$BOFH_PATH"/data/logs/$(date +'%m-%d-%Y_%H%M').txt
echo ==== CheckGpu End ====
exit
