
echo 'sinfo --Node | egrep idle | grep savio | wc'
sinfo --Node | egrep idle | grep savio | wc

echo 'sinfo --Node | egrep idle\|drain | grep savio | wc'
sinfo --Node | egrep idle\|drain | grep savio | wc

echo 'wwstats -s | egrep Dead\|utilization'
wwstats -s | egrep Dead\|utilization
