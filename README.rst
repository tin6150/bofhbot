
master branch: |status1| // nodelist branch: |status2|

.. |status1| image:: https://travis-ci.org/tin6150/bofhbot.svg?branch=master
    :target: https://travis-ci.org/tin6150/bofhbot

.. |status2| image:: https://travis-ci.org/tin6150/bofhbot.svg?branch=nodelist
    :target: https://travis-ci.org/tin6150/bofhbot 


BofhBot
=======

An enhanced sinfo -R for lazy sys admins--aka bofh :)

v2 rest+client
==============

actually, don't remember if this was using REST API format.

There are two steps to run this version.

First step collect all the info, formatted into a json.

Second step grab the json and analyze, provide output or suggestion for fix, depending on option used.

see `./bot --help` for further detail.


Step one could run like a server that generate json file

Step two could use a web browser based client to interact with the json 


Usage
-----

one time setup::

        module load python/3.6
        python3 -m venv .
        source bin/activate
        pip install -r requirements.txt

regular run::

	source bin/activate
	./bot check > botChk.out.json
	reset
	cat botChk.out.json | ./bot suggest -i | less


My teamates have not able to stomach it yet, but a cron job could be setup so simple failures can be fixed automatically by the bot as:: 

    bot check | bot suggest | bash 

Known issues
------------

- terminal may get corrupted after runnint the `bot` command, use `reset` to restore terminal functionality.
  
