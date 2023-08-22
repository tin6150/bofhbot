#!/bin/bash
ssh $1 "bash -s" << EOF
    # here you just type all your commmands, as you can see, i.e.
    module load python/3.6
    python /global/home/users/hchristopher/bofhbot/checkGpuOnNode.py
EOF
