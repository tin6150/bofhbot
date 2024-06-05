module load python/3.6

# run as: 
# ./checkGpuOnNode_sav3.sh 2>&1 | tee chkGpu.BRC.2024.0216.OUT


date

#pdsh -w n0[143-145,174-176,258-261].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3,n0[012-014,018-020,026,223-226,298-302].savio2 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py
#pdsh -w n0[143-145,174-176,258-261].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3,n0[012-014,018-020,227-229,298-302].savio2 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py

#pdsh -w n0[120-141].savio4,n0[143-145,174-176].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3,n0[012-014,018-020,227-229,298-302].savio2,n0[120-146].savio4 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py
# took out 258-261.sav3 sergey
# n0140-145.savio4 not parsed correctly cuz wwsh hostname added brc.berkeley.edu
#pdsh -w n0[120-145].savio4,n0[143-145,174-176].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py
pdsh -w n0[120-145].savio4,n0[143-145,174-176].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264,273-283].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py

exit $?


# pdsh -w n0[175,176,143,144].savio3 nhc
# tail -1 ... | sudo bash :P
#pdsh -w n0[120-145].savio4,n0[143-145,174-176,258-261].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3,n0[012-014,018-020,026,223-226,227-229,298-302].savio2 systemctl stop irqbalance
pdsh -w n0[120-145].savio4,n0[143-145,174-176,258-261].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264,273-283].savio3,n0[012-014,018-020,026,223-226,227-229,298-302].savio2 systemctl stop irqbalance
