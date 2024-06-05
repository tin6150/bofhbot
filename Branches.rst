
master: main branch, working bofhbot.py.  

sn_main: fork of main on 2024.0605, plan to merge other code into master for a bit to ack other's contribution and try to get to state where other can work.


rest: developing botd, api server daemon with REST interface using FLASK


TBA:

* create a slurm_lib.py with code from bofhbot.py
  take the stuff that use sinfo-RSE
  maybe even all the ssh code... 
  create a lib that botd can also tab into


* don't seems to have a python api for slurm :(
* this maybe usable, but don't seems to have sinfo:
  https://github.com/PySlurm/pyslurm/tree/18.08.0

* this seems to be only for submitting job...
  https://pypi.org/project/slurmpy/

