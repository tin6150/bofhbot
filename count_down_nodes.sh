#!/bin/bash 

## kludgy script to get idea of how many nodes are down, 
## and turned off to save power (cuz tripping breaker, etc)
## cronjob on master.brc as root
## 0 * * * *  /global/software/admin/count_down_nodes/count_down_nodes.sh | tee -a /global/software/admin/count_down_nodes/log.txt
## script in  /global/software/admin  slightly modified to be less verbose
## gsheet:  https://docs.google.com/spreadsheets/d/13Di2OdsszMtSqZ_vBUsZMpJf9cx1s1iE8xUw1-YnCUQ/edit#gid=0

## Tin 2022.1116

## date

## echo 'sinfo --Node | egrep idle | grep savio | wc -l'               ##
NumIdle=$(sinfo --Node | egrep idle | grep savio | wc -l)


## echo 'sinfo --Node | egrep idle\|drain | grep savio | wc -l'               ##
NumIdleDrain=$(sinfo --Node | egrep idle\|drain | grep savio | wc -l)

#  #echo 'sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| grep Pwr | wc -l'
#  #NumPwr=$(sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| grep Pwr | wc -l)

## echo 'sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| egrep Pwr\|sctrl_reservation | wc -l'               ##
#NumPwr=$(sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| egrep Pwr\|sctrl_reservation | wc -l)
NumPwr=$(sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| egrep PWR\|Power4 | wc -l)

## echo 'wwstats -s | egrep Dead\|utilization'               ##
#wwstats -s | egrep Dead\|utilization
NumWwDead=$(wwstats -s | egrep Dead | awk -F: '{print $2}')
NumWwUtil=$(wwstats -s | egrep utilization | awk -F: '{print $2}')

#echo $NumIdle,$NumIdleDrain,$NumPwr,$NumWwDead,$NumWwUtil | sed 's/,/\t/g'

Fecha=$(date +%m/%d_%H:%M)

Msg="$NumIdle,$NumIdleDrain,$NumPwr,$NumWwDead,$NumWwUtil,# $Fecha ## idle,idle+drain,PwrCons,Util"
echo $Msg | sed 's/,/\t/g'

#### echo "echo \t dont expand \t :-|"

####
#### by user visible partition, not cluster name...
#### scontrol show partitions | egrep PartitionName\|TotalNode

