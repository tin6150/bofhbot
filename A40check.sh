#!/bin/bash
# Job name:
#SBATCH --job-name=A40check
#
# Account:
#SBATCH --account=ac_scsguest
#
# Partition:
#SBATCH --partition=es1
#
#SBATCH --qos=es_normal
#
#SBATCH --nodes=1-14                                                                                                             
#
#SBATCH --constraint="es1_a40"
#
# Number of tasks (one for each GPU desired for use case) (example):
# SBATCH --ntasks=8
#
# Processors per task (please always specify the total number of processors twice the number of GPUs):
# SBATCH --cpus-per-task=1
#
#Number of GPUs, this can be in the format of "gpu:[1-4]", or "gpu:V100:[1-4] with the type included
#SBATCH --gres=gpu:A40:4
#
#SBATCH --exclusive
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
