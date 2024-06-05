date

echo 'sinfo --Node | egrep idle | grep savio | wc -l'
NumIdle=$(sinfo --Node | egrep idle | grep savio | wc -l)


echo 'sinfo --Node | egrep idle\|drain | grep savio | wc -l'
NumIdleDrain=$(sinfo --Node | egrep idle\|drain | grep savio | wc -l)

#echo 'sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| grep Pwr | wc -l'
#NumPwr=$(sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| grep Pwr | wc -l)

echo 'sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| egrep Pwr\|sctrl_reservation | wc -l'
NumPwr=$(sinfo --Node -R -S %E --format="%9u %19H %6t %N %E"| egrep Pwr\|sctrl_reservation | wc -l)

echo 'wwstats -s | egrep Dead\|utilization'
#wwstats -s | egrep Dead\|utilization
NumWwDead=$(wwstats -s | egrep Dead | awk -F: '{print $2}')
NumWwUtil=$(wwstats -s | egrep utilization | awk -F: '{print $2}')

#echo $NumIdle,$NumIdleDrain,$NumPwr,$NumWwDead,$NumWwUtil
echo $NumIdle,$NumIdleDrain,$NumPwr,$NumWwDead,$NumWwUtil | sed 's/,/\t/g'


####
#### by user visible partition, not cluster name...
#### scontrol show partitions | egrep PartitionName\|TotalNode

