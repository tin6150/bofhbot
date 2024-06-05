


# dell
ipmitool sensor |grep Pwr

# savio2_knl
# 96-208W, many around 160W
#pdsh -w n0[254-289].savio2,n0[295-297].savio2 ipmitool sensor |grep Pwr |sort -n
pdsh -w n0[254-289].savio2,n0[295-297].savio2 ipmitool sensor |grep Watt |sort -n


# savio3, savio3_m96,savio3_m384
# 392W high, 168-280
#pdsh -w n0[006-125].savio3  ipmitool sensor | grep Pwr 
pdsh -w n0[006-125].savio3  ipmitool sensor | grep Watt


# savio2 : 36W - 234W 
pdsh -w n0[000-034].savio2  ipmitool sensor | grep Watt


# savio2_1080ti # SMC ? ... 195-435W
#pdsh -w n0[298-301].savio2  ipmitool sensor | grep Power 
pdsh -w n0[298-301].savio2  ipmitool sensor | grep Watt

# savio2_knl
pdsh -w n0[254-281].savio2  ipmitool sensor | grep Watt



# savio1, no Power number...  Amp 5-25, many ~10-17
pdsh -w n0[004-071].savio1  ipmitool sensor | grep Amp


# incomplete.  collected the data in spreadsheet (DC Map for Warren)
# 
