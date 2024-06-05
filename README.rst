
master branch: |status1| // nodelist branch: |status2|

.. |status1| image:: https://travis-ci.org/tin6150/bofhbot.svg?branch=master
    :target: https://travis-ci.org/tin6150/bofhbot

.. |status2| image:: https://travis-ci.org/tin6150/bofhbot.svg?branch=nodelist
    :target: https://travis-ci.org/tin6150/bofhbot 


.. figure:: doc/bofhbot_screenshot2.png
	:align: center
	:alt: bofhbot v1 output screenshot

BofhBot
=======

An enhanced sinfo -R for lazy sys admins--aka bofh :)

BOFH is known to be a lazy slacker.
Laziness is a virtue.  which is why a bot is born to do the job for BOFH.
In this case, look at sinfo -R and help repair slurm nodes that are sick.
At first it would just help with some of the initial troubleshooting manial work, 
such as see if node:

- is pingable
- can be ssh to
- nhc report status
- some manual mount and checks not corrently configured in nhc cuz of histerical reason
- ipmi reachability (eg can ipmi power status/cycle) revive the node
- slurm pid 
- node status (presumably no running job on the node)
- recommended action
- confidence of recommendation


This repo now has several branches representing various version/flavor of this project.
The salient branches are:

- v1_classic_cli : bofhbot with wide screen output, color coded for sys admin eval
- v2_rest+client : bot check | bot suggest # commands that could be cron'd for automatic node fix
- checkGpu       : script to check GPU status, maybe take corrective action.

see README in the corresponding branches for more details of each version

Future work
===========

- Connect to slack to show error status, get confirmation from sysadmin before taking corrective action 
  (eg rebooting an already drained node).
  Connectivity to slack need to be worked on, which may need adding a fat library to this.
  If bot truly become reactive, need to explore security aspects.  
  Receiving command is obvious first challenge for HPC center.
  But DoS attack can likely be largely mitigated if commands allowed are time bound, only valid when node is already drained and thus no effect on running jobs.
  
- Other scripts to check hardware health status (eg alert LED shown on chassis)

Credit
======

- Nicolas Chan wrote most of the code for v2
- Tin Ho seeded this project.
- Other who have contributed: Hamza Kundi, Frank Chen, Zashary.  

Thank you!


License
=======
BSD 3-clause, as indicated in the github license choice for this project.


Other names
===========

* slurmbot
* sinfobot
* hpcbot
* bofhbot - yeah, i like this!


.rst reference
==============

- http://docutils.sourceforge.net/docs/user/rst/quickref.html
- http://www.sphinx-doc.org/en/1.3/markup/code.html


apparently boxing title with ===== above and below a line could throw off validator.
was that a .md feature?  but it had worked on short rst...
validate rst as:

::

        pip install rstvalidator
        python -m rstvalidator README.rst

