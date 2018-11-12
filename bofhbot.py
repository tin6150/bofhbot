#!/usr/bin/env python3

#### module load python/3.6
#### need python3 cuz exception handling for ssh call

# bofhbot - An enhanced sinfo -R for lazy sys admins--aka bofh :)
# see README.rst for detailed description (and license).
# tin (at) berkeley.edu 

# future exercise can likely write this using functional approach
# for now, regular scripting style. 
# OOP can have a structure with problem node as list of objects
# and parallel ssh/ping/etc check on them 
# to speed up output


import os
import re # regex
import time
import argparse
import shlex
import sys
import subprocess
#import paramiko  # could abandone
from multiprocessing import Pool

# global param :)  better as OOP get() fn or some such.  
sinfoRSfile = '/var/tmp/sinfo-RSE.txt'
#sinfoRSfile = 'sinfo-RSE-eg.txt.head5'
nodeColumnIndex=3
nodeColumnIndex=0

# programmer aid fn
# dbgLevel 3 (ie -ddd) is expected by user troubleshooting problem parsing input file
# currently most detailed output is at level 5 (ie -ddddd) and it is eye blurry even for programmer
#dbgLevel = 0  
##dbgLevel = 1   use -ddddd now
def dbg( level, strg ):
    if( dbgLevel >= level ) : 
        print( "<!--dbg%s: %s-->" % (level, strg) )

def vprint( level, strg ):
    if( verboseLevel >= level ) : 
        print( "%s" % strg )

#def parseCliArg():
#    optino1 = sys.argv[1]
# parseCliArg()-end
# Sorry Nick, I much rather use argparse. -Tin


def process_cli() :
        # https://docs.python.org/2/howto/argparse.html#id1
        parser = argparse.ArgumentParser( description='This script give enhanced status of problem nodes reported by eg sinfo -R')
        parser.add_argument('-n', '--nodelist',  help="Use a specified nodelist file",  required=False, default="/etc/pdsh/all" ) 
        parser.add_argument('-v', '--verboselevel', help="Add verbose output. Up to -vv maybe useful. ", action="count", default=0)
        parser.add_argument('-d', '--debuglevel', help="Debug mode. Up to -ddd useful for troubleshooting input file parsing. -ddddd intended for coder. ", action="count", default=0)
        parser.add_argument('--version', action='version', version='%(prog)s 0.2.  ')
        args = parser.parse_args()
        global dbgLevel 
        global verboseLevel 
        dbgLevel = args.debuglevel
        verboseLevel = args.verboselevel
        return args
# end process_cli() 




# get ouptupt of sinfo -R -S ... 
# return a list...  hash... oop nodelist?
def generateSinfo() :
    # https://github.com/PySlurm/pyslurm  but then have to install python lib before being able to use script :-/
    #sinfoRS = subprocess.run(['sinfo', '-R -S %E --format="%9u %19H %6t %N %E"'])
    #cmd = 'sinfo -R -S %E --format="%9u %19H %6t %N %E" ' + " > "  +  sinfoRSfile     # more human readable
    cmd = 'sinfo -N -R -S %E --format="%N %6t %19H %9u %E" ' + " > "  +  sinfoRSfile   # node first, one node per line :)
    command = cmd
    dbg(5, command)
    #sinfoRSout = subprocess.call(shlex.split(command))
    sinfoRSout = os.system(command) # exit code only from mos.system()
    dbg(5, sinfoRSout )
    return sinfoRSout 
    #+sinfoRS = os.popen(cmd).read()
    #sinfoRS = open('sinfo-RSE-eg.txt.head5','r')
#generateSinfo()-end

#def getSinfo():
def buildSinfoList():
    sinfoRS = open( sinfoRSfile,'r')
    #print( sinfoRS )
    #linelist = sinfoRS.split('\s')
    sinfoList = [ ] 
    for line in sinfoRS :
        dbg(4, "processing '%s'" % line.rstrip() )
        #currentLine = re.search( '([\S]+[\s]+)*', line.rstrip())   # truncate long lines :(  still match empty line :(
        currentLine = re.search( '^$', line )   # ie blank line
        if( currentLine ) :
            dbg(5, "skipping blank line" )
        else :
            dbg(5, "will add:  '%s' to sinfoList" % line.rstrip() )
            sinfoList.append( line.rstrip() )
    #print( sinfoList )
    return sinfoList 
# buildSinfoList()-end


# Input: array list of lines with output of sinfo -R -S ...
# OUTPUT: array list of nodes (maybe empty)
# may not use this fn anymore
def sinfoList2nodeList( sinfoList ):
    #--linenum = 0 
    #--item = 0
    nodeList = [ ] 
    for line in sinfoList :
        nodeList.append( getNodeList( line ) )
    return nodeList
# sinfoList2nodeList()-end


# Input: single line of output of sinfo -R -S ...
# OUTPUT: array list of nodes (maybe empty)
# for now return a list of nodes needing ping/ssh info
def getNodeList( sinfoLine ) :
        line = sinfoLine
        nodeList = [ ]
        #node = re.search( '(n\d\d\d\d\.[\w]+)[,]*', str, re.U|re.I )  # only handle 1 node for now...

        #print( "%d :: %s " % (linenum, sinfoRS[linenum]) )
        lineItem = line.split()
        try :
            #str = lineItem[3]
            str = lineItem[nodeColumnIndex]  # nodeColumnIndex is global param (++better OOP sinfo.nodeColumnIndex() )
        except IndexError :
            str = "NADA"
        #print( "%d :: %s " % (linenum, lineItem[0]) )
        #dbgstr = "%d :: %s " % (linenum, str) 
        #dbg( 3, dbgstr )
        #if( str ~= 'n[\d\d\d\d]' ) : 
        #node = re.search( r'(n[\d\d\d\d])', str, re.U|re.I|re.VERBOSE )  
        node = re.search( '(n\d\d\d\d\.[\w]+)[,]*', str, re.U|re.I )  # only handle 1 node for now...
        if node : 
            #nodeList[item] = str
            dbgstr =  "===%s===" % node.group(1) 
            dbg(3, dbgstr)
            nodeList.append( node.group(1) )
        return nodeList
