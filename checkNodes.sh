#!/bin/bash
module load python/3.6
> ~/bofhbot/data/gpuNodes.txt
CLUSTER=$(sacctmgr list cluster | tail -1 | awk '{print $1;}')
CLUSH_INSTALLED=$((pip list | grep ClusterShell) | wc -l)
BRC="brc"
LRC="perceus-00"
if [[ $CLUSTER = $BRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'savio2_gpu\|savio2_1080ti\|savio3_gpu\|savio4_gpu' > ~/bofhbot/data/gpuNodes.txt
elif [[ $CLUSTER = $LRC ]]
then
    sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'es1' > ~/bofhbot/data/gpuNodes.txt    
else
    echo "Unknown Cluster; can't parse sinfo"
    exit
fi
if [[ $CLUSH_INSTALLED -ne 1 ]]
then
    echo "ClusterShell not installed, try pip install --user ClusterShell"
    exit
fi
wait
> ~/bofhbot/data/reachableNodes.txt
> ~/bofhbot/data/unreachableNodes.txt
> ~/bofhbot/data/errorEmail.txt
> ~/bofhbot/data/fullReport.txt
python sshCheck.py
wait
truncate -s -1 ~/bofhbot/data/reachableNodes.txt
clush -w $(cat ~/bofhbot/data/reachableNodes.txt) python ~/bofhbot/checkGpuOnNode.py
~/bofhbot/sortNodes.sh
echo >> ~/bofhbot/data/errorEmail.txt
echo >> ~/bofhbot/data/errorEmail.txt
echo "Down Nodes, can't SSH" >> ~/bofhbot/data/errorEmail.txt
echo >> ~/bofhbot/data/errorEmail.txt
cat ~/bofhbot/data/errorEmail.txt ~/bofhbot/data/unreachableNodes.txt >> ~/bofhbot/data/fullReport.txt
python emailErrorBot.py
exit
