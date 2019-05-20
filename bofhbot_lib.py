

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
import pandas as pd
from multiprocessing import Pool, cpu_count
from shutil import copyfile 
from dateutil import parser
import time
import threading

PDSH_GROUP_DIR = "/etc/pdsh/group"
POWER_STATUS_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh status {node}"
POWER_CYCLE_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh cycle {node}"
POWER_ON_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh on {node}"
POWER_OFF_COMMAND = "sudo /global/home/groups/scs/sbin/ipmiwrapper.tin.sh off {node}"
SLURM_RESUME_COMMAND = "sudo scontrol update {node} state=resume"

# global param :)  better as OOP get() fn or some such.  
sinfoRSfile = '/var/tmp/sinfo-RSE.txt'
#sinfoRSfile = 'sinfo-RSE-eg.txt.head5'
nodeColumnIndex=3
nodeColumnIndex=0

# programmer aid fn
# dbgLevel 3 (ie -ddd) is expected by user troubleshooting problem parsing input file
# currently most detailed output is at level 5 (ie -ddddd) and it is eye blurry even for programmer
dbgLevel = 5    ## user of lib would change this "object" variable :)
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
    #format is: NODELIST        STATE   TIMESTAMP       USER    REASON
    cmd = 'sinfo -N -R -S %E --format="$(echo -e \'%N\t%t\t%H\t%u\t%E\')"' + " > "  +  sinfoRSfile   # node first, one node per line :)
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

# buildSinfoList() return an array of lines
# each line is sanitized version of sinfo -RSE output line
# ie, each record become an array entry
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

""" Read data from sinfoRSfile as a pandas DataFrame """
def buildSinfoDataFrame():
    splitColumns = lambda line: [ elem.strip() for elem in line.split('\t') ]
    columns, *data = map(splitColumns, open(sinfoRSfile, 'r'))
    return pd.DataFrame(data, columns = columns)
# buildSinfoDataFrame()-end

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
        return "Down"
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
    sshCommand = "ssh {node} {command}".format(node=node, command=shlex.quote(command))
    return executeLocalCommand(sshCommand, timeout=timeout)
# executeCommand()-end

def executeLocalCommand(command, timeout=5):
    try:
        with open(os.devnull, 'w') as devnull:
            stdout = subprocess.check_output(shlex.split(command), timeout=timeout, stderr=devnull)
            return stdout.decode('utf-8').strip()
    except subprocess.TimeoutExpired as e:
        dbg(2, "executeLocalCommand timed out--%s" % e) ## Sn
        return None # Might want to add specific error handling later
    except Exception as e:
        dbg(1, e)
        return None # Might want to add specific error handling later
# executeLocalCommand()-end

def checkPowerStatus(node):
    command = POWER_STATUS_COMMAND.format(node=node)
    output = executeLocalCommand(command)
    if output:
        return output.split('\n')[0].split(' ')[-1]
    return 'error' 

def checkMountUsage(mount):
    def checkNode(node):
        command = "df {mount} --output=target,size | grep {mount} | awk '{{ print $2 }}'".format(mount=mount)
        usage = executeCommand(node, command)
        return int(usage) * (2 ** 10) if usage else None
    return checkNode
# checkMountUsage()-end

def checkProcesses(node):
    command = 'ps -eo uname | egrep -v \\"^root$|^29$|^USER$|^telegraf$|^munge$|^rpc$|^chrony$|^dbus$|^{username}$\\" | uniq'.format(username=getpass.getuser())
    ## when placed as module lib for import, need to catch exception or it will returnt None and mess up all other ssh checks. -Sn
    return list(filter(lambda x: x, executeCommand(node, command).split('\n')))
# checkProcesses()-end


def checkLoad(node):
    command = "uptime | awk -F' ' '{ print substr($10,0,length($10)-1) }'"
    uptime = executeCommand(node, command)
    try:
        return float(uptime)
    except ValueError:
        return None

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
    if not start_time:
        return None
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

# These checks should always be run (locally)
local_checks = {
    'SSH': checkSsh,
    'POWER': checkPowerStatus,
}

# These checks should be run if SSH is up on the remote node
ssh_checks = {
    'SCRATCH': checkMountUsage("/global/scratch"),
    'SOFTWARE': checkMountUsage("/global/software"),
    'TMP': checkMountUsage("/tmp"),
    'USERS': checkProcesses,
    'LOAD': checkLoad,
    'UPTIME': checkUptime
}

def cache(timeout = 60):
    def make_cache(f):
        lock = threading.Lock()
        cache = {}
        def cached(*args):
            nonlocal cache
            key = hash(repr(args))
            lastUpdated, cached = cache[key] if key in cache else (None, None)
            currentTime = time.time()
            # If there is no update necessary, no need to do the lock stuff 
            if lastUpdated and (currentTime - lastUpdated) < timeout:
                return cached
            lock.acquire()
            # This check is necesarry because by the time the lock is 
            # acquired, the result may be fresh enough
            if not lastUpdated or (currentTime - lastUpdated) > timeout:
                result = f(*args)
                lastUpdated, cached = currentTime, result
                cache[key] = lastUpdated, cached
            lock.release()
            return cached
        return cached
    return make_cache