#getNodeList()-end

# like sinfoList2nodeList( sinfoList ), but only use 1 line as input
# return only first node for now
# try to ssh to a node and see what happens to it
# return a variety of string depending of status of the node.  eg Up, TimeOut, Down?, askPassword
# https://github.com/matthew-li/lbnl_scripts/blob/master/check_mounted_systems.py
def checkSsh( node ) :
    litmusCmd = "uptime"
    command = "ssh %s %s" % (node, litmusCmd)
    timeout = 5
    try:
        #exitCode = subprocess.call(shlex.split(command), timeout=timeout)
        #return exitCode
        #exitCode = subprocess.check_output(shlex.split(command), timeout=timeout)
        #exitCode = subprocess.check_output(shlex.split(command), stderr='/dev/null', timeout=timeout)
        with open(os.devnull, 'w') as devnull: 
            sshStdOut = subprocess.check_output(shlex.split(command), timeout=timeout, stderr=devnull)
            dbg(5, "ssh test stdout: %s" % sshStdOut)
        return "up"
    except subprocess.CalledProcessError as e:
        error = "\"{cmd}\" had a bad return code of {ret}.".format(cmd=command, ret=e.returncode)
        return "DOWN"
        #raise ValueError(err)
    except subprocess.TimeoutExpired as e:
        error = "\"{cmd}\" exceeded the timeout of {t} seconds.".format(cmd=command, t=timeout)
        #raise TimeoutError(error)
        dbg(1, "This case likely have ssh asking for password")
        print( e.output )
        return "TimedOut"
    return "Ssh_unexpected_problem"
# checkSsh()-end 

def executeCommand(node, command, timeout=5):
    sshCommand = "ssh {node} \"{command}\"".format(node=node, command=command)
    try:
        with open(os.devnull, 'w') as devnull:
            sshStdOut = subprocess.check_output(shlex.split(sshCommand), timeout=timeout, stderr=devnull)
            return sshStdOut.decode('utf-8').strip()
    except:
        return None # Might want to add specific error handling later
# executeCommand()-end

def checkMountUsage(node, mount):
    command = "df -h {mount} --output=target,used | grep {mount} | awk '{{ print $2 }}'".format(mount=mount)
    usage = executeCommand(node, command)
    return usage or "NotFound"
# checkMountUsage()-end

# https://stackoverflow.com/questions/14236346/elegant-way-to-test-ssh-availability
# but paramiko seems to req lot of username/key setup, too variable for generic user to use :(
def checkSshParamiko_Abandoned( node ) :
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    #ssh.set_missing_host_key_policy( AutoAddPolicy )
    retries = 1
    interval = 5
    #key =  None
    #private_key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(key))
    for x in range(retries) :
        try : 
            #ssh.connect(node, pkey=private_key)
            ssh.connect(node)
            ssh.close()
            return "Up"
        except Exception as e :
            dbg(3, "check_ssh exception %s" % e)
            time.sleep( interval )
    return "Down"
    #return "TimeOut"
# checkSsh()-end 

# other checks to add
# checkNhc()
# (see README)


def cleanUp() :
    os.remove( sinfoRSfile )
    print( "## Run 'reset' if terminal is messed up" )
    #os.system( "reset") # terminal maybe messed up due to bad ssh, but reset clears the screen :(
# cleanUp()-end

def processLine(data):
    node, line = data
    sshStatus = checkSsh(node)
    scratchStatus = checkMountUsage(node, "/global/scratch") 	if sshStatus == 'up' else "(skip)"
    swStatus      = checkMountUsage(node, "/global/software") 	if sshStatus == 'up' else "(skip)"
    tmpStatus     = checkMountUsage(node, "/tmp") 		if sshStatus == 'up' else "(skip)"
    #print("%-120s ## ssh:%4s scratch:%10s" % (line, sshStatus, scratchStatus, swStatus, tmpStatus))
    print("%-80s ## ssh:%4s scratch:%7s sw:%7s tmp:%7s" % (line, sshStatus, scratchStatus, swStatus,tmpStatus))
#processLine()-end

def main(): 
    args = process_cli()
    dbg(5, "bofhbot I am")
    vprint(1, "## sinfo enhanced by bofhbot ##")
    # tmp exit
    #return

    # ++ TODO
    # add code to handle --nodelist (from pdsh as template)
    # substitude the nodelist instead of running commands below

    generateSinfo()
    sinfoList = buildSinfoList()
    #sinfoNodeList = sinfoList2nodeList( sinfoList )  # OOP would be nice not having to pass whole array as fn param

    # ++ OOP gather all info
    # have diff fn to format output
    pool = Pool(20)
    nodes = [ (node, line) for line in sinfoList for node in getNodeList(line) ]
    pool.map(processLine, nodes)
    cleanUp()
# main()-end


main()


#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python  
