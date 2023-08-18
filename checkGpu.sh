#!/bin/bash
> /global/home/users/hchristopher/errorEmail.txt
sbatch ~/batch_scripts/A40check.sh
wait
sbatch ~/batch_scripts/V100check.sh
wait
sbatch ~/batch_scripts/2080TIcheck.sh
wait
python ~/bofhbot/emailErrorBot.py
