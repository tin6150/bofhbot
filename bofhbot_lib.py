

# pulling common fn out of bofhbot.py
# create this library
# so that botd can use it as well

# idea for now is bofhbot.py will just call lib fn
# and be small client program



import os
import re # regex
import time
import argparse
import shlex
import sys
import subprocess
import getpass
from multiprocessing import Pool, cpu_count
from shutil import copyfile 
from dateutil import parser
import time

# global param :)  better as OOP get() fn or some such.  
sinfoRSfile = '/var/tmp/sinfo-RSE.txt'
#sinfoRSfile = 'sinfo-RSE-eg.txt.head5'
nodeColumnIndex=3
nodeColumnIndex=0

# programmer aid fn
# dbgLevel 3 (ie -ddd) is expected by user troubleshooting problem parsing input file
# currently most detailed output is at level 5 (ie -ddddd) and it is eye blurry even for programmer
dbgLevel = 0     ## user of lib would change this "object" variable :)
##dbgLevel = 1   use -ddddd now
def dbg( level, strg ):
    if( dbgLevel >= level ) : 
        print( "<!--dbg%s: %s-->" % (level, strg) )

# -v add verbose output.  not sure if ever would need it
def vprint( level, strg ):
    if( verboseLevel >= level ) : 
        print( "%s" % strg )


# get ouptupt of sinfo -R -S ... 
# now just store output in a file  sinfoRSfile (global; future oop property)
# return is just exit code of running the sinfo cmd.
def generateSinfo() :
    # https://github.com/PySlurm/pyslurm  but then have to install python lib before being able to use script :-/
    # actually pyslurm don't have any fn for sinfo 
    #sinfoRS = subprocess.run(['sinfo', '-R -S %E --format="%9u %19H %6t %N %E"'])
    #cmd = 'sinfo -R -S %E --format="%9u %19H %6t %N %E" ' + " > "  +  sinfoRSfile     # more human readable
    cmd = 'sinfo -N -R -S %E --format="%N %6t %19H %9u %E" ' + " > "  +  sinfoRSfile   # node first, one node per line :)
    command = cmd
    dbg(5, command)
    #sinfoRSout = subprocess.call(shlex.split(command))
    sinfoRSout = os.system(command) # exit code only from mos.system()
    dbg(5, sinfoRSout )
    return sinfoRSout 
    # return is just exit code of running the sinfo cmd.
    #+sinfoRS = os.popen(cmd).read()
    #sinfoRS = open('sinfo-RSE-eg.txt.head5','r')
#generateSinfo()-end

#def getSinfo():
def buildSinfoList():
#def buildSinfoList(infoRS=sinfoRSfile):
    # sinfoRSfile is currently global, i guess OOP would be very similar...
    # ++ consider changing to use fn arg for the file
    dbg(3, "buildSinfoList() about to open '%s'" % sinfoRSfile )
    sinfoRS = open( sinfoRSfile,'r')
    #print( sinfoRS )
    #linelist = sinfoRS.split('\s')
    # basic cleansing/sanitizing done, just to avoid hacking
    # note that the debug still process original line
    # once stable and known work as desired, move the sanitizing earlier in the code
    # especially now user could be providing --nodelist or --sfile 
    sinfoList = [ ] 
    for line in sinfoRS :
        dbg(4, "processing '%s'" % line.rstrip() )
        #currentLine = re.search( '([\S]+[\s]+)*', line.rstrip())   # truncate long lines :(  still match empty line :(
        currentLine = re.search( '^$', line )   # ie blank line
        if( currentLine ) :
            dbg(5, "skipping blank line" )
        else :
            # sinfoList.append( line.rstrip() )  # unsanitized, work.
            currentLine =  re.sub( '[;$`#\&\\\]', '_', line ).rstrip()   # sanitized
            # sanitization/cleansing replaces ; $ ` # &  \ with underscore
            # () still allowed.  but since $ not allowed, won't have 4()
            # * ' " are allowd.  not thinking of problem with these at this point
            sinfoList.append( currentLine )  # sanitized, replaces ; & with underscore
            #sinfoList.append( re.sub( r':;\&\*', r'_', line.rstrip() ) )  # sanitized, replaces ; & with underscore
            dbg(5, "adding...: '%s' to   sinfoList" % currentLine )
    #print( sinfoList )
    return sinfoList 
# buildSinfoList()-end


# Input: array list of lines with output of sinfo -R -S ...
# OUTPUT: array list of nodes (maybe empty)
# this was first coded up for offline development with saved sinfo ... output
# but useful for new user to call it, in case they want to dry run the script
# in non production environment :)
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
## don't like this now.  very specific to our node naming convention of n0000.CLUSTER
## should just expect nodename from column 1 or some such
## TODO.  ie, relax it needing \d\d\d\d ... 
## do expect a cleansed file :)
#### i typically return only one node, and probably indeed do only so now
#### some sinfo -some-args return more than one node per line, maybe -RSE don't... 
#### this is working for bofhbot.py... 
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
        ##~~print( e.output )
        dbg(1, e.output )    # this output b''
        return "TimedOut"
    return "Ssh_unexpected_problem"
# checkSsh()-end 

