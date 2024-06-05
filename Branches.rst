
master: main branch, working bofhbot.py.  



rest: developing botd, api server daemon with REST interface using FLASK

v2: Nick's REST + client branch, working bot suite of script.

checkGpu: mostly just checkGpu.py script, but use some fn like vprint from library.
(branched off rest_draft_plan, which may need careful merge.  
or just rewrite completely when restart coding)

TBD:
v1.1: maybe create this from rest_draft_plan branch, as that's the bofhbot.py in regular use

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

