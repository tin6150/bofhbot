#!/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python3

## #!/usr/bin/env python3
## root don't have access SMF

## run as (tin@master): 
## exp: 8 ## pdsh -w n0[143-145,174-176,258-261].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 4 ## pdsh -w n0[134-138,158-161].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[209-217,262-264].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[004-005].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   


import socket 
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *
# could be set by argparse -v
bofhbot_lib.verboseLevel = 0 #6
bofhbot_lib.dbgLevel = 0 #6

# global param :)  better as OOP get() fn or some such.
devQueryOutFile = '/var/tmp/devQuery.out' # store deviceQuery output
osDevOutFile = '/var/tmp/osDev.out'       # store ls -l /dev/nvidia* 


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
  command = "ls -l %s*" % osDevPattern + " > " + osDevOutFile 
  runQueryOsDevPresentExitCode = os.system(command) 
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
  

# queryOsDevicePresent()-end

def main():
  bofhbot_lib.dbg(5, "bofhbot I am")
  vprint(1, "## checkGpuOnNode.py begin  ##")
  devQueryFound = queryDevicePresent()
  gpuExpect = "2,4,8" # need parse gres.conf
  osDevCount  = queryOsDevPresent()
  maquina = socket.gethostname()
  #print( "host: %s ; deviceQuery found: %s ; gpuExpected: %s ; /dev/nvidia* count: %s"  % (maquina, devQueryFound, gpuExpect, osDevCount ) )
  print( "host: %s ; gpuExpected: %s ; /dev/nvidia* count: %s ; deviceQuery found: %s"  % (maquina, gpuExpect, osDevCount, devQueryFound ) )
  # main()-end


main()


#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python
