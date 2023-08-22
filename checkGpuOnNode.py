
#!/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python3

## #!/usr/bin/env python3
## root don't have access SMF

## run as (tin@master): 
## exp: 8 ## pdsh -w n0[143-145,174-176,258-261].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 4 ## pdsh -w n0[134-138,158-161].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[209-217,262-264].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[004-005].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## comb   ## pdsh -w n0[143-145,174-176,258-261].savio3,n0[134-138,158-161].savio3,n0[004-005,209-217,262-264].savio3,n0[012-026,223-226,298-302].savio2 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   

## version/changes
## 0.1  Tin usable deviceQuery detection 
## 0.1a Prepping for Hamza's PR
## 0.2  merged with Hamza's code
## 0.3  Tin - better error detection, output


import socket 
import os
import getpass
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *
import csv, datetime
import smtplib
from tools import *
from jinja2 import Environment, FileSystemLoader
# TODO: use argparse -v, recycle from bofhbot.py ++FIXME++
bofhbot_lib.verboseLevel  = 1 #6 = very verbose; 0 = silent (check exist code, syslog/email, eg use in cron) 
bofhbot_lib.dbgLevel      = 1 #6

# global param :)  better as OOP get() fn or some such.
devQueryOutFile = f'/var/tmp/devQuery.{getpass.getuser()}.out' # store deviceQuery output
osDevOutFile = f'/var/tmp/osDev.{getpass.getuser()}.out'       # store ls -l /dev/nvidia* 

emailRecipient = 'hchristopher@lbl.gov'

def queryDevicePresent() : 
  # run command /usr/local/bin/deviceQuery  to detect number of live GPU on a system
  # don't seems to need root access to run deviceQuery
  # (lspci | grep NVIDIA does not get smaller when GPU fricks out)
  # deviceQuery | tee /global/scratch/users/tin/pub/devQ.n0144.out | grep Device\ [0-9] 
  # seems to reliably show how many GPU is actually live on the system.
  # ELSE, if result has 
  # Result = FAIL
  # then no gpu was found (eg n0258.savio3 after all gpu not usable, or n0054 which has no GPU)
  devQueryCount = 0
  devPattern = 'Device\ [0-9]'
  command = "/usr/local/bin/deviceQuery" + " > " + devQueryOutFile 
  runDevQueryExitCode = os.system(command) 
  os.chmod(devQueryOutFile, 0o777)  # that strange 0o777 is needed by python
  devQueryFH = open( devQueryOutFile, 'r' )
  for line in devQueryFH : 
    dbg(4, "processing '%s'" % line.rstrip() )
    currentLine = re.search( devPattern, line )  
    if( currentLine ) :
      dbg(5, "found a device line" )
      devQueryCount = devQueryCount + 1
    #enf-if
  #end-for
  dbg(2, "queryDevicePresent() about to return with %s" % devQueryCount )
  return devQueryCount
# queryDevicePresent()-end
  

def queryOsDevPresent() : 
  # count /dev/nvidia0 .. nvidia7 , but may include dead device
  osDevCount = 0
  osDevPattern = '/dev/nvidia[0-9]'
  command = "ls -l %s*" % osDevPattern + " 2>/dev/null " + " > " + osDevOutFile
  runQueryOsDevPresentExitCode = os.system(command) 
  os.chmod(osDevOutFile, 0o777)
  osDevFH = open( osDevOutFile, 'r' )
  for line in osDevFH : 
    dbg(4, "processing '%s'" % line.rstrip() )
    currentLine = re.search( osDevPattern, line )  
    if( currentLine ) :
      dbg(5, "found a /dev/nvidia line" )
      osDevCount = osDevCount + 1
    #enf-if
  #end-for
  dbg(2, "queryOsDevPresent() about to return with %s" % osDevCount )
  return osDevCount
# queryOsDevPresent()-end
  
def parseRange(rangeStr):
    """Parse a range string and return a list of integers."""
    result = []
    for x in rangeStr.split(','):
        if '-' in x:
            start, end = x.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(x))
    return result

