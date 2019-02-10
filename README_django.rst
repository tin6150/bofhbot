

BOFHbot django
==============

This is a new version of bofhbot, using django to create a 
RESTful client/server based version of bofhbot.

the cli version is needing a very wide screen.  
more features would need more columns, can't really fit in terminal.

So, have it renderable in browser instead.

Each feature become a REST (microservice) call.
- which set of host responds to ssh
- which set of host responds to ping
- which set of host responds to ipmi

resunt will be in json format, the browser can render which ever column is needed.

potentially, can have a cli client that query the browser.


BOFHbot REST API 
----------------

early thought process:

hmm... maybe start with looking what slurm api provides, how it does sinfo -RSE
depending how it provide the result/format, maybe then make this API to follow that...

GET URI:

/api/v1/sinfo           # current output of bofhbot --color ??
/api/v1/group-list      # list cluster, but get info from pdsh groups


/api/v1/status-ping?g=sinfo     # special case, get nodelist from sinfo -RSE
/api/v1/status-ping?g=savio3    # group (cluster) = savio3 node ping status
/api/v1/status-ping?g=all       # ping status of all nodes  

/api/v1/status-ssh?g=sinfo     # special case, get nodelist from sinfo -RSE

/api/v1/status-uptime?g=sinfo     # special case, get nodelist from sinfo -RSE
/api/v1/df?g=sinfo                       # df (for all)
/api/v1/df/tmp?g=sinfo                   # df for tmp only, implement as child?

/api/v1/status-ipmi-reachable?g=sinfo   # whether responding to ipmi cmd
/api/v1/status-ipmi-state?g=sinfo       # query ipmi for whether power is on/off


/api/v1/hostinfo?h=n0000.savio3         # need this?  store info of sinfo -RSE of a given host, so that it can be rendered into output?  
        # but may want the microservice to query for this and provide into json, 
        # rather than client asking everynode one at a time...


POST URI:

/api/v2/reboot?h=n0000.savio3           # action to reboot a node

Django enabling feature
-----------------------

provide a IPMI power cycle button to reboot a node.
Req authentication in such case.  Maybe tap into OTP, maybe the MProxy that Globus use and create a x-hours token.
this way, if django server for bofhbot is running as root, 
intern can click on power cycle, prompted for password, and reboot.
the roles control would then be in django, not sudoers.  (do i want to read from sudoers?)

it should provide a very granual approach, severly limiting possible damage from mistake.

hmm, maybe have way to do tail -f and other stuff in REST 



AI
--

only nodes where deemed reboot is appropriate and likely good fix, only then would "ipmi cycle" button be presented/enabled.

other AI feature could come later as more logs are parsed.

the server arch also allow for monitoring sinfo -RSE, 
keep a history of what has been done to nodes, etc.
so that AI can give action recommendation 



PS
--


could have done this as a separete github project/repo, but didn't want to create another project.  
the former bofhbot.py cli command would likely become a very separate/independent script, albeit with very similar goal in mind (which is why i kept everything in here).