def executeCommand(node, command, timeout=5):
    sshCommand = "ssh {node} \"{command}\"".format(node=node, command=command)
    try:
        with open(os.devnull, 'w') as devnull:
            sshStdOut = subprocess.check_output(shlex.split(sshCommand), timeout=timeout, stderr=devnull)
            return sshStdOut.decode('utf-8').strip()
    except subprocess.TimeoutExpired as e:
        dbg(2, "executeCommand via ssh timed out--%s" % e) ## Sn
        return None # Might want to add specific error handling later
    except Exception as e:
        dbg(1, e)
        return None # Might want to add specific error handling later
# executeCommand()-end

def checkMountUsage(node, mount):
    command = "df -h {mount} --output=target,size | grep {mount} | awk '{{ print $2 }}'".format(mount=mount)
    usage = executeCommand(node, command)
    return usage or "NotFound"
# checkMountUsage()-end

def checkProcesses(node):
    command = 'ps -eo uname | egrep -v \\"^root$|^29$|^USER$|^telegraf$|^munge$|^rpc$|^chrony$|^dbus$|^{username}$\\" | uniq'.format(username=getpass.getuser())
    ## when placed as module lib for import, need to catch exception or it will returnt None and mess up all other ssh checks. -Sn
    try : 
        users = ','.join(executeCommand(node, command).split('\n'))
    except subprocess.TimeoutExpired as e:
        users = "(time out)"
    except :
        dbg( 1, "checkProcesses() general exception, returning users as NA")
        users = "NA"
    return users or "(no users)"
# checkProcesses()-end


def checkLoad(node):
    command = "uptime | awk -F' ' '{ print substr($10,0,length($10)-1) }'"
    uptime = executeCommand(node, command)
    return uptime

def secondsToString(sec):
    sec = int(sec)
    if sec < 60:
        return "{}s".format(sec)
    minutes = sec // 60
    if minutes < 60:
        return "{}m".format(minutes)
    hours = minutes // 60
    if hours < 24:
        return "{}h".format(hours)
    days = hours // 24
    return "{}d".format(days) 

def checkUptime(node):
    command = "uptime -s"
    start_time = executeCommand(node, command)
    start_date = parser.parse(start_time) 
    return secondsToString(time.time() - start_date.timestamp())
    command = 'echo $(date +%s) - $(date --date="$(uptime -s)" +"%s") | bc'
    uptime = executeCommand(node, command)
    return secondsToString(int(uptime)) if uptime else "Error"

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
    if( dbgLevel == 0 ) :
        os.remove( sinfoRSfile ) 
    dbg(1, "sinfoRSfile left at: %s " % sinfoRSfile )
    vprint(1, "## Run 'reset' if terminal is messed up" )
    #os.system( "reset") # terminal maybe messed up due to bad ssh, but reset clears the screen :(
# cleanUp()-end

def make_color(a, b):
  return lambda s: '\033[{};{}m{}\033[0;0m'.format(a, b, s)
# Colors: https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python
light_red = make_color(1, 31)
red = make_color(0, 31)
green = make_color(0, 32)
red_bg = make_color(1, 41)
green_bg = make_color(1, 42)
gray = make_color(1, 30)

def processLine(data):
    node, line, color = data
    line = ' '.join(line.split(' ')[1:]) # Remove node name from beginning of line
    sshStatus = checkSsh(node)

    if color:
        ssh_color = green if sshStatus == 'up' else red
        sshStatusFormatted = ssh_color(sshStatus)
        node_color = green_bg if sshStatus == 'up' else red_bg
        nodeFormatted = node_color(node)
    else:
        sshStatusFormatted = sshStatus
        nodeFormatted = node
    skip = gray('(skip)') if color else '(skip)' 

    checks = [
        ('scratch', lambda: checkMountUsage(node, "/global/scratch")),
        ('software', lambda: checkMountUsage(node, "/global/software")),
        ('tmp', lambda: checkMountUsage(node, "/tmp")),
        ('users', lambda: checkProcesses(node)),
        ('load', lambda: checkLoad(node)),
        ('uptime', lambda: checkUptime(node))
    ]

    ## added the try block, at least program no longer crash
    ## but time out error spill all over the screen. 
    ## furthermore, now only show ssh up, no other status :(   FIXME
    ## likely need to break out `results =` line to process error individually
    try:
        ##results = [ '{}:{:7}'.format(name, check() if sshStatus == 'up' else skip) for name, check in checks ]
        if sshStatus == 'up' :
            results = [ '{}:{:7}'.format(name, check() ) for name, check in checks ]
        else :
            #skip
            results = "" ## ie no output when ssh time out
    #except :
    except TypeError as e:
        results = "" ## ie no output when ssh time out
    #print("%-120s ## ssh:%4s scratch:%10s" % (line, sshStatus, scratchStatus, swStatus, tmpStatus))
    print("{:14} {:80} ## ssh: {:4} ".format(nodeFormatted, line, sshStatusFormatted) + ' '.join(results))
#processLine()-end

def print_stderr(s, color = True):
    # Colors: https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python
    if color:
        s = light_red(s)
    sys.stderr.write(s + '\n')
    sys.stderr.flush()
# print_stderr()-end


#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python  