def parseGresConf():
    """Parse /etc/slurm/gres.conf and return a dictionary of gpu counts."""
    cluster = os.popen('sacctmgr list cluster | tail -1 | awk \'{print $1;}\'').read().split('\n')[0]
    gresConf = {}
    with open('/etc/slurm/gres.conf', 'r') as f:
        for line in f:
            line = line.strip()
            if(cluster == 'brc'):
              if not line.startswith('NodeName='):
                continue
            else:
              if not line.startswith('Nodename='):
                continue
            fields = line.split()
            nodeName = fields[0].split('=')[1]
            gresConf[nodeName] = {}
            for field in fields[1:]:
              if('=' in field):
                key, value = field.split('=')
                gresConf[nodeName][key] = value
            gresConf[nodeName]['Count'] = int(gresConf[nodeName]['Count'])
            gresConf[nodeName]['Nodes'] = set()
            if(cluster == 'brc'):
              prefix = nodeName[:nodeName.index('[')]
              suffix = nodeName[nodeName.index(']') + 1:]
              suffixPrefix = suffix[:suffix.index('[')]
              suffixSuffix = suffix[suffix.index(']') + 1:]
              suffixRange = suffix[suffix.index('[') + 1:suffix.index(']')]   
              nodeRange = nodeName[nodeName.index('[') + 1:nodeName.index(']')]
              for i in parseRange(nodeRange):
                for j in parseRange(suffixRange):
                  gresConf[nodeName]['Nodes'].add(f'%s%0{5-len(prefix)}d%s%s%s' % (prefix, i, suffixPrefix, j, suffixSuffix))
            else:
              gresConf[nodeName]['Nodes'].add((nodeName.replace('[','')).replace(']',''))
    return gresConf

def findExpectedGpu(machineName):
    # this function will parse /etc/slurm/gres.conf 
    # use the current hostname (machineName could be passed as fn argument)
    # return how many gpu this machine should have
    # node that have no gpu should return 0
    gresConf = parseGresConf()
    for nodeName in gresConf:
        if machineName in gresConf[nodeName]['Nodes']:
            return gresConf[nodeName]['Count']
    return 0

def gpuErrorActions(message):
  # Actions to run when a gpu error is detected
  logGpuError(message)
  emailGpuError(message)

def logGpuError(message):
  # Logs in syslog
  os.system('logger -p local0.error -t gpuError "%s"' % message)

def emailGpuError(message):
  # Emails the error to the recipients in emailRecipients
  # send-mail: Cannot open mail:25
  # Check: node seems to have problem executing mailx.  ++FIXME++
  # os.system('echo "%s" | mailx -s "gpuOffline - %s" %s' % (message,message,emailRecipient) )
  # notest = True
  # server = 'smtp.lbl.gov'
  # From = 'High Performance Computing Services <hpcs@lbl.gov>'
  # Cc = []
  # Bcc = ['High Performance Computing Services <hpcs@lbl.gov>']
  # subject = "test"
  # To = [emailRecipient]
  # Cc = []
  # Bcc = []
  # feeder = ""
  content_of_email = f"gpuOffline - {message}"
  # feeder = content_of_email
  # try:
    # info('Sending email to \"%s\" ...' % To)
    # email = send_email(server, From, To, Cc, Bcc, subject, feeder, notest)
  # except:
    # error('Error sending email to \"%s\", abort.' % To)
  # Open the file in append & read mode ('a+')
  with open("/global/home/users/hchristopher/bofhbot/data/errorEmail.txt", "a+") as file_object:
    file_object.seek(0)
    # If file is not empty then append '\n'
    data = file_object.read(100)
    if len(data) > 0 :
        file_object.write("\n")
    # Append text at the end of file
    file_object.write(content_of_email)
  pass


############################################################

def main():
  bofhbot_lib.dbg(5, "bofhbot I am")
  vprint(2, "## checkGpuOnNode.py begin  ##")
  machineName = socket.gethostname()
  devQueryFound = queryDevicePresent()
  gpuExpect = findExpectedGpu(machineName)
  osDevCount  = queryOsDevPresent()
  # stricly should clean up the /var/tmp/*out files created.  but they are 777 mode for now and maybe useful to have them around.
  #print( "host: %s ; deviceQuery found: %s ; gpuExpected: %s ; /dev/nvidia* count: %s"  % (machineName, devQueryFound, gpuExpect, osDevCount ) )
  #print( "host: %s ; gpuExpected: %s ; /dev/nvidia* count: %s ; deviceQuery found: %s"  % (machineName, gpuExpect, osDevCount, devQueryFound ) )    ## // old print by tin

  errorState = False 
  if( gpuExpect != osDevCount  or   gpuExpect != devQueryFound ):
    errorState = True
  message =  "host: %s ; gpuExpected: %s ; /dev/nvidia* count: %s ; " \
             "deviceQuery found: %s" \
             % (machineName, gpuExpect, osDevCount, devQueryFound )
  if ( errorState ):
    message = message + " == DISCREPANCY ==" 
    gpuErrorActions(message)
    vprint(1, message)
    vprint(2, "## checkGpuOnNode.py end (error) ##")
    exit(0)   # ssh is noisy in this case.  return doesn't set exit code :-\
  else :
    vprint(1, message)
    vprint(2, "## checkGpuOnNode.py end ##")
    exit(0)
  #end-if( errorState )
# main()-end


main()

#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python
