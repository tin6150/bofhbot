#!/bin/bash
# Job name:
#SBATCH --job-name=V100check
#
# Account:
#SBATCH --account=ac_scsguest
#
# Partition:
#SBATCH --partition=es1
#
#SBATCH --qos=es_normal
#
#SBATCH --exclusive 
#
#SBATCH --nodes=1-15
#
#SBATCH --constraint="es1_v100"
#
#SBATCH --exclude=n0012.es1,n0013.es1
#
# Number of tasks (one for each GPU desired for use case) (example):
# SBATCH --ntasks=2
#
# Processors per task (please always specify the total number of processors twice the number of GPUs):
# SBATCH --cpus-per-task=2
#
# Number of GPUs, this can be in the format of "gpu:[1-4]", or "gpu:V100:[1-4] with the type included
#SBATCH --gres=gpu:V100:2
#
# Wall clock limit:
#SBATCH --time=0:01:00
#
#SBATCH --wait
#
#SBATCH 
#
## Command(s) to run (example):
module load python
clush -w $SLURM_NODELIST python ~/bofhbot/checkGpuOnNode.py
