#!/bin/bash
module load python/3.6
> /global/home/users/hchristopher/bofhbot/data/gpuNodes.txt
CLUSTER=$(sacctmgr list cluster | tail -1 | awk '{print $1;}')
BRC="brc"
if [[ $CLUSTER = $BRC ]]
then
   sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'savio2_gpu\|savio2_1080ti\|savio3_gpu\|savio4_gpu' > /global/home/users/hchristopher/bofhbot/data/gpuNodes.txt
else
   sinfo -N -S %E --format="%P %N %6t %19H %9u %E"  | grep 'es1' > /global/home/users/hchristopher/bofhbot/data/gpuNodes.txt    
fi
wait
> /global/home/users/hchristopher/bofhbot/data/reachableNodes.txt
> /global/home/users/hchristopher/bofhbot/data/unreachableNodes.txt
> /global/home/users/hchristopher/bofhbot/data/errorEmail.txt
> /global/home/users/hchristopher/bofhbot/data/fullReport.txt
python sshCheck.py
wait
truncate -s -1 /global/home/users/hchristopher/bofhbot/data/reachableNodes.txt
truncate -s -1 /global/home/users/hchristopher/bofhbot/data/unreachableNodes.txt

clush -w $(cat /global/home/users/hchristopher/bofhbot/data/reachableNodes.txt) python /global/home/users/hchristopher/bofhbot/checkGpuOnNode.py
echo >> /global/home/users/hchristopher/bofhbot/data/errorEmail.txt
echo >> /global/home/users/hchristopher/bofhbot/data/errorEmail.txt
echo "Down Nodes, can't SSH" >> /global/home/users/hchristopher/bofhbot/data/errorEmail.txt
echo >> /global/home/users/hchristopher/bofhbot/data/errorEmail.txt
cat /global/home/users/hchristopher/bofhbot/data/errorEmail.txt /global/home/users/hchristopher/bofhbot/data/unreachableNodes.txt >> /global/home/users/hchristopher/bofhbot/data/fullReport.txt
python emailErrorBot.py
