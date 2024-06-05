

checkGpu.py when run locally on a gpu node:

.. figure:: doc/checkGpu_single_node.png
	:align: center
	:alt: bofhbot checkGpu output screenshot for single node

checkGpu.py when run via pdsh on several nodes in parallel:

.. figure:: doc/checkGpu_pdsh_sshErr.png
	:align: center
	:alt: bofhbot checkGpu output screenshot for single node

BofhBot
=======

The checkGpu branch is mostly for a single script:

`checkGpu.py`

which detect if any gpu is problematic and offline,
thereby needing intervention to bring gpu back online.
BOFH style: reboot the node, which fixes 80% of the cases :D

