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
echo hello
# hostname >> ~/bofhbot/data/reboot.txt
# reboot
