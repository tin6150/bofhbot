

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


Django enabling feature
-----------------------

provide a IPMI power cycle button to reboot a node.
Req authentication in such case.  Maybe tap into OTP, maybe the MProxy that Globus use and create a x-hours token.
this way, if django server for bofhbot is running as root, 
intern can click on power cycle, prompted for password, and reboot.
the roles control would then be in django, not sudoers.  (do i want to read from sudoers?)

it should provide a very granual approach, severly limiting possible damage from mistake.

hmm, maybe have way to do tail -f and other stuff in REST 


could have done this as a separete github project/repo, but didn't want to create another project.  
the former bofhbot.py cli command would likely become a very separate/independent script, albeit with very similar goal in mind (which is why i kept everything in here).



