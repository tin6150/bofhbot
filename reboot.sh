#!/bin/bash
# Job name:
#SBATCH --job-name=reboot
#
# Account:
#SBATCH --account=ac_scsguest
#
# Number of nodes:
#SBATCH --nodes=1
#
#SBATCH --exclusive
#
# Wall clock limit:
#SBATCH --time=1:00:00
#
## Command(s) to run (example):
BOFH_PATH="$( dirname -- "$( readlink -f -- "$0"; )"; )"
sudo -u tin /global/home/groups/scs/tin/remote_cycle_node.sh $SLURM_NODELIST $> "$BOFH_PATH"/data/sbatchReboots/"$SLURM_NODELIST".txt
REBOOT_STATUS="$cat $SLURM_NODELIST.txt | grep 'Chassis Power Control: Cycle' | wc -l"
if [[ $REBOOT_STATUS -eq 1 ]]
then
    echo $SLURM_NODELIST >> "$BOFH_PATH"/data/rebooted.txt
fi