DATA = {
    'KiB': (2 ** 10),
    'MiB': (2 ** 20),
    'GiB': (2 ** 30),
    'TiB': (2 ** 40),
    'PiB': (2 ** 50),
}

def validNodeName(f):
    def inner(node, *args, **kwargs):
        if not re.match('^[A-Za-z0-9-_\.]+$', node):
            # If you give a bad node name, don't do anything
            print("Invalid node name! {}".format(node))
            return
        return f(node, *args, **kwargs)
    return inner

@validNodeName
def powerOnNode(node):
    command = POWER_ON_COMMAND.format(node=node)
    print("Power on {}".format(node))
    return executeLocalCommand(command)

@validNodeName
def powerOffNode(node):
    command = POWER_OFF_COMMAND.format(node=node)
    print("Power off {}".format(node))
    # return executeLocalCommand(command)

@validNodeName
def powerCycleNode(node):
    powerStatus = checkPowerStatus(node)
    if powerStatus == "on":
        # Power cycle
        print("Power cycle {}".format(node))
        command = POWER_CYCLE_COMMAND.format(node=node)
    elif powerStatus == "off":
        # Power on
        print("Power on {}".format(node))
        command = POWER_ON_COMMAND.format(node=node)
    # return executeLocalCommand(command)

@validNodeName
def resumeNode(node):
    command = SLURM_RESUME_COMMAND.format(node=node)
    print("Resume {}".format(node))
    return executeLocalCommand(command)

nodeResumeQueue = set()
nodeResumeQueueLock = threading.Lock()

@validNodeName
def addNodeToResumeQueue(node):
    nodeResumeQueueLock.acquire()
    nodeResumeQueue.add(node)
    nodeResumeQueueLock.release()

RESUME_CHECK_INTERVAL = 60 # seconds

def processResumeQueue():
    nodeResumeQueueLock.acquire()
    if nodeResumeQueue:
        for node in list(nodeResumeQueue):
            results = getDataFromSsh(node)
            if results['OVERALL']:
                resumeNode(node)
                nodeResumeQueue.remove(node)
    nodeResumeQueueLock.release()
    t = threading.Timer(RESUME_CHECK_INTERVAL, processResumeQueue)
    t.start()

processResumeQueue()

""" Get node list by group name 
    Group name comes from /etc/pdsh/groups or 'sinfo'
    Invalid group name returns None"""
@cache(timeout = 300)
def getNodesByGroup(group):
    if group == 'sinfo':
        return buildSinfoDataFrame()['NODELIST']
    groups = os.listdir(PDSH_GROUP_DIR)
    if group not in groups:
        return [] # Invalid group name so there are no nodes in it
    # Beware of path injection... (group name contains /../ or similar)
    # Should be okay because we are only allowing valid group
    return [ node.strip() for node in open(os.path.join(PDSH_GROUP_DIR, group), 'r') ]

def overallCheck(results):
    for k, v in results.items():
        if v == None:
            return False
    return (results['LOAD'] < 1) and (len(results['USERS']) == 0) and (results['SCRATCH'] > 1 * DATA['PiB']) and (results['SOFTWARE'] > 700 * DATA['GiB']) and (results['TMP'] > 2 * DATA['GiB'])

""" Given a hostname, SSH to node if possible and perform checks.
    Returns a dictionary of the check results."""
def getDataFromSsh(hostname):
    localResults = { k: f(hostname) for k, f in local_checks.items() }
    sshResults = { k: f(hostname) if localResults['SSH'] == 'up' else None for k, f in ssh_checks.items() }
    return { **localResults, **sshResults, 'OVERALL': overallCheck(sshResults) }

""" Return a DataFrame containing sinfo + SSH check data """
@cache(timeout = 300)
def getFullNodeData(group):
    node_list = getNodesByGroup(group)
    df = pd.DataFrame(node_list, columns = ['NODELIST'])
    sinfo_df = buildSinfoDataFrame()
    df = pd.merge(df, sinfo_df, on='NODELIST', how='left')
    #pool = Pool(cpu_count())
    pool = Pool(cpu_count())
    results = pool.map(getDataFromSsh, df['NODELIST'])
    if len(results):
        for k in results[0].keys():
            df[k] = [ result[k] for result in results ]
    df.index = df['NODELIST']
    return df


# INPUT: data is ... ???
# OUTPUT:  stdout, decorated/improved output of sinfo -RSE
def processLine(data):
    node, line, color = data
    line = ' '.join(line.split('\t')[1:]) # Remove node name from beginning of line
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

    #++ these checks should be read from  a .cfg file
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
